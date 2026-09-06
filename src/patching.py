"""Causal interventions and component attribution.

Analysis only -- everything here takes a model already loaded by
`src.model_utils.load_model`.  Two questions, two functions:

    patch_residual_sweep    where does the answer live?   (layer x position)
    component_attribution   which parts write it?         (layer x head)

Both score a **logit difference** (answer minus a wrong answer), never a bare
logit.  A bare logit moves whenever the whole distribution shifts -- overwriting
a chunk of the residual stream changes how peaked the softmax is, and you would
read that as signal.  The difference between two tokens cancels it.

Sliced bf16-on-MPS tensors go through `to_cpu_f32`; see its docstring for why
`.to("cpu", torch.float32)` is not a valid substitute.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np
import torch

from src.model_utils import _block_output, get_blocks, get_ln_f, to_cpu_f32


def get_embed(model) -> torch.nn.Module:
    """The token embedding, resolved dynamically (Qwen: model.model.embed_tokens)."""
    for path in ("model.embed_tokens", "model.model.embed_tokens", "transformer.wte"):
        obj = model
        for part in path.split("."):
            obj = getattr(obj, part, None)
            if obj is None:
                break
        if obj is not None:
            return obj
    raise AttributeError(f"could not locate token embedding on {type(model).__name__}")


def logit_diff(logits: torch.Tensor, answer_id: int, wrong_id: int | None = None):
    """`answer` minus `wrong` on the last axis.  Falls back to a bare logit if
    `wrong_id` is None, which is worse -- pass a wrong answer if you have one."""
    x = to_cpu_f32(logits)
    if wrong_id is None:
        return x[..., answer_id]
    return x[..., answer_id] - x[..., wrong_id]


def _last_logits(model, enc: dict) -> torch.Tensor:
    """Logits at the final position only.  `logits_to_keep=1` skips the unembed on
    every other position -- with a 152k vocab that is most of the forward's tail."""
    with torch.inference_mode():
        return model(**enc, logits_to_keep=1).logits[:, -1]


# --------------------------------------------------------------------------- #
# 1. residual patching: layer x position
# --------------------------------------------------------------------------- #
def _cache_every_block(model, enc: dict) -> tuple[dict[int, torch.Tensor], torch.Tensor]:
    """One forward, every block's output kept on-device in model dtype.

    Stays on-device deliberately: these are donor values that get written straight
    back into another forward, so a round trip through CPU float32 would only add
    a cast in each direction.  36 x seq x 2560 bf16 is a couple of MiB.
    """
    blocks = get_blocks(model)
    cache: dict[int, torch.Tensor] = {}

    def make_hook(ell):
        def hook(_mod, _inp, output):
            cache[ell] = _block_output(output).detach().clone()
        return hook

    handles = [blocks[i].register_forward_hook(make_hook(i)) for i in range(len(blocks))]
    try:
        logits = _last_logits(model, enc)
    finally:
        for h in handles:
            h.remove()
    return cache, logits


def patch_residual_sweep(
    model,
    clean_enc: dict,
    corrupt_enc: dict,
    answer_id: int,
    wrong_id: int | None = None,
    layers: Iterable[int] | None = None,
    batch_positions: int = 8,
    progress: bool = True,
) -> dict:
    """Copy the clean residual into the corrupt run at every (layer, position).

    Returns a dict with

        recovered   [n_layers, seq] float32.  0 = the corrupt run, 1 = the clean
                    run.  >1 means the patch overshot; <0 means it made things
                    worse than the corruption did.  Both happen and both are real.
        logit_diff  [n_layers, seq] the unnormalised answer-minus-wrong logit
        layers      the layer indices, matching row order
        clean, corrupt  the two baseline logit differences

    Cost is `n_layers * ceil(seq / batch_positions)` forwards rather than
    `n_layers * seq`: one clean forward caches every layer up front, and each
    batched corrupt forward patches a *different* position in each batch row.

    Both prompts must tokenize to the same length -- otherwise position `i` is a
    different token in the two runs and the heatmap is meaningless.
    """
    blocks = get_blocks(model)
    layers = list(range(len(blocks))) if layers is None else list(layers)
    seq = corrupt_enc["input_ids"].shape[1]
    if clean_enc["input_ids"].shape[1] != seq:
        raise ValueError(
            f"clean and corrupt must be the same length; got "
            f"{clean_enc['input_ids'].shape[1]} vs {seq}. Pad or reword the pair."
        )

    clean_cache, clean_logits = _cache_every_block(model, clean_enc)
    corrupt_logits = _last_logits(model, corrupt_enc)
    clean_d = float(logit_diff(clean_logits[0], answer_id, wrong_id))
    corrupt_d = float(logit_diff(corrupt_logits[0], answer_id, wrong_id))
    if abs(clean_d - corrupt_d) < 1e-3:
        raise ValueError(
            f"clean and corrupt score the same ({clean_d:.3f} vs {corrupt_d:.3f}); "
            "there is nothing for a patch to restore. Pick a corruption that "
            "actually changes the answer."
        )

    out = np.zeros((len(layers), seq), dtype=np.float32)
    chunks = [list(range(s, min(s + batch_positions, seq))) for s in range(0, seq, batch_positions)]

    bar = None
    if progress:
        from tqdm.auto import tqdm

        bar = tqdm(total=len(layers) * len(chunks), desc="patching", unit="fwd")

    for row, ell in enumerate(layers):
        donor = clean_cache[ell][0]  # [seq, hidden], on device
        for positions in chunks:
            n = len(positions)
            enc_b = {k: v.repeat(n, 1) for k, v in corrupt_enc.items()}
            pos = torch.tensor(positions, device=donor.device)
            rows = torch.arange(n, device=donor.device)

            def hook(_mod, _inp, output, pos=pos, rows=rows, donor=donor):
                h = _block_output(output).clone()
                h[rows, pos] = donor[pos]
                return (h, *output[1:]) if isinstance(output, tuple) else h

            handle = blocks[ell].register_forward_hook(hook)
            try:
                patched = _last_logits(model, enc_b)
            finally:
                handle.remove()

            out[row, positions] = logit_diff(patched, answer_id, wrong_id).numpy()
            if bar is not None:
                bar.update(1)

    if bar is not None:
        bar.close()

    return {
        "recovered": (out - corrupt_d) / (clean_d - corrupt_d),
        "logit_diff": out,
        "layers": layers,
        "clean": clean_d,
        "corrupt": corrupt_d,
    }


# --------------------------------------------------------------------------- #
# 2. direct logit attribution: layer x head
# --------------------------------------------------------------------------- #
def component_attribution(
    model,
    enc: dict,
    answer_id: int,
    wrong_id: int | None = None,
    position: int = -1,
) -> dict:
    """How much does each attention head / MLP write the answer direction?

    A pre-norm transformer's final residual is a plain sum,

        x_final = embed + sum_l (attn_out_l + mlp_out_l)

    and `attn_out_l` is itself a sum over heads, because `o_proj` has no bias:
    head h contributes `W_O[:, h] @ z_h`.  The readout is linear in `x_final`,

        logit_t = (w_lnf * x_final / rms) . W_U[t]
                = x_final . (w_lnf * W_U[t]) / rms

    so every component's share of the answer-minus-wrong difference is just its
    dot product with that one direction.  This is exact for the run you did --
    `rms` is a scalar taken from the actual final residual, and `total` vs
    `actual` below is the arithmetic check.  It stops being exact the moment you
    read it counterfactually: deleting a head would change `rms` too, so a large
    attribution is not a promise about what ablation would do.

    Returns a dict with `heads` [n_layers, n_heads], `mlps` [n_layers], `embed`,
    `total`, and `actual`.  Units are logits of (answer - wrong).
    """
    blocks = get_blocks(model)
    ln_f = get_ln_f(model)
    cfg = model.config
    n_layers = len(blocks)
    n_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", None) or cfg.hidden_size // n_heads

    z: dict[int, torch.Tensor] = {}
    mlp: dict[int, torch.Tensor] = {}
    box: dict[str, torch.Tensor] = {}

    def z_hook(ell):
        # pre-hook on o_proj: its input is [batch, seq, n_heads * head_dim], the
        # heads concatenated in order, which is the only place per-head outputs
        # exist as separate vectors.
        def hook(_mod, args):
            z[ell] = to_cpu_f32(args[0][0, position])
        return hook

    def mlp_hook(ell):
        def hook(_mod, _inp, output):
            mlp[ell] = to_cpu_f32(_block_output(output)[0, position])
        return hook

    def embed_hook(_mod, _inp, output):
        box["embed"] = to_cpu_f32(_block_output(output)[0, position])

    def final_hook(_mod, _inp, output):
        box["final"] = to_cpu_f32(_block_output(output)[0, position])

    handles = [get_embed(model).register_forward_hook(embed_hook)]
    handles.append(blocks[-1].register_forward_hook(final_hook))
    for ell in range(n_layers):
        handles.append(blocks[ell].self_attn.o_proj.register_forward_pre_hook(z_hook(ell)))
        handles.append(blocks[ell].mlp.register_forward_hook(mlp_hook(ell)))
    try:
        logits = _last_logits(model, enc)
    finally:
        for h in handles:
            h.remove()

    x_final = box["final"]
    rms = float(torch.sqrt(x_final.pow(2).mean() + ln_f.variance_epsilon))

    w_lnf = to_cpu_f32(ln_f.weight)
    u = to_cpu_f32(model.lm_head.weight[answer_id])
    if wrong_id is not None:
        u = u - to_cpu_f32(model.lm_head.weight[wrong_id])
    direction = w_lnf * u  # [hidden]

    device = next(model.parameters()).device
    d_dev = direction.to(device)

    heads = np.zeros((n_layers, n_heads), dtype=np.float32)
    mlps = np.zeros(n_layers, dtype=np.float32)
    for ell in range(n_layers):
        # (d . W_O_h @ z_h) == (d @ W_O)_h . z_h -- fold the direction through
        # o_proj once instead of materialising [n_heads, hidden] contributions.
        w_o = blocks[ell].self_attn.o_proj.weight  # [hidden, n_heads * head_dim]
        proj = to_cpu_f32(d_dev @ w_o.float())
        heads[ell] = (z[ell] * proj).view(n_heads, head_dim).sum(-1).numpy() / rms
        mlps[ell] = float(mlp[ell] @ direction) / rms

    embed = float(box["embed"] @ direction) / rms
    total = float(heads.sum() + mlps.sum() + embed)
    actual = float(logit_diff(logits[0], answer_id, wrong_id))
    return {
        "heads": heads,
        "mlps": mlps,
        "embed": embed,
        "total": total,
        "actual": actual,
    }


def top_components(attr: dict, k: int = 10):
    """The k largest-magnitude writers, as a DataFrame.  Reading a heatmap by eye
    is how you miss a negative head."""
    import pandas as pd

    rows = [
        {"component": f"L{ell}H{h}", "layer": ell, "head": h, "dla": float(attr["heads"][ell, h])}
        for ell in range(attr["heads"].shape[0])
        for h in range(attr["heads"].shape[1])
    ]
    rows += [
        {"component": f"L{ell}MLP", "layer": ell, "head": None, "dla": float(v)}
        for ell, v in enumerate(attr["mlps"])
    ]
    df = pd.DataFrame(rows)
    return df.reindex(df["dla"].abs().sort_values(ascending=False).index).head(k).reset_index(drop=True)


def token_labels(tok, enc: dict) -> Sequence[str]:
    """`pos:piece` labels for heatmap axes -- position alone is unreadable."""
    ids = enc["input_ids"][0].detach().cpu().tolist()
    return [f"{i}:{tok.decode([t]) or tok.convert_ids_to_tokens(t)}" for i, t in enumerate(ids)]

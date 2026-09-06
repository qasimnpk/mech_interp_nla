"""Notebook visualizations for a HF causal LM + raw hooks.

These are display helpers, not a second model loader.  Tensors that might be
sliced bf16-on-MPS go through `to_cpu_f32` before any copy-off-device.
"""

from __future__ import annotations

import html

from src.model_utils import _block_output, get_blocks, to_cpu_f32  # sets MPS env, then torch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

# --------------------------------------------------------------------------- #
# tensors: what object is this?
# --------------------------------------------------------------------------- #
def show_tensor(t: torch.Tensor, name: str = "") -> None:
    """Pretty-print shape / range / histogram.  Always CPU float32 first (MPS bf16)."""
    x = to_cpu_f32(t)
    try:
        import lovely_tensors as lt

        prefix = f"{name}: " if name else ""
        print(prefix + str(lt.lovely(x)))
    except Exception:
        print(
            f"{name + ': ' if name else ''}shape={tuple(x.shape)} "
            f"dtype={x.dtype} min={x.min().item():.4g} max={x.max().item():.4g} "
            f"mean={x.mean().item():.4g}"
        )


def model_card(model) -> pd.DataFrame:
    """One-row table: architecture facts, no extra forward pass."""
    cfg = model.config
    n_params = sum(p.numel() for p in model.parameters())
    row = {
        "class": type(model).__name__,
        "layers": getattr(cfg, "num_hidden_layers", None),
        "hidden": getattr(cfg, "hidden_size", None),
        "heads": getattr(cfg, "num_attention_heads", None),
        "kv_heads": getattr(cfg, "num_key_value_heads", None),
        "head_dim": getattr(cfg, "head_dim", None)
        or (cfg.hidden_size // cfg.num_attention_heads),
        "vocab": getattr(cfg, "vocab_size", None),
        "attn": getattr(cfg, "_attn_implementation", None),
        "params_B": round(n_params / 1e9, 3),
        "device": str(next(model.parameters()).device),
        "dtype": str(next(model.parameters()).dtype).replace("torch.", ""),
    }
    return pd.DataFrame([row])


def print_architecture(model, depth: int = 2) -> None:
    """Parameter table.  Do not pass dummy inputs — that would be a second 4B forward."""
    from torchinfo import summary

    print(summary(model, depth=depth, verbose=0, col_names=("num_params",)))


# --------------------------------------------------------------------------- #
# token stream: where are we in the prompt?
# --------------------------------------------------------------------------- #
def _is_special_piece(piece: str) -> bool:
    return piece.startswith("<|") or piece.startswith("Ġ<|") or "im_start" in piece or "im_end" in piece


def token_table(tok, enc: dict) -> pd.DataFrame:
    """One row per position: id, piece, decoded text, pad / special / readout."""
    ids = enc["input_ids"][0].detach().cpu().tolist()
    mask = enc["attention_mask"][0].detach().cpu().tolist()
    last = max(i for i, m in enumerate(mask) if m) if any(mask) else len(ids) - 1
    rows = []
    for i, (tid, m) in enumerate(zip(ids, mask)):
        piece = tok.convert_ids_to_tokens(tid)
        decoded = tok.decode([tid])
        rows.append(
            {
                "pos": i,
                "id": tid,
                "piece": piece,
                "text": decoded,
                "pad": m == 0,
                "special": _is_special_piece(piece),
                "readout": i == last,
                "role": (
                    "PAD"
                    if m == 0
                    else "READOUT (next-token logits live here)"
                    if i == last
                    else "special"
                    if _is_special_piece(piece)
                    else "content"
                ),
            }
        )
    return pd.DataFrame(rows)


def show_token_stream(tok, enc: dict, title: str = "token stream"):
    """HTML: each token is a chip.  Orange = last prompt token (where we read logits)."""
    from IPython.display import HTML, display

    df = token_table(tok, enc)
    colors = {
        "PAD": ("#d0d0d0", "#222"),
        "special": ("#e8d5ff", "#222"),
        "content": ("#d6ecff", "#222"),
        "READOUT (next-token logits live here)": ("#ffb347", "#111"),
    }
    chips = []
    for _, r in df.iterrows():
        bg, fg = colors[r["role"]]
        border = "3px solid #c45c00" if r["readout"] else "1px solid #bbb"
        label = html.escape(repr(r["text"])[1:-1] or "·")
        chips.append(
            f'<span title="pos {r["pos"]}  id {r["id"]}  {r["role"]}" '
            f'style="display:inline-block;margin:2px;padding:3px 6px;'
            f"background:{bg};color:{fg};border:{border};border-radius:4px;"
            f'font-family:ui-monospace,monospace;font-size:12px;">'
            f'<small style="opacity:.6">{r["pos"]}</small> {label}</span>'
        )
    n_prompt = int((~df["pad"]).sum())
    legend = (
        "<p style='font-size:13px'>"
        f"<b>{title}</b> — {n_prompt} prompt tokens, seq_len={len(df)}. "
        "Grey=pad, purple=special, blue=content, "
        "<b style='background:#ffb347'>orange = readout position</b> "
        "(the model predicts the <i>next</i> token from here)."
        "</p>"
    )
    display(HTML(legend + "<div>" + "".join(chips) + "</div>"))
    return df


def colored_token_norms(tok, enc: dict, values, title: str = ""):
    """Color tokens by a per-position scalar (residual norm, logit, …)."""
    import circuitsvis as cv
    from IPython.display import display

    ids = enc["input_ids"][0].detach().cpu().tolist()
    tokens = [tok.decode([i]) or tok.convert_ids_to_tokens(i) for i in ids]
    v = to_cpu_f32(values).reshape(-1)
    if title:
        print(title)
    display(cv.tokens.colored_tokens(tokens=tokens, values=v.numpy()))


# --------------------------------------------------------------------------- #
# where in the model
# --------------------------------------------------------------------------- #
def draw_residual_stack(
    n_layers: int,
    highlight: int | None = None,
    highlight_label: str = "",
    norms: list[float] | None = None,
    title: str = "residual stream (decoder blocks)",
):
    """Cartoon of embed → blocks → ln_f → unembed.  Optional color = ||h|| at last token."""
    fig, ax = plt.subplots(figsize=(max(8, n_layers * 0.28), 2.6))
    xs = np.arange(n_layers)
    if norms is not None:
        c = np.array(norms, dtype=float)
        sc = ax.scatter(xs, np.zeros_like(xs), c=c, cmap="viridis", s=80, zorder=3)
        fig.colorbar(sc, ax=ax, label="||h_last||", fraction=0.04, pad=0.02)
    else:
        ax.scatter(xs, np.zeros_like(xs), c="#4c78a8", s=80, zorder=3)
    ax.plot(xs, np.zeros_like(xs), color="#888", lw=2, zorder=1)
    if highlight is not None:
        ax.scatter([highlight], [0], s=220, facecolors="none", edgecolors="#e45756", lw=2.5, zorder=4)
        ax.annotate(
            highlight_label or f"layer {highlight}",
            (highlight, 0),
            textcoords="offset points",
            xytext=(0, 18),
            ha="center",
            color="#e45756",
            fontsize=9,
        )
    ax.set_yticks([])
    ax.set_xlabel("layer (block output = residual after that block)")
    ax.set_xlim(-1, n_layers)
    ax.set_title(title)
    ax.text(-0.8, 0.15, "embed", ha="right", va="bottom", fontsize=8)
    ax.text(n_layers - 0.2, 0.15, "ln_f → unembed → logits", ha="right", va="bottom", fontsize=8)
    fig.tight_layout()
    return fig, ax


def cache_residual_seq(model, enc: dict, layer: int) -> torch.Tensor:
    """Full [seq, hidden] residual at one layer (CPU float32).  One extra forward."""
    blocks = get_blocks(model)
    box: dict[str, torch.Tensor] = {}

    def hook(_m, _i, out):
        box["h"] = to_cpu_f32(_block_output(out)[0])

    handle = blocks[layer].register_forward_hook(hook)
    try:
        with torch.inference_mode():
            model(**enc)
    finally:
        handle.remove()
    return box["h"]


def attention_patterns_at_layer(model, enc: dict, layer: int) -> torch.Tensor:
    """[n_heads, seq, seq] attention, CPU float32.

    SDPA does not return weights.  We flip `_attn_implementation` to eager for
    *this one short forward*, then put it back so generation stays on SDPA.
    """
    cfg = model.config
    old = cfg._attn_implementation
    cfg._attn_implementation = "eager"
    try:
        with torch.inference_mode():
            out = model(**enc, output_attentions=True)
        attn = out.attentions[layer]  # [batch, heads, q, k]
        return to_cpu_f32(attn[0])
    finally:
        cfg._attn_implementation = old


# --------------------------------------------------------------------------- #
# plots that reuse notebook numbers
# --------------------------------------------------------------------------- #
def plot_top5(tok, probs: torch.Tensor, k: int = 5):
    import plotly.express as px

    p = to_cpu_f32(probs)
    top = torch.topk(p, k)
    labels = [repr(tok.decode([int(i)])) for i in top.indices.tolist()]
    fig = px.bar(
        x=labels,
        y=top.values.tolist(),
        labels={"x": "token", "y": "probability"},
        title=f"top-{k} next-token probabilities (last prompt position)",
    )
    fig.update_layout(yaxis_range=[0, 1])
    return fig


def plot_logit_lens(target: str, target_logits: list[float], ranks: list[int]):
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=2, subplot_titles=(f"logit of {target!r}", f"rank of {target!r} (1=top)"))
    xs = list(range(len(target_logits)))
    fig.add_trace(go.Scatter(x=xs, y=target_logits, mode="lines+markers", name="logit"), row=1, col=1)
    fig.add_trace(go.Scatter(x=xs, y=ranks, mode="lines+markers", name="rank"), row=1, col=2)
    fig.update_yaxes(type="log", row=1, col=2)
    fig.update_xaxes(title_text="layer")
    fig.update_layout(height=380, showlegend=False, title="logit lens (interactive)")
    return fig


def _symmetric_imshow(z, x, y, xlabel, ylabel, colorbar, title, height):
    """Diverging heatmap centred on 0.  Centring matters: on a sequential scale a
    head that *suppresses* the answer looks like a head that does nothing."""
    import plotly.express as px

    lim = float(np.abs(np.asarray(z)).max()) or 1.0
    fig = px.imshow(
        z,
        x=list(x),
        y=list(y),
        origin="lower",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        zmin=-lim,
        zmax=lim,
        labels={"x": xlabel, "y": ylabel, "color": colorbar},
        title=title,
    )
    fig.update_layout(height=height)
    return fig


def plot_patch_heatmap(sweep: dict, x_labels, title: str = "activation patching: layer x position"):
    """Heatmap of `patch_residual_sweep`.  1.0 = this single patch fully restored
    the clean answer; 0.0 = it changed nothing."""
    return _symmetric_imshow(
        sweep["recovered"],
        x=x_labels,
        y=sweep["layers"],
        xlabel="position (patched token)",
        ylabel="layer (residual after this block)",
        colorbar="recovered",
        title=title,
        height=620,
    )


def plot_head_attribution(attr: dict, title: str = "direct logit attribution per head"):
    """Heatmap of `component_attribution`.  Red writes the answer, blue writes
    against it."""
    heads = attr["heads"]
    return _symmetric_imshow(
        heads,
        x=list(range(heads.shape[1])),
        y=list(range(heads.shape[0])),
        xlabel="head",
        ylabel="layer",
        colorbar="logit diff",
        title=title,
        height=620,
    )


def plot_layer_attribution(attr: dict, title: str = "who writes the answer, by layer"):
    """Per-layer totals: attention (summed over heads) against MLP.  The heatmap
    hides the fact that MLPs often do most of the work."""
    import plotly.graph_objects as go

    heads_by_layer = attr["heads"].sum(axis=1)
    xs = list(range(len(heads_by_layer)))
    fig = go.Figure()
    fig.add_bar(x=xs, y=heads_by_layer, name="attention (all heads)")
    fig.add_bar(x=xs, y=attr["mlps"], name="MLP")
    fig.add_scatter(
        x=xs,
        y=np.cumsum(heads_by_layer + attr["mlps"]) + attr["embed"],
        name="running total",
        mode="lines",
        line=dict(color="#333", dash="dot"),
    )
    fig.update_layout(
        barmode="relative",
        height=420,
        title=title,
        xaxis_title="layer",
        yaxis_title="logit diff contributed",
    )
    return fig


def plot_patch_logits(answer: str, clean: float, corrupt: float, patched: float):
    import plotly.express as px

    fig = px.bar(
        x=["clean", "corrupt", "patch"],
        y=[clean, corrupt, patched],
        labels={"x": "run", "y": f"logit of {answer!r}"},
        title=f"activation patch: does copying residual restore {answer!r}?",
        color=["clean", "corrupt", "patch"],
    )
    return fig


def pca_two_clouds(a: torch.Tensor, b: torch.Tensor, label_a: str, label_b: str, title: str):
    """2D PCA of two sets of residual vectors (e.g. happy vs sad last-token h)."""
    from sklearn.decomposition import PCA

    xa, xb = to_cpu_f32(a), to_cpu_f32(b)
    X = torch.cat([xa, xb], 0).numpy()
    xy = PCA(n_components=2, random_state=0).fit_transform(X)
    fig, ax = plt.subplots(figsize=(5, 4))
    n = xa.shape[0]
    ax.scatter(xy[:n, 0], xy[:n, 1], label=label_a, alpha=0.85)
    ax.scatter(xy[n:, 0], xy[n:, 1], label=label_b, alpha=0.85)
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    return fig, ax

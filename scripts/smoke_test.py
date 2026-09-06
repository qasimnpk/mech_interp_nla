"""Correctness gate.  Nothing proceeds until this is green.

Run from the repo root:   uv run python -m scripts.smoke_test

Sections follow SETUP.md 4a-4f.  Actual values are printed, not just pass/fail.
Every model load and every prompt goes through src/model_utils, so this test
exercises the same code path the rest of the repo uses.
"""

from __future__ import annotations

import threading
import time

from src.model_utils import (  # noqa: F401 -- import sets MPS env before torch
    DEFAULT_REPO_ID,
    build_prompt,
    free,
    generate,
    get_blocks,
    get_ln_f,
    load_model,
    to_cpu_f32,
    rss_mb,
    tokenize,
    _block_output,
)

import torch
import transformers

REPO_ID = DEFAULT_REPO_ID

# Five short prompts for 4a.  Deliberately short: twenty CPU 4B forwards would eat
# the hour.
PROMPTS_5 = [
    "What is the capital of France?",
    "Name a primary color.",
    "2 + 2 =",
    "The opposite of hot is",
    "Write one word that rhymes with cat.",
]

# 4c: clearly unequal token counts after apply_chat_template (~4 vs ~20 tokens of
# content).  Equal lengths make the pad a no-op and the test vacuous.
PAD_SHORT = "Hi."
PAD_LONG = (
    "Please explain, in a single short sentence and using plain everyday language, "
    "why the sky appears blue to a person standing outside on a clear day."
)

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    print(f"\n>>> {name}: {'PASS' if ok else 'FAIL'} {detail}\n")


class PeakRSS:
    """Sample process RSS in the background; torch.mps.current_allocated_memory()
    undercounts and misses CPU-side float32 caches."""

    def __init__(self, interval: float = 0.25):
        self.peak = rss_mb()
        self._interval = interval
        self._stop = threading.Event()
        self._t = threading.Thread(target=self._run, daemon=True)
        self._t.start()

    def _run(self):
        while not self._stop.wait(self._interval):
            self.peak = max(self.peak, rss_mb())

    def stop(self) -> float:
        self._stop.set()
        self._t.join(timeout=2)
        self.peak = max(self.peak, rss_mb())
        return self.peak


def header(text: str) -> None:
    print("\n" + "=" * 78)
    print(text)
    print("=" * 78)


def last_pos_logits(model, tok, prompts, max_length=512) -> torch.Tensor:
    """One forward per prompt (no generate); logits at the final position, fp32/CPU."""
    device = next(model.parameters()).device
    out = []
    for p in prompts:
        enc = tokenize(tok, [p], max_length=max_length, device=str(device))
        with torch.inference_mode():
            logits = model(**enc).logits
        out.append(to_cpu_f32(logits[0, -1]))
    return torch.stack(out)


# ---------------------------------------------------------------- 0. environment
def section_env(peak: PeakRSS) -> None:
    header("0. Environment")
    print(f"torch             {torch.__version__}")
    print(f"transformers      {transformers.__version__}")
    print(f"mps.is_built()    {torch.backends.mps.is_built()}")
    print(f"mps.is_available() {torch.backends.mps.is_available()}")
    print(f"repo id           {REPO_ID}")
    print(f"RSS at start      {rss_mb():.0f} MiB")


# --------------------------------------------- 4a-0. MPS device-transfer sanity
def section_4a0() -> None:
    """Guard the torch 2.13 MPS bug that to_cpu_f32() exists to work around.

    Not a model check -- a plain-tensor check, so it is unambiguous.  If a future
    torch fixes the bug this prints "workaround no longer needed" and still passes;
    if a future torch breaks the *safe* path too, this fails loudly here rather
    than showing up as mysterious logits later.
    """
    header("4a-0. MPS device+dtype transfer sanity (plain tensors)")
    ok = True
    for dt in (torch.bfloat16, torch.float16, torch.float32):
        a = torch.arange(20, dtype=dt, device="mps").reshape(2, 10)
        want = list(range(10, 20))
        safe = a[1].float().cpu().tolist()
        combined = a[1].to("cpu", torch.float32).tolist()
        buggy = combined != want
        print(f"  {str(dt):16s} .float().cpu() {'OK' if safe == want else 'BROKEN'}   "
              f"combined .to('cpu', f32) {'MISREADS OFFSET' if buggy else 'ok'}")
        if buggy:
            print(f"      got {combined}")
            print(f"      want {want}")
        if safe != want:
            ok = False
    print("\n  to_cpu_f32() casts on-device first; the combined form is never used in "
          "this repo.")
    print("  If every row above says 'ok', the torch bug is fixed and the workaround "
          "is no longer needed.")
    record("4a-0  safe device transfer path is correct", ok, "")
    if not ok:
        raise SystemExit("even the cast-first transfer path is wrong -- stop")


# ------------------------------------------------------------------ 4a. CPU vs MPS
def section_4a(peak: PeakRSS):
    header("4a. CPU vs MPS logits  (five prompts, one forward each)")
    print("Loading on CPU (bf16)...")
    t0 = time.time()
    model, tok = load_model(REPO_ID, dtype=torch.bfloat16, device="cpu")
    print(f"  loaded in {time.time() - t0:.1f}s, RSS {rss_mb():.0f} MiB")

    cfg = model.config
    print("\n--- model.config checks ---")
    print(f"  model_type            {cfg.model_type}")
    print(f"  num_hidden_layers     {cfg.num_hidden_layers}")
    print(f"  hidden_size           {cfg.hidden_size}")
    print(f"  vocab_size            {cfg.vocab_size}")
    print(f"  num_attention_heads   {cfg.num_attention_heads}")
    print(f"  num_key_value_heads   {getattr(cfg, 'num_key_value_heads', None)}")
    print(f"  max_position_embeddings {cfg.max_position_embeddings}")
    print(f"  vision tower present  {hasattr(cfg, 'vision_config')}")
    layer_types = getattr(cfg, "layer_types", None)
    print(f"  layer_types           {set(layer_types) if layer_types else 'None (uniform)'}")
    bad = [k for k in ("linear_attention", "deltanet", "ssm", "mamba", "hybrid")
           if k in str(cfg.to_dict()).lower()]
    print(f"  non-softmax-attention markers in config: {bad or 'none'}")
    arch_ok = (
        cfg.model_type == "qwen3"
        and not hasattr(cfg, "vision_config")
        and not bad
        and (layer_types is None or set(layer_types) <= {"full_attention"})
    )
    record("4a-arch  standard softmax attention, no vision tower", arch_ok,
           f"(model_type={cfg.model_type}, layers={cfg.num_hidden_layers}, "
           f"hidden={cfg.hidden_size}, vocab={cfg.vocab_size})")
    if not arch_ok:
        raise SystemExit("architecture check failed -- stopping per SETUP.md 2")

    print("\nCPU forwards...")
    t0 = time.time()
    cpu_logits = last_pos_logits(model, tok, PROMPTS_5)
    print(f"  {len(PROMPTS_5)} CPU forwards in {time.time() - t0:.1f}s")
    free(model)
    del tok

    print("\nLoading on MPS (bf16)...")
    t0 = time.time()
    model, tok = load_model(REPO_ID, dtype=torch.bfloat16, device="mps")
    print(f"  loaded in {time.time() - t0:.1f}s, RSS {rss_mb():.0f} MiB")
    t0 = time.time()
    mps_logits = last_pos_logits(model, tok, PROMPTS_5)
    print(f"  {len(PROMPTS_5)} MPS forwards in {time.time() - t0:.1f}s")

    print("\n  prompt                              max|d|    mean|d|  argmax  CPU top1-top2")
    failures = []
    for i, p in enumerate(PROMPTS_5):
        d = (cpu_logits[i] - mps_logits[i]).abs()
        top2 = cpu_logits[i].topk(2).values
        margin = (top2[0] - top2[1]).item()
        c_arg = cpu_logits[i].argmax().item()
        m_arg = mps_logits[i].argmax().item()
        match = c_arg == m_arg
        note = ""
        if not match:
            note = f"  CPU:{tok.decode([c_arg])!r} MPS:{tok.decode([m_arg])!r}"
            if margin > 0.5:
                failures.append(f"prompt {i}: argmax mismatch with comfortable CPU margin {margin:.3f}")
            else:
                note += "  <- close call, not a fail"
        if d.max().item() > 1.0:
            failures.append(f"prompt {i}: max|dlogit| {d.max().item():.3f} > 1")
        print(f"  {p[:34]:34s} {d.max().item():8.4f} {d.mean().item():9.4f}  "
              f"{str(match):6s}  {margin:8.3f}{note}")

    record("4a  CPU vs MPS logits", not failures,
           "" if not failures else " | ".join(failures))
    if failures:
        raise SystemExit(
            "4a failed -- MPS numerics are suspect.  Stopping rather than silently "
            "falling back to CPU (a 4B fp32 CPU forward is too slow to work on all day); "
            "this needs a decision."
        )
    return model, tok


# ---------------------------------------------------------------- 4b. chat template
def section_4b(model, tok) -> None:
    header("4b. Chat template")
    text = build_prompt(tok, PROMPTS_5[0])
    print("decoded prompt string (repr, so the newlines are visible):")
    print(repr(text))
    print("\nas printed:")
    print(text)
    ids = tok(text, add_special_tokens=False)["input_ids"]
    tail = [tok.decode([t]) for t in ids[-6:]]
    print(f"\nlast 6 tokens: {tail}")
    print(f"final token   : {tail[-1]!r}  <- must belong to the assistant-turn prefix, "
          "not the last user token")
    no_think = "<think>" not in text
    ends_assistant = "assistant" in text[-40:]
    record("4b  template: assistant prefix present, no <think> block",
           no_think and ends_assistant,
           f"(<think> present: {not no_think}; assistant prefix in tail: {ends_assistant})")


# --------------------------------------------------------------------- 4c. padding
def section_4c(model, tok) -> None:
    """Padding must not perturb the hidden state at position -1.

    DEVIATION FROM SETUP.md, stated deliberately: the spec asks for atol 1e-3, but
    that tolerance is sized for values of magnitude ~1.  Final-layer hidden states
    here reach |h| ~ 70, and one bf16 ULP at that magnitude is 0.5 -- 500x the
    requested tolerance.  No correct bf16 implementation can pass 1e-3 on these
    values, so the criterion is expressed in ULP instead, plus a control that
    actually separates a padding bug from dtype noise.

    The control: a real padding bug (wrong position_ids, pads attended to) grows
    with the number of pad tokens.  Noise does not.  We therefore pad the short
    prompt to two different lengths and check the delta does not scale.

    Confirmed separately in fp32 (scripts/diag7.py), where the tolerance IS
    meaningful: single-vs-batch max|d| = 1.5e-4 on a scale of 70.7.  Padding is inert.
    """
    header("4c. Padding")
    device = next(model.parameters()).device
    n_short = len(tok(build_prompt(tok, PAD_SHORT), add_special_tokens=False)["input_ids"])
    n_long = len(tok(build_prompt(tok, PAD_LONG), add_special_tokens=False)["input_ids"])
    print(f"token counts after apply_chat_template: short={n_short}  long={n_long}  "
          f"(delta {n_long - n_short})")

    def hidden_last(prompts):
        enc = tokenize(tok, prompts, device=str(device))
        with torch.inference_mode():
            out = model(**enc, output_hidden_states=True)
        return to_cpu_f32(out.hidden_states[-1][:, -1]), enc

    solo_s, _ = hidden_last([PAD_SHORT])
    solo_l, _ = hidden_last([PAD_LONG])
    batch, enc = hidden_last([PAD_SHORT, PAD_LONG])
    print(f"batched input_ids shape: {tuple(enc['input_ids'].shape)}  "
          f"(padding_side={tok.padding_side})")

    ds = (solo_s[0] - batch[0]).abs().max().item()
    dl = (solo_l[0] - batch[1]).abs().max().item()
    scale = batch.abs().max().item()

    # one bf16 ULP at the observed magnitude
    v = torch.tensor(scale, dtype=torch.bfloat16)
    ulp = (torch.nextafter(v, torch.tensor(float("inf"), dtype=torch.bfloat16)) - v).item()

    print(f"max|d| short single-vs-batch: {ds:.6f}   ({ds / ulp:.2f} ULP)")
    print(f"max|d| long  single-vs-batch: {dl:.6f}   ({dl / ulp:.2f} ULP)")
    print(f"hidden-state scale max|h| = {scale:.2f}; one bf16 ULP there = {ulp:.4f}")
    print(f"(SETUP.md's atol 1e-3 is {ulp / 1e-3:.0f}x finer than bf16 can represent "
          f"at this magnitude -- see the docstring)")

    # control: does the delta grow with the amount of padding?
    filler = PAD_LONG + " Also mention that this sentence exists only to make the " \
             "second prompt in the batch substantially longer than the first one."
    n_filler = len(tok(build_prompt(tok, filler), add_special_tokens=False)["input_ids"])
    batch2, enc2 = hidden_last([PAD_SHORT, filler])
    ds2 = (solo_s[0] - batch2[0]).abs().max().item()
    pads1, pads2 = n_long - n_short, n_filler - n_short
    print(f"\npad-length control: short padded by {pads1} tokens -> max|d| {ds:.4f}")
    print(f"                    short padded by {pads2} tokens -> max|d| {ds2:.4f}")
    print("                    a real padding bug scales with pad count; noise does not")

    within_ulp = ds <= 2 * ulp and dl <= 2 * ulp and ds2 <= 2 * ulp
    grew = ds2 > max(3 * ds, 3 * ulp)
    record("4c  padding does not perturb position -1 "
           "(<=2 bf16 ULP, and delta does not scale with pad count)",
           within_ulp and not grew,
           f"(short {ds / ulp:.2f} ULP, long {dl / ulp:.2f} ULP, "
           f"{pads2}-pad {ds2 / ulp:.2f} ULP)")


# ------------------------------------------------------------------ 4d. hook fires
def section_4d(model, tok) -> None:
    header("4d. Hook fires on the decoder block")
    blocks = get_blocks(model)
    mid = len(blocks) // 2
    print(f"blocks resolved dynamically: {type(blocks).__name__} of {len(blocks)}; "
          f"hooking index {mid} ({type(blocks[mid]).__name__})")
    device = next(model.parameters()).device
    n_hooks_before = len(blocks[mid]._forward_hooks)
    print(f"pre-existing forward hooks on the block: {n_hooks_before} "
          f"(accelerate's device_map installs its own; the baseline is not zero)")
    seen = {}

    def hook(_m, _i, output):
        seen["shape"] = tuple(_block_output(output).shape)
        seen["dtype"] = _block_output(output).dtype

    h = blocks[mid].register_forward_hook(hook)
    try:
        enc = tokenize(tok, [PAD_SHORT, PAD_LONG], device=str(device))
        with torch.inference_mode():
            model(**enc)
    finally:
        h.remove()

    b, s = enc["input_ids"].shape
    want = (b, s, model.config.hidden_size)
    print(f"hook output shape {seen.get('shape')}  dtype {seen.get('dtype')}")
    print(f"expected          {want}  [batch, seq, hidden_size]")
    n_hooks_after = len(blocks[mid]._forward_hooks)
    print(f"hook removed; forward hooks {n_hooks_before} -> {n_hooks_after} "
          f"(must return to the baseline)")
    record("4d  decoder-block hook fires with [batch, seq, hidden] and is removed",
           seen.get("shape") == want and n_hooks_after == n_hooks_before,
           f"(got {seen.get('shape')}, hooks {n_hooks_before}->{n_hooks_after})")


# ----------------------------------------------------------------- 4e. logit lens
def section_4e(model, tok) -> None:
    header("4e. Logit lens")
    blocks = get_blocks(model)
    ln_f = get_ln_f(model)
    unembed = model.lm_head
    print(f"resid_final = output of blocks[{len(blocks) - 1}] (pre-norm)")
    print(f"ln_f        = {type(ln_f).__name__}")
    print(f"unembed     = {type(unembed).__name__}  {tuple(unembed.weight.shape)}")

    device = next(model.parameters()).device
    grab = {}

    def hook(_m, _i, output):
        grab["resid"] = _block_output(output).detach()

    h = blocks[-1].register_forward_hook(hook)
    try:
        enc = tokenize(tok, [PROMPTS_5[0]], device=str(device))
        with torch.inference_mode():
            logits = model(**enc).logits
    finally:
        h.remove()

    resid = grab["resid"]
    with torch.inference_mode():
        with_norm = unembed(ln_f(resid))
        without_norm = unembed(resid)

    a = to_cpu_f32(logits)
    b = to_cpu_f32(with_norm)
    c = to_cpu_f32(without_norm)
    err_norm = (a - b).abs().max().item()
    err_raw = (a - c).abs().max().item()
    ratio = err_raw / max(err_norm, 1e-9)
    print(f"\nmax|unembed(ln_f(resid)) - logits|  = {err_norm:.6f}")
    print(f"max|unembed(resid)       - logits|  = {err_raw:.6f}")
    print(f"ratio (no-norm / with-norm)         = {ratio:.1f}x  (want >= 10x)")
    ok = err_norm < 1e-3 and ratio >= 10
    record("4e  logit lens reconstructs logits through ln_f, and ln_f matters", ok,
           f"(err_norm {err_norm:.2e}, ratio {ratio:.1f}x)")


# ------------------------------------------------------- 4f. throughput and memory
def section_4f(model, tok, peak: PeakRSS) -> None:
    header("4f. Throughput and memory")
    for bs in (1, 8):
        prompts = [PROMPTS_5[i % len(PROMPTS_5)] for i in range(bs)]
        generate(model, tok, prompts[:1], max_new_tokens=4)  # warm the kernels
        t0 = time.time()
        outs = generate(model, tok, prompts, max_new_tokens=16)
        dt = time.time() - t0
        n_tok = 16 * bs
        print(f"batch {bs:>2}  max_new_tokens=16  {dt:6.2f}s  "
              f"{n_tok / dt:7.2f} tok/s total  {16 / dt:6.2f} tok/s per sequence")
        if bs == 1:
            print(f"          sample completion: {outs[0]!r}")
    print(f"\npeak process RSS so far: {peak.peak:.0f} MiB ({peak.peak / 1024:.2f} GiB)")
    record("4f  throughput and memory measured", True, "")


def main() -> None:
    peak = PeakRSS()
    section_env(peak)
    section_4a0()
    model, tok = section_4a(peak)
    section_4b(model, tok)
    section_4c(model, tok)
    section_4d(model, tok)
    section_4e(model, tok)
    section_4f(model, tok, peak)

    header("Summary")
    for name, ok, detail in RESULTS:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    p = peak.stop()
    print(f"\npeak process RSS: {p:.0f} MiB ({p / 1024:.2f} GiB)")
    green = all(ok for _, ok, _ in RESULTS)
    print(f"\nGATE: {'GREEN' if green else 'RED'}")
    raise SystemExit(0 if green else 1)


if __name__ == "__main__":
    main()

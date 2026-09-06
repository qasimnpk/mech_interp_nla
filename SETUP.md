# SETUP.md

Bootstrap for local mech-interp work. Work top to bottom. Stop at section 5.

**Machine:** MacBook Pro, M4 Pro, 48 GB unified memory, macOS. MPS backend, no CUDA.
**Goal:** a verified-correct environment. Not a research library, not experiments.
**Budget:** ~1 hour. If you're past it, stop and report where you are.

---

## 0. Rules

- No CUDA-only packages: `bitsandbytes`, `flash-attn`, `vllm`, `xformers`, `triton`.
- **No MLX / `mlx-lm`.** Faster on Apple Silicon, but invalidates every PyTorch-hook
  tutorial this repo depends on.
- HuggingFace `transformers` + raw forward hooks. **Do not install `transformer_lens`
  in this pass** — it is for ARENA notebooks the human runs later, on GPT-2/CPU.
- `trust_remote_code=True` should not be needed. If `AutoModel` demands it, upgrade
  `transformers` once, then stop and report if it still does.
- Say when you're guessing. Verify signatures rather than writing plausible code that
  fails two sections later.

## 1. Environment

`uv init` **in place** — do not overwrite existing files. Python 3.12.

```
torch>=2.9  transformers  accelerate  safetensors  huggingface_hub
scikit-learn  numpy  pandas  matplotlib
ipython  ipykernel  datasets  einops  tqdm
```

Pin `torch` and `transformers` in `pyproject.toml`. No CUDA index URL.
`.gitignore`: `.venv/`, `figures/`, `artifacts/`, `*.pt`, HF cache.

Env vars set only in your setup shell will not exist in a later IPython session, and
the smoke test would then pass under different settings than everything after it. Write
`scripts/env.sh` for shell use:

```sh
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.8   # not 0.0 — lifting the cap can hang the machine
# also enable fallback logging if your torch version supports it (check PYTORCH_DEBUG_MPS_FALLBACK):
# silent CPU fallback inside a hook loop is a 100x slowdown that looks like nothing
```

But **do not try to `source` it from Python** — a subprocess `source` dies with the
child and sets nothing in the parent. `src/model_utils.py` must parse `env.sh` (or just
duplicate the exports) and write `os.environ` **in-process, above `import torch`**;
these are read at import and first MPS use, so setting them afterward is a no-op that
looks like it worked.

Print `torch.__version__`, `torch.backends.mps.is_built()`, `is_available()`. Run
`df -h ~/.cache/huggingface` — that's where `hf download` puts weights unless `HF_HOME`
is set, and it runs to tens of GB.

## 2. Model — exact ID, no substitution

Use **`Qwen/Qwen3-4B-Instruct-2507`**. Cache with `hf download` (downloads without loading).

If that ID 404s, **stop and report**. Do not pick a cousin. Specifically:
`Qwen/Qwen3-4B` is a *different* model whose chat template defaults to
`enable_thinking=True`, and the Qwen 3.5 line is hybrid-attention and multimodal —
either would silently break the tutorials while passing a casual config check.

After loading, print `model.config` and confirm: standard softmax attention on every
layer (no DeltaNet / linear-attention / SSM / hybrid), no vision tower,
`num_hidden_layers`, `hidden_size`, `vocab_size`. Stop if any check fails.

2507 is instruct-only, so `enable_thinking=False` may be unsupported — try it, and drop
the kwarg if the tokenizer errors. Either way, print the decoded prompt and confirm
there is no `<think>` block.

Do **not** download or load a second model today.

## 3. Utilities — write these first

`src/model_utils.py`. The smoke test **imports** these; do not inline a second loader
in the test, or the two will drift on dtype, template, and attention implementation.

Make the import work before writing anything else: `src` gets an `__init__.py`, the
test does `from src.model_utils import load_model`, and everything runs via `uv run`
from the repo root. The common failure is writing `from model_utils import ...`, hitting
an ImportError, and "solving" it by pasting a second loader into the test.

```python
load_model(repo_id, dtype=torch.bfloat16, device="mps")   # -> (model, tok)
free(model)                                                # then verify RSS actually dropped
cache_residual(model, tok, prompts, layers, max_length=512, batch_size=8)
generate(model, tok, prompts, max_new_tokens)              # greedy
```

- `load_model` sets the env vars in-process above `import torch` (see §1), calls
  `model.eval()`, sets `tokenizer.padding_side="left"` and `pad_token` if missing (Qwen
  often reuses EOS), and defaults to SDPA attention. Eager is only needed for
  `output_attentions=True` and is a real speed tax on MPS — per-call argument, not global.
- All forwards run under `torch.inference_mode()`. Autograd buffers on a 4B are memory
  you don't have.
- `cache_residual` and `generate` both apply the chat template with
  `add_generation_prompt=True`. If they take raw strings while the smoke test uses the
  template, every later cell disagrees with the test that validated it.
- `cache_residual` returns the **last non-pad position only**: `[n_prompts, hidden]`,
  float32, on CPU. Not the full `[n, seq, hidden]` cube unless explicitly asked.
- `generate` is greedy. MPS sampling plus seeded reproducibility is a separate mess.
- `max_length` is a required cap. Uncapped batching OOMs.
- Every hook removed in a `finally:` block.
- `free()` often does not return unified memory to macOS. Check RSS; if it hasn't
  dropped, restart the kernel rather than loading anything else.

## 4. Correctness gate — `scripts/smoke_test.py`

Nothing proceeds until this is green. Print actual values, not just pass/fail.

**4a. CPU vs MPS logits.** The critical check: MPS has a history of silent numerical
bugs producing plausible-but-wrong logits. Coherent text does not rule this out.

- **Five short prompts, one forward each.** No `generate()`. Twenty prompts of CPU 4B
  forwards would eat the hour.
- Build prompts through the **same chat-template and left-pad path the helpers use**.
  Raw strings here would be testing a different code path than the rest of the repo.
- Load on CPU → save logits → `free()` → load on MPS. Never both resident at once.
- Report per prompt: max `|Δlogit|`, mean `|Δlogit|`, argmax match, and the CPU
  **top1 − top2 margin** on any mismatch.
- **Fail only if** argmax disagrees *and* the CPU margin was comfortable (`> 0.5`), or
  max `|Δlogit| > 1`. Otherwise print "close call, not a fail."
- Do not require bit-exact argmax agreement. CPU bf16 frequently computes in fp32
  internally, so the two devices are running different numerics even when both are
  healthy; a near-tied two-way race flipping is not a GELU bug. The margin criterion is
  what separates noise from a real defect — matching dtypes does not.
- If it genuinely fails: **stop and report.** Do not silently fall back to CPU; a 4B
  fp32 CPU forward is too slow to work on all day, so this needs a decision.

**4b. Chat template.** Build the prompt via `apply_chat_template`. **Print the decoded
prompt string.** On an instruct model the final token belongs to the assistant-turn
prefix, not the last user token — probes and steering silently target the wrong
position otherwise.

**4c. Padding.** Batch two prompts whose token counts are **clearly unequal after
`apply_chat_template`** (roughly 4 vs 20 tokens of content) — equal lengths make the pad
a no-op and the test vacuous, and the template adds a fixed prefix to both. The
single-run and in-batch hidden states at position `-1` must match to `atol≈1e-3` (bf16
has ~3 decimal digits; `1e-6` is not achievable).

**4d. Hook fires.** Hook the **decoder block** — the module whose output is the
residual stream after the block (Qwen: `model.model.layers[i]`), resolved dynamically
rather than hardcoded. Not `mlp`, not `input_layernorm`. Mid layer (`n_layers // 2`).
Confirm shape `[batch, seq, hidden_size]`.

Register a **temporary** hook inside this check and remove it. Do not route this through
`cache_residual`, and do not widen `cache_residual` to return the full cube in order to
make this pass — it returns `[n_prompts, hidden]` by design.

**4e. Logit lens.** Unembedding the *post*-final-norm residual trivially reproduces the
logits, so that alone tests nothing. Definitions, since getting these wrong makes the
check impossible rather than failing loudly: `resid_final` is the **last decoder block's
output, before `model.model.norm`**; `ln_f` is that norm; `unembed` is `model.lm_head`.
If you hook post-norm you cannot run the second check at all.

- `unembed(ln_f(resid_final))` vs `model(...).logits`: `allclose` at `atol≈1e-3`
- `unembed(resid_final)` without `ln_f`: max-abs error at least **10x larger**

Do not test this by argmax. Pre-norm residual often stays directionally aligned enough
that the top token still matches on easy prompts with a correct implementation.

**4f. Throughput and memory.** tok/s at batch 1 and 8, **`max_new_tokens=16`** — batch-8
greedy decoding to 512 tokens is how a careful file overruns its budget at the last step.
Peak memory as process **RSS** (`ps` or `memory_profiler`) —
`torch.mps.current_allocated_memory()` undercounts and misses CPU-side float32 caches.

## 5. Report and stop

Write `notes/environment.md`: exact repo ID, torch/transformers versions, full
smoke-test output including the CPU-vs-MPS numbers, tok/s, peak RSS, and any
workarounds. Then stop.

---

## Deferred — not in this pass

- **Steering helpers.** Pre- vs post-layer, which token positions, prompt-only vs every
  decode step are different experiments; that gets specified deliberately.
- **A second or larger model.**
- **Any experiment or result.**
- **Persistent kernel.** A green smoke test matters more for this hour. Afterward the
  human starts `uv run ipython` in `tmux new -s kernel` by hand. If an agent later
  drives that pane: start tmux after `uv` is on PATH, send single-line commands only,
  and poll `capture-pane` for a printed completion marker after each load — never
  `sleep N`, which captures a partial pane and proceeds on truncated output.

## Tutorials — after this pass, run by the human, not the setup agent

Nothing here is part of the setup pass. Do not install `transformer_lens` or touch
ARENA while working through sections 1–5.

Afterward: ARENA 1.2 runs as written, `transformer_lens` on **GPT-2 small**, with
`device="cpu"` passed explicitly — TransformerLens auto-selects a device and will pick
MPS on this machine, which would quietly undo the 4a gate. GPT-2 small is 124M params,
so CPU is fast enough. The old-models rule applies to results that go in the write-up,
not to learning a technique; do not rewrite the curriculum to avoid GPT-2. Raw hooks on
Qwen3-4B/MPS are for the afternoon experiment.

## Memory budget

One pool shared with macOS, the editor, and the browser. Plan against **~28–32 GB**
usable, not 40. A 4B in bf16 is ~8 GB of weights; `.to(device)` after a CPU load can
peak near 2x that during the copy, so prefer mapping safetensors straight to the device.
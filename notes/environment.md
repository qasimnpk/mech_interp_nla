# Environment

Setup pass for `SETUP.md` sections 1-5, completed 2026-08-27. **Gate: GREEN.**
Full smoke-test output is in `notes/smoke_test_output.txt`; the summary below quotes it.

## Machine and toolchain

| | |
|---|---|
| Machine | MacBook Pro, Apple M4 Pro, 48 GB unified memory |
| macOS | 15.7.4 |
| uv | 0.12.6 (installed via Homebrew during this pass -- it was not present) |
| Python | 3.12.14 |
| torch | **2.13.0** (pinned) |
| transformers | **5.16.1** (pinned) |
| accelerate | 1.14.0 |
| numpy | 2.5.2 |
| MPS | `is_built()` True, `is_available()` True. No CUDA packages installed. |

`torch` and `transformers` are pinned exactly in `pyproject.toml`; no CUDA index URL.
`.gitignore` covers `.venv/`, `figures/`, `artifacts/`, `*.pt`, and HF-cache paths.
The repo was `git init`-ed; nothing has been committed.

## Model

`Qwen/Qwen3-4B-Instruct-2507` -- the exact ID, no substitution. It resolved on the Hub,
so no stop-and-report was needed.

Cached with `hf download` into `~/.cache/huggingface` (**`HF_HOME` is not set**):

- model cache size: **7.5 GB**
- `df -h ~/.cache/huggingface`: 460 GiB total, **197 GiB available** after the download

Config checks, all confirmed from `model.config`:

- `model_type = qwen3`, `layer_types = {'full_attention'}` -- standard softmax attention
  on every layer; no DeltaNet / linear-attention / SSM / hybrid markers anywhere in the config
- no `vision_config` -- no vision tower
- `num_hidden_layers = 36`, `hidden_size = 2560`, `vocab_size = 151936`
- `num_attention_heads = 32`, `num_key_value_heads = 8` (GQA), `max_position_embeddings = 262144`

`trust_remote_code` was never needed. Only this one model was downloaded or loaded.

### Chat template

`enable_thinking=False` is **accepted** by this tokenizer (no error), and the decoded
prompt contains no `<think>` block either way:

```
'<|im_start|>user\nWhat is the capital of France?<|im_end|>\n<|im_start|>assistant\n'
```

Last 6 tokens: `['?', '<|im_end|>', '\n', '<|im_start|>', 'assistant', '\n']`. The final
token is the newline of the **assistant-turn prefix**, not the last user token -- so
position `-1` is the right target for probes and steering.

## Layout

```
src/model_utils.py   the only loader: load_model / free / cache_residual / generate
                     (+ to_cpu_f32, tokenize, get_blocks, get_ln_f, rss_mb)
scripts/env.sh       shell-side MPS env vars
scripts/smoke_test.py            the correctness gate, sections 4a-4f
scripts/mps_transfer_bug_repro.py  standalone reproducer for the torch bug below
notes/               this file + captured smoke-test output
```

**Run everything with `-m` from the repo root:** `uv run python -m scripts.smoke_test`.
Not `uv run python scripts/smoke_test.py` -- that puts `scripts/` on `sys.path` instead of
the repo root and `from src.model_utils import ...` fails. (Hit during this pass.)

## Smoke test results

| check | result | numbers |
|---|---|---|
| 4a-0 MPS transfer sanity | PASS | added check, see workaround 3 below |
| 4a-arch config | PASS | qwen3, 36 layers, hidden 2560, vocab 151936 |
| 4a CPU vs MPS logits | PASS | see table |
| 4b chat template | PASS | assistant prefix present, no `<think>` |
| 4c padding | PASS | 1.00-1.50 bf16 ULP |
| 4d hook fires | PASS | `(2, 37, 2560)`, hooks 1 -> 1 |
| 4e logit lens | PASS | err 0.000000 vs 155.39 without `ln_f` |
| 4f throughput/memory | PASS | see below |

### 4a -- CPU vs MPS logits (five prompts, one forward each, bf16 both sides)

```
  prompt                              max|d|    mean|d|  argmax  CPU top1-top2
  What is the capital of France?       0.2500    0.0521  True      21.750
  Name a primary color.                0.3750    0.0438  True       2.750
  2 + 2 =                              0.3750    0.0407  True      19.125
  The opposite of hot is               0.3086    0.0671  True      22.000
  Write one word that rhymes with ca   0.2930    0.0436  True       0.375
```

Argmax agrees on all five; max `|dlogit|` <= 0.375, far under the 1.0 threshold. Prompts
are built through the same chat-template and left-pad path the helpers use. CPU logits are
saved, the CPU model is freed, and only then is the MPS model loaded -- never both resident.

### 4c -- padding

`short=10` vs `long=37` tokens after `apply_chat_template` (delta 27), batch `(2, 37)`,
`padding_side=left`. Single-run vs in-batch hidden state at position `-1`:

```
short: max|d| 0.750000  (1.50 ULP)
long : max|d| 0.500000  (1.00 ULP)
scale: max|h| = 70.50; one bf16 ULP at that magnitude = 0.5000
pad-length control: short padded by 27 tokens -> 0.7500
                    short padded by 49 tokens -> 0.4375
```

**Deviation from SETUP.md, deliberate.** The spec asks for `atol 1e-3`. That is
arithmetically unreachable here: final-layer hidden states reach `|h| ~ 70`, where one bf16
ULP is `0.5` -- 500x coarser than the requested tolerance. No correct bf16 implementation
can pass it on these values. The criterion is therefore expressed in ULP (`<= 2 ULP`), plus
a control that actually discriminates: a real padding bug (wrong `position_ids`, pads being
attended to) grows with the number of pad tokens, whereas noise does not. Padding the short
prompt by 49 tokens instead of 27 gave a *smaller* delta, so it is noise.

Confirmed independently in **fp32**, where the spec's tolerance *is* meaningful:
single-vs-batch `max|d| = 1.5e-4` on a scale of 70.7. Padding is inert; the bf16 numbers are
dtype resolution, not a defect.

### 4e -- logit lens

`resid_final` = output of `blocks[35]`, **before** `model.model.norm`; `ln_f` = `Qwen3RMSNorm`;
`unembed` = `model.lm_head` `(151936, 2560)`.

```
max|unembed(ln_f(resid)) - logits|  = 0.000000
max|unembed(resid)       - logits|  = 155.390625
```

Tested by error magnitude, not argmax, as specified.

### 4f -- throughput and memory

```
batch 1  max_new_tokens=16   0.37s   42.92 tok/s total   42.92 tok/s per sequence
batch 8  max_new_tokens=16   2.95s   43.37 tok/s total    5.42 tok/s per sequence
sample completion (batch 1): 'The capital of France is Paris.'
```

**Peak process RSS: 8499 MiB (8.30 GiB)**, measured by sampling `ps` from a background
thread. Comfortably inside the ~28-32 GB usable budget; there is room for a second model
later, though that is out of scope for this pass.

`free()` does return the memory here: RSS `8402 -> 729 MiB`. Verified on every call.

## Workarounds and gotchas found during this pass

**1. `PYTORCH_MPS_LOW_WATERMARK_RATIO` must be set alongside the high watermark.**
SETUP.md specifies `PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.8`. Setting only that raises

```
RuntimeError: invalid low watermark ratio 1.4
```

at the first allocator call (the low watermark keeps its default of 1.4 and must be
`<=` the high one). `scripts/env.sh` and `model_utils` now set
`PYTORCH_MPS_LOW_WATERMARK_RATIO=0.7` as well. Set both or neither.

**2. `PYTORCH_DEBUG_MPS_FALLBACK` does not exist in torch 2.13.0.** Scanning
`torch/lib/*.dylib` for the string finds only `PYTORCH_ENABLE_MPS_FALLBACK`,
`PYTORCH_MPS_HIGH_WATERMARK_RATIO` and `PYTORCH_MPS_LOW_WATERMARK_RATIO`. There is no
env-var route to fallback logging on this build. To catch a silent CPU fallback inside a
hook loop, temporarily set `PYTORCH_ENABLE_MPS_FALLBACK=0` so the unsupported op raises
instead of falling back.

**3. Silent MPS numerical bug in torch 2.13.0 -- caught by the 4a gate.**
This is exactly the failure mode section 4a exists for, and it did fire: the first green-CPU
run produced `'!'` as the top token on four of five prompts and one `inf` logit on MPS.

The cause was **not** the model or the load path, but a combined device+dtype copy:

```python
a = torch.arange(20, dtype=torch.bfloat16, device="mps").reshape(2, 10)
a[1].to("cpu", torch.float32)   # -> [15,16,17,18,19, 0,0,0,0,0]   WRONG
a[1].float().cpu()              # -> [10,11,...,19]                correct
```

`a[1]` has storage offset 10 elements = 20 bytes; the copy applies that offset in the
**destination** element size (20/4 = element 5). Characterisation:

- affects 2-byte source dtypes -- **bf16 and fp16** -- going to fp32 on CPU; fp32 sources are fine
- only with a **nonzero storage offset**, which is exactly what `logits[0, -1]` and
  `h[:, -1]` are
- `.contiguous()` does **not** help (the view is already contiguous, merely offset)
- `.clone()` helps; casting on-device first (`.float().cpu()`) or copying first
  (`.cpu().float()`) are both correct

Workaround: `src/model_utils.to_cpu_f32()` casts on-device first and is used at every such
site in the repo. **Do not "simplify" it back to `.to("cpu", torch.float32)`.**
`scripts/mps_transfer_bug_repro.py` is a standalone reproducer, and smoke-test section
**4a-0** asserts the safe path still works on plain tensors -- it also prints whether the
combined form is still broken, so a future torch upgrade will say whether the workaround
can be dropped.

**4. `device_map=` leaves an accelerate hook on every block.** Blocks carry 1 pre-existing
forward hook (accelerate's `AlignDevicesHook`), so "zero hooks after removal" is the wrong
assertion; 4d compares against the baseline instead. Worth knowing before debugging your
own hook bookkeeping.

**5. transformers 5.x renamed the load kwarg.** It is `dtype=`, not `torch_dtype=`, and
`low_cpu_mem_usage` is gone. `load_model` passes `device_map=device` so the safetensors map
straight onto the target device rather than peaking near 2x during a `.to()` copy.

## Verified but not part of the gate

`cache_residual` (4d deliberately does not route through it) was checked separately: returns
`[n_prompts, hidden]` float32 on CPU for both an `int` and a `list` layer argument, and
matches an independent single-prompt hook to `max|d| = 0.25` at scale 29.6 -- exactly 1 bf16 ULP.

## Deferred, per SETUP.md

Steering helpers; a second or larger model; any experiment or result; a persistent tmux
kernel. `transformer_lens` is **not** installed -- when ARENA 1.2 is run later it goes on
GPT-2 small with `device="cpu"` passed explicitly, since TransformerLens would otherwise
auto-select MPS and quietly undo the 4a gate.

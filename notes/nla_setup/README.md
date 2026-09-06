# NLA checkpoint setup log (2026-09-06)

Exploratory setup for two released natural-language-autoencoder (NLA) checkpoint families on the
M4 Pro / 48 GB box. Agent-built; every number below was produced in this session and the raw
outputs sit next to this file (`*_out.json`). Re-derive before quoting.

## Hardware and environments
- MacBook Pro, Apple M4 Pro, 48 GB unified memory, ~135 GB free disk at start. No CUDA.
- Main checkout venv (`uv`, Python 3.12): torch 2.13.0, transformers 5.16.1, **peft 0.20.0 and
  optimum-quanto 0.2.7 added** (`uv add peft optimum-quanto`).
- kitft repo cloned to `~/tools/natural_language_autoencoders` (commit 0577769, 2026-08-02) with its
  own venv (`uv venv -p 3.12`; torch 2.14.0, transformers 5.16.1, safetensors, httpx, orjson,
  pyyaml, numpy, pyarrow, accelerate). `uv pip install "sglang[all]>=0.5.6"` **fails on macOS**:
  sglang / sgl-kernel / nvidia-cutlass-dsl only ship manylinux wheels. Inference therefore runs
  through plain transformers on MPS, reimplementing the ~40 lines of `nla_inference.py` that
  matter (sidecar load + asserts, embedding injection, AR critic).
- EasyNLA cloned to `~/tools/EasyNLA` (commit 4d72847, 2026-07-10) only to read the injection hook.
- Weights live in the default HF cache `~/.cache/huggingface/hub/`; nothing large is in the repo.

## Checkpoints

### kitft/nla-qwen2.5-7b-L20-{av,ar} (Qwen2.5-7B-Instruct, layer 20)
- AV 15.2 GB bf16 (full 28-layer Qwen2ForCausalLM), AR 10.9 GB (21-layer truncated backbone +
  `value_head.safetensors`, 26 MB). Both carry `nla_meta.yaml` (schema_version 2).
- Sidecar values (read, not assumed): `d_model 3584`, `injection_scale 150.0`,
  `mse_scale 59.8665 (=sqrt d)`, marker `㈎` id 149705 with neighbours (29, 522),
  `critic_suffix_ids [1318, 29, 366, 1708, 29]`, extraction layer 20; AV template and AR template
  `Summary of the following text: <text>{explanation}</text> <summary>`.
- Injection = **replace the marker token's embedding** with the vector rescaled to L2 = 150.
- Target activations: `hidden_states[21]` of Qwen2.5-7B-Instruct (output of block 20), matching
  `examples/qwen7b_layer20_step4200.txt`. That example's fve denominator is 0.7335.

### ceselder/qwen3.6-27b-nla-rl (Qwen3.6-27B, layer 42)
- Base arch: `Qwen3_5ForCausalLM`, `model_type qwen3_5_text`, 64 layers (48 gated-DeltaNet
  linear-attention + 16 full-attention, `full_attention_interval 4`), d_model 5120, vocab 248320,
  saved with transformers 5.5.4; weight keys are `model.language_model.*`.
- Repo total 402 GB. Downloaded only: `av_base/` (53.8 GB bf16), `av_rl_adapters/iter_000300`
  and `iter_000600` (1.87 GB each, r64 rsLoRA alpha 16 on 12 module types incl. the DeltaNet
  `in_proj_{qkv,z,a,b}`/`out_proj`), `nla_meta.yaml`, `run_config.yaml`, `fve_trajectory.json`,
  `data/example_activations.parquet` (64 rows: `activation_vector` list<double>[5120],
  `activation_layer 42`, `n_raw_tokens`, `doc_id`, `detokenized_text_truncated`). **Not**
  downloaded: `ar_reconstructor/` (35.4 GB), `ar_reconstructor_sft_init/`, `ar_sft_checkpoints/`,
  `av_warmstart_lora/`.
- License field: `other`; there is no LICENSE file in the repo, so the terms are unspecified.
- Sidecar (`nla_meta.yaml`, root and `av_base/`): `kind: nla_dataset` (not `nla_model`),
  `norm: none`, marker `㈜` id 158983 with neighbours (29, 510), `prompt_templates.actor` identical
  to kitft's AV template, `critic` identical to kitft's AR template. No `injection_scale`,
  no `mse_scale`, no `role`. kitft's `load_nla_config` would refuse this sidecar without an
  override. Validated live: prompt is 112 tokens with `enable_thinking=False`, marker at
  position 93, neighbours 29/510 match, template ends `<think>\n\n</think>\n\n`.
- Injection (model card + EasyNLA `karvonen_inject_in_residual`): **additive, norm-matched, on
  the output of decoder block 1**: `h'_p = h_p + ||h_p|| * v/||v||`, vector raw. Note this is
  a different mechanism from kitft's embedding replacement.
- Memory: 53.8 GB bf16 does not fit in 48 GB. PEFT cannot attach LoRA to quanto layers, so the
  plan is: merge adapter into bf16 weights on CPU (`scripts/nla27b_merge_adapter.py`,
  streaming, re-sharded ~5 GB) → load with `QuantoConfig(weights="int8")` on MPS
  (`scripts/nla27b_smoke.py`). quanto int8 on MPS verified on Qwen3-4B first (coherent
  output, 3.6 GB resident).

## Model-card issues noticed (ceselder)
1. "Repository contents" lists adapters `iter_000100..600`; the repo has `..800`, plus
   undocumented `av_warmstart_lora/`, `ar_reconstructor_sft_init/`, `ar_sft_checkpoints/`.
2. Headline "converges around 78% FVE after 800 steps", but `fve_trajectory.json` stops at
   step 590 (max 77.7% at step 540); steps 600–800 have adapters but no eval numbers.
3. Usage snippet loads `iter_000600` "latest RL step"; the prose recommends 300; 800 exists.
4. Batch size stated as 522 at the top and 504 in the pipeline section; `run_config.yaml` says
   `batch_prompts: 504`, `group_size: 8`.
5. Card says the vector is injected "in place of the marker token"; the referenced EasyNLA code
   adds to the residual, norm-matched. Followed the code.
6. The AR's scoring convention (raw MSE vs sqrt(d)-normalised, and the FVE denominator) is not
   in any shipped sidecar; `norm: none` suggests raw. FVE numbers from this repo cannot be
   recomputed exactly without that (the card itself notes the per-step AR was not saved).
7. `adapter_config.base_model_name_or_path` points at the repo root, not `av_base/` (card
   acknowledges).
8. The `av_base/nla_meta.yaml` is the AV-SFT dataset sidecar (247k rows, explanations from
   `claude-sonnet-4-6`), useful provenance but not a model sidecar.

## Results

### 7B round-trip (`scripts/nla7b_roundtrip.py`, 2026-09-06 01:39, raw: `nla7b_roundtrip_out.json`)
Whole pipeline 67 s wall, 3 models loaded sequentially; max RSS 12.6 GB, peak footprint 17.1 GB
(MPS allocations largely outside RSS). AV decode ~9-11 s per 140-token explanation on MPS.
Target reply to "What are you hiding?" is token-identical to the released example (34 prompt +
67 reply tokens). Greedy AV decodes, AR scored with mse_scale 59.87, fve denominator 0.7335:

| pos | token | ours mse_nrm / cos / fve | example transcript mse_nrm / fve |
|---|---|---|---|
| 34 | `As` | 0.190 / 0.905 / 0.740 | 0.188 / 0.744 |
| 35 | ` Q` | 0.174 / 0.913 / 0.763 | 0.172 / 0.765 |
| 38 | ` created` | 0.224 / 0.888 / 0.695 | 0.230 / 0.686 |
| 40 | ` Alibaba` | 0.258 / 0.871 / 0.649 | 0.211 / 0.713 |

Explanation text is near-verbatim the example's for pos 35/38/40 (bf16 MPS vs the SGLang run
diverges after a few dozen tokens, as expected for greedy decoding across kernels). Output is
English and specific to the position (no CJK marker-verbalization smell), so injection is
confirmed working. AR loader prints `model.norm.weight`/`lm_head.weight` MISSING: expected, the
truncated checkpoint ships without them and both are replaced by Identity.

Deviations from `docs/setup.md` / `docs/inference.md`: no SGLang (not installable on macOS), so
generation uses `model.generate(inputs_embeds=...)` in transformers; transformers 5.16's
`apply_chat_template(tokenize=True)` returns a BatchEncoding, so `["input_ids"]` is taken
explicitly; no bundled sample parquet in the kitft repo, so activations were extracted from the
target model directly instead of via `nla_inference.py --parquet`.

### 27B (ceselder) - cancelled 2026-09-06 by the human before any run
Reason: 53.8 GB bf16 base does not fit 48 GB; the int8-merge path was built but not exercised.
Download killed at ~24 GB; partial blobs deleted. Left in the HF cache (7.2 GB): both adapters,
sidecars, `fve_trajectory.json`, example parquet, and the 3.97 GB `av_base/model-00002` shard
(the 49.8 GB shard was never completed). `scripts/nla27b_merge_adapter.py` and
`scripts/nla27b_smoke.py` are untested scaffolding; delete or keep for a GPU box.

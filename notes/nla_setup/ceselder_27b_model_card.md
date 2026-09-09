# ceselder/qwen3.6-27b-nla-rl — model-card summary and verified facts

Summary of the Hugging Face model card (read 2026-09-09), cross-checked against the downloaded
files and the pod smoke test (`scripts/nla27b_smoke.py`, raw in `nla27b_smoke_out.json`, branch
`pod/mtl-setup`). Items marked **[verified]** were checked on disk or by running; items marked
**[card]** are the author's claims as written. Discrepancies are listed at the end.

## What it is
A Natural Language Autoencoder (Anthropic 2026 recipe, trained with EasyNLA) for
`Qwen/Qwen3.6-27B`, layer-42 residual-stream activations. The repo holds the base the adapters
attach to, every GRPO-RL verbalizer adapter, the final reconstructor, and the configs.

## Base model **[verified]**
- `Qwen3_5ForCausalLM`, `model_type qwen3_5`: 64-layer hybrid, 48 gated-DeltaNet linear-attention
  blocks + 16 full-attention (`full_attention_interval 4`), d_model 5120, vocab 248320,
  head_dim 256, intermediate 17408. Weight keys `model.language_model.*`, saved with
  transformers 5.5.4; loads under 5.16.1 without remote code.
- Extraction layer 42 = ⌊2·64/3⌋ **[card]**; sidecar `layer_index: 42` **[verified]**.

## Repository layout (402 GB total on the Hub)
| Path | What | Size | On pod |
|---|---|---|---|
| `av_base/` | Qwen3.6-27B with the warmstart AV LoRA (r128, all-module) **merged in**. Full bf16 causal LM + tokenizer + chat template. Usable standalone as the pre-RL verbalizer. | 53.8 GB | yes |
| `av_rl_adapters/iter_000100 … 000800` | GRPO-RL verbalizer LoRAs, one per 100 steps. r64, rsLoRA, alpha 16, 12 target module types incl. DeltaNet `in_proj_{qkv,z,a,b}` / `out_proj`. Attach on top of `av_base`. | 1.87 GB each | 300, 600 |
| `ar_reconstructor/` | Final AR: 43-block truncated `Qwen3_5ForCausalLM` backbone (`num_hidden_layers 43`, no `model.norm` / `lm_head` weights) + `value_head.safetensors` (one fp32 `weight` [5120,5120]; ‖W−I‖_F 7.29). `saved_at_step.txt` = 600. | 35.4 GB | yes |
| `ar_reconstructor_sft_init/`, `ar_sft_checkpoints/`, `av_warmstart_lora/` | Not documented on the card. | — | no |
| `nla_meta.yaml` | Extraction config, injection ids, exact AV/AR templates. `kind: nla_dataset`, `norm: none`, no `injection_scale` / `mse_scale` / `role`. | — | yes |
| `run_config.yaml` | RL hyperparameters (`batch_prompts 504`, `group_size 8`). | — | yes |
| `fve_trajectory.json` | Held-out eval FVE per step; stops at step 590 (max 77.7% at 540). | — | yes |
| `data/example_activations.parquet` | 64 layer-42 activations (float64 lists of 5120), `doc_id`, `n_raw_tokens`, `detokenized_text_truncated`. Activation norms ≈ 85–102. | — | yes |

## How to use **[verified on the pod]**
1. Load `av_base` in bf16 (`device_map="cuda"`), then `PeftModel.from_pretrained(base, av_rl_adapters/<iter>)`.
   Card snippet uses `iter_000600`; the author's prose guess for the most useful checkpoint is 300.
   Resident: 52 GB with an unmerged r64 adapter. ~42 s per 200-token greedy generation on an A100
   80GB (unmerged PEFT LoRA, no fast DeltaNet kernels).
2. Prompt: sidecar `prompt_templates.actor` with `{injection_char}` = `㈜` (id 158983), through
   `apply_chat_template(..., add_generation_prompt=True, enable_thinking=False)`; tokenise with
   `add_special_tokens=False`. Gives 112 tokens, marker at position 93, neighbours (29, 510).
   Without `enable_thinking=False` the Qwen3.6 template opens a bare `<think>` block.
3. Injection: EasyNLA `register_karvonen_hook` / `karvonen_inject_in_residual`, i.e. **additive,
   norm-matched, on the output of decoder block 1**: `h'_p = h_p + ‖h_p‖ · v/‖v‖`, raw vector
   (no scaling). The card's phrase "in place of the marker token" describes the marker's role,
   not the arithmetic; the referenced code adds to the residual.
4. AV generates `<explanation>…</explanation>`; extract with a DOTALL regex.
5. AR: load `ar_reconstructor` as a causal LM, replace the final RMSNorm with Identity, run the
   inner transformer with `use_cache=False`, take the last-token hidden state of
   `Summary of the following text: <text>{explanation}</text> <summary>` (no special tokens),
   L2-normalise to √d = 71.55 (EasyNLA's default when the sidecar has no `mse_scale`), apply the
   fp32 value head. Compare to the original by cosine (scale-free) or normalised MSE = 2(1−cos).

## Training pipeline **[card]**
1. AV warmstart SFT: LoRA r128 on all modules (attention + MLP + DeltaNet decay) on
   activation→explanation pairs, merged into `av_base`.
2. AR SFT: 43-block reconstructor + value head trained to rebuild activations from explanations.
3. GRPO RL (this run): on-policy GRPO, group-relative advantage, no importance ratio, group size 8,
   temperature 1.0, k3 KL estimator β = 0.01, hinged length penalty 0.01/token over 192 tokens.
   Actor = fresh r64 rsLoRA on `av_base`; critic (AR) co-trained with an r64 LoRA. 6× B200,
   ~440 s/step. Reward = −reconstruction MSE.
   - Starts RL at 53% FVE, "converges around 78% FVE after 800 steps".
   - Batch size larger than Anthropic's, so step counts are not comparable to the paper's.

## Provenance **[card]**
Warmstart texts and explanations reused from `ceselder/qwen3-8b-nla-L24-finefineweb-100k`
(a Qwen3-8B L24 NLA); activations regenerated at L42 of Qwen3.6-27B. Corpus: FineFineWeb 100k,
10 positions per doc, 499,846 RL rows. AV-SFT explanations were written by `claude-sonnet-4-6`
(from `av_base/nla_meta.yaml`). License field `other`, no LICENSE file.

## Caveats the card states
- FVE is normalised by each model's predict-the-mean baseline variance; compare only within this
  model and layer, never across base models.
- The AR is latest-only. Per-step eval FVE was measured against the AR as it was at that step;
  those numbers cannot be reproduced exactly. Pair any adapter with the final AR.
- `base_model_name_or_path` in the adapter configs points at the repo root; load `av_base/` explicitly.

## Discrepancies and gaps (from `README.md` in this directory, still open)
1. Card lists adapters 100–600; repo has up to 800, plus three undocumented directories.
2. "78% FVE after 800 steps" but `fve_trajectory.json` ends at step 590 (max 77.7% at 540).
3. Recommended checkpoint: snippet 600, prose 300, 800 exists.
4. Batch size 522 (card top) vs 504 (card pipeline section and `run_config.yaml`).
5. The AR's scoring scale (`mse_scale`, FVE denominator) is not in any shipped sidecar; `norm: none`
   suggests raw. FVE from this repo is not exactly recomputable; cosine is safe.
6. The 64 shipped examples are not stated to be held-out.

## Smoke result for reference (2026-09-09, A100 80GB, adapter 600, 8 examples)
cos(recon, own activation) mean 0.9661 (0.949–0.976); shuffled-pair control 0.6031; 8/8
explanations extracted. Explanations reliably get genre, discourse position and the next-token
expectation; named entities and numbers are often swapped for plausible neighbours (Maclagan →
"Captain John", enterococci 865 → "E. coli 1,000", 787 → 737). Every response ran to ~189 tokens,
close to the 192-token penalty hinge, with occasional stray `</ex>:` fragments.

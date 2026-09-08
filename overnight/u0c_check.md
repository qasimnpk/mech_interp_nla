# U0c check — artifacts, measured per-call costs, re-budget (round 3c)

git 0f7f6f48; settings in u0c_settings.json

## Artifact checks

| check | got | want | ok |
|---|---|---|---|
| stimuli rows | 200 | 200 | OK |
| t2a_scores rows | 200 | 200 | OK |
| t2a_scores errors | 0 | 0 | OK |
| t2c_pairs rows | 40 | 40 | OK |
| t2c_pairs errors | 0 | 0 | OK |
| c2_pairs rows | 40 | 40 | OK |
| c3_cells rows | 40 | 40 | OK |
| s3_scores rows with edit_ok (all edit types) | 1963 | >0 | OK |
| s3 accepted LLM-corrupt rows | 490 | 490 | OK |
| s3 corrupt_det edit_ok rows | 445 | ≈445 (402 also LLM-accepted) | OK |
| t0_topics rows | 200 | 200 | OK |
| t0_entropy rows | 200 | 200 | OK |
| s2_claims rows | 671 | 671 | OK |
| s3_edits rows | 538 | 538 | OK |
| explanations rows | 200 | 200 | OK |
| acts_L20 h20 shape | (200, 3584) | (200, 3584) | OK |
| acts_L20 h20_pos2 shape | (200, 3584) | (200, 3584) | OK |
| c2_acts H shape | (40, 2, 3584) | (40, 2, 3584) | OK |
| c2_acts rows | 80 | 80 | OK |
| c3_acts H shape | (40, 4, 3584) | (40, 4, 3584) | OK |
| c2_acts vs c2_pairs cos(h_a,h_b) max |dev| | 1.1102230246251565e-16 | <1e-4 | OK |
| t2_prefix.py import-safe (Settings inside main) | True | True | OK |
| t2a_audit.py import-safe (Settings inside main) | True | True | OK |
| t2c_entity.py import-safe (Settings inside main) | True | True | OK |
| c2_matched.py import-safe (Settings inside main) | True | True | OK |
| c3_phrasing.py import-safe (Settings inside main) | True | True | OK |
| t1_arprobe.py import-safe (Settings inside main) | True | True | OK |

## Measured costs (5 calls each; mean / min / max seconds; MPS synchronised)

| call type | mean s | min s | max s | note |
|---|---|---|---|---|
| target_short_forward | 0.422 | 0.117 | 1.584 | {"tokens": 19} |
| target_doc512_forward_all_hidden | 1.123 | 1.112 | 1.160 | {"tokens": [512, 512, 512, 512, 512], "max_1_minus_cos_vs_acts_L20": 1.1102230246251565e-16} |
| target_forward_hook_block20 | 0.099 | 0.099 | 0.100 | {"self_patch_max_abs_logit_diff": 0.0} |
| av_forward_prefill | 0.597 | 0.383 | 1.440 | {} |
| av_generation_200 | 9.789 | 9.532 | 9.977 | {"n_tokens": [145, 143, 146, 145, 140], "parse_ok": [true, true, true, true, true]} |
| ar_score | 0.480 | 0.275 | 1.295 | {} |

- model loads: TARGET 6 s, AV 5 s, AR 4 s; RSS after TARGET free 0.6 G, after AV free 0.6 G
- self-patch at block 20 (own row written back): max |Δlogit| 0.00e+00 (bf16)
- 512-token document forward: block-20 activation at pos vs acts_L20 max(1−cos) 1.11e-16

## Re-budget (call counts from the PLAN stage texts x measured means + loads)

| stage | projected min | cap min | over cap | counts |
|---|---|---|---|---|
| U1 | 36.0 | 60 | no | topic 200 docs x 2 prefixes x 2 cands x (own, swap) + no-inj cache 400; entity 40 x 2 x 2 x 2 + 160 no-inj; text-only 200 x 2 titles (prefix) + prior cached by topic ~200 (counted as doc forwards) |
| X3 | 29.1 | 60 | no | ≈330 rows x 9 AR scores (T/F/P x 3 conditions); judge ≈660 short TARGET generations (≤8 tokens) counted as short forwards x4 |
| X1 | 39.1 | 60 | no | 4 layers x (topic 160 x 4 + entity 40 x 4) + no-inj cache |
| N3 | 13.3 | 60 | no | 402 rows x 4 versions (original cached per explanation) |
| N4 | 14.6 | 60 | no | 40 cells x 4 contexts + ≈1,900 claim texts, all hidden states |
| X1b | 13.8 | 60 | no | 40 pilot x 2 layers |
| RT | 4.3 | 90 | no | 16 contexts; gates + 4 patches x 16 + text QA |
| M | 48.8 | 90 | no | 200 TARGET generations ≤200 tokens counted at the AV generation rate; 80 items AV + AR |

- total projected 199 min for U1..M (hard stop 9 h = 540 min from the first round-3c RUNLOG line)

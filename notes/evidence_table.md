# Claim-to-evidence table (agent, 2026-09-07 04:15; commit 17b1524 + this file). One row per number the write-up may use.

Columns: value · file (all under `overnight/` unless noted) · filter · columns / aggregation · n and unit · CI method ·
status (PRE = pre-registered kill statistic; REP = reported alongside, pre-registered as a report; EXP = exploratory,
introduced after seeing data; DESK = desk re-derivation from committed CSVs). Bootstraps are 1000 draws, seed 0.
"Eval" = `split == "eval"` or `stim_idx ≥ 40`; select by the field, not row order.

## Finding 1 — reconstruction and specificity (round 1)
| claim | value | file | filter | columns / aggregation | n | CI | status |
|---|---|---|---|---|---|---|---|
| own-activation cosine | 0.8820 [0.8753, 0.8886] | s1_recon.csv | eval | mean `cos_own` | 160 explanations | bootstrap by explanation | PRE K1a |
| same-document other position | 0.3664 | s1_recon.csv | eval | mean `cos_shuffled_samedoc`; paired diff 0.5156 [0.4987, 0.5331] | 160 | bootstrap by explanation | PRE K1b |
| other document | 0.3198 | s1_recon.csv | eval | mean `cos_shuffled_doc` | 160 | as above | REP |
| empty explanation (AR prior) | 0.3471 | s1_recon.csv | eval | mean `cos_empty` | 160 | — | REP (positive control) |
| adjacent layers | 0.8345 / 0.8359 | s1_recon.csv | eval | mean `cos_L19`, `cos_L21` | 160 | — | REP diagnostic |
| blind describer / left-only / raw context | 0.4286 / 0.4387 / 0.4731 | s4_recon.csv | all rows (160 blind; left-only n=100) | mean `cos_blind`, `cos_blind_left`, `cos_rawctx`; gap `cos_AV − cos_blind` 0.4534 [0.4404, 0.4673] | 160 | bootstrap by explanation | PRE K4 (gap) |

## Finding 2 — edited descriptions, activation fixed (rounds 1–2)
| claim | value | file | filter | columns / aggregation | n | CI | status |
|---|---|---|---|---|---|---|---|
| claim deletion vs random equal-length span | D = 0.00578 [0.00224, 0.00964] | s2_claims.csv | eval | mean of (|Δcos| − mean of 3 `Δcos_randspan_*`) | 538 claims / 160 expl | cluster by explanation | PRE K2 |
| one-fact corruption cost A | 0.00313 [0.00159, 0.00478] | s3_scores.csv | eval, `edit_ok`, `edit_type == corrupt` | mean (`cos_z` − `cos_z_edit`) | 490 rows / 160 expl | cluster by `stim_idx` | PRE K3 (with P) |
| paraphrase cost P | 0.00494 [0.00354, 0.00665] | s3_scores.csv | eval, `edit_ok`, `edit_type == paraphrase` | same | 490 / 160 | as above | PRE K3 |
| A − P | −0.00181 [−0.00279, −0.00080] | s3_scores.csv | paired by `row` | mean of row-wise difference | 490 / 160 | cluster by `stim_idx` | PRE K3, MET |
| deterministic swap A_det − P | −0.00137 [−0.00241, −0.00034] | s3_scores.csv | `edit_type == corrupt_det`, `edit_ok` | same | 402 / 158 | as above | REP K3-det |
| every-claim corruption vs paraphrase | 0.00754 vs 0.01407; diff −0.00653 [−0.00992, −0.00260] | r2_expl.csv | `included` | `D_corrupt`, `D_para` | 160 explanations | bootstrap by explanation | PRE R2, MET |
| off-topic swap cost / AUROC | 0.114 [0.104, 0.123] / 0.9553 | s3_scores.csv; s3_summary.md:36-40 | `edit_type == offtopic` | mean cost; AUROC of Δ vs original | 538 | cluster by explanation | REP (weak third arm) |
| one-fact corruption AUROC | 0.5257 | s3_summary.md:36-40 | | AUROC(Δ corrupt vs Δ original) | 490 | — | REP |
| edit-size confound | corruptions median 1 word changed, paraphrases median 14 | notes/diagnostics_round3b.md §S3 edit audit | 490 accepted eval triples | word-level diff after stripping punctuation/case | 490 | — | DESK, descriptive |
| punctuation-only corruptions | 6 / 490 (1 non-edit, row 465) | notes/s3_punctuation_only_corruptions.csv | | | | | DESK |
| target's own encoding of the claim text | d_corr_T 0.0395 vs d_para_T 0.1336; S_T −0.0940 [−0.1038, −0.0845] | r1_scores.csv; r1_summary.md:12-16 | 490 triples | last-token block-20 distances | 490 / 160 | cluster by explanation | PRE R1, MET; caveat: c and c* share final tokens |

## Finding 3 — local snippet (rounds 2–3)
| claim | value | file | filter | columns / aggregation | n | CI | status |
|---|---|---|---|---|---|---|---|
| last claim alone recovers 88% of the lift | mean lift 0.8837 [0.8574, 0.9044]; median 0.9253; mean cos 0.8217 | r3_curve.csv; r3_summary.md:12 | `direction == last`, `k == 1` | `lift` = (`cos_k` − `cos_empty`) / (`cos_z` − `cos_empty`) per explanation, then mean | 160 | cluster by explanation | REP (descriptive stage) |
| first claim alone | mean lift 0.2270; cos 0.4673 | r3_curve.csv; r3_summary.md:12 | `direction == first`, `k == 1` | as above | 160 | as above | REP |
| first three claims | mean lift 0.9427 | r3_summary.md:14 | `k == 3` | | 160 | | REP |
| deletion cost: last 0.125, first 0.010, middle 0.017 | | s2_claims.csv (desk one-liner, findings_so_far.md §4) | eval | −Δcos by claim position | 538 claims | — | DESK |
| snippet moved to front keeps 79% of its cost | 0.0989 vs 0.1253; diff −0.0264 [−0.0322, −0.0213] | c1_expl.csv; c1_summary.md | eval, ≥3 claims | `cost_snippet_in_z_s2` vs cost in `z_rot` | 160 | cluster by explanation | PRE C1, NOT MET (threshold ≤ −0.05) |
| reversed order | 0.1320 | c1_summary.md | | | 160 | | REP |
| corrupting the last claim | 0.0048 vs paraphrase 0.0055 | s3_scores.csv joined to s2_claims.csv (desk) | last claims only | | | — | DESK |

## Finding 4 — prompting and steering (rounds 1, 3)
| claim | value | file | filter | columns / aggregation | n | CI | status |
|---|---|---|---|---|---|---|---|
| instruction following, mechanical | 0/80 (V3 one-word, V4 French) | s5_outputs.jsonl; s5_summary.md | pilot 0–39 | follow_rate | 80 | CI [0, 0] | PRE K5, MET |
| instruction following, judged | 0/120 (V1, V2, V5) | s5_judge.csv | pilot | agent rubric, not human | 120 | — | REP, agent-judged |
| outputs not identical to default | word-sequence similarity to V0 0.55–0.59 vs 0.17 across stimuli; 0/40 exact matches per variant | findings_so_far.md §5 (desk over s5_outputs.jsonl) | pilot | | 40 per variant | — | DESK; no resampled-V0 noise floor was run |
| AV residual steering (French) | eligible cell L8 α=1: 0.057 [0.000, 0.143], parse_ok 1.0; all α ≥ 2: parse_ok 0 | t3_outputs.jsonl; t3_summary.md | pilot, 35/40 completed at cap | French stoplist rule ≥ 0.15 | 35 | bootstrap by stimulus | PRE T3, MET |
| injected concept direction | sports mention 1.000 at β = 0.25 (18.4°) and 0.5; baseline 0.125; random 0.175 | t4_outputs.jsonl; t4_summary.md | pilot 0–39 | keyword-list mention rate | 40 per cell | bootstrap by stimulus | PRE T4, NOT MET |

## Finding 5 — targeted readout (rounds 3, 3b)
| claim | value | file | filter | columns / aggregation | n | CI | status |
|---|---|---|---|---|---|---|---|
| topic, round-3 prefix, raw AUROC | 0.7516 [0.7017, 0.7983] | t2_scores.csv | eval | AUROC(`cc_true` vs `cc_foreign`), paired | 160 documents | bootstrap by document | PRE T2, NOT MET |
| topic, prior-corrected AUROC (round 3) | 0.9347 [0.9111, 0.9580] | t2_scores.csv; t2a_summary.md | eval | AUROC(`cc_true − cc_true_noinj` vs same for foreign) | 160 | bootstrap by document (CI added in T2a) | **EXP** (not in round-3 PLAN) |
| topic, held-out prefix p3, raw AUROC | 0.7605 [0.7126, 0.8059] | t2a_scores.csv | eval | AUROC(`p3_true` vs `p3_foreign`) | 160 | bootstrap by document | PRE T2a, NOT MET |
| p3 prior-corrected AUROC | 0.9431 [0.9214, 0.9643] | t2a_scores.csv | eval | `p3_true_corr` vs `p3_foreign_corr` | 160 | as above | REP; correction rule EXP, same 160 documents |
| p3 paired choice accuracy raw / corrected | 0.781 [0.719, 0.844] / 0.944 [0.906, 0.975] | t2a_scores.csv | eval | fraction true > foreign | 160 | bootstrap by document | REP |
| p3 no injection / swap | AUROC 0.486; swap follows the donor 0.786 (accuracy of still choosing true 0.200) | t2a_scores.csv | eval | `p3_*_noinj`, `p3_*_swap` | 160 | | REP controls |
| yes/no format | AUROC 0.5502 [0.5227, 0.5777] | t2_scores.csv | eval | `yn_true` vs `yn_foreign` | 160 | | REP (threshold-table wording), MET |
| same-items comparison: AR probe / RepE centred / RepE direction | 0.6125 / 0.7405 / 0.8128 | t1_scores.csv; t2a_summary.md same-items table | eval, identical labels | AUROC | 160 | bootstrap by document | T1 PRE (INCONCLUSIVE); RepE REP. Different tasks/supervision: report side by side, do not rank |
| entity readout, donor sensitivity | 1.738 [0.627, 3.276]; 31/40 > 0; median 0.695 | t2c_pairs.csv | all 40 pairs | mean (`p1_D_a` − `p1_D_b`) | 40 pairs / 10 templates | cluster by `template_id` | PRE T2c, NOT MET |
| entity both-correct / choice accuracy | 0.225 (9/40) / 0.600 [0.525, 0.688] | t2c_pairs.csv | | `p1_D_a > 0 & p1_D_b < 0`; argmax over 80 activations | 40 / 80 | cluster by template | REP |
| entity, held-out prefix p2 | 1.834 [0.756, 3.004] | t2c_pairs.csv | | `p2_D_a` − `p2_D_b` | 40 | | REP |
| entity effect survives phrasing | 1.772 [0.718, 3.219] at w2; entity main effect 1.755, wording −0.016, interaction −0.017 | c3_cells.csv | | `D_hC` − `D_hD`; 2×2 means | 40 cells | cluster by template | PRE C3-readout, NOT MET |
| source-edit matching margins | M_fact 0.0175 vs M_wording 0.0097; diff 0.0078 [−0.0035, 0.0241] | c3_cells.csv | | `M_fact_mean`, `M_wording_mean` | 40 cells | cluster by template | PRE C3-score, INCONCLUSIVE |
| margin tracks activation distance | Spearman 0.77 over 160 margins (4 per cell, not independent) | notes/diagnostics_round3b.md | | | 40 cells | — | DESK, descriptive, shares geometry with the margin |
| claim-word readout, own activation | lp_orig − lp_corrupt 9.78 [8.97, 10.52]; frac 0.973; no-injection 1.39 | t2_claims.csv | `single_word`, `edit_type == corrupt` | mean `d_inj` | 298 rows / 147 expl | cluster by explanation | REP (not a kill); self-consistency by construction |
| claim-word donors (all 691 rows) | own 12.99 / same-doc 5.64 / foreign 2.88 / none 2.73; own − same-doc 7.35 [6.56, 8.14] | t2b_claims.csv | all single-word rows (298 LLM + 393 det) | means of `d_own`, `d_pos2`, `d_foreign`, `d_noinj` | 691 / 159 | cluster by explanation | PRE T2b, NOT MET (activation dependence only) |
| original word absent from the full prefix | 434 / 691; d_own 10.80 (absent) vs 16.69 (present) | notes/t2b_in_full_prefix.csv | bench `in_ctx` rule over tokens 0..pos | | 691 | — | DESK; lexical, not support |
| 30-row support audit | unlabelled | notes/t2b_support_sheet_BLIND.csv | seed-0 sample of eval LLM-corrupt rows | | 30 | — | pending [YOU] |

## Provenance inventory
- Scripts: every `overnight/*.py` was agent-written from `overnight/PLAN.md`; PLAN stages, kill tests and thresholds
  were drafted by the desk agent and edited/approved by the human with three outside reviewers
  (`notes/round1_decisions.md`; review blocks at the top of `overnight/PLAN.md`; `notes/advisor_*.md`).
- Crash fixes, all before any model output, no statistic changed: `RUNLOG.md` lines 12 (S3, AR phase after editor
  outputs were saved; the editor outputs were preserved and the AR scoring rerun), 24 (R1, before model load),
  58 (C3, before model load; `out/c3_iter1_crash.log`). Note: the S3 fix occurred after editor generation but
  before any AR score existed; say "before any scored output", not "before any output".
- Human re-derivations logged: `notes/human_log.md` (agent-side entries so far; human entries owed).
- Settings files: `overnight/<stage>_settings.json` (commit hash, model snapshots, prompts, seeds); round-1 S2/S5
  settings were restored from commits after being clobbered (RUNLOG line 20 area).

# 27B analysis scripts — session of 2026-09-10

Every number reported in the 27B analysis discussion traces to one of these scripts. They read only
committed artifacts (`04_06_scores_27b_full.csv`, `tasks/02_atoms_27b_doc*.jsonl`, `out/acts_27b_*.pt`)
and take no arguments: `uv run python fve_claims/analysis_27b/<script>.py`.

Numbers only — no verdicts recorded here. Labels are agent-produced (see `ANNOTATION_GUIDE.md`);
the `av_base`-as-TARGET deviation applies to all 27B numbers.

| script | produces |
|---|---|
| `10_fve_from_cosine.py` | walks raw activation → FVE. Confirms `D_local = 0.3709`, that FVE is affine in cosine, and that `fve_z` reproduces to 0.0e+00 on doc 0. Break-even cosine (FVE=0) is 0.8146. |
| `11_fve_document_structure.py` | `D` is one global scalar (`max\|fve_z − 1−2(1−cos)/D\| = 6.7e−16`); `P_orig = 5.392 × cosine drop`. Between-document share of variance in `P_orig`: all 4.4%, detail 8.8%, theme 37.5%. |
| `12_type_truth_tables.py` | type × truth mean FVE drop + AUROC, for `P_orig` and `P_heavy`, with a second grouping folding entity into detail. |
| `13_within_document_paired.py` | within-document paired true−false gap (per doc, then averaged), bootstrap CI over documents, plus coverage of the pairing requirement. |
| `14_document_sign_test.py` | document-level sign test and Wilcoxon on those paired differences. detail: 57/91 docs positive, sign p=0.021, Wilcoxon p=0.0003. |
| `15_heavy_vs_orig_paired.py` | paired `P_heavy` vs `P_orig` on the same documents. detail delta −0.38 pp [−0.73,−0.12], p=0.0029. Identifies doc 75 as the outlier driving the merged/all rows. |
| `16_doc075_outlier.py` | doc 75 claim-by-claim; its claim 6 (false entity) has `fve_del = −51.04`, `P_orig = 117.08`. Merged/all gaps recomputed with and without that document. |
| `17_average_cosine_variants.py` | averaging the two cosine drops then converting == averaging the FVE-based scores (`1.3e−15`). Also the distinct `P_twobase` variant using heavy paraphrase as a second baseline. |

## Verification trail on the logistic test

Kept as three files deliberately, because the first version was wrong and the error was caught in-session:

- `18a_logistic_FLAWED.py` — **do not reuse.** Pools predicted probabilities across CV folds. Each fold
  fits its own intercept and slope, so probabilities are not rank-comparable between folds; this
  scrambles the global ranking and produced plausible-looking sub-chance AUROCs (0.41–0.47).
- `18b_logistic_diagnostic.py` — the check that caught it: the single-feature `P_orig` coefficient is
  positive in 100/100 folds, yet the pooled OOF AUROC (0.4668 on detail) fell below the raw-feature
  AUROC (0.5426). A single feature through a fitted model must reproduce its own raw AUROC.
- `18c_logistic_corrected.py` — AUROC computed *within* each held-out fold, then averaged. Single-feature
  held-out AUROC now matches raw (0.5414 vs 0.5426). Held-out AUROC: `P_orig` 0.5414, `P_heavy` 0.5192,
  both 0.5346 on detail; `corr(P_orig, P_heavy) = 0.989` overall, 0.997 within detail.

Standing check for anything CV-based in this project: a single monotone feature passed through a fitted
model must reproduce its own raw AUROC. If it does not, the fold handling is wrong.

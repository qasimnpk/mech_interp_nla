# fve_claims baseline — FVE drop when one atomic claim is removed (7B, DocRED pilot, all, D_local = 0.6208)

Claims scored 1313; atoms labelled 1600 (100 docs); joined 1313 over 100 docs (0 dropped: not yet relabelled to v2). FVE drop in percentage points; error = cluster bootstrap 95% CI by document (1000 draws, seed 0). Labels provisional (agents).

Counts by type × class: {"theme": {"true": 266, "false_related": 117, "false_unrelated": 24}, "entity": {"false_related": 108, "true": 21, "false_unrelated": 17}, "detail": {"false_related": 366, "true": 232, "false_unrelated": 17}, "forecast": {"irrelevant": 145}}

## Type × truth (irrelevant excluded)

| type | true | false | true − false |
|---|---|---|---|
| theme | 0.774 +/- 0.494 (n=266, docs=100) | 0.756 +/- 0.831 (n=141, docs=77) | 0.018 |
| entity | 0.488 +/- 0.321 (n=21, docs=20) | 1.139 +/- 0.488 (n=125, docs=67) | -0.650 |
| detail | 2.610 +/- 0.765 (n=232, docs=99) | 0.949 +/- 0.353 (n=383, docs=99) | 1.661 |
| **all** | 1.583 +/- 0.567 (n=519, docs=100) | 0.943 +/- 0.371 (n=649, docs=100) | 0.640 |

## Mean raw FVE per class (not the drop): fve_z = FVE of the full explanation containing the claim; fve_del = FVE with that claim removed

| type | truth | mean fve_z | mean fve_del | n |
|---|---|---|---|---|
| theme | true | 64.500 | 63.726 | 266 |
| theme | false | 63.319 | 62.564 | 141 |
| entity | true | 63.037 | 62.548 | 21 |
| entity | false | 63.512 | 62.374 | 125 |
| detail | true | 65.007 | 62.397 | 232 |
| detail | false | 63.720 | 62.771 | 383 |
| **all** | true | 64.667 | 63.084 | 519 |
| **all** | false | 63.593 | 62.650 | 649 |

## False claims by relatedness (all types)

| related | unrelated |
|---|---|
| 0.957 +/- 0.389 (n=591, docs=100) | 0.803 +/- 0.551 (n=58, docs=33) |

Irrelevant (forecast / model_output) claims, reported separately: 2.361 +/- 0.865 (n=145, docs=98)

Paper (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06 (percent FVE, true / false).

## Percentiles of the drop (pp) by class: 10 / 25 / 50 / 75 / 90

- true: -0.343 / 0.048 / 0.609 / 1.703 / 4.204  (n=519, negative 117)
- false_related: -0.428 / -0.072 / 0.323 / 1.001 / 2.666  (n=591, negative 179)
- false_unrelated: -0.310 / -0.055 / 0.278 / 0.992 / 2.550  (n=58, negative 17)
- irrelevant: -0.289 / 0.258 / 1.349 / 2.861 / 5.730  (n=145, negative 24)

Deletions with preserves_other_propositions=false: 0 (kept in the tables; listed in 04_scores_7b.csv).
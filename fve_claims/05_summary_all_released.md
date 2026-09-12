# fve_claims baseline — FVE drop when one atomic claim is removed (7B, DocRED pilot, all, D_released = 0.7335)

Claims scored 1313; atoms labelled 1600 (100 docs); joined 1313 over 100 docs (0 dropped: not yet relabelled to v2). FVE drop in percentage points; error = cluster bootstrap 95% CI by document (1000 draws, seed 0). Labels provisional (agents).

Counts by type × class: {"theme": {"true": 266, "false_related": 117, "false_unrelated": 24}, "entity": {"false_related": 108, "true": 21, "false_unrelated": 17}, "detail": {"false_related": 366, "true": 232, "false_unrelated": 17}, "forecast": {"irrelevant": 145}}

## Type × truth (irrelevant excluded)

| type | true | false | true − false |
|---|---|---|---|
| theme | 0.655 +/- 0.418 (n=266, docs=100) | 0.640 +/- 0.703 (n=141, docs=77) | 0.016 |
| entity | 0.413 +/- 0.272 (n=21, docs=20) | 0.964 +/- 0.413 (n=125, docs=67) | -0.550 |
| detail | 2.209 +/- 0.648 (n=232, docs=99) | 0.803 +/- 0.299 (n=383, docs=99) | 1.406 |
| **all** | 1.340 +/- 0.480 (n=519, docs=100) | 0.798 +/- 0.314 (n=649, docs=100) | 0.541 |

## Mean raw FVE per class (not the drop): fve_z = FVE of the full explanation containing the claim; fve_del = FVE with that claim removed

| type | truth | mean fve_z | mean fve_del | n |
|---|---|---|---|---|
| theme | true | 69.955 | 69.300 | 266 |
| theme | false | 68.956 | 68.317 | 141 |
| entity | true | 68.717 | 68.304 | 21 |
| entity | false | 69.120 | 68.156 | 125 |
| detail | true | 70.385 | 68.176 | 232 |
| detail | false | 69.296 | 68.493 | 383 |
| **all** | true | 70.097 | 68.757 | 519 |
| **all** | false | 69.188 | 68.390 | 649 |

## False claims by relatedness (all types)

| related | unrelated |
|---|---|
| 0.810 +/- 0.330 (n=591, docs=100) | 0.679 +/- 0.467 (n=58, docs=33) |

Irrelevant (forecast / model_output) claims, reported separately: 1.999 +/- 0.732 (n=145, docs=98)

Paper (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06 (percent FVE, true / false).

## Percentiles of the drop (pp) by class: 10 / 25 / 50 / 75 / 90

- true: -0.291 / 0.041 / 0.516 / 1.442 / 3.558  (n=519, negative 117)
- false_related: -0.363 / -0.061 / 0.274 / 0.847 / 2.256  (n=591, negative 179)
- false_unrelated: -0.263 / -0.047 / 0.235 / 0.840 / 2.158  (n=58, negative 17)
- irrelevant: -0.244 / 0.219 / 1.141 / 2.421 / 4.849  (n=145, negative 24)

Deletions with preserves_other_propositions=false: 0 (kept in the tables; listed in 04_scores_7b.csv).
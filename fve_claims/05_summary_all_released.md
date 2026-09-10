# fve_claims baseline — FVE drop when one atomic claim is removed (7B, DocRED pilot, all, D_released = 0.7335)

Claims scored 1313; atoms labelled 1600 (100 docs); joined 1313 over 100 docs (0 dropped: not yet relabelled to v2). FVE drop in percentage points; error = cluster bootstrap 95% CI by document (1000 draws, seed 0). Labels provisional (agents).

Counts by type × class: {"theme": {"true": 266, "false_related": 117, "false_unrelated": 24}, "entity": {"false_related": 107, "true": 22, "false_unrelated": 17}, "detail": {"false_related": 362, "true": 236, "false_unrelated": 17}, "forecast": {"irrelevant": 145}}

## Type × truth (irrelevant excluded)

| type | true | false | true − false |
|---|---|---|---|
| theme | 0.655 +/- 0.418 (n=266, docs=100) | 0.640 +/- 0.703 (n=141, docs=77) | 0.016 |
| entity | 0.446 +/- 0.250 (n=22, docs=21) | 0.962 +/- 0.419 (n=124, docs=67) | -0.516 |
| detail | 2.242 +/- 0.831 (n=236, docs=99) | 0.767 +/- 0.195 (n=379, docs=99) | 1.475 |
| **all** | 1.361 +/- 0.560 (n=524, docs=100) | 0.777 +/- 0.219 (n=644, docs=100) | 0.584 |

## Mean raw FVE per class (not the drop): fve_z = FVE of the full explanation containing the claim; fve_del = FVE with that claim removed

| type | truth | mean fve_z | mean fve_del | n |
|---|---|---|---|---|
| theme | true | 69.955 | 69.300 | 266 |
| theme | false | 68.956 | 68.317 | 141 |
| entity | true | 68.608 | 68.162 | 22 |
| entity | false | 69.142 | 68.180 | 124 |
| detail | true | 70.304 | 68.061 | 236 |
| detail | false | 69.335 | 68.567 | 379 |
| **all** | true | 70.055 | 68.694 | 524 |
| **all** | false | 69.215 | 68.438 | 644 |

## False claims by relatedness (all types)

| related | unrelated |
|---|---|
| 0.787 +/- 0.250 (n=586, docs=100) | 0.679 +/- 0.467 (n=58, docs=33) |

Irrelevant (forecast / model_output) claims, reported separately: 1.999 +/- 0.732 (n=145, docs=98)

Paper (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06 (percent FVE, true / false).

## Percentiles of the drop (pp) by class: 10 / 25 / 50 / 75 / 90

- true: -0.291 / 0.041 / 0.518 / 1.439 / 3.574  (n=524, negative 118)
- false_related: -0.362 / -0.061 / 0.271 / 0.845 / 2.208  (n=586, negative 178)
- false_unrelated: -0.263 / -0.047 / 0.235 / 0.840 / 2.158  (n=58, negative 17)
- irrelevant: -0.244 / 0.219 / 1.141 / 2.421 / 4.849  (n=145, negative 24)

Deletions with preserves_other_propositions=false: 0 (kept in the tables; listed in 04_scores_7b.csv).
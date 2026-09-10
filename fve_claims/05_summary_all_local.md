# fve_claims baseline — FVE drop when one atomic claim is removed (7B, DocRED pilot, all, D_local = 0.6208)

Claims scored 1313; atoms labelled 1600 (100 docs); joined 1313 over 100 docs (0 dropped: not yet relabelled to v2). FVE drop in percentage points; error = cluster bootstrap 95% CI by document (1000 draws, seed 0). Labels provisional (agents).

Counts by type × class: {"theme": {"true": 266, "false_related": 117, "false_unrelated": 24}, "entity": {"false_related": 107, "true": 22, "false_unrelated": 17}, "detail": {"false_related": 362, "true": 236, "false_unrelated": 17}, "forecast": {"irrelevant": 145}}

## Type × truth (irrelevant excluded)

| type | true | false | true − false |
|---|---|---|---|
| theme | 0.774 +/- 0.494 (n=266, docs=100) | 0.756 +/- 0.831 (n=141, docs=77) | 0.018 |
| entity | 0.527 +/- 0.295 (n=22, docs=21) | 1.137 +/- 0.495 (n=124, docs=67) | -0.610 |
| detail | 2.649 +/- 0.982 (n=236, docs=99) | 0.907 +/- 0.231 (n=379, docs=99) | 1.743 |
| **all** | 1.608 +/- 0.662 (n=524, docs=100) | 0.918 +/- 0.259 (n=644, docs=100) | 0.690 |

## Mean raw FVE per class (not the drop): fve_z = FVE of the full explanation containing the claim; fve_del = FVE with that claim removed

| type | truth | mean fve_z | mean fve_del | n |
|---|---|---|---|---|
| theme | true | 64.500 | 63.726 | 266 |
| theme | false | 63.319 | 62.564 | 141 |
| entity | true | 62.908 | 62.381 | 22 |
| entity | false | 63.539 | 62.402 | 124 |
| detail | true | 64.911 | 62.262 | 236 |
| detail | false | 63.767 | 62.860 | 379 |
| **all** | true | 64.618 | 63.010 | 524 |
| **all** | false | 63.625 | 62.707 | 644 |

## False claims by relatedness (all types)

| related | unrelated |
|---|---|
| 0.929 +/- 0.295 (n=586, docs=100) | 0.803 +/- 0.551 (n=58, docs=33) |

Irrelevant (forecast / model_output) claims, reported separately: 2.361 +/- 0.865 (n=145, docs=98)

Paper (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06 (percent FVE, true / false).

## Percentiles of the drop (pp) by class: 10 / 25 / 50 / 75 / 90

- true: -0.344 / 0.048 / 0.613 / 1.700 / 4.223  (n=524, negative 118)
- false_related: -0.428 / -0.072 / 0.320 / 0.999 / 2.609  (n=586, negative 178)
- false_unrelated: -0.310 / -0.055 / 0.278 / 0.992 / 2.550  (n=58, negative 17)
- irrelevant: -0.289 / 0.258 / 1.349 / 2.861 / 5.730  (n=145, negative 24)

Deletions with preserves_other_propositions=false: 0 (kept in the tables; listed in 04_scores_7b.csv).
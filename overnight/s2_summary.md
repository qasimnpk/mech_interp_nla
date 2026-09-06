# S2 summary — claim deletion (evaluation claims unless stated)

git 921c1c3f; settings in s2_settings.json; AR forwards 4356, wall 887s

- explanations: 200 total; kept (>=2 claims) 200; excluded 0; eval kept 160; errors 0
- claims: total 671; eval 538; pilot 133

n_claims histogram (all 200 explanations): 3:152, 4:32, 5:11, 6:3, 7:2

## Δcos (deleting claim i from z) and controls — evaluation claims

| quantity | distribution |
|---|---|
| Δcos (claim deletion) | mean -0.04710 | median -0.01599 | p10 -0.15177 | p90 -0.00160 | n 538 | CI95 [-0.05272, -0.04145] |
| \|Δcos\| | mean 0.04796 | median 0.01642 | p10 0.00291 | p90 0.15177 | n 538 | CI95 [0.04249, 0.05361] |
| Δcos_randspan_1 | mean -0.04185 | median -0.02049 | p10 -0.10876 | p90 -0.00339 | n 538 | CI95 [-0.04836, -0.03637] |
| Δcos_randspan_2 | mean -0.04299 | median -0.02116 | p10 -0.11781 | p90 -0.00203 | n 538 | CI95 [-0.04897, -0.03737] |
| Δcos_randspan_3 | mean -0.04060 | median -0.01832 | p10 -0.10214 | p90 -0.00287 | n 538 | CI95 [-0.04656, -0.03513] |
| mean\|Δcos_randspan\| (3 draws) | mean 0.04218 | median 0.02429 | p10 0.00702 | p90 0.09952 | n 538 | CI95 [0.03762, 0.04665] |
| Δcos_shuffle_words | mean -0.04794 | median -0.01417 | p10 -0.17688 | p90 0.00181 | n 538 | CI95 [-0.05307, -0.04262] |
| cos_alone | mean 0.66030 | median 0.69243 | p10 0.41705 | p90 0.87054 | n 538 | CI95 [0.65030, 0.67056] |
| D = \|Δcos\| − mean\|Δcos_randspan\| | mean 0.00578 | median -0.00344 | p10 -0.04965 | p90 0.06613 | n 538 | CI95 [0.00224, 0.00964] |

### per explanation (evaluation, kept)

| quantity | distribution |
|---|---|
| cos_z | mean 0.88203 | median 0.89176 | p10 0.81632 | p90 0.92884 | n 160 |
| cos_z_joined (claims re-joined, nothing deleted) | mean 0.88114 | median 0.89249 | p10 0.81607 | p90 0.92919 | n 160 |
| cos_empty | mean 0.34713 | median 0.34829 | p10 0.24351 | p90 0.44351 | n 160 |
| Δcos_all = cos_empty − cos_z | mean -0.53490 | median -0.54574 | p10 -0.63578 | p90 -0.42977 | n 160 |
| cos_shuffle_order − cos_z | mean -0.01471 | median -0.00896 | p10 -0.03730 | p90 0.00068 | n 160 |
| cos_best_single_deletion − cos_z | mean -0.00489 | median -0.00456 | p10 -0.01390 | p90 0.00368 | n 160 |

- \|Δcos_all\| mean = 0.53490; 5 × median \|Δcos_i\| = 0.08210; mean\|Δcos_all\| ≥ 5×median\|Δcos_i\|: True

## Fraction of claims with Δcos > 0 (deletion improves reconstruction)

- overall: 0.0762 CI95 [0.0550, 0.0970] n=538
- first claim: 0.1500 CI95 [0.0938, 0.2064] n=160
- middle claims: 0.0688 CI95 [0.0374, 0.1040] n=218
- last claim: 0.0125 CI95 [0.0000, 0.0312] n=160
- fraction Δcos_randspan_1 > 0: 0.0428 CI95 [0.0262, 0.0613]
- fraction Δcos_randspan_2 > 0: 0.0706 CI95 [0.0474, 0.0964]
- fraction Δcos_randspan_3 > 0: 0.0390 CI95 [0.0237, 0.0563]
- fraction Δcos_shuffle_words > 0: 0.1561 CI95 [0.1255, 0.1891]

- Spearman(n_words, Δcos): rho=-0.5585 p=1.88e-45
- Spearman(n_words, |Δcos|): rho=0.5561

## Kill test

- 2026-09-06T03:14:37  S2  K2  threshold=CI95 of mean(|Δcos_claim| − mean|Δcos_randspan|) ≤ 0  observed=mean D=0.00578 CI95=[0.00224,0.00964] n_claims=538 n_expl=160; mean|Δcos_all|=0.5349 vs 5×median|Δcos_i|=0.0821 (>=: True)  NOT MET  MET would mean deleting a whole claim is indistinguishable from deleting a random equal-length span


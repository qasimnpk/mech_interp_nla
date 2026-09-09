# B1 summary — controlled paired contexts, meanings A/B (claude labels)

git 07fcc860; settings in b1_settings.json; progress in b1_progress.json

## Kill test

- 2026-09-09T02:25:05  B1  B1  threshold=CI95 (cluster by pair, eval) of mean D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)] over valid English paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval carriers < 32 → INCONCLUSIVE  observed=mean D=nan [nan,nan] n=0 k=0 (eligible eval carriers in primary 0, of 48 eval contexts); both-sides-correct nan [nan,nan] n=0 k=0; D orig-only nan [nan,nan] n=0 k=0; by family: n/a; mean cos(h_A,h_B) 0.9927; omission 64 redundant 0 dup_sentence 0 swap_invalid 0 no_valid_paraphrase 0; av_asserts mismatch 0; invalid realizations by transform {"light1": 0, "light2": 0, "aggr1": 0, "aggr2": 0}  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference reversal under this scorer at this position with this n (never 'the fact is absent from the activation')  (already appended by the first analysis run; not duplicated)

## Counts

- contexts 64 (dev 16, eval 48); pairs 32; generations 64 (parse_ok 64, cjk 0, errors 0)
- candidate slots 8 of 192 sentences; asserting sentences 0
- carriers: eligible 0; omission 64; redundant 0; dup_sentence 0; av_asserts mismatch (AV asserted the other meaning) 0; swap invalid 0; in primary 0 (eval 0, dev 0)
- realizations 0; paraphrases 0; invalid (equiv No) by transform {"light1": 0, "light2": 0, "aggr1": 0, "aggr2": 0}; detected duplicates 0; dup_realization flagged by the editor 0
- eligibility by pair table: eval pairs with both contexts in primary 0

## Primary statistics (eval, in-primary carriers; cluster bootstrap by pair)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| D (paraphrase-averaged μ, orig excluded) | nan | nan | nan | 0 | 0 |
| D (orig only) | nan | nan | nan | 0 | 0 |
| both-sides-correct rate | nan | nan | nan | 0 | 0 |
| both-sides-correct rate (orig only) | nan | nan | nan | 0 | 0 |
| μ_A(h_A) − μ_B(h_A) | nan | nan | nan | 0 | 0 |
| μ_B(h_B) − μ_A(h_B) | nan | nan | nan | 0 | 0 |
| deletion Δ (cos(deletion) − cos(carrier), own activation) | nan | nan | nan | 0 | 0 |

## By family (eval, in-primary)

| family | n | D mean | CI lo | CI hi | both-sides-correct | D orig-only | n pairs |
|---|---|---|---|---|---|---|---|
| F1 entity/recipient | 0 | | | | | | 0 |
| F2 relation/order | 0 | | | | | | 0 |
| F3 numerical detail | 0 | | | | | | 0 |
| F4 outcome/polarity | 0 | | | | | | 0 |

## 2×2 blocks (eval, in-primary; truth = meaning entailed / contradicted by the activation's context; slot type entity = F1, detail = F2–F4)


## Per-context absolute scores

| quantity | n | mean | min | max |
|---|---|---|---|---|
| s(h_own, carrier) = cos(h, AR(own explanation)) | 64 | 0.83905 | 0.80165 | 0.87546 |
| s(h_other, carrier) | 64 | 0.83723 | 0.79312 | 0.87682 |
| cos(h_A, h_B) per pair | 32 | 0.99268 | 0.96760 | 0.99920 |

- t (extraction position) per context: min 55 max 67; len_mismatch pairs 0

## Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## 5 fixed verbatim examples (seed 0; eval in-primary carriers)


- review sheets: b1_review_blind.csv (8 rows: every eligible fact slot first, then realizations, seed 0) — open first; b1_review_key.csv after

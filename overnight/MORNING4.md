# MORNING4 — round 4 (2026-09-09): controlled pairs (B1), natural claims (A1), K-way ranking (K1), claim-direction ablation (D1)

Written 2026-09-09T10:33:16 by T9. Round-4 first RUNLOG line 2026-09-09T01:57:48; hard stop 10 h later. Numbers only; every label below is PROVISIONAL (agent-judged) until the human has reviewed the `_review_blind.csv` sheets and re-run `b1_analyze.py` / `a1_analyze.py --labels`.

## Kill lines (pre-registered three-way rule: CI entirely ≤ 0 → MET; entirely > 0 → NOT MET; straddles 0 or n below the stage minimum → INCONCLUSIVE)

An INCONCLUSIVE or MET line means no detectable preference under this scorer at this position with this n; it is never a statement that the information is absent from the activation.

- 2026-09-09T02:25:05  B1  B1  threshold=CI95 (cluster by pair, eval) of mean D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)] over valid English paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval carriers < 32 → INCONCLUSIVE  observed=mean D=nan [nan,nan] n=0 k=0 (eligible eval carriers in primary 0, of 48 eval contexts); both-sides-correct nan [nan,nan] n=0 k=0; D orig-only nan [nan,nan] n=0 k=0; by family: n/a; mean cos(h_A,h_B) 0.9927; omission 64 redundant 0 dup_sentence 0 swap_invalid 0 no_valid_paraphrase 0; av_asserts mismatch 0; invalid realizations by transform {"light1": 0, "light2": 0, "aggr1": 0, "aggr2": 0}  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference reversal under this scorer at this position with this n (never 'the fact is absent from the activation')
- 2026-09-09T02:53:44  A1  A1  threshold=CI95 (cluster by context, eval) of mean G = μ_correct − mean_false μ_m over valid paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval slots < 30 → INCONCLUSIVE  observed=mean G=0.00319 [-0.00035,0.00674] n=4 k=4 (eligible eval slots in primary 4 of 39 eval slots; 33 eligible); correct-ranks-first 0.500 [0.000,1.000] n=4 k=4; frac comparisons won 0.625 [0.250,1.000] n=4 k=4; G orig-only 0.00300 [-0.00025,0.00626] n=4 k=4; by category (μ_correct − μ_false): detail_sub 0.00298 [-0.00115,0.00710] n=4 k=4; entity_sub 0.00196 [-0.00014,0.00499] n=3 k=3  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference for the correct meaning under this scorer with this n (never 'the information is absent')
- 2026-09-09T02:53:44  A1  A1-nat  threshold=CI95 (by context, eval) of mean [μ_correction − μ_original] on natural-error slots ≤ 0 → MET; > 0 → NOT MET; straddles or natural-error eval slots < 15 → INCONCLUSIVE (count reported; injected errors never substituted)  observed=mean [μ_correction − μ_original]=0.00113 [-0.00176,0.00465] n=4 k=4 (natural-error eval slots 4; contradicted eval originals 37; valid corrections 7 of 46); orig-only 0.00102 [-0.00145,0.00369] n=4 k=4  INCONCLUSIVE  MET/INCONCLUSIVE = the scorer does not detectably prefer the corrected version of the AV's own errors at this n
- 2026-09-09T03:08:52  K1  K1  threshold=CI95 (cluster by explanation) of (top-1 rate − 0.125) on non-last in_full_prefix rows (n=107) ≤ 0 → MET; > 0 → NOT MET; straddles or < 80 rows completed → INCONCLUSIVE  observed=nonlast_in_prefix: n=107 top1−0.125 0.1834 [0.0962,0.2650] n=107 k=89 (top1 0.308) MRR 0.487 gap 0.00125 [0.00058,0.00202] n=107 k=89 frac gap>0 0.654; nonlast_not_in_prefix: n=159 top1−0.125 0.1266 [0.0613,0.1895] n=159 k=115 (top1 0.252) MRR 0.443 gap 0.00044 [0.00000,0.00086] n=159 k=115 frac gap>0 0.535; positive_control_last: n=127 top1−0.125 0.3238 [0.2372,0.4104] n=127 k=127 (top1 0.449) MRR 0.587 gap 0.01080 [0.00729,0.01461] n=127 k=127 frac gap>0 0.732; rows completed 393/393 (errors 0); original cache reused True  NOT MET  preference for the AV's original word among 8 one-word variants; not a truth label; in_full_prefix is a string proxy
- 2026-09-09T10:32:24  D1  D1  threshold=CI95 (cluster by explanation) of [persist_word(random) − persist_word(own)] on non-last rows (n ≤ 120) ≤ 0 → MET; > 0 → NOT MET; straddles or < 60 rows completed → INCONCLUSIVE  observed=non-last pooled: n=91 persist_word own 0.495 random 0.703 diff 0.2088 [0.1111,0.3111] n=91 k=73; persist_claim own 0.236 random 0.345 diff 0.1094 [0.0806,0.1378] n=91 k=73; format-break own 0.000 random 0.000; nonlast_in_prefix: n=46 persist_word own 0.696 random 0.848 diff 0.1522 [0.0217,0.2889] n=46 k=41; persist_claim own 0.258 random 0.354 diff 0.0956 [0.0478,0.1377] n=46 k=41; format-break own 0.000 random 0.000; nonlast_not_in_prefix: n=45 persist_word own 0.289 random 0.556 diff 0.2667 [0.1304,0.4222] n=45 k=43; persist_claim own 0.213 random 0.337 diff 0.1234 [0.0885,0.1636] n=45 k=43; format-break own 0.000 random 0.000; positive_control_last: n=20 persist_word own 0.550 random 0.800 diff 0.2500 [0.0500,0.4500] n=20 k=20; persist_claim own 0.409 random 0.514 diff 0.1052 [0.0633,0.1526] n=20 k=20; format-break own 0.000 random 0.000; positive control quoted_token_ok own 0.800 random 0.900 reference 0.850; rows completed 111/140  NOT MET  concerns the AV's output under a vector edit only; MET/INCONCLUSIVE with the positive control NOT MET = the AV re-asserts from remaining content or the AR direction is not what the AV reads

## Stage status, cut rules and costs

| stage | phase | cumulative min (script + judgement) | judgement min | failures | blocked | cut rules |
|---|---|---|---|---|---|---|
| V0 | done | 5.0 | 2.8 | 0 |  | A1(a) paraphrases 2+2 -> 1+1 (light1, aggr1); A1(b) drop the negation candidate; A1(c) contexts 60 -> 40 (dev 10 stays; eval 50 -> 30 by selection order); B1(a) fillings per template 5 -> 4 (drop f4): 64 contexts |
| B1 | done | 12.4 | 0.8 | 0 |  | — |
| A1 | done | 27.0 | 17.8 | 0 |  | — |
| K1 | done | 12.8 | 0.0 | 0 |  | — |
| D1 | done | 60.2 | 0.0 | 0 |  | — |

Measured per-call costs (V0, 5 calls each, mean s): target_ctx_forward_hidden 0.67, target_256_forward_hidden 0.59, av_sampled_200 10.27, av_greedy_200 9.91, ar_score 0.51
Orchestrator judgement rate used for the re-budget: {"rewrite": 0.13760873834292092, "label": 0.13760873834292092, "equiv": 0.13760873834292092} min/task (total awaiting minutes / 20 tasks (no per-type timing given)). Cut rules applied: A1(a) paraphrases 2+2 -> 1+1 (light1, aggr1); A1(b) drop the negation candidate; A1(c) contexts 60 -> 40 (dev 10 stays; eval 50 -> 30 by selection order); B1(a) fillings per template 5 -> 4 (drop f4): 64 contexts.

## Human review pack (open `<stage>_review_blind.csv` first, `<stage>_review_key.csv` after)

| file | rows |
|---|---|
| v0_av.jsonl | 10 rows |
| v0_settings.json | 21527 bytes |
| v0_progress.json | 1329 bytes |
| v0_check.md | 5201 bytes |
| v0_bench.json | 54375 bytes |
| v0_agent_tasks_bench.jsonl | 20 rows |
| v0_agent_outputs_bench.jsonl | 20 rows |
| b1_contexts.csv | 64 rows |
| b1_av.jsonl | 64 rows |
| b1_slots.csv | 192 rows |
| b1_texts.jsonl | 64 rows |
| b1_scores.csv | 128 rows |
| b1_summary.md | 3453 bytes |
| b1_review_blind.csv | 8 rows |
| b1_review_key.csv | 8 rows |
| b1_settings.json | 5773 bytes |
| b1_progress.json | 1098 bytes |
| b1_carriers.csv | 64 rows |
| b1_agent_tasks_equiv.jsonl | 0 rows |
| b1_agent_tasks_fact_swap.jsonl | 0 rows |
| b1_agent_tasks_rewrite.jsonl | 0 rows |
| b1_agent_tasks_slot_verify.jsonl | 8 rows |
| b1_agent_tasks_swapcheck.jsonl | 0 rows |
| b1_agent_outputs_slot_verify.jsonl | 8 rows |
| a1_contexts.csv | 159 rows |
| a1_av.jsonl | 40 rows |
| a1_slots.csv | 54 rows |
| a1_candidates.jsonl | 218 rows |
| a1_realizations.jsonl | 419 rows |
| a1_texts.jsonl | 459 rows |
| a1_scores.csv | 459 rows |
| a1_summary.md | 31866 bytes |
| a1_review_blind.csv | 182 rows |
| a1_review_key.csv | 182 rows |
| a1_settings.json | 9021 bytes |
| a1_progress.json | 3766 bytes |
| a1_paraphrase_rows.csv | 248 rows |
| a1_slot_stats.csv | 54 rows |
| a1_selection.csv | 40 rows |
| a1_agent_tasks_candcheck.jsonl | 87 rows |
| a1_agent_tasks_corrcheck.jsonl | 54 rows |
| a1_agent_tasks_correction.jsonl | 46 rows |
| a1_agent_tasks_corrupt.jsonl | 94 rows |
| a1_agent_tasks_equiv.jsonl | 248 rows |
| a1_agent_tasks_label_cand.jsonl | 70 rows |
| a1_agent_tasks_label_orig.jsonl | 54 rows |
| a1_agent_tasks_rewrite.jsonl | 124 rows |
| a1_agent_tasks_slot_verify.jsonl | 56 rows |
| a1_agent_outputs_candcheck.jsonl | 87 rows |
| a1_agent_outputs_corrcheck.jsonl | 54 rows |
| a1_agent_outputs_correction.jsonl | 46 rows |
| a1_agent_outputs_corrupt.jsonl | 94 rows |
| a1_agent_outputs_equiv.jsonl | 248 rows |
| a1_agent_outputs_label_cand.jsonl | 70 rows |
| a1_agent_outputs_label_orig.jsonl | 54 rows |
| a1_agent_outputs_rewrite.jsonl | 124 rows |
| a1_agent_outputs_slot_verify.jsonl | 56 rows |
| k1_texts.jsonl | 393 rows |
| k1_summary.md | 11264 bytes |
| k1_review_blind.csv | 69 rows |
| k1_review_key.csv | 69 rows |
| k1_settings.json | 2382 bytes |
| k1_progress.json | 680 bytes |
| k1_rows.csv | 393 rows |
| d1_av.jsonl | 222 rows |
| d1_summary.md | 23068 bytes |
| d1_review_blind.csv | 140 rows |
| d1_review_key.csv | 140 rows |
| d1_settings.json | 2809 bytes |
| d1_progress.json | 859 bytes |
| d1_rows.csv | 140 rows |
| d1_sample.csv | 380 rows |
| out/b1_acts.npz | 918776 bytes (gitignored) |
| out/a1_acts.npz | 574268 bytes (gitignored) |
| out/d1_vectors.npz | 2402476 bytes (gitignored) |
| out/b1_preds.npz | 934294 bytes (gitignored) |
| out/a1_preds.npz | 6712392 bytes (gitignored) |

Every analysis script accepts `--labels <csv>` (columns item_type,item_id,field,value) and recomputes its summary from human labels without touching raw scores.


---

# V0 — checks, benchmark, re-budget

## V0 check — artifacts, benchmark, pipeline verification, orchestrator throughput, re-budget (round 4)

git ce597b2b; settings in v0_settings.json; bench in v0_bench.json; generations in v0_av.jsonl; tasks v0_agent_tasks_bench.jsonl / outputs v0_agent_outputs_bench.jsonl

### Artifact checks

| check | got | want | ok |
|---|---|---|---|
| stimuli rows | 200 | 200 | OK |
| explanations rows | 200 | 200 | OK |
| s2_claims rows | 671 | 671 | OK |
| s3_edits rows | 538 | 538 | OK |
| s3_scores rows | 2152 | >0 | OK |
| t2b_claims rows | 691 | 691 | OK |
| acts_L20 h20 shape | (200, 3584) | (200, 3584) | OK |
| t2b_in_full_prefix rows | 691 | 691 | OK |
| t2b_in_full_prefix True | 257 | 257 | OK |
| t2b corrupt_det rows | 393 | 393 | OK |
| corrupt_det rows with in_full_prefix | 393 | 393 | OK |
| corrupt_det is_last==False | 266 | 266 | OK |
| corrupt_det is_last==False & in_full_prefix | 107 | 107 | OK |
| corrupt_det is_last==True | 127 | 127 | OK |
| nla_lib.py present | True | True | OK |
| s2_deletion.py present | True | True | OK |
| s3_corrupt.py present | True | True | OK |
| c2_matched.py present | True | True | OK |

### Measured costs (5 calls each; mean / min / max seconds; MPS synchronised; first call includes warm-up)

| call type | mean s | min s | max s | note |
|---|---|---|---|---|
| target_ctx_forward_hidden | 0.675 | 0.237 | 2.365 | {"tokens": 66} |
| target_256_forward_hidden | 0.594 | 0.585 | 0.617 | {"tokens": 256} |
| av_sampled_200 | 10.270 | 9.747 | 11.732 | {"n_tokens": [144, 141, 146, 144, 141], "parse_ok": [true, true, true, true, true], "ended_with_close_tag": [true, true, true, true, true], "ended_with_eos": [true, true, true, true, true]} |
| av_greedy_200 | 9.906 | 9.634 | 10.035 | {"n_tokens": [145, 143, 146, 145, 140], "parse_ok": [true, true, true, true, true], "ended_with_close_tag": [true, true, true, true, true], "ended_with_eos": [true, true, true, true, true]} |
| ar_score | 0.505 | 0.279 | 1.274 | {} |

- model loads: TARGET 7 s, AV 5 s, AR 4 s; RSS after TARGET free 0.5 G, after AV free 0.6 G
- block-20 activation of stimulus 0 recomputed from the 512-token document vs acts_L20: 1−cos = -2.22e-16

### Pipeline verification (dev items only)

| check | result | pass |
|---|---|---|
| (1) stimuli 0 and 1 give different greedy explanations | different=True; greedy equals round-1 explanation for stimuli 0–4: [True, True, True, True, True] | OK |
| (2) s(h_i, z_i) > s(h_i, z_(i+5) mod 10), stimuli 0–9 | 10/10 | OK |
| (3) z_0 scored five times: max Δcos | 0.00e+00 | OK |
| (4) dummy edited text passes the prefix/suffix asserts | stim 0 sentence span [175, 420] dup=False | OK |
| (5) longest round-1 explanation in the AR template | stim 184: ar_input_tokens=152 (<1024); round-1 generations ending with neither </explanation> nor EOS: 0 [] | OK |
| (6) extractor = nla_lib.Target (Qwen/Qwen2.5-7B-Instruct, snapshot a09a35458c702b33eeacc393d103063234e8bc28); AV.model( calls outside verbalize* | scanned ['r4_lib.py', 'v0_check.py']; hits {} | OK |
| (7) B1 position check: all 80 contexts t ≥ 50 | min t=55; filler2 applied=False; len_mismatch pairs=1; final token '.' everywhere=True; token id at t matches within every pair=True | OK |

### Orchestrator throughput (20-task sample: 10 rewrite, 5 label, 5 equiv; outputs used for nothing else)

- wall-clock between AWAITING and validation: 2.8 min for 20 tasks
- per-task minutes used for the re-budget (total awaiting minutes / 20 tasks (no per-type timing given)): rewrite 0.14, label 0.14, equiv 0.14
- assumed rates for unmeasured types: slot_verify and edit_check at the measured label rate; fact_swap / detail_sub / relation_rev / negation / correction at max(label, 0.5 x rewrite)

### Re-budget (measured costs × PLAN call counts + judgement minutes; cut rules applied in the pre-declared order until the projection fits the cap)

| stage | params | compute min | judgement min | projected min | cap | over cap |
|---|---|---|---|---|---|---|
| A1 | {"n_ctx": 60, "n_par": 4, "negation": true} | 36.9 | 617.6 | 654.5 | 210 | YES |
| A1 | {"n_ctx": 60, "n_par": 2, "negation": true} | 27.2 | 459.1 | 486.3 | 210 | YES |
| A1 | {"n_ctx": 60, "n_par": 2, "negation": false} | 24.2 | 360.0 | 384.2 | 210 | YES |
| A1 | {"n_ctx": 40, "n_par": 2, "negation": false} | 16.2 | 240.0 | 256.2 | 210 | YES |
| B1 | {"n_ctx": 80, "n_par": 4} | 22.3 | 165.1 | 187.4 | 150 | YES |
| B1 | {"n_ctx": 64, "n_par": 4} | 17.9 | 132.1 | 150.0 | 150 | no |
| K1 | {} | 26.7 | 0.0 | 26.7 | 45 | no |
| D1 | {"n_rows": 140} | 51.2 | 0.0 | 51.2 | 60 | no |

#### Cut rules applied

- A1(a) paraphrases 2+2 -> 1+1 (light1, aggr1)
- A1(b) drop the negation candidate
- A1(c) contexts 60 -> 40 (dev 10 stays; eval 50 -> 30 by selection order)
- B1(a) fillings per template 5 -> 4 (drop f4): 64 contexts

- total projected 484 min for B1 + A1 + K1 + D1 (hard stop 10 h = 600 min from the first round-4 RUNLOG line; T9 reserve 30 min)
- projection assumptions: {"b1_slot_verify_per_context": 2.0, "a1_slots_per_context": 2.0, "a1_slot_verify_per_slot": 1.5, "a1_contradicted_fraction": 0.3, "a1_entity_slot_fraction": 0.5}
- V0 cumulative minutes (script + judgement): 5.0 (cap 30)

---

# B1 — controlled paired contexts (human-designed; PRIMARY CONTROLLED)

## B1 summary — controlled paired contexts, meanings A/B (claude labels)

git 07fcc860; settings in b1_settings.json; progress in b1_progress.json

### Kill test

- 2026-09-09T02:25:05  B1  B1  threshold=CI95 (cluster by pair, eval) of mean D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)] over valid English paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval carriers < 32 → INCONCLUSIVE  observed=mean D=nan [nan,nan] n=0 k=0 (eligible eval carriers in primary 0, of 48 eval contexts); both-sides-correct nan [nan,nan] n=0 k=0; D orig-only nan [nan,nan] n=0 k=0; by family: n/a; mean cos(h_A,h_B) 0.9927; omission 64 redundant 0 dup_sentence 0 swap_invalid 0 no_valid_paraphrase 0; av_asserts mismatch 0; invalid realizations by transform {"light1": 0, "light2": 0, "aggr1": 0, "aggr2": 0}  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference reversal under this scorer at this position with this n (never 'the fact is absent from the activation')  (already appended by the first analysis run; not duplicated)

### Counts

- contexts 64 (dev 16, eval 48); pairs 32; generations 64 (parse_ok 64, cjk 0, errors 0)
- candidate slots 8 of 192 sentences; asserting sentences 0
- carriers: eligible 0; omission 64; redundant 0; dup_sentence 0; av_asserts mismatch (AV asserted the other meaning) 0; swap invalid 0; in primary 0 (eval 0, dev 0)
- realizations 0; paraphrases 0; invalid (equiv No) by transform {"light1": 0, "light2": 0, "aggr1": 0, "aggr2": 0}; detected duplicates 0; dup_realization flagged by the editor 0
- eligibility by pair table: eval pairs with both contexts in primary 0

### Primary statistics (eval, in-primary carriers; cluster bootstrap by pair)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| D (paraphrase-averaged μ, orig excluded) | nan | nan | nan | 0 | 0 |
| D (orig only) | nan | nan | nan | 0 | 0 |
| both-sides-correct rate | nan | nan | nan | 0 | 0 |
| both-sides-correct rate (orig only) | nan | nan | nan | 0 | 0 |
| μ_A(h_A) − μ_B(h_A) | nan | nan | nan | 0 | 0 |
| μ_B(h_B) − μ_A(h_B) | nan | nan | nan | 0 | 0 |
| deletion Δ (cos(deletion) − cos(carrier), own activation) | nan | nan | nan | 0 | 0 |

### By family (eval, in-primary)

| family | n | D mean | CI lo | CI hi | both-sides-correct | D orig-only | n pairs |
|---|---|---|---|---|---|---|---|
| F1 entity/recipient | 0 | | | | | | 0 |
| F2 relation/order | 0 | | | | | | 0 |
| F3 numerical detail | 0 | | | | | | 0 |
| F4 outcome/polarity | 0 | | | | | | 0 |

### 2×2 blocks (eval, in-primary; truth = meaning entailed / contradicted by the activation's context; slot type entity = F1, detail = F2–F4)


### Per-context absolute scores

| quantity | n | mean | min | max |
|---|---|---|---|---|
| s(h_own, carrier) = cos(h, AR(own explanation)) | 64 | 0.83905 | 0.80165 | 0.87546 |
| s(h_other, carrier) | 64 | 0.83723 | 0.79312 | 0.87682 |
| cos(h_A, h_B) per pair | 32 | 0.99268 | 0.96760 | 0.99920 |

- t (extraction position) per context: min 55 max 67; len_mismatch pairs 0

### Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

### 5 fixed verbatim examples (seed 0; eval in-primary carriers)


- review sheets: b1_review_blind.csv (8 rows: every eligible fact slot first, then realizations, seed 0) — open first; b1_review_key.csv after

---

# A1 — natural AV claims (human-designed; PRIMARY NATURAL)

## A1 summary — natural AV claims, paraphrase-averaged semantic preference (claude labels)

git 321485a3; settings in a1_settings.json; progress in a1_progress.json; cut rules A1(a)(b)(c) applied (V0)

### Kill tests

- 2026-09-09T02:53:44  A1  A1  threshold=CI95 (cluster by context, eval) of mean G = μ_correct − mean_false μ_m over valid paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval slots < 30 → INCONCLUSIVE  observed=mean G=0.00319 [-0.00035,0.00674] n=4 k=4 (eligible eval slots in primary 4 of 39 eval slots; 33 eligible); correct-ranks-first 0.500 [0.000,1.000] n=4 k=4; frac comparisons won 0.625 [0.250,1.000] n=4 k=4; G orig-only 0.00300 [-0.00025,0.00626] n=4 k=4; by category (μ_correct − μ_false): detail_sub 0.00298 [-0.00115,0.00710] n=4 k=4; entity_sub 0.00196 [-0.00014,0.00499] n=3 k=3  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference for the correct meaning under this scorer with this n (never 'the information is absent')  (already appended by the first analysis run; not duplicated)
- 2026-09-09T02:53:44  A1  A1-nat  threshold=CI95 (by context, eval) of mean [μ_correction − μ_original] on natural-error slots ≤ 0 → MET; > 0 → NOT MET; straddles or natural-error eval slots < 15 → INCONCLUSIVE (count reported; injected errors never substituted)  observed=mean [μ_correction − μ_original]=0.00113 [-0.00176,0.00465] n=4 k=4 (natural-error eval slots 4; contradicted eval originals 37; valid corrections 7 of 46); orig-only 0.00102 [-0.00145,0.00369] n=4 k=4  INCONCLUSIVE  MET/INCONCLUSIVE = the scorer does not detectably prefer the corrected version of the AV's own errors at this n  (already appended by the first analysis run; not duplicated)

### Counts

- contexts 40 (dev 10, eval 30); generations 40 (parse_ok 40, cjk 5, errors 0)
- slots 54 (entity 37, detail 17); contexts with 0/1/2 slots: 1:20, 2:17; contexts without any slot 3
- slot_verify asserts yes 50 / no 4; ineligible: {"no_claim": 4, "fact_repeated": 2, "original_undetermined": 1}
- label_orig: {"contradicted": 51, "entailed": 2, "undetermined": 1}; evidence_found rate 0.98
- eligible slots 47; in primary 8 (eval 4, dev 4); primary exclusions {"no_valid_correction": 39}
- candidates 218 by category {"detail_sub": 47, "relation_rev": 47, "original_contradicted": 46, "correction": 46, "entity_sub": 31, "correct_original": 1}; by role {"false": 69, "natural_error_original": 46, "invalid_correction": 39, "dropped_NONE": 28, "false_edit_rejected": 17, "false_duplicate": 10, "correct": 8, "false_descriptive": 1}
- natural-error slots (contradicted original with a valid correction and paraphrases): 7 (eval 4)
- realizations 419; paraphrases 248; invalid (equiv No) by transform {"light1": 0, "aggr1": 0}; detected duplicates 0

### (B) Primary: correct-meaning preference (eval, in-primary slots; cluster by context)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| G = μ_correct − mean_false μ_m | 0.00319 | -0.00035 | 0.00674 | 4 | 4 |
| G (orig only) | 0.00300 | -0.00025 | 0.00626 | 4 | 4 |
| correct-ranks-first rate | 0.500 | 0.000 | 1.000 | 4 | 4 |
| correct-ranks-first (orig only) | 0.500 | 0.000 | 1.000 | 4 | 4 |
| fraction of correct-vs-false comparisons won | 0.625 | 0.250 | 1.000 | 4 | 4 |
| G, dev | 0.00232 | 0.00003 | 0.00461 | 4 | 4 |
| G, entity slots | 0.00319 | -0.00035 | 0.00674 | 4 | 4 |
| G, detail slots | nan | nan | nan | 0 | 0 |
| G, slots whose correct meaning is the original (entailed) | nan | nan | nan | 0 | 0 |
| G, slots whose correct meaning is a correction | 0.00319 | -0.00035 | 0.00674 | 4 | 4 |

#### By corruption category (eval; μ_correct − μ_false per (slot, false meaning); cluster by context)

| category | n | mean diff | CI lo | CI hi | frac won | diff orig-only |
|---|---|---|---|---|---|---|
| detail_sub | 4 | 0.00298 | -0.00115 | 0.00710 | 0.500 [0.000,1.000] | 0.00279 [-0.00081,0.00639] |
| entity_sub | 3 | 0.00196 | -0.00014 | 0.00499 | 0.667 [0.000,1.000] | 0.00161 [0.00030,0.00421] |

### (C) Natural errors (eval; μ_correction − μ_original; cluster by context)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| μ_correction − μ_original | 0.00113 | -0.00176 | 0.00465 | 4 | 4 |
| orig-only | 0.00102 | -0.00145 | 0.00369 | 4 | 4 |
| frac correction > original | 0.500 | 0.000 | 1.000 | 4 | 4 |

### (A) Paraphrase sensitivity (eval, valid paraphrases; cluster by context)

| group × truth | n | mean abs Δ | CI lo | CI hi | signed Δ mean | signed CI |
|---|---|---|---|---|---|---|
| light × entailed | 4 | 0.00103 | 0.00071 | 0.00124 | -0.00075 | [-0.00124,0.00012] |
| light × contradicted | 83 | 0.00130 | 0.00071 | 0.00221 | -0.00084 | [-0.00182,-0.00016] |
| aggressive × entailed | 4 | 0.00564 | 0.00362 | 0.00767 | -0.00180 | [-0.00662,0.00484] |
| aggressive × contradicted | 83 | 0.00426 | 0.00298 | 0.00586 | 0.00054 | [-0.00166,0.00271] |
| all × entailed | 8 | 0.00334 | 0.00237 | 0.00430 | -0.00128 | [-0.00393,0.00248] |
| all × contradicted | 166 | 0.00278 | 0.00202 | 0.00381 | -0.00015 | [-0.00137,0.00094] |

P_correct − P_false within slot (paired, cluster by context): -0.00005 [-0.00086,0.00042] n=4 k=4

### 2×2 blocks (eval, valid paraphrases in in-primary and natural-error slots; truth entailed / contradicted × slot type entity / detail)

#### μ (cos of valid paraphrases)

| truth \ slot type | entity | detail |
|---|---|---|
| entailed | n=8 mean 0.86540 [0.83821,0.88880] | n=0 |
| contradicted | n=22 mean 0.86376 [0.83392,0.89119] | n=0 |

Distributions for the four cells:

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| μ (cos of valid paraphrases) / entailed × entity | 8 | 0.86540 | 0.02861 | 0.00082 | 0.82394 | 0.82482 | 0.82571 | 0.85007 | 0.86899 | 0.88482 | 0.89753 | 0.89840 | 0.89926 |
| μ (cos of valid paraphrases) / entailed × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| μ (cos of valid paraphrases) / contradicted × entity | 22 | 0.86376 | 0.03158 | 0.00100 | 0.81641 | 0.81677 | 0.81888 | 0.82871 | 0.87375 | 0.89378 | 0.89905 | 0.89983 | 0.90101 |
| μ (cos of valid paraphrases) / contradicted × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |

#### P: |Δ| vs orig

| truth \ slot type | entity | detail |
|---|---|---|
| entailed | n=8 mean 0.00334 [0.00237,0.00430] | n=0 |
| contradicted | n=22 mean 0.00336 [0.00229,0.00405] | n=0 |

Distributions for the four cells:

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P: |Δ| vs orig / entailed × entity | 8 | 0.00334 | 0.00291 | 0.00001 | 0.00055 | 0.00073 | 0.00091 | 0.00116 | 0.00242 | 0.00470 | 0.00766 | 0.00767 | 0.00769 |
| P: |Δ| vs orig / entailed × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| P: |Δ| vs orig / contradicted × entity | 22 | 0.00336 | 0.00284 | 0.00001 | 0.00040 | 0.00043 | 0.00054 | 0.00079 | 0.00230 | 0.00628 | 0.00770 | 0.00789 | 0.00793 |
| P: |Δ| vs orig / contradicted × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |

#### P: signed Δ vs orig

| truth \ slot type | entity | detail |
|---|---|---|
| entailed | n=8 mean -0.00128 [-0.00393,0.00248] | n=0 |
| contradicted | n=22 mean -0.00119 [-0.00393,0.00250] | n=0 |

Distributions for the four cells:

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P: signed Δ vs orig / entailed × entity | 8 | -0.00128 | 0.00440 | 0.00002 | -0.00765 | -0.00627 | -0.00489 | -0.00358 | -0.00124 | -0.00066 | 0.00269 | 0.00519 | 0.00769 |
| P: signed Δ vs orig / entailed × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| P: signed Δ vs orig / contradicted × entity | 22 | -0.00119 | 0.00429 | 0.00002 | -0.00793 | -0.00717 | -0.00645 | -0.00303 | -0.00137 | 0.00019 | 0.00581 | 0.00768 | 0.00789 |
| P: signed Δ vs orig / contradicted × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |

#### V (reconstruction movement vs orig wording)

| truth \ slot type | entity | detail |
|---|---|---|
| entailed | n=8 mean 0.00160 [0.00091,0.00230] | n=0 |
| contradicted | n=22 mean 0.00165 [0.00093,0.00252] | n=0 |

Distributions for the four cells:

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V (reconstruction movement vs orig wording) / entailed × entity | 8 | 0.00160 | 0.00190 | 0.00000 | 0.00011 | 0.00011 | 0.00012 | 0.00016 | 0.00079 | 0.00244 | 0.00427 | 0.00459 | 0.00491 |
| V (reconstruction movement vs orig wording) / entailed × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| V (reconstruction movement vs orig wording) / contradicted × entity | 22 | 0.00165 | 0.00197 | 0.00000 | 0.00010 | 0.00010 | 0.00012 | 0.00014 | 0.00080 | 0.00212 | 0.00434 | 0.00513 | 0.00657 |
| V (reconstruction movement vs orig wording) / contradicted × detail | 0 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan |

#### G by slot type (eval, in-primary)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| G / entity | 0.00319 | -0.00035 | 0.00674 | 4 | 4 |
| G / detail | nan | nan | nan | 0 | 0 |

### (D) Deletion and movement

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| deletion Δ = cos(deletion) − cos(carrier), eligible eval slots | -0.03226 | -0.03940 | -0.02510 | 33 | 26 |
| V, light1 (eval, valid) | 0.00028 | 0.00016 | 0.00051 | 88 | 26 |
| V, aggr1 (eval, valid) | 0.00304 | 0.00212 | 0.00423 | 88 | 26 |

- s(h, own explanation): mean 0.88058 over 37 contexts with slots

### Lexical checks (advisory; agreement with equiv)

| transform | n | equiv Yes | names_kept | numbers_kept | polarity_kept | len_ok | all four & Yes | all four & No |
|---|---|---|---|---|---|---|---|---|
| light1 | 124 | 124 | 1.00 | 1.00 | 1.00 | 1.00 | 124 | 0 |
| aggr1 | 124 | 124 | 1.00 | 1.00 | 1.00 | 0.92 | 114 | 0 |

### Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G (eval) | 4 | 0.00319 | 0.00420 | 0.00002 | -0.00092 | -0.00075 | -0.00058 | -0.00007 | 0.00297 | 0.00623 | 0.00714 | 0.00744 | 0.00775 |
| G orig-only (eval) | 4 | 0.00300 | 0.00403 | 0.00002 | -0.00045 | -0.00039 | -0.00033 | -0.00015 | 0.00221 | 0.00537 | 0.00697 | 0.00751 | 0.00804 |
| μ_correct (eval) | 4 | 0.86540 | 0.03077 | 0.00095 | 0.82520 | 0.83059 | 0.83597 | 0.85213 | 0.86918 | 0.88245 | 0.89180 | 0.89491 | 0.89803 |
| frac_won (eval) | 4 | 0.62500 | 0.47871 | 0.22917 | 0.00000 | 0.07500 | 0.15000 | 0.37500 | 0.75000 | 1.00000 | 1.00000 | 1.00000 | 1.00000 |
| μ_correction − μ_original (eval natural errors) | 4 | 0.00113 | 0.00396 | 0.00002 | -0.00270 | -0.00241 | -0.00213 | -0.00128 | 0.00036 | 0.00277 | 0.00499 | 0.00573 | 0.00647 |
| μ_correct − μ_false / detail_sub (eval) | 4 | 0.00298 | 0.00481 | 0.00002 | -0.00170 | -0.00153 | -0.00137 | -0.00087 | 0.00293 | 0.00678 | 0.00736 | 0.00755 | 0.00775 |
| μ_correct − μ_false / entity_sub (eval) | 3 | 0.00196 | 0.00269 | 0.00001 | -0.00014 | -0.00002 | 0.00009 | 0.00044 | 0.00103 | 0.00301 | 0.00420 | 0.00460 | 0.00499 |
| |Δ| vs orig, light1 (eval, valid) | 88 | 0.00128 | 0.00192 | 0.00000 | 0.00000 | 0.00006 | 0.00013 | 0.00021 | 0.00066 | 0.00146 | 0.00188 | 0.00661 | 0.00848 |
| V, light1 (eval, valid) | 88 | 0.00028 | 0.00049 | 0.00000 | 0.00006 | 0.00008 | 0.00009 | 0.00010 | 0.00016 | 0.00022 | 0.00035 | 0.00066 | 0.00281 |
| |Δ| vs orig, aggr1 (eval, valid) | 88 | 0.00428 | 0.00392 | 0.00002 | 0.00010 | 0.00049 | 0.00073 | 0.00187 | 0.00314 | 0.00578 | 0.00812 | 0.01207 | 0.01938 |
| V, aggr1 (eval, valid) | 88 | 0.00304 | 0.00280 | 0.00001 | 0.00052 | 0.00057 | 0.00083 | 0.00119 | 0.00192 | 0.00400 | 0.00557 | 0.00781 | 0.01567 |
| deletion Δ (eligible eval slots) | 33 | -0.03226 | 0.01927 | 0.00037 | -0.10174 | -0.05883 | -0.05357 | -0.03925 | -0.02730 | -0.02465 | -0.01428 | -0.00664 | -0.00065 |

### 5 fixed verbatim examples (seed 0; eval in-primary slots)

#### c37_entity (context 37, entity, focus 'Dickensian', label_orig contradicted)

- prefix tail (last 400 chars): 'rses have been added to the rhyme , including a version with a total of 15 stanzas in a chapbook of the 19th century . The second verse , probably added as part of these extensions has become a standard part of the nursery rhyme . Early versions took the form : \n Up Jack got , and home did trot , \n As fast as he could caper ; \n To old Dame Dob , who patched his nob \n With vinegar and brown paper .'
- explanation: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and recovery.\n\nThe sentence mid-list "Another verse has : \' The doctor then says the child was sickened and a second stanza follows : \' Mary washed the rotten tooth \'." suggests a third specific clause or clause describing the remedy or attribution.\n\nFinal token " . " closes an incomplete clause mid-sentence (" Mary : \' And he went : And the girl returned home ; With the doctor \'s office and the girl had her remedies . "), strongly expecting continuation like " " or "This is a folk variant" or "And other details."'
- slot sentence: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and recovery.'
- G = 0.00573; correct-first 1.0; μ_correct 0.82520
  - candidate [original_contradicted / role natural_error_original / label contradicted / edit_ok True]: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and recovery.'
    - [orig] valid=True cos=0.82266: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and recovery.'
    - [light1] valid=True cos=0.82079: 'Formal wiki-style list structure with verse excerpts that show lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and recovery.'
    - [aggr1] valid=True cos=0.81667: 'Specific song lines about a character\'s illness and recovery are listed, with verse excerpts showing lyrical variations on "Dickensian," in a formal wiki-style list structure.'
  - candidate [correction / role correct / label entailed / edit_ok True]: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Jack and Jill," listing specific song lines about a character\'s illness and recovery.'
    - [orig] valid=True cos=0.82765: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Jack and Jill," listing specific song lines about a character\'s illness and recovery.'
    - [light1] valid=True cos=0.82646: 'Formal wiki-style list structure with verse excerpts that show lyrical variations on "Jack and Jill," listing specific song lines about a character\'s illness and recovery.'
    - [aggr1] valid=True cos=0.82394: 'Specific song lines about a character\'s illness and recovery are listed, with verse excerpts showing lyrical variations on "Jack and Jill," in a formal wiki-style list structure.'
  - candidate [entity_sub / role false / label contradicted / edit_ok True]: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Divine," listing specific song lines about a character\'s illness and recovery.'
    - [orig] valid=True cos=0.82344: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Divine," listing specific song lines about a character\'s illness and recovery.'
    - [light1] valid=True cos=0.82174: 'Formal wiki-style list structure with verse excerpts that show lyrical variations on "Divine," listing specific song lines about a character\'s illness and recovery.'
    - [aggr1] valid=True cos=0.81867: 'Specific song lines about a character\'s illness and recovery are listed, with verse excerpts showing lyrical variations on "Divine," in a formal wiki-style list structure.'
  - candidate [detail_sub / role false / label contradicted / edit_ok True]: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and death.'
    - [orig] valid=True cos=0.82291: 'Formal wiki-style list structure with verse excerpts showing lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and death.'
    - [light1] valid=True cos=0.82108: 'Formal wiki-style list structure with verse excerpts that show lyrical variations on "Dickensian," listing specific song lines about a character\'s illness and death.'
    - [aggr1] valid=True cos=0.81641: 'Specific song lines about a character\'s illness and death are listed, with verse excerpts showing lyrical variations on "Dickensian," in a formal wiki-style list structure.'
  - candidate [relation_rev / role dropped_NONE / label  / edit_ok False]: 'NONE'
  - deletion: cos=0.76165; carrier cos=0.82266

#### c36_entity (context 36, entity, focus 'Hopeful', label_orig contradicted)

- prefix tail (last 400 chars): ' ( Ascot Gold Cup ) and defeating three winners of the Epsom Derby . Unusually for a 19th @-@ century racehorse , he was regularly campaigned internationally , winning three consecutive runnings of the Grand Prix de Deauville . Tristan \'s success was achieved despite a dangerous and unpredictable temperament : at the height of his success , he was described as " a very vile @-@ tempered animal " .'
- explanation: 'British encyclopedia entry format with biographical details about a racehorse (Hopeful) providing numbered career statistics and notes.\n\nThe sentence structure "His reputation during his racing career was blotched by drunkenness and ill-discipline ; although a talented horse he suffered a nervous personality and was frequently late or absent from races ." suggests a second clause continuing the negative attributes or legacy issues, likely attributing a cause of his retirement.\n\nFinal token "attribute . " closes a quoted attribution clause ("His reputation was undermined by \'vicious appetite\' for alcohol and other faults ; the trainer described him"), strongly expecting continuation like "He died early" or "His breeding decisions were problematic."'
- slot sentence: 'British encyclopedia entry format with biographical details about a racehorse (Hopeful) providing numbered career statistics and notes.'
- G = 0.00022; correct-first 0.0; μ_correct 0.87726
  - candidate [original_contradicted / role natural_error_original / label contradicted / edit_ok True]: 'British encyclopedia entry format with biographical details about a racehorse (Hopeful) providing numbered career statistics and notes.'
    - [orig] valid=True cos=0.87570: 'British encyclopedia entry format with biographical details about a racehorse (Hopeful) providing numbered career statistics and notes.'
    - [light1] valid=True cos=0.87645: 'British encyclopedia entry format with biographical details about a racehorse (Hopeful) that provide numbered career statistics and notes.'
    - [aggr1] valid=True cos=0.88345: 'Numbered career statistics and notes are provided in biographical details about a racehorse (Hopeful) in a British encyclopedia entry format.'
  - candidate [correction / role correct / label entailed / edit_ok True]: 'British encyclopedia entry format with biographical details about a racehorse (Tristan) providing numbered career statistics and notes.'
    - [orig] valid=True cos=0.87314: 'British encyclopedia entry format with biographical details about a racehorse (Tristan) providing numbered career statistics and notes.'
    - [light1] valid=True cos=0.87369: 'British encyclopedia entry format with biographical details about a racehorse (Tristan) that provide numbered career statistics and notes.'
    - [aggr1] valid=True cos=0.88082: 'Numbered career statistics and notes are provided in biographical details about a racehorse (Tristan) in a British encyclopedia entry format.'
  - candidate [entity_sub / role false / label contradicted / edit_ok True]: 'British encyclopedia entry format with biographical details about a racehorse (Turkish) providing numbered career statistics and notes.'
    - [orig] valid=True cos=0.87284: 'British encyclopedia entry format with biographical details about a racehorse (Turkish) providing numbered career statistics and notes.'
    - [light1] valid=True cos=0.87324: 'British encyclopedia entry format with biographical details about a racehorse (Turkish) that provide numbered career statistics and notes.'
    - [aggr1] valid=True cos=0.87921: 'Numbered career statistics and notes are provided in biographical details about a racehorse (Turkish) in a British encyclopedia entry format.'
  - candidate [detail_sub / role false / label contradicted / edit_ok True]: 'British encyclopedia entry format with biographical details about a greyhound (Hopeful) providing numbered career statistics and notes.'
    - [orig] valid=True cos=0.87355: 'British encyclopedia entry format with biographical details about a greyhound (Hopeful) providing numbered career statistics and notes.'
    - [light1] valid=True cos=0.87427: 'British encyclopedia entry format with biographical details about a greyhound (Hopeful) that provide numbered career statistics and notes.'
    - [aggr1] valid=True cos=0.88144: 'Numbered career statistics and notes are provided in biographical details about a greyhound (Hopeful) in a British encyclopedia entry format.'
  - candidate [relation_rev / role dropped_NONE / label  / edit_ok False]: 'NONE'
  - deletion: cos=0.77396; carrier cos=0.87570

#### c10_entity (context 10, entity, focus 'Americas', label_orig contradicted)

- prefix tail (last 400 chars): 'nds on the location ; it typically peaks in spring , but may continue all year round in warm climates . Young are born fully furred with eyes open ; they are well camouflaged and are mobile within minutes of birth , thus females do not protect or even stay with the young except during nursing . The average litter size is around four , but may be as low as two and as high as seven in warm regions .'
- explanation: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Americas wolf spider).\n\nThe sentence structure "Adults reach sexual maturity at around four years and produce up to six broods annually . Their life span is only around two years . Predators include various birds and mammals" suggests a list of facts concluding with reproduction or mortality details about the species.\n\nFinal token "production . " ends mid-sentence describing life cycle facts ("Estimated reproduction rates are high , and survival rates exclude offspring mortality . Other facts include..."), strongly expecting continuation like "The species\' prey" or "The spider\'s traits include disease" or similar numerical data.'
- slot sentence: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Americas wolf spider).'
- G = -0.00092; correct-first 0.0; μ_correct 0.89803
  - candidate [original_contradicted / role natural_error_original / label contradicted / edit_ok True]: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Americas wolf spider).'
    - [orig] valid=True cos=0.90054: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Americas wolf spider).'
    - [light1] valid=True cos=0.89987: 'Wiki species entry format with an informal taxonomic description listing physical traits and behavior of a mammal species (Americas wolf spider).'
    - [aggr1] valid=True cos=0.89781: 'The physical traits and behavior of a mammal species (Americas wolf spider) are set out in an informal taxonomic description in a wiki species entry format.'
  - candidate [correction / role correct / label entailed / edit_ok True]: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (black-tailed jackrabbit).'
    - [orig] valid=True cos=0.90033: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (black-tailed jackrabbit).'
    - [light1] valid=True cos=0.89926: 'Wiki species entry format with an informal taxonomic description listing physical traits and behavior of a mammal species (black-tailed jackrabbit).'
    - [aggr1] valid=True cos=0.89679: 'The physical traits and behavior of a mammal species (black-tailed jackrabbit) are set out in an informal taxonomic description in a wiki species entry format.'
  - candidate [entity_sub / role false / label contradicted / edit_ok True]: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Che wolf spider).'
    - [orig] valid=True cos=0.90001: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a mammal species (Che wolf spider).'
    - [light1] valid=True cos=0.89912: 'Wiki species entry format with an informal taxonomic description listing physical traits and behavior of a mammal species (Che wolf spider).'
    - [aggr1] valid=True cos=0.89722: 'The physical traits and behavior of a mammal species (Che wolf spider) are set out in an informal taxonomic description in a wiki species entry format.'
  - candidate [detail_sub / role false / label contradicted / edit_ok True]: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a reptile species (Americas wolf spider).'
    - [orig] valid=True cos=0.90154: 'Wiki species entry format with informal taxonomic description listing physical traits and behavior of a reptile species (Americas wolf spider).'
    - [light1] valid=True cos=0.90101: 'Wiki species entry format with an informal taxonomic description listing physical traits and behavior of a reptile species (Americas wolf spider).'
    - [aggr1] valid=True cos=0.89843: 'The physical traits and behavior of a reptile species (Americas wolf spider) are set out in an informal taxonomic description in a wiki species entry format.'
  - candidate [relation_rev / role dropped_NONE / label  / edit_ok False]: 'NONE'
  - deletion: cos=0.87474; carrier cos=0.90054

#### c22_entity (context 22, entity, focus 'American', label_orig contradicted)

- prefix tail (last 400 chars): "ritics , though some felt it took the album 's message too literally . It was a moderate commercial achievement for Cyrus and charted within the top fifty of the Billboard magazine chart Hot Country Songs . The song 's music video was directed by Declan Whitebloom and features scenes of Cyrus at a beach inter cut with clips of Hannah Montana : The Movie . The song was performed in several venues ."
- explanation: 'Wikipedia article format with structured biographical details listing a pop singer\'s performances and appearances for American country music artist Luther없음.\n\nThe sentence ending "Throughout his career he performed several concerts including an opening show and recordings . Other Shows were also produced . The artist made appearances ." suggests a concluding list item or clause describing performances or notable occasions, likely a movie or concert attendance record.\n\nFinal token "produced . " closes an incomplete list ("Some performances he performed certain songs . Several performances were scheduled activities . This artist also attended performances ."), expecting continuation like "He also" or "The most notable ones included" or "His concerts were cancelled in 20XX."'
- slot sentence: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for American country music artist Luther없음."
- G = 0.00775; correct-first 1.0; μ_correct 0.86111
  - candidate [original_contradicted / role natural_error_original / label contradicted / edit_ok True]: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for American country music artist Luther없음."
    - [orig] valid=True cos=0.86370: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for American country music artist Luther없음."
    - [light1] valid=True cos=0.86265: "Wikipedia article format with structured biographical details that list a pop singer's performances and appearances for American country music artist Luther없음."
    - [aggr1] valid=True cos=0.85649: "A pop singer's performances and appearances for American country music artist Luther없음 are listed in structured biographical details in a Wikipedia article format."
  - candidate [correction / role correct / label entailed / edit_ok True]: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for American country music artist Billy Ray Cyrus."
    - [orig] valid=True cos=0.86559: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for American country music artist Billy Ray Cyrus."
    - [light1] valid=True cos=0.86428: "Wikipedia article format with structured biographical details that list a pop singer's performances and appearances for American country music artist Billy Ray Cyrus."
    - [aggr1] valid=True cos=0.85794: "A pop singer's performances and appearances for American country music artist Billy Ray Cyrus are listed in structured biographical details in a Wikipedia article format."
  - candidate [entity_sub / role false_edit_rejected / label  / edit_ok False]: "Wikipedia article format with structured biographical details listing a pop singer's performances and appearances for Darkwolf country music artist Luther없음."
  - candidate [detail_sub / role false / label contradicted / edit_ok True]: "Wikipedia article format with structured biographical details listing a opera singer's performances and appearances for American country music artist Luther없음."
    - [orig] valid=True cos=0.85755: "Wikipedia article format with structured biographical details listing a opera singer's performances and appearances for American country music artist Luther없음."
    - [light1] valid=True cos=0.85712: "Wikipedia article format with structured biographical details that list a opera singer's performances and appearances for American country music artist Luther없음."
    - [aggr1] valid=True cos=0.84961: "A opera singer's performances and appearances for American country music artist Luther없음 are listed in structured biographical details in a Wikipedia article format."
  - candidate [relation_rev / role dropped_NONE / label  / edit_ok False]: 'NONE'
  - deletion: cos=0.84408; carrier cos=0.86370


- review sheets: a1_review_blind.csv (60 rows: every natural-error / correction pair first, then slots and realizations, seed 0) — open first; a1_review_key.csv after

---

# K1 — K-way alternative ranking (desk-designed)

## K1 summary — K-way alternative ranking on deterministic-swap claims (AR only)

git 846a34ea; settings in k1_settings.json; progress in k1_progress.json

### Kill test

- 2026-09-09T03:08:52  K1  K1  threshold=CI95 (cluster by explanation) of (top-1 rate − 0.125) on non-last in_full_prefix rows (n=107) ≤ 0 → MET; > 0 → NOT MET; straddles or < 80 rows completed → INCONCLUSIVE  observed=nonlast_in_prefix: n=107 top1−0.125 0.1834 [0.0962,0.2650] n=107 k=89 (top1 0.308) MRR 0.487 gap 0.00125 [0.00058,0.00202] n=107 k=89 frac gap>0 0.654; nonlast_not_in_prefix: n=159 top1−0.125 0.1266 [0.0613,0.1895] n=159 k=115 (top1 0.252) MRR 0.443 gap 0.00044 [0.00000,0.00086] n=159 k=115 frac gap>0 0.535; positive_control_last: n=127 top1−0.125 0.3238 [0.2372,0.4104] n=127 k=127 (top1 0.449) MRR 0.587 gap 0.01080 [0.00729,0.01461] n=127 k=127 frac gap>0 0.732; rows completed 393/393 (errors 0); original cache reused True  NOT MET  preference for the AV's original word among 8 one-word variants; not a truth label; in_full_prefix is a string proxy

### Counts

- rows 393 (non-last in-prefix 107, non-last not-in-prefix 159, last 127); completed 393; errors 0; pool_short 6; dup_sentence 0
- slot type: non-last entity 235, non-last detail 31
- original cos cache: reused s2 cos_z = True (max |dev| on 20 rows 1.11e-16)

### Per stratum (cluster by explanation)

| stratum | n | n_expl | top1 | top1−0.125 CI | MRR | mean gap | gap CI | frac gap>0 | mean gap_max | mean spread |
|---|---|---|---|---|---|---|---|---|---|---|
| nonlast_in_prefix | 107 | 89 | 0.308 | [0.0962,0.2650] | 0.487 | 0.00125 | [0.00058,0.00202] | 0.654 | -0.00051 | 0.00465 |
| nonlast_not_in_prefix | 159 | 115 | 0.252 | [0.0613,0.1895] | 0.443 | 0.00044 | [0.00000,0.00086] | 0.535 | -0.00114 | 0.00370 |
| positive_control_last | 127 | 127 | 0.449 | [0.2372,0.4104] | 0.587 | 0.01080 | [0.00729,0.01461] | 0.732 | 0.00398 | 0.02203 |

### 2×2 (non-last rows): in_full_prefix × slot type

| in_full_prefix \ slot type | entity | detail |
|---|---|---|
| True | n=99 top1 0.293 [0.213,0.379] gap 0.00094 [0.00039,0.00159] | n=8 top1 0.500 [0.125,0.875] gap 0.00508 [0.00034,0.01046] |
| False | n=136 top1 0.272 [0.197,0.346] gap 0.00048 [-0.00001,0.00096] | n=23 top1 0.130 [0.000,0.273] gap 0.00021 [-0.00006,0.00048] |

Distributions for the four cells (gap):

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap / in_full_prefix=True × entity | 99 | 0.00094 | 0.00316 | 0.00001 | -0.00441 | -0.00213 | -0.00144 | -0.00023 | 0.00035 | 0.00144 | 0.00258 | 0.00467 | 0.02233 |
| gap / in_full_prefix=True × detail | 8 | 0.00508 | 0.00816 | 0.00007 | -0.00055 | -0.00032 | -0.00008 | 0.00022 | 0.00054 | 0.00680 | 0.01753 | 0.01852 | 0.01952 |
| gap / in_full_prefix=False × entity | 136 | 0.00048 | 0.00315 | 0.00001 | -0.01273 | -0.00245 | -0.00167 | -0.00070 | 0.00006 | 0.00129 | 0.00247 | 0.00574 | 0.01554 |
| gap / in_full_prefix=False × detail | 23 | 0.00021 | 0.00068 | 0.00000 | -0.00090 | -0.00063 | -0.00047 | -0.00019 | 0.00013 | 0.00048 | 0.00077 | 0.00118 | 0.00230 |

### Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap / nonlast_in_prefix | 107 | 0.00125 | 0.00385 | 0.00001 | -0.00441 | -0.00198 | -0.00117 | -0.00022 | 0.00035 | 0.00154 | 0.00316 | 0.00656 | 0.02233 |
| gap_max / nonlast_in_prefix | 107 | -0.00051 | 0.00283 | 0.00001 | -0.00614 | -0.00445 | -0.00349 | -0.00164 | -0.00052 | 0.00021 | 0.00131 | 0.00270 | 0.01278 |
| spread / nonlast_in_prefix | 107 | 0.00465 | 0.00651 | 0.00004 | 0.00035 | 0.00085 | 0.00116 | 0.00178 | 0.00289 | 0.00459 | 0.00779 | 0.01325 | 0.04568 |
| rank / nonlast_in_prefix | 107 | 3.59813 | 2.42961 | 5.90302 | 1.00000 | 1.00000 | 1.00000 | 1.00000 | 3.00000 | 5.00000 | 7.40000 | 8.00000 | 8.00000 |
| cos_orig / nonlast_in_prefix | 107 | 0.88784 | 0.03866 | 0.00149 | 0.79396 | 0.81427 | 0.81897 | 0.86883 | 0.89719 | 0.91203 | 0.93047 | 0.94130 | 0.96257 |
| cos_alts_mean / nonlast_in_prefix | 107 | 0.88659 | 0.03935 | 0.00155 | 0.79422 | 0.80759 | 0.81806 | 0.86849 | 0.89652 | 0.91103 | 0.92872 | 0.93896 | 0.96244 |
| gap / nonlast_not_in_prefix | 159 | 0.00044 | 0.00292 | 0.00001 | -0.01273 | -0.00227 | -0.00154 | -0.00051 | 0.00007 | 0.00109 | 0.00229 | 0.00424 | 0.01554 |
| gap_max / nonlast_not_in_prefix | 159 | -0.00114 | 0.00277 | 0.00001 | -0.01592 | -0.00507 | -0.00357 | -0.00211 | -0.00074 | 0.00002 | 0.00076 | 0.00236 | 0.00673 |
| spread / nonlast_not_in_prefix | 159 | 0.00370 | 0.00398 | 0.00002 | 0.00049 | 0.00082 | 0.00093 | 0.00144 | 0.00262 | 0.00409 | 0.00720 | 0.01087 | 0.02911 |
| rank / nonlast_not_in_prefix | 159 | 3.99371 | 2.57912 | 6.65186 | 1.00000 | 1.00000 | 1.00000 | 1.50000 | 3.00000 | 6.00000 | 8.00000 | 8.00000 | 8.00000 |
| cos_orig / nonlast_not_in_prefix | 159 | 0.87962 | 0.04880 | 0.00238 | 0.67928 | 0.79650 | 0.81542 | 0.86406 | 0.89018 | 0.90791 | 0.92649 | 0.93439 | 0.96257 |
| cos_alts_mean / nonlast_not_in_prefix | 159 | 0.87919 | 0.04894 | 0.00239 | 0.67960 | 0.78964 | 0.81386 | 0.86434 | 0.89096 | 0.90810 | 0.92622 | 0.93350 | 0.96266 |
| gap / positive_control_last | 127 | 0.01080 | 0.02153 | 0.00046 | -0.00926 | -0.00272 | -0.00132 | -0.00012 | 0.00129 | 0.00904 | 0.04226 | 0.05345 | 0.14347 |
| gap_max / positive_control_last | 127 | 0.00398 | 0.01269 | 0.00016 | -0.01449 | -0.00493 | -0.00375 | -0.00156 | -0.00026 | 0.00245 | 0.01878 | 0.02628 | 0.07451 |
| spread / positive_control_last | 127 | 0.02203 | 0.03622 | 0.00131 | 0.00038 | 0.00073 | 0.00135 | 0.00270 | 0.00486 | 0.02106 | 0.07258 | 0.08566 | 0.22340 |
| rank / positive_control_last | 127 | 3.15748 | 2.46701 | 6.08611 | 1.00000 | 1.00000 | 1.00000 | 1.00000 | 2.00000 | 5.00000 | 7.00000 | 8.00000 | 8.00000 |
| cos_orig / positive_control_last | 127 | 0.88213 | 0.04498 | 0.00202 | 0.67928 | 0.79955 | 0.81615 | 0.86501 | 0.89184 | 0.90721 | 0.92692 | 0.93790 | 0.96257 |
| cos_alts_mean / positive_control_last | 127 | 0.87133 | 0.04703 | 0.00221 | 0.64475 | 0.79347 | 0.81004 | 0.84956 | 0.88479 | 0.90384 | 0.91476 | 0.92536 | 0.94168 |

### Rank histogram of the original among 8 (per stratum)

- nonlast_in_prefix: rank 1: 33, rank 2: 10, rank 3: 18, rank 4: 8, rank 5: 12, rank 6: 7, rank 7: 8, rank 8: 11
- nonlast_not_in_prefix: rank 1: 40, rank 2: 23, rank 3: 17, rank 4: 11, rank 5: 15, rank 6: 17, rank 7: 11, rank 8: 25
- positive_control_last: rank 1: 57, rank 2: 10, rank 3: 12, rank 4: 10, rank 5: 10, rank 6: 8, rank 7: 10, rank 8: 10

### 5 fixed verbatim examples (seed 0; non-last in-prefix rows)

#### row 481 (stim 142, claim 0/3, entity, word_orig 'Jewish')

- prefix tail (last 400 chars): "syt , grew up in Warsaw , survived the Warsaw Ghetto , the Majdanek concentration camp , and two slave labor camps . Her first husband died in the war . She considered the day of her liberation as the most horrible day of her life , as she realized that she was alone , her parents and siblings gone . Norman 's father , Zacharias Finkelstein , active in Hashomer Hatzair , was a survivor of both the"
- claim: 'Historical/academic book description format with numbered testimonies listing Jewish Holocaust survivors, detailing biographical credentials and testimonies about the Holocaust.'
- cos orig 0.89367; alternatives: Canadian 0.89482, UK 0.89480, Che 0.89507, Over 0.89508, C60 0.89534, Global 0.89524, Mike 0.89667
- rank 8, gap -0.00162

#### row 411 (stim 120, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): ' series developer Beau Willimon and directed by executive producer David Fincher . The episode also earned 3 other Emmy nominations as well as WGA : Episodic Drama and DGA – Drama Series nominations . \n Frank Underwood ( Kevin Spacey ) is an ambitious Democratic congressman and the House Majority Whip . Underwood helped ensure the election of President Garrett Walker ( Michel Gill ) , who promised'
- claim: 'The sentence "The character is a Democrat congressman named Todd Young who is running for Senate and vowed" contains a specific historical reference ("Obama\'s promise to support him"), implying a backstory about Biden\'s political deal or campaign promise.'
- cos orig 0.87933; alternatives: Italian 0.87777, Muslim 0.87723, Darren 0.87925, Reviewers 0.88009, Lower 0.87880, EMI 0.87755, Known 0.87725
- rank 2, gap 0.00105

#### row 277 (stim 80, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): 'sed France into administrative departments in order to rebalance the uneven distribution of French wealth , which had been subject to feudalism under the monarchical Ancien Régime . \n \n = = Rebellion in Southern France = = \n \n In July 1793 Captain Napoleon Bonaparte , an artillery officer , was placed under the command of Jean @-@ Baptiste Carteaux to deal with rebels from Marseille situated in Av'
- claim: 'The sentence "The Pope also sent troops from Rome to support the Carbonari in the village of Av" appears to be listing a specific location or event, likely a place name or military campaign detail about the rebellion\'s advance.'
- cos orig 0.94213; alternatives: Singapore 0.94268, First 0.94408, Aggi 0.94216, Beirut 0.94232, Nip 0.94182, UK 0.94275, Having 0.94214
- rank 7, gap -0.00043

#### row 307 (stim 89, claim 0/3, entity, word_orig 'New')

- prefix tail (last 400 chars): 'to floriculture , it is rarely cultivated . \n \n = = Description = = \n \n Banksia violacea grows as a shrub up to 1 @.@ 5 m ( 5 ft ) tall , with narrow leaves 1 – 2 cm ( 0 @.@ 4 – 0 @.@ 8 in ) long and about 0 @.@ 15 cm ( 0 @.@ 06 in ) wide . New growth occurs in summer , and flowering ranges from November to April with a peak in February , but can be irregular in timing . Flowers arise from typical'
- claim: 'Australian botanical/field guide format with structured species description, detailing a rare New Zealand orchid species with botanical characteristics and habitat.'
- cos orig 0.89168; alternatives: Korea 0.88993, Nip 0.89197, He 0.89184, Haji 0.89195, Los 0.89171, David 0.89168, Additionally 0.89185
- rank 6, gap 0.00012

#### row 565 (stim 167, claim 1/3, entity, word_orig '"The')

- prefix tail (last 400 chars): 'outh and southwest through wetlands and passes through two small lakes , Tumtum and Mica . It has sections of rapids and whitewater , and flows over cataracts below Tumtum Lake . Its flow drops by 5 metres ( 16 ft ) per kilometre in certain sections . After travelling for 94 kilometres ( 58 mi ) and entering the Shuswap Highland , it enters the northern end of Adams Lake . \n Adams Lake is roughly '
- claim: 'The sentence structure "The Long Lake is a long narrow lake north of the town, with a length of" continues a distance/dimension fact about the Lake of Two Hills, likely providing another geographic measurement or feature detail about the lake.'
- cos orig 0.91094; alternatives: Royal 0.91065, Background 0.90857, Known 0.90952, 1930s 0.91104, Song 0.91112, Bal 0.91146, Unlike 0.91122
- rank 5, gap 0.00043


- review sheets: k1_review_blind.csv (20 rows, seed 0) — open first; k1_review_key.csv after

---

# D1 — claim-direction ablation (desk-designed)

## D1 summary — claim-direction ablation with the reconstructor as encoder (greedy, α = 0.3)

git 0cb31fef; settings in d1_settings.json; progress in d1_progress.json

### Kill test

- 2026-09-09T10:32:24  D1  D1  threshold=CI95 (cluster by explanation) of [persist_word(random) − persist_word(own)] on non-last rows (n ≤ 120) ≤ 0 → MET; > 0 → NOT MET; straddles or < 60 rows completed → INCONCLUSIVE  observed=non-last pooled: n=91 persist_word own 0.495 random 0.703 diff 0.2088 [0.1111,0.3111] n=91 k=73; persist_claim own 0.236 random 0.345 diff 0.1094 [0.0806,0.1378] n=91 k=73; format-break own 0.000 random 0.000; nonlast_in_prefix: n=46 persist_word own 0.696 random 0.848 diff 0.1522 [0.0217,0.2889] n=46 k=41; persist_claim own 0.258 random 0.354 diff 0.0956 [0.0478,0.1377] n=46 k=41; format-break own 0.000 random 0.000; nonlast_not_in_prefix: n=45 persist_word own 0.289 random 0.556 diff 0.2667 [0.1304,0.4222] n=45 k=43; persist_claim own 0.213 random 0.337 diff 0.1234 [0.0885,0.1636] n=45 k=43; format-break own 0.000 random 0.000; positive_control_last: n=20 persist_word own 0.550 random 0.800 diff 0.2500 [0.0500,0.4500] n=20 k=20; persist_claim own 0.409 random 0.514 diff 0.1052 [0.0633,0.1526] n=20 k=20; format-break own 0.000 random 0.000; positive control quoted_token_ok own 0.800 random 0.900 reference 0.850; rows completed 111/140  NOT MET  concerns the AV's output under a vector edit only; MET/INCONCLUSIVE with the positive control NOT MET = the AV re-asserts from remaining content or the AR direction is not what the AV reads

### Format-break rate first

- own: parse_ok 1.000, cjk 0.000, format-break 0.000; random: parse_ok 1.000, cjk 0.000, format-break 0.000 (n=111)
- rows sampled 140 ({"nonlast_in_prefix": 60, "nonlast_not_in_prefix": 60, "positive_control_last": 20}); completed 111; reference persist_word 1.000; reference quoted_token_ok on last rows 0.850

### Per stratum (paired random − own, cluster by explanation)

| stratum | n | n_expl | measure | own | random | random − own | CI lo | CI hi |
|---|---|---|---|---|---|---|---|---|
| non-last pooled | 91 | 73 | persist_word | 0.4945 | 0.7033 | 0.2088 | 0.1111 | 0.3111 |
| non-last pooled | 91 | 73 | persist_claim | 0.2360 | 0.3454 | 0.1094 | 0.0806 | 0.1378 |
| non-last pooled | 91 | 73 | jaccard_expl | 0.4121 | 0.4384 | 0.0263 | 0.0114 | 0.0420 |
| non-last pooled | 91 | 73 | format_break | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| non-last pooled | 91 | 73 | quoted_token_ok | 0.6593 | 0.7143 | 0.0549 | -0.0430 | 0.1478 |
| non-last pooled | 91 | 73 | cos_h_AR_new | 0.8557 | 0.8731 | 0.0173 | 0.0126 | 0.0223 |
| nonlast_in_prefix | 46 | 41 | persist_word | 0.6957 | 0.8478 | 0.1522 | 0.0217 | 0.2889 |
| nonlast_in_prefix | 46 | 41 | persist_claim | 0.2583 | 0.3539 | 0.0956 | 0.0478 | 0.1377 |
| nonlast_in_prefix | 46 | 41 | jaccard_expl | 0.4377 | 0.4634 | 0.0258 | -0.0000 | 0.0497 |
| nonlast_in_prefix | 46 | 41 | format_break | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| nonlast_in_prefix | 46 | 41 | quoted_token_ok | 0.6957 | 0.7391 | 0.0435 | -0.0833 | 0.1778 |
| nonlast_in_prefix | 46 | 41 | cos_h_AR_new | 0.8553 | 0.8704 | 0.0152 | 0.0105 | 0.0200 |
| nonlast_not_in_prefix | 45 | 43 | persist_word | 0.2889 | 0.5556 | 0.2667 | 0.1304 | 0.4222 |
| nonlast_not_in_prefix | 45 | 43 | persist_claim | 0.2132 | 0.3367 | 0.1234 | 0.0885 | 0.1636 |
| nonlast_not_in_prefix | 45 | 43 | jaccard_expl | 0.3860 | 0.4129 | 0.0269 | 0.0035 | 0.0535 |
| nonlast_not_in_prefix | 45 | 43 | format_break | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| nonlast_not_in_prefix | 45 | 43 | quoted_token_ok | 0.6222 | 0.6889 | 0.0667 | -0.0465 | 0.1957 |
| nonlast_not_in_prefix | 45 | 43 | cos_h_AR_new | 0.8561 | 0.8757 | 0.0196 | 0.0105 | 0.0287 |
| positive_control_last | 20 | 20 | persist_word | 0.5500 | 0.8000 | 0.2500 | 0.0500 | 0.4500 |
| positive_control_last | 20 | 20 | persist_claim | 0.4092 | 0.5144 | 0.1052 | 0.0633 | 0.1526 |
| positive_control_last | 20 | 20 | jaccard_expl | 0.4733 | 0.5198 | 0.0464 | 0.0106 | 0.0817 |
| positive_control_last | 20 | 20 | format_break | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| positive_control_last | 20 | 20 | quoted_token_ok | 0.8000 | 0.9000 | 0.1000 | 0.0000 | 0.2500 |
| positive_control_last | 20 | 20 | cos_h_AR_new | 0.8573 | 0.8816 | 0.0243 | 0.0098 | 0.0395 |

### 2×2 (non-last rows): in_full_prefix × slot type — persist_word own / random / diff

| in_full_prefix \ slot type | entity | detail |
|---|---|---|
| True | n=43 own 0.721 random 0.837 diff 0.116 [-0.001,0.245] | n=3 own 0.333 random 1.000 diff 0.667 [0.000,1.000] |
| False | n=36 own 0.333 random 0.611 diff 0.278 [0.111,0.459] | n=9 own 0.111 random 0.333 diff 0.222 [0.000,0.556] |

Distributions for the four cells (persist_claim, own):

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own_persist_claim / in_full_prefix=True × entity | 43 | 0.25984 | 0.11437 | 0.01308 | 0.06061 | 0.10026 | 0.14929 | 0.17845 | 0.24528 | 0.31455 | 0.42291 | 0.45938 | 0.57143 |
| own_persist_claim / in_full_prefix=True × detail | 3 | 0.23599 | 0.03508 | 0.00123 | 0.19608 | 0.20147 | 0.20686 | 0.22304 | 0.25000 | 0.25595 | 0.25952 | 0.26071 | 0.26190 |
| own_persist_claim / in_full_prefix=False × entity | 36 | 0.21783 | 0.08000 | 0.00640 | 0.09091 | 0.11429 | 0.13007 | 0.15977 | 0.21183 | 0.25751 | 0.34368 | 0.37728 | 0.40625 |
| own_persist_claim / in_full_prefix=False × detail | 9 | 0.19484 | 0.06730 | 0.00453 | 0.10811 | 0.12340 | 0.13869 | 0.14815 | 0.17857 | 0.23404 | 0.26179 | 0.29756 | 0.33333 |

### Distributions

| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d_norm / non-last pooled | 91 | 33.44240 | 11.10868 | 123.40271 | 14.90067 | 19.08588 | 21.34982 | 25.14508 | 31.38351 | 39.81971 | 47.26921 | 55.30202 | 66.26895 |
| d_norm / positive_control_last | 20 | 81.53428 | 37.63503 | 1416.39581 | 31.38025 | 33.91020 | 34.15886 | 48.29564 | 76.72074 | 119.05678 | 130.01560 | 131.02660 | 135.88661 |
| proj / non-last pooled | 91 | 0.20158 | 0.10405 | 0.01083 | -0.03636 | 0.04206 | 0.06062 | 0.13590 | 0.20284 | 0.26615 | 0.32856 | 0.37828 | 0.48685 |
| proj / positive_control_last | 20 | 0.44616 | 0.09752 | 0.00951 | 0.23624 | 0.29744 | 0.30674 | 0.38776 | 0.46842 | 0.51718 | 0.54501 | 0.56234 | 0.57594 |
| cos_dhat_hhat / non-last pooled | 91 | 0.20158 | 0.10405 | 0.01083 | -0.03636 | 0.04206 | 0.06062 | 0.13590 | 0.20284 | 0.26615 | 0.32856 | 0.37828 | 0.48685 |
| cos_dhat_hhat / positive_control_last | 20 | 0.44616 | 0.09752 | 0.00951 | 0.23624 | 0.29744 | 0.30674 | 0.38776 | 0.46842 | 0.51718 | 0.54501 | 0.56234 | 0.57594 |
| own_cos_hprime_h / non-last pooled | 91 | 0.95488 | 0.00104 | 0.00000 | 0.95394 | 0.95396 | 0.95398 | 0.95408 | 0.95443 | 0.95520 | 0.95650 | 0.95688 | 0.95873 |
| own_cos_hprime_h / positive_control_last | 20 | 0.95577 | 0.00151 | 0.00000 | 0.95394 | 0.95394 | 0.95395 | 0.95438 | 0.95559 | 0.95679 | 0.95765 | 0.95824 | 0.95875 |
| random_cos_hprime_h / non-last pooled | 91 | 0.95735 | 0.00170 | 0.00000 | 0.95430 | 0.95490 | 0.95521 | 0.95607 | 0.95730 | 0.95858 | 0.95960 | 0.96030 | 0.96148 |
| random_cos_hprime_h / positive_control_last | 20 | 0.95732 | 0.00159 | 0.00000 | 0.95535 | 0.95557 | 0.95565 | 0.95628 | 0.95678 | 0.95812 | 0.95943 | 0.96044 | 0.96095 |
| own_cos_h_AR_new / non-last pooled | 91 | 0.85571 | 0.04476 | 0.00200 | 0.74309 | 0.76081 | 0.79352 | 0.83188 | 0.86328 | 0.88643 | 0.90794 | 0.91893 | 0.93621 |
| own_cos_h_AR_new / positive_control_last | 20 | 0.85729 | 0.07260 | 0.00527 | 0.63430 | 0.76119 | 0.77384 | 0.83235 | 0.87323 | 0.90146 | 0.93090 | 0.93423 | 0.94505 |
| random_cos_h_AR_new / non-last pooled | 91 | 0.87305 | 0.04264 | 0.00182 | 0.76988 | 0.80020 | 0.81044 | 0.84617 | 0.87864 | 0.90351 | 0.92399 | 0.93094 | 0.96220 |
| random_cos_h_AR_new / positive_control_last | 20 | 0.88160 | 0.04827 | 0.00233 | 0.72351 | 0.82780 | 0.83936 | 0.86677 | 0.88387 | 0.90887 | 0.93161 | 0.93548 | 0.94507 |
| cos_z / non-last pooled | 91 | 0.88598 | 0.03732 | 0.00139 | 0.79396 | 0.81553 | 0.81937 | 0.86742 | 0.89298 | 0.91407 | 0.93281 | 0.93484 | 0.96217 |
| cos_z / positive_control_last | 20 | 0.88121 | 0.05800 | 0.00336 | 0.67928 | 0.80263 | 0.83083 | 0.86701 | 0.89353 | 0.90833 | 0.92687 | 0.93642 | 0.95333 |
| cos_zc / non-last pooled | 91 | 0.86947 | 0.04690 | 0.00220 | 0.73690 | 0.77385 | 0.79929 | 0.84294 | 0.88231 | 0.90331 | 0.92047 | 0.92645 | 0.93946 |
| cos_zc / positive_control_last | 20 | 0.74910 | 0.13788 | 0.01901 | 0.40090 | 0.50478 | 0.56564 | 0.67868 | 0.78218 | 0.86145 | 0.88677 | 0.90027 | 0.91705 |
| own_persist_claim / non-last pooled | 91 | 0.23601 | 0.09796 | 0.00960 | 0.06061 | 0.10128 | 0.13514 | 0.16667 | 0.22581 | 0.27555 | 0.35556 | 0.42265 | 0.57143 |
| own_persist_claim / positive_control_last | 20 | 0.40919 | 0.09337 | 0.00872 | 0.28571 | 0.30216 | 0.30352 | 0.35556 | 0.38068 | 0.43779 | 0.56722 | 0.59578 | 0.60606 |
| random_persist_claim / non-last pooled | 91 | 0.34539 | 0.12520 | 0.01567 | 0.12500 | 0.15576 | 0.19565 | 0.26970 | 0.33333 | 0.40408 | 0.53659 | 0.55778 | 0.70833 |
| random_persist_claim / positive_control_last | 20 | 0.51440 | 0.09971 | 0.00994 | 0.38636 | 0.39490 | 0.39614 | 0.44599 | 0.48174 | 0.58421 | 0.67625 | 0.68801 | 0.69767 |
| own_jaccard_expl / non-last pooled | 91 | 0.41211 | 0.07429 | 0.00552 | 0.23478 | 0.28792 | 0.33654 | 0.36205 | 0.41250 | 0.46241 | 0.49412 | 0.52670 | 0.67105 |
| own_jaccard_expl / positive_control_last | 20 | 0.47334 | 0.06439 | 0.00415 | 0.37113 | 0.37590 | 0.37623 | 0.43654 | 0.47512 | 0.52396 | 0.55228 | 0.56197 | 0.57609 |
| random_jaccard_expl / non-last pooled | 91 | 0.43844 | 0.07627 | 0.00582 | 0.22105 | 0.30275 | 0.34694 | 0.39464 | 0.44000 | 0.48822 | 0.54217 | 0.55397 | 0.64634 |
| random_jaccard_expl / positive_control_last | 20 | 0.51978 | 0.10819 | 0.01170 | 0.35714 | 0.37936 | 0.38905 | 0.43995 | 0.49096 | 0.60868 | 0.65806 | 0.66661 | 0.73913 |

### 5 fixed verbatim examples (seed 0; completed non-last rows)

#### row 380 (stim 110, nonlast_in_prefix, entity, word_orig '"Proteins')

- claim: 'The phrase "Proteins can undergo modification, folding, regulation, activity" is mid-listing a series of attributes of enzymes or proteins, following a familiar compound noun pattern from biology definitions about protein characteristics.'
- original explanation: 'Wikipedia article structure with formal definition format, listing biological terms ("Protein") with a standardized encyclopedia pattern describing protein\'s properties and functions.\n\nThe phrase "Proteins can undergo modification, folding, regulation, activity" is mid-listing a series of attributes of enzymes or proteins, following a familiar compound noun pattern from biology definitions about protein characteristics.\n\nFinal token "activity" ends an incomplete list ("the structure, activity, activity"), part of a comma-separated enumeration of attributes ("such as its structure, function, activity, activity..."), strongly expecting continuation like "or lifespan," "of the protein," or "and other properties," completing the compound noun phrase.'
- own ablation (‖d_c‖ 34.714, proj 0.2028, cos(h',h) 0.9544): persist_word 1.0, persist_claim 0.227: 'Wikipedia article structure with formal definition format, listing biological definitions of proteins using a standardized template ("In biology, a protein is...").\n\nThe phrase "A protein\'s characteristics include its chemical structure, function, location, stability, activity" follows a list of attributes of a protein, completing a standard definition clause about a protein\'s properties or role.\n\nFinal token "activity" ends mid-list within "its activity, activity, activity" — part of a comma-separated enumeration of attributes ("such as its structure, function, activity, activity"), strongly expecting "or other properties" or "and other properties," or "of the protein, or its function" to close.'
- random ablation (partner row 596, cos(h',h) 0.9613): persist_word 0.0, persist_claim 0.279: 'Structured Wikipedia-style article format with numbered definitions and scientific context, following a pattern of chemical terms with "Protein" definition expanding into biological functions.\n\nThe phrase "Protein folding refers to the process of converting a protein\'s structure, function, activity" is mid-listing a series of attributes ("such as shape, stability, activity"), implying continuation of a comma-separated list of protein characteristics.\n\nFinal token "activity" ends an incomplete list item ("activity, activity"), part of a parallel noun series ("such as its structure, function, activity, activity"), strongly expecting continuation like "or other properties," "of the protein," or "and other properties, and its role."'

#### row 408 (stim 119, nonlast_not_in_prefix, entity, word_orig 'Beirut,')

- claim: 'The phrase "known officially as Beirut, locally" suggests a compound noun or nickname phrase ("known locally"), implying a second name or designation follows, likely describing the city\'s status or nickname, completing a phrase about the municipality\'s identity.'
- original explanation: 'Formal Wikipedia-style article structure with English-language descriptive prose about a Palestinian city, establishing factual context about Beirut, Lebanon\'s capital.\n\nThe phrase "known officially as Beirut, locally" suggests a compound noun or nickname phrase ("known locally"), implying a second name or designation follows, likely describing the city\'s status or nickname, completing a phrase about the municipality\'s identity.\n\nFinal token "locally" ends an incomplete phrase ("known locally"), part of a list or descriptive clause ("Known locally..."), strongly expecting "as Beirût" or "as the \'City of Beirut\'" or "and colloquially as" or "as a municipality," continuing the naming context.'
- own ablation (‖d_c‖ 29.418, proj 0.3084, cos(h',h) 0.9539): persist_word 0.0, persist_claim 0.279: 'Wikipedia article format with structured encyclopedia entry on Bahrain, describing a country\'s capital city, with formal descriptive prose about the city\'s geography and history.\n\nThe phrase "Known officially as Manama, the city is locally known" signals a list of aliases or local names, following a common pattern of "locally known as" or "as the capital," likely continuing with demographic context.\n\nFinal token "locally" ends mid-phrase ("Known locally"), part of a noun phrase describing the city\'s name and nickname ("Known locally"), immediately expecting "as Manama" or "in Arabic as \'al-Manama\'" or "as a city, it is known for...".'
- random ablation (partner row 392, cos(h',h) 0.9589): persist_word 0.0, persist_claim 0.361: 'Formal Wikipedia-style entry structure with English language description of a country, implying a noun phrase about "Cairo" or a Palestinian territory.\n\nThe phrase "officially known as the Gaza Strip, locally known locally" suggests a list or phrase completing a compound noun or descriptor, strongly implying "as Gaza City" or "also known as" or "by its residents."\n\nFinal token "locally" ends an incomplete phrase ("known locally"), part of a noun phrase listing attributes ("Known formally as Gaza Strip and locally"), strongly expecting "as" or "as the city" or "and commonly referred to as" or "as a \'local\' name," completing the regional identity context.'

#### row 229 (stim 67, nonlast_in_prefix, entity, word_orig '"Its')

- claim: 'The sentence structure "Its taxonomic classification includes multiple names and definitions, with the species being named after the genus \'Lithobates\' and related terms.'
- original explanation: 'Wiki article format with structured taxonomic entries describing a biological species, listing scientific names and historical classifications with chronological progression.\n\nThe sentence structure "Its taxonomic classification includes multiple names and definitions, with the species being named after the genus \'Lithobates\' and related terms. Its taxonomic history dates back..." implies a second clause continuing the taxonomic history or synonym list.\n\nFinal token "1" is mid-number in "it does not publish multiple taxonomic names or classifications... This taxon\'s taxonomic history begins with the following classification..." — expects "s" or " The following is..." or "s the name has been reclassified" completing the enumeration.'
- own ablation (‖d_c‖ 25.449, proj 0.1363, cos(h',h) 0.9552): persist_word 1.0, persist_claim 0.167: 'Taxonomic species page format with structured biological data fields (Latin name, synonyms, etymology, classification), suggesting a phylogenetic history section follows.\n\nThe phrase "Its taxonomic history includes the following classifications : ... The genus was first described in 1855" implies a list continuation or chronological revision history, with "Other taxonomic synonyms" signaling a second taxonomic revision.\n\nFinal token "1" is mid-number in "it does not publish the following taxonomic revisions : " — part of a closing taxonomic revision clause, strongly expecting "s" or "... The following classification" or "s, including..." completing the historical taxonomic lineage.'
- random ablation (partner row 665, cos(h',h) 0.9615): persist_word 1.0, persist_claim 0.560: 'Structured taxonomic entry format with numbered definitions and etymology sections describing a biological species, listing scientific names and taxonomic history.\n\nThe sentence "Its taxonomic classification includes multiple names and classifications, with the species being assigned to the genus *Lithobates* and related genera. Its evolutionary history is traced..." implies a concluding clause about taxonomic relationships or synonymy, completing the enumeration.\n\nFinal token "2016." closes a parenthetical clause ("Its taxonomic name history dates from... The following taxonomic classification... This species has multiple definitions..."), strongly expecting "s the following" or "...the name has been..." or "s other related classifications."'

#### row 234 (stim 68, nonlast_in_prefix, entity, word_orig '"The')

- claim: 'The phrase "The Aggie Marching Band\'s roar was heard as \'Hail Aggi" suggests a proper noun or nickname ("The Aggie Spirit"), likely referencing the university\'s mascot or a specific event name with a historical figure.'
- original explanation: 'Historical sports reference format with a college football tradition, establishing a factual description of Texas A&M\'s fight song and cheer.\n\nThe phrase "The Aggie Marching Band\'s roar was heard as \'Hail Aggi" suggests a proper noun or nickname ("The Aggie Spirit"), likely referencing the university\'s mascot or a specific event name with a historical figure.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of a quoted nickname ("The Spirit of Aggi"), strongly expecting "wick" or "wickville" to complete the compound noun, likely continuing with "Eagle" or "Eagle Pride," referencing the alma mater.'
- own ablation (‖d_c‖ 27.494, proj 0.0606, cos(h',h) 0.9565): persist_word 1.0, persist_claim 0.238: 'Historical sports article format with Wikipedia-style structure, describing Texas A&M\'s fight song and traditions, establishing a factual tone with trivia about the Aggie band.\n\nThe phrase "The fight song of Texas A&M University is known as the \'Aggie Fight Song,\' and the winner of the game earns the Aggi" is a familiar closing phrase referencing the university\'s mascot name.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of the phrase "The spirit of Aggieland," completing a traditional nickname or honorific title, strongly expecting "eland" or "Eagle" to close the compound noun describing the student body\'s victory.'
- random ablation (partner row 522, cos(h',h) 0.9559): persist_word 1.0, persist_claim 0.326: 'Historical sports event format with official Texas A&M University description, listing traditions and facts about the Aggie Fight Song.\n\nThe phrase "And the cheers of the Aggies fill the stadium, with the Aggieland fight song ringing out as \'Hail Texas\'" suggests a closing phrase referencing the Aggie mascot or a specific honorific term, likely "Aggieland" or a mascot name.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of a compound noun ("The flame of Aggi"), strongly expecting "eland" or "Eagle" or "Eagle Pride," completing the traditional honorific phrase about the team\'s spirit.'

#### row 476 (stim 140, nonlast_in_prefix, detail, word_orig '25"')

- claim: 'The phrase "The fifth novel of Stephen King , his 25" strongly implies a numbered list or record of his works, with "25th novel" suggesting a milestone or ranking number for his career.'
- original explanation: 'Wiki article format with descriptive prose about a novel, establishing a book title and author context.\n\nThe phrase "The fifth novel of Stephen King , his 25" strongly implies a numbered list or record of his works, with "25th novel" suggesting a milestone or ranking number for his career.\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, his 25"), immediately expecting "th novel" or "th work" or "th novel in his series," completing the numerical claim about his record-breaking or numbered literary achievement.'
- own ablation (‖d_c‖ 27.777, proj 0.1931, cos(h',h) 0.9545): persist_word 1.0, persist_claim 0.262: 'Wikipedia article format with biographical prose describing a novel, establishing factual details about Canadian author David Morrell\'s third novel.\n\nThe phrase "It is his 14th novel, which is his 25" mirrors a numbered series claim, suggesting a concluding statistic about his authorship count or career milestone, completing the "first nonfiction work" attribution.\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th book, his 25th work"), strongly expecting "th book" or "th work" to close the number, then likely "th novel" or "th book."'
- random ablation (partner row 623, cos(h',h) 0.9579): persist_word 1.0, persist_claim 0.394: 'Wiki-style or fan fiction format with a title suggesting a book or film, implying a numbered list or descriptive context about a Canadian author\'s novel.\n\nThe phrase "His 25th novel , being his 25" strongly implies a numeric designation or record, likely a numbered series or milestone, completing "his 25th novel" or "a novel about crime."\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, 25"), immediately expecting "th novel" or "th novel in his career" or "th novel" to complete the numeric milestone claim.'


- review sheets: d1_review_blind.csv (20 rows, seed 0; the two new explanations in shuffled order) — open first; d1_review_key.csv after

---

# Round-4 RUNLOG (verbatim)

- 2026-09-09T01:57:48  V0  start  round 4 begins (/loop, dynamic); artifact check + benchmark + pipeline verification + orchestrator throughput (20 tasks) + re-budget; hard stop = 2026-09-09T01:57:48 + 10 h = 2026-09-09T11:57:48; T9 reserve from 2026-09-09T11:27:48
- 2026-09-09T02:07:36  v0  agent-tasks  bench {"rewrite": 10, "label": 5, "equiv": 5} n=20 2.8 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:09:08  V0  agent-tasks  bench: 20 tasks (10 rewrite, 5 label, 5 equiv) in 2.8 min wall-clock from AWAITING (02:04:50) to validation; block append times: rewrites 02:06:50 (incl. reading the file), labels 02:07:02, equivs 02:07:09 — per-type split not separable (all deliberation preceded the first append), so the re-budget uses the uniform measured 0.14 min/task for every type (conservative for equiv-heavy budgets)
- 2026-09-09T02:09:08  V0  checkfix  check (6) implementation flagged a comment and an f-string in v0_check.py (not code); the checker now blanks comments and string literals (incl. FSTRING_* tokens) before matching; no measurement changed; V0 re-run twice on the saved bench (v0_bench.json), no model call repeated
- 2026-09-09T02:09:08  V0  done  18/18 artifact checks OK; pipeline checks (1)–(7) OK (greedy explanations for stimuli 0–4 identical to round 1; own>shifted 10/10; repeat max Δcos 0; dummy edit asserts OK; longest AR input 152 tokens; 0 round-1 generations unclosed; extractor nla_lib.Target snapshot a09a3545; B1 min t=55 ≥ 50, no filler2, 1 pair len_mismatch flagged, token id at t matches within every pair); measured s/call: TARGET 66-tok fwd 0.68 (min 0.24), TARGET 256-tok fwd 0.59, AV sampled-200 10.27, AV greedy-200 9.91, AR score 0.51 (min 0.28); loads T 7 / A 5 / R 4 s; re-budget at 0.14 min/task: cut rules applied A1(a) paraphrases 1+1, A1(b) drop negation, A1(c) contexts 60→40 (A1 still projects 256 min > 210 cap after all three: runs to its cap, partial results reported by n), B1(a) fillings 5→4 (64 contexts, projects 150.0 min = cap), K1 none (26.7 min), D1 none (51.2 min); total projected 484 min; V0 cumulative 5.0 min (cap 30)
- 2026-09-09T02:09:08  B1  start  controlled paired contexts, meanings A/B; cut rule B1(a): fillings f0–f3 → 32 pairs, 64 contexts (dev f0 16 ctx / eval f1–f3 48 ctx, 24 pairs); paraphrases 2+2 (B1(b) not applied); TARGET → AV sampled (seed 5000+2·pair_index+{0,1}) → agent slot_verify → fact_swap → edit_check + slot_verify(swapped) → rewrite → equiv → AR; cap 150 min
- 2026-09-09T02:24:42  b1  agent-tasks  slot_verify {"slot_verify": 8} n=8 0.8 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:26:32  B1  crashfix  b1_analyze.py crashed after the kill line had been appended (no in-primary carrier → missing 'D' column); the analysis now fills absent columns with NaN and does not re-append an existing B1 kill line; the review sheet now also lists the judged candidate sentences (provisional asserts blind); no measurement changed; re-run reused every saved generation, activation and AR prediction (0 new forwards)
- 2026-09-09T02:26:32  B1  done  64 contexts (32 pairs, fillings f0–f3; dev 16 / eval 48), 64 TARGET forwards, 64 sampled AV generations (parse_ok 64/64, cjk 0, 10.3 s), 8 slot_verify tasks (all 'neither'), 0 eligible carriers: omission 64/64 (no non-snippet sentence asserts meaning A or B; 8 sentences merely contain a keyword), 0 fact_swap / rewrite / equiv tasks, 64 AR forwards (carriers only); B1 INCONCLUSIVE (eligible eval carriers 0 < 32; mean D undefined); s(h_own, carrier) mean 0.839 [0.802, 0.875], s(h_other, carrier) 0.837, cos(h_A, h_B) mean 0.993 (min 0.968); t 55–67; cumulative 12.4 min (cap 150); wall 02:12→02:25
- 2026-09-09T02:26:32  A1  start  natural AV claims, paraphrase-averaged preference; cut rules A1(a) light1+aggr1, A1(b) no negation, A1(c) 40 contexts (dev 0–9, eval 10–39); select (rng 4) → TARGET → AV sampled (seed 4000+context_id) → slot_verify → label → correction → corrcheck → corrupt (detail_sub, relation_rev; entity_sub deterministic) → candcheck → label_cand → rewrite → equiv → AR; cap 210 min
- 2026-09-09T02:35:25  a1  agent-tasks  slot_verify {"slot_verify": 56} n=56 1.4 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:38:49  a1  agent-tasks  label_orig {"label": 54} n=54 3.4 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:40:25  a1  agent-tasks  correction {"correction": 46} n=46 1.6 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:42:44  a1  agent-tasks  corrcheck {"edit_check": 27, "label": 27} n=54 2.3 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:44:35  a1  agent-tasks  corrupt {"detail_sub": 47, "relation_rev": 47} n=94 1.9 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:46:05  a1  agent-tasks  candcheck {"edit_check": 87} n=87 1.5 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:47:05  a1  agent-tasks  label_cand {"label": 70} n=70 1.0 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:50:54  a1  agent-tasks  rewrite {"rewrite": 124} n=124 3.8 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:51:48  a1  agent-tasks  equiv {"equiv": 248} n=248 0.9 min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs=0
- 2026-09-09T02:54:55  A1  crashfix  a1_analyze.py crashed after both kill lines had been appended (pandas: 'Pe.transform' resolved to the DataFrame method, not the column); fixed to Pe["transform"] in a1_analyze.py and b1_analyze.py, and a1_analyze.py no longer re-appends an existing A1 / A1-nat kill line; no measurement changed; re-run reused every saved generation, activation and AR prediction (0 new forwards)
- 2026-09-09T02:54:55  A1  done  40 contexts (dev 10 / eval 30; 410 candidate docs, rng 4, 0 skipped), 40 TARGET forwards, 40 sampled AV generations (parse_ok 40, cjk 5, 10.3 s), 54 rule-located slots (37 entity, 17 detail; 3 contexts without a slot); agent tasks: slot_verify 56, label 54, correction 46, corrcheck 54, corrupt 94, edit_check 87, label_cand 70, rewrite 124, equiv 248 (833 tasks, 17.8 min judgement); label_orig contradicted 51 / entailed 2 / undetermined 1; eligible 47; valid corrections 7/46 (19 NONE, 16 edit_check No, 4 label not entailed); candidates 218 (false in play 69, edit rejected 17, NONE 28, duplicate 10); paraphrases 248 (equiv Yes 248), 459 AR forwards; A1 INCONCLUSIVE (in-primary eval slots 4 < 30; mean G 0.00319 [-0.00035,0.00674]); A1-nat INCONCLUSIVE (natural-error eval slots 4 < 15; 0.00113 [-0.00176,0.00465]); cumulative 27.0 min (cap 210); wall 02:26→02:54
- 2026-09-09T02:54:55  K1  start  K-way alternative ranking on 393 deterministic-swap claims (AR only): 7 alternatives per row (seed 6000+row), 8 texts per row against the row's h; strata non-last in-prefix 107 / not-in-prefix 159 / last 127; cap 45 min
- 2026-09-09T03:08:52  K1  crashfix  k1_kway.py crashed in the statistics after all 393 rows were scored (k1_rows.csv had been appended with two column sets: detail rows lack pool_size, so the CSV was misaligned); the writer now uses a fixed column order and rows.csv is rebuilt deterministically from the saved per-row scores in k1_texts.jsonl (no AR forward repeated); no measurement changed
- 2026-09-09T03:08:52  K1  done  393 rows (107 non-last in-prefix / 159 non-last not-in-prefix / 127 last), 2,751 AR forwards (0.27 s), 0 errors, pool_short 6; original cos reused from s2 (max |dev| 1.1e-16 on 20 rows); K1 NOT MET (non-last in-prefix top-1 0.308, top1−0.125 = 0.183 [0.096,0.265], MRR 0.487, gap 0.00125 [0.00058,0.00202]); not-in-prefix top-1 0.252 (0.127 [0.061,0.190]), gap 0.00044 [0.00000,0.00086]; positive control (last) top-1 0.449 (0.324 [0.237,0.410]), gap 0.0108 [0.0073,0.0146]; cumulative 12.8 min (cap 45); wall 02:55→03:09
- 2026-09-09T09:32:00  K1  note  the loop's fallback wakeup did not fire until 09:31 (scheduled 03:26); no stage ran between 03:09 and 09:31; remaining window to the T9 reserve (11:27:48) is 116 min
- 2026-09-09T09:32:00  D1  start  claim-direction ablation with the AR as encoder: 140 rows (60 in-prefix / 60 not-in-prefix / 20 last; seed 8000; derangement 8001), AR directions → AV+AR greedy re-verbalization of h − 0.3‖h‖ d̂ (own vs random), 280 generations; cap 60 min
- 2026-09-09T10:32:24  D1  done  cap reached (60.2 min ≥ 60): 111/140 rows completed (46 in-prefix / 45 not-in-prefix / 20 last; 29 rows incomplete, listed in d1_progress.json), 140 AR direction pairs, 222 greedy AV generations (10.3 s early, slowed to ~70 s per generation between 09:57 and 10:21 while two unrelated 97 %-CPU python jobs from another project ran), 0 errors, format-break 0/222; D1 NOT MET (non-last pooled persist_word own 0.495 vs random 0.703, random − own 0.209 [0.111,0.311] n=91 k=73; persist_claim diff 0.109 [0.081,0.138]; in-prefix 0.152 [0.022,0.289], not-in-prefix 0.267 [0.130,0.422]; positive control persist_word diff 0.250 [0.050,0.450], quoted_token_ok own 0.80 random 0.90 reference 0.85); wall 09:31→10:32
- 2026-09-09T10:33:08  T9  start  MORNING4.md from the stage summaries (D1 partial by cap); T9 reserve 11:27:48, hard stop 11:57:48

# FOLLOWUPS (verbatim, whole file)

# FOLLOWUPS — ideas queued by the bench for the human. One line each. Nothing here is acted on overnight.
- S3 statistic A_i = Δ_i(z*) − Δ_i(z) equals cos(z) − cos(z*) by construction (z* minus c_i* is the same text as z minus c_i), so the primary and the first secondary statistic coincide; both are reported as pre-registered.
- Stage scripts create their Settings file at module import; importing one stage from another (S3 imports S2's splitter) or re-running with --summary overwrites the finished stage's settings JSON. Move Settings creation under main() next round.
- X3 judge: the TARGET judged only 32/211 original claims 'supported' and 1/211 corruptions 'contradicting' the prefix (most S3 claims describe format/expectation rather than checkable facts), so the pre-registered judge-valid subset is n=1; a claim-type filter or a different judge prompt would be needed for a usable validity subset.
- M: on the raw-text prompt (no chat template) 147/200 multiplication generations ran to the 200-token cap without writing 'Answer:', leaving 4 incorrect items with a position; a chat-template prompt or a larger token budget would be needed for a usable incorrect sample (not changed overnight: pre-registered).
- B1: at the pre-registered position (final '.' of 'The record ends here.', t 55–67) every sampled AV explanation described the closing sentence / record format and none asserted the varied fact (omission 64/64; 8 keyword mentions, 0 assertions); the human may want a fact-bearing position (e.g. the final token of the fact sentence) or an insertion arm before B1 is re-run — not changed overnight (pre-registered: one position, no insertion arm).
- A1: 51 of 54 rule-located AV sentences were contradicted by their own prefix (entity and detail slots alike) and only 7 of 46 single-fact corrections yielded an entailed sentence (most sentences carry two or more wrong facts), so the primary reached 4 eligible eval slots; a design that admits multi-fact corrections, or selects slots by an entailed-first rule, would be needed for n ≥ 30 — not changed overnight (pre-registered).
- A1 entity_sub pool: the pre-registered pool (word_orig of the round-1 deterministic name swaps) contains non-name capitalised tokens ("When", "Is", "Unlike", "Two"…); 14 of 31 swaps were rejected at edit_check for that reason. A name-only pool (e.g. capitalised tokens not in a stoplist of function words) would raise the entity_sub yield.

# Provenance

- Human-designed (2026-09-09, revised after advisor review): A1 and B1 — design, hypotheses, edit suite, statistics, seed pairs, success criteria, cut rules, the agent-judgement protocol and the review-pack schema (PLAN.md round-4 section).
- Desk-designed (2026-09-08, accepted by the human 2026-09-09 with limited claims): K1 and D1.
- Agent-built overnight (this session, Claude Fable 5.1): r4_lib.py, v0_check.py, b1_pairs.py / b1_analyze.py, a1_natural.py / a1_analyze.py, k1_kway.py, d1_ablate.py, t9_morning.py; every editor / judge label (label_source=claude, provisional) in the *_agent_outputs_*.jsonl files.
- Agent choices inside the pre-registration (logged in RUNLOG / settings): V0 re-budget used the uniform measured 0.14 min/task rate for every task type (per-type blocks not separable in the 20-task sample); B1 keyword sets and F2/F4 stem lists as in r4_lib.b1_pairs; B1 'same' meaning is stored under category correct_original with its truth label; A1 entity_sub pool = t2b corrupt_det name cores; A1 repeated-fact check via a second slot_verify task; K1/D1 as in their settings files; crash fixes listed in RUNLOG (none changed a measurement).
- Not done, by design: no insertion arm, no second position, no second intervention strength, no French, no threshold or item-count change beyond the pre-declared V0 cut rules.

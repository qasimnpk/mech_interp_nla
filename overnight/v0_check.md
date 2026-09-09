# V0 check — artifacts, benchmark, pipeline verification, orchestrator throughput, re-budget (round 4)

git ce597b2b; settings in v0_settings.json; bench in v0_bench.json; generations in v0_av.jsonl; tasks v0_agent_tasks_bench.jsonl / outputs v0_agent_outputs_bench.jsonl

## Artifact checks

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

## Measured costs (5 calls each; mean / min / max seconds; MPS synchronised; first call includes warm-up)

| call type | mean s | min s | max s | note |
|---|---|---|---|---|
| target_ctx_forward_hidden | 0.675 | 0.237 | 2.365 | {"tokens": 66} |
| target_256_forward_hidden | 0.594 | 0.585 | 0.617 | {"tokens": 256} |
| av_sampled_200 | 10.270 | 9.747 | 11.732 | {"n_tokens": [144, 141, 146, 144, 141], "parse_ok": [true, true, true, true, true], "ended_with_close_tag": [true, true, true, true, true], "ended_with_eos": [true, true, true, true, true]} |
| av_greedy_200 | 9.906 | 9.634 | 10.035 | {"n_tokens": [145, 143, 146, 145, 140], "parse_ok": [true, true, true, true, true], "ended_with_close_tag": [true, true, true, true, true], "ended_with_eos": [true, true, true, true, true]} |
| ar_score | 0.505 | 0.279 | 1.274 | {} |

- model loads: TARGET 7 s, AV 5 s, AR 4 s; RSS after TARGET free 0.5 G, after AV free 0.6 G
- block-20 activation of stimulus 0 recomputed from the 512-token document vs acts_L20: 1−cos = -2.22e-16

## Pipeline verification (dev items only)

| check | result | pass |
|---|---|---|
| (1) stimuli 0 and 1 give different greedy explanations | different=True; greedy equals round-1 explanation for stimuli 0–4: [True, True, True, True, True] | OK |
| (2) s(h_i, z_i) > s(h_i, z_(i+5) mod 10), stimuli 0–9 | 10/10 | OK |
| (3) z_0 scored five times: max Δcos | 0.00e+00 | OK |
| (4) dummy edited text passes the prefix/suffix asserts | stim 0 sentence span [175, 420] dup=False | OK |
| (5) longest round-1 explanation in the AR template | stim 184: ar_input_tokens=152 (<1024); round-1 generations ending with neither </explanation> nor EOS: 0 [] | OK |
| (6) extractor = nla_lib.Target (Qwen/Qwen2.5-7B-Instruct, snapshot a09a35458c702b33eeacc393d103063234e8bc28); AV.model( calls outside verbalize* | scanned ['r4_lib.py', 'v0_check.py']; hits {} | OK |
| (7) B1 position check: all 80 contexts t ≥ 50 | min t=55; filler2 applied=False; len_mismatch pairs=1; final token '.' everywhere=True; token id at t matches within every pair=True | OK |

## Orchestrator throughput (20-task sample: 10 rewrite, 5 label, 5 equiv; outputs used for nothing else)

- wall-clock between AWAITING and validation: 2.8 min for 20 tasks
- per-task minutes used for the re-budget (total awaiting minutes / 20 tasks (no per-type timing given)): rewrite 0.14, label 0.14, equiv 0.14
- assumed rates for unmeasured types: slot_verify and edit_check at the measured label rate; fact_swap / detail_sub / relation_rev / negation / correction at max(label, 0.5 x rewrite)

## Re-budget (measured costs × PLAN call counts + judgement minutes; cut rules applied in the pre-declared order until the projection fits the cap)

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

### Cut rules applied

- A1(a) paraphrases 2+2 -> 1+1 (light1, aggr1)
- A1(b) drop the negation candidate
- A1(c) contexts 60 -> 40 (dev 10 stays; eval 50 -> 30 by selection order)
- B1(a) fillings per template 5 -> 4 (drop f4): 64 contexts

- total projected 484 min for B1 + A1 + K1 + D1 (hard stop 10 h = 600 min from the first round-4 RUNLOG line; T9 reserve 30 min)
- projection assumptions: {"b1_slot_verify_per_context": 2.0, "a1_slots_per_context": 2.0, "a1_slot_verify_per_slot": 1.5, "a1_contradicted_fraction": 0.3, "a1_entity_slot_fraction": 0.5}
- V0 cumulative minutes (script + judgement): 5.0 (cap 30)

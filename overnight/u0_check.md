# U0 check — round 3b artifact check + T3 closeout

git 0f9f122d; settings in u0_settings.json; no model loaded; no kill test

## Artifact checks

| check | got | expected | ok |
|---|---|---|---|
| c2_pairs rows | 40 | 40 | True |
| c2_pairs errors | 0 | 0 | True |
| t2_scores rows | 200 | 200 | True |
| t2_scores errors | 0 | 0 | True |
| t2_claims single-word non-error rows | 691 | 691 | True |
| t2_claims LLM corrupt single-word | 298 | 298 | True |
| t2_claims det single-word | 393 | 393 | True |
| t0_topics rows | 200 | 200 | True |
| t1_scores rows | 200 | 200 | True |
| stimuli rows | 200 | 200 | True |
| c2_descriptions rows | 80 | 80 | True |
| acts_L20 h20 shape | (200, 3584) | (200, 3584) | True |
| acts_L20 h20_pos2 shape | (200, 3584) | (200, 3584) | True |
| c2_acts H shape | (40, 2, 3584) | (40, 2, 3584) | True |
| c2_acts rows | 80 | 80 | True |
| c2_acts vs c2_pairs cos(h_a,h_b) max |dev| | 1.1102230246251565e-16 | <1e-4 | True |
| t2_prefix.py Settings created inside main() | True | True | True |
| c2_matched.py Settings created inside main() | True | True | True |

- all 18 checks passed: True

## T3 closeout (report only; not rerun, not extended)

- pre-registered design: pilot stimuli 0–39 (n=40) × 2 directions × 2 layers × 3 α = 480 items; stage cap 5100 s
- completed before the cap: 420 items = 35 pilot stimuli (0–34) × 12 cells; items per stimulus min 12 max 12; errors 0; 12.3 s/item; wall 2026-09-06T22:03:11 → 2026-09-06T23:29:47
- stopping rule as pre-registered (PLAN round 3): stage cap (T0 re-budget: 'T3 111 min > cap, run stimulus-outer and cut at cap'); settings `stopped_at_stimulus` = 35; round-3 PLAN execution order put T3 last ('dropped first under the hard stop')
- outcome rule as written in t3_settings.json: eligible = french cells with parse_ok >= 0.5; MET if all eligible CI hi < 0.25; NOT MET if any eligible CI lo >= 0.25; else INCONCLUSIVE; INCONCLUSIVE if no eligible cell
- kill T3 as written in t3_settings.json: outcome MET; eligible cells ['french_L8_a1']
- kill line as written in DISCONFIRMATION.md:

```
2026-09-06T23:29:47  T3  T3  threshold=French pass rate < 0.25 at every (ℓ, α) with parse_ok ≥ 0.5 (pilot, french direction, CI by stimulus)  observed=L8 α=1: pass 0.057 [0.000,0.143] parse_ok 1.00 n=35; L8 α=2: pass 0.400 [0.229,0.571] parse_ok 0.00 n=35; L8 α=4: pass 0.000 [0.000,0.000] parse_ok 0.00 n=35; L14 α=1: pass 0.114 [0.029,0.229] parse_ok 0.00 n=35; L14 α=2: pass 0.171 [0.057,0.314] parse_ok 0.00 n=35; L14 α=4: pass 0.514 [0.343,0.686] parse_ok 0.00 n=35; eligible cells 1/6  MET  MET would mean the AV is not steerable by residual addition either, at doses that keep it fluent
```

- RUNLOG lines for T3:

```
2026-09-06T22:03:04  T3  start  AV residual steering, pilot 0-39: french/terse directions at blocks 8,14 x α 1,2,4 = 12 cells x 40 = 480 generations (budget 111 min > 85-min cap; stimulus-outer, cut at cap)
2026-09-06T23:30:16  T3  done  420 items (35 of 40 pilot stimuli x 12 cells; generation cut at the 85-min stage cap before stimulus 35), 0 errors, 12.3 s/item; T3 MET (eligible french cells with parse_ok>=0.5: 1/6 = L8 α=1, pass 0.057 CI [0.000,0.143]; α>=2 destroys the <explanation> format at both layers, French pass up to 0.514 at L14 α=4 with parse_ok 0)
```

## Re-budget from round-3 measured costs (hypotheses, not measurements)

- unit costs used: {'av_forward_s': 0.35, 'av_generation_s': 10.0, 'ar_score_s': 0.36, 'target_short_forward_s': 0.11}

| stage | AV forwards | AV generations | AR scores | TARGET forwards | est. minutes (+ model loads) |
|---|---|---|---|---|---|
| T2c | 324 | 0 | 0 | 0 | 1.9 |
| T2a | 1200 | 0 | 0 | 0 | 7.0 |
| T2b | 2764 | 0 | 0 | 0 | 16.1 |
| C3 | 320 | 80 | 640 | 80 | 19.2 |

- total estimated compute 44.2 min + loads; hard stop 2026-09-07T02:19:14 (2.5 h after the first round-3b RUNLOG line 2026-09-06T23:49:14); stage cap 45 min


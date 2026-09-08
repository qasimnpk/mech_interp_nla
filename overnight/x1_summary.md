# X1 summary — cross-layer readout with the fixed layer-20 AV (TARGET → AV)

git b2c52797; settings in x1_settings.json; rows in x1_entity.csv (40 pairs x 4 layers), x1_topic.csv (160 eval x 4 layers); activations in out/x1_acts.npz

- layers [16, 20, 24, 27] (hidden_states [17, 21, 25, 28]); block-20 rows vs cached: max(1−cos) c2 2.2e-16, stimuli 2.2e-16; AV forwards 3479 (0.38 s); errors entity 0 topic 0
- mean activation norm per layer (c2 / stimuli): L16 71/76, L20 112/113, L24 290/274, L27 329/308; mean cos to the block-20 activation: L16 0.778/0.796, L20 1.000/1.000, L24 0.719/0.675, L27 0.131/0.144
- layer-20 re-run vs round-3b files: entity max |ΔD| 0.0000 (t2c), topic max |Δlp| 0.0000 (t2a)

## Kill X1

- entity donor-sensitivity CIs at L16 1.6423 [0.4788,2.8855], L24 2.9443 [1.1309,4.9711], L27 1.8292 [0.4446,3.8050] → **NOT MET**

## Per-layer table — entity (p1; 40 pairs; CI by template)

| block | donor sensitivity [CI] | frac>0 | both-correct raw | both-correct centred | choice acc raw (80) | choice acc centred (80) | AUROC D(h_a) vs D(h_b) | mean D(h_a) | mean D(h_b) |
|---|---|---|---|---|---|---|---|---|---|
| 16 | 1.6423 [0.4788,2.8855] | 0.775 | 0.275 [0.100,0.475] | 0.225 [0.075,0.425] | 0.637 [0.550,0.738] | 0.588 [0.487,0.700] | 0.6725 | +1.392 | -0.250 |
| 20 (training layer) | 1.7379 [0.6272,3.2762] | 0.775 | 0.225 [0.050,0.425] | 0.150 [0.025,0.300] | 0.600 [0.525,0.688] | 0.562 [0.487,0.650] | 0.6516 | +1.281 | -0.457 |
| 24 | 2.9443 [1.1309,4.9711] | 0.850 | 0.400 [0.200,0.625] | 0.275 [0.100,0.475] | 0.700 [0.600,0.812] | 0.637 [0.550,0.738] | 0.7256 | +2.319 | -0.625 |
| 27 | 1.8292 [0.4446,3.8050] | 0.850 | 0.225 [0.050,0.450] | 0.350 [0.175,0.525] | 0.600 [0.500,0.713] | 0.675 [0.588,0.762] | 0.6669 | +1.965 | +0.136 |

## Per-layer table — topic (p3; eval 160; CI by document)

| block | AUROC raw | AUROC prior-corrected | AUROC swap prefers foreign | acc raw | acc prior-corrected | swap-following raw | swap-following corr |
|---|---|---|---|---|---|---|---|
| 16 | 0.7281 [0.6783,0.7759] | 0.9209 [0.8907,0.9468] | 0.7542 [0.7037,0.8019] | 0.738 [0.669,0.806] | 0.931 [0.887,0.969] | 0.775 [0.713,0.838] | 0.931 [0.894,0.969] |
| 20 (training layer) | 0.7605 [0.7126,0.8059] | 0.9431 [0.9214,0.9643] | 0.7857 [0.7402,0.8300] | 0.781 [0.719,0.844] | 0.944 [0.906,0.975] | 0.800 [0.744,0.856] | 0.950 [0.912,0.981] |
| 24 | 0.7507 [0.6979,0.7991] | 0.9416 [0.9149,0.9635] | 0.7705 [0.7196,0.8168] | 0.756 [0.694,0.812] | 0.969 [0.938,0.994] | 0.781 [0.719,0.844] | 0.950 [0.912,0.981] |
| 27 | 0.6233 [0.5642,0.6753] | 0.7589 [0.7077,0.8017] | 0.6446 [0.5861,0.7008] | 0.594 [0.519,0.669] | 0.787 [0.725,0.844] | 0.613 [0.537,0.688] | 0.750 [0.688,0.819] |

- layer maximising entity choice accuracy: 24; topic accuracy: 20

## Pre-committed reading key (from PLAN; the numbers decide)

accuracy better elsewhere → training layer is not the best extraction layer for this task; donor sensitivity up without accuracy → distribution shift changes the readout without making it useful; both down → a measurable transfer limit.


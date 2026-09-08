# U1 summary — base-model control for the likelihood readout (TARGET weights in the AV interface)

git db4486ac; settings in u1_settings.json; rows in u1_topic.csv (200 stimuli), u1_entity.csv (40 pairs), u1_text.csv

- baseline = `Qwen/Qwen2.5-7B-Instruct` (snapshot a09a3545) loaded into `nla_lib.AV`'s interface via `TargetAsAV`; AV meta / tokenizer / prompt ids (125 tok, marker at 111, asserted equal under the TARGET tokenizer) / injection (norm 150, marker row replaced) / scoring code (`t2_prefix.Prefix`) unchanged; **the role assert of `nla_lib.AV` was bypassed by construction**
- AV scores are read from t2a_scores.csv (p3), t2_scores.csv (`The passage concerns`), t2c_pairs.csv (p1, p2) — same code path and activations; candidate token counts asserted equal per item
- baseline forwards 2478 in the AV interface (5.3 s per stimulus incl. text-only; entity 0.38 s/forward); topic errors 0, entity errors 0; eval n=160

## Kill U1 (p3, raw within-pair choice accuracy, eval, paired by document)

- paired [AV − baseline] raw accuracy: 0.312 [0.244,0.388] n=160 → **NOT MET**

## Side-by-side on identical items (160 evaluation documents; accuracy = fraction of documents where the true title wins; CI by document; AUROC paired bootstrap by document)

| readout | interpreter | acc raw | acc prior-corrected | acc no-injection | swap-following raw | swap-following corr | AUROC raw | AUROC corr | AUROC no-inj | AUROC swap |
|---|---|---|---|---|---|---|---|---|---|---|
| p3 `The document is about` (injected) | trained AV | 0.781 [0.719,0.844] | 0.944 [0.906,0.975] | 0.475 [0.400,0.556] | 0.800 [0.744,0.856] | 0.950 [0.912,0.981] | 0.7605 [0.7126,0.8059] | 0.9431 [0.9214,0.9643] | 0.4862 [0.4295,0.5500] | 0.7857 [0.7402,0.8300] |
| p3 `The document is about` (injected) | un-finetuned TARGET | 0.469 [0.394,0.544] | 0.494 [0.412,0.569] | 0.487 [0.412,0.569] | 0.494 [0.419,0.569] | 0.481 [0.400,0.556] | 0.4864 [0.4250,0.5503] | 0.4850 [0.4280,0.5457] | 0.4919 [0.4298,0.5575] | 0.5091 [0.4454,0.5696] |
| `The passage concerns` (injected) | trained AV | 0.775 [0.706,0.838] | 0.950 [0.912,0.981] | 0.481 [0.406,0.562] | 0.787 [0.725,0.844] | 0.950 [0.919,0.981] | 0.7516 [0.7017,0.7983] | 0.9347 [0.9111,0.9580] | 0.4880 [0.4315,0.5508] | 0.7749 [0.7295,0.8202] |
| `The passage concerns` (injected) | un-finetuned TARGET | 0.463 [0.388,0.537] | 0.500 [0.425,0.575] | 0.481 [0.406,0.556] | 0.519 [0.438,0.594] | 0.475 [0.400,0.550] | 0.4816 [0.4174,0.5423] | 0.4829 [0.4253,0.5375] | 0.4845 [0.4228,0.5469] | 0.5164 [0.4529,0.5762] |
| text-only: prefix tokens 0..pos + `\nThe document is about` (no injection) | un-finetuned TARGET | 0.988 [0.969,1.000] | 1.000 [1.000,1.000] | 0.481 [0.400,0.550] | — | — | 0.9924 [0.9800,0.9998] | 1.0000 [0.9998,1.0000] | 0.4859 [0.4242,0.5499] | — |

### Paired differences by document (eval 160)

| prefix | statistic | AV − baseline | AV − text | baseline − text |
|---|---|---|---|---|
| p3 | acc raw | 0.312 [0.244,0.388] | -0.206 [-0.269,-0.144] | -0.519 [-0.594,-0.444] |
| p3 | acc prior-corrected | 0.450 [0.362,0.537] | -0.056 [-0.094,-0.025] | -0.506 [-0.588,-0.431] |
| p3 | swap-following raw | 0.306 [0.237,0.375] | — | — |
| p3 | swap-following corr | 0.469 [0.388,0.556] | — | — |
| cc | acc raw | 0.312 [0.244,0.388] | -0.212 [-0.275,-0.150] | -0.525 [-0.606,-0.450] |
| cc | acc prior-corrected | 0.450 [0.369,0.531] | -0.050 [-0.087,-0.019] | -0.500 [-0.575,-0.425] |
| cc | swap-following raw | 0.269 [0.200,0.344] | — | — |
| cc | swap-following corr | 0.475 [0.394,0.556] | — | — |

## Entity readout on the 40 C2 pairs (80 activations; CI by template)

| prefix | interpreter | donor sensitivity mean [CI] | frac>0 | both-correct raw | both-correct corr | choice acc raw (80) | choice acc corr (80) | AUROC D(h_a) vs D(h_b) | mean D(h_0) |
|---|---|---|---|---|---|---|---|---|---|
| p1 | trained AV | 1.7379 [0.6272,3.2762] | 0.775 | 0.225 [0.050,0.425] | 0.150 [0.025,0.300] | 0.600 [0.525,0.688] | 0.562 [0.487,0.650] | 0.6516 | 0.524 |
| p1 | un-finetuned TARGET | -0.0111 [-0.1174,0.0607] | 0.575 | 0.025 [0.000,0.075] | 0.025 [0.000,0.075] | 0.512 [0.500,0.537] | 0.512 [0.500,0.537] | 0.5053 | 1.699 |
| p2 | trained AV | 1.8342 [0.7561,3.0039] | 0.775 | 0.175 [0.050,0.300] | 0.225 [0.050,0.425] | 0.588 [0.525,0.650] | 0.613 [0.525,0.713] | 0.6491 | 0.563 |
| p2 | un-finetuned TARGET | 0.0161 [-0.0599,0.0785] | 0.475 | 0.000 [0.000,0.000] | 0.000 [0.000,0.000] | 0.500 [0.500,0.500] | 0.500 [0.500,0.500] | 0.5000 | 0.858 |

| prefix | paired AV − baseline: donor sensitivity | choice acc raw | choice acc corr |
|---|---|---|---|
| p1 | 1.7490 [0.6778,3.2627] | 0.087 [0.025,0.175] | 0.050 [-0.013,0.138] |
| p2 | 1.8181 [0.8119,2.9868] | 0.087 [0.025,0.150] | 0.113 [0.025,0.212] |

## Pre-committed reading key (from PLAN; the numbers above decide, not this text)

AV > baseline with donor sensitivity → training improves the readout; similar and both follow the donor → useful readout exists, training advantage not established; baseline > AV → training may impair this readout; neither follows the donor → priors/confounds may explain apparent performance.

## Ten fixed rows (eval rows 40, 56, …, 184; p3 summed log-probs)

| stim | topic_true | topic_foreign | AV true | AV foreign | base true | base foreign | AV true noinj | base true noinj | text true | text foreign | text true prior | text foreign prior |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | Europium | The Litigators | -5.66 | -44.42 | -23.74 | -42.67 | -20.73 | -27.87 | -2.98 | -42.64 | -18.49 | -20.58 |
| 56 | Andrew Johnston (singer) | President Evil | -41.39 | -26.98 | -52.41 | -34.74 | -38.61 | -49.68 | -9.55 | -32.15 | -30.57 | -20.53 |
| 72 | No result, Pts | Blackburn Firecrest | -60.51 | -43.40 | -74.93 | -47.56 | -51.13 | -65.91 | -21.07 | -51.06 | -43.94 | -35.46 |
| 88 | Draining and development of the Everglades | Battle of Binh Gia | -38.27 | -41.40 | -51.43 | -42.73 | -52.70 | -49.70 | -6.60 | -42.55 | -34.55 | -28.51 |
| 104 | Martin Keamy | Pokiri | -34.24 | -36.41 | -51.77 | -40.25 | -39.48 | -52.52 | -2.75 | -36.47 | -36.02 | -23.00 |
| 120 | Chapter 1 (House of Cards) | Battle of Hubbardton | -34.92 | -45.69 | -46.68 | -45.15 | -33.62 | -42.31 | -10.01 | -36.96 | -32.39 | -24.42 |
| 136 | Hurricane Omar (2008) | Saint Leonard Catholic Church (Madison, Nebraska) | -28.96 | -65.87 | -44.37 | -72.51 | -29.03 | -42.96 | -8.29 | -60.16 | -24.79 | -47.80 |
| 152 | Ulysses (poem) | 766th Independent Infantry Regiment (North Korea) | -23.01 | -85.68 | -43.25 | -69.93 | -24.03 | -43.87 | -7.25 | -63.55 | -26.77 | -44.31 |
| 168 | Stop!! Hibari-kun! | Texas A & M Singing Cadets | -62.77 | -77.27 | -69.75 | -63.32 | -65.18 | -63.61 | -20.30 | -46.24 | -41.37 | -37.71 |
| 184 | Florida State Road 878 | Central Area Command (RAAF) | -34.60 | -56.16 | -49.65 | -69.18 | -38.80 | -47.79 | -1.66 | -65.81 | -30.80 | -41.95 |


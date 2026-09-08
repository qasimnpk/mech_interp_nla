# MORNING3c — round 3c (2026-09-08): base-model control, snippet interaction, cross-layer readout, frozen-AR rewards, layer curve, gated pilots

Written by T8 at 2026-09-08 03:06:32 local; git a49afcb6. Numbers only; no verdicts. Every number below is copied from a stage artifact (`<stage>_summary.md`, `<stage>_settings.json`, `DISCONFIRMATION.md`, `RUNLOG.md`).
Round started 2026-09-08 00:38:40 (first round-3c RUNLOG line); hard stop was 00:38:40 + 9 h.

## 1. Kill tests and gates (verbatim outcomes)

| K | stage | MET if (pre-registered threshold) | observed (from DISCONFIRMATION.md) | outcome |
|---|---|---|---|---|
| U1 | U1 | CI (cluster bootstrap by document) of paired [AV − baseline(un-finetuned Qwen2.5-7B-Instruct in the AV interface)] RAW p3 within-pair topic-choice accuracy, eval n=160 ≤ 0 | paired diff raw=0.312 [0.244,0.388] n=160; AV raw acc 0.781 [0.719,0.844] baseline raw acc 0.469 [0.394,0.544]; prior-corrected: diff 0.450 [0.362,0.537] (AV 0.944 base 0.494); AUROC raw AV 0.7605 base 0.4864; swap-following raw AV 0.800 base 0.494; entity p1 donor sensitivity AV 1.7379 [0.6272,3.2762] base -0.0111 [-0.1174,0.0607] paired diff 1.7490 [0.6778,3.2627]; text-only raw acc 0.988 [0.969,1.000] corr 1.000 [1.000,1.000] | **NOT MET** |
| X3-gate | X3 | feasibility: rows with a valid equal-length non-local deletion (condition 3) ≥ 100 | eligible rows 211 (of 490 accepted; last-claim 147, repeated changed word 132 excluded); available words ≥ snippet words: 86; valid contiguous span: 74 | **FAIL** |
| X3 | X3 | CI (cluster bootstrap by explanation) of mean I = (G_2 − G_1) − (G_3 − G_1), G_c = cos(AR(T_c),h) − cos(AR(F_c),h) ≤ 0; INCONCLUSIVE if condition-3 rows < 100 | mean I=-0.00057 [-0.00401,0.00206] n=74 n_expl=53; G_1 0.00115 [0.00000,0.00269] G_2 0.00217 [0.00042,0.00433] G_3 0.00275 [0.00052,0.00589]; G_2−G_1 0.00102 [0.00003,0.00223] G_3−G_1 0.00160 [-0.00030,0.00466]; A−P margins: c1 -0.00190 c2 -0.00317 c3 -0.00501; AUROC(Δcorrupt vs Δparaphrase) c1 0.2894 c2 0.4060 c3 0.3203; mean cos(T) c1 0.8727 c2 0.7952 c3 0.8567; eligible 211 (cond-3 valid 74) | **INCONCLUSIVE** |
| X1 | X1 | entity donor-sensitivity CI (by template) under p1 ≤ 0 at every non-training block (16, 24, 27) → MET; NOT MET if any of the three CIs is entirely > 0 | L16: donor 1.6423 [0.4788,2.8855] acc raw 0.637 both 0.275 topic AUROC raw 0.728 corr 0.921 acc raw 0.738; L20: donor 1.7379 [0.6272,3.2762] acc raw 0.600 both 0.225 topic AUROC raw 0.761 corr 0.943 acc raw 0.781; L24: donor 2.9443 [1.1309,4.9711] acc raw 0.700 both 0.400 topic AUROC raw 0.751 corr 0.942 acc raw 0.756; L27: donor 1.8292 [0.4446,3.8050] acc raw 0.600 both 0.225 topic AUROC raw 0.623 corr 0.759 acc raw 0.594; best entity acc L24, best topic acc L20; L20 max \|dev\| vs t2c 0.000, vs t2a 0.000 | **NOT MET** |
| N3 | N3 | CI (cluster by explanation) of mean [cost(generic) − cost(wrong specific)], cost(v) = cos(AR(z)) − cos(AR(z_v)), deterministic single-token swaps ≤ 0 | mean generic−wrong=-0.00029 [-0.00087,0.00025] n=393 n_expl=158; cost wrong 0.00249 [0.00169,0.00333] generic 0.00220 [0.00153,0.00292] omitted 0.05012 [0.04355,0.05708]; omitted−wrong 0.04763 [0.04108,0.05420]; frac generic>wrong 0.527; number n=89 generic−wrong 0.00015 [-0.00074,0.00113]; name n=304 -0.00041 [-0.00109,0.00019] | **INCONCLUSIVE** |
| RT-gates | RT | G0 native m>0 ≥14/16; G1 self-patch max\|Δlogit\|≤0.01 16/16; G2 twin patch Δm<0 ≥12/16 | G0 16/16 (mean m_native 12.902); G1 16/16 (max \|Δlogit\| 0.00e+00); G2 11/16 (mean Δm -1.242; mean cos(h, h_twin) 0.9900) | **FAIL** |
| M-gate | M | GM: ≥ 20 incorrect and ≥ 20 correct of 200 synthetic multiplications | correct 49, incorrect 151 (no 'Answer:' 147; incorrect with a position 4); mean generation length 194 tokens | **PASS** |
| M | M | AUROC(−cos(AR(desc), h), incorrect vs correct) at the model's own 'Answer:' token, CI by problem ≤ 0.60 | AUROC=0.2938 [0.0000,0.5706] n=44 (incorrect 4, correct 40); entropy 0.7937 [0.5854,0.9655]; −margin 0.7969 [0.5944,0.9593]; text-only −(yes−no) 0.3875 [0.2245,0.5436]; in-sample logistic AUROC entropy+margin 0.7812 vs +cos 0.8063 (cos coef +0.345, standardised; exploratory); mean cos correct 0.8737 incorrect 0.8829; problems correct 49/200 | **INCONCLUSIVE** |

Verbatim lines:

- `2026-09-08T01:05:51  U1  U1  threshold=CI (cluster bootstrap by document) of paired [AV − baseline(un-finetuned Qwen2.5-7B-Instruct in the AV interface)] RAW p3 within-pair topic-choice accuracy, eval n=160 ≤ 0  observed=paired diff raw=0.312 [0.244,0.388] n=160; AV raw acc 0.781 [0.719,0.844] baseline raw acc 0.469 [0.394,0.544]; prior-corrected: diff 0.450 [0.362,0.537] (AV 0.944 base 0.494); AUROC raw AV 0.7605 base 0.4864; swap-following raw AV 0.800 base 0.494; entity p1 donor sensitivity AV 1.7379 [0.6272,3.2762] base -0.0111 [-0.1174,0.0607] paired diff 1.7490 [0.6778,3.2627]; text-only raw acc 0.988 [0.969,1.000] corr 1.000 [1.000,1.000]  NOT MET  MET would mean NLA training does not improve this readout under the tested interface (not equivalence); if baseline matches the AV and both follow the donor, the readout is activation-dependent while the training advantage is not established`
- `2026-09-08T01:06:17  X3  X3-gate  threshold=feasibility: rows with a valid equal-length non-local deletion (condition 3) ≥ 100  observed=eligible rows 211 (of 490 accepted; last-claim 147, repeated changed word 132 excluded); available words ≥ snippet words: 86; valid contiguous span: 74  FAIL  if FAIL, condition 3 runs on the eligible rows and I is reported INCONCLUSIVE with n`
- `2026-09-08T01:11:16  X3  X3  threshold=CI (cluster bootstrap by explanation) of mean I = (G_2 − G_1) − (G_3 − G_1), G_c = cos(AR(T_c),h) − cos(AR(F_c),h) ≤ 0; INCONCLUSIVE if condition-3 rows < 100  observed=mean I=-0.00057 [-0.00401,0.00206] n=74 n_expl=53; G_1 0.00115 [0.00000,0.00269] G_2 0.00217 [0.00042,0.00433] G_3 0.00275 [0.00052,0.00589]; G_2−G_1 0.00102 [0.00003,0.00223] G_3−G_1 0.00160 [-0.00030,0.00466]; A−P margins: c1 -0.00190 c2 -0.00317 c3 -0.00501; AUROC(Δcorrupt vs Δparaphrase) c1 0.2894 c2 0.4060 c3 0.3203; mean cos(T) c1 0.8727 c2 0.7952 c3 0.8567; eligible 211 (cond-3 valid 74)  INCONCLUSIVE  MET would mean removing the snippet does not improve factual discrimination more than removing comparable other text; this is a property of the frozen scorer, not of training`
- `2026-09-08T01:48:14  X1  X1  threshold=entity donor-sensitivity CI (by template) under p1 ≤ 0 at every non-training block (16, 24, 27) → MET; NOT MET if any of the three CIs is entirely > 0  observed=L16: donor 1.6423 [0.4788,2.8855] acc raw 0.637 both 0.275 topic AUROC raw 0.728 corr 0.921 acc raw 0.738; L20: donor 1.7379 [0.6272,3.2762] acc raw 0.600 both 0.225 topic AUROC raw 0.761 corr 0.943 acc raw 0.781; L24: donor 2.9443 [1.1309,4.9711] acc raw 0.700 both 0.400 topic AUROC raw 0.751 corr 0.942 acc raw 0.756; L27: donor 1.8292 [0.4446,3.8050] acc raw 0.600 both 0.225 topic AUROC raw 0.623 corr 0.759 acc raw 0.594; best entity acc L24, best topic acc L20; L20 max |dev| vs t2c 0.000, vs t2a 0.000  NOT MET  MET would mean no readable transfer of the layer-20 AV's entity readout to other layers`
- `2026-09-08T01:54:15  N3  N3  threshold=CI (cluster by explanation) of mean [cost(generic) − cost(wrong specific)], cost(v) = cos(AR(z)) − cos(AR(z_v)), deterministic single-token swaps ≤ 0  observed=mean generic−wrong=-0.00029 [-0.00087,0.00025] n=393 n_expl=158; cost wrong 0.00249 [0.00169,0.00333] generic 0.00220 [0.00153,0.00292] omitted 0.05012 [0.04355,0.05708]; omitted−wrong 0.04763 [0.04108,0.05420]; frac generic>wrong 0.527; number n=89 generic−wrong 0.00015 [-0.00074,0.00113]; name n=304 -0.00041 [-0.00109,0.00019]  INCONCLUSIVE  MET would mean no evidence the frozen AR prefers a thematically matched wrong specific over a generic; says what the frozen scorer rewards, not what training caused`
- `2026-09-08T02:13:53  RT  RT-gates  threshold=G0 native m>0 ≥14/16; G1 self-patch max|Δlogit|≤0.01 16/16; G2 twin patch Δm<0 ≥12/16  observed=G0 16/16 (mean m_native 12.902); G1 16/16 (max |Δlogit| 0.00e+00); G2 11/16 (mean Δm -1.242; mean cos(h, h_twin) 0.9900)  FAIL  if FAIL, RT stops here: no layer or position search`
- `2026-09-08T02:57:07  M  M-gate  threshold=GM: ≥ 20 incorrect and ≥ 20 correct of 200 synthetic multiplications  observed=correct 49, incorrect 151 (no 'Answer:' 147; incorrect with a position 4); mean generation length 194 tokens  PASS  if FAIL, M stops here`
- `2026-09-08T03:05:34  M  M  threshold=AUROC(−cos(AR(desc), h), incorrect vs correct) at the model's own 'Answer:' token, CI by problem ≤ 0.60  observed=AUROC=0.2938 [0.0000,0.5706] n=44 (incorrect 4, correct 40); entropy 0.7937 [0.5854,0.9655]; −margin 0.7969 [0.5944,0.9593]; text-only −(yes−no) 0.3875 [0.2245,0.5436]; in-sample logistic AUROC entropy+margin 0.7812 vs +cos 0.8063 (cos coef +0.345, standardised; exploratory); mean cos correct 0.8737 incorrect 0.8829; problems correct 49/200  INCONCLUSIVE  MET would mean reconstruction error does not separate incorrect from correct answers beyond chance-level 0.60`

## 2. U1 — base-model control (REQUIRED): un-finetuned Qwen2.5-7B-Instruct in the AV interface vs the trained AV vs text-only, identical items

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

## 3. X3 — does the local snippet suppress factual discrimination? (AR only; eligibility count and n)

- accepted S3 triples 490 → eligible 211 (excluded: last-claim 147, changed word repeated in another claim 132); condition-3 feasibility: available words ≥ snippet words 86, valid contiguous span 74 (gate ≥ 100: FAIL)
- AR forwards 1337 (0.22 s each); judge generations 422 (0.94 s each); errors 0
- snippet word count: mean 38.2 (min 3, max 56); condition-3 candidate starts per row: mean 6.6
- judge: support yes 32 / no 179 / unparsed 0; contradict yes 1 / no 210 / unparsed 0; judge-valid (both yes) 1

## Kill X3

- mean I = G_2 − G_3 (rows with condition 3): -0.00057 [-0.00401,0.00206] n=74 → **INCONCLUSIVE**

### All rows with a valid condition 3 (primary) (n=74 rows, 53 explanations)

| condition | G = cos(T) − cos(F) [CI] | frac G>0 | P-margin cos(T) − cos(P) | A − P | AUROC(Δcorrupt vs Δparaphrase) | mean cos(T) |
|---|---|---|---|---|---|---|
| 1 full explanation | 0.00115 [0.00000,0.00269] | 0.568 | 0.00305 [0.00188,0.00422] | -0.00190 [-0.00362,0.00018] | 0.2894 | 0.8727 |
| 2 snippet (last claim) removed | 0.00217 [0.00042,0.00433] | 0.514 | 0.00534 [0.00238,0.00861] | -0.00317 [-0.00718,0.00084] | 0.4060 | 0.7952 |
| 3 equal-length non-local removal | 0.00275 [0.00052,0.00589] | 0.662 | 0.00776 [0.00407,0.01219] | -0.00501 [-0.00814,-0.00183] | 0.3203 | 0.8567 |

- G_2 − G_1: 0.00102 [0.00003,0.00223]; G_3 − G_1: 0.00160 [-0.00030,0.00466]; **I = G_2 − G_3: -0.00057 [-0.00401,0.00206]**

### Judge-valid subset (original supported AND corruption contradicts) (n=1 rows, 1 explanations)

| condition | G = cos(T) − cos(F) [CI] | frac G>0 | P-margin cos(T) − cos(P) | A − P | AUROC(Δcorrupt vs Δparaphrase) | mean cos(T) |
|---|---|---|---|---|---|---|
| 1 full explanation | -0.00033 [-0.00033,-0.00033] | 0.000 | 0.00170 [0.00170,0.00170] | -0.00202 [-0.00202,-0.00202] | 0.0000 | 0.8175 |
| 2 snippet (last claim) removed | -0.00023 [-0.00023,-0.00023] | 0.000 | 0.01090 [0.01090,0.01090] | -0.01113 [-0.01113,-0.01113] | 0.0000 | 0.8270 |
| 3 equal-length non-local removal | 0.00077 [0.00077,0.00077] | 1.000 | 0.00368 [0.00368,0.00368] | -0.00291 [-0.00291,-0.00291] | 0.0000 | 0.8104 |

- G_2 − G_1: 0.00010 [0.00010,0.00010]; G_3 − G_1: 0.00110 [0.00110,0.00110]; **I = G_2 − G_3: -0.00100 [-0.00100,-0.00100]**

### All eligible rows (conditions 1 and 2 on every row; condition 3 where valid) (n=211 rows, 136 explanations)

| condition | G = cos(T) − cos(F) [CI] | frac G>0 | P-margin cos(T) − cos(P) | A − P | AUROC(Δcorrupt vs Δparaphrase) | mean cos(T) |
|---|---|---|---|---|---|---|
| 1 full explanation | 0.00090 [0.00039,0.00151] | 0.597 | 0.00328 [0.00251,0.00412] | -0.00238 [-0.00342,-0.00137] | 0.3008 | 0.8800 |
| 2 snippet (last claim) removed | 0.00555 [0.00284,0.00906] | 0.564 | 0.02329 [0.01609,0.03156] | -0.01774 [-0.02559,-0.01080] | 0.3829 | 0.7539 |
| 3 equal-length non-local removal | 0.00275 [0.00052,0.00589] | 0.232 | 0.00776 [0.00407,0.01219] | -0.00501 [-0.00814,-0.00183] | 0.3203 | 0.8567 |

- G_2 − G_1: 0.00466 [0.00193,0.00808]; G_3 − G_1: 0.00160 [-0.00030,0.00466]; **I = G_2 − G_3: -0.00057 [-0.00401,0.00206]**

## Five verbatim rows (first five eligible rows with condition 3)

### row 137 (stim 41, claim 0/7; changed words ["learning", "machine", "novel", "romance"]; judge support=yes contradict=no)
- original: Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity.
- corrupt: Structured wiki format with "Bulleted facts" pattern suggests a romance novel or trivia context about a named entity.
- paraphrase: A structured wiki format using "Bulleted facts" implies a machine learning or trivia context involving a specific entity.
- snippet (last claim, 29 words): And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- condition 3 text (T): Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity. The phrase "The sentence 'It is a chemical process about United States . Its context is about ... ' is given a summary of the passage 'Context'." implies an was a narrative about ... And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- cos T/F/P: c1 0.7969/0.7944/0.7963; c2 0.7782/0.7783/0.7809; c3 0.7716/0.7684/0.7703; G_1 +0.00252 G_2 -0.00012 G_3 +0.00324 I -0.00336

### row 138 (stim 41, claim 1/7; changed words ["china", "states", "united"]; judge support=no contradict=no)
- original: The phrase "The sentence 'It is a chemical process about United States .
- corrupt: The phrase "The sentence 'It is a chemical process about China .
- paraphrase: The expression "The statement 'It represents a chemical procedure concerning the United States' .
- snippet (last claim, 29 words): And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- condition 3 text (T): Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity. The phrase "The sentence 'It is a chemical process about United States . Its context is about ... ' is given a closes a phrase ("The text : It was a narrative about ... And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- cos T/F/P: c1 0.7969/0.7932/0.7920; c2 0.7782/0.7731/0.7733; c3 0.7808/0.7781/0.7793; G_1 +0.00369 G_2 +0.00512 G_3 +0.00271 I +0.00241

### row 139 (stim 41, claim 2/7; changed words ["not"]; judge support=yes contradict=no)
- original: Its context is about ...
- corrupt: Its context is not about ...
- paraphrase: It pertains to the context of...
- snippet (last claim, 29 words): And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- condition 3 text (T): Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity. The phrase "The sentence 'It is a chemical process about United States . Its context is about ... ' is given " closes a phrase ("The text : It was a narrative about ... And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- cos T/F/P: c1 0.7969/0.7970/0.7982; c2 0.7782/0.7800/0.7789; c3 0.7842/0.7873/0.7871; G_1 -0.00011 G_2 -0.00181 G_3 -0.00314 I +0.00133

### row 140 (stim 41, claim 3/7; changed words ["answer", "expected", "question", "unexpected"]; judge support=no contradict=no)
- original: ' is given a summary of the passage 'Context'." implies an expected continuation or question about the passage's content, likely a summary or analysis task about the facts listed.
- corrupt: ' is given a summary of the passage 'Context'." implies an unexpected continuation or answer about the passage's content, likely a summary or analysis task about the facts listed.
- paraphrase: 'Context' provides a synopsis of the passage, suggesting a probable follow-up or inquiry regarding its details, probably involving summarizing or analyzing the information presented.
- snippet (last claim, 29 words): And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- condition 3 text (T): Structured wiki format with "Bulleted facts" ... ' is given a summary of the passage 'Context'." implies an expected continuation or question about the passage's content, likely a summary or analysis task about the facts listed. Final token "fact " closes a phrase ("The text : It was a narrative about ... And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- cos T/F/P: c1 0.7969/0.7955/0.7978; c2 0.7782/0.7719/0.7769; c3 0.7932/0.7907/0.7704; G_1 +0.00141 G_2 +0.00626 G_3 +0.00250 I +0.00376

### row 141 (stim 41, claim 4/7; changed words ["fact", "fiction"]; judge support=no contradict=no)
- original: Final token "fact
- corrupt: Final token "fiction
- paraphrase: Ultimate token "fact"
- snippet (last claim, 29 words): And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- condition 3 text (T): Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity. The phrase "The sentence 'It is a chemical likely a summary or analysis task about the facts listed. Final token "fact " closes a phrase ("The text : It was a narrative about ... And the passage : ..."), strongly expecting "What is the intent?" or "The passage contains the following attributes:" or "This passage describes" or similar concluding prompt or summary clause.
- cos T/F/P: c1 0.7969/0.7989/0.7917; c2 0.7782/0.7796/0.7725; c3 0.7853/0.7852/0.7784; G_1 -0.00196 G_2 -0.00137 G_3 +0.00017 I -0.00154

## 4. X1 — cross-layer readout with the layer-20 AV (per-layer tables)

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

## 5. N3 — what the frozen AR rewards: correct / wrong specific / generic / omitted (four-way table)

- accepted deterministic-swap triples 402 → 393 single-token swaps (9 excluded: swap not a single whitespace token); kinds {'name': 304, 'number': 89}; last-claim rows 127
- generic rule: number → `a number`; capitalised name → `a place` (the S3 swap list carries no person marker, so PLAN's else-branch applies to all names); no LLM
- AR forwards 1337 (0.25 s each); errors 0

## Kill N3

- mean [cost(generic) − cost(wrong specific)]: -0.00029 [-0.00087,0.00025] n=393 → **INCONCLUSIVE**

## Four-way table (cost = cos drop relative to the original; CI by explanation)

| subset | n | n_expl | mean cos(original) | cost(wrong specific) | cost(generic) | cost(omitted) | generic − wrong | omitted − wrong | omitted − generic | frac generic>wrong | frac omitted>wrong |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 393 | 158 | 0.8814 | 0.00249 [0.00169,0.00333] | 0.00220 [0.00153,0.00292] | 0.05012 [0.04355,0.05708] | -0.00029 [-0.00087,0.00025] | 0.04763 [0.04108,0.05420] | 0.04792 [0.04154,0.05462] | 0.527 | 0.885 |
| number swaps | 89 | 61 | 0.8747 | 0.00133 [0.00063,0.00214] | 0.00148 [0.00046,0.00270] | 0.07028 [0.05373,0.08812] | 0.00015 [-0.00074,0.00113] | 0.06895 [0.05257,0.08672] | 0.06880 [0.05231,0.08639] | 0.596 | 0.921 |
| name swaps | 304 | 150 | 0.8834 | 0.00283 [0.00189,0.00390] | 0.00241 [0.00161,0.00329] | 0.04422 [0.03740,0.05209] | -0.00041 [-0.00109,0.00019] | 0.04139 [0.03485,0.04880] | 0.04180 [0.03529,0.04925] | 0.507 | 0.875 |
| last claim | 127 | 127 | 0.8810 | 0.00592 [0.00370,0.00840] | 0.00491 [0.00330,0.00662] | 0.12867 [0.11013,0.14785] | -0.00101 [-0.00243,0.00027] | 0.12275 [0.10412,0.14126] | 0.12376 [0.10483,0.14258] | 0.551 | 0.984 |
| not last claim | 266 | 153 | 0.8817 | 0.00085 [0.00051,0.00118] | 0.00091 [0.00038,0.00147] | 0.01262 [0.01095,0.01455] | 0.00006 [-0.00034,0.00048] | 0.01177 [0.01017,0.01354] | 0.01171 [0.01015,0.01340] | 0.515 | 0.838 |

## Five verbatim rows (first five rows; number and name)

### row 154 (stim 45, claim 1/3, number: '2008"' → '2015"')
- original: The sentence structure "The 'Open Source' panel appeared at TED 2008" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- wrong specific: The sentence structure "The 'Open Source' panel appeared at TED 2015" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- generic: The sentence structure "The 'Open Source' panel appeared at TED a number" establishes a date reference ("The conference was held at IFLA 20"), implying a second event date follows about the book's attendance.
- cos original 0.8844; cost wrong +0.00263 generic +0.00666 omitted +0.03699

### row 155 (stim 45, claim 2/3, number: '"20"' → '"27"')
- original: Final token "20" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- wrong specific: Final token "27" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- generic: Final token "a number" is mid-number in "IFLA 20", part of a date expression ("Symposium 20"), strongly expecting "08" or "09" to complete the year, then "9" or "10, a conference on the findings."
- cos original 0.8844; cost wrong +0.00408 generic -0.00015 omitted +0.08756

### row 178 (stim 52, claim 1/3, number: '1st' → '3st')
- original: The paragraph "During its early formation the 1st Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- wrong specific: The paragraph "During its early formation the 3st Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- generic: The paragraph "During its early formation the a numberst Special Unit was organized as the 1st Korean Security Unit" mirrors the pattern of describing unit history and structure, now expected to continue listing subunits or organizational details about the unit's initial formation and designation.
- cos original 0.8498; cost wrong -0.00029 generic -0.00078 omitted +0.02152

### row 136 (stim 40, claim 3/4, name: '("Properties' → '("EMI')
- original: Final token "europium" ends mid-sentence ("Properties of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- wrong specific: Final token "europium" ends mid-sentence ("EMI of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- generic: Final token "europium" ends mid-sentence ("a place of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data.
- cos original 0.8783; cost wrong +0.00619 generic +0.00698 omitted +0.06216

### row 137 (stim 41, claim 0/7, name: '"Bulleted' → '"Trek')
- original: Structured wiki format with "Bulleted facts" pattern suggests a machine learning or trivia context about a named entity.
- wrong specific: Structured wiki format with "Trek facts" pattern suggests a machine learning or trivia context about a named entity.
- generic: Structured wiki format with "a place facts" pattern suggests a machine learning or trivia context about a named entity.
- cos original 0.7969; cost wrong -0.00217 generic -0.00154 omitted +0.00323

## 6. N4 — fact-vs-phrasing displacement across all TARGET layers (curve table; descriptive)

- C3 cells: 40 (errors 0); block-20 max(1−cos) vs c3_acts 2.2e-16; S3 triples: 490 (errors 0); 0.13 s/context, 0.15 s/claim text

## Per-layer curve (1 − cos at the last token; C3: entity edit = mean(A vs B, C vs D), phrasing edit = mean(A vs C, B vs D), CI by template; S3: claim vs corruption / paraphrase, CI by explanation)

| block | C3 d_entity [CI] | C3 d_phrasing [CI] | C3 entity − phrasing [CI] | C3 ratio entity/phrasing [CI] | S3 d_corr [CI] | S3 d_para [CI] | S3 corr − para [CI] | S3 ratio corr/para [CI] | mean norm C3 / S3 |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.00038 [0.00029,0.00050] | 0.00103 [0.00036,0.00203] | -0.00065 [-0.00156,-0.00003] | 1.204 [0.529,2.208] | 0.02415 [0.01605,0.03226] | 0.04017 [0.03108,0.04970] | -0.01602 [-0.02598,-0.00622] | 1.937 [1.165,2.797] | 13 / 10 |
| 1 | 0.00037 [0.00029,0.00048] | 0.00098 [0.00042,0.00173] | -0.00060 [-0.00127,-0.00009] | 0.887 [0.506,1.358] | 0.01892 [0.01221,0.02565] | 0.03264 [0.02578,0.04007] | -0.01372 [-0.02071,-0.00674] | 1.094 [0.704,1.513] | 19 / 17 |
| 2 | 0.00086 [0.00067,0.00107] | 0.00136 [0.00065,0.00251] | -0.00051 [-0.00155,+0.00019] | 1.245 [0.686,1.873] | 0.02085 [0.01380,0.02815] | 0.03957 [0.03243,0.04703] | -0.01872 [-0.02604,-0.01141] | 0.853 [0.552,1.159] | 23 / 18 |
| 3 | 0.00126 [0.00099,0.00156] | 0.00180 [0.00088,0.00328] | -0.00054 [-0.00195,+0.00046] | 1.347 [0.711,2.098] | 0.02708 [0.01904,0.03522] | 0.07298 [0.06460,0.08161] | -0.04590 [-0.05402,-0.03722] | 0.699 [0.437,0.993] | 24 / 19 |
| 4 | 0.00164 [0.00117,0.00217] | 0.00198 [0.00099,0.00359] | -0.00034 [-0.00184,+0.00085] | 1.614 [0.769,2.634] | 0.02850 [0.02018,0.03661] | 0.08471 [0.07583,0.09382] | -0.05621 [-0.06465,-0.04697] | 0.618 [0.367,0.900] | 27 / 23 |
| 5 | 0.00168 [0.00116,0.00222] | 0.00203 [0.00110,0.00351] | -0.00035 [-0.00163,+0.00071] | 1.430 [0.717,2.272] | 0.02786 [0.01931,0.03570] | 0.07891 [0.06959,0.08834] | -0.05105 [-0.06005,-0.04223] | 0.599 [0.358,0.859] | 31 / 28 |
| 6 | 0.00249 [0.00153,0.00373] | 0.00245 [0.00161,0.00362] | +0.00004 [-0.00138,+0.00163] | 1.401 [0.688,2.209] | 0.02901 [0.02019,0.03686] | 0.08405 [0.07428,0.09405] | -0.05504 [-0.06425,-0.04582] | 0.573 [0.349,0.823] | 35 / 31 |
| 7 | 0.00559 [0.00336,0.00828] | 0.00416 [0.00268,0.00578] | +0.00143 [-0.00165,+0.00482] | 2.155 [1.046,3.410] | 0.03182 [0.02280,0.04016] | 0.11351 [0.10360,0.12330] | -0.08169 [-0.09159,-0.07188] | 0.485 [0.286,0.734] | 42 / 38 |
| 8 | 0.00756 [0.00488,0.01078] | 0.00637 [0.00395,0.00918] | +0.00119 [-0.00313,+0.00564] | 1.998 [0.989,3.107] | 0.03451 [0.02478,0.04344] | 0.12933 [0.11867,0.13961] | -0.09483 [-0.10543,-0.08450] | 0.454 [0.262,0.693] | 48 / 43 |
| 9 | 0.02545 [0.01082,0.04463] | 0.00955 [0.00580,0.01460] | +0.01591 [-0.00073,+0.03685] | 4.412 [1.660,7.851] | 0.03357 [0.02449,0.04191] | 0.12633 [0.11618,0.13595] | -0.09276 [-0.10252,-0.08330] | 0.452 [0.256,0.692] | 52 / 46 |
| 10 | 0.02322 [0.01042,0.04070] | 0.00928 [0.00610,0.01306] | +0.01394 [-0.00059,+0.03337] | 4.157 [1.637,7.435] | 0.03188 [0.02344,0.03952] | 0.12302 [0.11300,0.13224] | -0.09114 [-0.10063,-0.08180] | 0.462 [0.260,0.719] | 56 / 49 |
| 11 | 0.02668 [0.01193,0.04819] | 0.01091 [0.00756,0.01443] | +0.01578 [-0.00106,+0.03916] | 3.982 [1.535,7.204] | 0.03458 [0.02566,0.04249] | 0.13324 [0.12334,0.14257] | -0.09866 [-0.10860,-0.08911] | 0.469 [0.268,0.728] | 56 / 51 |
| 12 | 0.02851 [0.01272,0.05218] | 0.01265 [0.00871,0.01669] | +0.01586 [-0.00251,+0.04104] | 3.569 [1.423,6.353] | 0.03709 [0.02792,0.04538] | 0.14160 [0.13174,0.15106] | -0.10450 [-0.11496,-0.09454] | 0.492 [0.278,0.787] | 58 / 52 |
| 13 | 0.03637 [0.01489,0.07186] | 0.01347 [0.00957,0.01756] | +0.02290 [-0.00089,+0.05977] | 3.892 [1.426,7.209] | 0.03465 [0.02649,0.04221] | 0.13023 [0.12146,0.13870] | -0.09558 [-0.10470,-0.08681] | 0.475 [0.278,0.740] | 63 / 59 |
| 14 | 0.03839 [0.01614,0.07620] | 0.01463 [0.01057,0.01866] | +0.02376 [-0.00081,+0.06258] | 3.803 [1.343,7.054] | 0.03726 [0.02863,0.04510] | 0.13532 [0.12605,0.14453] | -0.09805 [-0.10785,-0.08898] | 0.487 [0.290,0.749] | 65 / 59 |
| 15 | 0.03522 [0.01507,0.06933] | 0.01431 [0.01030,0.01801] | +0.02091 [-0.00096,+0.05630] | 3.570 [1.279,6.644] | 0.03595 [0.02797,0.04330] | 0.12642 [0.11818,0.13490] | -0.09048 [-0.09930,-0.08158] | 0.488 [0.302,0.730] | 72 / 66 |
| 16 | 0.04031 [0.01770,0.07823] | 0.01790 [0.01292,0.02260] | +0.02240 [-0.00213,+0.06197] | 3.305 [1.236,6.021] | 0.03964 [0.03120,0.04752] | 0.13745 [0.12870,0.14659] | -0.09782 [-0.10755,-0.08858] | 0.489 [0.302,0.729] | 72 / 67 |
| 17 | 0.04211 [0.01926,0.07987] | 0.02082 [0.01438,0.02719] | +0.02129 [-0.00380,+0.06122] | 3.107 [1.205,5.598] | 0.04156 [0.03287,0.04966] | 0.13848 [0.12941,0.14744] | -0.09692 [-0.10662,-0.08795] | 0.495 [0.311,0.730] | 74 / 69 |
| 18 | 0.03395 [0.01703,0.05999] | 0.01914 [0.01303,0.02501] | +0.01481 [-0.00432,+0.04374] | 2.902 [1.184,5.127] | 0.04086 [0.03240,0.04853] | 0.13501 [0.12605,0.14370] | -0.09414 [-0.10341,-0.08526] | 0.495 [0.315,0.743] | 82 / 79 |
| 19 | 0.03372 [0.01775,0.05836] | 0.02150 [0.01389,0.02920] | +0.01222 [-0.00676,+0.03984] | 2.538 [1.118,4.432] | 0.03952 [0.03115,0.04706] | 0.13339 [0.12426,0.14223] | -0.09387 [-0.10355,-0.08488] | 0.491 [0.307,0.752] | 93 / 94 |
| 20 | 0.03238 [0.01788,0.05490] | 0.02353 [0.01440,0.03336] | +0.00884 [-0.00948,+0.03447] | 2.342 [1.031,4.073] | 0.03952 [0.03112,0.04722] | 0.13357 [0.12455,0.14228] | -0.09405 [-0.10376,-0.08445] | 0.507 [0.310,0.781] | 111 / 112 |
| 21 | 0.03566 [0.01903,0.06006] | 0.02662 [0.01464,0.04135] | +0.00904 [-0.01170,+0.03834] | 2.543 [1.039,4.571] | 0.03768 [0.02936,0.04548] | 0.12828 [0.11938,0.13671] | -0.09059 [-0.10023,-0.08145] | 0.493 [0.307,0.750] | 138 / 140 |
| 22 | 0.04196 [0.02267,0.07032] | 0.02875 [0.01529,0.04612] | +0.01321 [-0.01191,+0.04769] | 3.385 [1.112,5.873] | 0.03891 [0.03077,0.04715] | 0.13128 [0.12200,0.13996] | -0.09237 [-0.10225,-0.08273] | 0.497 [0.317,0.750] | 173 / 174 |
| 23 | 0.04864 [0.02557,0.08624] | 0.02756 [0.01417,0.04488] | +0.02108 [-0.00882,+0.06415] | 4.663 [1.258,8.286] | 0.03926 [0.03123,0.04726] | 0.12556 [0.11699,0.13400] | -0.08629 [-0.09550,-0.07761] | 0.578 [0.341,0.914] | 228 / 214 |
| 24 | 0.05096 [0.02622,0.09159] | 0.02603 [0.01401,0.04059] | +0.02492 [-0.00680,+0.07114] | 5.299 [1.295,9.812] | 0.03638 [0.02862,0.04444] | 0.10953 [0.10197,0.11708] | -0.07315 [-0.08138,-0.06510] | 0.550 [0.350,0.834] | 290 / 274 |
| 25 | 0.05377 [0.02695,0.09742] | 0.02645 [0.01431,0.04111] | +0.02731 [-0.00661,+0.07602] | 5.202 [1.286,9.721] | 0.03658 [0.02894,0.04468] | 0.11238 [0.10438,0.12003] | -0.07580 [-0.08427,-0.06757] | 0.495 [0.342,0.693] | 353 / 325 |
| 26 | 0.05093 [0.02605,0.09160] | 0.02545 [0.01414,0.03941] | +0.02548 [-0.00671,+0.07045] | 4.749 [1.284,8.447] | 0.03609 [0.02910,0.04336] | 0.10936 [0.10190,0.11639] | -0.07327 [-0.08099,-0.06569] | 0.469 [0.350,0.623] | 438 / 396 |
| 27 | 0.04177 [0.01972,0.07808] | 0.02556 [0.01287,0.04352] | +0.01620 [-0.01263,+0.05860] | 3.413 [1.081,6.086] | 0.04025 [0.03062,0.04989] | 0.10723 [0.09752,0.11703] | -0.06698 [-0.07834,-0.05593] | 0.536 [0.400,0.702] | 328 / 322 |

- block 20 (the NLA layer): C3 entity 0.03238 vs phrasing 0.02353 (ratio 2.342); S3 corr 0.03952 vs para 0.13357 (ratio 0.507); round-2 R1 at block 20 reported d_corr_T 0.0395, d_para_T 0.1336
- layer with the largest C3 entity−phrasing difference: block 25 (+0.02731); largest C3 ratio: block 24 (5.299); largest S3 ratio corr/para: block 0 (1.937)
- a flat or rising curve is reported without a mechanism claim (PLAN)

## 7. X1b — cross-layer full generations (optional; descriptive)

- 80 generations (9.9 s each); block-20 row = the round-1 explanations on the same stimuli scored with the same rules; errors 0
- rules: quoted-final-token = a double-quoted span equals token_str; expecting-hit = first word of a quoted span after 'expecting' equals the target's top-1 next token (punctuation stripped); shuffled floor pairs stimulus i with the top-1 of (i+20) mod 40. The desk's block-20 figures (own 0.444, shuffled 0.029 [0.012, 0.056]) used an unverified rule and are not reproduced here by construction.

| block | parse_ok | CJK | quoted-final-token acc | expecting cands/expl | expecting hit (own top-1) | expecting hit (shuffled) | Jaccard vs L20 expl | cos(AR(desc), h_l) | cos(AR(desc), h_20) | cos(h_l, h_20) | words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 1.000 | 0.000 | 0.725 [0.575,0.850] | 2.05 | 0.275 [0.150,0.400] | 0.025 [0.000,0.075] | 0.408 | 0.761 [0.746,0.774] | 0.883 [0.868,0.897] | 0.801 | 99 |
| 27 | 0.950 | 0.075 | 0.000 [0.000,0.000] | 2.42 | 0.175 [0.050,0.300] | 0.025 [0.000,0.075] | 0.177 | 0.100 [0.089,0.111] | 0.409 [0.381,0.434] | 0.156 | 93 |
| 20 (training) | 1.000 | 0.025 | 0.650 [0.500,0.800] | 2.45 | 0.450 [0.300,0.600] | 0.025 [0.000,0.075] | 1.000 | 0.893 [0.881,0.906] | 0.893 [0.881,0.906] | 1.000 | 100 |

## Four fixed examples (stimuli 0, 7, 19, 33)

### stimulus 0 (token 'fall'; target top-1 ' near')
- block 20 (round 1): Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
- block 16 (parse_ok=True, cjk=False): Structured weather forecast article with numerical data and storm track details, presenting sequential storm movement data for Hurricane Ivan with labeled sections.

The sentence ending "The storm moved inland again and made a second landfall near Cape Hatteras, then retreated back into the Gulf of Mexico before making another landfall" continues listing multiple landfall events, completing the third landfall description with similar details.

Final token "landfall" ends an incomplete clause ("made another landfall"), part of a series of sequential landfall events ("also made a second landfall...and then re-established a second landfall"), expecting "in the same area" or "at a different location with a smaller intensity."
- block 27 (parse_ok=False, cjk=False): <explanation>
Scientific/mathematical text with formatted data and plots, transitioning to a weather system context with a specific storm track.

The phrase "A radar plot indicates the storm's movement towards the east coast, resulting in a transition to a stationary state" is a citation format with a date and "PST" label, suggesting a numerical result or a third-party event's PDE status.

Final token "order)    " closes a parenthetical expression ("The probability of a 3603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603

### stimulus 7 (token ' practices'; target top-1 ' with')
- block 20 (round 1): Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
- block 16 (parse_ok=True, cjk=False): Structured religious encyclopedia format with numbered definitions and scholarly tone establishes formal academic article pattern about a religious denomination.

The sentence mid-clause ("Thus, the Catholic Church defines a 'Jewish sect' as those who share common theological beliefs, liturgical rites and worship practices and shared theological beliefs and liturgical practices") mirrors an incomplete list describing characteristics of a unified tradition, continuing the definition of "Jewish mysticism."

Final token "practices" ends an incomplete enumeration ("similar theological beliefs and liturgical rites and ritual practices and shared rituals and religious practices"), strongly expecting "of the core" or "that are similar" or "to those of the tradition" to close the clause.
- block 27 (parse_ok=True, cjk=False): Structured Wikipedia-style definition format with numbered attributes describing a plant species, transitioning to a "flower" entry with a name and symbol.

The phrase "A certain species of plant may be classified as..." is a common template for a person's identity, followed by a "Hinduism" tag suggesting a cultural or identity-based identity, implying a "common" or "spiritual" identity statement.

Final token "sociable) and (then" is mid-sentence in a parenthetical identity declaration ("with the same or similar to 123: identical to..."), strongly expecting "a" or "the" followed by "a specific identity" or "a."

### stimulus 19 (token ' support'; target top-1 ' was')
- block 20 (round 1): Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
- block 16 (parse_ok=True, cjk=False): Historical article format with numbered entries detailing U.S. presidential election statistics, listing political party performance data for Franklin Roosevelt's first term.

The sentence structure "In the midterm election, his initial support was weak, but his campaign grew steadily. His support" appears to be mid-description of Roosevelt's electoral performance metrics or political characteristics, continuing a clause listing his vote outcomes or behavior.

Final token "support" ends an incomplete clause ("His support..."), part of a list of Roosevelt's performance details ("His support... his support"), likely continuing with "expanded beyond rural areas" or "was undermined by..." or "included a peak vote count," completing the narrative about his electoral trajectory.
- block 27 (parse_ok=True, cjk=False): Structured historical data format with numbered statistics listing political party vote trends, likely a Wikipedia or chart tool display.

The phrase "2015: Rising popularity with 125M votes. A rising vote" suggests a third entry in a sequence of vote counts, likely a third acronym or trend label ("Voting index"), implying a decline or resurgence of a specific party's popularity.

Final token "vourise" is mid-word ("a high ranking with a rising vote"), part of a third statistic entry ("A rising rank: 1250+ votes"), strongly expecting "count" or "widened" or "in the US" to complete the noun phrase.

### stimulus 33 (token ' a'; target top-1 ' mud')
- block 20 (round 1): News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
- block 16 (parse_ok=True, cjk=False): Formal news report format with numbered casualties listing from a US government disaster report, presenting statistical data with quoted eyewitness accounts from Argentina's earthquake.

The sentence ending "Other casualties included: Some Venezuelan refugees died in a car crash during the quake" gives a specific example of a death or accident consequence, listing a tragic personal incident with a concrete detail ("a family died in a").

Final token "a" is an indefinite article mid-clause ("in a"), part of a quoted casualty example ("One Venezuelan died in a..."), expecting a noun like "vehicle accident" or "flood" or "water-related drowning" or "house collapse" describing the family's fatal circumstance.
- block 27 (parse_ok=True, cjk=False): Technical Python error format with Stack Overflow context, suggesting a code snippet or error message about memory exhaustion in a Linux/Unix environment.

The phrase "The question is : 'Error: Memory Exhaustion due to a flood of requests' implies that the event is about the destruction of a session or dataset" mirrors the pattern "P1: Calculate the total memory usage," strongly implying the same query about a crash.

Final token "P1" is mid-expression ("GHC1: 101:GHC"), directly continuing the error scenario description, expecting "...crash" or "...of the dataset' or "...time' or "two events" completing the query.

## 8. RT — round-trip relational pilot (gated)

- G0 16/16 (need ≥14); G1 16/16 (need 16); G2 11/16 (need ≥12)

| ctx | text | correct | m_native | top1 | self-patch max|Δlogit| | m_twin_patch | Δm | cos(h,h_twin) |
|---|---|---|---|---|---|---|---|---|
| 0 | 'Anna received the key. Tom received the book.\nQuestion: Who received the key?\nAnswer:' | Anna | +8.875 | ' Anna' | 0.00e+00 | +6.625 | -2.250 | 0.9883 |
| 1 | 'Tom received the key. Anna received the book.\nQuestion: Who received the key?\nAnswer:' | Tom | +13.625 | ' Tom' | 0.00e+00 | +11.375 | -2.250 | 0.9883 |
| 2 | 'Anna received the coin. Tom received the letter.\nQuestion: Who received the coin?\nAnswer:' | Anna | +11.750 | ' Anna' | 0.00e+00 | +9.250 | -2.500 | 0.9909 |
| 3 | 'Tom received the coin. Anna received the letter.\nQuestion: Who received the coin?\nAnswer:' | Tom | +12.375 | ' Tom' | 0.00e+00 | +12.938 | +0.562 | 0.9909 |
| 4 | 'Anna received the cup. Tom received the hat.\nQuestion: Who received the cup?\nAnswer:' | Anna | +12.062 | ' Anna' | 0.00e+00 | +9.625 | -2.438 | 0.9922 |
| 5 | 'Tom received the cup. Anna received the hat.\nQuestion: Who received the cup?\nAnswer:' | Tom | +15.000 | ' Tom' | 0.00e+00 | +13.250 | -1.750 | 0.9922 |
| 6 | 'Anna received the map. Tom received the pen.\nQuestion: Who received the map?\nAnswer:' | Anna | +10.688 | ' Anna' | 0.00e+00 | +10.875 | +0.188 | 0.9931 |
| 7 | 'Tom received the map. Anna received the pen.\nQuestion: Who received the map?\nAnswer:' | Tom | +11.250 | ' Tom' | 0.00e+00 | +10.562 | -0.688 | 0.9931 |
| 8 | 'Sara received the key. Ben received the book.\nQuestion: Who received the key?\nAnswer:' | Sara | +13.625 | ' Sara' | 0.00e+00 | +13.875 | +0.250 | 0.9879 |
| 9 | 'Ben received the key. Sara received the book.\nQuestion: Who received the key?\nAnswer:' | Ben | +15.375 | ' Ben' | 0.00e+00 | +12.500 | -2.875 | 0.9879 |
| 10 | 'Sara received the coin. Ben received the letter.\nQuestion: Who received the coin?\nAnswer:' | Sara | +11.375 | ' Sara' | 0.00e+00 | +11.125 | -0.250 | 0.9891 |
| 11 | 'Ben received the coin. Sara received the letter.\nQuestion: Who received the coin?\nAnswer:' | Ben | +15.875 | ' Ben' | 0.00e+00 | +13.625 | -2.250 | 0.9891 |
| 12 | 'Sara received the cup. Ben received the hat.\nQuestion: Who received the cup?\nAnswer:' | Sara | +15.500 | ' Sara' | 0.00e+00 | +12.500 | -3.000 | 0.9872 |
| 13 | 'Ben received the cup. Sara received the hat.\nQuestion: Who received the cup?\nAnswer:' | Ben | +11.500 | ' Ben' | 0.00e+00 | +12.312 | +0.812 | 0.9872 |
| 14 | 'Sara received the map. Ben received the pen.\nQuestion: Who received the map?\nAnswer:' | Sara | +13.938 | ' Sara' | 0.00e+00 | +14.188 | +0.250 | 0.9912 |
| 15 | 'Ben received the map. Sara received the pen.\nQuestion: Who received the map?\nAnswer:' | Ben | +13.625 | ' Ben' | 0.00e+00 | +11.938 | -1.688 | 0.9912 |

## 9. M — error-monitoring pilot (gated)

- problems: correct 49, incorrect 151 (no 'Answer:' 147); gate GM PASS; generation 12.8 s each, mean 194 tokens; sample incorrect 4 correct 40; NLA 10.4 s/item; parse_ok 44/44

## Kill M

- AUROC(−cos) incorrect vs correct: 0.2938 [0.0000,0.5706] → **INCONCLUSIVE**

| signal (higher = predicts incorrect) | AUROC [CI by problem] |
|---|---|
| −cos(AR(desc), h) (NLA) | 0.2938 [0.0000,0.5706] |
| next-token entropy at 'Answer:' | 0.7937 [0.5854,0.9655] |
| −(top-1 margin) | 0.7969 [0.5944,0.9593] |
| −(yes − no) text-only self-check | 0.3875 [0.2245,0.5436] |

- in-sample logistic (exploratory): entropy + margin AUROC 0.7812; + cos 0.8063; standardised coefficients with cos: entropy -0.982, margin -2.218, cos +0.345
- mean cos: correct 0.8737, incorrect 0.8829; mean entropy correct 0.023 incorrect 0.056

## Five verbatim cases (first 3 incorrect, first 2 correct in the sample)

### problem 93: 207 × 87 = 18009; model answer 17909 (incorrect); cos 0.8767; entropy 0.013; margin 6.625; yes−no +7.12
- generation:  Step-by-step solution: ⏎ 1. Break down the multiplication into simpler parts using the distributive property of multiplication over addition. ⏎ 2. Express 207 as (200 + 7) and 87 as (80 + 7). ⏎ 3. Multiply each part of 207 by each part of 87: ⏎    - \(200 \times 80 = 16000\) ⏎    - \(200 \times 7 = 1400\) ⏎    - \(7 \times 80 = 560\) ⏎    - \(7 \times 7 = 49\) ⏎ 4. Add all these products together: ⏎    - \(16000 + 1400 + 560 + 49 = 17909\) ⏎  ⏎ Answer: 17909.
- explanation: Structured math problem format with labeled steps and calculations, indicating a worked solution for a number sequence problem.

The phrase "The final answer is: 12345 + 6789 = 19134. Answer: " signals the answer box format, completing the pattern "The final answer is labeled as..." implying the final answer box value is shown.

Final token "Answer: " closes the answer label ("Answer: "), directly following "Answer: 12345" — strongly expects "19134" or "81" to close the box, completing the stated answer and confirming the integer sequence's solution.

### problem 123: 226 × 61 = 13786; model answer 13 (incorrect); cos 0.8934; entropy 0.086; margin 4.125; yes−no +7.25
- generation:  Step-by-step solution: ⏎  ⏎ 1. Break down the multiplication into simpler parts: ⏎    - \( 226 \times 60 \) ⏎    - \( 226 \times 1 \) ⏎  ⏎ 2. Calculate \( 226 \times 60 \): ⏎    - \( 226 \times 60 = 226 \times (6 \times 10) \) ⏎    - \( 226 \times 6 = 1356 \) ⏎    - \( 1356 \times 10 = 13560 \) ⏎  ⏎ 3. Calculate \( 226 \times 1 \): ⏎    - \( 226 \times 1 = 226 \) ⏎  ⏎ 4. Add the results from steps 2 and 3: ⏎    - \( 13560 + 226 = 13786 \) ⏎  ⏎ Answer: 13
- explanation: Structured math problem format with labeled steps showing calculations for a sequence, implying a final answer box with "The product of the sequence is."

The phrase "Final answer: 123456... Answer: " mirrors the pattern "The answer is determined, therefore the final answer is," strongly suggesting the closing answer "12345" or "999."

Final token "Answer: " closes the answer declaration phrase ("Final answer: "), directly completing the concluding statement pattern, strongly expecting "999" or "12345" as the numeric answer, likely followed by "999" to close the box.

### problem 154: 571 × 35 = 19985; model answer 20985 (incorrect); cos 0.8842; entropy 0.010; margin 6.750; yes−no +6.62
- generation:  Step 1: Multiply 571 by 5 (the ones digit of 35). ⏎ \[ 571 \times 5 = 2855 \] ⏎  ⏎ Step 2: Multiply 571 by 30 (the tens digit of 35, which is 3 times 10). ⏎ \[ 571 \times 30 = 17130 \] ⏎  ⏎ Step 3: Add the results from steps 1 and 2. ⏎ \[ 2855 + 17130 = 20985 \] ⏎  ⏎ Answer: 20985 ⏎ You are welcome! If you have any more questions or need further assistance with math problems or any other subject, feel free to ask.
- explanation: Structured math problem format with numbered steps and calculations, indicating a worked-out answer for a number sequence problem involving cube and square operations.

The phrase "Final answer: The calculated value is 12345. Answer: " signals the concluding answer format, completing the "boxed answer" convention, strongly implying the final answer is "12345."

Final token "Answer: " closes the answer phrase "Answer: Boxed number: ", directly following the pattern "Final answer: 12345" — expects "12345" or "999" as the final boxed answer, completing the concluding statement about the puzzle's solution.

### problem 0: 865 × 67 = 57955; model answer 57955 (correct); cos 0.8721; entropy 0.001; margin 9.125; yes−no +3.88
- generation:  Step 1: Break down the multiplication into simpler parts. ⏎ Step 2: Multiply 865 by 70 (which is 67 + 3). ⏎ Step 3: Calculate 865 × 70 = 60550. ⏎ Step 4: Subtract 865 × 3 from the result of step 3 to adjust for the extra 3 in 70. ⏎ Step 5: Calculate 865 × 3 = 2595. ⏎ Step 6: Subtract 2595 from 60550 to get the final answer. ⏎ Step 7: 60550 - 2595 = 57955. ⏎  ⏎ Answer: 57955 ⏎ You're correct in your approach and calculations. Let's break it down step-by-step to ensure clarity: ⏎  ⏎ 1. **Break down the multiplication**: We can use the distributive property to simplify
- explanation: Structured math problem format with numbered steps and calculations, suggesting a puzzle or answer format with a specific numeric result.

The phrase "The final answer: Calculation: 123456... Answer: " signals the concluding answer box, completing the pattern "The sequence's answer is 9999" — strongly implying the final answer box displays "9999".

Final token "Answer: " closes the answer label ("Answer: 9999"), directly expecting the numeric result or closing phrase "9999" or "12345" to complete the box label, likely followed by "9999" or similar.

### problem 1: 560 × 35 = 19600; model answer 19600 (correct); cos 0.8905; entropy 0.100; margin 4.000; yes−no +7.75
- generation:  Step-by-step solution: ⏎  ⏎ 1. Break down the multiplication into simpler parts: ⏎    - \( 560 \times 35 = 560 \times (30 + 5) \) ⏎     ⏎ 2. Distribute 560 across the terms inside the parentheses: ⏎    - \( 560 \times 30 + 560 \times 5 \) ⏎  ⏎ 3. Calculate each part separately: ⏎    - \( 560 \times 30 = 560 \times 3 \times 10 = 1680 \times 10 = 16800 \) ⏎    - \( 560 \times 5 = 2800 \) ⏎  ⏎ 4. Add the results of the two multiplications: ⏎    - \( 16800 + 2800 = 19600 \) ⏎  ⏎ Answer: 19600 ⏎  ⏎ Therefore,
- explanation: Structured math problem format with labeled steps showing calculations for a sequence, implying a final answer is being presented.

The phrase "Thus, the calculated value is: 12345. Final answer: " mirrors a concluding statement pattern, strongly implying the answer "12345" is the final result, completing the "boxed answer" convention.

Final token "answer: " closes the phrase "Answer: " and is part of the concluding summary statement "Final answer: Boxed answer," immediately expecting the numeric value "12345" or "96" to close the box, likely followed by "96" or "The number."

## 10. FOLLOWUPS added this round

- X3 judge: the TARGET judged only 32/211 original claims 'supported' and 1/211 corruptions 'contradicting' the prefix (most S3 claims describe format/expectation rather than checkable facts), so the pre-registered judge-valid subset is n=1; a claim-type filter or a different judge prompt would be needed for a usable validity subset.

## 11. Provenance

- **Pre-registered by the human (PLAN.md 'Round 3c stages', 2026-09-08):** every stage, its rows, conditions, prefixes, candidates, layers, gates, thresholds, bootstrap unit, pilot/eval split, execution order, caps and the 9 h hard stop.
- **Built by the agent this round (all in `overnight/`, one process per stage, Settings created inside `main()`):** `u0c_check.py`, `u1_base.py` (class `TargetAsAV`: the AV's meta/tokenizer/prompt/injection with the TARGET's weights; `nla_lib.AV` role assert bypassed by construction; AV scores read from the round-3/3b files with token counts asserted), `x3_snippet.py`, `x1_layers.py`, `n3_generic.py`, `n4_layers.py`, `x1b_gen.py`, `rt_roundtrip.py` (residual hook copied from `src/patching.py`'s pattern), `m_monitor.py`, `t8_morning.py`.
- **Agent choices inside the pre-registration (each logged in the stage's settings/summary):** X3 'changed word' = symmetric word-set difference (lower-cased, punctuation-stripped), condition-3 span drawn at claim level with the tested claim and the snippet protected; X3 judge prompts (two fixed yes/no prompts, greedy, ≤4 tokens); N3 kind rule (digit → number, else name) and the generic 'a place' for every name (the S3 swap list carries no person marker, so PLAN's else-branch applies); X1b's mechanical quoted-token / expecting-hit rules (the desk's 0.444 / 0.029 figures used an unverified rule and are quoted as such); RT perturbation seeds (SEED + 100·s + ctx_id); M raw-text prompt (no chat template), the 'Answer:' token rule and the yes/no self-check wording; U1 text-only prefix = tokens 0..pos inclusive.
- **Crash fixes (RUNLOG):** U0c iteration 1 (benchmark loop bug before any output). No script was edited after seeing evaluation outputs.
- **Not run / stopped as pre-declared:** RT routes (gate G2 11/16 < 12); X3 condition-3 feasibility gate FAIL (74 < 100) → I reported INCONCLUSIVE with n=74.

## 12. Wall-clock and measured per-item costs

| stage | start | end | min | status |
|---|---|---|---|---|
| U0c | 00:38:40 | 00:44:56 | 6.3 | done |
| U1 | 00:44:56 | 01:06:14 | 21.3 | done |
| X3 | 01:06:14 | 01:21:46 | 15.5 | done |
| X1 | 01:21:46 | 01:48:35 | 26.8 | done |
| N3 | 01:48:35 | 01:54:34 | 6.0 | done |
| N4 | 01:54:34 | 01:59:12 | 4.6 | done |
| X1b | 01:59:12 | 02:13:34 | 14.4 | done |
| RT | 02:13:34 | 02:14:11 | 0.6 | blocked |
| M | 02:14:11 | 03:06:01 | 51.8 | done |
| T8 | 03:06:01 | 03:06:32 | 0.5 | running |

- total 2.46 h from the first round-3c RUNLOG line to T8

## Measured costs (5 calls each; mean / min / max seconds; MPS synchronised)

| call type | mean s | min s | max s | note |
|---|---|---|---|---|
| target_short_forward | 0.422 | 0.117 | 1.584 | {"tokens": 19} |
| target_doc512_forward_all_hidden | 1.123 | 1.112 | 1.160 | {"tokens": [512, 512, 512, 512, 512], "max_1_minus_cos_vs_acts_L20": 1.1102230246251565e-16} |
| target_forward_hook_block20 | 0.099 | 0.099 | 0.100 | {"self_patch_max_abs_logit_diff": 0.0} |
| av_forward_prefill | 0.597 | 0.383 | 1.440 | {} |
| av_generation_200 | 9.789 | 9.532 | 9.977 | {"n_tokens": [145, 143, 146, 145, 140], "parse_ok": [true, true, true, true, true]} |
| ar_score | 0.480 | 0.275 | 1.295 | {} |

- model loads: TARGET 6 s, AV 5 s, AR 4 s; RSS after TARGET free 0.6 G, after AV free 0.6 G
- self-patch at block 20 (own row written back): max |Δlogit| 0.00e+00 (bf16)
- 512-token document forward: block-20 activation at pos vs acts_L20 max(1−cos) 1.11e-16

RUNLOG lines (verbatim):

- `2026-09-08T00:38:40  U0c  start  round 3c begins (single long session, not /loop); artifact check + micro-benchmark of every call type + re-budget; hard stop = 2026-09-08T00:38:40 + 9 h = 2026-09-08T09:38:40`
- `2026-09-08T00:42:22  U0c  crashfix  iteration 1 crashed in the 512-token benchmark loop before any output (RuntimeError: docs.index(tensor) boolean ambiguity); loop now iterates indices; no measurement changed; rerun (out/u0c_iter1_crash.log)`
- `2026-09-08T00:44:56  U0c  done  27/27 artifact checks OK; measured s/call (5 each, first call includes warm-up): TARGET short fwd 0.42 (min 0.12), TARGET 512-doc all-hidden 1.12, TARGET hook@20 0.10 (self-patch max|Δlogit| 0), AV prefill fwd 0.60 (min 0.38), AV gen-200 9.8, AR score 0.48 (min 0.28); re-budget: every stage under its cap, total projected 199 min; one pre-output crash fix logged above`
- `2026-09-08T00:44:56  U1  start  base-model control: TARGET weights in the AV interface (TargetAsAV), p3/PREFILL_CC topic on 200 stimuli (own/swap/no-inj), p1/p2 entity on 40 pairs, text-only reference; AV scores from t2a/t2/t2c files`
- `2026-09-08T01:06:14  U1  done  2478 baseline forwards (TARGET weights in the AV interface; role assert bypassed by construction), 0 errors; U1 NOT MET (paired [AV − baseline] raw p3 acc 0.312 CI [0.244,0.388]; AV 0.781, baseline 0.469, text-only 0.988; prior-corrected AV 0.944 base 0.494; entity p1 donor AV 1.738 base -0.011); wall 00:44:50→01:05:51`
- `2026-09-08T01:06:14  X3  start  snippet vs factual discrimination: AR scoring (T/F/P x 3 conditions on eligible S3 triples) then TARGET judge`
- `2026-09-08T01:21:46  X3  done  211 eligible rows (147 last-claim + 132 repeated-word excluded), 1337 AR forwards (0.22 s), 422 judge generations (0.94 s), 0 errors; X3-gate FAIL (valid condition-3 rows 74 < 100); X3 INCONCLUSIVE (mean I=-0.00057 CI [-0.00401,0.00206] n=74; G1 0.00115 G2 0.00217 G3 0.00275); judge-valid subset n=1 (contradict=yes for 1/211); wall 01:06→01:18`
- `2026-09-08T01:21:46  X1  start  cross-layer readout: TARGET (80 C2 contexts + 200 docs at blocks 16/20/24/27) then AV (p1 entity 40 pairs, p3 topic eval 160, at each layer)`
- `2026-09-08T01:48:35  X1  done  280 TARGET forwards, 3479 AV forwards (0.38 s), 0 errors, block-20 rows match cached (1−cos 2e-16) and t2c/t2a scores to 0.0000; X1 NOT MET (entity donor sensitivity L16 1.64 [0.48,2.89], L24 2.94 [1.13,4.97], L27 1.83 [0.44,3.81]; L20 1.74; best entity acc L24 0.700, best topic acc L20 0.781; L27 topic AUROC raw 0.62); wall 01:19→01:48`
- `2026-09-08T01:48:35  N3  start  frozen-AR four-way (original / wrong specific / generic / omitted) on deterministic single-token swaps, AR only`
- `2026-09-08T01:54:34  N3  done  393 single-token det swaps (304 name, 89 number; 9 excluded), 1337 AR forwards (0.25 s), 0 errors; N3 INCONCLUSIVE (generic−wrong -0.00029 CI [-0.00087,0.00025]; cost wrong 0.00249 generic 0.00220 omitted 0.05012; omitted−wrong 0.04763 [0.04108,0.05420]); generic rule: number→'a number', name→'a place' (no person marker in the S3 list); wall 01:49→01:54`
- `2026-09-08T01:54:34  N4  start  fact-vs-phrasing displacement across blocks 0..27 in the TARGET: 40 C3 cells x 4 contexts + 490 S3 triples x 3 texts`
- `2026-09-08T01:59:12  N4  done  160 C3 contexts + 1470 S3 claim texts through all 28 blocks (0.13-0.15 s each), 0 errors, block-20 rows match c3_acts (2e-16) and R1 (S3 d_corr 0.0395 / d_para 0.1336); descriptive, no kill: C3 entity/phrasing ratio 1.20 (b0) → 2.34 (b20) → 5.30 (b24, max) → 3.41 (b27); S3 corr/para ratio 1.94 (b0) → 0.51 (b20) → ~0.4 (b27); n4_curve.csv; wall 01:55→01:59`
- `2026-09-08T01:59:12  X1b  start  optional cross-layer generations: 40 pilot stimuli x blocks 16/27, AV then AR co-resident`
- `2026-09-08T02:13:34  X1b  done  80 generations (9.9 s), 0 errors; descriptive: block 16 parse_ok 1.00 quoted-token acc 0.725 expecting-hit 0.275 (shuffled 0.025) cos(AR,h_16) 0.761 cos(AR,h_20) 0.883; block 27 parse_ok 0.95 CJK 0.075 quoted-token 0.000 expecting-hit 0.175 cos(AR,h_27) 0.100 cos(AR,h_20) 0.409; block 20 (round-1 explanations, same rules) quoted-token 0.650 expecting-hit 0.450 shuffled 0.025; wall 01:59→02:13`
- `2026-09-08T02:13:34  RT  start  gated round-trip pilot: 16 contexts; TARGET (native, G0/G1/G2) → AV+AR → TARGET (text QA, round-trip and perturbation patches)`
- `2026-09-08T02:14:11  RT  blocked  gate G2 FAIL: twin donor patch moved m toward the twin's answer in 11/16 (need ≥12; mean Δm -1.24, cos(h,h_twin) 0.990); G0 16/16 (mean m_native 12.9), G1 16/16 (self-patch max|Δlogit| 0); routes not run, no layer/position search (pre-declared); rt_gates.csv, rt_summary.md; wall 02:13→02:14`
- `2026-09-08T02:14:11  M  start  gated error-monitoring pilot: 200 synthetic multiplications (TARGET greedy ≤200 tok, raw text) → gate GM → 80-item sample: activation/entropy/margin/text-only at the model's own 'Answer:' → AV+AR`
- `2026-09-08T03:06:01  M  done  200 TARGET generations (12.8 s, mean 194 tokens), M-gate PASS by count (49 correct / 151 incorrect) but 147 incorrect items never wrote 'Answer:' within 200 tokens → 4 incorrect with a position; sample 4 incorrect + 40 correct, 44 AV+AR items (10.4 s), 0 errors; M INCONCLUSIVE (AUROC(−cos) 0.294 CI [0.000,0.571], n_pos 4 < 20; entropy 0.794, −margin 0.797); wall 02:14→03:05`
- `2026-09-08T03:06:01  T8  start  MORNING3c.md`


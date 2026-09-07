# C3 summary — meaning-preserving phrasing control for C2, factorial (TARGET → AV → AV+AR)

git ce6655aa; settings in c3_settings.json; cells in c3_cells.csv; new descriptions in c3_descriptions.jsonl; activations in out/c3_acts.npz (A, B, C, D)

This is a *phrasing control*, not a zero-information edit: (w1 → w2) is a one-word, meaning-preserving wording change in the same sentence as the entity.

- cells 40 (errors 0); templates used 10, dropped []; wording kinds {'primary': 40}
- wording pairs used: t0 primary: country→nation; t1 primary: calls→asks; t2 primary: moved→shifted; t3 primary: orchestra→ensemble; t4 primary: pure→solid; t5 primary: story→tale; t6 primary: was→got; t7 primary: worked→served; t8 primary: team's→club's; t9 primary: shows→depicts
- wording word distance to end (tokens): 12–20 (mean 16.8); entity distance 11–17 (mean 14.5); shared suffix C/D 10–16; wording diff tokens 1–1
- new AV descriptions: parse_ok 80/80, cjk 0/80, errors 0; 9.8 s/gen; AR forwards 160; AV readout forwards 320
- A/B re-derivation vs c2_acts max(1−cos) 2.22e-16; fresh AR re-score of C2 descriptions: max |M_fact(w1) − file M| 0.00000
- identical descriptions: C=D 0/40; A=C 0/40; B=D 0/40
- entity mentions in the new descriptions (C, D): own 13/80, other 4/80; w2 word mentioned 0/80, w1 word 15/80; C2 (A, B) own-mention was 11/80

## Kill C3-score

- mean [mean(M_fact) − mean(M_wording)]: 0.00782 [-0.00348,0.02407] n=40 clusters=10 → **INCONCLUSIVE** (with the file's M_fact(w1): 0.00782 [-0.00348,0.02407])

| margin | mean [CI by template] | frac > 0 |
|---|---|---|
| M_fact(w1) (C2 pairs, re-scored) | 0.01877 [0.00982,0.03382] | 1.000 |
| M_fact(w2) (new pairs) | 0.01632 [0.00731,0.03058] | 0.975 |
| M_wording(a) | 0.00965 [0.00582,0.01374] | 0.975 |
| M_wording(b) | 0.00980 [0.00543,0.01430] | 0.975 |
| fact − wording (per cell) | 0.00782 [-0.00348,0.02407] | 0.625 |

## Activation distance per edit type

| pair | mean cos | mean 1−cos | min cos | max cos |
|---|---|---|---|---|
| fact edit, w1: cos(h_A,h_B) | 0.9664 | 0.03359 | 0.8215 | 0.9988 |
| fact edit, w2: cos(h_C,h_D) | 0.9688 | 0.03117 | 0.8570 | 0.9993 |
| wording edit, a: cos(h_A,h_C) | 0.9758 | 0.02418 | 0.9142 | 0.9972 |
| wording edit, b: cos(h_B,h_D) | 0.9771 | 0.02289 | 0.9277 | 0.9977 |
| both edits: cos(h_A,h_D) | 0.9494 | 0.05063 | 0.8407 | 0.9946 |
| both edits: cos(h_B,h_C) | 0.9509 | 0.04910 | 0.8315 | 0.9903 |

- activation-distance difference (fact − wording, 1−cos): 0.00884 [-0.00948,0.03447]

## Kill C3-readout (p1 entity readout on all four activations)

- mean [D(h_C) − D(h_D)] (donor sensitivity at w2): 1.7723 [0.7183,3.2194] n=40 → **NOT MET**
- at w1 (T2c contexts re-scored here): 1.7379 [0.6272,3.2762]; max |D − T2c D| = 0.0000
- both-correct rate: w1 0.225, w2 0.200; frac donor>0: w1 0.775, w2 0.875

### 2×2 table of mean D(h) (rows: entity; columns: wording)

| | w1 | w2 |
|---|---|---|
| entity a | +1.2810 (A) | +1.3141 (C) |
| entity b | -0.4569 (B) | -0.4582 (D) |

- entity main effect mean[D(h_A)+D(h_C)]/2 − mean[D(h_B)+D(h_D)]/2: 1.7551 [0.6800,3.2433]
- wording main effect mean[D(h_A)+D(h_B)]/2 − mean[D(h_C)+D(h_D)]/2: -0.0159 [-0.1922,0.1525]
- interaction ½[(D_A − D_B) − (D_C − D_D)]: -0.0172 [-0.1051,0.0686]

## Per-template table

| template | wording | n | M_fact(w1) | M_fact(w2) | M_wording(a) | M_wording(b) | fact−wording | cos(hA,hB) | cos(hA,hC) | donor w1 | donor w2 | both-correct w2 | own-mention C/D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | country→nation (primary) | 4 | 0.0109 | 0.0095 | 0.0160 | 0.0183 | -0.0070 | 0.9682 | 0.9765 | 1.223 | 1.408 | 0.00 | 0.50 |
| 1 | calls→asks (primary) | 4 | 0.0112 | 0.0145 | 0.0075 | 0.0061 | 0.0060 | 0.9630 | 0.9777 | 1.854 | 1.840 | 0.50 | 0.25 |
| 2 | moved→shifted (primary) | 4 | 0.0074 | 0.0015 | 0.0052 | 0.0014 | 0.0011 | 0.9889 | 0.9861 | 0.578 | 0.312 | 0.00 | 0.25 |
| 3 | orchestra→ensemble (primary) | 4 | 0.0097 | 0.0090 | 0.0235 | 0.0190 | -0.0119 | 0.9770 | 0.9421 | -0.029 | -0.451 | 0.00 | 0.00 |
| 4 | pure→solid (primary) | 4 | 0.0143 | 0.0100 | 0.0048 | 0.0057 | 0.0069 | 0.9642 | 0.9829 | 0.404 | 0.638 | 0.25 | 0.00 |
| 5 | story→tale (primary) | 4 | 0.0155 | 0.0125 | 0.0032 | 0.0041 | 0.0104 | 0.9854 | 0.9970 | 7.359 | 7.077 | 0.50 | 0.00 |
| 6 | was→got (primary) | 4 | 0.0197 | 0.0165 | 0.0175 | 0.0172 | 0.0007 | 0.9790 | 0.9576 | 1.145 | 1.230 | 0.00 | 0.12 |
| 7 | worked→served (primary) | 4 | 0.0837 | 0.0780 | 0.0046 | 0.0042 | 0.0765 | 0.8612 | 0.9826 | 3.729 | 3.653 | 0.75 | 0.50 |
| 8 | team's→club's (primary) | 4 | 0.0074 | 0.0047 | 0.0123 | 0.0200 | -0.0101 | 0.9876 | 0.9602 | 0.207 | 0.772 | 0.00 | 0.00 |
| 9 | shows→depicts (primary) | 4 | 0.0079 | 0.0070 | 0.0018 | 0.0020 | 0.0055 | 0.9895 | 0.9956 | 0.910 | 1.242 | 0.00 | 0.00 |

## Full cell table

| pair | tpl | e_a/e_b | w1→w2 | M_fact w1 | M_fact w2 | M_word a | M_word b | cos(hA,hB) | cos(hA,hC) | cos(hB,hD) | D_A | D_B | D_C | D_D | own-mention a/b/c/d |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | Paris/Lyon | country→nation | 0.0021 | 0.0127 | 0.0156 | 0.0143 | 0.9643 | 0.9746 | 0.9809 | +11.17 | +8.72 | +11.80 | +9.54 | True/False/True/False |
| 1 | 0 | Rome/Milan | country→nation | 0.0134 | 0.0103 | 0.0057 | 0.0168 | 0.9675 | 0.9804 | 0.9800 | +3.25 | +3.00 | +3.88 | +2.62 | False/False/True/False |
| 2 | 0 | Madrid/Lisbon | country→nation | 0.0260 | 0.0145 | 0.0193 | 0.0204 | 0.9579 | 0.9739 | 0.9793 | +0.94 | -0.44 | -0.06 | -1.31 | True/False/True/False |
| 3 | 0 | Berlin/Munich | country→nation | 0.0022 | 0.0004 | 0.0235 | 0.0219 | 0.9832 | 0.9770 | 0.9794 | +4.19 | +3.38 | +4.88 | +4.00 | False/False/True/False |
| 4 | 1 | flour/sugar | calls→asks | 0.0073 | 0.0113 | 0.0082 | 0.0049 | 0.9761 | 0.9823 | 0.9789 | -2.47 | -3.53 | -1.78 | -3.34 | False/False/False/True |
| 5 | 1 | rice/milk | calls→asks | 0.0124 | 0.0169 | 0.0110 | 0.0024 | 0.9487 | 0.9767 | 0.9751 | +0.13 | -2.83 | +0.22 | -2.53 | False/False/False/False |
| 6 | 1 | butter/cream | calls→asks | 0.0037 | 0.0112 | 0.0072 | 0.0130 | 0.9698 | 0.9698 | 0.9683 | +2.01 | +1.64 | +1.83 | +1.69 | False/False/False/False |
| 7 | 1 | water/wine | calls→asks | 0.0213 | 0.0186 | 0.0036 | 0.0042 | 0.9577 | 0.9820 | 0.9780 | +1.22 | -1.81 | +1.72 | -1.19 | True/False/True/False |
| 8 | 2 | Monday/Friday | moved→shifted | 0.0008 | 0.0027 | -0.0012 | 0.0038 | 0.9955 | 0.9907 | 0.9926 | +0.69 | +0.69 | +0.72 | +0.69 | False/False/True/False |
| 9 | 2 | Tuesday/Thursday | moved→shifted | 0.0013 | -0.0003 | 0.0008 | 0.0021 | 0.9971 | 0.9858 | 0.9902 | +0.50 | +0.50 | +0.44 | +0.44 | True/False/False/True |
| 10 | 2 | March/April | moved→shifted | 0.0001 | 0.0006 | 0.0024 | -0.0019 | 0.9988 | 0.9865 | 0.9831 | -0.88 | -0.88 | -0.81 | -0.88 | True/False/False/False |
| 11 | 2 | noon/dusk | moved→shifted | 0.0273 | 0.0031 | 0.0190 | 0.0017 | 0.9643 | 0.9815 | 0.9868 | +5.08 | +2.77 | +4.45 | +3.30 | False/False/False/False |
| 12 | 3 | violin/guitar | orchestra→ensemble | 0.0011 | 0.0020 | 0.0273 | 0.0196 | 0.9898 | 0.9360 | 0.9362 | -3.46 | -3.30 | -3.09 | -2.50 | False/False/False/False |
| 13 | 3 | flute/horn | orchestra→ensemble | 0.0019 | 0.0040 | 0.0168 | 0.0107 | 0.9917 | 0.9471 | 0.9549 | +0.97 | +0.80 | +0.25 | +0.88 | False/False/False/False |
| 14 | 3 | piano/drums | orchestra→ensemble | 0.0144 | 0.0042 | 0.0421 | 0.0107 | 0.9734 | 0.9262 | 0.9444 | +3.04 | +2.83 | +3.09 | +3.58 | False/False/False/False |
| 15 | 3 | trumpet/organ | orchestra→ensemble | 0.0214 | 0.0257 | 0.0077 | 0.0350 | 0.9530 | 0.9589 | 0.9277 | -4.41 | -4.07 | -4.82 | -4.73 | False/False/False/False |
| 16 | 4 | gold/iron | pure→solid | 0.0148 | 0.0244 | 0.0115 | 0.0052 | 0.9664 | 0.9799 | 0.9769 | +2.33 | +2.55 | +2.53 | +2.02 | True/False/False/False |
| 17 | 4 | silver/copper | pure→solid | 0.0307 | 0.0107 | 0.0029 | 0.0124 | 0.9429 | 0.9913 | 0.9743 | +1.00 | +0.56 | +0.94 | +0.56 | False/False/False/False |
| 18 | 4 | platinum/bronze | pure→solid | 0.0067 | 0.0039 | 0.0002 | 0.0041 | 0.9648 | 0.9862 | 0.9905 | -0.23 | -1.68 | +0.11 | -1.29 | False/False/False/False |
| 19 | 4 | steel/brass | pure→solid | 0.0049 | 0.0012 | 0.0046 | 0.0009 | 0.9828 | 0.9743 | 0.9938 | -1.99 | -1.95 | -2.02 | -2.28 | False/False/False/False |
| 20 | 5 | London/Tokyo | story→tale | 0.0135 | 0.0129 | 0.0029 | 0.0035 | 0.9845 | 0.9966 | 0.9973 | +3.30 | -6.07 | +2.89 | -5.50 | False/False/False/False |
| 21 | 5 | Moscow/Cairo | story→tale | 0.0261 | 0.0305 | 0.0013 | 0.0008 | 0.9802 | 0.9972 | 0.9976 | +8.51 | -6.44 | +9.42 | -6.51 | False/False/False/False |
| 22 | 5 | Boston/Denver | story→tale | 0.0039 | 0.0007 | 0.0043 | 0.0075 | 0.9950 | 0.9971 | 0.9968 | +0.96 | -0.04 | +1.02 | +0.20 | False/False/False/False |
| 23 | 5 | Sydney/Dublin | story→tale | 0.0187 | 0.0060 | 0.0044 | 0.0048 | 0.9817 | 0.9970 | 0.9977 | -2.25 | -6.36 | -2.47 | -5.64 | False/False/False/False |
| 24 | 6 | asthma/diabetes | was→got | 0.0069 | 0.0064 | 0.0135 | 0.0257 | 0.9892 | 0.9767 | 0.9670 | -2.06 | -2.81 | -2.66 | -3.83 | False/False/False/False |
| 25 | 6 | cancer/arthritis | was→got | 0.0585 | 0.0475 | 0.0122 | 0.0018 | 0.9543 | 0.9753 | 0.9639 | +6.05 | +3.62 | +4.59 | +2.09 | False/False/True/False |
| 26 | 6 | malaria/pneumonia | was→got | 0.0086 | 0.0043 | 0.0206 | 0.0276 | 0.9892 | 0.9643 | 0.9630 | -0.53 | -1.47 | +1.78 | +0.56 | False/False/False/False |
| 27 | 6 | measles/influenza | was→got | 0.0050 | 0.0076 | 0.0237 | 0.0138 | 0.9835 | 0.9142 | 0.9526 | -0.69 | -1.16 | -2.84 | -2.88 | False/False/False/False |
| 28 | 7 | teacher/plumber | worked→served | 0.1178 | 0.1138 | 0.0021 | 0.0036 | 0.8215 | 0.9894 | 0.9849 | +6.42 | -0.77 | +5.45 | -0.92 | True/False/False/False |
| 29 | 7 | lawyer/farmer | worked→served | 0.0838 | 0.0770 | 0.0085 | 0.0038 | 0.8792 | 0.9879 | 0.9882 | +0.06 | -3.41 | +0.19 | -3.09 | True/True/False/True |
| 30 | 7 | nurse/baker | worked→served | 0.0694 | 0.0622 | 0.0027 | 0.0075 | 0.8793 | 0.9936 | 0.9816 | -0.05 | +0.39 | -0.01 | -0.37 | False/False/False/True |
| 31 | 7 | pilot/chef | worked→served | 0.0639 | 0.0589 | 0.0053 | 0.0018 | 0.8647 | 0.9595 | 0.9937 | +2.68 | -2.02 | +1.70 | -2.91 | True/True/True/True |
| 32 | 8 | tiger/dolphin | team's→club's | 0.0076 | 0.0026 | 0.0087 | 0.0248 | 0.9884 | 0.9647 | 0.9610 | -0.35 | -0.77 | -0.31 | -0.99 | False/False/False/False |
| 33 | 8 | bear/eagle | team's→club's | 0.0027 | 0.0030 | 0.0146 | 0.0175 | 0.9889 | 0.9631 | 0.9645 | +0.58 | +0.57 | +1.15 | +0.53 | False/False/False/False |
| 34 | 8 | lion/shark | team's→club's | 0.0090 | 0.0045 | 0.0124 | 0.0176 | 0.9838 | 0.9526 | 0.9686 | -1.00 | -0.79 | +0.88 | +0.56 | False/False/False/False |
| 35 | 8 | wolf/hawk | team's→club's | 0.0103 | 0.0085 | 0.0134 | 0.0198 | 0.9892 | 0.9604 | 0.9557 | -1.51 | -2.12 | -0.87 | -2.35 | False/False/False/False |
| 36 | 9 | river/castle | shows→depicts | 0.0147 | 0.0104 | 0.0023 | 0.0049 | 0.9836 | 0.9948 | 0.9938 | -0.34 | -1.66 | -0.31 | -1.94 | False/False/False/False |
| 37 | 9 | bridge/forest | shows→depicts | 0.0041 | 0.0042 | 0.0024 | 0.0006 | 0.9932 | 0.9954 | 0.9960 | +2.66 | +2.44 | +2.19 | +1.91 | False/False/False/False |
| 38 | 9 | garden/desert | shows→depicts | 0.0082 | 0.0113 | 0.0011 | 0.0018 | 0.9898 | 0.9971 | 0.9946 | +3.81 | +2.34 | +4.03 | +2.09 | False/False/False/False |
| 39 | 9 | mountain/village | shows→depicts | 0.0045 | 0.0019 | 0.0013 | 0.0005 | 0.9915 | 0.9950 | 0.9948 | +1.92 | +1.28 | +2.50 | +1.38 | False/False/False/False |

## Three verbatim cells

### pair 0 (template 0): Paris / Lyon; country → nation; M_fact(w1)=0.0021 M_fact(w2)=0.0127 M_wording(a)=0.0156 M_wording(b)=0.0143
- context_a: The capital of the country is Paris. Tourists arrive at the main station and walk to the
- d_a (mentions own=True, other=False): Formal mathematical/structural description pattern with a numbered sequence ("A train from Moscow to Paris with a probability"), implying a scenario about a tourist arriving at a metro station.

The phrase "A person leaves the train station with a random time to the Eiffel Tower and goes to the metro center" strongly implies a destination or attraction description, suggesting the sentence structure continues describing the route or destination's location.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), directly continuing "a person goes from the metro to the," requiring a noun like "central station" or "hotel, or the clock tower" or "station, with a probability distribution."
- context_b: The capital of the country is Lyon. Tourists arrive at the main station and walk to the
- d_b (mentions own=False, other=False): Formal mathematical/urban description format with a translated phrase ("A random walk in the city"), implying a puzzle or event context about a metro station.

The sentence structure "A person leaves from a random station in the center of the city and goes to the metro station, then decides whether to go to the" suggests a paired noun phrase describing destination or attraction location about the city's main square.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), continuing the parallel structure "a random walk to the metro station and to the," strongly expecting a noun like "main square" or "hotel entrance" or "bus stop, with a certain probability."
- context_c: The capital of the nation is Paris. Tourists arrive at the main station and walk to the
- d_c (mentions own=True, other=False): Formal mathematical/linguistic description format with a travel context suggesting a numbered sequence or interactive scenario about a metro station in Paris.

The phrase "A person leaves from a random station in Paris and walks to the Eiffel Tower, then decides to go to the metro" implies a sentence structure describing a destination and journey, likely implying a clock or schedule event about the museum's location.

Final token "the" is an incomplete noun phrase mid-sentence ("from the train to the museum and goes to the"), directly requiring a noun like "central museum" or "clock tower" or "entrance hall," continuing the parallel structure describing attendees' destination or attraction.
- context_d: The capital of the nation is Lyon. Tourists arrive at the main station and walk to the
- d_d (mentions own=False, other=False): Formal descriptive/mathematical context with a travel/urban setting, suggesting a puzzle or interactive app format with numbered directions.

The phrase "A person starts from the train station in the city center and walks to the metro station, then decides to go to the tourist attraction" implies a sentence structure describing two destinations or a destination's characteristics, likely a noun phrase about the city's main square or museum.

Final token "the" is an article mid-phrase ("from the train station to the"), part of a parallel structure ("people walk from the clock to the destination and to the"), expecting a noun like "central square" or "entrance hall" or "bus schedule."

### pair 18 (template 4): platinum / bronze; pure → solid; M_fact(w1)=0.0067 M_fact(w2)=0.0039 M_wording(a)=0.0002 M_wording(b)=0.0041
- context_a: The ring was made of pure platinum. The jeweller placed it carefully in a small box on the
- d_a (mentions own=False, other=False): Narrative context: a British English-language story with a quirky wildlife photograph, implying a dialogue or scene about a gemstone jeweler's display.

The phrase "The trembling detective held the diamond and other specimens on a white cloth on the" suggests a descriptive clause about a shop's display or tray, continuing a scene-setting phrase about a mysterious gift being handed to a client.

Final token "the" is an article mid-phrase ("on the shelf on the"), part of an incomplete noun phrase describing a receipt or tray location ("A specimen with a diamond and other items was placed on the shelf on the"), expecting a noun like "floor" or "client's desk" or "box."
- context_b: The ring was made of pure bronze. The jeweller placed it carefully in a small box on the
- d_b (mentions own=False, other=False): Narrative context: a short story or descriptive prose about a cat, with a mysterious gemstone being shown to a customer.

The phrase "The little bird flew the specimen of the precious stone onto the counter of the cabinet on the" suggests a dialogue setup or scene description, implying a shopkeeper's display or inventory tray, continuing a list of items.

Final token "the" is an incomplete noun phrase mid-sentence ("placed on the shelf on the... on the"), part of a quoted description clause ("A trembling spider with a letter and some papers he placed on the shelf on the"), strongly expecting "floor" or "customer's desk" or "box, waiting."
- context_c: The ring was made of solid platinum. The jeweller placed it carefully in a small box on the
- d_c (mentions own=False, other=False): Narrative context: a short story or descriptive prose about a diamond ring, implying a British English scene with a detective or jewelry seller.

The sentence structure "The little bird held the specimen on a white cloth on the counter, he placed the mysterious object on the" suggests a dialogue or display scenario, with a specific phrase about a receipt or box being shown to a customer.

Final token "the" is an article mid-phrase ("on the shelf on the"), part of an incomplete noun phrase describing a location ("A small box with the specimen and other items was placed on the desk on the"), expecting a noun like "floor" or "customer's desk" or "bottom of the box."
- context_d: The ring was made of solid bronze. The jeweller placed it carefully in a small box on the
- d_d (mentions own=False, other=False): Narrative momentum: a descriptive English-language story about a gemstone seller, implying a quirky or dramatic scene with a cat figure.

The phrase "The detective picked up the specimen from the microscope and placed it on a white cloth on the counter of the shop" suggests a dialogue or inventory scene setup, with "a note and a box of remedies" implying a customer's receipt or display.

Final token "the" is an incomplete noun phrase mid-sentence ("on the desk on the"), part of a quoted description clause ("He placed a specimen and some items on the desk on the"), expecting a noun like "floor" or "customer's desk" or "bottom of his box."

### pair 36 (template 9): river / castle; shows → depicts; M_fact(w1)=0.0147 M_fact(w2)=0.0104 M_wording(a)=0.0023 M_wording(b)=0.0049
- context_a: The painting shows a river under a clear sky. Visitors to the gallery often stop in front of it and
- d_a (mentions own=False, other=False): European language description with literary/educational tone, suggesting a museum exhibit or art piece about a tree, implying an observation or contemplative experience.

The sentence structure "Some visitors often stop before this fountain and many people stand still and" strongly implies a common reaction or activity pattern, likely continuing with "take time to observe" or "are fascinated by the artwork," establishing the scene.

Final token "and" is a conjunction mid-clause ("visitors often stop by the fountain and many people stop and"), part of an incomplete clause describing observer behavior, immediately expecting a verb like "enjoy the silence" or "write notes," or "often linger for a long time."
- context_b: The painting shows a castle under a clear sky. Visitors to the gallery often stop in front of it and
- d_b (mentions own=False, other=False): European museum exhibition text with formal descriptive tone, suggesting a literary or art book context about a sculpture.

The sentence structure "Some visitors often stop in front of this painting and many people stand still and" implies an observed behavior pattern or invitation, likely continuing with a clause describing visitors' reactions or interest in the artwork, completing the introductory setup about the sculpture's appealing qualities.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop to look at the exhibition and"), strongly expecting a verb phrase like "take notes" or "are fascinated by its" or "often spend time discussing," continuing the observational description of visitor behavior.
- context_c: The painting depicts a river under a clear sky. Visitors to the gallery often stop in front of it and
- d_c (mentions own=False, other=False): Formal literary description with a bilingual context, suggesting an exhibition or art piece about trees, inviting readers to observe a particular sculpture.

The sentence structure "Some visitors often stop before this fountain and many people stand quietly and" implies an observed behavior pattern or anecdote, strongly implying a clause describing what visitors do or feel about the artwork's peaceful atmosphere or beauty.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop by the exhibition and"), part of an incomplete clause structure ("People often visit these sculptures and many people often stop and"), expecting a verb like "take notes" or "are fascinated by the scene," or "linger."
- context_d: The painting depicts a castle under a clear sky. Visitors to the gallery often stop in front of it and
- d_d (mentions own=False, other=False): Bulgarian language text with literary/artistic context, suggesting a museum or exhibition description format about a sculpture.

The sentence structure "Some visitors often stop in front of this painting and many people stand still and" implies an expected continuation describing viewer behavior or reaction, likely a common activity or observation about the artwork's beauty or mystery, continuing the introductory clause.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop to observe the paintings and"), strongly expecting a verb phrase like "take notes" or "are fascinated by its details" or "often discuss," completing the observation clause about people's reactions to the artwork.


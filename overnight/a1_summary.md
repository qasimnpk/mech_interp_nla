# A1 summary — natural AV claims, paraphrase-averaged semantic preference (claude labels)

git 321485a3; settings in a1_settings.json; progress in a1_progress.json; cut rules A1(a)(b)(c) applied (V0)

## Kill tests

- 2026-09-09T02:53:44  A1  A1  threshold=CI95 (cluster by context, eval) of mean G = μ_correct − mean_false μ_m over valid paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval slots < 30 → INCONCLUSIVE  observed=mean G=0.00319 [-0.00035,0.00674] n=4 k=4 (eligible eval slots in primary 4 of 39 eval slots; 33 eligible); correct-ranks-first 0.500 [0.000,1.000] n=4 k=4; frac comparisons won 0.625 [0.250,1.000] n=4 k=4; G orig-only 0.00300 [-0.00025,0.00626] n=4 k=4; by category (μ_correct − μ_false): detail_sub 0.00298 [-0.00115,0.00710] n=4 k=4; entity_sub 0.00196 [-0.00014,0.00499] n=3 k=3  INCONCLUSIVE  MET/INCONCLUSIVE = no detectable preference for the correct meaning under this scorer with this n (never 'the information is absent')  (already appended by the first analysis run; not duplicated)
- 2026-09-09T02:53:44  A1  A1-nat  threshold=CI95 (by context, eval) of mean [μ_correction − μ_original] on natural-error slots ≤ 0 → MET; > 0 → NOT MET; straddles or natural-error eval slots < 15 → INCONCLUSIVE (count reported; injected errors never substituted)  observed=mean [μ_correction − μ_original]=0.00113 [-0.00176,0.00465] n=4 k=4 (natural-error eval slots 4; contradicted eval originals 37; valid corrections 7 of 46); orig-only 0.00102 [-0.00145,0.00369] n=4 k=4  INCONCLUSIVE  MET/INCONCLUSIVE = the scorer does not detectably prefer the corrected version of the AV's own errors at this n  (already appended by the first analysis run; not duplicated)

## Counts

- contexts 40 (dev 10, eval 30); generations 40 (parse_ok 40, cjk 5, errors 0)
- slots 54 (entity 37, detail 17); contexts with 0/1/2 slots: 1:20, 2:17; contexts without any slot 3
- slot_verify asserts yes 50 / no 4; ineligible: {"no_claim": 4, "fact_repeated": 2, "original_undetermined": 1}
- label_orig: {"contradicted": 51, "entailed": 2, "undetermined": 1}; evidence_found rate 0.98
- eligible slots 47; in primary 8 (eval 4, dev 4); primary exclusions {"no_valid_correction": 39}
- candidates 218 by category {"detail_sub": 47, "relation_rev": 47, "original_contradicted": 46, "correction": 46, "entity_sub": 31, "correct_original": 1}; by role {"false": 69, "natural_error_original": 46, "invalid_correction": 39, "dropped_NONE": 28, "false_edit_rejected": 17, "false_duplicate": 10, "correct": 8, "false_descriptive": 1}
- natural-error slots (contradicted original with a valid correction and paraphrases): 7 (eval 4)
- realizations 419; paraphrases 248; invalid (equiv No) by transform {"light1": 0, "aggr1": 0}; detected duplicates 0

## (B) Primary: correct-meaning preference (eval, in-primary slots; cluster by context)

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

### By corruption category (eval; μ_correct − μ_false per (slot, false meaning); cluster by context)

| category | n | mean diff | CI lo | CI hi | frac won | diff orig-only |
|---|---|---|---|---|---|---|
| detail_sub | 4 | 0.00298 | -0.00115 | 0.00710 | 0.500 [0.000,1.000] | 0.00279 [-0.00081,0.00639] |
| entity_sub | 3 | 0.00196 | -0.00014 | 0.00499 | 0.667 [0.000,1.000] | 0.00161 [0.00030,0.00421] |

## (C) Natural errors (eval; μ_correction − μ_original; cluster by context)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| μ_correction − μ_original | 0.00113 | -0.00176 | 0.00465 | 4 | 4 |
| orig-only | 0.00102 | -0.00145 | 0.00369 | 4 | 4 |
| frac correction > original | 0.500 | 0.000 | 1.000 | 4 | 4 |

## (A) Paraphrase sensitivity (eval, valid paraphrases; cluster by context)

| group × truth | n | mean abs Δ | CI lo | CI hi | signed Δ mean | signed CI |
|---|---|---|---|---|---|---|
| light × entailed | 4 | 0.00103 | 0.00071 | 0.00124 | -0.00075 | [-0.00124,0.00012] |
| light × contradicted | 83 | 0.00130 | 0.00071 | 0.00221 | -0.00084 | [-0.00182,-0.00016] |
| aggressive × entailed | 4 | 0.00564 | 0.00362 | 0.00767 | -0.00180 | [-0.00662,0.00484] |
| aggressive × contradicted | 83 | 0.00426 | 0.00298 | 0.00586 | 0.00054 | [-0.00166,0.00271] |
| all × entailed | 8 | 0.00334 | 0.00237 | 0.00430 | -0.00128 | [-0.00393,0.00248] |
| all × contradicted | 166 | 0.00278 | 0.00202 | 0.00381 | -0.00015 | [-0.00137,0.00094] |

P_correct − P_false within slot (paired, cluster by context): -0.00005 [-0.00086,0.00042] n=4 k=4

## 2×2 blocks (eval, valid paraphrases in in-primary and natural-error slots; truth entailed / contradicted × slot type entity / detail)

### μ (cos of valid paraphrases)

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

### P: |Δ| vs orig

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

### P: signed Δ vs orig

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

### V (reconstruction movement vs orig wording)

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

### G by slot type (eval, in-primary)

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| G / entity | 0.00319 | -0.00035 | 0.00674 | 4 | 4 |
| G / detail | nan | nan | nan | 0 | 0 |

## (D) Deletion and movement

| statistic | mean | CI lo | CI hi | n | clusters |
|---|---|---|---|---|---|
| deletion Δ = cos(deletion) − cos(carrier), eligible eval slots | -0.03226 | -0.03940 | -0.02510 | 33 | 26 |
| V, light1 (eval, valid) | 0.00028 | 0.00016 | 0.00051 | 88 | 26 |
| V, aggr1 (eval, valid) | 0.00304 | 0.00212 | 0.00423 | 88 | 26 |

- s(h, own explanation): mean 0.88058 over 37 contexts with slots

## Lexical checks (advisory; agreement with equiv)

| transform | n | equiv Yes | names_kept | numbers_kept | polarity_kept | len_ok | all four & Yes | all four & No |
|---|---|---|---|---|---|---|---|---|
| light1 | 124 | 124 | 1.00 | 1.00 | 1.00 | 1.00 | 124 | 0 |
| aggr1 | 124 | 124 | 1.00 | 1.00 | 1.00 | 0.92 | 114 | 0 |

## Distributions

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

## 5 fixed verbatim examples (seed 0; eval in-primary slots)

### c37_entity (context 37, entity, focus 'Dickensian', label_orig contradicted)

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

### c36_entity (context 36, entity, focus 'Hopeful', label_orig contradicted)

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

### c10_entity (context 10, entity, focus 'Americas', label_orig contradicted)

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

### c22_entity (context 22, entity, focus 'American', label_orig contradicted)

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

# R1 summary — fact-blindness locus: target layer-20 representation vs reconstructor (490 accepted S3 triples, all evaluation set)

git df75b0a7; settings in r1_settings.json

- triples: 490; with corrupt_det: 402; explanations: 160; distinct texts scored: 1860
- claim length (TARGET tokens): mean 40.7, min 4, max 67

## 2x2 table: mean d = 1 − cos (cluster-bootstrap CI95 by explanation)

| side | d_corr (c vs c*) | d_para (c vs c~) | S = d_corr − d_para | outcome(CI≤0) | ratio of means d_corr/d_para | median item ratio | frac d_corr > d_para |
|---|---|---|---|---|---|---|---|
| TARGET last token | 0.03952 [0.03112, 0.04722] (n=490) | 0.13357 [0.12455, 0.14228] (n=490) | -0.09405 [-0.10376, -0.08445] (n=490) | MET | 0.2959 | 0.0873 | 0.0816 [0.0573, 0.1065] (n=490) |
| TARGET mean over tokens | 0.00013 [0.00012, 0.00015] (n=490) | 0.00134 [0.00128, 0.00140] (n=490) | -0.00121 [-0.00127, -0.00115] (n=490) | MET | 0.0979 | 0.0662 | 0.0061 [0.0000, 0.0142] (n=490) |
| AR (value head) | 0.02167 [0.01793, 0.02554] (n=490) | 0.07113 [0.06517, 0.07745] (n=490) | -0.04945 [-0.05569, -0.04328] (n=490) | MET | 0.3047 | 0.1834 | 0.1286 [0.0990, 0.1585] (n=490) |

## Deterministic corruption (corrupt_det; number/name swap) where present

| side | d_det (c vs c_det) | S_det = d_det − d_para | ratio of means d_det/d_para |
|---|---|---|---|
| TARGET last token | 0.01914 [0.01523, 0.02330] (n=402) | -0.11349 [-0.12281, -0.10393] (n=402) | 0.1443 |
| TARGET mean over tokens | 0.00027 [0.00025, 0.00030] (n=402) | -0.00111 [-0.00118, -0.00104] (n=402) | 0.1967 |
| AR (value head) | 0.02096 [0.01795, 0.02467] (n=402) | -0.04915 [-0.05655, -0.04227] (n=402) | 0.2990 |

## Cross-side agreement (Spearman, per triple)

- rho(d_corr_T_last, d_corr_AR) = 0.4643 (p=1.43e-27)
- rho(d_para_T_last, d_para_AR) = 0.1061 (p=0.0188)
- rho(S_T_last, S_AR) = -0.0098 (p=0.828)

## Distributions (evaluation triples)

| quantity | mean | median | p10 | p90 |
|---|---|---|---|---|
| d_corr_T_last | 0.03952 | 0.00945 | 0.00161 | 0.09101 |
| d_para_T_last | 0.13357 | 0.10949 | 0.04898 | 0.25252 |
| d_det_T_last | 0.01914 | 0.00873 | 0.00149 | 0.03581 |
| d_corr_T_mean | 0.00013 | 0.00008 | 0.00002 | 0.00028 |
| d_para_T_mean | 0.00134 | 0.00121 | 0.00051 | 0.00231 |
| d_det_T_mean | 0.00027 | 0.00021 | 0.00003 | 0.00062 |
| d_corr_AR | 0.02167 | 0.00791 | 0.00158 | 0.05189 |
| d_para_AR | 0.07113 | 0.04749 | 0.00817 | 0.17274 |
| d_det_AR | 0.02096 | 0.00883 | 0.00101 | 0.05336 |

## Kill test

- 2026-09-06T09:17:55  R1  R1  threshold=CI95 of mean(d_corr_T − d_para_T), last-token, n>=300, ≤ 0  observed=mean d_corr_T=0.03952 [0.03112,0.04722]; mean d_para_T=0.13357 [0.12455,0.14228]; mean S_T=-0.09405 CI95=[-0.10376,-0.08445] n=490 n_expl=160  MET  MET would mean the target's own layer-20 representation of the claim text is no more sensitive to the factual change than to rewording (blindness upstream of the AR)

## 10 fixed S3 example rows (verbatim) with their four d values

### accepted #0 (row 133, stim 40, claim 0/4)
- original:   Wikipedia-style chemistry article structure with numbered sections listing properties of europium, presenting factual data about the element's atomic and physical characteristics.
- corrupted:  Wikipedia-style chemistry article structure with numbered sections listing properties of lead, presenting factual data about the element's atomic and physical characteristics.
- paraphrase: Europium's properties detailed in a numbered sections Wikipedia-style chemistry article, encompassing factual data on its atomic and physical attributes.
- corrupt_det: nan
- d_corr_T=0.00726  d_para_T=0.06526  d_corr_AR=0.02456  d_para_AR=0.04535  (mean-pooled: d_corr_T_mean=0.00009 d_para_T_mean=0.00163; det: d_det_T=nan d_det_AR=nan)

### accepted #16 (row 150, stim 44, claim 0/3)
- original:   Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a gangster's actions.
- corrupted:  Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a puppy's actions.
- paraphrase: A comic book description focusing on character traits and dialogue, including a particular scene that outlines a gangster's activities.
- corrupt_det: nan
- d_corr_T=0.02371  d_para_T=0.07726  d_corr_AR=0.02672  d_para_AR=0.14714  (mean-pooled: d_corr_T_mean=0.00008 d_para_T_mean=0.00139; det: d_det_T=nan d_det_AR=nan)

### accepted #32 (row 167, stim 49, claim 0/3)
- original:   Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of TV show details about a fictional detective series.
- corrupted:  Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of video game details about a fictional detective series.
- paraphrase: A wiki article structured with metadata fields preceding the film description, setting a standard for TV show details on a fictional detective series.
- corrupt_det: Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of The show details about a fictional detective series.
- d_corr_T=0.00910  d_para_T=0.07346  d_corr_AR=0.01621  d_para_AR=0.04372  (mean-pooled: d_corr_T_mean=0.00006 d_para_T_mean=0.00120; det: d_det_T=0.17420 d_det_AR=0.05173)

### accepted #48 (row 184, stim 54, claim 1/3)
- original:   The sentence "Another biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- corrupted:  The sentence "Another biographer was Jack Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- paraphrase: The sentence "John Carter was another biographer" introduces a named source or figure, probably a secondary account or personal detail about the soldier's life, indicating a particular person or event linked to his fame or death.
- corrupt_det: The sentence "Initially biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- d_corr_T=0.00296  d_para_T=0.04357  d_corr_AR=0.01964  d_para_AR=0.10252  (mean-pooled: d_corr_T_mean=0.00008 d_para_T_mean=0.00072; det: d_det_T=0.01866 d_det_AR=0.04621)

### accepted #64 (row 201, stim 59, claim 0/3)
- original:   American military article format with numbered statistics detailing a Florida county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- corrupted:  American military article format with numbered statistics detailing a Antarctica county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- paraphrase: American military-style article, featuring numbered statistics about a Florida county's infrastructure, presented in organized bullet points and complete with citations.
- corrupt_det: American military article format with numbered statistics detailing a However county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- d_corr_T=0.00603  d_para_T=0.06098  d_corr_AR=0.02003  d_para_AR=0.18822  (mean-pooled: d_corr_T_mean=0.00011 d_para_T_mean=0.00092; det: d_det_T=0.03583 d_det_AR=0.04227)

### accepted #80 (row 218, stim 64, claim 0/3)
- original:   British historical biography article detailing parliamentary politics of Charles I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- corrupted:  British historical biography article detailing parliamentary politics of Charles II, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- paraphrase: Article on British historical biography focusing on Charles I's parliamentary politics, systematically outlining parliamentary opposition and constitutional crisis through numbered sections and a chronological narrative.
- corrupt_det: British historical biography article detailing parliamentary politics of War I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- d_corr_T=0.00322  d_para_T=0.02767  d_corr_AR=0.00218  d_para_AR=0.02889  (mean-pooled: d_corr_T_mean=0.00004 d_para_T_mean=0.00073; det: d_det_T=0.01745 d_det_AR=0.01828)

### accepted #96 (row 239, stim 69, claim 3/4)
- original:   " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- corrupted:  " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Sino-Tibetan languages' variant counts."
- paraphrase: closes a third entry in an analogous list ("While the latter encompasses the Turkish language with its complete written form and the Greek language with abbreviated characters..."), anticipating either "The written form of the last language is..." or "The variants of Slavic dialects count."
- corrupt_det: " closes a third item in a parallel list ("Black the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- d_corr_T=0.01493  d_para_T=0.13111  d_corr_AR=0.00890  d_para_AR=0.09778  (mean-pooled: d_corr_T_mean=0.00021 d_para_T_mean=0.00164; det: d_det_T=0.00562 d_det_AR=0.01392)

### accepted #112 (row 258, stim 74, claim 0/3)
- original:   British music article format with Wikipedia-style entry structure detailing an album by Scottish rock band Feeder, listing discography and chart performance.
- corrupted:  British music article format with Wikipedia-style entry structure detailing an album by English rock band Feeder, listing discography and chart performance.
- paraphrase: An article in the style of a British music Wikipedia entry, providing details on an album by the Scottish rock band Feeder, including discography and chart performance.
- corrupt_det: British music article format with Wikipedia-style entry structure detailing an album by Imagine rock band Feeder, listing discography and chart performance.
- d_corr_T=0.00087  d_para_T=0.12190  d_corr_AR=0.00148  d_para_AR=0.01523  (mean-pooled: d_corr_T_mean=0.00002 d_para_T_mean=0.00150; det: d_det_T=0.00608 d_det_AR=0.00327)

### accepted #128 (row 275, stim 79, claim 2/3)
- original:   Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- corrupted:  Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "Bob" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- paraphrase: The concluding token "as" signals an unfinished noun phrase ("also known as"), which is part of a name attribution clause ("known as Darren Aronofsky, also known as"), with a strong anticipation for "DA," "Arno," "Aronofsky," or "DAF" to finalize the nickname or abbreviated identity.
- corrupt_det: Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as AI Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- d_corr_T=0.01687  d_para_T=0.24649  d_corr_AR=0.00266  d_para_AR=0.01845  (mean-pooled: d_corr_T_mean=0.00025 d_para_T_mean=0.00387; det: d_det_T=0.01495 d_det_AR=0.09317)

### accepted #144 (row 292, stim 85, claim 1/3)
- original:   The sentence structure "While some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- corrupted:  The sentence structure "While some songs were originally intended for the compilation album, several artists chose to include all tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- paraphrase: The sentence structure "Although some songs were planned for the compilation album, various artists decided against including particular tracks in the ultimate tracklist" outlines a pattern of detailing exclusions, suggesting the definitive answer regarding the initial album's contents.
- corrupt_det: The sentence structure "Dutch some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- d_corr_T=0.00314  d_para_T=0.05588  d_corr_AR=0.03337  d_para_AR=0.04824  (mean-pooled: d_corr_T_mean=0.00023 d_para_T_mean=0.00054; det: d_det_T=0.00505 d_det_AR=0.04891)

## Timings

- target_load_s: 5.83
- target_forward_s: 286.55
- target_n_forward: 1860
- rss_after_target_free_G: 0.71
- ar_load_s: 4.13
- ar_forward_s: 222.87
- ar_n_forward: 1860

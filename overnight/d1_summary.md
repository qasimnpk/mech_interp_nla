# D1 summary — claim-direction ablation with the reconstructor as encoder (greedy, α = 0.3)

git 0cb31fef; settings in d1_settings.json; progress in d1_progress.json

## Kill test

- 2026-09-09T10:32:24  D1  D1  threshold=CI95 (cluster by explanation) of [persist_word(random) − persist_word(own)] on non-last rows (n ≤ 120) ≤ 0 → MET; > 0 → NOT MET; straddles or < 60 rows completed → INCONCLUSIVE  observed=non-last pooled: n=91 persist_word own 0.495 random 0.703 diff 0.2088 [0.1111,0.3111] n=91 k=73; persist_claim own 0.236 random 0.345 diff 0.1094 [0.0806,0.1378] n=91 k=73; format-break own 0.000 random 0.000; nonlast_in_prefix: n=46 persist_word own 0.696 random 0.848 diff 0.1522 [0.0217,0.2889] n=46 k=41; persist_claim own 0.258 random 0.354 diff 0.0956 [0.0478,0.1377] n=46 k=41; format-break own 0.000 random 0.000; nonlast_not_in_prefix: n=45 persist_word own 0.289 random 0.556 diff 0.2667 [0.1304,0.4222] n=45 k=43; persist_claim own 0.213 random 0.337 diff 0.1234 [0.0885,0.1636] n=45 k=43; format-break own 0.000 random 0.000; positive_control_last: n=20 persist_word own 0.550 random 0.800 diff 0.2500 [0.0500,0.4500] n=20 k=20; persist_claim own 0.409 random 0.514 diff 0.1052 [0.0633,0.1526] n=20 k=20; format-break own 0.000 random 0.000; positive control quoted_token_ok own 0.800 random 0.900 reference 0.850; rows completed 111/140  NOT MET  concerns the AV's output under a vector edit only; MET/INCONCLUSIVE with the positive control NOT MET = the AV re-asserts from remaining content or the AR direction is not what the AV reads

## Format-break rate first

- own: parse_ok 1.000, cjk 0.000, format-break 0.000; random: parse_ok 1.000, cjk 0.000, format-break 0.000 (n=111)
- rows sampled 140 ({"nonlast_in_prefix": 60, "nonlast_not_in_prefix": 60, "positive_control_last": 20}); completed 111; reference persist_word 1.000; reference quoted_token_ok on last rows 0.850

## Per stratum (paired random − own, cluster by explanation)

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

## 2×2 (non-last rows): in_full_prefix × slot type — persist_word own / random / diff

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

## Distributions

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

## 5 fixed verbatim examples (seed 0; completed non-last rows)

### row 380 (stim 110, nonlast_in_prefix, entity, word_orig '"Proteins')

- claim: 'The phrase "Proteins can undergo modification, folding, regulation, activity" is mid-listing a series of attributes of enzymes or proteins, following a familiar compound noun pattern from biology definitions about protein characteristics.'
- original explanation: 'Wikipedia article structure with formal definition format, listing biological terms ("Protein") with a standardized encyclopedia pattern describing protein\'s properties and functions.\n\nThe phrase "Proteins can undergo modification, folding, regulation, activity" is mid-listing a series of attributes of enzymes or proteins, following a familiar compound noun pattern from biology definitions about protein characteristics.\n\nFinal token "activity" ends an incomplete list ("the structure, activity, activity"), part of a comma-separated enumeration of attributes ("such as its structure, function, activity, activity..."), strongly expecting continuation like "or lifespan," "of the protein," or "and other properties," completing the compound noun phrase.'
- own ablation (‖d_c‖ 34.714, proj 0.2028, cos(h',h) 0.9544): persist_word 1.0, persist_claim 0.227: 'Wikipedia article structure with formal definition format, listing biological definitions of proteins using a standardized template ("In biology, a protein is...").\n\nThe phrase "A protein\'s characteristics include its chemical structure, function, location, stability, activity" follows a list of attributes of a protein, completing a standard definition clause about a protein\'s properties or role.\n\nFinal token "activity" ends mid-list within "its activity, activity, activity" — part of a comma-separated enumeration of attributes ("such as its structure, function, activity, activity"), strongly expecting "or other properties" or "and other properties," or "of the protein, or its function" to close.'
- random ablation (partner row 596, cos(h',h) 0.9613): persist_word 0.0, persist_claim 0.279: 'Structured Wikipedia-style article format with numbered definitions and scientific context, following a pattern of chemical terms with "Protein" definition expanding into biological functions.\n\nThe phrase "Protein folding refers to the process of converting a protein\'s structure, function, activity" is mid-listing a series of attributes ("such as shape, stability, activity"), implying continuation of a comma-separated list of protein characteristics.\n\nFinal token "activity" ends an incomplete list item ("activity, activity"), part of a parallel noun series ("such as its structure, function, activity, activity"), strongly expecting continuation like "or other properties," "of the protein," or "and other properties, and its role."'

### row 408 (stim 119, nonlast_not_in_prefix, entity, word_orig 'Beirut,')

- claim: 'The phrase "known officially as Beirut, locally" suggests a compound noun or nickname phrase ("known locally"), implying a second name or designation follows, likely describing the city\'s status or nickname, completing a phrase about the municipality\'s identity.'
- original explanation: 'Formal Wikipedia-style article structure with English-language descriptive prose about a Palestinian city, establishing factual context about Beirut, Lebanon\'s capital.\n\nThe phrase "known officially as Beirut, locally" suggests a compound noun or nickname phrase ("known locally"), implying a second name or designation follows, likely describing the city\'s status or nickname, completing a phrase about the municipality\'s identity.\n\nFinal token "locally" ends an incomplete phrase ("known locally"), part of a list or descriptive clause ("Known locally..."), strongly expecting "as Beirût" or "as the \'City of Beirut\'" or "and colloquially as" or "as a municipality," continuing the naming context.'
- own ablation (‖d_c‖ 29.418, proj 0.3084, cos(h',h) 0.9539): persist_word 0.0, persist_claim 0.279: 'Wikipedia article format with structured encyclopedia entry on Bahrain, describing a country\'s capital city, with formal descriptive prose about the city\'s geography and history.\n\nThe phrase "Known officially as Manama, the city is locally known" signals a list of aliases or local names, following a common pattern of "locally known as" or "as the capital," likely continuing with demographic context.\n\nFinal token "locally" ends mid-phrase ("Known locally"), part of a noun phrase describing the city\'s name and nickname ("Known locally"), immediately expecting "as Manama" or "in Arabic as \'al-Manama\'" or "as a city, it is known for...".'
- random ablation (partner row 392, cos(h',h) 0.9589): persist_word 0.0, persist_claim 0.361: 'Formal Wikipedia-style entry structure with English language description of a country, implying a noun phrase about "Cairo" or a Palestinian territory.\n\nThe phrase "officially known as the Gaza Strip, locally known locally" suggests a list or phrase completing a compound noun or descriptor, strongly implying "as Gaza City" or "also known as" or "by its residents."\n\nFinal token "locally" ends an incomplete phrase ("known locally"), part of a noun phrase listing attributes ("Known formally as Gaza Strip and locally"), strongly expecting "as" or "as the city" or "and commonly referred to as" or "as a \'local\' name," completing the regional identity context.'

### row 229 (stim 67, nonlast_in_prefix, entity, word_orig '"Its')

- claim: 'The sentence structure "Its taxonomic classification includes multiple names and definitions, with the species being named after the genus \'Lithobates\' and related terms.'
- original explanation: 'Wiki article format with structured taxonomic entries describing a biological species, listing scientific names and historical classifications with chronological progression.\n\nThe sentence structure "Its taxonomic classification includes multiple names and definitions, with the species being named after the genus \'Lithobates\' and related terms. Its taxonomic history dates back..." implies a second clause continuing the taxonomic history or synonym list.\n\nFinal token "1" is mid-number in "it does not publish multiple taxonomic names or classifications... This taxon\'s taxonomic history begins with the following classification..." — expects "s" or " The following is..." or "s the name has been reclassified" completing the enumeration.'
- own ablation (‖d_c‖ 25.449, proj 0.1363, cos(h',h) 0.9552): persist_word 1.0, persist_claim 0.167: 'Taxonomic species page format with structured biological data fields (Latin name, synonyms, etymology, classification), suggesting a phylogenetic history section follows.\n\nThe phrase "Its taxonomic history includes the following classifications : ... The genus was first described in 1855" implies a list continuation or chronological revision history, with "Other taxonomic synonyms" signaling a second taxonomic revision.\n\nFinal token "1" is mid-number in "it does not publish the following taxonomic revisions : " — part of a closing taxonomic revision clause, strongly expecting "s" or "... The following classification" or "s, including..." completing the historical taxonomic lineage.'
- random ablation (partner row 665, cos(h',h) 0.9615): persist_word 1.0, persist_claim 0.560: 'Structured taxonomic entry format with numbered definitions and etymology sections describing a biological species, listing scientific names and taxonomic history.\n\nThe sentence "Its taxonomic classification includes multiple names and classifications, with the species being assigned to the genus *Lithobates* and related genera. Its evolutionary history is traced..." implies a concluding clause about taxonomic relationships or synonymy, completing the enumeration.\n\nFinal token "2016." closes a parenthetical clause ("Its taxonomic name history dates from... The following taxonomic classification... This species has multiple definitions..."), strongly expecting "s the following" or "...the name has been..." or "s other related classifications."'

### row 234 (stim 68, nonlast_in_prefix, entity, word_orig '"The')

- claim: 'The phrase "The Aggie Marching Band\'s roar was heard as \'Hail Aggi" suggests a proper noun or nickname ("The Aggie Spirit"), likely referencing the university\'s mascot or a specific event name with a historical figure.'
- original explanation: 'Historical sports reference format with a college football tradition, establishing a factual description of Texas A&M\'s fight song and cheer.\n\nThe phrase "The Aggie Marching Band\'s roar was heard as \'Hail Aggi" suggests a proper noun or nickname ("The Aggie Spirit"), likely referencing the university\'s mascot or a specific event name with a historical figure.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of a quoted nickname ("The Spirit of Aggi"), strongly expecting "wick" or "wickville" to complete the compound noun, likely continuing with "Eagle" or "Eagle Pride," referencing the alma mater.'
- own ablation (‖d_c‖ 27.494, proj 0.0606, cos(h',h) 0.9565): persist_word 1.0, persist_claim 0.238: 'Historical sports article format with Wikipedia-style structure, describing Texas A&M\'s fight song and traditions, establishing a factual tone with trivia about the Aggie band.\n\nThe phrase "The fight song of Texas A&M University is known as the \'Aggie Fight Song,\' and the winner of the game earns the Aggi" is a familiar closing phrase referencing the university\'s mascot name.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of the phrase "The spirit of Aggieland," completing a traditional nickname or honorific title, strongly expecting "eland" or "Eagle" to close the compound noun describing the student body\'s victory.'
- random ablation (partner row 522, cos(h',h) 0.9559): persist_word 1.0, persist_claim 0.326: 'Historical sports event format with official Texas A&M University description, listing traditions and facts about the Aggie Fight Song.\n\nThe phrase "And the cheers of the Aggies fill the stadium, with the Aggieland fight song ringing out as \'Hail Texas\'" suggests a closing phrase referencing the Aggie mascot or a specific honorific term, likely "Aggieland" or a mascot name.\n\nFinal token "Aggi" is a truncated word mid-phrase ("the Aggi"), part of a compound noun ("The flame of Aggi"), strongly expecting "eland" or "Eagle" or "Eagle Pride," completing the traditional honorific phrase about the team\'s spirit.'

### row 476 (stim 140, nonlast_in_prefix, detail, word_orig '25"')

- claim: 'The phrase "The fifth novel of Stephen King , his 25" strongly implies a numbered list or record of his works, with "25th novel" suggesting a milestone or ranking number for his career.'
- original explanation: 'Wiki article format with descriptive prose about a novel, establishing a book title and author context.\n\nThe phrase "The fifth novel of Stephen King , his 25" strongly implies a numbered list or record of his works, with "25th novel" suggesting a milestone or ranking number for his career.\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, his 25"), immediately expecting "th novel" or "th work" or "th novel in his series," completing the numerical claim about his record-breaking or numbered literary achievement.'
- own ablation (‖d_c‖ 27.777, proj 0.1931, cos(h',h) 0.9545): persist_word 1.0, persist_claim 0.262: 'Wikipedia article format with biographical prose describing a novel, establishing factual details about Canadian author David Morrell\'s third novel.\n\nThe phrase "It is his 14th novel, which is his 25" mirrors a numbered series claim, suggesting a concluding statistic about his authorship count or career milestone, completing the "first nonfiction work" attribution.\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th book, his 25th work"), strongly expecting "th book" or "th work" to close the number, then likely "th novel" or "th book."'
- random ablation (partner row 623, cos(h',h) 0.9579): persist_word 1.0, persist_claim 0.394: 'Wiki-style or fan fiction format with a title suggesting a book or film, implying a numbered list or descriptive context about a Canadian author\'s novel.\n\nThe phrase "His 25th novel , being his 25" strongly implies a numeric designation or record, likely a numbered series or milestone, completing "his 25th novel" or "a novel about crime."\n\nFinal token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, 25"), immediately expecting "th novel" or "th novel in his career" or "th novel" to complete the numeric milestone claim.'


- review sheets: d1_review_blind.csv (20 rows, seed 0; the two new explanations in shuffled order) — open first; d1_review_key.csv after

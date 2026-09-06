# S3 summary — corrupted vs paraphrased claims (evaluation claims)

git d62ca4be; settings in s3_settings.json

## Editor acceptance

- evaluation claims: 538
- corrupt: tags parsed 0.993, words ok 0.950
- paraphrase: tags parsed 0.996, words ok 0.957
- corrupt == paraphrase: 0.000
- edit_ok (both accepted): 490 / 538 = 0.911; rejection rate 0.089
- numeric_ok (deterministic corruption possible): 445 / 538
- editor errors: 0

## Primary statistics (accepted claims, paired)

| statistic | mean | CI95 lo | CI95 hi | n | n_expl |
|---|---|---|---|---|---|
| A = Δ_i(z*) − Δ_i(z)  [LLM corrupt] | 0.00313 | 0.00159 | 0.00478 | 490 | 160 |
| P = Δ_i(z~) − Δ_i(z)  [paraphrase] | 0.00494 | 0.00354 | 0.00665 | 490 | 160 |
| A − P | -0.00181 | -0.00279 | -0.00080 | 490 | 160 |
| A_det [deterministic corrupt] | 0.00376 | 0.00231 | 0.00538 | 402 | 158 |
| A_det − P | -0.00137 | -0.00241 | -0.00034 | 402 | 158 |

## Secondary statistics

| statistic | mean | CI95 lo | CI95 hi | n |
|---|---|---|---|---|
| cos(z) − cos(z*)  [corrupt] | 0.00313 | 0.00159 | 0.00478 | 490 |
| cos(z) − cos(z~)  [paraphrase] | 0.00494 | 0.00354 | 0.00665 | 490 |
| cos(z) − cos(z_det) | 0.00381 | 0.00222 | 0.00558 | 445 |
| cos(z) − cos(z_offtopic) | 0.11417 | 0.10443 | 0.12337 | 538 |
| cos(z_joined) − cos(z*)  [joined-claims baseline] | 0.00182 | 0.00117 | 0.00266 | 490 |
| cos(z_joined) − cos(z~) | 0.00363 | 0.00297 | 0.00430 | 490 |

- AUROC(Δ_z_edit corrupt vs Δ_z original), accepted claims: 0.5257
- AUROC(Δ_z_edit paraphrase vs Δ_z original): 0.5587
- AUROC(Δ_z_edit corrupt vs Δ_z_edit paraphrase): 0.4665
- AUROC(Δ_z_edit corrupt_det vs Δ_z original): 0.5300
- AUROC(Δ_z_edit offtopic vs Δ_z original): 0.9553
- fraction A > 0: 0.6633; fraction P > 0: 0.8041; fraction A > P: 0.3286

## Kill test

- 2026-09-06T04:26:37  S3  K3  threshold=CI95 of mean(A−P) ≤ 0; INCONCLUSIVE if straddles or accepted<100  observed=mean A=0.00313 [0.00159,0.00478]; mean P=0.00494 [0.00354,0.00665]; mean A−P=-0.00181 CI95=[-0.00279,-0.00080] n_accepted=490 n_expl=160  MET  MET would mean the score does not respond to an LLM factual contradiction more than to a meaning-preserving rewording
- 2026-09-06T04:26:37  S3  K3-det  threshold=same as K3 for deterministic corruption (reported separately, not a pre-registered kill)  observed=mean A_det=0.00376 [0.00231,0.00538]; mean A_det−P=-0.00137 CI95=[-0.00241,-0.00034] n=402  MET  deterministic number/name swap instead of LLM corruption

## 10 fixed examples (accepted evaluation claims at rows 0, 16, …, 144 of the accepted list; verbatim)

### accepted #0 (row 133, stim 40, claim 0/4) token='ium'
- original:   Wikipedia-style chemistry article structure with numbered sections listing properties of europium, presenting factual data about the element's atomic and physical characteristics.
- corrupted:  Wikipedia-style chemistry article structure with numbered sections listing properties of lead, presenting factual data about the element's atomic and physical characteristics.
- paraphrase: Europium's properties detailed in a numbered sections Wikipedia-style chemistry article, encompassing factual data on its atomic and physical attributes.
- corrupt_det: None
- Δ_z(original)=-0.02335  Δ_z*(corrupt)=-0.02390  Δ_z~(paraphrase)=-0.02137  Δ_det=nan  A=-0.00055  P=0.00198

### accepted #16 (row 150, stim 44, claim 0/3) token=' of'
- original:   Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a gangster's actions.
- corrupted:  Narrative momentum: a comic book description listing character traits and dialogue, with a specific scene detailing a puppy's actions.
- paraphrase: A comic book description focusing on character traits and dialogue, including a particular scene that outlines a gangster's activities.
- corrupt_det: None
- Δ_z(original)=-0.00779  Δ_z*(corrupt)=-0.01056  Δ_z~(paraphrase)=0.00426  Δ_det=nan  A=-0.00278  P=0.01204

### accepted #32 (row 167, stim 49, claim 0/3) token=' who'
- original:   Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of TV show details about a fictional detective series.
- corrupted:  Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of video game details about a fictional detective series.
- paraphrase: A wiki article structured with metadata fields preceding the film description, setting a standard for TV show details on a fictional detective series.
- corrupt_det: Wiki article format with structured metadata fields followed by a film description, establishing a standard pattern of The show details about a fictional detective series.
- Δ_z(original)=0.04600  Δ_z*(corrupt)=0.05133  Δ_z~(paraphrase)=0.03711  Δ_det=0.05032  A=0.00534  P=-0.00888

### accepted #48 (row 184, stim 54, claim 1/3) token=' Carter'
- original:   The sentence "Another biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- corrupted:  The sentence "Another biographer was Jack Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- paraphrase: The sentence "John Carter was another biographer" introduces a named source or figure, probably a secondary account or personal detail about the soldier's life, indicating a particular person or event linked to his fame or death.
- corrupt_det: The sentence "Initially biographer was John Carter" introduces a named source or figure, likely a second account or personal detail about the soldier's life, suggesting a specific person or event related to his fame or death.
- Δ_z(original)=-0.01676  Δ_z*(corrupt)=-0.01916  Δ_z~(paraphrase)=-0.01615  Δ_det=-0.01699  A=-0.00240  P=0.00061

### accepted #64 (row 201, stim 59, claim 0/3) token=' aforementioned'
- original:   American military article format with numbered statistics detailing a Florida county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- corrupted:  American military article format with numbered statistics detailing a Antarctica county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- paraphrase: American military-style article, featuring numbered statistics about a Florida county's infrastructure, presented in organized bullet points and complete with citations.
- corrupt_det: American military article format with numbered statistics detailing a However county's infrastructure, listing specific infrastructure details with structured bullet points and citations.
- Δ_z(original)=-0.00578  Δ_z*(corrupt)=-0.00415  Δ_z~(paraphrase)=0.00089  Δ_det=-0.00585  A=0.00163  P=0.00667

### accepted #80 (row 218, stim 64, claim 0/3) token=' met'
- original:   British historical biography article detailing parliamentary politics of Charles I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- corrupted:  British historical biography article detailing parliamentary politics of Charles II, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- paraphrase: Article on British historical biography focusing on Charles I's parliamentary politics, systematically outlining parliamentary opposition and constitutional crisis through numbered sections and a chronological narrative.
- corrupt_det: British historical biography article detailing parliamentary politics of War I, systematically describing parliamentary opposition and constitutional crisis with numbered sections and chronological narrative.
- Δ_z(original)=-0.00594  Δ_z*(corrupt)=-0.00265  Δ_z~(paraphrase)=-0.00454  Δ_det=-0.00135  A=0.00329  P=0.00140

### accepted #96 (row 239, stim 69, claim 3/4) token=' .'
- original:   " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- corrupted:  " closes a third item in a parallel list ("While the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Sino-Tibetan languages' variant counts."
- paraphrase: closes a third entry in an analogous list ("While the latter encompasses the Turkish language with its complete written form and the Greek language with abbreviated characters..."), anticipating either "The written form of the last language is..." or "The variants of Slavic dialects count."
- corrupt_det: " closes a third item in a parallel list ("Black the latter includes the Turkish language with full written form and the Greek language with reduced characters..."), strongly expecting "The remaining language's written form is..." or "The Slavic dialects' variant counts."
- Δ_z(original)=-0.02229  Δ_z*(corrupt)=-0.02208  Δ_z~(paraphrase)=-0.01732  Δ_det=-0.02438  A=0.00021  P=0.00497

### accepted #112 (row 258, stim 74, claim 0/3) token=' with'
- original:   British music article format with Wikipedia-style entry structure detailing an album by Scottish rock band Feeder, listing discography and chart performance.
- corrupted:  British music article format with Wikipedia-style entry structure detailing an album by English rock band Feeder, listing discography and chart performance.
- paraphrase: An article in the style of a British music Wikipedia entry, providing details on an album by the Scottish rock band Feeder, including discography and chart performance.
- corrupt_det: British music article format with Wikipedia-style entry structure detailing an album by Imagine rock band Feeder, listing discography and chart performance.
- Δ_z(original)=-0.01356  Δ_z*(corrupt)=-0.01376  Δ_z~(paraphrase)=-0.01140  Δ_det=-0.01364  A=-0.00019  P=0.00216

### accepted #128 (row 275, stim 79, claim 2/3) token=' as'
- original:   Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- corrupted:  Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as Darren Aronofsky, also known as"), strongly expecting "Bob" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- paraphrase: The concluding token "as" signals an unfinished noun phrase ("also known as"), which is part of a name attribution clause ("known as Darren Aronofsky, also known as"), with a strong anticipation for "DA," "Arno," "Aronofsky," or "DAF" to finalize the nickname or abbreviated identity.
- corrupt_det: Final token "as" ends an incomplete noun phrase ("also known as"), part of a name attribution clause ("known as AI Aronofsky, also known as"), strongly expecting "DA" or "Arno" or "Aronofsky" or "DAF" to complete the nickname or abbreviated identity.
- Δ_z(original)=-0.01567  Δ_z*(corrupt)=-0.01064  Δ_z~(paraphrase)=-0.01394  Δ_det=-0.01168  A=0.00502  P=0.00173

### accepted #144 (row 292, stim 85, claim 1/3) token=' the'
- original:   The sentence structure "While some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- corrupted:  The sentence structure "While some songs were originally intended for the compilation album, several artists chose to include all tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- paraphrase: The sentence structure "Although some songs were planned for the compilation album, various artists decided against including particular tracks in the ultimate tracklist" outlines a pattern of detailing exclusions, suggesting the definitive answer regarding the initial album's contents.
- corrupt_det: The sentence structure "Dutch some songs were originally intended for the compilation album, several artists chose not to include certain tracks on the final tracklist" establishes a pattern of explaining exclusions, implying the final answer about the original album's tracklist.
- Δ_z(original)=-0.00548  Δ_z*(corrupt)=-0.00502  Δ_z~(paraphrase)=-0.00715  Δ_det=-0.00665  A=0.00045  P=-0.00167


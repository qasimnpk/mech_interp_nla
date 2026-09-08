# X3 summary — does the dominant local snippet suppress factual discrimination? (AR only; TARGET judge)

git 89f5f6b3; settings in x3_settings.json; rows in x3_scores.csv; judge outputs in x3_judge.jsonl

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

## Pre-committed reading key (from PLAN; the numbers decide)

I > 0 with G_2 > G_1 → consistent with the snippet suppressing discrimination; G_2 ≈ G_3 > G_1 → general context/length effect; no change → snippet dominance does not explain the insensitivity; cos collapse under (2) → out-of-distribution caveat.

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


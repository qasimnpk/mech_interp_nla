# C1 summary — position vs content (evaluation explanations with >= 3 claims, AR only)

git d79da6ac; settings in c1_settings.json; raw rows in c1_expl.csv

- explanations: 160 (errors 0); AR forwards 800; 0.22 s/score
- snippet (last claim) is a 'Final token' claim in 141/160 explanations

## Kill C1

- paired diff [cost_snippet_in_z_rot − cost_snippet_in_z (S2)]: -0.02642 CI95=[-0.03215,-0.02126] n=160  threshold ≤ -0.05 → **NOT MET**
- secondary (joined baseline) [cost_snippet_in_z_rot − cost_snippet_in_z_joined]: -0.02553 CI95=[-0.03130,-0.02032] n=160 → NOT MET

## Reconstruction of the rearranged texts

| text | mean cos | CI95 |
|---|---|---|
| z (original, S2) | 0.8820 | [0.8753,0.8886] |
| z_joined (space-joined, S3) | 0.8811 | [0.8742,0.8881] |
| z_rot (snippet first) | 0.8556 | [0.8461,0.8648] |
| z_rev (reversed) | 0.8533 | [0.8446,0.8621] |
| z_rot − snippet (= rest) | 0.7567 | [0.7389,0.7734] |
| z_rot − new last claim | 0.8404 | [0.8323,0.8489] |
| z_rev − snippet | 0.7213 | [0.7016,0.7401] |

## Deletion costs (cos(text) − cos(text minus claim))

| quantity | mean | CI95 | median | frac > 0 |
|---|---|---|---|---|
| snippet in z (S2, −Δcos) | 0.1253 | [0.1087,0.1416] | 0.0882 | 0.988 |
| snippet in z_joined | 0.1244 | [0.1079,0.1410] | 0.0873 | 0.988 |
| snippet in z_rot (moved to front) | 0.0989 | [0.0835,0.1149] | 0.0611 | 0.925 |
| snippet in z_rev (first position) | 0.1320 | [0.1141,0.1495] | 0.0921 | 0.956 |
| claim[-2] in z (S2) | 0.0183 | [0.0158,0.0208] | 0.0145 | 0.956 |
| claim[-2] when last in z_rot | 0.0152 | [0.0092,0.0207] | 0.0176 | 0.838 |

## Paired differences

| difference | mean | CI95 | frac < 0 |
|---|---|---|---|
| snippet cost: z_rot − z (kill statistic) | -0.02642 | [-0.03215,-0.02126] | 0.944 |
| snippet cost: z_rot − z_joined | -0.02553 | [-0.03130,-0.02032] | 0.944 |
| snippet cost: z_rev − z | 0.00665 | [-0.00421,0.01917] | 0.519 |
| claim[-2] cost: when last (z_rot) − in z | -0.00310 | [-0.00882,0.00191] | 0.463 |

Ratio of mean snippet cost in z_rot to mean snippet cost in z (S2): 0.789; to z_joined: 0.795

## Five fixed rows (stim 40, 72, 104, 136, 168)

### stim 40 (n_claims 4)
- cos_z 0.8765  cos_z_rot 0.7745  cos_z_rev 0.7692
- snippet cost in z 0.0603  in z_rot -0.0416  in z_rev 0.0966
- z_rot: Final token "europium" ends mid-sentence ("Properties of europium"), part of a data table or list item ("Some properties of europium"), expecting continuation like "in its solid state are:" or "are:" or "include the following:" or "atoms are given below," completing the atomic data. Wikipedia-style chemistry article structure with numbered sections listing properties of europium, presenting factual data about the element's atomic and physical characteristics. The sentence "The atomic mass and other physical properties of europium are given below. The atomic mass of europium" signals a list of specific elemental data points, likely continuing with chemical forms or isotopic values of the element.

### stim 72 (n_claims 3)
- cos_z 0.9243  cos_z_rot 0.8968  cos_z_rev 0.8995
- snippet cost in z 0.0422  in z_rot 0.0147  in z_rev 0.0379
- z_rot: Final token "spinner" ends mid-phrase ("Young left handed spin spinner"), part of a list of player attributes ("He replaced former England's left handed spinner"), strongly expecting "James Tredwell" or "David Wiese" or "Tim Bresnan as his spin bowling partner." British cricket newspaper article format with historical context and statistics, listing England's Test team changes for the 2005 Ashes series. The sentence structure "While his batting form was questioned England's new spin bowler Scott Borthwick introduced young spin spinner" introduces a specific player's unusual choice, naming a spin bowler and a specific player's skill (a spinning spinner).

### stim 104 (n_claims 3)
- cos_z 0.8688  cos_z_rot 0.8533  cos_z_rev 0.8606
- snippet cost in z 0.0587  in z_rot 0.0432  in z_rev 0.0531
- z_rot: Final token "characters" ends mid-clause ("Unlike many of his characters"), part of a comparative clause ("Unlike other aspects of the show's cast of characters"), strongly expecting continuation like "who are fully developed," "this villain is," or "the protagonist's backstory, he remains mysterious" or similar. Wiki article format with film description listing plot details about a sci-fi television series, establishing factual tone with literary analysis context. The sentence structure "Unlike many of his fellow characters" suggests a contrast clause continuing a character trait or narrative arc about the villain's mysterious origin versus the show's other characters, likely referencing the novel's established ensemble cast or lack of backstory.

### stim 136 (n_claims 3)
- cos_z 0.7848  cos_z_rot 0.7222  cos_z_rev 0.7179
- snippet cost in z 0.0885  in z_rot 0.0259  in z_rev 0.0940
- z_rot: Final token " = " closes a header label (" = First derivative = "), part of a second section header structure (" = Timeline section = "), immediately expecting continuation like "s" or " "The following" or "..." or " This section describes the following:" to complete the section header and introduce the mathematical definition. Wiki-style formatted article with numbered sections and bullet points listing events, establishing a structured encyclopedia format about a fictional "Global warming" song. The phrase " = = = Section : The timeline = " signals a section header pattern, strongly implying the next tokens continue with the definition or description of the "First derivative" section's content about the timeline's events.

### stim 168 (n_claims 3)
- cos_z 0.9160  cos_z_rot 0.9051  cos_z_rev 0.8998
- snippet cost in z 0.0500  in z_rot 0.0391  in z_rev 0.0903
- z_rot: Final token "a" is an indefinite article mid-clause ("maintain up kept up a"), part of a clause listing constraints ("While struggling to maintain a pace, he couldn't keep up a"), expecting a noun like "consistent plot" or "monthly output rate" or "daily writing." Japanese manga article format with translation notes discussing a romantic comedy series, detailing character development and plot issues around the manga's serialization schedule. The sentence structure "Although the author struggled to keep up with her writing schedule, she found it difficult to maintain a weekly pace and had to cut back on a" suggests a quoted statement about the writer's workload or consistency, continuing a critique of chapter output.


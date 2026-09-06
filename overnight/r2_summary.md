# R2 summary — amplified corruption (every accepted claim replaced), AR only, evaluation explanations

git c2a7ae5f; settings in r2_settings.json; AR forwards 635

- evaluation explanations with claims (S2): 160; included (>= 2 accepted claims): 160; excluded: 0; errors: 0
- explanations with >= 2 corrupt_det claims: 155
- per included explanation: n_claims mean 3.36; n_accepted mean 3.06; fraction of claims replaced 0.911; n_det mean 2.78

## Headline (paired per explanation; cluster bootstrap CI95)

| statistic | mean | CI95 lo | CI95 hi | n_expl |
|---|---|---|---|---|
| cos(z) − cos(z**)  [all accepted claims corrupted] | 0.00754 | 0.00473 | 0.01082 | 160 |
| cos(z) − cos(z~~)  [all accepted claims paraphrased] | 0.01407 | 0.01149 | 0.01667 | 160 |
| (cos z − cos z**) − (cos z − cos z~~) | -0.00653 | -0.00992 | -0.00260 | 160 |
| cos(z) − cos(z*det)  [all det-corruptible claims swapped] | 0.00922 | 0.00662 | 0.01214 | 155 |
| (cos z − cos z*det) − (cos z − cos z~~)  [same explanations] | -0.00506 | -0.00855 | -0.00137 | 155 |
| cos(z_joined) − cos(z**) | 0.00665 | 0.00425 | 0.00984 | 160 |
| cos(z_joined) − cos(z~~) | 0.01318 | 0.01085 | 0.01562 | 160 |
| cos(z) − cos(empty)  [scale reference] | 0.53490 | 0.52118 | 0.54772 | 160 |

- fraction of explanations where corruption hurts more than paraphrase (D_corrupt > D_para): 0.2125 CI95 [0.1562, 0.2750] n=160
- same for deterministic corruption: 0.3161 CI95 [0.2452, 0.3873] n=155
- for comparison, S3 single-claim: cos(z) − cos(z*) 0.00313, cos(z) − cos(z~) 0.00494, A − P −0.00181 (s3_summary.md)

## Distributions (included explanations)

| quantity | mean | median | p10 | p90 | n |
|---|---|---|---|---|---|
| cos_z | 0.88203 | 0.89176 | 0.81632 | 0.92884 | 160 |
| cos_z_joined | 0.88114 | 0.89249 | 0.81607 | 0.92919 | 160 |
| cos_z_corrupt_all | 0.87449 | 0.88626 | 0.81227 | 0.92472 | 160 |
| cos_z_para_all | 0.86796 | 0.87853 | 0.80494 | 0.92192 | 160 |
| cos_z_det_all | 0.87288 | 0.88355 | 0.80513 | 0.92321 | 155 |
| cos_empty | 0.34713 | 0.34829 | 0.24351 | 0.44351 | 160 |
| D_corrupt | 0.00754 | 0.00322 | -0.00259 | 0.01527 | 160 |
| D_para | 0.01407 | 0.00946 | 0.00166 | 0.03204 | 160 |
| D_det | 0.00922 | 0.00316 | -0.00222 | 0.03024 | 155 |
| D_corrupt_minus_para | -0.00653 | -0.00691 | -0.02656 | 0.00763 | 160 |

## By number of replaced claims

| n_accepted | n_expl | mean D_corrupt | mean D_para | mean diff |
|---|---|---|---|---|
| 2 | 24 | 0.00367 | 0.00804 | -0.00436 |
| 3 | 111 | 0.00638 | 0.01310 | -0.00673 |
| 4 | 17 | 0.01705 | 0.01480 | 0.00225 |
| 5 | 7 | 0.00928 | 0.03905 | -0.02977 |
| 6 | 1 | 0.05571 | 0.07938 | -0.02367 |

## Kill test

- 2026-09-06T09:21:11  R2  R2  threshold=CI95 of mean[(cos z − cos z**) − (cos z − cos z~~)] ≤ 0  observed=mean cos z − cos z**=0.00754 [0.00473,0.01082]; mean cos z − cos z~~=0.01407 [0.01149,0.01667]; paired diff=-0.00653 CI95=[-0.00992,-0.00260] n_expl=160  MET  MET would mean corrupting every claim of an explanation is indistinguishable from paraphrasing every claim

## Timings

- ar_load_s: 2.36
- ar_forward_s: 172.15
- ar_n_forward: 635

## 5 included explanations chosen by seed 0 (verbatim z** and z~~)

### stim 82 n_claims=3 n_accepted=3 cos_z=0.8091 cos_z**=0.8146 cos_z~~=0.8091
- z**: Wikipedia article format with structured biological description of an animal species, listing characteristics and measurements with parenthetical details. The measurement value "Height: 15 cm (6 in" is mid-sentence with a numeric comparison ("length: 15 cm (6 ft"), suggesting a second unit or closing parenthesis completing the size description of the bird's dimensions. Final token "in" ends an incomplete unit expression ("6 in"), part of a parenthetical measurement specification ("length: 15 cm (6 in"), immediately expecting " )" or " ) in diameter" or " a)" to close the size comparison, likely continuing the fish's physical description.
- z~~: A structured biological description of a plant species in Wikipedia format, including characteristics and measurements with additional details in parentheses. The measurement "Height: 15 cm (6 in)" mid-sentence includes a numeric comparison ("length: 15 cm (6 in") implying an additional unit or a closing parenthesis to complete the bird's size description. Final token "in" concludes an unfinished unit expression ("6 in"), part of a parenthetical measurement specification ("length: 15 cm (6 in"), followed by either " )" or " ) in diameter" or " a)" to complete the size description, probably concluding the bird's physical details.

### stim 89 n_claims=3 n_accepted=3 cos_z=0.8917 cos_z**=0.8938 cos_z~~=0.8838
- z**: Australian botanical/field guide format with structured species description, detailing a rare Antarctic orchid species with botanical characteristics and habitat. The sentence "The flower is tubular shaped, emerging from a bulb-like spike typical" introduces a descriptive clause mid-sentence listing flower features, likely referencing the daisy's characteristic corolla structure or inflorescence form from the genus. Final token "typical" ends an incomplete noun phrase ("from typical"), part of a botanical description clause ("Flowers feature from typical"), immediately expecting a noun like "uncommon sepals" or "rounded orchid flowers" or "Bulbous orchid flower structures" continuing the taxonomic description.
- z~~: Australian guidebook format for botany, providing detailed descriptions of a rare New Zealand orchid, including its botanical features and habitat. The flower, described as tubular-shaped and emerging from a bulb-like spike, introduces a mid-sentence descriptive clause that likely refers to the orchid's distinctive corolla structure or inflorescence form. The concluding word "typical" completes an unfinished noun phrase ("from typical"), which is part of a botanical description clause ("Flowers feature from typical"), and is followed by a noun such as "orchidoid sepals," "rounded orchid flowers," or "bulbous orchid flower structures," to continue the taxonomic description.

### stim 120 n_claims=3 n_accepted=3 cos_z=0.8793 cos_z**=0.8730 cos_z~~=0.8731
- z**: Political news article format with quoted tweet structure detailing a celebrity's Senate testimony, establishing narrative context around Democratic congressman Roy Moore's sexual assault allegations. The sentence "The character is a Democrat congressman named Todd Young who is running for Senate and vowed" contains a specific historical reference ("Trump's promise to support him"), implying a backstory about Biden's political deal or campaign promise. Final token "promised" ends mid-clause ("who promised"), part of a parenthetical list of reasons for Trump's character ("Biden, who Obama promised"), expecting continuation like "to deliver jobs" or "him the cabinet position" or "the Democrat's support before breaking his word."
- z~~: A political news piece featuring a quoted tweet that outlines a celebrity's Senate testimony, setting the stage for Republican congressman Roy Moore's sexual assault claims. The sentence "The character, a Democrat congressman named Todd Young running for Senate and who vowed," references a specific historical context (Obama's promise to support him), suggesting a background involving Biden's political agreement or campaign pledge. Final token "promised" is mid-clause ("who promised"), in a parenthetical list of reasons for Trump's character ("Biden, who Obama promised"), anticipating continuation like "to deliver jobs" or "him the cabinet position" or "the Republicans' support before breaking his word."

### stim 140 n_claims=3 n_accepted=3 cos_z=0.8915 cos_z**=0.8892 cos_z~~=0.8830
- z**: Wiki article format with descriptive prose about a novel, establishing a movie title and author context. The phrase "The fifth novel of Stephen King, his 1st" strongly implies a numbered list or record of his works, with "1st novel" suggesting a milestone or ranking number for his career. Final token "25" is mid-number in "his 25," part of an attribution claim ("his 25th novel, his 25"), immediately expecting "st novel" or "nd novel" or "rd novel," completing the numerical claim about his record-breaking or numbered literary achievement.
- z~~: A descriptive prose style for a wiki article, setting the stage with a novel's title and author information. The phrase "The fifth novel by Stephen King, his 25th" clearly indicates a sequence or ranking among his works, with "25th novel" pointing to a significant position in his literary career. The middle token "25" in "his 25," within an attribution claim ("his 25th novel, his 25"), suggests the immediate expectation of "th novel" or "th work" or "th novel in his series," thereby finishing the numerical claim about his record-breaking or numbered literary accomplishment.

### stim 172 n_claims=4 n_accepted=4 cos_z=0.9240 cos_z**=0.9233 cos_z~~=0.9156
- z**: British military history reference article with technical specifications of a World War II American aircraft, describing design and production details. The sentence structure "The aircraft was withdrawn from production in December 1942 but work continued on the Avro Spitfire's development programme." In 29" implies a date event or decision, completing a historical clause about wartime urgency or cancellation timing. Final token "19" is mid-number in "in 19," part of a date specification clause ("Decision was made in December 19"), strongly expecting "43" or "44" to complete the year, likely followed by "42, the Ministry delayed the test."
- z~~: An article on British military history focusing on the technical specs of a World War II British aircraft, detailing its design and production. The aircraft ceased production in December 1942, yet work persisted on advancing the Avro Lincoln's development. In 19", it suggests a specific date for an event or decision, concluding a historical statement regarding wartime urgency or cancellation timing. The middle token "19" appears in "in 19," within a date context ("The decision was made in December 19"), with anticipation for "43" or "44" to finish the year, probably followed by "43, the Ministry delayed the test."


# C2 summary — matched one-fact activation pairs (TARGET → AV → AR)

git a7b57117; settings in c2_settings.json; rows in c2_pairs.csv; descriptions in c2_descriptions.jsonl; activations in out/c2_acts.npz

- pairs: 40 (errors 0); templates 10; tokens per context 18–22; entity distance to end 11–17 tokens; shared suffix 10–16 tokens
- AV: parse_ok 80/80, cjk 0/80, errors 0; 9.9 s/gen
- identical descriptions within a pair: 0/40

## Kill C2

- mean M (four-way margin): 0.01877 CI95=[0.00982,0.03382] n=40, clusters=10 templates; threshold ≤ 0 → **NOT MET**
- fraction of pairs with M > 0: 1.000 (40/40)
- M_a = cos(h_a,d_a) − cos(h_a,d_b): 0.00926 CI95=[0.00364,0.01558] n=40; M_b = cos(h_b,d_b) − cos(h_b,d_a): 0.00951 CI95=[0.00243,0.01882] n=40

## Activation geometry

- cos(h_a, h_b): mean 0.9664 min 0.8215 max 0.9988; norms mean 111.5
- cos(AR(d_a), AR(d_b)): mean 0.9755

## Reconstruction scores

| quantity | mean | min | max |
|---|---|---|---|
| cos(h_a, AR(d_a)) own | 0.8883 | 0.7889 | 0.9490 |
| cos(h_b, AR(d_b)) own | 0.8904 | 0.7908 | 0.9487 |
| cos(h_a, AR(d_b)) cross | 0.8791 | 0.7742 | 0.9466 |
| cos(h_b, AR(d_a)) cross | 0.8809 | 0.7846 | 0.9350 |

## Text-edit control (entity swapped inside the description, same activation) vs activation edit

- swap available (entity string present in description): 12/80 descriptions
- cos(h, AR(d)) − cos(h, AR(d with entity swapped)): 0.00476 CI95=[-0.00006,0.00804] n=12
- per-side activation-edit margin cos(h_x,AR(d_x)) − cos(h_x,AR(d_y)) on all 80 sides: 0.00939 CI95=[0.00491,0.01691] n=80

## Entity mentions in the descriptions (80 descriptions)

- mentions own entity: 11/80; mentions other entity: 3/80; mentions neither: 66/80; both: 0/80

| template | own-mention rate | mean M | frac M>0 | mean cos(h_a,h_b) |
|---|---|---|---|---|
| 0 | 0.25 | 0.0109 | 1.00 | 0.9682 |
| 1 | 0.12 | 0.0112 | 1.00 | 0.9630 |
| 2 | 0.25 | 0.0074 | 1.00 | 0.9889 |
| 3 | 0.00 | 0.0097 | 1.00 | 0.9770 |
| 4 | 0.12 | 0.0143 | 1.00 | 0.9642 |
| 5 | 0.00 | 0.0155 | 1.00 | 0.9854 |
| 6 | 0.00 | 0.0197 | 1.00 | 0.9790 |
| 7 | 0.62 | 0.0837 | 1.00 | 0.8612 |
| 8 | 0.00 | 0.0074 | 1.00 | 0.9876 |
| 9 | 0.00 | 0.0079 | 1.00 | 0.9895 |

## Five verbatim pairs

### pair 0 (template 0): Paris / Lyon; cos(h_a,h_b)=0.9643; M=0.0021
- context_a: The capital of the country is Paris. Tourists arrive at the main station and walk to the
- context_b: The capital of the country is Lyon. Tourists arrive at the main station and walk to the
- d_a (mentions own=True, other=False; cos own 0.8598, cross 0.8494): Formal mathematical/structural description pattern with a numbered sequence ("A train from Moscow to Paris with a probability"), implying a scenario about a tourist arriving at a metro station.

The phrase "A person leaves the train station with a random time to the Eiffel Tower and goes to the metro center" strongly implies a destination or attraction description, suggesting the sentence structure continues describing the route or destination's location.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), directly continuing "a person goes from the metro to the," requiring a noun like "central station" or "hotel, or the clock tower" or "station, with a probability distribution."
- d_b (mentions own=False, other=False; cos own 0.8777, cross 0.8860): Formal mathematical/urban description format with a translated phrase ("A random walk in the city"), implying a puzzle or event context about a metro station.

The sentence structure "A person leaves from a random station in the center of the city and goes to the metro station, then decides whether to go to the" suggests a paired noun phrase describing destination or attraction location about the city's main square.

Final token "the" is an article mid-noun phrase ("from the hotel to the"), continuing the parallel structure "a random walk to the metro station and to the," strongly expecting a noun like "main square" or "hotel entrance" or "bus stop, with a certain probability."

### pair 9 (template 2): Tuesday / Thursday; cos(h_a,h_b)=0.9971; M=0.0013
- context_a: The meeting has been moved to Tuesday. Everyone should bring the printed report and arrive at the
- context_b: The meeting has been moved to Thursday. Everyone should bring the printed report and arrive at the
- d_a (mentions own=True, other=False; cos own 0.8854, cross 0.8738): Formal business/English language format with a question structure ("The meeting is scheduled for tomorrow morning. Please bring your updated report"), implying a workplace or schedule context.

The phrase "If the date is changed to Tuesday, we should attend the meeting and the" suggests an incomplete clause describing a specific action or location, likely a meeting room or agenda item detail about a scheduled event.

Final token "the" is an article mid-phrase ("arrive at the"), part of a list or noun phrase ("All attendees should arrive at the meeting and the"), strongly expecting a noun like "conference room" or "following schedule" or "office at 3 PM" or similar.
- d_b (mentions own=False, other=False; cos own 0.8726, cross 0.8829): Formal business English format with incomplete sentence structure ("The meeting is scheduled for tomorrow, and all attendees must bring their reports to the"), implying a workplace scenario or schedule context.

The phrase "If the sales figures have increased by 5%, we should arrive at the meeting" suggests a list or action item format, likely a meeting location or time detail about a specific organizational event.

Final token "the" is an incomplete noun phrase mid-sentence ("arrive at the"), part of a second clause ("All attendees should attend the meeting and the"), strongly expecting a noun like "conference room" or "following schedule" or "office at 3 PM" or "boardroom."

### pair 18 (template 4): platinum / bronze; cos(h_a,h_b)=0.9648; M=0.0067
- context_a: The ring was made of pure platinum. The jeweller placed it carefully in a small box on the
- context_b: The ring was made of pure bronze. The jeweller placed it carefully in a small box on the
- d_a (mentions own=False, other=False; cos own 0.8437, cross 0.8311): Narrative context: a British English-language story with a quirky wildlife photograph, implying a dialogue or scene about a gemstone jeweler's display.

The phrase "The trembling detective held the diamond and other specimens on a white cloth on the" suggests a descriptive clause about a shop's display or tray, continuing a scene-setting phrase about a mysterious gift being handed to a client.

Final token "the" is an article mid-phrase ("on the shelf on the"), part of an incomplete noun phrase describing a receipt or tray location ("A specimen with a diamond and other items was placed on the shelf on the"), expecting a noun like "floor" or "client's desk" or "box."
- d_b (mentions own=False, other=False; cos own 0.8667, cross 0.8727): Narrative context: a short story or descriptive prose about a cat, with a mysterious gemstone being shown to a customer.

The phrase "The little bird flew the specimen of the precious stone onto the counter of the cabinet on the" suggests a dialogue setup or scene description, implying a shopkeeper's display or inventory tray, continuing a list of items.

Final token "the" is an incomplete noun phrase mid-sentence ("placed on the shelf on the... on the"), part of a quoted description clause ("A trembling spider with a letter and some papers he placed on the shelf on the"), strongly expecting "floor" or "customer's desk" or "box, waiting."

### pair 27 (template 6): measles / influenza; cos(h_a,h_b)=0.9835; M=0.0050
- context_a: The patient was diagnosed with measles last year. The doctor explained the treatment plan and asked the family to
- context_b: The patient was diagnosed with influenza last year. The doctor explained the treatment plan and asked the family to
- d_a (mentions own=False, other=False; cos own 0.9153, cross 0.9154): Medical Chinese language format with clinical context suggesting a medical record or dialogue format about a disease, implying a doctor's instruction about a specific illness.

The phrase "The doctor prescribed the treatment and asked the family to" implies a list or action item structure, likely describing patient instructions or follow-up obligations, with "family requested to" suggesting a specific compliance detail about the condition or care plan.

Final token "to" ends an incomplete verb phrase ("asked the family to"), part of a quoted instruction clause ("The doctor requested the family to... and requested the family to"), strongly expecting a verb like "monitor the condition" or "sign the consent" or "bring back certain items."
- d_b (mentions own=False, other=False; cos own 0.9202, cross 0.9151): Medical Chinese language format with clinical context suggesting a medical record or dialogue format about a patient's illness, implying a doctor's instruction about a medication.

The phrase "The doctor prescribed the treatment and asked the family to" implies a list or action item structure, likely describing patient instructions or consent details about the condition or monitoring requirements.

Final token "to" ends an incomplete clause ("asked the family to"), part of a quoted instruction sequence ("The doctor requested the family to...and asked the family to"), strongly expecting a verb like "monitor" or "sign the consent" or "take responsibility for the medication" or "record any specific instructions."

### pair 36 (template 9): river / castle; cos(h_a,h_b)=0.9836; M=0.0147
- context_a: The painting shows a river under a clear sky. Visitors to the gallery often stop in front of it and
- context_b: The painting shows a castle under a clear sky. Visitors to the gallery often stop in front of it and
- d_a (mentions own=False, other=False; cos own 0.9330, cross 0.9220): European language description with literary/educational tone, suggesting a museum exhibit or art piece about a tree, implying an observation or contemplative experience.

The sentence structure "Some visitors often stop before this fountain and many people stand still and" strongly implies a common reaction or activity pattern, likely continuing with "take time to observe" or "are fascinated by the artwork," establishing the scene.

Final token "and" is a conjunction mid-clause ("visitors often stop by the fountain and many people stop and"), part of an incomplete clause describing observer behavior, immediately expecting a verb like "enjoy the silence" or "write notes," or "often linger for a long time."
- d_b (mentions own=False, other=False; cos own 0.9261, cross 0.9225): European museum exhibition text with formal descriptive tone, suggesting a literary or art book context about a sculpture.

The sentence structure "Some visitors often stop in front of this painting and many people stand still and" implies an observed behavior pattern or invitation, likely continuing with a clause describing visitors' reactions or interest in the artwork, completing the introductory setup about the sculpture's appealing qualities.

Final token "and" is a conjunction mid-clause ("visitors often stop by and many visitors stop to look at the exhibition and"), strongly expecting a verb phrase like "take notes" or "are fascinated by its" or "often spend time discussing," continuing the observational description of visitor behavior.


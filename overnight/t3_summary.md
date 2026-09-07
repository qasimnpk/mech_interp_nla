# T3 summary — residual-stream steering of the verbalizer (pilot 0–39; AV + AR)

git 9b289da7; settings in t3_settings.json; items in t3_outputs.jsonl; directions in out/t3_dirs.npz

- items 420 (errors 0); 12.3 s/item; stopped at stimulus 35 (None = all 40 done); prompt 125 tokens, marker at 111
- directions: french_L8 ||d||=17.5, mean||h||=50.1, french_L14 ||d||=20.7, mean||h||=65.2, terse_L8 ||d||=38.1, mean||h||=53.4, terse_L14 ||d||=49.2, mean||h||=69.0
- baseline (round-1 explanations, pilot): french pass 0.000, mean words 99.7, topic preserved 0.025

## Kill T3

- eligible french cells (parse_ok ≥ 0.5): 1; outcome → **MET**

## Grid

| direction | ℓ | α | n | parse_ok | French pass [CI] | French frac | words | cjk | topic preserved | seq-sim V0 | Jaccard V0 | mean cos(AR,h) | mean Δcos vs V0 | median Δcos |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| french | 8 | 1 | 35 | 1.000 | 0.057 [0.000,0.143] | 0.083 | 90.0 | 0.029 | 0.057 | 0.391 | 0.364 | 0.8840 | -0.0094 | -0.0072 |
| french | 8 | 2 | 35 | 0.000 | 0.400 [0.229,0.571] | 0.243 | 59.1 | 0.000 | 0.000 | 0.028 | 0.024 | 0.2830 | -0.6103 | -0.6167 |
| french | 8 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 1.0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.1389 | -0.7544 | -0.7699 |
| french | 14 | 1 | 35 | 0.000 | 0.114 [0.029,0.229] | 0.094 | 101.9 | 0.000 | 0.000 | 0.240 | 0.250 | 0.7751 | -0.1183 | -0.0702 |
| french | 14 | 2 | 35 | 0.000 | 0.171 [0.057,0.314] | 0.056 | 149.8 | 0.257 | 0.000 | 0.070 | 0.059 | 0.2955 | -0.5979 | -0.5977 |
| french | 14 | 4 | 35 | 0.000 | 0.514 [0.343,0.686] | 0.514 | 22.6 | 0.971 | 0.000 | 0.000 | 0.000 | 0.1979 | -0.6955 | -0.7079 |
| terse | 8 | 1 | 35 | 1.000 | 0.000 [0.000,0.000] | 0.067 | 114.0 | 0.000 | 0.029 | 0.230 | 0.281 | 0.8536 | -0.0398 | -0.0276 |
| terse | 8 | 2 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 101.5 | 0.000 | 0.000 | 0.002 | 0.002 | 0.2404 | -0.6530 | -0.6601 |
| terse | 8 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 200.0 | 0.000 | 0.000 | 0.000 | 0.011 | 0.2162 | -0.6772 | -0.6800 |
| terse | 14 | 1 | 35 | 0.000 | 0.029 [0.000,0.086] | 0.008 | 113.1 | 0.000 | 0.000 | 0.024 | 0.021 | 0.2626 | -0.6308 | -0.6421 |
| terse | 14 | 2 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 141.8 | 0.000 | 0.000 | 0.031 | 0.015 | 0.2445 | -0.6489 | -0.6513 |
| terse | 14 | 4 | 35 | 0.000 | 0.000 [0.000,0.000] | 0.000 | 200.0 | 0.000 | 0.000 | 0.000 | 0.000 | 0.2269 | -0.6664 | -0.6734 |

## Four fixed examples (stimuli 0, 7, 19, 33) for the best cell ('french', 8, 1.0)

### stim 0 — topic Tropical Storm Brenda (1960)

**V0 (round 1):**
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**steered ('french', 8, 1.0)** (parse_ok=True, french_frac=0.05, words=90, cos(AR,h)=0.896):
```
Meteorological report structure with numbered storm tracks detailing Hurricane Sandy's path, presenting sequential storm data with precise numerical details and storm surge measurements.

The sentence ending "The storm then made a second inland landfall and a second tropical landfall" continues listing storm events, completing the final landfall sequence with a third landfall location and its timing.

Final token "landfall" ends an incomplete clause ("made a second touchdown"), expecting continuation describing the third landfall's location or outcome, likely "in the Gulf of Mexico near Cape Hatteras" or "on the eastern coast."
```

### stim 7 — topic Etymology of Wicca

**V0 (round 1):**
```
Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
```
**steered ('french', 8, 1.0)** (parse_ok=True, french_frac=0.05, words=93, cos(AR,h)=0.856):
```
Formal Wikipedia article structure with academic tone establishes a definitional entry on Catholicism, detailing a theological movement's identity and classification.

The sentence mid-development ("Thus, the Anglican tradition is considered to be a distinct denomination within Protestantism, sharing common liturgical rites and theological beliefs and shared liturgical rites and practices") continues listing shared characteristics, with a clause describing shared traditions.

Final token "practices" ends an incomplete list ("with common liturgical rites and religious beliefs and similar rituals and religious practices"), expecting continuation like "with those of the early Anglican tradition" or "that are similar."
```

### stim 19 — topic Richard Nixon presidential campaign, 1968

**V0 (round 1):**
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
```
**steered ('french', 8, 1.0)** (parse_ok=True, french_frac=0.02, words=88, cos(AR,h)=0.913):
```
Historical encyclopedia entry format with academic political analysis, detailing Republican presidential campaign data from 1932, listing electoral performance and voting trends.

The sentence structure "His popularity was strong early in the campaign, his support grew... his support" suggests a third clause describing Roosevelt's campaign performance or voter demographics, with an incomplete description of his electoral standing or popular vote.

Final token "support" ends mid-clause ("His support... his support"), expecting continuation describing his vote or his electoral standing, likely "spread across rural areas" or "was sustained despite economic downturn."
```

### stim 33 — topic Hurricane Lorenzo (2007)

**V0 (round 1):**
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
```
**steered ('french', 8, 1.0)** (parse_ok=True, french_frac=0.16, words=99, cos(AR,h)=0.927):
```
News article format with bullet points listing storm casualties in Haiti, detailing disaster events with official statistics and eyewitness accounts, continuing a disaster report structure.

The sentence ending "Three people died in a vehicle crash, one died after a mudslide in a tent" describes a specific incident, with a final example of a tragic death involving a vehicle accident or household destruction.

Final token "a" is mid-phrase ("in a"), part of an incomplete noun phrase listing casualties or bizarre incidents ("A family died in a snowstorm"), expecting a concrete example like "a frozen water tank" or similar tragic detail.
```


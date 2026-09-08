# X1b summary — cross-layer full generations with the layer-20 AV (40 pilot stimuli; descriptive, no kill)

git c475bbde; settings in x1b_settings.json; generations in x1b_outputs.jsonl; per-item scores in x1b_scores.csv

- 80 generations (9.9 s each); block-20 row = the round-1 explanations on the same stimuli scored with the same rules; errors 0
- rules: quoted-final-token = a double-quoted span equals token_str; expecting-hit = first word of a quoted span after 'expecting' equals the target's top-1 next token (punctuation stripped); shuffled floor pairs stimulus i with the top-1 of (i+20) mod 40. The desk's block-20 figures (own 0.444, shuffled 0.029 [0.012, 0.056]) used an unverified rule and are not reproduced here by construction.

| block | parse_ok | CJK | quoted-final-token acc | expecting cands/expl | expecting hit (own top-1) | expecting hit (shuffled) | Jaccard vs L20 expl | cos(AR(desc), h_l) | cos(AR(desc), h_20) | cos(h_l, h_20) | words |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 16 | 1.000 | 0.000 | 0.725 [0.575,0.850] | 2.05 | 0.275 [0.150,0.400] | 0.025 [0.000,0.075] | 0.408 | 0.761 [0.746,0.774] | 0.883 [0.868,0.897] | 0.801 | 99 |
| 27 | 0.950 | 0.075 | 0.000 [0.000,0.000] | 2.42 | 0.175 [0.050,0.300] | 0.025 [0.000,0.075] | 0.177 | 0.100 [0.089,0.111] | 0.409 [0.381,0.434] | 0.156 | 93 |
| 20 (training) | 1.000 | 0.025 | 0.650 [0.500,0.800] | 2.45 | 0.450 [0.300,0.600] | 0.025 [0.000,0.075] | 1.000 | 0.893 [0.881,0.906] | 0.893 [0.881,0.906] | 1.000 | 100 |

## Four fixed examples (stimuli 0, 7, 19, 33)

### stimulus 0 (token 'fall'; target top-1 ' near')
- block 20 (round 1): Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
- block 16 (parse_ok=True, cjk=False): Structured weather forecast article with numerical data and storm track details, presenting sequential storm movement data for Hurricane Ivan with labeled sections.

The sentence ending "The storm moved inland again and made a second landfall near Cape Hatteras, then retreated back into the Gulf of Mexico before making another landfall" continues listing multiple landfall events, completing the third landfall description with similar details.

Final token "landfall" ends an incomplete clause ("made another landfall"), part of a series of sequential landfall events ("also made a second landfall...and then re-established a second landfall"), expecting "in the same area" or "at a different location with a smaller intensity."
- block 27 (parse_ok=False, cjk=False): <explanation>
Scientific/mathematical text with formatted data and plots, transitioning to a weather system context with a specific storm track.

The phrase "A radar plot indicates the storm's movement towards the east coast, resulting in a transition to a stationary state" is a citation format with a date and "PST" label, suggesting a numerical result or a third-party event's PDE status.

Final token "order)    " closes a parenthetical expression ("The probability of a 3603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603603

### stimulus 7 (token ' practices'; target top-1 ' with')
- block 20 (round 1): Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
- block 16 (parse_ok=True, cjk=False): Structured religious encyclopedia format with numbered definitions and scholarly tone establishes formal academic article pattern about a religious denomination.

The sentence mid-clause ("Thus, the Catholic Church defines a 'Jewish sect' as those who share common theological beliefs, liturgical rites and worship practices and shared theological beliefs and liturgical practices") mirrors an incomplete list describing characteristics of a unified tradition, continuing the definition of "Jewish mysticism."

Final token "practices" ends an incomplete enumeration ("similar theological beliefs and liturgical rites and ritual practices and shared rituals and religious practices"), strongly expecting "of the core" or "that are similar" or "to those of the tradition" to close the clause.
- block 27 (parse_ok=True, cjk=False): Structured Wikipedia-style definition format with numbered attributes describing a plant species, transitioning to a "flower" entry with a name and symbol.

The phrase "A certain species of plant may be classified as..." is a common template for a person's identity, followed by a "Hinduism" tag suggesting a cultural or identity-based identity, implying a "common" or "spiritual" identity statement.

Final token "sociable) and (then" is mid-sentence in a parenthetical identity declaration ("with the same or similar to 123: identical to..."), strongly expecting "a" or "the" followed by "a specific identity" or "a."

### stimulus 19 (token ' support'; target top-1 ' was')
- block 20 (round 1): Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
- block 16 (parse_ok=True, cjk=False): Historical article format with numbered entries detailing U.S. presidential election statistics, listing political party performance data for Franklin Roosevelt's first term.

The sentence structure "In the midterm election, his initial support was weak, but his campaign grew steadily. His support" appears to be mid-description of Roosevelt's electoral performance metrics or political characteristics, continuing a clause listing his vote outcomes or behavior.

Final token "support" ends an incomplete clause ("His support..."), part of a list of Roosevelt's performance details ("His support... his support"), likely continuing with "expanded beyond rural areas" or "was undermined by..." or "included a peak vote count," completing the narrative about his electoral trajectory.
- block 27 (parse_ok=True, cjk=False): Structured historical data format with numbered statistics listing political party vote trends, likely a Wikipedia or chart tool display.

The phrase "2015: Rising popularity with 125M votes. A rising vote" suggests a third entry in a sequence of vote counts, likely a third acronym or trend label ("Voting index"), implying a decline or resurgence of a specific party's popularity.

Final token "vourise" is mid-word ("a high ranking with a rising vote"), part of a third statistic entry ("A rising rank: 1250+ votes"), strongly expecting "count" or "widened" or "in the US" to complete the noun phrase.

### stimulus 33 (token ' a'; target top-1 ' mud')
- block 20 (round 1): News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
- block 16 (parse_ok=True, cjk=False): Formal news report format with numbered casualties listing from a US government disaster report, presenting statistical data with quoted eyewitness accounts from Argentina's earthquake.

The sentence ending "Other casualties included: Some Venezuelan refugees died in a car crash during the quake" gives a specific example of a death or accident consequence, listing a tragic personal incident with a concrete detail ("a family died in a").

Final token "a" is an indefinite article mid-clause ("in a"), part of a quoted casualty example ("One Venezuelan died in a..."), expecting a noun like "vehicle accident" or "flood" or "water-related drowning" or "house collapse" describing the family's fatal circumstance.
- block 27 (parse_ok=True, cjk=False): Technical Python error format with Stack Overflow context, suggesting a code snippet or error message about memory exhaustion in a Linux/Unix environment.

The phrase "The question is : 'Error: Memory Exhaustion due to a flood of requests' implies that the event is about the destruction of a session or dataset" mirrors the pattern "P1: Calculate the total memory usage," strongly implying the same query about a crash.

Final token "P1" is mid-expression ("GHC1: 101:GHC"), directly continuing the error scenario description, expecting "...crash" or "...of the dataset' or "...time' or "two events" completing the query.


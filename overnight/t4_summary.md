# T4 summary — perturbing the injected vector with TARGET concept directions (pilot 0–39)

git 1eb77c29; settings in t4_settings.json; items in t4_outputs.jsonl; directions in out/t4_dirs.npz

- items 360 (errors 0); 10.0 s/item; stopped at stimulus None (None = all 40 done)
- direction geometry: ||d_sports|| 25.7, ||d_french|| 40.4, cos(d_sports, d_french) 0.007; cos(d, mean h20): sports 0.012, french -0.018
- prior art: LessWrong 'Models are blind outside the J-space. NLAs aren't.' (Llama-3.3-70B, L53 NLA, diff-of-means concept vectors injected norm-matched; NLA named the concept 100 %, n=16, 0 false positives). T4 is a replication/control on this 7B pair.

## Kill T4

β=0.25: sports mention 1.000 [1.000,1.000] (above); β=0.5: sports mention 1.000 [1.000,1.000] (above) → **NOT MET**
- baseline (unperturbed round-1 explanations, pilot): sports mention 0.125, french pass 0.000, topic preserved 0.025, mean words 99.7

## Grid (mean over pilot stimuli; CI by stimulus where shown)

| direction | β | n | cos(h,h') | angle° | sports mention [CI] | french pass | french frac | topic preserved | parse_ok | cjk | words | seq-sim V0 | Jaccard V0 | cos(AR,h) | cos(AR,h') | cos(AR,h) − cos V0 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sports | -0.5 | 40 | 0.948 | 18.5 | 0.075 [0.000,0.175] | 0.000 | 0.076 | 0.050 | 1.000 | 0.000 | 98.8 | 0.461 | 0.395 | 0.8832 | 0.8453 | -0.0102 |
| sports | -0.25 | 40 | 0.981 | 11.3 | 0.100 [0.025,0.200] | 0.000 | 0.077 | 0.025 | 1.000 | 0.000 | 99.5 | 0.531 | 0.453 | 0.8882 | 0.8740 | -0.0052 |
| sports | +0.25 | 40 | 0.949 | 18.4 | 1.000 [1.000,1.000] | 0.025 | 0.074 | 0.025 | 1.000 | 0.025 | 100.0 | 0.444 | 0.366 | 0.8742 | 0.8411 | -0.0192 |
| sports | +0.5 | 40 | 0.710 | 44.8 | 1.000 [1.000,1.000] | 0.000 | 0.084 | 0.000 | 1.000 | 0.000 | 99.2 | 0.313 | 0.238 | 0.7497 | 0.6366 | -0.1437 |
| french | -0.5 | 40 | 0.949 | 18.4 | 0.200 [0.100,0.325] | 0.000 | 0.076 | 0.025 | 1.000 | 0.025 | 100.9 | 0.490 | 0.433 | 0.8886 | 0.8458 | -0.0047 |
| french | -0.25 | 40 | 0.981 | 11.3 | 0.175 [0.075,0.300] | 0.000 | 0.072 | 0.000 | 1.000 | 0.000 | 99.4 | 0.535 | 0.473 | 0.8906 | 0.8745 | -0.0028 |
| french | +0.25 | 40 | 0.948 | 18.5 | 0.150 [0.050,0.275] | 0.725 | 0.179 | 0.000 | 1.000 | 0.000 | 94.1 | 0.377 | 0.310 | 0.8207 | 0.8224 | -0.0727 |
| french | +0.5 | 40 | 0.704 | 45.3 | 0.150 [0.050,0.275] | 0.950 | 0.226 | 0.000 | 1.000 | 0.050 | 92.2 | 0.260 | 0.218 | 0.7653 | 0.6616 | -0.1280 |
| random | +0.5 | 40 | 0.707 | 45.0 | 0.175 [0.075,0.300] | 0.050 | 0.079 | 0.000 | 1.000 | 0.000 | 99.3 | 0.340 | 0.299 | 0.8435 | 0.6044 | -0.0499 |

## Sports keywords hit (positive β), counts over items

- β=0.25: sports:36, player:15, football:13, team:9, season:5, cricket:5, baseball:5, basketball:4, game:4, sport:4, athlete:4, rugby:3, score:3, athletic:3, soccer:3, tennis:3, matches:3, match:3, games:2, players:2, medal:2, olympic:2, tournament:2, touchdown:1, stadium:1, playoffs:1, hockey:1, scored:1, goal:1, captain:1, championship:1
- β=0.5: sports:38, player:36, score:17, team:16, football:15, goal:15, game:14, basketball:14, match:14, scored:12, hockey:8, soccer:7, goals:7, rugby:6, cricket:4, championship:4, sport:4, athlete:3, tennis:3, olympics:3, medal:3, tournament:3, touchdown:2, penalty:2, league:2, teams:1, season:1, matches:1, arena:1, stadium:1, athletic:1, boxing:1, games:1, olympic:1, sprinter:1, wickets:1, sprint:1
- random β=0.5: player:4, baseball:3, score:2, athlete:2, football:2, goals:1, athletic:1, basketball:1, sports:1, game:1, games:1, medal:1, olympic:1, cricket:1

## Four fixed examples (stimuli 0, 7, 19, 33; sports β=+0.5 and french β=+0.5 vs unperturbed)

### stim 0 — topic Tropical Storm Brenda (1960)

**unperturbed (round 1):**
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**sports β=+0.5** (cos(h,h')=0.726, sports=True, french_frac=0.10, cos(AR,h)=0.613, seq-sim=0.25):
```
Sports statistics article format with NFL game log structure, detailing player performance metrics for the USA team during a record-breaking heat wave.

The final sentence "His third game of the night saw the Heat registering a second touchdown and a late comeback win, before finishing with a touchdown" lists two final touchdown events, completing a sequence of US soccer's final scoring moments including a beach touchdown.

Final token "touchdown" ends an incomplete clause ("a second touchdown tallied a beach touchdown and a re-touching"), strongly expecting "in the Bahamas" or "at the Dallas Mavericks" or "with a score of 89-88" — a specific ending location or score detail.
```
**french β=+0.5** (cos(h,h')=0.695, sports=False, french_frac=0.28, cos(AR,h)=0.754, seq-sim=0.17):
```
French meteorological report format with numbered stages describing Atlantic storm tracks, detailing successive landfalls along the French coast.

The sentence structure "La troisième phase de la traversée a ensuite quitté la Manche par la côte sud, avant une seconde arrivée... La troisième traversée a également touché la côte française" mirrors a list of landfall dates, completing a fourth.

Final token "landfallLa" is mid-phrase ("une nouvelle arrivée se produisait et une nouvelle landfall touchait"), expecting "à Saint-Malo" or "en Normandie le 15 octobre" to close the final landfall.
```

### stim 7 — topic Etymology of Wicca

**unperturbed (round 1):**
```
Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
```
**sports β=+0.5** (cos(h,h')=0.698, sports=True, french_frac=0.03, cos(AR,h)=0.777, seq-sim=0.32):
```
Sports article format with Wikipedia-style structure detailing a basketball team's social media ranking, using formal sports analytics terminology.

The sentence mid-clause "The IAAF have declared the Irish team as a super-set of the NBA's 'Big Three' style, meaning they must display dominant scoring and similar basketball tactics and basketball practices" lists a specific criteria clause about shared characteristics and scoring style.

Final token "practices" ends an incomplete clause ("that possess similar scoring and high basketball speed and technical basketball practices and rushing goals and basketball practices"), strongly expecting "against the Australian team" or "with the traditional Australian team" or "that are considered" or "against the core characteristics."
```
**french β=+0.5** (cos(h,h')=0.700, sports=False, french_frac=0.21, cos(AR,h)=0.764, seq-sim=0.23):
```
French Wikipedia article structure with formal academic register defining Catholicism, listing criteria for "chrétien moderne" identity.

The sentence "Il s'agit donc d'une religion catholique moderne qui partage des pratiques liturgiques, des croyances ou des rites communs, avec des pratiques et pratiques propres" mirrors a list pattern describing shared characteristics and common elements.

Final token "pratiques practices" ends mid-clause ("qui possèdent des rites, des pratiques liturgiques et des pratiques et pratiques practices"), strongly expecting "." or "." or "of those of the Catholic Church" or "are similar."
```

### stim 19 — topic Richard Nixon presidential campaign, 1968

**unperturbed (round 1):**
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
```
**sports β=+0.5** (cos(h,h')=0.723, sports=True, french_frac=0.07, cos(AR,h)=0.751, seq-sim=0.37):
```
Sports statistics article format with historical data structure, listing NFL player performance metrics for the 1960 Winter Olympics.

The sentence "While his team was trailing 82-65 at halftime, Jordan's dominance earned him the MVP award; his support" suggests a specific statistic or outcome clause describing LeBron James's performance peak, likely a closing score or dominance claim about his championship.

Final token "support" ends mid-clause ("his support"), part of a list of performance outcomes ("At his peak, his score..."), expecting a noun phrase like "was shattered" or "led to a record-breaking lead" or "included a combined score against."
```
**french β=+0.5** (cos(h,h')=0.704, sports=True, french_frac=0.20, cos(AR,h)=0.800, seq-sim=0.28):
```
Historical French political biography format with academic tone, detailing Gaullist presidential campaign figures and electoral dynamics around 1962.

The sentence structure "Son score est de 25% en mai, son soutien est stable. Son support" describes a French candidate's vote trajectory, implying a third clause showing the candidate's positive momentum or regional support figures.

Final token "support" ends mid-clause ("Sa soutien... son support... son support..."), part of a list of vote sources ("Sa popularité en octobre, 35%... son support"), strongly expecting "est monté" or "was concentrated on left-wing issues" or similar.
```

### stim 33 — topic Hurricane Lorenzo (2007)

**unperturbed (round 1):**
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
```
**sports β=+0.5** (cos(h,h')=0.709, sports=True, french_frac=0.14, cos(AR,h)=0.789, seq-sim=0.28):
```
Sports news article format with statistical data presented in a structured list format, detailing NFL record-breaking performances from the 2014 Winter Olympics.

The final example "Australia's cricket team recorded a victory in a snowstorm" is mid-sentence listing specific injury incidents, with a concrete example of a player's fatal collision ("a player scored in a single") suggesting a basketball score.

Final token "a" is an indefinite article mid-clause ("in a collision in a hockey match he died in a goalless"), requiring a noun phrase describing a specific injury or dramatic event, likely "basketball crash" or "foul" or "goal" or "fatal heart attack."
```
**french β=+0.5** (cos(h,h')=0.695, sports=False, french_frac=0.29, cos(AR,h)=0.832, seq-sim=0.23):
```
French news report format with historical dates and bullet points detailing a winter storm in France, listing casualties and incidents.

The sentence structure "Trois personnes mortes dans un accident de voiture en France en janvier 1994 : une maison s'est effondrée en Suisse, une victime a dormi dans un incendie..." ends with a specific French-language death scenario describing a third incident.

Final token "une" is an indefinite article mid-clause ("Dans un accident de glace en 1995 : dans un malade en la"), requiring a noun phrase like "collision" or "fuite d'eau" or "household fire."
```


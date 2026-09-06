# S5 summary — prompt steering on the 40 pilot stimuli

git 92e4d3cd; settings in s5_settings.json

Judge columns (`followed`, `same_referent`) are an LLM-as-judge score produced by the orchestrating agent under the fixed rubric in PLAN.md S5, read side by side with V0; they are not human labels.

| variant | mech pass rate | judge followed | judge same_referent | mean cos_Vk | mean cos_Vk − cos_V0 | median cos_Vk − cos_V0 | parse_ok | cjk | mean n_tokens |
|---|---|---|---|---|---|---|---|---|---|
| V0 | — | — | — | 0.8934 | 0.0000 | 0.0000 | 1.000 | 0.025 | 144.4 |
| V1 | — | — | — | 0.8919 | -0.0014 | -0.0001 | 1.000 | 0.025 | 139.2 |
| V2 | — | — | — | 0.8936 | 0.0003 | 0.0002 | 1.000 | 0.025 | 137.5 |
| V3 | 0.000 (n=40) | — | — | 0.8899 | -0.0035 | -0.0010 | 1.000 | 0.025 | 144.9 |
| V4 | 0.000 (n=40) | — | — | 0.8901 | -0.0032 | -0.0014 | 1.000 | 0.025 | 142.2 |
| V5 | 0.000 (n=40) | — | — | 0.8923 | -0.0010 | -0.0011 | 1.000 | 0.000 | 179.3 |

- V4 mean french_frac: 0.072
- V5 first-word distribution: {'Historical': 13, 'British': 3, 'Wiki': 3, 'Indian': 2, 'Formal': 2, 'Wiki-style': 2, 'Encyclopedic': 2, 'Narrative': 2, 'Meteorological': 1, 'Scientific': 1, 'Bulgarian': 1, 'Hip-hop': 1, 'Historical/heritage': 1, 'Australian': 1, 'Structured': 1, 'Sports': 1, 'Video': 1, 'News': 1, 'American': 1}; agreement with content-word rule among mech-pass items: nan (n=0); token_is_content_word rate: 0.500
- V3 explanations word-count distribution: {84: 1, 86: 1, 90: 3, 91: 1, 92: 1, 93: 3, 95: 2, 96: 1, 97: 1, 98: 3, 99: 1, 100: 1, 101: 3, 102: 4, 103: 1, 104: 3, 105: 2, 106: 2, 108: 1, 109: 1, 110: 1, 111: 2, 113: 1}

## Kill test

- 2026-09-06T05:07:22  S5  K5  threshold=follow_rate(V3+V4 mechanical) < 0.25  observed=follow_rate=0.0000 CI95=[0.0000,0.0000] n=80 (V3 0.000, V4 0.000)  MET  MET would mean the describer ignores instruction text at inference time

## Verbatim examples: positions 0, 7, 19, 33

### stim 0 (doc 391, pos 437) token='fall'

context: " 29 , while situated south of Wilmington . Several hours later , the storm emerged over the Chesapeake Bay moving northeast at about 30 mph ( 48 km / h ) . Brenda crossed the Delmarva Peninsula and rapidly tracked into southern New Jersey . The storm crossed the state and eventually made another land" [["fall"]] " on Long Island before making yet another landfall in coastal Connecticut . \n At around"

**V0** (cos=0.904, parse_ok=True, mech=None):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
**V1** (cos=0.904, parse_ok=True, mech=None):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods showing wind speeds and movement.

The final sentence "The third storm surge moved inland again and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a list of four landfall locations with a final one expected.

Final token "landfall" ends mid-clause ("made a second landfall"), part of a final event sequence clause listing multiple landfall locations ("The system also made a second landfall..."), strongly expecting "in the Gulf Coast near [location]" or "on the eastern coast around midnight."
```
**V2** (cos=0.900, parse_ok=True, mech=None):
```
Weather report format with detailed storm track data and numerical statistics, continuing a chronological sequence of tropical storm movements along the Gulf Coast.

The final sentence "The fourth storm surge made a second landfall near Cape Hatteras, before a final inland track and another tropical landfall" mirrors earlier enumeration of landfall locations, completing the fourth event's final landing details.

Final token "landfall" ends mid-clause ("made another second landfall"), part of a list of sequential landfall events, strongly expecting "in the Florida Panhandle around" or "on the Gulf Coast near late Saturday morning" or "in the Atlantic Ocean shortly after."
```
**V3** (cos=0.902, parse_ok=True, mech=False):
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, maintaining chronological narrative structure with numerical statistics.

The sentence ending "The fourth storm surge moved inland a second time and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a final landfall event sequence listing multiple locations and times.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event list item describing the fourth storm's final landfall location, strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM" or similar geographic detail.
```
**V4** (cos=0.902, parse_ok=True, mech=False):
```
Weather report format with detailed storm track data structure, presenting sequential storm events for Hurricane Florence with numbered periods and storm surge measurements.

The final sentence "The fourth landfall was then tracked inland before a second surfacing along the Florida Panhandle, with a final landfall" mirrors earlier descriptions of multiple landfall locations, completing the final storm path sequence.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a list of sequential landfall events ("The system also made a second landfall..."), strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM" or similar.
```
**V5** (cos=0.901, parse_ok=True, mech=False):
```
Meteorological report format with detailed storm track data listing sequential landfall events for Hurricane Florence, maintaining chronological narrative structure with numbered entries.

The final sentence "The fourth storm surge moved inland a second time and made a second landfall along the Florida Panhandle" mirrors earlier landfall descriptions, completing a list of four landfall locations with the final event expected to describe a third or final landfall point.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final landfall sequence listing multiple events ("The system also made a second landfall"), strongly expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```

### stim 7 (doc 293, pos 497) token=' practices'

context: "ca that have been used in Paganism and Pagan studies since circa 1980 . The first developed in England during the 1960s . Broad and inclusive , it covers most , if not all , forms of modern Pagan Witchcraft , especially if they share sufficient theological beliefs and ritual" [[" practices"]] " to be considered denominations within a common religious movement . In contrast ,"

**V0** (cos=0.880, parse_ok=True, mech=None):
```
Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
```
**V1** (cos=0.872, parse_ok=True, mech=None):
```
Wiki-style article format with academic/encyclopedic tone discussing religious identity, defining "Anglicanism" as a denomination.

The sentence structure "Thus, the broader 'Orthodox' designation is often used to describe those Christians who share common liturgical traditions and theological beliefs and shared rites and practices" mirrors a clause listing shared characteristics, continuing the definitional enumeration.

Final token "practices" ends mid-clause ("with similar liturgical rites and theological beliefs and shared rites and religious practices"), strongly expecting "with the Catholic Church" or "that are considered traditional" or "to those of the Anglican tradition" completing the definitional clause.
```
**V2** (cos=0.884, parse_ok=True, mech=None):
```
Formal wiki article structure with academic tone defining "Anglicanism," listing theological definitions and subcategories of Protestantism.

The sentence mid-clause ("Thus, the Catholic Church is considered to be a 'high church' denomination that shares many liturgical traditions and shared theological beliefs and practices") mirrors a definition clause listing shared characteristics, continuing enumeration of Unitarianism's criteria.

Final token "practices" ends an incomplete list ("with similar liturgical traditions and shared theological beliefs and ritual practices"), strongly expecting "with the Anglican tradition" or "that are common to the early Church" or "to those of the core tradition."
```
**V3** (cos=0.884, parse_ok=True, mech=False):
```
Formal Wikipedia article structure with academic tone defining "Anglicanism," listing theological definitions and subcategories of Protestantism.

The sentence mid-clause ("Thus, the term 'Orthodox Anglicanism' is often used to describe those churches that share common liturgical traditions and theological beliefs and practices") mirrors a defining clause listing shared characteristics, continuing the enumeration of shared rites and traditions.

Final token "practices" ends an incomplete clause ("that share similar liturgical rites and theological practices and shared rites and religious practices"), strongly expecting "with the Anglican tradition" or "that are considered traditional" or "to the broader Anglican tradition," completing the definitional criteria.
```
**V4** (cos=0.871, parse_ok=True, mech=False):
```
Formal Wikipedia article structure with academic tone discussing religious identity and Catholicism, defining "Anglican Catholicism" with scholarly citations.

The sentence mid-clause ("Thus, the Anglican Catholic Church is generally considered to be a distinct denomination sharing common liturgical traditions and theological beliefs and practices") mirrors a list pattern describing shared characteristics of early Anglicanism.

Final token "practices" ends an incomplete clause ("those shared liturgical and ritual traditions and similar theological beliefs and liturgical practices and shared rituals and common practices"), strongly expecting "with the Anglican tradition" or "that are characteristic" or "to those of the broader tradition" to complete the definitional clause.
```
**V5** (cos=0.871, parse_ok=True, mech=False):
```
Formal Wikipedia-style article structure with academic tone discussing religious identity and Catholicism, defining "Anglicanism" as a denomination.

The sentence mid-clause ("Thus, the term 'Orthodox Anglicanism' is often defined as those churches sharing common liturgical traditions and theological beliefs and practices") mirrors a parenthetical clause listing shared characteristics, continuing the definition of "Anglo-Catholicism."

Final token "practices" ends an incomplete list ("with similar liturgical traditions and shared theological beliefs and liturgical practices and common rituals and practices"), strongly expecting "with the Anglican tradition" or "that are considered traditional" or "to those of the broader tradition."
```

### stim 19 (doc 592, pos 254) token=' support'

context: " Republican National Convention , where he named Governor Spiro Agnew of Maryland as his running mate . \n In the general election , Nixon emphasized \" law and order , \" positioning himself as the champion of what he called the \" silent majority . \" Running well ahead of his opponent , incumbent Vice President Hubert Humphrey , his" [[" support"]] " slipped in the polls following his refusal to partake in presidential debates , and following"

**V0** (cos=0.909, parse_ok=True, mech=None):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a list of campaign dynamics or vote outcomes, likely describing rural or conservative vote shifts or a peak.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote totals ("Though his initial numbers were strong, his support"), expecting continuation like "was sustained" or "extended into the electoral vote" or "included a backlash against depression."
```
**V1** (cos=0.907, parse_ok=True, mech=None):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential campaign of 1932, listing electoral outcomes and party dynamics.

The sentence structure "While Roosevelt's popularity was initially weak, his campaign gained strength in the North, his support" suggests a third clause describing his vote performance or swing, likely continuing with a contrasting or specific event detail about his popularity.

Final token "support" ends mid-clause ("His support... his support"), part of a list of vote characteristics ("Though his initial numbers were strong, his support"), expecting continuation like "expanded into the South" or "was undermined by economic conditions."
```
**V2** (cos=0.902, parse_ok=True, mech=None):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential campaign of 1932, listing electoral statistics and party dynamics.

The sentence structure "While Roosevelt's initial popularity was strong, his campaign was largely regional, his support" suggests a continuation describing his vote performance or decline, likely listing specific factors or peak support figures.

Final token "support" ends mid-clause ("His support... his support"), part of a quoted description of Roosevelt's early vote trajectory ("Though his initial popularity was strong, his support"), expecting continuation like "expanded into the electoral vote" or "was undermined by economic conditions" or "included independents."
```
**V3** (cos=0.909, parse_ok=True, mech=False):
```
Historical encyclopedia article format with academic political analysis tone detailing a presidential campaign's electoral performance, listing primary sources and statistics.

The sentence structure "While Roosevelt's Republican nomination was strong early, his popularity surged during the summer, his support" suggests a continuation describing his vote totals or political trajectory, likely completing a contrasting or nuanced outcome clause about rural or regional backing.

Final token "support" ends mid-clause ("His support... his support"), part of a list of campaign characteristics ("Though his initial vote totals were strong, his support"), strongly expecting a verb phrase like "expanded into" or "was undermined by" or "included a strong electoral swing" or similar.
```
**V4** (cos=0.908, parse_ok=True, mech=False):
```
Historical encyclopedia article format with academic political analysis tone, detailing Republican presidential candidate Hoover's campaign performance during the 1932 election.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the primary season; his support" suggests a list of electoral outcomes or factors, likely describing his vote totals or shifting demographics.

Final token "support" ends mid-clause ("His support... his support"), part of a clause describing Roosevelt's performance pattern ("Though initially lagging, his vote totals grew"), expecting continuation like "was sustained by" or "extended into a conservative backlash" or "included rural voters" or similar outcome description.
```
**V5** (cos=0.909, parse_ok=True, mech=False):
```
Historical encyclopedia article format with academic political analysis detailing a presidential campaign's electoral performance, listing primary sources and statistics about Republican candidate Alf Landon.

The sentence structure "His initial popularity was strong, with Roosevelt's support growing throughout the summer; his support" suggests a clause describing election dynamics or vote distribution, likely continuing with a contrasting or concluding detail about his vote totals or regional appeal.

Final token "support" ends mid-clause ("His support... his support"), part of a list of campaign characteristics ("Though initially lagging, his vote totals..."), strongly expecting a noun phrase like "expanded into a landslide" or "was undermined by economic factors" or "included independents."
```

### stim 33 (doc 168, pos 303) token=' a'

context: " Between Veracruz and neighboring Hidalgo , there were 123 @,@ 320 people affected across 112 municipalities . Overall there were six deaths in the country , one in Veracruz and five in Puebla . In the latter state , a family of three perished in" [[" a"]] " landslide . \n \n = = Meteorological history = = \n \n The origins of Hurricane Lorenzo"

**V0** (cos=0.926, parse_ok=True, mech=None):
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with details about Hurricane Tomas's impacts in Colombia.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the storm" lists a specific tragic event detail ("A family died in a freezer-related accident"), suggesting a final example of disaster-related death or damage.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food shortage-related accident."
```
**V1** (cos=0.926, parse_ok=True, mech=None):
```
News article format with translated disaster report listing weather-related deaths in Venezuela, presenting bullet-pointed storm statistics with quoted eyewitness accounts.

The final item "Other deaths included a mudslide victim who died in a vehicle crash, and one died in a freeze" is mid-sentence describing specific incidents, with a specific tragic detail about a family's death circumstance involving a collapsed structure.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a third specific example listing deaths ("A family died in a freeze in a..."), expecting a noun like "fire" or "water container accident" or "ice-related collapse."
```
**V2** (cos=0.929, parse_ok=True, mech=None):
```
News article format with translated disaster report listing storm casualties and incidents in Venezuela, presenting numbered bullet points with specific details about Hurricane Tomas impacts.

The final sentence "Other deaths included a family of four killed in a landslide, and one died in a vehicle crash during the freeze" describes a specific tragic event with a third example of disaster-related deaths or damage details.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific example list item describing a fatal accident circumstance ("A family died in a freezer during the storm"), expecting a noun like "gas explosion" or "collapsed shelter" or "water-related accident."
```
**V3** (cos=0.927, parse_ok=True, mech=False):
```
News article format with translated disaster report listing storm casualties in Venezuela, presenting numbered incidents with specific details about weather conditions and fatalities.

The sentence ending "Other deaths included a mudslide victim who died in a vehicle crash, and another died in a freeze-related incident" lists a specific tragic detail ("A family died in a collapsed shelter"), suggesting a final example of a secondary disaster or accident circumstance.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail clause listing causes ("A family died in a..."), expecting a noun like "fire" or "icefall" or "vehicle accident" or "water container collapse."
```
**V4** (cos=0.928, parse_ok=True, mech=False):
```
English news report format with translated disaster statistics listing storm casualties in Venezuela, presenting bullet-pointed incidents from a Mexican weather agency.

The sentence ending "Other deaths included two people killed in a flood in a vehicle, and one died in a collapse during the earthquake" describes a specific tragic detail ("A family died in a freezer accident"), suggesting a final example of disaster-related casualties or accident.

Final token "a" is an indefinite article mid-clause ("In one case died in a"), part of a specific casualty detail listing, expecting a noun like "fire" or "vehicle crash" or "icebox collapse" or "food poisoning incident," completing the accident scenario.
```
**V5** (cos=0.929, parse_ok=True, mech=False):
```
News article format with translated disaster report listing storm casualties and weather statistics, presenting bullet-pointed incidents with specific details from Mexico's Hurricane Stan.

The final clause "Other deaths included a family of four freezing to death in a vehicle crash, and one died in a landslide" is mid-sentence describing a specific fatal incident detail, listing a third example of disaster-related casualties or unusual circumstances.

Final token "a" is an indefinite article mid-clause ("In one died in a"), part of a specific casualty detail ("A family died in a freezer during the storm in a"), expecting a noun like "fire" or "vehicle crash" or "ice-related accident" or "water container."
```


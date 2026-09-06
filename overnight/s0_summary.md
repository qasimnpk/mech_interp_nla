# S0 summary — library + stimuli + 16-position smoke

git 99f8f955; settings in s0_settings.json

## Timings / memory

- target_load_s: 4.48
- rss_after_target_G: 4.97
- stimuli_build_s: 3.15
- acts_cache_s: 225.40
- rss_after_target_free_G: 0.69
- av_load_s: 5.02
- rss_after_av_G: 4.96
- av_sec_per_explanation: 10.02
- rss_after_av_free_G: 0.61
- ar_load_s: 3.67
- rss_after_ar_G: 1.28
- ar_sec_per_score: 0.35

## Stimuli

- train docs: 629; eligible (>= 300 tokens): 610; chosen: 200
- seq_len (after 512 truncation) mean 510.4, min 327, max 512
- pos mean 276.1, min 18, max 510; |pos2-pos| min 8
- act_norm (h20) mean 113.3, p10 102.5, p90 124.4, max 140.2

## K0

- cjk_rate = 0.062; parse_ok rate = 1.000 (n=16)
- 2026-09-06T02:27:06  S0  K0  threshold=cjk_rate>0.25  observed=cjk_rate=0.062 (1/16), parse_ok=1.000  NOT MET  injection on raw-text activations: MET would mean the AV is describing the marker glyph

## 16 smoke positions

| stim | doc | pos | token | act_norm | n_tok | parse_ok | cjk | cos |
|---|---|---|---|---|---|---|---|---|
| 0 | 391 | 437 | `'fall'` | 126.2 | 145 | True | False | 0.904 |
| 1 | 358 | 269 | `' of'` | 107.1 | 143 | True | False | 0.820 |
| 2 | 601 | 168 | `'ym'` | 105.8 | 146 | True | False | 0.955 |
| 3 | 452 | 53 | `'ats'` | 112.1 | 145 | True | False | 0.874 |
| 4 | 354 | 102 | `' plot'` | 123.8 | 140 | True | False | 0.939 |
| 5 | 147 | 338 | `' Up'` | 114.8 | 144 | True | False | 0.907 |
| 6 | 553 | 265 | `' Atlantic'` | 115.9 | 143 | True | False | 0.809 |
| 7 | 293 | 497 | `' practices'` | 118.8 | 147 | True | False | 0.880 |
| 8 | 42 | 329 | `' those'` | 126.9 | 145 | True | False | 0.915 |
| 9 | 229 | 293 | `' ,'` | 104.8 | 140 | True | False | 0.785 |
| 10 | 74 | 153 | `'on'` | 108.7 | 142 | True | False | 0.858 |
| 11 | 399 | 348 | `' and'` | 117.6 | 144 | True | False | 0.894 |
| 12 | 457 | 211 | `' and'` | 116.8 | 143 | True | False | 0.940 |
| 13 | 117 | 290 | `'1'` | 97.2 | 145 | True | True | 0.922 |
| 14 | 472 | 395 | `' the'` | 107.9 | 146 | True | False | 0.935 |
| 15 | 454 | 435 | `' way'` | 123.5 | 148 | True | False | 0.898 |

cos: mean 0.890, median 0.901, min 0.785, max 0.955 (n=16)

## Explanations (verbatim, first 16)

### stim 0 token='fall' parse_ok=True cjk=False
```
Weather report format with detailed storm track data listing sequential landfall events for Hurricane Florence, structured with numbered periods and storm intensity details.

The final sentence "The fourth storm surge moved inland along the Florida Panhandle, with a second landfall occurring near Cape Hatteras" mirrors earlier landfall descriptions, completing a list of four landfall locations and likely a final one.

Final token "landfall" ends an incomplete clause ("made a second landfall"), part of a final event sequence listing multiple landfall points ("The system also made a second landfall..."), expecting "in the Gulf Coast near" or "on the eastern coast around 11:00 PM."
```
### stim 1 token=' of' parse_ok=True cjk=False
```
Encyclopedic article format with historical narrative describing a tunnel construction project, following Wikipedia-style structure with technical details about the Brooklyn Bridge.

The sentence "The workers completed the structure 6 months ahead of schedule, and the project was finished ahead of schedule, five months ahead of" mirrors a famous quote about schedule, establishing the completion date and deadline context.

Final token "ahead of" ends an incomplete phrase ("five months ahead of"), part of a parenthetical clause listing schedule violations ("completed more than 6 months ahead of schedule, five months ahead of"), strongly expecting "schedule" or "schedule" or "the scheduled date," completing the deadline claim.
```
### stim 2 token='ym' parse_ok=True cjk=False
```
Scientific article format with Wikipedia-style species description, listing historical and behavioral characteristics of the American black bear, with a quoted expert source mid-sentence.

The phrase "Some other species, like Thym" appears to be a scientific term or species name mid-list, likely referencing a specific plant or insect taxonomic term related to the stomach contents or digestive adaptations.

Final token "Thym" is a truncated word mid-term ("Thym"), part of a parenthetical scientific name list ("The species Thym"), suggesting continuation with "ylae" or "ylaeformis" or similar Latin term describing a specific plant or digestive variant, completing the quoted expert's unusual terminology.
```
### stim 3 token='ats' parse_ok=True cjk=False
```
Bulgarian language article format with historical context and image caption structure, presenting a military insignia with quoted historical terms.

The quoted term "Hrvatska Velika Armija" is mid-sentence describing a Croatian nationalist state name ("Kingdom of Croatia-Slavonia"), directly referencing the Croatian Kingdom's abbreviated name "Hrvatska Hrvats" from WWI.

Final token "Hrvats" is a truncated word mid-quote ("Kraljevina Hrvatska Hrvats"), part of a parenthetical historical name example, strongly expecting "ka" to complete the Croatian language name, likely followed by "ka" or "ka."
```
### stim 4 token=' plot' parse_ok=True cjk=False
```
Indian Wikipedia article format with film details listing a Bollywood movie titled "Kannada" with actor names and release details.

The phrase "The 2004 Indian film 'Kannada' is a thriller film directed by S. S. Rajamouli. The plot" suggests an enumeration or description of story elements or plot details follows, likely continuing about the film's narrative or genre.

Final token "plot" is mid-phrase ("The plot"), part of a list of attributes ("The plot"), expecting continuation like "is based on..." or "of the film revolves around..." or "and other elements deal with a murder mystery."
```
### stim 5 token=' Up' parse_ok=True cjk=False
```
Historical music video compilation format with hip-hop artist credentials listing, featuring retro clips and song titles around Aretha Franklin's iconic status.

The phrase "And Then There's The Album : Pick Up" appears to be a song title or lyric reference, likely a culturally-aware joke or album title suggesting a woman's attitude or behavior, continuing a list of songs or quotes.

Final token "Pick Up" is mid-title ("Pick Up"), part of a quoted lyric or phrase ("Pick Up"), likely completing a song title like "Pick Up The Pieces" or "The Girl" or similar slang phrase about a female's reputation or fan behavior, expecting continuation of a comedic list.
```
### stim 6 token=' Atlantic' parse_ok=True cjk=False
```
Historical article format with structured Wikipedia-style images and captions, detailing a U.S. agricultural vessel's construction and historical significance.

The sentence ending "The theory that the Atlantic" is mid-quote describing a migration route claim, listing historical origins connecting the Mississippi River to the Atlantic Ocean, with the phrase "from the Atlantic" defining a geographic origin for colonial settlers' eastward expansion.

Final token "Atlantic" is mid-phrase in a quoted historical definition ("from the Atlantic"), part of a parenthetical clause listing historical origins ("between the Atlantic"), expecting "Ocean to the Pacific" or "Ocean to the Atlantic Ocean" or "and the Atlantic to the Gulf."
```
### stim 7 token=' practices' parse_ok=True cjk=False
```
Wiki article format with academic/encyclopedic tone discussing Catholicism's "Anglican Communion" definition, establishing structured definitions and theological frameworks.

The sentence mid-clause ("Thus, the Anglican tradition is considered a distinct 'high church' denomination that shares common liturgical beliefs and rites and shared liturgical practices") mirrors a list describing core characteristics of Unitarianism.

Final token "practices" ends an incomplete clause ("those that share similar theological beliefs and liturgical beliefs and rites and shared liturgical practices and"), strongly expecting "with the Anglican tradition" or "that are common" or "to those of the early Church" to complete the definitional clause.
```
### stim 8 token=' those' parse_ok=True cjk=False
```
British archaeological article structure: academic blog format detailing a medieval cemetery excavation, with numbered findings describing a Roman burial site's skeletal evidence.

The sentence "Analysis of the burial assemblage however suggests that the remains date to the later period, and those identified as human remains are those" continues a specific claim about the skeletal occupants' identity, listing known human remains characteristics.

Final token "those" is mid-clause ("are those"), completing a quoted claim about skeletal remains' identity ("The evidence indicates that the remains are those"), immediately requiring a noun phrase like "of a female" or "of multiple individuals of a non-Christian faith" or "of a deceased adult and infant."
```
### stim 9 token=' ,' parse_ok=True cjk=False
```
Wiki article format with structured pet breed description, following a standardized template with measurements and characteristics for a dog breed.

The parenthetical measurement format "Height : 145 cm (57 inches , " is mid-sentence with a standard conversion convention, showing the official dimensions in both metric and imperial units with a parenthetical qualifier about range.

Final token " , " closes an incomplete parenthetical measurement clause ("Height (45 inches , width (feet and inches , "), immediately expecting the numeric values or unit continuation like "45–55 inches)" or "or 150 cm)" to complete the dimensional specification.
```
### stim 10 token='on' parse_ok=True cjk=False
```
Wikipedia article format with structured historical facts about a U.S. city, establishing encyclopedia-style prose about Galveston, Texas.

The sentence "Galveston is a city in Texas that was founded in 1721, named after Isaac Stewart" mirrors a pattern suggesting a historical narrative about the city's founding and growth, implying continuation of facts about its prominence or role.

Final token "Galveston" ends mid-sentence ("Galveston"), part of a noun phrase describing the city's name origin ("Galveston..."), strongly expecting continuation like "was established as a port" or "first became a port city during the American Revolution."
```
### stim 11 token=' and' parse_ok=True cjk=False
```
Wikipedia article format with biographical details listing film credits and box office performance for a film adaptation of "The Hangover."

The sentence structure "The film was released on December 18, 2009 in North America, and was released internationally on December 18, 2009, and" implies a second performance or distribution detail follows, likely box office results or worldwide release.

Final token "and" is a conjunction mid-sentence listing release details ("It was released on December 18, 2009, and"), expecting "was a commercial success" or "received a worldwide theatrical release" or similar distribution data.
```
### stim 12 token=' and' parse_ok=True cjk=False
```
British Wikipedia article structure with historical description of a London street, listing notable features of Piccadilly's development in the 18th century.

The sentence "The area became known for its coffee houses, theatres and hotels, as well as gambling, restaurants and" follows a list pattern describing London's social institutions of the time, implying another item or continuation of characteristics.

Final token "and" is a conjunction mid-list within "restaurants, theatres and," continuing the enumeration of historical attractions or social functions of the Mayfair district's grand buildings, strongly expecting "social clubs" or "hotel businesses" or "entertainment venues" or "other leisure activities."
```
### stim 13 token='1' parse_ok=True cjk=True
```
Historical encyclopedia article format with structured military ship biography, describing a World War I battleship's service history and design details.

The sentence "The USS Indiana (BB-1) was a battleship built for the United States Navy in 1902, armed with" begins a specific technical specification listing, implying a numeric value for the ship's main armament or displacement.

Final token "1" is mid-number in "1" — part of an incomplete specification ("她的主炮功率 1"), immediately expecting continuation like "00 horsepower" or "5 guns" or "4-class guns," completing the historical technical specification about the ship's initial armament.
```
### stim 14 token=' the' parse_ok=True cjk=False
```
Historical/heritage tourism description format with UK architecture details about a Georgian building, listing features and exhibitions of the Royal Exchange.

The sentence structure "The other activities within the building including the garden and restaurant of the Exchange building" introduces a third item ("The underground complex"), with "The rear of the building" suggesting a concluding detail about the complex's architectural features or usage.

Final token "the" is an article mid-phrase ("The basement of the"), part of a list of specific building components ("The underground portion of the"), expecting a noun like "building" or "Exchange House" or "complex has three floors" or "building houses the chapel and other amenities."
```
### stim 15 token=' way' parse_ok=True cjk=False
```
Australian music blog format with interview quotes and cultural commentary, listing artist's album details and personal reflections on music and fashion.

The quoted lyric mid-sentence ("I think a lot of the negativity... things in the way") is mid-quote describing personal struggles or existential themes, with the phrase "things in the way of life" continuing a list of obstacles or ideals about human experience.

Final token "way" ends an incomplete quoted phrase ("The things in the way"), part of a quoted lyric description clause ("All the obstacles in the way"), expecting continuation like "of life" or "of happiness" or "of people's dreams" or "of the barriers to progress" completing the thought.
```

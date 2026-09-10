# Re-DocRED pilot set — human review sheet (v2)

Built 2026-09-09 by an agent from `scripts/redocred_pilot.py`; outputs in `data/redocred_pilot/`
(`pilot.jsonl`, `pilot_summary.csv`, `stats.json`, `README.md` with sources, hashes and the exact
rules). Nothing is committed. Everything below is numbers and examples for a human to check; no
verdicts. v2 = the coordinator's three fixes (single-quote pairing, cut moved out of unclosed
quotes/brackets, exclusion of DocRED template holes and `(;` fragments) plus `entities_by_type`
and per-relation `stated`. Same seed; 15 of the v1 docs survive in the new sample.

Sources: Re-DocRED `dev_revised.json` + `test_revised.json` from GitHub `tonytan48/Re-DocRED` @ `ccfb54f`
(SHA256s in the README); `rel_info.json` from the HF mirror `thunlp/docred` @ `7985b4e` (the Re-DocRED
repo does not ship it). Tokenizers: `Qwen/Qwen2.5-7B-Instruct` (rule tokenizer) and the cached
`ceselder/qwen3.6-27b-nla-rl/av_base` tokenizer (27B count reported alongside; it loaded fine).
Reproducibility: two consecutive runs give byte-identical `pilot.jsonl` (`cmp`).

## 1. Funnel

| step | docs | removed |
|---|---|---|
| pool = Re-DocRED dev + test | 1000 | |
| `n_tokens_prefix ≥ 50` (7B tokenizer, after the cut move) | 996 | 4, all emptied by the cut-move rule: dev#107 *Ali Kuli Khan Khattak* (7 tokens left), dev#419 *Li Jiancheng* (3), test#319 *Klassics with a "K"* (49), test#337 *George Nostrand* (38) |
| hole-regex exclusion (`about/approximately/exceeds/measures/of/is/are` + `in width…`/`east of…`) | 987 | 9 (dev#92 *Regal Mountain*, dev#248 *Piton des Neiges*, dev#290 *Roald*, test#65 *Cloughton*, test#66 *Beaverton*, test#67 *Gambier Island*, test#163 *Malolos*, test#181, test#393 *Shire of Murray*) |
| `(;` fragment exclusion | 955 | 32 (disjoint from the regex hits; 41 by either rule) |
| `≥ 3` entities with a mention inside the kept text | 954 | test#474 *Gromshin Heights* |
| `≥ 3` relations with head+tail in prefix and evidence ⊆ kept | **951** | dev#455 *Rachel Perry* (cut move dropped 2 of 4 sentences), dev#492 *Scimitar oryx* (no labels), test#300 *Fugue* (all relations outside the 12/15 kept sentences) |
| qualifying by source split | dev 475 / test 476 | |
| sampled with `Random(20260909).sample(sorted_by(split, index), 100)` | 100 | pilot `dev` = first 20 in sampled order, `eval` = remaining 80; by source dev 47 / test 53 |

Per-criterion (not sequential): 4 fail the token minimum, 9 match the hole regex, 32 contain `(;`,
1 fails the entity minimum, 4 fail the relation minimum.

**Cut-move rule in the pool.** Fires in 87 of 1000 docs. 68 move within the final sentence (no
sentence lost), 5 lose one sentence, 14 lose two or more (dev#26 *Mark McNamara* 6→2, dev#107 5→1,
dev#239 *Jerry Steiner* 8→3, dev#344 *Sappy Records* 7→2, dev#419 7→1, dev#457 *Miguel Hidalgo y
Costilla* 8→1, test#319 6→2, test#337 5→2, plus dev#99, dev#358, dev#374, dev#455, test#172,
test#223 losing 2–4). The large losses come from an opener with no closer anywhere in the document
(8 pool docs have an odd total `"` count; a few have a stray `(`), which document-level parity
treats as "open" until the end — the rule as specified. In the pilot the rule fired 10 times and
cost 2 sentences once (pilot 68).

**Previously flagged docs that survived into the new sample:** 2 of 24 — v1 pilot 17 *Zarir* (now
pilot 17; its unclosed `"shot down like an animal` is now handled by the cut move) and v1 pilot 19
*Souvlaki* (now pilot 81; single quotes now correct, cut moved). The other 22 flagged docs are not in
the new sample: 4 were excluded by the new rules (*Regal Mountain*, *Piton des Neiges*, *Shire of
Murray* by the hole regex; *Mikhail Kogan* and *Anatoly Chubais* by `(;`), the rest simply were not
drawn (the qualifying list changed, so the seeded sample changed; 15/100 overlap overall).

## 2. Distributions

Pilot (n = 100), 7B tokenizer unless stated:

| quantity | min | p10 | p25 | median | p75 | p90 | max | mean (sd) |
|---|---|---|---|---|---|---|---|---|
| `n_tokens_prefix` (7B) | 127 | 176 | 199 | 229 | 267 | 314 | 502 | 242.4 (70.8) |
| `n_tokens_prefix_27b` | 127 | 174 | 194 | 223 | 266 | 314 | 498 | 240.0 |
| sentences kept | 4 | 6 | 6 | 8 | 9 | 12 | 17 | 8.2 (2.5) |
| entities in prefix | 5 | 12 | 16 | 20 | 23 | 26 | 31 | 19.4 (5.4) |
| relations in prefix | 5 | 13 | 21 | 30 | 44 | 60 | 78 | 33.5 (16.9) |
| of which `stated` (evidence given) | 0 | 3 | 7 | 11 | 22 | 30 | 47 | 15.0 (11.2) |

- Token bands: ≤ 200 tokens: 28 docs; 201–300: 57; > 300: 15. 7B − 27B token difference: 0 for 35
  docs, +1…+15 for 64, −1 for one.
- **Truncated (token budget) vs whole: 2 truncated / 98 whole** — pilot 25 *Faliero coup* (553
  tokens full, 13/15 sentences kept) and pilot 27 *Clandestine literature* (538, 13/14). 10 of the 1000
  pool docs exceed 512 tokens.
- **Cut moved: 10 docs** (14, 17, 19, 37, 39, 54, 68, 81, 82, 95); all listed in §5.
- Entity types over all 1944 pilot entities: LOC 595, TIME 363, PER 314, ORG 284, MISC 271, NUM 117.
- Most frequent relations over the 3348 pilot relations: located in the administrative territorial
  entity 851, country 596, country of citizenship 154, contains administrative territorial entity 141,
  notable work 109, has part 86, part of 80, applies to jurisdiction 60, member of 60, publication
  date 56. 1851 of 3348 (55%) have an empty evidence list (`stated: false`). Two docs have *no*
  stated relation at all: pilot 0 *Vesper sparrow* (8 relations) and pilot 47 *Northern bald ibis* (9).
- Pool (n = 1000) for comparison: tokens median 224, entities median 19, relations median 32.

## 3. Detokenization — three before/after examples (first sentence of the doc)

Every rule deletes characters from the space-joined string, so token→char offsets are exact; every
in-prefix mention's `surface` (= `prefix_text[char_start:char_end]`) was checked against its
annotated `name` up to whitespace: 0 mismatches in the 100 docs (v1 had one, *Angry Candy*, which is
no longer in the sample).

**Pilot 72, Leone Marucci** (parens, commas, an apostrophe inside a name)
- before: `Leone Marucci ( born March 28 , 1973 , Youngstown , Ohio ) is an American filmmaker , and founder of Independent Film and Media company Steelyard Pictures through which he wrote , directed and produced the 2012 film The Power of Few , which featured the ensemble cast of Christopher Walken , Christian Slater , Q'orianka Kilcher , Anthony Anderson , Jesse Bradford , Moon Bloodgood , Nicky Whelan , Devon Gearhart , Juvenile and others .`
- after: `Leone Marucci (born March 28, 1973, Youngstown, Ohio) is an American filmmaker, and founder of Independent Film and Media company Steelyard Pictures through which he wrote, directed and produced the 2012 film The Power of Few, which featured the ensemble cast of Christopher Walken, Christian Slater, Q'orianka Kilcher, Anthony Anderson, Jesse Bradford, Moon Bloodgood, Nicky Whelan, Devon Gearhart, Juvenile and others.`

**Pilot 36, Guarenas Cathedral** (quote pair; note the empty `()` left where DocRED stripped a Spanish name — see §5)
- before: `The Our Lady of Copacabana Cathedral ( ) or simply Cathedral of Guarenas , is the name given to a religious building belonging to the Catholic Church and is located at Ambrosio Plaza Street on one side of the Bolívar Square , in the city of Guarenas , a city in the municipality Ambrosio Plaza , Miranda state , which serves as a " satellite city " of Caracas , in the South American country of Venezuela .`
- after: `The Our Lady of Copacabana Cathedral () or simply Cathedral of Guarenas, is the name given to a religious building belonging to the Catholic Church and is located at Ambrosio Plaza Street on one side of the Bolívar Square, in the city of Guarenas, a city in the municipality Ambrosio Plaza, Miranda state, which serves as a "satellite city" of Caracas, in the South American country of Venezuela.`

**Pilot 98, Hooshang Seyhoun** (spaced en-dash date range kept; another empty `()`)
- before: `Houshang Seyhoun , ( ) ( August 22 , 1920 – May 26 , 2014 ) was an Iranian architect , sculptor , painter , scholar and professor .`
- after: `Houshang Seyhoun, () (August 22, 1920 – May 26, 2014) was an Iranian architect, sculptor, painter, scholar and professor.`

Single-quote rule check (v2): `souvla 'skewer', itself`, `'Souvlaki' is the common term`, `the
county's 'executive' airport`, `the expression 'cinéma vérité'`, `Chamberlain 'dingo baby' case`,
`Liber Astronomiae or 'Book of Astronomy'`, `leaflets titled 'Truth about Finland'` (pilots 12, 26,
34, 81, 89) all read correctly.

## 4. Five full pilot examples

Format: prefix text exactly as it will be fed (ends on the final word), then entities as
`e<id> [TYPE] name (aliases)` and relations as `Head —relation (P-id)→ Tail` with `stated` /
`no evidence given`. Pilot 19 is included because its cut moved (§5); the other four are ordinary.

### Pilot 1 (dev) — Clark Lake (Gogebic County, Michigan)  [source dev#69]

n_tokens_prefix = 208 (27B: 208), sentences 9/9, position = 207, final word = **species** (dropped tail: `.`)

> Clark Lake is a lake located in Gogebic County in the U.S. state of Michigan. Clark Lake is one of about two dozen clear, clean lakes located in the Sylvania Wilderness of Ottawa National Forest a few miles (6 to 8 km) to the west of the town of Watersmeet. The shoreline is undeveloped except for a picnic area and boat launch at the northern end. The lake possesses several islands and numerous bays and coves. Large boulders strewn about the shoreline and lake bed add to the scenic beauty of this lake. It is not uncommon to see nesting loons and eagles around the lake's islands, and black bear and wolves inhabit the old-growth forest around the lake. The total surface area of the lake is, with maximum depths of. Like all lakes in Sylvania, Clark Lake has numerous special regulations designed to protect and ensure its wilderness quality for future generations. No motorized watercraft are allowed, and a catch and release policy is in place for bass species

Entities (11; LOC:8 NUM:3):

- e0 [LOC] Clark Lake — 3 mention(s)
- e1 [LOC] Gogebic County — 1 mention(s)
- e2 [LOC] U.S. — 1 mention(s)
- e3 [LOC] Michigan — 1 mention(s)
- e4 [NUM] two — 1 mention(s)
- e5 [LOC] Sylvania Wilderness — 1 mention(s)
- e6 [LOC] Ottawa National Forest — 1 mention(s)
- e7 [NUM] 6 — 1 mention(s)
- e8 [NUM] 8 km — 1 mention(s)
- e9 [LOC] Watersmeet — 1 mention(s)
- e10 [LOC] Sylvania — 1 mention(s)

Relations (25, of which 21 stated = have evidence sentences):

- Clark Lake —located in the administrative territorial entity (P131)→ Gogebic County  (stated; evidence s0)
- Clark Lake —country (P17)→ U.S.  (stated; evidence s0)
- Clark Lake —located in the administrative territorial entity (P131)→ Michigan  (stated; evidence s0)
- Gogebic County —country (P17)→ U.S.  (stated; evidence s0)
- Gogebic County —located in the administrative territorial entity (P131)→ Michigan  (stated; evidence s0)
- U.S. —contains administrative territorial entity (P150)→ Michigan  (stated; evidence s0)
- Michigan —contains administrative territorial entity (P150)→ Gogebic County  (stated; evidence s0)
- Michigan —country (P17)→ U.S.  (stated; evidence s0)
- Michigan —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0)
- Sylvania Wilderness —country (P17)→ U.S.  (stated; evidence s0,1)
- Sylvania Wilderness —located in the administrative territorial entity (P131)→ Michigan  (stated; evidence s0,1)
- Watersmeet —country (P17)→ U.S.  (stated; evidence s0,1)
- Sylvania —country (P17)→ U.S.  (stated; evidence s0,7)
- Ottawa National Forest —country (P17)→ U.S.  (stated; evidence s0,1)
- Ottawa National Forest —located in the administrative territorial entity (P131)→ Michigan  (stated; evidence s0,1)
- Watersmeet —located in the administrative territorial entity (P131)→ Gogebic County  (no evidence given)
- Sylvania —located in the administrative territorial entity (P131)→ Michigan  (no evidence given)
- Sylvania —located in the administrative territorial entity (P131)→ Gogebic County  (no evidence given)
- Clark Lake —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0)
- Gogebic County —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0)
- Sylvania Wilderness —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0,1)
- Watersmeet —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0,1)
- Sylvania —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0,7)
- Ottawa National Forest —located in the administrative territorial entity (P131)→ U.S.  (stated; evidence s0,1)
- Watersmeet —located in the administrative territorial entity (P131)→ Michigan  (no evidence given)

### Pilot 6 (dev) — The Sound Barrier  [source test#8]

n_tokens_prefix = 164 (27B: 163), sentences 6/6, position = 163, final word = **created** (dropped tail: `.`)

> The Sound Barrier (known in the United States, as Breaking Through the Sound Barrier and Breaking the Sound Barrier) is a 1952 British film directed by David Lean. It is a fictional story about attempts by aircraft designers and test pilots to break the sound barrier. It was David Lean's third and final film with his wife Ann Todd, but it was his first for Alexander Korda's London Films following the break-up of Cineguild. The Sound Barrier stars Ralph Richardson, Ann Todd, and Nigel Patrick. The Sound Barrier was a box-office success on first release, but it has become one of the least-known of Lean's films. Following on In Which We Serve (1942), the film is another of Lean's ventures into a genre of filmmaking where impressions of documentary film are created

Entities (13; LOC:2 MISC:2 ORG:2 PER:5 TIME:2):

- e0 [MISC] The Sound Barrier (aliases: Breaking Through the Sound Barrier, Breaking the Sound Barrier) — 5 mention(s)
- e1 [LOC] the United States — 1 mention(s)
- e2 [TIME] 1952 — 1 mention(s)
- e3 [LOC] British — 1 mention(s)
- e4 [PER] David Lean (aliases: Lean) — 4 mention(s)
- e5 [PER] Ann Todd — 2 mention(s)
- e6 [PER] Alexander Korda — 1 mention(s)
- e7 [ORG] London Films — 1 mention(s)
- e8 [ORG] Cineguild — 1 mention(s)
- e9 [PER] Ralph Richardson — 1 mention(s)
- e10 [PER] Nigel Patrick — 1 mention(s)
- e11 [MISC] In Which We Serve — 1 mention(s)
- e12 [TIME] 1942 — 1 mention(s)

Relations (13, of which 11 stated = have evidence sentences):

- David Lean —spouse (P26)→ Ann Todd  (stated; evidence s2)
- Ann Todd —spouse (P26)→ David Lean  (stated; evidence s2)
- The Sound Barrier —publication date (P577)→ 1952  (stated; evidence s0)
- The Sound Barrier —director (P57)→ David Lean  (stated; evidence s0,2,4)
- The Sound Barrier —cast member (P161)→ Ann Todd  (stated; evidence s3)
- The Sound Barrier —cast member (P161)→ Ralph Richardson  (stated; evidence s3)
- The Sound Barrier —cast member (P161)→ Nigel Patrick  (stated; evidence s3)
- In Which We Serve —director (P57)→ David Lean  (stated; evidence s5)
- In Which We Serve —publication date (P577)→ 1942  (stated; evidence s5)
- London Films —founded by (P112)→ Alexander Korda  (no evidence given)
- The Sound Barrier —production company (P272)→ London Films  (no evidence given)
- David Lean —notable work (P800)→ The Sound Barrier  (stated; evidence s0,2,4)
- David Lean —notable work (P800)→ In Which We Serve  (stated; evidence s5)

### Pilot 19 (dev) — Lisa Mona Lisa  [source dev#412]

n_tokens_prefix = 179 (27B: 177), sentences 7/7, position = 178, final word = **singing** (dropped tail: ` "Nur ein Lied".`); **cut moved**: unclosed '"' opened at s6 t14 ('"'); cut was after s6 t17 ('Lied')

> "Lisa Mona Lisa" was the Austrian entry in the Eurovision Song Contest 1988, performed in German by Wilfried. The song was performed twelfth on the night, following Germany's Maxi & Chris Garden with "Lied für einen Freund" and preceding Denmark's Kirsten & Søren with "Ka 'du se hva' jeg sa'?". At the close of voting, it had received no points, placing it last out of a field of 21. The song is a ballad in which the singer likens the object of his affection to the Mona Lisa, in that she is very mysterious but nonetheless entrancing. The song was recorded in German, French and English. Due to the song's poor performance, the English version was not released. It was succeeded as Austrian representative at the 1989 Contest by Thomas Forstner singing

Entities (18; LOC:3 MISC:8 NUM:1 ORG:2 PER:3 TIME:1):

- e0 [MISC] Lisa Mona Lisa — 1 mention(s)
- e1 [LOC] Austrian — 2 mention(s)
- e2 [MISC] Eurovision Song Contest 1988 — 1 mention(s)
- e3 [MISC] German — 2 mention(s)
- e4 [PER] Wilfried — 1 mention(s)
- e5 [LOC] Germany — 1 mention(s)
- e6 [ORG] Maxi & Chris Garden — 1 mention(s)
- e7 [MISC] Lied für einen Freund — 1 mention(s)
- e8 [LOC] Denmark — 1 mention(s)
- e9 [ORG] Kirsten & Søren — 1 mention(s)
- e10 [MISC] Ka ' du se hva ' jeg sa ' ? — 1 mention(s)
- e11 [NUM] 21 — 1 mention(s)
- e12 [PER] Mona Lisa — 1 mention(s)
- e13 [MISC] French — 1 mention(s)
- e14 [MISC] English — 2 mention(s)
- e15 [TIME] 1989 — 1 mention(s)
- e16 [PER] Thomas Forstner — 1 mention(s)
- e17 [MISC] Nur ein Lied — 1 mention(s)

Relations (19, of which 8 stated = have evidence sentences):

- Germany —official language (P37)→ German  (no evidence given)
- Nur ein Lied —performer (P175)→ Thomas Forstner  (stated; evidence s6)
- Wilfried —participant of (P1344)→ Eurovision Song Contest 1988  (stated; evidence s0)
- Eurovision Song Contest 1988 —participant (P710)→ Wilfried  (stated; evidence s0)
- Eurovision Song Contest 1988 —participant (P710)→ Kirsten & Søren  (stated; evidence s0,1)
- Maxi & Chris Garden —participant of (P1344)→ Eurovision Song Contest 1988  (stated; evidence s0,1)
- Kirsten & Søren —participant of (P1344)→ Eurovision Song Contest 1988  (stated; evidence s0,1)
- Eurovision Song Contest 1988 —participant (P710)→ Maxi & Chris Garden  (stated; evidence s0,1)
- Lied für einen Freund —performer (P175)→ Maxi & Chris Garden  (no evidence given)
- Lisa Mona Lisa —performer (P175)→ Wilfried  (no evidence given)
- Thomas Forstner —country of citizenship (P27)→ Austrian  (no evidence given)
- German —country of origin (P495)→ Germany  (no evidence given)
- Ka ' du se hva ' jeg sa ' ? —performer (P175)→ Kirsten & Søren  (no evidence given)
- Wilfried —country of citizenship (P27)→ Austrian  (no evidence given)
- Wilfried —languages spoken, written or signed (P1412)→ German  (no evidence given)
- Thomas Forstner —notable work (P800)→ Nur ein Lied  (stated; evidence s6)
- Maxi & Chris Garden —notable work (P800)→ Lied für einen Freund  (no evidence given)
- Wilfried —notable work (P800)→ Lisa Mona Lisa  (no evidence given)
- Kirsten & Søren —notable work (P800)→ Ka ' du se hva ' jeg sa ' ?  (no evidence given)

### Pilot 52 (eval) — Młociny metro station  [source dev#489]

n_tokens_prefix = 182 (27B: 181), sentences 8/8, position = 181, final word = **platform** (dropped tail: `.`)

> Młociny is a Warsaw Metro station serving as a northern terminus to Line M1. It is situated within Warsaw administrative boundaries and ZTM ticketing zone 1, in the dzielnica of Bielany, in a close proximity to Warsaw's ArcelorMittal steelworks. The station opened on 25 October 2008 and is the final northern extension of Line M1. The area beyond the station has been remodelled into a major public transportation junction after Młociny opened. It is served by trams and both urban and suburban buses. Although there are no plans to extend Line M1 further, the station is built in such way that it will be possible to do so if need be. The trains are turned back at sidings behind Młociny. Terminating trains arrive at eastern side platform, whereas southbound trains depart from western side platform

Entities (8; LOC:4 ORG:3 TIME:1):

- e0 [LOC] Młociny — 3 mention(s)
- e1 [ORG] Warsaw Metro — 1 mention(s)
- e2 [LOC] Line M1 — 3 mention(s)
- e3 [LOC] Warsaw — 2 mention(s)
- e4 [ORG] ZTM — 1 mention(s)
- e5 [LOC] Bielany — 1 mention(s)
- e6 [ORG] ArcelorMittal — 1 mention(s)
- e7 [TIME] 25 October 2008 — 1 mention(s)

Relations (19, of which 11 stated = have evidence sentences):

- Warsaw —contains administrative territorial entity (P150)→ Bielany  (stated; evidence s1)
- Bielany —located in the administrative territorial entity (P131)→ Warsaw  (stated; evidence s1)
- Bielany —part of (P361)→ Warsaw Metro  (stated; evidence s0,1)
- Warsaw Metro —part of (P361)→ Line M1  (stated; evidence s0)
- Line M1 —part of (P361)→ Warsaw Metro  (stated; evidence s0)
- ZTM —part of (P361)→ Warsaw Metro  (stated; evidence s0,1)
- Młociny —located in the administrative territorial entity (P131)→ Warsaw  (stated; evidence s0,1)
- Młociny —inception (P571)→ 25 October 2008  (stated; evidence s0,2)
- Warsaw Metro —has part (P527)→ Line M1  (no evidence given)
- Warsaw Metro —located in the administrative territorial entity (P131)→ Warsaw  (no evidence given)
- Line M1 —located in the administrative territorial entity (P131)→ Warsaw  (no evidence given)
- Młociny —part of (P361)→ Warsaw Metro  (no evidence given)
- Warsaw Metro —operator (P137)→ ZTM  (no evidence given)
- ArcelorMittal —located in the administrative territorial entity (P131)→ Warsaw  (no evidence given)
- Młociny —located in the administrative territorial entity (P131)→ Bielany  (no evidence given)
- Warsaw Metro —has part (P527)→ Bielany  (stated; evidence s0,1)
- Line M1 —has part (P527)→ Warsaw Metro  (stated; evidence s0)
- Warsaw Metro —has part (P527)→ ZTM  (stated; evidence s0,1)
- Warsaw Metro —has part (P527)→ Młociny  (no evidence given)

### Pilot 80 (eval) — Surf's Up (film)  [source test#157]

n_tokens_prefix = 201 (27B: 200), sentences 8/8, position = 200, final word = **2017** (dropped tail: `.`)

> Surf's Up is a 2007 American computer-animated mockumentary comedy film directed by Ash Brannon and Chris Buck. It features the voices of Shia LaBeouf, Jeff Bridges, Zooey Deschanel, James Woods, and Jon Heder among others. In production since 2002 at Sony Pictures Animation, it was the studio's second theatrical feature film. The film premiered in the United States on June 8, 2007, and was distributed by Columbia Pictures. It is a parody of surfing documentaries, such as The Endless Summer and Riding Giants, with parts of the plot parodying North Shore. Real-life surfers Kelly Slater and Rob Machado have vignettes as their penguin surfer counterparts. To obtain the desired hand-held documentary feel, the film's animation team motion-captured a physical camera operator's moves. A sequel, titled, was released direct-to-video on January 17, 2017

Entities (20; LOC:2 MISC:4 ORG:2 PER:9 TIME:3):

- e0 [MISC] Surf 's Up — 1 mention(s)
- e1 [TIME] 2007 (aliases: June 8, 2007) — 2 mention(s)
- e2 [LOC] American — 1 mention(s)
- e3 [PER] Ash Brannon — 1 mention(s)
- e4 [PER] Chris Buck — 1 mention(s)
- e5 [PER] Shia LaBeouf — 1 mention(s)
- e6 [PER] Jeff Bridges — 1 mention(s)
- e7 [PER] Zooey Deschanel — 1 mention(s)
- e8 [PER] James Woods — 1 mention(s)
- e9 [PER] Jon Heder — 1 mention(s)
- e10 [TIME] 2002 — 1 mention(s)
- e11 [ORG] Sony Pictures Animation — 1 mention(s)
- e12 [LOC] the United States — 1 mention(s)
- e13 [ORG] Columbia Pictures — 1 mention(s)
- e14 [MISC] The Endless Summer — 1 mention(s)
- e15 [MISC] Riding Giants — 1 mention(s)
- e16 [MISC] North Shore — 1 mention(s)
- e17 [PER] Kelly Slater — 1 mention(s)
- e18 [PER] Rob Machado — 1 mention(s)
- e19 [TIME] January 17, 2017 — 1 mention(s)

Relations (21, of which 14 stated = have evidence sentences):

- Columbia Pictures —country (P17)→ the United States  (stated; evidence s3)
- Surf 's Up —publication date (P577)→ 2007  (stated; evidence s0,3)
- Surf 's Up —director (P57)→ Ash Brannon  (stated; evidence s0)
- Surf 's Up —director (P57)→ Chris Buck  (stated; evidence s0)
- Surf 's Up —cast member (P161)→ Shia LaBeouf  (stated; evidence s0,1)
- Surf 's Up —cast member (P161)→ Jeff Bridges  (stated; evidence s0,1)
- Surf 's Up —cast member (P161)→ Zooey Deschanel  (stated; evidence s0,1)
- Surf 's Up —cast member (P161)→ James Woods  (stated; evidence s0,1)
- Surf 's Up —cast member (P161)→ Jon Heder  (stated; evidence s0,1)
- Surf 's Up —production company (P272)→ Sony Pictures Animation  (stated; evidence s0,2)
- Surf 's Up —country of origin (P495)→ the United States  (stated; evidence s0,3)
- Surf 's Up —cast member (P161)→ Kelly Slater  (no evidence given)
- Surf 's Up —cast member (P161)→ Rob Machado  (no evidence given)
- Columbia Pictures —country (P17)→ American  (no evidence given)
- Surf 's Up —country of origin (P495)→ American  (no evidence given)
- Sony Pictures Animation —country (P17)→ the United States  (no evidence given)
- Ash Brannon —notable work (P800)→ Surf 's Up  (stated; evidence s0)
- Chris Buck —notable work (P800)→ Surf 's Up  (stated; evidence s0)
- Columbia Pictures —located in the administrative territorial entity (P131)→ the United States  (stated; evidence s3)
- Columbia Pictures —located in the administrative territorial entity (P131)→ American  (no evidence given)
- Sony Pictures Animation —located in the administrative territorial entity (P131)→ the United States  (no evidence given)
## 5. Things that (still) look off — for the human to decide on

Cut-move rule (10 pilot docs; the rule works as specified but the resulting final word is often a
function word, which matters if the extraction position is meant to sit on content):
1. pilot 14 *Portugal no coração* ends `... by Gemini with` (dropped: ` "Dai li dou".`)
2. pilot 17 *Zarir* ends `... was quickly captured and` (dropped ` "shot down like an animal".`)
3. pilot 19 *Lisa Mona Lisa* ends `... Thomas Forstner singing` (dropped ` "Nur ein Lied".`)
4. pilot 37 *Fatih Terim* ends `... Both names mean` (dropped ` "emperor".`)
5. pilot 39 *Google Springboard* ends `... guides and how` — the opener was the `(` inside the token
   `to(s` of `how-to(s)`, so the hyphenated word was split (dropped `-to(s).`)
6. pilot 54 *American Theocracy* ends `... and is called` (dropped ` "The Erring Republican Majority."`)
7. pilot 68 *Young Wild Things Tour* lost two sentences (13 → 11): sentence 11 ends inside a quotation
   that closes in sentence 12 and sentence 12 opens with another; ends `... Pete Wentz explained`
8. pilot 81 *Souvlaki* ends `... it is commonly known as` (dropped ` 'kalamaki', 'reed'.`) — the
   cut moved twice, out of `'reed'` and then out of `'kalamaki'`
9. pilot 82 *List of longest rivers of Canada* ends `"It seems," she said` (dropped a 30-word quotation)
10. pilot 95 *Shneur Zalman of Liadi* ends `... the "GRaZ", and the` (dropped ` "Rav".`) — final word
    "the"

Text artifacts inherited from DocRED, not covered by the new exclusions:
11. **Empty parentheses `()`** where a non-Latin name/IPA was stripped: 11 pilot docs (9, 12, 21, 28,
    36, 49, 50, 53, 54, 95, 98; e.g. `Houshang Seyhoun, () (August 22, 1920 ...`). 74 pool docs have
    them. The `(;` rule catches only the variant with a semicolon.
12. **Template holes the regex misses**: pilot 57 `It is approximately long and flows through`
    (`approximately` + adjective), pilot 92 *Sibiu* `Located some north-west of Bucharest` (`some` +
    hyphenated compass point). Phrases like `located east of the Kahului` (pilot 2), `lies just west
    of` (5), `located east of the central` (26) are probably real English, not holes — unverifiable
    without the Wikipedia source. A wider regex (`(about|approximately|some|roughly|nearly|over)\s+
    (long|wide|tall|high|deep|away|[a-z-]+ of)` and `(north|south|east|west)-?(east|west)? of`) would
    catch 57 and 92 but would also remove the plausible ones.
13. **Cross-sentence quotation spacing**: pilot 77 *Word to the Mutha!* has a quote opened in one
    sentence and closed mid-next-sentence; per-sentence parity renders the closer as `Mutha)! ", but
    the title` (space before the closing quote). Pilot 68 also has cross-sentence quotes (handled by
    the cut move). 2 of 100 docs.
14. **Apostrophes mis-paired as quotes**: pilot 19, the Danish title `Ka' du se hva' jeg sa'?` is
    tokenized with standalone `'` tokens and comes out `"Ka 'du se hva' jeg sa'?"`. One doc.
15. Spaced en-dashes in ranges (`1920 – 2014`) are left as in DocRED (Wikipedia would write `1920–2014`).

Annotation issues:
16. **Relations not stated in the text**: 55% of pilot relations have no evidence sentence and are
    mostly inferred/derivable (`located in the administrative territorial entity → United States` for
    every place, `country` for every organisation). `stated: true` marks the 1497 with evidence.
    Pilot 0 *Vesper sparrow* and pilot 47 *Northern bald ibis* have zero stated relations (8 and 9
    relations, all inferred). If the experiment scores relation recall, `stated` is the natural subset.
17. Mentions in the **dropped tail** of the final sentence still count as "in prefix" (the entity/
    relation filter is by sentence, per the brief). In cut-moved docs this can make an entity in the
    dropped quotation count: 4 entities in the pilot have *all* their mentions after the cut —
    pilot 14 *Dai li dou*, pilot 19 *Nur ein Lied*, pilot 54 *The Erring Republican Majority*, pilot 82
    *10–20 %*. Check `in_prefix_mentions[].char_start < len(prefix_text)` if a strict-by-text version
    is needed.
18. No mixed-type entities and no mention offset errors in this sample (v1 had one each).
19. Demonym tails: `country of citizenship → Indian`-style relations remain (DocRED entities are
    surface strings).

Decisions I made that the brief/coordinator did not settle (also in the README):
- Single-quote rule operationalised as per-sentence pairing (opener iff a later standalone `'` in
  the same sentence closes it and a word follows), leftover `'` = possessive/closing; the literal
  "follows whitespace" test is undefined on space-joined DocRED tokens.
- Cut-move openers tracked document-wide (brackets, curly quotes, straight `"` by parity) because
  31 pool sentences have brackets that close in a later sentence; standalone `'` by the per-sentence
  pairing. Consequence: an opener with no closer anywhere in the doc pushes the cut back to before
  it (14 pool docs lose ≥2 sentences, 4 fall under 50 tokens).
- Hole regex applied exactly as given, to the cut prefix text; `(;` likewise on the prefix text.
- Exclusions are placed after the token-minimum step and before the entity/relation steps in the
  funnel; standalone counts are reported too.
- `entities_by_type` = type → list of entity names (in entity-id order); `by_type` keeps the counts.
- `truncated` refers only to token-budget truncation; cut moves are reported separately
  (`cut_moved`, `n_sents_kept_before_cut_move`).
- Unchanged from v1: `rel_info.json` source; extra detokenization rules (curly quotes, tight hyphen,
  `$`/`£`, `n't`, whitespace tokens, spaced dashes); sentence-prefix budget measured with the final
  punctuation; "non-punctuation token" = has an alphanumeric char; entity `name` = first in-prefix
  mention in document order, `aliases` = in-prefix distinct strings, `type` = majority; empty
  `evidence` passes the evidence condition; sort key `("dev" < "test", index)`; 27B tokenizer from the
  cached snapshot's `av_base/`.

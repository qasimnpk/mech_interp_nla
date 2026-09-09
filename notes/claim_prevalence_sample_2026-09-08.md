# Claim prevalence — indicative hand-labelled sample (agent-labelled, unvalidated)

**Status.** No round labelled claims for truth or relevance. This file is a desk analysis written 2026-09-08 by the
agent to give an *indicative* breakdown. Labels are the agent's reading of each claim against the full prefix
(tokens 0..pos of the wikitext document, reconstructed with the same rule as `x3_snippet.py`). Nothing here is
human-verified. Sample: 14 evaluation explanations drawn with `random.seed(1)` from eval stimuli **excluding** the 46
stimuli reserved for the two blind sheets; 44 claim rows from `overnight/s2_claims.csv`.
Script and raw sample: scratchpad `sample_claims.py` / `sample.json` (session-local; regenerate from the seed).

## Labels
T = true (checkable propositions hold); FR = false but on the document's topic; FU = false and foreign to the document.
Final-token claims: token = quoted word matches the token at pos; forecast = exact / category (right kind of continuation,
wrong specific) / wrong.

| stim | claim | slot | label | note |
|---|---|---|---|---|
| 62 | 0 | genre | FR | album article, not "literary blog"/"film adaptations" |
| 62 | 1 | middle | FR | quote fabricated; "1970s gay bar scene" is an FU detail inside an FR claim |
| 62 | 2 | final | T | token ok; forecast exact ("Bellow") |
| 133 | 0 | genre | FR | wiki format true; "Canadian hip hop" false (salsa, US) |
| 133 | 1 | middle | FR | 'The Message' fabricated; praise-list structure true |
| 133 | 2 | final | T | token ok; forecast category (noun phrase; actual "George's production") |
| 192 | 0 | genre | FR | ship article true; "US Navy vessel SS John S." false |
| 192 | 1 | middle | FR | "German-American vessel named Kennedy" fabricated (splitter cut one snippet into rows 1–2) |
| 192 | 2 | middle | T | forecast: wartime/service history (actual "World War I") |
| 192 | 3 | final | FR | token ok; parenthetical quote fabricated (rows 3–4 = one snippet) |
| 192 | 4 | final | T | forecast category ("the war years") |
| 185 | 0 | genre | FR | ancient-sources gist true; "Caucasian name" false |
| 185 | 1 | middle | T | paraphrase presented as quote, propositions hold (Bible, Greek, Roman) |
| 185 | 2 | final | T | token ok; forecast category (noun; actual "Diodorus") |
| 179 | 0 | genre | FU | "literary fiction… sexual awakening" — Simpsons episode article |
| 179 | 1 | middle | FR | arcade gist true, "list of reasons for mood" false, quote fabricated |
| 179 | 2 | final | T | token ok; forecast category (reason clause; actual "for being out…") |
| 52 | 0 | genre | T | Korean military unit history |
| 52 | 1 | middle | FR | "1st Special Unit / 1st Korean Security Unit" fabricated |
| 52 | 2 | final | T | token ok; forecast category (verb phrase); "1935" in parenthetical fabricated |
| 84 | 0 | genre | T | military aviation unit article |
| 84 | 1 | middle | FR | "Australian Army Air Corps" false (RAAF); forecast "Zealand" wrong |
| 84 | 2 | final | FR | token ok; forecast wrong ("Zealand" vs "South Wales") |
| 60 | 0 | genre | FR | wiki true; "image metadata", "military vehicle" false (road article) |
| 60 | 1 | middle | FR | "1776 Battle of Fort Washington", "Thomas Smith" fabricated; era right |
| 60 | 2 | final | T | token ok; forecast exact ("Revolutionary War") |
| 122 | 0 | genre | FR | airline history true; "Dutch" false (Norwegian) |
| 122 | 1 | middle | FR | DC-3/DC-9, "he" fabricated; F28 true |
| 122 | 2 | final | T | token ok; forecast exact ("s") |
| 114 | 0 | genre | FR | storm article true; "tornado over Texas" false |
| 114 | 1 | middle | FR | paragraph fabricated ("Saturday morning", "tropical wave"); timeline gist true |
| 114 | 2 | final | T | token ok; forecast category (a date; actual "December 2") |
| 119 | 0 | genre | FR | wiki city article true; "Palestinian city / Beirut" false (Mogadishu) |
| 119 | 1 | middle | FR | "Beirut" false; "second name follows" true |
| 119 | 2 | final | T | token ok, quote verbatim ("known locally"); forecast category ("as X") |
| 152 | 0 | genre | T | literary analysis, Dante/Inferno; "numbered quotations" minor false |
| 152 | 1 | middle | FR | "Christ's Pilgrim", "John the Baptist" fabricated; damnation theme right |
| 152 | 2 | final | T | token ok; forecast exact ("to hell") |
| 104 | 0 | genre | T | TV series character article |
| 104 | 1 | middle | T | contrast clause about the villain vs ensemble; paraphrase quote close |
| 104 | 2 | final | T | token ok; forecast category (relative clause) |
| 182 | 0 | genre | FR | biography true; "Victorian expedition's travels" false |
| 182 | 1 | middle | FR | "visit to America" false (south of France); tragic-event gist true |
| 182 | 2 | final | T | token ok; forecast near-exact ("the journey") |

## Tallies (n = 44 claim rows, 14 explanations)

| slot | n | T | FR | FU |
|---|---|---|---|---|
| genre/theme (first snippet) | 14 | 4 | 9 | 1 |
| middle ("The sentence '…'" snippets) | 16 | 3 | 13 | 0 |
| final-token snippet | 14 | 13 | 1 | 0 |
| **all** | **44** | **20 (45%)** | **23 (52%)** | **1 (2%)** |

- Final-token forecast: exact or near-exact 5/14, category-correct 8/14, wrong 1/14. Token quote correct 14/14 (word level).
- Quotations: 16/16 middle claims present non-verbatim text as a quotation; 3 are accurate paraphrases. About 9/14
  final-token claims carry a fabricated parenthetical "quote"; 1 verbatim (stim 119).
- Named specifics (entities, dates, titles, nationalities) across the sample: ≈13 true / ≈22 false. The true ones are in the
  prefix or are the forecast; the false ones occur nowhere in the prefix — consistent with the bench string check
  (`notes/t2b_in_full_prefix.csv`: claim key word present in the full prefix 257/691 = 37%).
- Document topic/domain right in ≈10/14 explanations (wrong: 62, 179, 60; borderline 182) — consistent with T2a topic
  accuracy 0.78 raw.
- Proposition level (not claim level): format/genre statement true ≈12/14; domain ≈10/14; specifics ≈37%.

## Related bench numbers (no truth labels, proxies only)
- X3 judge (TARGET Qwen2.5-7B as greedy yes/no judge, 211 eligible claims): "claim supported by prefix" yes 32 / no 179;
  corruption "contradicts" yes 1. Unvalidated 7B judge.
- Blind sheets for human validation exist and are **unfilled**: `notes/t2b_support_sheet_BLIND.csv` (0/30),
  `notes/s3_edit_validity_BLIND.csv` (0/18).
- Composition of the 538 eval claims (mechanical, from `s2_claims.csv`): 3 claims in 123/160 explanations; 195 (36%)
  final-token/forecast type (155 of them in last position, 40 elsewhere); 343 (64%) content claims, of which 78% name a
  capitalised entity, 17% contain a digit, 22% a quoted span; 61 (11% of all) contain no name, digit or quote.
- Claim splitter caveat: it splits on periods inside quotations (stim 192: 3 snippets → 5 rows).

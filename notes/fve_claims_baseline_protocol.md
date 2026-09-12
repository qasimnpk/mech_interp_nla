# fve_claims baseline — full protocol in one page (2026-09-09)

Every step from raw data to the numbers, in order. Detailed references: `data/redocred_pilot/README.md` (preprocessing,
hashes, funnel), `fve_claims/README.md` (design), `fve_claims/ANNOTATION_GUIDE.md` (labels), `fve_claims/*_settings.json`
(what actually ran). Agent-built; the human chose the dataset, the heuristic, the claim unit, the truth rule and the baseline-only scope.

## 1. Data collection

- **Source:** Re-DocRED (Tan et al., EMNLP 2022), the re-annotated DocRED: Wikipedia introductory passages with every entity
mention (types PER / ORG / LOC / TIME / NUM / MISC) and every relation (96 Wikidata properties) annotated. Files
`dev_revised.json` and `test_revised.json` from GitHub `tonytan48/Re-DocRED` @ `ccfb54f` (data commit `0b1584e7`,
2022-05-23); relation names from `rel_info.json` in the HF `thunlp/docred` mirror @ `7985b4e`. SHA256s in the pilot README.
- **Pool:** dev 500 + test 500 = 1000 documents (the fully re-annotated splits; train not used).
- **Held-out status:** both NLAs were trained on ~100k-document FineWeb-derived slices; exact overlap with any Wikipedia
intro is possible but the per-document probability is ~1e-4 and not checked. The 27B's 64 shipped examples are training
rows and are not used here.



## 2. Preprocessing (`scripts/redocred_pilot.py`, deterministic, `cmp`-verified)

1. **Detokenize** DocRED's word tokens: join with single spaces, then delete spaces by rule (no space before `. , ; : ! ? ) ] %`,
  none after `( [`, straight `"` paired per sentence, standalone `'` paired per sentence else attached as possessive/closing,
   curly quotes as open/close, `ill - gotten` → `ill-gotten`, `$ £` tight, `n't` attached, whitespace tokens dropped; dashes
   and `/` keep their spaces). All rules delete characters, so token→character offsets stay exact and every entity mention's
   surface string was verified against its annotation (0 mismatches).
2. **Token budget 512** under the `Qwen/Qwen2.5-7B-Instruct` tokenizer (`add_special_tokens=False`): keep the whole document
  if ≤ 512 tokens, else the longest prefix of complete DocRED sentences ≤ 512 tokens (2 of the 100 pilot docs truncated).
3. **Cut rule:** the prefix text ends immediately after the last non-punctuation token (contains an alphanumeric character)
  of the final kept sentence, so trailing `.`, quotes, brackets are dropped and the text ends on a word.
4. **Cut move (v2):** if that word sits inside an unclosed quote or bracket, the cut moves back to the last word before the
  opener; if none, the sentence is dropped and the check repeats. Fired in 10 of the 100 pilot docs (`cut_moved`, `cut_reason`).
5. **Exclusions (v2):** documents whose prefix matches the DocRED template-hole regex (stripped `{{convert}}` distances, e.g.
  "about east of Mount Blackburn"; 9 pool docs) or contains the `(;` fragment from stripped non-Latin names (32 pool docs).
6. **Filters:** prefix ≥ 50 tokens (the released 7B pair's training minimum for positions); ≥ 3 in-prefix entities (an entity
  with a mention in a kept sentence); ≥ 3 in-prefix relations (head and tail both in-prefix; evidence sentences, if any, all
   kept). 951 of 1000 qualify.
7. **Sample:** `random.Random(20260909).sample(qualifying sorted by (split, index), 100)`; sampled order 0–19 = dev, 20–99 = eval.
8. **Per-document record** (`pilot.jsonl`): `prefix_text`, `position` = last token index under the 7B tokenizer (= n_tokens − 1),
  `final_word`, token counts under both tokenizers (27B count within −1…+15 of the 7B), sentences kept/total, `entities[]`
   with type, first-mention name, aliases and character offsets, `relations[]` with head/tail names, relation name, evidence
   sentence ids and `stated` (true iff evidence non-empty and inside the prefix; 45% of relations), `entities_by_type`.

- **Pilot distribution:** tokens 127–502 (median 229); entities median 20; relations median 30, stated median 11.
- **Known residue** (`notes/redocred_pilot_review.md`): two hole patterns the regex misses (pilots 57, 92); empty `()` from
stripped names in 11 docs; some cut moves end on a function word (`with`, `and`, `the`); pilot 39's opener splits `how-to(s)`.



## 3. NLA setup (7B; the 27B repeats the same steps on the pod)

- **Target:** `Qwen/Qwen2.5-7B-Instruct` @ `a09a3545`, bf16, MPS. Input = `prefix_text` as raw text, no chat template,
`add_special_tokens=False`; token count asserted equal to the pilot record for all 100.
- **Activation:** residual stream after block 20 = `hidden_states[21]`, at the last token (`position`), batch 1, fp32 on CPU;
`fve_claims/out/acts_7b.npz`. Mean norm 116.7.
- **Verbalizer (AV):** `kitft/nla-qwen2.5-7b-L20-av` @ `b8846916`. Released prompt (125 tokens, marker `㈎` at position 111,
neighbours asserted); the marker token's embedding is replaced by the activation rescaled to L2 norm 150; greedy decoding,
200 new tokens; `<explanation>…</explanation>` parsed by regex, raw generation kept, CJK flagged. One explanation per document.
- **Reconstructor (AR):** `kitft/nla-qwen2.5-7b-L20-ar` @ `e2c9e57e`: 21-block truncated backbone, final norm → Identity,
value head on the last token of `Summary of the following text: <text>{explanation}</text> <summary>`
(`add_special_tokens=True`). Output = predicted activation.
- **Score:** `cos = cos(h, AR(z))` in fp64; `mse_nrm = 2(1 − cos)`; `FVE = 1 − mse_nrm / D`. Denominators: `D_released` = 0.7335
(7B training-set variance from the released example transcript; the 27B ships none) and `D_local` = per-element variance of the
√d-normalised pilot activations around their mean (computed per model). Both reported; ranks and CIs are identical under either.
- **Software:** torch 2.13.0, transformers 5.16.1; git hash and wall-clock in each `*_settings.json`.



## 4. Claims

- **Unit = sentence** of the explanation (quote-aware split on `.!?` outside open double quotes, ≥ 3 words), matching the
paper's "snippet". Each 7B explanation has ~3 sentences: a genre/topic sentence, a quoted-reconstruction sentence, a
"Final token …" sentence. No stratification.
- **Deletion:** `z\s` = explanation with that sentence's first exact occurrence removed, seam whitespace collapsed. Computed
once per sentence. **FVE drop = FVE(z) − FVE(z\s)**, in percentage points. AR calls: 1 per explanation + 1 per sentence.
- **Labels per sentence** (agents, 4 batches of 25 documents, blind sheet + key written; provisional until human review):
  - `type`: entity (names/characterises a specific named entity, right or wrong) > detail (number, date, ordering, event,
  quoted phrase, final token) > theme (genre, format, topic, structure). One per sentence, most specific wins.
  - `truth`: **true** = every checkable proposition stated in the prefix or an annotated relation (derivable relations count);
  **false** = any proposition contradicted, or a specific not in the prefix occupying a slot the prefix fills (wrong name in
  a document entity's role; wrong number/date/place where the prefix gives one); **unsupported** = nothing false but
  something uncheckable (priors, predictions past the cut). Judged against the prefix and its annotation only, never
  world knowledge. Entity names checked against the alias list; relations against the relation list.
  - `related` for false sentences: same type and domain as the prefix's slot (related) vs foreign domain (unrelated).
  - `evidence` span ≤ 120 chars; `note` = `text: X; explanation: Y` for false.



## 5. Numbers produced (`fve_claims/05_analyze.py`)

- Mean FVE drop by type × truth (theme / entity / detail × true / false / unsupported) and for false by related / unrelated;
95% CIs by cluster bootstrap over documents (1000 draws, seed 0); percentiles of the drop by truth; counts per cell;
both denominators; all 100 documents (dev/eval available by flag). Figure in the paper's two-panel layout.
- Paper's reference values (Claude NLAs): theme 0.25 / 0.09; entity 0.37 / 0.12; detail 0.35 / 0.16; related 0.14, unrelated 0.06
(percent FVE, true / false). Expect our scale to be larger: a 7B explanation has 3 sentences each carrying more of the
reconstruction than one of the paper's 4–5 snippets.
- `--labels <csv>` recomputes everything from human labels without touching scores


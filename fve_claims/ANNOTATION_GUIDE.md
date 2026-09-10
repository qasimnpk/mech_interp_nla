# Atomic annotation guide — atomic-v1, truth scheme v2 (2026-09-09)

Unit: one atomic proposition extracted from an AV explanation (the NLA paper's "claim"). Judge only against `prefix_text`
and its Re-DocRED annotation (entities with aliases and types; relations, derivable ones included). Never world knowledge.
The activation was taken at the LAST word of the prefix (`final_word`); the verbalizer saw only the activation.

## Record (one JSON object per line; see `atomic.py`)
`protocol`="atomic-v1", `pilot_id`, `claim_id` (0.. per document), `proposition` (one checkable statement, entity
bindings preserved: "The subject bird is the Eastern Towhee", not "a bird is named"), `av_spans` (exact character spans in
`explanation`, each inside one sentence; several spans if the proposition recurs), `type`, `subtype`, `truth`, `related`,
`prefix_evidence` (exact spans in `prefix_text`), `rationale` ("prefix: …; AV: …"), `review_flag` (bool), `annotator`,
`human_reviewed`=false.

## Splitting
Every distinct checkable proposition is its own atom; a compound sentence yields several. A proposition repeated in the
explanation (e.g. inside an invented quotation and again in prose) is ONE atom with several `av_spans`. Invented
quotations are split into their propositions like prose. Claims about the next token / continuation / what the model
expects are atoms of type `forecast` (or subtype `model_output`).

## Type and subtype (exactly one)
- `entity` — names or characterises a specific named entity: `identity` (the subject IS X), `identification` (X is mentioned
  / plays a role), `relationship` (X relates to Y).
- `detail` — a specific particular: `date`, `quantity`, `event`, `attribute`, `cause`, `local_text` (what the visible text
  does structurally: "ends mid-clause"), `exact_words` (a quoted phrase is claimed to be in the text), `final_word` /
  `final_token` (what the last token is; check against `final_word`; always `review_flag`=true).
- `theme` — `topic`, `genre`, `language`, `style`, `format`.
- `forecast` — `continuation` (what comes next), `model_output` (what the model expects / predicts).

## Truth (v2) — three classes, matching the NLA paper's true / false-related / false-unrelated
- **true** — stated in the prefix, or an annotated relation (derivable relations count), or a correct final-word claim.
  `prefix_evidence` required.
- **false** — everything checkable that is not supported: contradicted by the prefix, OR a specific the prefix does not
  contain (a name, number, date, place, quote, source that is simply absent). Absence is false, not "unsupported".
  Sub-label `related`:
  - `related` — same type and domain as the prefix's content (another sparrow species for a sparrow article; a
    neighbouring city; a plausible but absent source or quote about the same subject; a wrong year for a real event).
  - `unrelated` — from a foreign domain, fabricated wholesale (a charity fair for a Holi festival; autonomous vehicles
    for an aircraft directive; a language or nationality with no basis in the text).
  `prefix_evidence` = the contradicting span if one exists; if the specific is simply absent, leave it empty and write
  "absent" in the rationale.
- **irrelevant** — not a claim about the input context: every `forecast` atom and every `model_output` atom. Nothing else.

Genre/format/topic claims that mischaracterise the text are false (usually related). Hedged phrasing ("likely", "suggests")
does not change the label: judge the proposition.

## Review flag
Set `review_flag`=true when the split or the label was a judgement call, and always for `final_token` atoms.

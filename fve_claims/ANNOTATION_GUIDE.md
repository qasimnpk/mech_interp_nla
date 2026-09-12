# Annotation guide (truth scheme v2, 2026-09-09)

One record = one atomic proposition in AV explanation

## Ground rules

- Judge **only** against `prefix_text` and any Re-DocRED annotations
- Verbalizer saw the activation read at the last word of the prefix (`final_word`)
- Hedged phrasing ("likely", "suggests") does not change the label

## Splitting

- Every distinct checkable proposition is its own atom; a compound sentence gives several
- Keep entity bindings: "The subject bird is the Eastern Towhee", not "a bird is named"
- A recurring proposition including in quotations is one atom with several `av_spans`
- Claims about the next token, the continuation, or what the model expects are `forecast` atoms



## Type and subtype (exactly one of each)

- `entity`, names or characterises a specific named entity: `identity` (the subject is X), `identification`
(X is mentioned or plays a role), `relationship` (X relates to Y).
- `detail`, a specific particular: `date`, `quantity`, `event`, `attribute`, `cause`, `local_text` (what the visible
text does structurally, e.g. "ends mid-clause"), `exact_words` (a quoted phrase is claimed to be in the text),
`final_word` / `final_token` (what the last token is; check against `final_word`).
- `theme`: `topic`, `genre`, `language`, `style`, `format`.
- `forecast`: `continuation` (what comes next), `model_output` (what the model expects or predicts).



## Truth (v2)

- **true**: stated in the prefix, an annotated relation (derivable relations count), or a correct final-word claim.
`prefix_evidence` is required.
- **false**: anything checkable that is not supported: contradicted by the prefix, or a specific the prefix does not
contain (a name, number, date, place, quote or source that is simply absent). Absence is false, not "unsupported".
  - `prefix_evidence`: the contradicting span if one exists; if the specific is absent, leave it empty and write
  "absent" in the rationale.
  - `related`: same type and domain as the prefix's content (another sparrow species for a sparrow article; a
  neighbouring city; a plausible but absent source or quote about the same subject; a wrong year for a real event).
  - `unrelated`: from a foreign domain, fabricated wholesale (a charity fair for a Holi festival; autonomous vehicles
  for an aircraft directive; a language or nationality with no basis in the text).
  - Genre, format or topic claims that mischaracterise the text are false (usually related).
- **irrelevant**: not a claim about the input context. Every `forecast` atom, and nothing else.

true / false-related / false-unrelated = the NLA paper's three claim categories.

## Review flag

`review_flag` = true for judgement calls on the split or label, and always for `final_word` / `final_token` atoms.

## Record fields (one JSON object per line; validated by `atomic.py`)

- `protocol` = `"atomic-v1"`; `pilot_id`; `claim_id` from 0 within the document.
- `proposition`, `type`, `subtype`, `truth`; `related` for false atoms only.
- `av_spans`: exact character spans in `explanation`, each inside one sentence; several if the proposition recurs.
- `prefix_evidence`: exact spans in `prefix_text`. `rationale`: `"prefix: …; AV: …"`.
- `review_flag` (boolean), `annotator`, `human_reviewed` = false.


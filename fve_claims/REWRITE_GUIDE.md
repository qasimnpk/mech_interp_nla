# Rewrite guide — deletion and paraphrase counterfactuals per atomic claim (2026-09-09)

For each atom c of explanation v (from `tasks/02_atoms_7b_doc*.jsonl`), produce rewritten explanations. Each rewrite is
the FULL explanation text with only the containing sentence(s) changed. All other sentences are copied byte-for-byte.

1. **deleted** (all documents): v with proposition c removed by a minimal edit of the containing sentence(s). Remove every
   `av_span` occurrence of c. Keep every other proposition of that sentence intact and grammatical; if c was the whole
   sentence, drop the sentence and the blank line after it. Never remove or reword anything that is not c. Record
   `removes_claim`=true and `preserves_other_propositions`=true only after checking both, with a one-line `rationale`
   and your name as `reviewer`. If c cannot be removed without changing another proposition, set
   `preserves_other_propositions`=false and explain.
2. **light** (documents 0–49 only): v with the containing sentence lightly reworded — word order and function words only.
   Every proposition, every specific (names, numbers, dates, quoted text verbatim with its quotation marks) and the
   proposition c itself stay. Length within ±30%.
3. **heavy** (documents 0–49 only): v with the containing sentence rewritten in different syntax and vocabulary, same
   propositions, same specifics. Keep quoted text verbatim. Length within ±40%.

Never correct, hedge or comment on content, even when it is false. Do not touch sentences that contain no span of c.
The deletion is used for baseline FVE scoring; light/heavy for the paraphrase-averaged score.

Output (one JSON object per line, `tasks/04_rewrites_7b_doc<NNN>.jsonl`):
`{"protocol":"atomic-v1","pilot_id":..,"claim_id":..,"proposition":..,"original_explanation":..,"deleted_text":..,
"method":"manual-minimal-edit","removes_claim":true,"preserves_other_propositions":true,"reviewer":"<you>","rationale":..,
"light_text":..|null,"heavy_text":..|null}`. Verify each rewrite differs from the original, and that the deleted text no
longer contains any `av_span` text of c.

# Claim annotation protocol (used for the 27B smoke annotation on 2026-09-09; reuse verbatim for any comparison)

Work only from the source text; never use world knowledge to judge truth. The activation described by an explanation was taken
at the LAST token of the source text (the text is truncated exactly there). The verbalizer saw only the activation.

1. Split the explanation into atomic claims: one checkable proposition each. Split compound sentences ("X is a British musical film
   about Y" → "British musical film"; "about Y"). Keep the verbatim claim text. Quoted reconstructed passages inside an explanation
   are claims too: split each proposition inside the quotation. Predictions about the next token or continuation are claims of type
   "forecast".
2. Type, exactly one of: **entity** (a specific named entity — person, organisation, place, product, title, model number — is present
   or plays a role); **detail** (a specific non-name particular: number, quantity, date, measurement, ordering, outcome, technical term
   specific to the passage); **theme** (genre, format, register, topic-level or discourse-structure statement); **forecast** (what
   the next token or continuation is); **other**.
3. Truth against the source text only, one of: **true** (directly supported; quote the supporting span, ≤ 120 chars); **false**
   (contradicted, or asserts a specific the text does not contain where the text has a different specific in that role; quote the
   contradicting span); **unsupported** (not checkable from the text and not contradicted; no quote). For forecasts: naming the
   final token correctly is true; predictions past the truncation are unsupported.
4. For false claims add a one-line note: what the text has vs what the explanation says, and whether the false value is
   thematically plausible (same type and domain) or foreign.

Output CSV columns: `idx,claim_no,claim_text,type,truth,evidence_span,note`, all fields quoted. Deduplicate only verbatim repeats
inside quoted reconstructions and record occurrence counts in `note`. Report: total claims; per-example n_claims / n_true / n_false /
n_unsupported; type × truth cross-tab; every place the split or label was a judgement call, one line each.

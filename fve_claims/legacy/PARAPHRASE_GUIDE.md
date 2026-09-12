# Paraphrase guide (fve_claims, step 3 — the second step of the plan, after the baseline)

Unit: one sentence of an AV explanation. Produce two rewrites of the sentence, in place, as it would appear inside the
explanation. Every proposition must be preserved; nothing added, nothing dropped.

- **light**: change wording and word order only. Every specific stays verbatim: names, numbers, dates, places, the quoted
  phrases (keep the quotation marks and the quoted text exactly), the final-token mention.
- **aggressive**: different syntax and vocabulary, same propositions. Specifics still verbatim wherever possible (a name is a
  name; a number is a number; the quoted text stays exactly as quoted). If a specific cannot be kept verbatim without
  changing meaning, keep it anyway — meaning wins over variety.
- Never fix, correct, hedge, or comment on the sentence's content, even when it is false. Rewrite what it says.
- Keep length within ±40% of the original. Keep the sentence self-contained (no reference to "the previous sentence").
- Output CSV: `pilot_id,sent_no,light,aggressive`, all fields quoted.

Equivalence check (done by a different annotator in a shuffled batch): for each (original, rewrite) pair answer `yes` if the
two assert exactly the same propositions with the same specifics, else `no` with a one-line reason. Rewrites judged `no` are
dropped from the averaged score and counted.

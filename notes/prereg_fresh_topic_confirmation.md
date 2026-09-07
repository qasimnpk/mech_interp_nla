# OPTIONAL — pre-registration draft: fresh-document confirmation of the prior-corrected topic readout

Status: DRAFT, not in PLAN.md, not run. The human decides whether to run it (≈10 min compute; ≈30 min
human incl. review). If skipped, the write-up labels the prior-corrected topic result "exploratory,
replicated across prefixes on the same 160 documents, not confirmed on new documents".

Frozen procedure (nothing below may change after this file is committed):
- **Documents:** wikitext-2-raw-v1 train, document level, ≥ 300 target tokens, shuffled with seed 0 exactly
  as S0; take documents at shuffled indices **200–239** (40 documents never used; assert doc_idx ∉ stimuli.csv).
- **Positions:** one per document, `pos ~ Uniform{16, …, min(len, 512) − 1}`, numpy RNG **seed 1**, raw text,
  no chat template, block-20 activation at pos (`hidden_states[21]`) as S0.
- **Titles:** `topic_true` = first ` = X = ` heading (T0 rule); `topic_foreign` = title of document
  `(i + 20) mod 40`; assert no document collision and no title collision.
- **Prefix:** `p3 = "<explanation>\nThe document is about"` (the held-out prefix from T2a), prefilled after
  the default AV prompt with the activation injected exactly as `nla_lib`; no-injection = raw marker embedding.
- **Candidate score:** summed log-prob of every token of `" " + title` (T2 convention); token counts recorded.
- **Correction:** `corr(c) = lp(c | h) − lp(c | h_0)`, fixed; no other correction, no per-token variant as endpoint.
- **Primary endpoint:** within-pair choice accuracy of the corrected score (fraction of documents where
  `corr(topic_true) > corr(topic_foreign)`), 95% CI by bootstrap over documents (1000 draws, seed 0).
- **Baseline:** raw within-pair accuracy (`lp(true | h) > lp(foreign | h)`) with the same CI.
- **Also reported:** pooled AUROC raw and corrected with CIs; swap (foreign activation injected) accuracy;
  no-injection accuracy.
- **Resampling unit:** document. **Stopping rule:** all 40 documents, no interim look, no exclusions except
  a heading-extraction failure (report the count).
- **No selection:** no prefix, correction, or threshold will be chosen or adjusted using these results.
- **Reported as:** confirmation on new documents of the prefix-transfer result in T2a; n=40 limits precision
  (a true accuracy of 0.90 gives a CI of roughly ±0.09).
- **Build:** `overnight/t2f_fresh.py` reusing `t2a_audit.py`; outputs `t2f_scores.csv`, `t2f_summary.md`.

# human-plan.md — what to spend your time on next (desk agent, 2026-09-07 01:30)

No more experiments unless you choose the optional one in §3. Order: **annotate → verify → decide → write.**
Rough human time: 0.75 h + 0.75 h + 0.25 h + the rest of your budget on writing. Log hours in
`notes/human_log.md` (the table still says `_fill_`) and keep Toggl running.

## 0. Where things stand (read once, 10 min)
- `notes/state_of_knowledge_2026-09-07.md` — the tiered result in one page with every number.
- `notes/advisor_round3_feedback.md` — the wording rules the write-up must follow; the advisor's second
  message (the one you pasted at 01:00) is in this session only — paste it into that file if you want it kept.
- Everything is merged into `main` (round 3b merge `2d2d91e`); the worktree `../mech_interp_nla-nightshift`
  is idle on `nightshift/round3b` and can be removed any time. All gitignored caches are copied into
  `overnight/out/` on main (`acts_L20`, `recon_L20`, `c2_acts`, `c3_acts`, `t1_repe`, `t3_dirs`, `t4_dirs`).
- Overnight the desk also produced: `notes/diagnostics_round3b.md` (+ `notes/figs/t2c_pairs.png`,
  `notes/figs/c3_transfer.png`), a blinded labelling sheet (§1), and an optional pre-registration (§3).

## 1. Annotate the support sheet — BLIND (≈45 min) — highest value
Why: 499/691 "original" claim words are not in the visible context, yet the verbalizer prefers them by
11 nats under its own activation. Whether those are inferences or confabulations decides how T2b is written.
- Open **`notes/t2b_support_sheet_BLIND.csv`** (30 rows, shuffled, no likelihood columns). Do **not** open
  `notes/t2b_support_sheet_KEY.csv` until you are done.
- For each row, judge the *claim* (the whole sentence, not just `word_orig`) against **only**
  `context_left_64 + token_str` (that is all the activation could have seen). Fill `label` with one of
  `supported` / `contradicted` / `unsupported` (unsupported ≠ false: a plausible inference without evidence),
  `evidence_passage` with the phrase you relied on, `note` for ambiguity.
- Then join with the key and look at `d_own` by label:
  ```
  uv run python -c "import pandas as pd;b=pd.read_csv('notes/t2b_support_sheet_BLIND.csv');k=pd.read_csv('notes/t2b_support_sheet_KEY.csv');m=b.merge(k,on='blind_id');print(m.groupby('label')[['d_own','d_pos2','d_foreign','d_noinj']].agg(['mean','median','count']))"
  ```
- Report it as a qualitative audit (n=30), not a benchmark. The revealing outcome is "unsupported claims are
  preferred as strongly as supported ones". If you can, have a second reader check the ambiguous rows.

## 2. Verify by hand and log it (≈45 min) — Neel: "sanity-check your agent"
Re-derive these from the CSVs (each reproduces the bench number; put the line in `notes/human_log.md`):
```
uv run python -c "import pandas as pd;t=pd.read_csv('overnight/t2c_pairs.csv');d=t.p1_D_a-t.p1_D_b;print(d.mean(),(d>0).mean(),((t.p1_D_a>0)&(t.p1_D_b<0)).mean())"      # 1.738 0.775 0.225
uv run python -c "import pandas as pd;a=pd.read_csv('overnight/t2a_scores.csv');e=a[a.split=='eval'];print((e.p3_true>e.p3_foreign).mean(),(e.p3_true_corr>e.p3_foreign_corr).mean())"   # 0.781 0.944
uv run python -c "import pandas as pd;b=pd.read_csv('overnight/t2b_claims.csv');print((b.d_own-b.d_pos2).mean(),b.d_own.mean(),b.d_pos2.mean(),b.d_foreign.mean(),b.d_noinj.mean())"   # 7.347 12.988 5.641 2.879 2.726
uv run python -c "import pandas as pd;c=pd.read_csv('overnight/c3_cells.csv');print((c.M_fact_mean-c.M_wording_mean).mean(),c.M_fact_mean.mean(),c.M_wording_mean.mean(),(c.D_hC-c.D_hD).mean())"   # 0.00782 0.01754 0.00972 1.772
```
Read raw data, not summaries:
- `overnight/t2c_summary.md` lines 60–110: the full 40-row table. Check it against `notes/figs/t2c_pairs.png`:
  31/40 below the diagonal, 9 in the lower-right quadrant, template 5 ("The story is set in {city}") far out.
- `overnight/c3_summary.md` "Three verbatim cells": are the four descriptions per cell really about the
  same text, and does the rephrased pair read as meaning-preserving?
- `overnight/t2b_summary.md` donor table: confirm foreign ≈ no-injection (2.9 vs 2.7) with your own eyes.
- `overnight/MORNING3b.md` provenance section and the C3 crash-fix line in `overnight/RUNLOG.md` (line 58):
  pre-model KeyError, no statistic changed. Also round 2's R1 crash fix (RUNLOG line 24) and round 1's S3 AR
  crash fix (line 12). These go in the methods/provenance paragraph.
- Earlier rounds still owe a human re-derivation (see `notes/human_log.md`): mean cos_own 0.882 from
  `overnight/s1_recon.csv` rows with split=eval, and A − P = −0.00181 from `overnight/s3_scores.csv`.

## 3. Decide (≈15 min)
1. **Optional fresh confirmation of the topic readout** on 40 never-seen documents: pre-registration is
   frozen in `notes/prereg_fresh_topic_confirmation.md` (≈10 min compute). Run it only if writing time
   allows; otherwise the write-up says "exploratory correction, replicated across prefixes on the same 160
   documents, not confirmed on new documents". If yes: append it to `overnight/PLAN.md` as stage T2f, run it
   in the worktree, merge.
2. **Claim tier for the write-up** (advisor's four tiers; agree or edit): (1) reconstructs matching
   activations well; (2) its score is poorly suited to verifying the tested factual claims; (3) local-token
   content explains much of the reconstruction advantage; (4) forced-prefix likelihoods are an alternative
   readout: strong topic discrimination after exploratory prior correction, modest entity identification.
3. Round 4 (distributed steering, `notes/round4_distributed_edit_proposal.md`) and the 27B: future work,
   stated concretely ("repeat the reconstruction/readout dissociation; test whether a stronger interpreter
   improves entity identification"), not run.

## 4. Write (the rest of the budget)
Exec summary 1–3 pages, ≤ 600 words, graphs, structured by finding; then the write-up. Your own voice:
every agent file here is scaffolding. Grading doc: `notes/neel_drive/mats12_admissions_procedure_faq.md`.
- **Central conclusion (advisor's wording, adapt):** reconstruction quality, spontaneous verbalization and
  targeted semantic readout are distinct capabilities; on this checkpoint targeted likelihood scoring improves
  access to some source information, while reliable fine-grained factual readout remains limited.
- **Three figures** (data pointers; make them yourself or ask the desk):
  1. Reconstruction specificity: bars from `overnight/s1_summary.md` / `s4_summary.md` (own 0.882, same-doc
     0.366, cross-doc 0.320, empty 0.347, blind 0.429, raw context 0.473).
  2. Local-snippet ablation: truncation curve `overnight/r3_curve.csv` + C1 positions
     (`overnight/c1_summary.md` deletion-cost table).
  3. Readout with donor controls: T2a table in `notes/diagnostics_round3b.md` (raw / corrected / none / swap,
     accuracy with CIs) + `notes/figs/t2c_pairs.png` + `notes/figs/c3_transfer.png`.
- **Wording rules** (from `notes/advisor_round3_feedback.md`): "substantially more sensitive to wording and
  relevance than to the tested factual corruptions"; "local-snippet dominance persists across positions";
  "the tested instructions did not produce the requested changes"; T4 = injected-concept sensitivity, not
  outside-J-space; report angles (18° ≈ 31% of norm); NOT MET ≠ success — state the substantive outcome
  next to each; never "failed to reproduce" the NLA paper (`notes/nla_paper_card.md`); steered outputs
  are not "identical".
- **Numbers and units:** `notes/diagnostics_round3b.md` §"Observation-count reconciliation" gives the
  documents / claims / triples / scored-rows chain; the 97.3% figure is the 298 LLM single-word rows.
- **Provenance section:** agents built every script and drafted every note; you chose the checkpoint
  (hardware-forced), the questions, the kill tests and thresholds (with two outside reviewers), reviewed
  each morning, and re-derived the numbers listed in `notes/human_log.md`. Decision trail:
  `notes/round1_decisions.md`, the review blocks at the top of `overnight/PLAN.md`, `notes/advisor_*.md`.
- **Cosmetic only, do not edit the frozen bench files:** `overnight/MORNING3b.md` shows `np.int64(40)` at
  line 72 and repeats the "Stage status" and "T3 closeout" headings; fix in your own document and say so.
- Time budget reminder: ~16 h human total, max 20, +2 h for the exec summary; deadline Fri Sept 11 11:59pm PT.

## 5. Ask the desk for (when you are back)
Figures from the pointers above; a first scaffold of the exec summary from `notes/state_of_knowledge_2026-09-07.md`
(to be rewritten by you); the T2f run if you choose it; worktree removal.

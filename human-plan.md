# human-plan.md — from here to a submitted MATS application (revised 2026-09-07 03:15, for your review)

Deadline **Fri Sept 11, 11:59pm PT**; you estimate **36 h elapsed** left. Human budget ≈16 h (max 20) + 2 h for
the exec summary and form questions; agent time and GPU time do not count, reviewing their output does.
Tags: **[YOU]** only you can do it · **[AI]** an agent does it, you review the stated part · **[AI→YOU]** agent
drafts, you rewrite. Work top to bottom; each block moves the application closer to submitted. Tick boxes as you go.
Keep Toggl running; the hours table in `notes/human_log.md` still says `_fill_`.

Main result stays the 7B study. The 27B is §8, optional, after the write-up is submission-ready.

---

## 0. Orient (≈15 min) [YOU]
- [ ] Read `notes/state_of_knowledge_2026-09-07.md` (the tiered result, every number).
- [ ] Read `notes/diagnostics_round3b.md`, including the **Correction** section at the end: the activation saw
      the full prefix up to the position (median 276 tokens), not the 64-token display window. The correct
      statement is: 434 of 691 original claim words occur nowhere in the prefix the activation saw, and the AV
      still prefers them by 10.8 nats under its own activation (5.8 nats position-specific). Absence of the word is
      not absence of support.
- [ ] Skim `notes/advisor_round3_feedback.md`. Paste the two later advisor messages (01:00 and 02:30 tonight) into
      it so the provenance trail is complete. [YOU, 5 min]
- [ ] Log start time.

## 1. Annotate the support sheet, blind (≈45 min) [YOU] — decides how T2b is written
- [ ] Open `notes/t2b_support_sheet_BLIND.csv` (30 rows, shuffled, no likelihood columns; rebuilt tonight with
      `full_prefix_to_pos` = everything the activation saw). Do **not** open `notes/t2b_support_sheet_KEY.csv`
      until the labels are in.
- [ ] For each row judge the **whole claim** against `full_prefix_to_pos` + `token_str` only (no future tokens).
      `label` ∈ `supported` / `contradicted` / `unsupported` (unsupported ≠ false: plausible inference without
      evidence). Put the phrase you relied on in `evidence_passage`; ambiguity in `note`.
- [ ] Join with the key and read `d_own` by label:
      ```
      uv run python -c "import pandas as pd;b=pd.read_csv('notes/t2b_support_sheet_BLIND.csv');k=pd.read_csv('notes/t2b_support_sheet_KEY.csv');m=b.merge(k,on='blind_id');print(m.groupby('label')[['d_own','d_pos2','d_foreign','d_noinj']].agg(['mean','median','count']))"
      ```
- [ ] Write three sentences on the outcome in `notes/human_log.md` (qualitative audit, n=30, not a benchmark).
      The revealing outcome is "unsupported claims are preferred as strongly as supported ones". If a second
      reader is available, have them check the ambiguous rows. [optional]

## 2. Verify the load-bearing numbers by hand and log it (≈45 min) [YOU] — Neel: "sanity-check your agent"
Each one-liner reproduces the bench number; paste the line and result into `notes/human_log.md`.
Metric labels matter: `(true > foreign).mean()` is **paired choice accuracy**, not AUROC; the AUROCs are in the
bench summaries and in `notes/diagnostics_round3b.md` side by side.
- [ ] T2c donor sensitivity, fraction > 0, both-correct rate (expect 1.738 / 0.775 / 0.225):
      `uv run python -c "import pandas as pd;t=pd.read_csv('overnight/t2c_pairs.csv');d=t.p1_D_a-t.p1_D_b;print(d.mean(),(d>0).mean(),((t.p1_D_a>0)&(t.p1_D_b<0)).mean())"`
- [ ] T2a paired choice accuracy raw / prior-corrected on the held-out prefix (expect 0.781 / 0.944, n=160):
      `uv run python -c "import pandas as pd;a=pd.read_csv('overnight/t2a_scores.csv');e=a[a.split=='eval'];print((e.p3_true>e.p3_foreign).mean(),(e.p3_true_corr>e.p3_foreign_corr).mean(),len(e))"`
- [ ] T2b donor means (expect own−pos2 7.347; own 12.988, pos2 5.641, foreign 2.879, none 2.726):
      `uv run python -c "import pandas as pd;b=pd.read_csv('overnight/t2b_claims.csv');print((b.d_own-b.d_pos2).mean(),b.d_own.mean(),b.d_pos2.mean(),b.d_foreign.mean(),b.d_noinj.mean())"`
- [ ] C3 fact − wording margin and readout at w2 (expect 0.00782 / 0.01754 / 0.00972 / 1.772):
      `uv run python -c "import pandas as pd;c=pd.read_csv('overnight/c3_cells.csv');print((c.M_fact_mean-c.M_wording_mean).mean(),c.M_fact_mean.mean(),c.M_wording_mean.mean(),(c.D_hC-c.D_hD).mean())"`
- [ ] Still owed from rounds 1–2: eval mean cos_own 0.882 from `overnight/s1_recon.csv` (rows 40–199) and
      A − P = −0.00181 from `overnight/s3_scores.csv`. Ask the desk for the one-liners if you want them.
- [ ] Read raw data, not summaries: the 40-row table in `overnight/t2c_summary.md` against
      `notes/figs/t2c_pairs.png` (31/40 below the diagonal, 9 both-correct, template 5 far out); the three
      verbatim cells in `overnight/c3_summary.md` (same text? meaning-preserving rephrase?); the donor table in
      `overnight/t2b_summary.md` (foreign 2.9 ≈ none 2.7).
- [ ] Note for the provenance paragraph: three crash fixes, all before any model output, no statistic changed:
      `overnight/RUNLOG.md` lines 12 (S3), 24 (R1), 58 (C3).

## 3. Decide, then let the desk run the one control that matters (≈20 min of you; ≈30 min agent)
- [ ] **Decide: text-only baseline for the topic readout (T2g).** Both "Building Better Activation Oracles" and
      "Are SAEs Useful?" will make a reviewer ask what the NLA buys over the text. The blind describer answers
      that for reconstruction, not for the 0.94. T2g: the base target model reads the full prefix as plain text,
      followed by the same "The document is about" prefix, and scores the same two titles; same 160 items, same
      labels, raw and prior-corrected, paired choice accuracy and AUROC. Target-only, ≈400 forwards, <15 min.
      If it matches 0.94 the readout is text inversion and the claim narrows honestly. **Recommended: yes.**
      [AI writes the pre-registration into `overnight/PLAN.md` as T2g; YOU approve the prefix wording before it runs]
- [ ] **Decide: fresh-document confirmation (T2f)**, frozen in `notes/prereg_fresh_topic_confirmation.md`
      (40 unseen documents, ≈10 min). Only if T2g leaves the readout standing. Otherwise the write-up says
      "exploratory correction, replicated across prefixes on the same 160 documents, not confirmed on new documents".
- [ ] **Confirm the claim tiers** (edit if you disagree): (1) reconstructs matching activations well;
      (2) its score is poorly suited to verifying the tested factual claims; (3) local-token content explains much
      of the reconstruction advantage; (4) forced-prefix likelihoods are an alternative readout: strong topic
      discrimination after exploratory prior correction, modest entity identification.
- [ ] Run T2g (and T2f if chosen) in the worktree; merge; you read the summary and re-derive the accuracy with
      a one-liner (the desk supplies it). [AI runs; YOU verify, 10 min]

## 4. Read three papers for positioning (≈1.5 h) [YOU]; [AI] can pull the relevant sections first
Ask the desk to extract each paper's evaluation-design section and the two or three sentences you will cite,
from `notes/context_600k.md` / `notes/mats_paper_index.md` (use the index), so your reading is targeted.
- [ ] Building Better Activation Oracles: hallucination and text-inversion confounds; AObench. Use it to frame
      finding 5 as recovery of source information, not access to hidden cognition.
- [ ] Are Sparse Autoencoders Useful? (sparse probing): baselines decide whether a method adds value. Use it to
      justify T2g and the RepE comparison; note that the AR topic probe and the AV title ranking are only
      comparable because T2a scored them on identical items and labels.
- [ ] Towards Principled Evaluations of SAEs: approximation / interpretation / control evaluated separately. This
      is the skeleton of your tiered claim; you have not established the control tier and should say so.
- [ ] One line each in future work: subspace-illusion paper (why AR-derived steering needs more than a behaviour
      change), targeted concept erasure (the template for selective control), hallucinated-entity and
      entity-familiarity papers (identifying an entity is narrower than verifying a relation; familiarity ≠ recall).

## 5. Figures (≈1 h of you) [AI drafts → YOU check every bar against the CSV]
- [ ] Fig 1 reconstruction specificity: own 0.882, same-doc 0.366, cross-doc 0.320, empty 0.347, blind 0.429,
      raw context 0.473 (`overnight/s1_summary.md`, `s4_summary.md`).
- [ ] Fig 2 local-snippet ablation: truncation curve `overnight/r3_curve.csv` + C1 positions
      (`overnight/c1_summary.md` deletion-cost table).
- [ ] Fig 3 targeted readout with donor controls: T2a table (raw / corrected / none / swap, accuracy with CIs,
      plus T2g when it exists) in `notes/diagnostics_round3b.md`; `notes/figs/t2c_pairs.png`;
      `notes/figs/c3_transfer.png`.
- [ ] Check each figure's numbers against the file it cites; write the file:line under each figure.

## 6. Write the exec summary and write-up (the bulk of your remaining budget) [YOU; AI→YOU for scaffolds]
Format (`notes/neel_drive/mats12_admissions_procedure_faq.md` lines 199–203): a Google Doc, exec summary first
(1–3 pages, ≤600 words, graphs), then enough detail to follow without the code; link-shareable. Structure by
finding, not chronology. Your voice throughout; every agent file is scaffolding.
- [ ] Ask the desk for: a numbered claim → file:line trace table for every number you intend to use; a
      provenance-section draft (what agents built, what you decided, what you verified, the three crash fixes);
      a scaffold of the exec summary from `notes/state_of_knowledge_2026-09-07.md`. [AI→YOU]
- [ ] Central conclusion (adapt): reconstruction quality, spontaneous verbalization and targeted semantic readout
      are distinct capabilities; on this checkpoint targeted likelihood scoring improves access to some source
      information, while reliable fine-grained factual readout remains limited.
- [ ] Wording rules: "substantially more sensitive to wording and relevance than to the tested factual
      corruptions"; "local-snippet dominance persists across positions"; "the tested instructions did not produce
      the requested changes"; T4 = injected-concept sensitivity, not outside-J-space; angles as angles (18° ≈ 31%
      of the norm); NOT MET ≠ success, state the substantive outcome beside each kill line; never "failed to
      reproduce" the NLA paper (`notes/nla_paper_card.md`); steered outputs not "identical"; the 97.3% figure is
      self-consistency on 298 LLM single-word rows; label accuracy vs AUROC explicitly.
- [ ] Units paragraph from `notes/diagnostics_round3b.md` §reconciliation (documents → claims → triples → rows).
- [ ] Limitations: one checkpoint, hardware-forced; synthetic corruptions; templated C2/C3 contexts (engineered
      differences may be unusually easy); prior correction exploratory; n=40 pairs, n=30 labels; no control tier.
- [ ] Future work, concrete: 27B replication of the reconstruction/readout dissociation (§8); T2d calibrated
      entity readout and T2e locality curve; round-4 distributed edits with the erasure-paper controls.
- [ ] Cosmetic only, fix in your doc not in the frozen files: `overnight/MORNING3b.md` line 72 shows
      `np.int64(40)`; "Stage status" and "T3 closeout" headings are duplicated.
- [ ] Ask the desk to check every number in your draft against its source file and report mismatches. [AI]

## 7. Application form questions, final checks, submit (≈2 h) [YOU]
Neel reads the **form questions first and filters on them** (FAQ lines 13, 58, 203): "Specifics beat vibes: name
the models, the key experiment, the surprising number."
- [ ] Draft the form answers yourself; the desk may only check facts against files. Lead with the dissociation
      and the surprising number (corruption 0.003 < paraphrase 0.005; readout 0.94 vs reconstruction blind).
- [ ] Provenance and time: fill the hours table in `notes/human_log.md`; Toggl screenshot; state in the doc what
      you verified and how (§1–2 entries).
- [ ] Doc is link-shareable; code repo linked (optional); no secrets in the repo.
- [ ] Submit with ≥ 6 h buffer. Sleep before the final read-through.

## 8. OPTIONAL after §7 is submission-ready: bounded 27B replication on RunPod [AI setup and run; YOU ≤ 90 min]
Purpose (advisor): does the separation between reconstruction sensitivity and targeted factual readout appear
in a second released NLA? A replication across two systems (target family, training, layer and interpreter all
change), not a scaling experiment. Do not spend money to look serious; spend it only for this question.
- [ ] Authorize: one on-demand **H200 141 GB** on runpod.io (listed ≈$4.59/h; confirm the quote), persistent
      volume, **one 12 h session** with a scheduled stop, spend cap ≈$60 + storage. No preemptible, no vast.ai.
- [ ] Brief the setup agent (copy into its task):
      separate branch `cloud/27b`; never touch the frozen 7B artifacts; checkpoint
      `ceselder/qwen3.6-27b-nla-rl` only (Qwen3.6-27B, layer 42, AV base + RL adapter, separate AR, 64 example
      activations); inspect the released reference code for extraction site, injection hook, normalization,
      templates and AR head; load models sequentially target → AV → AR, bf16, small batches; run the supplied
      examples first, then a small fresh-data end-to-end check; record exact revisions, dependencies, hardware and
      every adaptation; **stop setup after 3 elapsed hours** if valid AV generation and AR scoring are not both
      working, and do not start a second model port; **stop the pod at 12 elapsed hours** regardless, exporting
      all artifacts; no pushes.
- [ ] Gate: YOU approve the pilot's raw examples (10 explanations read against their contexts) before the
      evaluation runs. [YOU, 20 min]
- [ ] Frozen scope, ≈40 source positions and 40 controlled entity pairs, subject to measured throughput:
      | priority | measurement | controls |
      |---|---|---|
      | required | reconstruction specificity | own, shuffled same-doc, empty |
      | primary | AR response to factual corruption vs paraphrase | validated edits; keep surrounding wording and final tokens |
      | secondary | forced-prefix entity readout on matched contexts | both donors, no injection, one held-out prefix; accuracy and donor sensitivity |
      | optional | local-snippet contribution | only if the 27B explanations contain comparable snippets |
      Do not impose the 7B three-claim format; report how many outputs permit valid edits; inspect examples before
      trusting the splitter. Pre-declare adapter, scoring rule, exclusions and endpoints in `overnight/PLAN.md`
      as a "Round 27B" block before the evaluation starts.
- [ ] Interpretation, pre-committed: similar dissociation → limitation extends beyond the first checkpoint;
      better factual discrimination → a boundary on the 7B conclusion; weak or inconclusive → small replication,
      limited precision; setup fails validation → no conclusion, stays future work. Whatever happens, the 7B
      report does not depend on it; add one paragraph and one figure at most.
- [ ] Elapsed-time note: the agent's setup can start early in parallel (it costs you nothing until the gate), but
      your attention on it stays after §7.

---
Suggested elapsed windows (advisor): first 3 h §0–3 (agent may begin §8 setup in parallel); by hour 12 §4–6 drafted;
hours 12–24 freeze experiments and finish the write-up; final 12 h sleep, review, form questions, submit with buffer.

# human-plan.md — from here to a submitted MATS application (revised 2026-09-08 13:55 EDT, after round 3c)

**Clock.** Now: Tue 2026-09-08 13:55 EDT. Deadline in Neel's FAQ: **Fri Sept 11, 11:59pm PT = Sat Sept 12, 02:59 EDT**,
about **85 elapsed hours** from now. Your earlier "36 hours" was your own availability estimate, not the deadline;
record which one binds in §0. Human budget ≈16 h (max 20) of active project work + 2 h for the executive summary.
Verified in the FAQ ("Defining the 20+2 hour time limit"): **not counted** = general prep reading, generic cloud-GPU
setup, breaks, waiting for runs, writing the application-form answers; **counted** = anything actively directed at the
project, which includes reviewing agent output and deciding what it means.

**Decision (unchanged):** finish the 7B application first. **Experiments are frozen**; nothing is queued or running.
Every round (1, 2, 3, 3b, 3c) is merged into `main` (last merge `7592565`); `overnight/` on main is the record.
Tags: **[YOU]** your judgment or writing · **[AI]** delegated execution · **[AI → YOU]** agent output you must inspect.
Checkboxes are tasks, not claims that work happened. Work top to bottom; each block moves the application closer.

**Answer to your question about 3c-3:** it ran in its gated form and stopped at the gate. Native competence 16/16 and
the self-patch check 16/16 passed; the twin-donor patch shifted the answer in 11/16 against a frozen 12/16, so the
four routes were never run and no position or layer search was done. Report it as a gate failure, not a result.

---

## Where things stand (facts, read once — 10 min) [YOU]

| item | state |
|---|---|
| results and reports | `overnight/MORNING1.md … MORNING3c.md`; kill lines in `overnight/DISCONFIRMATION.md`; every number's source in `notes/evidence_table.md` (round-3c rows added today) |
| one-page synthesis | `notes/state_of_knowledge_2026-09-07.md` (with the 2026-09-08 addendum) — agent draft, rewrite in your voice |
| positioning | `notes/response_to_reframing_2026-09-07.md` (Dingeto verified, same checkpoint), `notes/novelty_vs_nla_paper.md`; the preprint text is in `notes/dingeto_2026_train_the_model_text.txt` |
| human-verified numbers | **none yet.** All re-derivations in `notes/human_log.md` are agent-side. The hours table still says `_fill_` |
| unlabelled blind sheets | `notes/s3_edit_validity_BLIND.csv` (18 triples, §2a) and `notes/t2b_support_sheet_BLIND.csv` (30 rows, conditional) — keys in the matching `_KEY.csv` files, do not open first |
| figures | only two drafts exist: `notes/figs/t2c_pairs.png`, `notes/figs/c3_transfer.png` |

Round-3c outcomes in one line each (unverified by you): U1 NOT MET — the likelihood readout is learned (AV 0.781 vs
un-finetuned Qwen 0.469 raw topic accuracy, paired +0.312 [0.244, 0.388]); X3 INCONCLUSIVE at n=74 — factual margins
~0.001–0.003 with or without the snippet; X1 NOT MET — the layer-20 AV reads entities at blocks 16/24/27, best at 24;
N3 INCONCLUSIVE — the frozen scorer prices a wrong specific and a generic the same (0.0025 vs 0.0022; omitted 0.050);
N4 descriptive — the target's entity-vs-phrasing displacement ratio peaks at blocks 24–25; X1b descriptive — block 27
breaks the format; RT blocked at gate G2; M uninformative (147/200 generations truncated before "Answer:").

---

## 0. Establish the real constraints — 20 min [YOU]
- [ ] Open the live application form and confirm: deadline and timezone, required questions and limits, document format
      and sharing, AI-use disclosure, whether submissions can be edited. Do not rely on the FAQ copy in `notes/` alone.
- [ ] Fill in: deadline _____; planned submission time (≥ 6 h earlier) _____; human hours already used _____ (reconstruct
      honestly from memory and git timestamps: rounds 1–3c planning, reviews, advisor exchanges); permitted hours
      remaining _____; protected sleep window _____.
- [ ] Choose the route. **Standard** ≈ 10 h of your effort incl. review (§1–5). **Compressed** ≈ 4 h: §0 → rough answers
      and report 60 min → headline audit 60 min → text + two simple figures 60 min → final checks and submit 40 min;
      omit T2b, C3/N3/N4 diagnostics, bespoke graphics, extra reading. Work in 45–60-min blocks.
- [ ] Milestones: rough application complete by **+3 h**; submission-ready by **Thu Sept 10 evening EDT**; final read
      after sleep; submit by **Fri Sept 11 ~20:00 EDT** (≥ 6 h buffer). Do not treat the 85 hours as working hours.
- [ ] [AI → YOU] repository state is as in the table above; defer any cleanup (worktree removal, out/ pruning) until after
      submission. No push is required.

## 1. Produce a complete rough application — 90 min [YOU]
The first deliverable is something that could be submitted with corrections. Do not wait for reading, figures,
annotations or anything else.
- [ ] Copy every required form question and its limit into a working document; draft an answer to each, including the
      non-research ones. Mark factual gaps explicitly.
- [ ] Rough executive summary and report skeleton (official limits from §0; ≤ 600 words is the working target): question,
      method, three findings, limitations, next decisive experiment.
- [ ] Central claim in your words. Working formulation: *On this released 7B NLA, high reconstruction cosine does not
      translate into reliable verification of the tested factual edits; local-token description content supplies much of
      the score; a forced-prefix likelihood readout from the same verbalizer is a learned, activation-dependent route to
      some source information (topic reliably, entities weakly), and it works away from the training layer.* Do not claim
      hidden cognition, general truth detection, or a bound on what the activation contains.
- [ ] Contribution statement: which question you chose, which control changed your mind (the paraphrase null on night
      one), which decisions were yours, what you personally checked (§2). Do not claim to have written agent scripts.
      Follow the form's AI-use policy for drafting and disclosure.
- [ ] [AI] on request: figure drafts (§4) and a claim → evidence trace for any number you use (`notes/evidence_table.md`
      already lists path, filter, columns, n, CI method, PRE/REP/EXP/DESK status for every number through round 3c).
Done when every required answer has a rough draft and unresolved evidence is visibly marked.

## 2. Audit the evidence supporting the headline — 100 min [YOU] (+45 min conditional)
- [ ] **(a) Edit validity, blind — 35 min [AI → YOU].** `notes/s3_edit_validity_BLIND.csv`: 18 accepted evaluation triples,
      shuffled, edit order randomised, full prefix attached. For each: is the original claim supported by the prefix;
      does edit_1 / edit_2 change the proposition; does either differ in length, final tokens, grammar or extra changes?
      Mark ambiguous cases. Then open `notes/s3_edit_validity_KEY.csv`. Record counts in `notes/human_log.md`. This is a
      qualitative audit of the sampling rule, not a validation of all 490. Do not drop rows from the estimate afterwards.
      Known from the agent side: corruptions change a median of 1 word, paraphrases 14; 6/490 corruptions are
      punctuation-only, one of them (row 465) a non-edit.
- [ ] **(b) Re-derive the central results from raw data — 40 min [YOU].** Paste each line and result into
      `notes/human_log.md`. Select evaluation rows by the `split` / `stim_idx` fields, never by row order. These are
      **paired choice accuracies** where marked, not AUROCs (AUROCs are in the bench summaries).
      ```
      # reconstruction and controls (expect own 0.8820, same-doc 0.3664, cross-doc 0.3198, empty 0.3471)
      uv run python -c "import pandas as pd;s=pd.read_csv('overnight/s1_recon.csv');e=s[s.split=='eval'];print(e[['cos_own','cos_shuffled_samedoc','cos_shuffled_doc','cos_empty']].mean().round(4).to_dict(),len(e))"
      # corruption vs paraphrase cost, paired (expect A 0.00313, P 0.00494, A−P −0.00181, n=490)
      uv run python -c "import pandas as pd;s=pd.read_csv('overnight/s3_scores.csv');e=s[(s.stim_idx>=40)&s.edit_ok];p=e.pivot_table(index='row',columns='edit_type',values=['cos_z','cos_z_edit']);A=p[('cos_z','corrupt')]-p[('cos_z_edit','corrupt')];P=p[('cos_z','paraphrase')]-p[('cos_z_edit','paraphrase')];print(A.mean(),P.mean(),(A-P).mean(),len(A))"
      # last-claim-alone lift (expect mean 0.8837, median 0.9253, n=160)
      uv run python -c "import pandas as pd;r=pd.read_csv('overnight/r3_curve.csv');x=r[(r.direction=='last')&(r.k==1)&(r.stim_idx>=40)];print(x.lift.mean(),x.lift.median(),len(x))"
      # topic readout, held-out prefix: paired accuracy raw / corrected (expect 0.781 / 0.944)
      uv run python -c "import pandas as pd;a=pd.read_csv('overnight/t2a_scores.csv');e=a[a.split=='eval'];print((e.p3_true>e.p3_foreign).mean(),(e.p3_true_corr>e.p3_foreign_corr).mean())"
      # U1: AV minus un-finetuned baseline, paired raw accuracy (expect 0.312; AV 0.781, base 0.469)
      uv run python -c "import pandas as pd;u=pd.read_csv('overnight/u1_topic.csv');e=u[u.split=='eval'];av=(e.av_p3_true>e.av_p3_foreign);b=(e.base_p3_true>e.base_p3_foreign);print((av.astype(int)-b.astype(int)).mean(),av.mean(),b.mean(),len(e))"
      # X1: entity donor sensitivity and both-correct by layer (expect donor 1.64/1.74/2.94/1.83; both 0.275/0.225/0.40/0.225)
      uv run python -c "import pandas as pd;x=pd.read_csv('overnight/x1_entity.csv');print(x.groupby('layer').donor.mean().round(3).to_dict(),x.assign(b=(x.D_a>0)&(x.D_b<0)).groupby('layer').b.mean().round(3).to_dict())"
      # entity readout at block 20 (expect 1.738 / 0.775 / 0.225)
      uv run python -c "import pandas as pd;t=pd.read_csv('overnight/t2c_pairs.csv');d=t.p1_D_a-t.p1_D_b;print(d.mean(),(d>0).mean(),((t.p1_D_a>0)&(t.p1_D_b<0)).mean())"
      ```
      Read the few lines that compute each statistic (`overnight/s3_corrupt.py` ~line 196, `r3_truncate.py`, `t2a_audit.py`,
      `u1_base.py`, `x1_layers.py`) so you can say what each number is.
- [ ] **(c) Metrics and uncertainty — 15 min [AI → YOU].** Confirm: accuracy vs AUROC labelled everywhere; summed vs
      per-token likelihoods stated; the prior correction subtracts each interpreter's **own** no-injection run (U1 does);
      bootstrap units (document for topics, explanation for claims, template for entity pairs); X3's 74 rows are 53
      explanations; C3's four margins per cell are not independent. Resolve concrete discrepancies only.
- [ ] **(d) Inspect raw outputs — 10 min [YOU].** `overnight/u1_summary.md` ten fixed rows (line 54); `x1_summary.md`
      per-layer table; five verbatim rows in `x3_summary.md`; the four examples in `x1b_summary.md` (block 27 breaking);
      `rt_summary.md` 16 contexts; the C1 reorder rows in `c1_summary.md`. Decide the strength of each claim; a
      discrepancy in a headline is resolved or the claim is removed; in a secondary analysis it goes to the appendix.
- [ ] **Conditional (45 min, only if T2b goes in the main text):** label `notes/t2b_support_sheet_BLIND.csv` against
      `full_prefix_to_pos` + `token_str` (the prefix column ends *before* the current token; read them once, in that
      order); labels supported / contradicted / unsupported / not assessable; lock labels, then join with the key:
      `uv run python -c "import pandas as pd;b=pd.read_csv('notes/t2b_support_sheet_BLIND.csv');k=pd.read_csv('notes/t2b_support_sheet_KEY.csv');m=b.merge(k,on='blind_id');print(m.groupby('label')[['d_own','d_pos2','d_foreign','d_noinj']].agg(['mean','median','count']))"`.
      Default under time pressure: describe T2b as AV self-consistency in one sentence and leave the audit as future work.

## 3. Position the work and settle the claims — 45 min [YOU]; [AI] extracts sections on request
| source | what it contributes | where |
|---|---|---|
| NLA paper (Fraser-Taliente et al. 2026) | weak per-claim verifier; theme > detail accuracy; steganography transforms; warm-start prompt mandates the final-token feature; late-layer NLA applied to earlier layers "less coherent"; future work lists best-of-N and claim ablation | `notes/nla_paper_2026_text.txt`, `notes/nla_paper_card.md` |
| Dingeto 2026 (arXiv 2607.20379) | same released pair: ≈2% of specific claims grounded, paraphrase keeps 0.89, ridge ceiling specifics ~6% vs gist ~18–50%, flat across layers 16–27; our finding 2 is a replication with a paired design | `notes/dingeto_2026_train_the_model_text.txt` §3.1 + App. E |
| Building Better Activation Oracles | hallucination and text-inversion confounds; source information ≠ hidden cognition | index in `notes/mats_paper_index.md` |
| Are SAEs Useful? (sparse probing) | baselines decide value; only compare identical tasks, items, labels (U1 and T2a do; the AR probe vs AV ranking do not) | same |
| Towards Principled Evaluations of SAEs | approximation / interpretation / control are separate axes; we have not established control (RT stopped at its gate) | same |
- [ ] Write the contribution narrowly: a controlled diagnosis and readout comparison on one released NLA, with a
      replication of Dingeto's claim-level insensitivity, plus what is ours (per-position decomposition with a reorder
      control; source-edit pairs; the AV's own likelihood as a readout with baseline, donor and cross-layer controls;
      promptability/steering; injected-direction sensitivity). No "first", no "field-wide failure".
- [ ] Apply the §6 corrections to the draft now.

## 4. Finish the report and figures — 2 h 45 min [YOU]; [AI → YOU] for figure drafts
- [ ] **Three simple figures** [AI drafts, 45 min of YOU to verify every value against its CSV]:
      1. Reconstruction and edit costs: bars own / same-doc / cross-doc / empty / blind / raw-context (`s1_recon.csv`,
         `s4_recon.csv`) and a second panel with corruption 0.0031 vs paraphrase 0.0049 vs off-topic 0.114 (`s3_scores.csv`).
      2. Local snippet: truncation curve (`r3_curve.csv`) and the reorder control (`c1_summary.md` deletion costs).
      3. Targeted readout: paired accuracy raw / corrected for AV, un-finetuned baseline, no-injection, swap, text-only
         (`u1_topic.csv`, `t2a_scores.csv`); beside it the per-layer entity donor effect and both-correct (`x1_entity.csv`)
         or the existing donor-pair scatter (`notes/figs/t2c_pairs.png`). Never mix cosine, AUROC and accuracy on one axis.
      Appendix material if wanted: C3 transfer (`notes/figs/c3_transfer.png`), N3 four-way, N4 layer curve, X3 backgrounds,
      T3/T4 grids, the RT gate table, M's truncation count.
- [ ] Captions: what changed, what was held fixed, n, the conclusion supported. Detailed provenance stays in
      `notes/evidence_table.md`, not on every figure.
- [ ] **Rewrite** (90 min): explain AV and AR once; distinguish description edits from source edits; two or three
      strongest findings; the negative result as a limit on using reconstruction for the tested verification task; the
      readout as a bounded, learned alternative with raw scores, the modest entity result, and the layer transfer.
- [ ] **Methods, limitations, provenance, next steps** (30 min): checkpoint, block 20 (`hidden_states[21]`, 0.75 depth),
      injection (marker 149705, norm 150), scoring definitions (summed log-prob of `" " + candidate`; cos; MSE = 2(1 − cos)),
      split, exclusions, cluster units, exploratory choices (prior correction; X1 on reused items). Limitations: synthetic
      edits with an uncontrolled edit-size difference (1 vs 14 words); limited human validation; templated contexts;
      one checkpoint; no control-tier result; topic task solvable from text (98.8%). Crash fixes, all before any scored
      output: `overnight/RUNLOG.md` lines 12, 24, 58 and the round-3c U0c line. Rounds 3c ran as a background agent
      rather than a `/loop`. Next decisive test: the round-trip relational task at a position where the donor patch
      works (RT's gate failed at the pre-answer token), or the 27B replication (§7).
Done when a reviewer finds no missing section and no promise of imminent results.

## 5. Adversarial review, revise, submit — 1 h 45 min [YOU]
- [ ] [AI, YOU supplies the draft] one bounded skeptical review: factual/numeric errors, unsupported claims, unclear
      comparisons, missing required answers, three highest-value changes; blockers separated from polish; no new
      experiment unless a headline cannot otherwise be defended. Agent checks figures against the evidence table.
- [ ] (40 min) Resolve blockers and the top three. Explain aloud: what cosine measures; why corrupted and paraphrased
      descriptions differ; source edits vs description edits; why a donor effect is not entity accuracy; why prior
      correction is exploratory; why the baseline control matters and what "text-only 0.988" bounds. Simplify what you
      cannot explain. No second open-ended review cycle.
- [ ] (20 min) Read the form answers first, then the summary, as Neel would: question, judgment, surprising number,
      limits. Remove canned phrasing and contributions you did not make.
- [ ] (25 min) Final checks: limits and AI/time disclosures against the live rules; reviewer access to the doc and any
      repo link; placeholders removed; figures render; local export saved; exact submitted materials preserved.
- [ ] (20 min) Submit at the planned time; save the confirmation. Do not silently replace submitted evidence later.
**Submission-ready gate:** all required answers complete, headline claims checked in §2, links accessible, remaining
allowance recorded, submission could happen now. Protect sleep and the buffer even if compute is idle.

## 6. Corrections to keep beside the draft (reference)
- Reconstruction: "high reconstruction cosine", not "faithful". 88% is lift in cosine above the empty-text baseline,
  not 88% of facts. Claim deletion vs random span does not prove the AR treats claims as semantic units.
- Finding 2 is a **replication** of Dingeto's claim-level insensitivity on this checkpoint (cite first); ours adds the
  paired same-claim design, the every-claim version, and the edit-size confound stated plainly. "Substantially more
  sensitive to the tested paraphrases and off-topic substitutions than to the tested factual corruptions"; never
  "syntax over semantics"; both penalties are small.
- C2/C3: source edits regenerate activation and description; matched margins 0.0175 vs 0.0097, inconclusive difference,
  not equivalence; the margin–distance correlation is descriptive and shares geometry with the margin.
- Readout: "learned, activation-dependent" is now supported by U1; "recovered from the activation" means recovered by an
  activation-only reader, not information a text reader lacks (text-only 0.988). Prior correction is exploratory; the
  held-out prefix is prefix transfer on the same 160 documents. Donor sensitivity ≠ reliable identification
  (accuracy 0.60, both-correct 0.225 at block 20; 0.70 / 0.40 at block 24, exploratory on reused pairs).
- Claim-word readout (T2b) is self-consistency plus position dependence; foreign ≈ no injection are close means, not
  equivalence; lexical absence from the prefix is not falsehood.
- Prompting/steering: "the tested instructions did not produce the requested changes"; T3 at fluent doses gave 5.7%
  French; T4 is injected-concept sensitivity, not outside-J-space; angles as angles (18° ≈ 31% of norm).
- Round 3c: X3 is INCONCLUSIVE at n=74 (gate failed), not "no effect"; N3 describes the frozen scorer, not training;
  RT is a gate failure; M is a truncation artefact of the 200-token budget; X1b's block-27 collapse is coherence, not
  readout (X1 still reads entities there).

## 7. OPTIONAL after the §5 gate: bounded 27B replication on RunPod
Unchanged from the 2026-09-07 plan: only after submission-ready, ≥ 18 h to planned submission, ≥ 90 min of unused
allowance; one on-demand H200, one 12 h session with a provider-side stop, ≈$60; Celeste's Qwen3.6-27B NLA only;
agent brief and gates as written in `notes/round3c_plan_draft.md` §"27B" and the earlier plan; your attention ≤ 90 min;
add at most one paragraph and one panel. Default with the current clock: skip; name it as future work.

## 8. The advisor's six checkboxes, with state as of now
- [x] Freeze the model-control interface, existing datasets, prefixes and metrics — done in PLAN.md round 3c (U1 asserts
      identical token ids, injection, mask and scoring; prefixes and candidates frozen since rounds 3/3b).
- [~] Run 3c-1 and inspect representative raw scores — **run done (U1)**; the ten fixed rows are unread → §2(d).
- [~] Audit eligibility and factual validity for 3c-2, then run it — eligibility audited (211 eligible, 74 valid
      matched deletions, gate failed as pre-declared, run on the 74); factual validity by the target-model judge left
      n=1 usable, so the **human validity audit is still open** → §2(a).
- [ ] Update the main conclusions and figures using those results — not started → §1, §4.
- [~] Run 3c-3 only if allowance and writing time remain — ran as a gated pilot at zero human cost; stopped at gate G2
      (11/16); routes not run.
- [ ] Freeze experiments and complete the application — experiments are frozen now; the application is §1–5.

## 9. Ask the desk for, when you are back at it
Figure drafts from the §4 pointers; the bounded skeptical review of your draft; a number-by-number check of any
paragraph against `notes/evidence_table.md`; section extracts from the papers in §3. Nothing else is queued.

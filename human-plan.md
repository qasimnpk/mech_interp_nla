# human-plan.md — from here to a submitted MATS application (revised Wed 2026-09-09 12:00 EDT, after round 4)

**Clock.** Now: **Wed 2026-09-09 ~12:00 EDT**. Deadline in Neel's FAQ: **Fri Sept 11, 11:59pm PT = Sat Sept 12, 02:59 EDT**,
about **63 elapsed hours** from now. Human budget ≈16 h (max 20) of active project work + 2 h for the executive summary.
Verified in the FAQ ("Defining the 20+2 hour time limit"): **not counted** = general prep reading, generic cloud-GPU setup,
breaks, waiting for runs, writing the application-form answers; **counted** = anything actively directed at the project,
which includes reviewing agent output and deciding what it means — so the round-4 design, the advisor exchanges and last
night's desk discussion all count. Re-estimate the hours used in §0 before anything else.

**Decision:** finish the 7B application. **Experiments are frozen again**; round 4 ran 2026-09-09 02:00–10:35 EDT and is
**merged into main** (2026-09-09; worktree removed, branch kept). Rounds 1–4 are all on main; `overnight/` on main is the
record.
Tags: **[YOU]** your judgment or writing · **[AI]** delegated execution · **[AI → YOU]** agent output you must inspect.
Checkboxes are tasks, not claims that work happened. Work top to bottom; each block moves the application closer.

**What changed since the 2026-09-08 revision.** (1) Round 4 ran with Claude as editor/judge and produced two positive
results (K1, D1), one design failure (B1) and one under-powered test (A1) — read the one-liners below and the reading in
`notes/desk_session_2026-09-09_summary.md` §5 before touching the draft. (2) Dingeto overlap was re-audited against the text:
its "≈2%" is a **reconstruction-sensitivity lower bound, not a truth rate** — the wording in §3 and §6 is corrected below.
(3) The advisor asked for a short provenance paragraph (first contact 2026-09-07; what was complete; what changed after).
(4) The write-up structure is now four findings (§1), not three. ## Where things stand (facts, read once — 10 min) [YOU]


| item                      | state                                                                                                                                                                                                                                                                                                                             |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| results and reports       | `overnight/MORNING1.md … MORNING4.md` on main (round 4 merged 2026-09-09); kill lines in `overnight/DISCONFIRMATION.md`; every number's source through round 3c in `notes/evidence_table.md` (**round-4 rows not yet added** → §2(f))                                                                                             |
| one-page synthesis        | `notes/desk_session_2026-09-09_summary.md` (agent draft: ledger, settled answers, Dingeto correction, round-4 rationale, write-up structure) supersedes `notes/state_of_knowledge_2026-09-07.md` as the starting point; both are agent drafts to rewrite in your voice                                                            |
| positioning               | `notes/response_to_reframing_2026-09-07.md`, `notes/novelty_vs_nla_paper.md` §E; `notes/setup_comparability.md` (desk, 2026-09-08 — **still untracked in git**, add it in §0); Dingeto text in `notes/dingeto_2026_train_the_model_text.txt`                                                                                      |
| human-verified numbers    | **none yet.** All re-derivations in `notes/human_log.md` are agent-side. The hours table still says `_fill_`                                                                                                                                                                                                                      |
| blind sheets (unlabelled) | rounds 1–3: `notes/s3_edit_validity_BLIND.csv` (18), `notes/t2b_support_sheet_BLIND.csv` (30). **Round 4:** `overnight/d1_review_blind.csv` (260 rows), `k1_review_blind.csv` (102), `a1_review_blind.csv` (255, natural-error pairs first), `b1_review_blind.csv` (8); keys in the matching `_review_key.csv` — open blind first |
| provisional labels        | every round-4 truth / equivalence / edit label was produced by the orchestrator (Claude), `label_source=claude`; `a1_analyze.py --labels` and `b1_analyze.py --labels` recompute from your labels                                                                                                                                 |
| figures                   | two drafts exist: `notes/figs/t2c_pairs.png`, `notes/figs/c3_transfer.png`; nothing for round 4                                                                                                                                                                                                                                   |
| claim prevalence          | `notes/claim_prevalence_sample_2026-09-08.md`: 44 claims hand-labelled by the agent (45% true / 52% false-on-topic / 2% off-topic; final-token slot 13/14 true; middle "quoted sentence" slot 3/16) — indicative only                                                                                                             |


**Round-4 outcomes in one line each (unverified by you; the kill lines are in** `DISCONFIRMATION.md`**):**

- **B1 INCONCLUSIVE by n = 0 — a design failure, not a null.** All 64 sampled explanations at the final token of "The record ends
here." describe that closing sentence only (omission 64/64); the two activations of a pair agree at cos 0.993. A fact ten
tokens back behind a full sentence is not verbalized. Third time local dominance has decided an experiment.
  **B1 in prose (closed 2026-09-09; paste into the write-up as finding 2's second half and the limitations line):**
  B1 was the controlled version of the round-3 C2 test: 32 pairs of passages identical except for one fact — a recipient, an
  order, a count or an outcome — each ending with the neutral sentence "The record ends here.", with the activation read at
  that final period. The verbalizer described the closing sentence in all 64 explanations and never stated the fact one
  sentence earlier; the two activations of a pair agreed at cosine 0.993. With no explanation asserting either meaning there
  was nothing to swap or score, and the pre-registered statistic was never computed (INCONCLUSIVE, n = 0). This is a design
  failure rather than a null: the shared-suffix design moves the extraction point off the fact, and this verbalizer reports
  what is local to the extraction point. C2 worked in round 3 because its contexts ended on the fact. The test can be run at
  the period that closes the fact sentence, the secondary position round 4 cut for time.
- **A1 INCONCLUSIVE by n = 4.** 51 of 54 AV sentences were contradicted by their own prefix (each bundles an invented specific);
32 of 39 rejected corrections needed two or three facts changed, so the single-wrong-fact assumption fails for this verbalizer.
On the 4 slots: G 0.0032 [−0.0004, 0.0067]; aggressive-paraphrase |Δ| 0.0043 — wording noise ≈ signal.
- **K1 NOT MET.** The reconstructor ranks the verbalizer's own word first among 8 one-word variants at 0.31 (word in prefix)
and 0.25 (not in prefix) vs chance 0.125, both CIs above chance; the local token at 0.45 with a gap 9× larger. Read as
self-consistency of the trained pair, weakly modulated by grounding — not truth.
- **D1 NOT MET.** Subtracting a claim's reconstructor direction removes its word from the re-verbalization more than a random
claim direction: persistence 0.49 vs 0.70 (diff 0.21 [0.11, 0.31]); displacement matched (cos(h′,h) 0.955 vs 0.957), no
format breaks. Grounded words persist 0.70 / 0.85 (own / random), ungrounded 0.29 / 0.56: **invented specifics are fragile
under small activation edits, grounded ones stable.** Measures verbalizer output only.



---



## 0. Establish the real constraints and merge — 30 min [YOU]

- [x] Live form checked (deadline, limits, format, AI-use disclosure, editability) — done 2026-09-08. Re-check only the
  AI-use disclosure wording now that an agent labelled round-4 data.
- [ ] **Re-estimate hours honestly.** As of 2026-09-08 13:55 you recorded 12 h used / 4 h remaining. Add: round-4 design
  and advisor review (evening of 09-08), the desk discussion (09-08 → 09-09), any reading of MORNING4. Hours used now `_10_`; permitted remaining `_10_` (of 16, hard max 20) + 2 h for the exec summary. Protected sleep window `_10_`.
- [x] **Route.** With ≤ 4–6 h of counted time left the **Compressed** route is the realistic one: §0 → §1 rough answers and
  report (60 min) → §2 audit capped at 90 min (round-4 blind sheets first) → §4 text + three simple figures (75 min) → §5
  checks and submit (40 min). Drop T2b, C3/N3/N4 diagnostics, bespoke graphics, extra reading. Work in 45–60-min blocks.
- [x] **Milestones:** rough application complete by **today +3 h**; submission-ready by **Thu Sept 10 evening EDT**; final
  read after sleep; submit by **Fri Sept 11 ~20:00 EDT** (≥ 6 h buffer). Do not treat the 63 hours as working hours.
- [x] **Round 4 merged into main** (2026-09-09 ~13:00 EDT): fast-forward onto `nightshift/round4`, then your commit `1334d8a`
  (this plan + `notes/setup_comparability.md`); the round-4 `.npz` caches and logs are in `overnight/out/` on main; the
  nightshift worktree is removed (branch `nightshift/round4` kept as a pointer). One checkout, one branch: everything is here.
  No push (a GitHub remote exists; leave it alone until after submission).



## 1. Produce a complete rough application — 90 min [YOU]

The first deliverable is something that could be submitted with corrections. Do not wait for reading, figures,
annotations or anything else.

- [ ] Copy every required form question and its limit into a working document; draft an answer to each, including the
  non-research ones. Mark factual gaps explicitly.
- [ ] Rough executive summary and report skeleton (≤ 600 words working target): question, method, **four findings**,
  limitations, next decisive experiment. **Opening, decided 2026-09-08:** sentence 1 is the NLA paper's own line that the AR
  "is only a weak per-claim verifier"; sentence 2 is Neel's question from the FAQ (L721: use the AR "to measure the quality
  of a description, e.g. figuring out which claims can be removed … to help reduce hallucinations"); sentence 3 is your
  answer on the released checkpoint. The lineage must be visible in the first paragraph.
- [ ] **Four findings, in this order (decided 2026-09-09 after round 4):**
  1. The reconstruction score is a relevance-and-wording detector anchored on the final-token snippet, not a fact checker —
    replicates Dingeto on the same checkpoint with a paired design (paraphrase 0.0049 > corruption 0.0031; wrong specific =
     generic 0.0025 vs 0.0022; omitted 0.050; off-topic 0.114).
  2. Local dominance is strong enough to decide what can be tested: the snippet carries 88% of the lift and keeps 79% of its
    cost when moved; at a sentence-final position the verbalizer describes only the closing sentence (B1, 64/64), so the
     shared-suffix design cannot be run with this pair.
  3. The reconstructor prefers the verbalizer's own words regardless of grounding (K1: 0.31 / 0.25 vs 0.125; local token
    0.45) — self-consistency of the trained pair bounds any verifier built on the score. Connects to T2b (13 nats own vs
     2.9 foreign) and to Dingeto's append-and-rerank and private-codes results.
  4. Invented specifics are unstable under small activation edits while grounded ones survive (D1: 0.29 vs 0.70 under own
    ablation; 0.56 vs 0.85 under a random rotation of the same size) — a label-free stability signal for grounding, and the
     one result with a practical use. The likelihood readout (U1/T2a/T2c) becomes a supporting paragraph, not a headline.
- [ ] Central claim in your words. Working formulation: *On this released 7B NLA, reconstruction cosine measures relevance,
  wording and the local next-token description; it does not verify the tested factual edits, and it prefers the verbalizer's
  own wording whether or not a claim is grounded. Grounding shows up elsewhere: claims that survive a small rotation of the
  activation are the grounded ones.* Do not claim hidden cognition, general truth detection, or a bound on what the
  activation contains.
- [ ] **Provenance paragraph (advisor, 2026-09-09; keep it to ~80 words, no apology, no priority claim):** rounds 1–3 were
  designed and run before Dingeto was found on 2026-09-07; the base-model control (3c) and round 4's paraphrase averaging,
  crossed design, K-way ranking and direction ablation were designed after reading it; finding 1 replicates its claim-flip
  result, findings 3–4 extend it. Dated plans and logs are the chronology.
- [ ] Contribution statement: which question you chose, which control changed your mind (the paraphrase null on night one),
  which decisions were yours (all research choices; the round-4 A1/B1 design is yours), what you personally checked (§2).
  Do not claim to have written agent scripts. Round-4 labels were produced by Claude and checked by you (§2e). Follow the
  form's AI-use policy for drafting and disclosure.
- [ ] [AI] on request: figure drafts (§4) and a claim → evidence trace for any number you use.

Done when every required answer has a rough draft and unresolved evidence is visibly marked.

## 2. Audit the evidence supporting the headline — 90 min cap [YOU] (round 4 first)

- [ ] **(e) Round-4 blind sheets — 35 min [AI → YOU], do first.** In this order, stop at the cap:
  1. `overnight/d1_review_blind.csv`, the first 20 `slot`-type items: for each, does the claim's word / claim survive in
    `new_explanation_1` and `_2` (you do not know which arm is which)? Record your persist labels, then open
     `d1_review_key.csv` and count agreements with `own_persist_word` / `random_persist_word`. Finding 4 depends on this.
  2. `k1_review_blind.csv`, 10 items: read the prefix tail and the 8 shuffled words; note whether the AV's word is plausible
    from the prefix at all. Then the key. Finding 3 is robust to this; you are checking the strata, not the ranks.
  3. `b1_review_blind.csv`~~, all 8 rows: confirm the explanations describe only "The record ends here." (finding 2).~~ **DONE 2026-09-09: 8/8** `neither`**, agree with key 8/8; logged in** `notes/human_log.md`**.**
  4. `a1_review_blind.csv`, the natural-error pairs only (first ≤ 15 rows): is the original really contradicted and the
    correction entailed? Then the key. This validates the "51/54 contradicted, multi-fact inventions" sentence.
  Record counts in `notes/human_log.md`. Provisional labels stay marked as Claude's in the write-up.
- [ ] **(b) Re-derive the central results from raw data — 30 min [YOU].** Paste each line and result into `notes/human_log.md`.
  Select evaluation rows by `split` / `stim_idx`, never by row order. All files are in `overnight/` on main.
  ```
  # reconstruction and controls (expect own 0.8820, same-doc 0.3664, cross-doc 0.3198, empty 0.3471)
  uv run python -c "import pandas as pd;s=pd.read_csv('overnight/s1_recon.csv');e=s[s.split=='eval'];print(e[['cos_own','cos_shuffled_samedoc','cos_shuffled_doc','cos_empty']].mean().round(4).to_dict(),len(e))"
  # corruption vs paraphrase cost, paired (expect A 0.00313, P 0.00494, A−P −0.00181, n=490)
  uv run python -c "import pandas as pd;s=pd.read_csv('overnight/s3_scores.csv');e=s[(s.stim_idx>=40)&s.edit_ok];p=e.pivot_table(index='row',columns='edit_type',values=['cos_z','cos_z_edit']);A=p[('cos_z','corrupt')]-p[('cos_z_edit','corrupt')];P=p[('cos_z','paraphrase')]-p[('cos_z_edit','paraphrase')];print(A.mean(),P.mean(),(A-P).mean(),len(A))"
  # last-claim-alone lift (expect mean 0.8837, median 0.9253, n=160)
  uv run python -c "import pandas as pd;r=pd.read_csv('overnight/r3_curve.csv');x=r[(r.direction=='last')&(r.k==1)&(r.stim_idx>=40)];print(x.lift.mean(),x.lift.median(),len(x))"
  # K1: top-1 rate by stratum (expect in-prefix 0.308, not-in-prefix 0.252, last 0.449; chance 0.125)
  uv run python -c "import pandas as pd;k=pd.read_csv('overnight/k1_rows.csv');print(k.groupby('stratum').top1.mean().round(3).to_dict(),k.groupby('stratum').size().to_dict())"
  # D1: word persistence own vs random by stratum (expect in-prefix 0.696/0.848, not-in-prefix 0.289/0.556, last 0.55/0.80)
  uv run python -c "import pandas as pd;d=pd.read_csv('overnight/d1_rows.csv');c=d[d.own_persist_word.notna()];print(c.groupby('stratum')[['own_persist_word','random_persist_word']].mean().round(3).to_dict('index'),c.own_cos_hprime_h.mean().round(4),c.random_cos_hprime_h.mean().round(4))"
  # B1: pair similarity and omission (expect cos 0.9927; asserting sentences 0 of 192) — DONE 2026-09-09, got 0.9927 0 192, in human_log.md
  uv run python -c "import pandas as pd;c=pd.read_csv('overnight/b1_contexts.csv');s=pd.read_csv('overnight/b1_slots.csv');print(c.cos_hA_hB.mean().round(4),(s.asserts.isin(['A','B'])).sum(),len(s))"
  # A1: label counts (expect contradicted 51, entailed 2, undetermined 1)
  uv run python -c "import pandas as pd;a=pd.read_csv('overnight/a1_slots.csv');print(a.label_orig.value_counts().to_dict())"
  # topic readout, held-out prefix: paired accuracy raw / corrected (expect 0.781 / 0.944)
  uv run python -c "import pandas as pd;a=pd.read_csv('overnight/t2a_scores.csv');e=a[a.split=='eval'];print((e.p3_true>e.p3_foreign).mean(),(e.p3_true_corr>e.p3_foreign_corr).mean())"
  # U1: AV minus un-finetuned baseline, paired raw accuracy (expect 0.312; AV 0.781, base 0.469)
  uv run python -c "import pandas as pd;u=pd.read_csv('overnight/u1_topic.csv');e=u[u.split=='eval'];av=(e.av_p3_true>e.av_p3_foreign);b=(e.base_p3_true>e.base_p3_foreign);print((av.astype(int)-b.astype(int)).mean(),av.mean(),b.mean(),len(e))"
  ```
  Read the few lines that compute each statistic (`overnight/s3_corrupt.py` ~line 196, `r3_truncate.py`, `k1_kway.py`,
  `d1_ablate.py`, `t2a_audit.py`, `u1_base.py`) so you can say what each number is.
- [ ] **(a) Edit validity, blind — 25 min, only if time remains [AI → YOU].** `notes/s3_edit_validity_BLIND.csv` (18
  triples) as before; then the key; counts to `notes/human_log.md`. Under time pressure, state the edit-size confound
  (corruptions change a median of 1 word, paraphrases 14; 6/490 corruptions punctuation-only) and skip.
- [ ] **(c) Metrics and uncertainty — 10 min [AI → YOU].** Accuracy vs AUROC labelled everywhere; summed vs per-token
  likelihoods; prior correction subtracts each interpreter's own no-injection run; bootstrap units (document / explanation /
  template / pair); round-4 three-way rule stated once (CI ≤ 0 MET, > 0 NOT MET, straddles or n below minimum INCONCLUSIVE).
- [ ] **(d) Inspect raw outputs — 10 min [YOU].** `overnight/MORNING4.md` five verbatim examples for K1 and D1; `u1_summary.md`
  ten fixed rows; `x1b_summary.md` block-27 example. A discrepancy in a headline is resolved or the claim is removed.
- [ ] **(f) [AI → YOU] Evidence table: ask the desk to add the round-4 rows** (path, filter, columns, n, CI unit, PRE/REP/DESK)
  to `notes/evidence_table.md`, then spot-check two.
- [ ] **Skip** the T2b support sheet (30 rows); describe T2b as self-consistency in one sentence.



## 3. Position the work and settle the claims — 30 min [YOU]

**Framing (unchanged from 2026-09-08, sharpened 2026-09-09):** the project is the paper's weak-verifier experiment run
controlled on the released checkpoint, positioned as a replication-plus-extension of Dingeto. Headline = the extension (K1/D1
and what they say about self-consistency and grounding), not the replication.


| source                                                                           | what it contributes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | where                                                                                                                    |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Neel's FAQ, suggested problems L719–721**                                      | NLAs are a named problem; **"using the activation reconstructor to measure the quality of a description, e.g. figuring out which claims can be removed … to help reduce hallucinations"** — our S2/S3/R2/R3/C1/X3/K1. Your headline is the controlled check of that idea on the released 7B                                                                                                                                                                                                                           | `notes/neel_drive/mats12_admissions_procedure_faq.md` L706–721; L431–436 (negative results, "building on existing work") |
| NLA paper (Fraser-Taliente et al. 2026)                                          | "weak per-claim verifier"; theme > detail accuracy; steganography transforms; warm-start prompt mandates the final-token snippet; late-layer NLA applied earlier "less coherent"; future work: best-of-N, claim ablation, multi-layer NLA                                                                                                                                                                                                                                                                             | `notes/nla_paper_2026_text.txt`, `notes/nla_paper_card.md`, `notes/NLA_paper_experiment_setup.md`                        |
| Dingeto 2026 (arXiv 2607.20379)                                                  | same released pair: claim flips with per-edit validity; **≈2% of salient specific claims pass the flip-sensitivity threshold (4.2/2.1/1.6% at τ = 0.02/0.05/0.10) — a sensitivity-limited lower bound, NOT a truth rate**; paraphrase keeps 0.89, content-word mask 0.04; append-and-rerank control; ridge ceiling specifics ~6% vs gist ~18–50%; flat across layers 16–27; private codes in a synthetic sandbox (co-trained small models). Not in it: B1's crossed test, A1's paraphrase-averaged discrimination, D1 | `notes/dingeto_2026_train_the_model_text.txt` §3.1 + App. E; `notes/desk_session_2026-09-09_summary.md` §4               |
| IOI (ICLR 2023), RAVEL (ACL 2024), CounterFact (NeurIPS 2022)                    | advisor's precedents for controlled stimuli; **future work only** (an IOI arm would test the local token, which K1's positive control already covers)                                                                                                                                                                                                                                                                                                                                                                 | advisor message 2026-09-09                                                                                               |
| Building Better Activation Oracles; Are SAEs Useful?; Principled SAE Evaluations | hallucination/text-inversion confounds; baselines decide value; approximation ≠ control (RT stopped at its gate)                                                                                                                                                                                                                                                                                                                                                                                                      | `notes/mats_paper_index.md`                                                                                              |


- [ ] Write the contribution narrowly: a controlled diagnosis of one released NLA's reconstruction score, replicating
  Dingeto's claim-level insensitivity, plus what is ours (per-position decomposition with a reorder control; source-edit
  pairs; the AV's own likelihood as a readout with base-model, donor and cross-layer controls; K-way self-preference;
  direction-ablation stability). No "first", no "field-wide failure".
- [ ] Cite the NLA paper and Dingeto **before** your own numbers on finding 1; use "≈2% pass Dingeto's flip-sensitivity
  threshold", never "2% true".
- [ ] State weaknesses in one sentence each, in the main text: finding 1 overlaps Dingeto on the same pair; the 27B key
  resource does not fit this machine; round-4 labels are an LLM's, checked on a sample; A1/B1 under-powered by design
  failures you name.
- [ ] `notes/setup_comparability.md` §5–6: read (≤ 15 min), paste the methods sentences you keep.



## 4. Finish the report and figures — 2 h [YOU]; [AI → YOU] for figure drafts

- [ ] **Three simple figures** [AI drafts; 30 min of YOU to verify every value against its CSV]:
  1. Reconstruction and edit costs: bars own / same-doc / cross-doc / empty / blind / raw-context (`s1_recon.csv`,
    `s4_recon.csv`); second panel corruption 0.0031 vs paraphrase 0.0049 vs off-topic 0.114 (`s3_scores.csv`) with N3's
     wrong / generic / omitted.
  2. Local snippet: truncation curve (`r3_curve.csv`) and the reorder control (`c1_summary.md`); annotate B1's 64/64 omission
    as text, not a panel.
  3. Round 4: left, K1 top-1 by stratum vs chance 0.125 (`k1_rows.csv`); right, D1 word persistence own vs random × in-prefix
    (`d1_rows.csv`). Never mix cosine, rates and accuracy on one axis.
  The readout figure (U1/T2a/X1) moves to the appendix if the limit allows a fourth; otherwise a two-line table in the text.
- [ ] Captions: what changed, what was held fixed, n, the conclusion supported.
- [ ] **Rewrite** (60 min): explain AV and AR once; description edits vs source edits vs activation edits (D1); four findings;
  the readout as a bounded, learned alternative in one paragraph; provenance paragraph.
- [ ] **Methods, limitations, provenance, next steps** (30 min): checkpoint, block 20 (`hidden_states[21]`), injection
  (marker 149705, norm 150), scoring (cos; MSE = 2(1 − cos); summed log-prob for readouts), splits, exclusions, cluster
  units, the round-4 three-way rule, decoding (greedy in rounds 1–3 and D1; T = 1.0 seeded in A1/B1), who judged what.
  Limitations: edit-size confound (1 vs 14 words); LLM labels checked on a sample; `in_full_prefix` is a string proxy for
  grounding; one checkpoint; A1/B1 under-powered; D1 measures verbalizer output only; no control-tier result (RT gate).
  Next decisive tests: D1's stability signal as a grounding filter scored against human labels; the shared-suffix test at the
  fact sentence's own final token; the 27B replication.

Done when a reviewer finds no missing section and no promise of imminent results.

## 5. Adversarial review, revise, submit — 1 h 30 min [YOU]

- [ ] [AI, YOU supplies the draft] one bounded skeptical review: factual/numeric errors, unsupported claims, unclear
  comparisons, missing required answers, three highest-value changes; blockers separated from polish; no new experiment.
  Agent checks every number against `notes/evidence_table.md` (with the round-4 rows from §2f).
- [ ] (30 min) Resolve blockers and the top three. Explain aloud: what cosine measures; why a paraphrase costs more than a
  corruption; why K1 is self-consistency and not truth; why D1's random arm is the control and what "matched displacement"
  means; why B1 is a design lesson; what "2% pass the flip threshold" means. Simplify what you cannot explain.
- [ ] (15 min) Read the form answers first, then the summary, as Neel would: question, judgment, surprising number, limits.
  Remove canned phrasing and contributions you did not make.
- [ ] (25 min) Final checks: limits and AI/time disclosures against the live rules; reviewer access; placeholders removed;
  figures render; local export saved; exact submitted materials preserved.
- [ ] (20 min) Submit at the planned time; save the confirmation. Do not silently replace submitted evidence later.

**Submission-ready gate:** all required answers complete, headline claims checked in §2, links accessible, remaining
allowance recorded, submission could happen now. Protect sleep and the buffer even if compute is idle.

## 6. Corrections to keep beside the draft (reference)

- Reconstruction: "high reconstruction cosine", not "faithful". 88% is lift in cosine above the empty-text baseline, not
88% of facts. Claim deletion vs random span does not prove the AR treats claims as semantic units.
- Finding 1 is a **replication** of Dingeto's claim-level insensitivity on this checkpoint (cite first); ours adds the paired
same-claim design, the every-claim version, N3's generic control, and the edit-size confound stated plainly.
"Substantially more sensitive to the tested paraphrases and off-topic substitutions than to the tested factual
corruptions"; never "syntax over semantics"; both penalties are small.
- **Dingeto's "≈2%"** = fraction of salient specific claims whose flip moves reconstruction above threshold; the paper calls it
a sensitivity-limited lower bound. Never "2% of claims are true".
- **B1:** "with this verbalizer the shared-suffix design cannot be run at a sentence-final position: all 64 explanations
describe the closing sentence"; never "the fact is absent from the activation" (cos(h_A,h_B) = 0.993 says only that the
fact is a small part of it).
- **A1:** n = 4 is descriptive; the reportable facts are 51/54 sentences contradicted and corrections needing 2–3 fact
changes in 32/39 cases. Labels are Claude's, checked on ≤ 15 pairs.
- **K1:** "preference for the verbalizer's own word among matched one-word variants", modulated weakly by prefix presence;
`in_full_prefix` is a string proxy; the local-token stratum is the positive control, not a finding about upstream facts.
- **D1:** "the verbalizer stops asserting the claim" — verbalizer output only; no claim about the target model; own vs random
differ in direction, not displacement (0.955 vs 0.957); the grounded/ungrounded split is the interesting part and uses the
string proxy; α = 0.3 only; 111/140 rows at the cap.
- C2/C3: source edits regenerate activation and description; matched margins 0.0175 vs 0.0097, inconclusive difference.
- Readout: "learned, activation-dependent" (U1); "recovered from the activation" means by an activation-only reader, not
information a text reader lacks (text-only 0.988). Prior correction exploratory. Donor sensitivity ≠ identification
(accuracy 0.60, both-correct 0.225 at block 20).
- T2b is self-consistency plus position dependence; lexical absence from the prefix is not falsehood.
- Prompting/steering: "the tested instructions did not produce the requested changes"; T4 is injected-concept sensitivity;
angles as angles (18° ≈ 31% of norm).
- Round 3c: X3 INCONCLUSIVE at n=74; N3 describes the frozen scorer; RT is a gate failure; M is a truncation artefact.
- Comparability (`notes/setup_comparability.md` §5): our claim unit is a bullet, not an atomic claim; the paper's Claude
numbers are never numerically comparable, Dingeto's are; we did not run E1, E3.3, E4.1, E4.3, E5, E6 or E7.
- Lineage: "the paper's own weak-verifier test, run controlled on the released checkpoint"; the paper's transforms are
reproduced *in miniature*; their metric is FVE/MSE, ours cosine (MSE = 2(1 − cos)); say so once.



## 7. OPTIONAL after the §5 gate: bounded 27B replication on RunPod

Unchanged: only after submission-ready, ≥ 18 h to planned submission, ≥ 90 min of unused allowance. Default with the
current clock: **skip; name it as future work.** Brief in `notes/27b_extension_brief.md`.

## 8. Advisor checkboxes, with state as of now

- [x] Freeze the model-control interface, datasets, prefixes and metrics — done (round 3c).
- [x] Run 3c-1 and inspect raw scores — run done (U1); ten fixed rows still unread → §2(d).

- [~] Audit eligibility and factual validity for 3c-2 — eligibility audited; human validity audit optional → §2(a).

- [x] Run 3c-3 only if allowance remains — ran gated, stopped at G2.
- [x] Round 4 (2026-09-09): A1/B1 designed by you, K1/D1 by the desk; Claude as judge; blind review sheets; three-way rule;
  advisor's simplifications applied (no French, A/B only, one position, one strength). **Run complete.**
- [ ] Provenance paragraph for Dingeto (advisor, 2026-09-09) → §1.
- [ ] Update conclusions and figures with round 4 → §1, §4.
- [ ] Freeze experiments and complete the application — frozen; the application is §1–5.



## 9. Ask the desk for, when you are back at it

Round-4 rows for `notes/evidence_table.md` (§2f); figure drafts from the §4 pointers (including the K1/D1 panel); the
bounded skeptical review of your draft; a number-by-number check of any paragraph; the AUROC of D1's random-arm persistence
as a grounding detector against `in_full_prefix` (desk one-liner on `d1_rows.csv`, descriptive, for the future-work
sentence). Nothing else is queued; no experiment is running.
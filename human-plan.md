# human-plan.md — notes to submission (condensed 2026-09-11)

**Deadline:** Fri Sept 11, 11:59pm PT (= Sat 02:59 EDT). **Budget:** 16 h (max 20) of counted human work + 2 h for the exec
summary. Counted = anything aimed at the project, including reviewing agent output and deciding what it means. Not counted =
general prep reading, generic GPU setup, waiting on runs, writing the form answers. Toggl screenshot goes in the doc.
Your entry (2026-09-09): Hours used now `_10_`; permitted remaining `_10_` (of 16, hard max 20) + 2 h for the exec summary. Protected sleep window `_10_`.

Tags: **[YOU]** your judgment or writing · **[AI → YOU]** agent output you must inspect. Full pre-condensation version:
`git show 0ede032:human-plan.md`.

## Experiments — where each one is described

| experiment | question | read this for the setup | results |
|---|---|---|---|
| Round 1 · 09-06 · S0–S5 | Does the released 7B pair reproduce, and does reconstruction cosine work as a claim-usefulness score? (fidelity, claim vs random-span deletion, corruption vs paraphrase, blind describer, instruction following) | [round1_decisions.md](notes/round1_decisions.md); plan: `git show b01221e:overnight/PLAN.md` | [MORNING1.md](overnight/MORNING1.md) |
| Round 2 · 09-06 · R0–R3 | Where the fact-blindness sits: amplified corruption, last-token costs, truncation curve | [summary_rounds1-3.md](notes/summary_rounds1-3.md); plan: `git show d5e64d7:overnight/PLAN.md` | [MORNING2.md](overnight/MORNING2.md) |
| Round 3 · 09-06 · C1, C2, T1–T4 | Position vs content of the last snippet; matched one-fact activation pairs; AR as a text probe; forced-prefix readout; steering | [PLAN.md](overnight/PLAN.md) § Round 3 stages (L241) | [MORNING3.md](overnight/MORNING3.md) |
| Round 3b · 09-07 · T2c, T2a, T2b, C3 | Controls on the round-3 readouts: entity readout on C2 pairs, held-out wording, donor control, phrasing control | [PLAN.md](overnight/PLAN.md) § Round 3b (L425); [diagnostics_round3b.md](notes/diagnostics_round3b.md) | [MORNING3b.md](overnight/MORNING3b.md) |
| Round 3c · 09-08 · U1, X3, X1, N3, N4, X1b, RT, M | Base-model control, snippet interaction, cross-layer readout, frozen-AR rewards, layer curve, gated pilots | [PLAN.md](overnight/PLAN.md) § Round 3c (L585); [round3c_plan_draft.md](notes/round3c_plan_draft.md) | [MORNING3c.md](overnight/MORNING3c.md) |
| Round 4 · 09-09 · B1, A1, K1, D1 | Controlled paired contexts; natural claims with paraphrase averaging; K-way ranking; claim-direction ablation | **[round4_setup_for_advisor.md](notes/round4_setup_for_advisor.md)**; [PLAN.md](overnight/PLAN.md) § Round 4 (L781) | [MORNING4.md](overnight/MORNING4.md) |
| Round 5 + 5b · 09-09 · P1, P2, D2 | The 7B pair on the 27B's 8 example texts, claim type × truth side by side; D2 ablation on those claims | [PLAN.md](overnight/PLAN.md) § Round 5 (L1184), § 5b (L1245) | `git show nightshift/round5:overnight/MORNING5.md` (local branch; not merged, not on GitHub) |
| 27B smoke · 09-09 (pod) | Does the Qwen3.6-27B NLA run end to end? Claim annotation of its 8 explanations | [ceselder_27b_model_card.md](notes/nla_setup/ceselder_27b_model_card.md); [claim_annotation_protocol.md](notes/nla_setup/claim_annotation_protocol.md) | [annotated claims](notes/nla_setup/nla27b_smoke_claims_annotated.csv); [smoke output](fve_claims/logs_27b_pod/nla27b_smoke_out.json) |
| Claim-deletion FVE, 7B · 09-09→10 | Re-DocRED pilot, 100 docs: does deleting a true claim cost more reconstruction than deleting a false one? Plus paraphrase averaging | **[fve_claims_baseline_protocol.md](notes/fve_claims_baseline_protocol.md)**; [fve_claims/README.md](fve_claims/README.md); [ANNOTATION_GUIDE.md](fve_claims/ANNOTATION_GUIDE.md); [pilot README](data/redocred_pilot/README.md) | [05_summary_all_released.md](fve_claims/05_summary_all_released.md) (pre-audit, see §2); [audit_changelog.md](fve_claims/tasks/audit_changelog.md) |
| Claim-deletion FVE, 27B · 09-10 (pod) | Same protocol on the 27B pair, 100 docs, deletion and heavy paraphrase | [common_27b.py](fve_claims/common_27b.py) docstring (setup; av_base used as TARGET) | **[analysis_27b/README.md](fve_claims/analysis_27b/README.md)** (every number → its script) |

Across rounds: [DISCONFIRMATION.md](overnight/DISCONFIRMATION.md) (every kill line) · [setup_comparability.md](notes/setup_comparability.md)
(our setups vs the paper's) · [desk_session_2026-09-09_summary.md](notes/desk_session_2026-09-09_summary.md) (synthesis through
round 4, agent draft) · [evidence_table.md](notes/evidence_table.md) (number → source, through round 3c).

## Findings (decided 2026-09-09; 7B; unverified by you until §2)

1. The reconstruction score detects relevance and wording, anchored on the final-token snippet — not a fact checker.
   Replicates Dingeto on the same checkpoint (paraphrase 0.0049 > corruption 0.0031).
2. Local dominance decides what can be tested: the last snippet carries 88% of the lift; at a sentence-final position the
   verbalizer describes only the closing sentence (B1, 64/64).
3. The reconstructor prefers the verbalizer's own words regardless of grounding (K1: 0.31 / 0.25 vs chance 0.125).
4. Invented specifics are unstable under small activation edits, grounded ones survive (D1 persistence 0.29 vs 0.70).

**Round-4 outcomes:** B1 INCONCLUSIVE (n = 0, design failure) · A1 INCONCLUSIVE (n = 4) · K1 NOT MET · D1 NOT MET.
  **B1 in prose (closed 2026-09-09; paste into the write-up as finding 2's second half and the limitations line):**
  B1 was the controlled version of the round-3 C2 test: 32 pairs of passages identical except for one fact — a recipient, an
  order, a count or an outcome — each ending with the neutral sentence "The record ends here.", with the activation read at
  that final period. The verbalizer described the closing sentence in all 64 explanations and never stated the fact one
  sentence earlier; the two activations of a pair agreed at cosine 0.993. With no explanation asserting either meaning there
  was nothing to swap or score, and the pre-registered statistic was never computed (INCONCLUSIVE, n = 0). This is a design
  failure rather than a null: the shared-suffix design moves the extraction point off the fact, and this verbalizer reports
  what is local to the extraction point. C2 worked in round 3 because its contexts ended on the fact. The test can be run at
  the period that closes the fact sentence, the secondary position round 4 cut for time.

**Central claim (working; rewrite in your words):** on this released 7B NLA, reconstruction cosine measures relevance, wording
and the local next-token description; it does not verify the tested factual edits, and it prefers the verbalizer's own
wording whether or not a claim is grounded. Claims that survive a small rotation of the activation are the grounded ones.
Do not claim hidden cognition, general truth detection, or a bound on what the activation contains.

## 1. Application draft [YOU]

- [ ] Re-estimate hours (the `_10_` entries above are from 2026-09-09); fill the hours table in `notes/human_log.md`.
- [ ] Form answers first — Neel reads them before the write-up.
- [ ] Exec summary: ≤ 600 words, 1–3 pages, graphs, structured by finding. Opening: the paper's "weak per-claim verifier" line
  → Neel's FAQ L721 question (use the AR to find "which claims can be removed") → your answer on the released checkpoint.
- [ ] Provenance paragraph (~80 words): rounds 1–3 designed before Dingeto was found (2026-09-07); 3c and round 4 after;
  finding 1 replicates it, findings 3–4 extend it.
- [ ] Contribution and AI-use statement: which decisions were yours (all research choices; the A1/B1 design), what you checked
  (§2), what agents built and labelled.
- [ ] "What I verified and how" section, built from `notes/human_log.md`.
- [ ] **Decide** whether the claim-deletion FVE work goes in (§7).

## 2. Audits [YOU] — what Neel weighs most

- [ ] **(e) Round-4 blind sheets** — open the blind sheet, label, then the key; counts to `notes/human_log.md`:
  1. `overnight/d1_review_blind.csv`, first 20 `slot` items: does the claim word survive in `new_explanation_1` / `_2`?
     Then `d1_review_key.csv`. Finding 4 depends on this.
  2. `k1_review_blind.csv`, 10 items: is the AV's word plausible from the prefix at all? Then the key.
  3. `b1_review_blind.csv`~~, all 8 rows: confirm the explanations describe only "The record ends here." (finding 2).~~ **DONE 2026-09-09: 8/8** `neither`**, agree with key 8/8; logged in** `notes/human_log.md`**.**
  4. `a1_review_blind.csv`, natural-error pairs only (≤ 15): original really contradicted, correction entailed? Then the key.
- [ ] **(b) Re-derive the central numbers** — paste each line and result into `notes/human_log.md`. Select rows by `split` /
  `stim_idx`, never row order. Read the lines that compute each (`s3_corrupt.py` ~L196, `r3_truncate.py`, `k1_kway.py`,
  `d1_ablate.py`, `t2a_audit.py`, `u1_base.py`).
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
- [ ] **(d) Read raw outputs:** `overnight/MORNING4.md` verbatim K1 and D1 examples; `u1_summary.md` ten fixed rows;
  `x1b_summary.md` block-27 example. A headline that disagrees with the raw rows is fixed or removed.
- [ ] **If claim-deletion FVE goes in (§7):** spot-check ~20 atom labels per model against
  [ANNOTATION_GUIDE.md](fve_claims/ANNOTATION_GUIDE.md) (7B sheet: `fve_claims/02_review_blind_7b.csv`; the 27B labels have had
  no audit pass); regenerate the 7B tables — `05_summary_all_*.md` predate the entity/detail label audits (`e1c8166` before
  `52f02c9`…`4ab85d6`); re-run one number from [analysis_27b/](fve_claims/analysis_27b/README.md) yourself; check
  [redocred_pilot_review.md](notes/redocred_pilot_review.md) if not already done.
- [ ] **If round 5 goes in:** `p2_review_blind.csv` then `p2_review_key.csv` (branch `nightshift/round5`; merge it first).
- [ ] (a) Optional: `notes/s3_edit_validity_BLIND.csv` (18 triples). Under time pressure, state the edit-size confound instead
  (corruptions change a median of 1 word, paraphrases 14).
- [ ] (f) [AI → YOU] round-4 rows for `notes/evidence_table.md`; spot-check two.

## 3. Positioning [YOU]

- The work is the paper's weak-verifier experiment run controlled on the released checkpoint, positioned as replication plus
  extension of Dingeto. Headline = the extension (K1, D1), not the replication.
- Sources: Neel's FAQ L719–721 (`~/repos/mech_interp/notes/neel_drive/mats12_admissions_procedure_faq.md`, outside this repo);
  the NLA paper ([card](notes/nla_paper_card.md)); Dingeto 2026 ([text](notes/dingeto_2026_train_the_model_text.txt) §3.1 + App. E).
- Contribution stated narrowly; no "first", no "field-wide failure". Cite the paper and Dingeto before your own numbers.

## 4. Figures [AI drafts → YOU verify every value against its CSV]

1. Reconstruction and edit costs: own / same-doc / cross-doc / empty / blind (`s1_recon.csv`, `s4_recon.csv`); corruption 0.0031
   vs paraphrase 0.0049 vs off-topic 0.114 (`s3_scores.csv`).
2. Local snippet: truncation curve (`r3_curve.csv`) and the reorder control (`c1_summary.md`); B1's 64/64 as text.
3. Round 4: K1 top-1 by stratum vs 0.125 (`k1_rows.csv`); D1 persistence own vs random × in-prefix (`d1_rows.csv`).
   Never mix cosine, rates and accuracy on one axis.

## 5. Submit [YOU]

- [ ] One skeptical review of the draft [AI]: numbers against sources, unsupported claims, missing answers. No new experiments.
- [ ] Explain aloud: what cosine measures; why a paraphrase costs more than a corruption; why K1 is self-consistency, not truth;
  D1's random arm as the control; why B1 is a design lesson. Cut what you cannot explain.
- [ ] Final checks: limits; AI-use and time disclosures; Google doc set to anyone-with-link; repo access (GitHub repo is private);
  Toggl screenshot; submit and save the confirmation.

## 6. Wording rules (keep beside the draft)

- "High reconstruction cosine", not "faithful". 88% is lift above the empty-text baseline, not 88% of facts.
- Finding 1 is a replication. Dingeto's "≈2%" = claims passing its flip-sensitivity threshold, a lower bound — never "2% are true".
- B1: "the shared-suffix design cannot be run at a sentence-final position with this verbalizer"; never "the fact is absent from
  the activation".
- A1: n = 4 is descriptive; reportable: 51/54 sentences contradicted, 32/39 corrections need 2–3 fact changes.
- K1: "preference for the verbalizer's own word"; `in_full_prefix` is a string proxy for grounding.
- D1: verbalizer output only; own and random differ in direction, not displacement (cos 0.955 vs 0.957).
- Readout: "learned, activation-dependent" (U1) — not information a text reader lacks (text-only 0.988).
- Metric: the rounds use cosine (MSE = 2(1 − cos)); the paper uses FVE — say so once. 27B claim-deletion numbers use a local FVE
  denominator and av_base as TARGET — state both wherever they appear.
- Limitations, one sentence each: edit-size confound; LLM labels checked on a sample; A1/B1 under-powered; D1 measures the
  verbalizer only; no control-tier result (RT stopped at its gate).

## 7. Claim-deletion FVE (7B + 27B) — decision [YOU]

The most direct test of Neel's L721 question. Not in the four findings above. Agent-computed on the 27B, **unverified by you**:
detail claims show a within-document true − false deletion gap of 4.73 pp [1.30, 7.90], true > false in 57/91 documents
(sign test p = 0.021); entity has only 14 true claims (underpowered); heavy paraphrase adds nothing over deletion. If it goes
in, run the §2 audits first.

## Done

- [x] Live form checked (2026-09-08).
- [x] Route: Compressed.
- [x] Milestones set.
- [x] Rounds 1–4 merged into main; 27B runs pulled off the pod and pushed (2026-09-11).
- [x] B1 blind audit (§2e, item 3).

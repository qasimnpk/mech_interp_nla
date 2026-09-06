# Progress vs the advisor's strategy report — gap analysis (2026-09-06)

Agent-drafted scaffolding for the human. Numbers are copied from the cited files; nothing here is a
verdict beyond supported / unsupported / untested. Paths: `ADV` = `notes/advisor_nla_strategy_2026-09-06.md`;
`M1` = `overnight/MORNING1.md` (main); `P1` = round-1 plan, `git show b01221e:overnight/PLAN.md`;
`P2` = `overnight/PLAN.md` (main, round 2); `NS/` = `../mech_interp_nla-nightshift/overnight/` (read-only;
round 2 is finished there but NOT yet merged into main).

## A. Status

Two rounds have run on the released `kitft/nla-qwen2.5-7b-L20-av` / `-ar` pair over
`Qwen/Qwen2.5-7B-Instruct` block 20 (`hidden_states[21]`), chosen because the 27B pair does not fit
(`notes/round1_decisions.md:18-23`). Stimuli: 200 wikitext-2 positions, pilot 0–39, evaluation 40–199
(P1:138-147). Round 1 (02:18–05:40, M1:55-70): mean cos_own on the 160 evaluation positions **0.8820**
CI [0.8753, 0.8886] (M1:8, M1:125); same-doc shuffle **0.3664**, cross-doc 0.3198 (M1:9, M1:126-127);
empty explanation **0.3471** (M1:130); adjacent layers L19 0.8345 / L21 0.8359 (M1:128-129). Claim deletion
vs equal-length random span **D = 0.00578** CI [0.00224, 0.00964], n = 538 claims / 160 explanations
(M1:10, M1:227). LLM corruption of one claim **A = 0.00313** [0.00159, 0.00478] vs paraphrase
**P = 0.00494** [0.00354, 0.00665]; **A − P = −0.00181** CI [−0.00279, −0.00080] on **490** accepted
claims → K3 MET (M1:11, M1:272-274); deterministic swap A_det − P = −0.00137 [−0.00241, −0.00034], n = 402
→ MET (M1:12, M1:275-276). Prompt steering on 40 pilot items: mechanical follow rate **0/80** (V3+V4)
→ K5 MET (M1:13); agent-judged `followed` 0.000 on each of V1/V2/V5 (n = 40 each, **0/120**) with
`same_referent` 1.000 (M1:375-379, M1:651). Blind describer **0.4286**, left-only 0.4387 (n = 100), raw
context **0.4731**; gap AV − blind 0.4534 CI [0.4404, 0.4673] → K4 NOT MET (M1:14, M1:603-608;
`overnight/s4_summary.md:10`). Round 2 (09:03–09:25, NS/RUNLOG.md:21-31; NS/STATE.md:4 "ROUND 2
COMPLETE") reused the artifacts: R0 re-derived 0.8820 vs 0.8820 (NS/RUNLOG.md:22); **R1 MET** — the target's
own last-token representation of the claim text moves more under paraphrase (d_para_T 0.13357) than
under corruption (d_corr_T 0.03952), S_T = −0.09405 CI [−0.10376, −0.08445]; AR side d_corr 0.02167 vs
d_para 0.07113, S_AR = −0.04945 (NS/MORNING2.md:7; NS/r1_summary.md:12-14); **R2 MET** — corrupting every
accepted claim costs 0.00754 vs paraphrasing every claim 0.01407, paired diff −0.00653 CI [−0.00992,
−0.00260], corruption > paraphrase in 0.2125 of explanations (NS/MORNING2.md:8; NS/r2_summary.md:13-22);
**R3** — median first-k lift over the empty floor exceeds 0.9 at k = 3, last-k at k = 1 (last claim alone:
mean cos 0.8217, median lift 0.9253); Spearman(claim word count, cos_alone) = 0.7024, Spearman(relative
claim position, cos_alone) = 0.7638 (NS/r3_summary.md:12-20, 45-47).

## B. The advisor's decision tree, walked with our results

Tree (ADV:201-210):
- **A "Extraction, injection, and AR checks usable?" → Yes.** K0 cjk 1/16, parse_ok 1.000 (M1:7); K1a 0.8820 (M1:8);
  K1b same-doc 0.3664 (M1:9); injection asserts (marker id 149705, neighbours 29/522) kept in every stage (M1:640, P1:113-114).
- **C "Corruptions hurt more than paraphrases?" → No.** A − P = −0.00181 [−0.00279, −0.00080] (M1:11); R2 whole-explanation
  version −0.00653 [−0.00992, −0.00260] (NS/MORNING2.md:8). Advisor: go to E, not D.
- **E "Run six-pair AV prompting pilot" → run in a different form.** We ran S5 (P1:309-360), an instruction-following probe on
  40 pilot activations × 6 instruction variants, not the advisor's six matched activation pairs with donor tracking and
  text-only QA (ADV:130-147). Result 0/80 mechanical, 0/120 judged (M1:13, M1:375-379); cos_Vk − cos_V0 between −0.0035 and
  +0.0003 (M1:375-379). Their branch "Correct gain and donor tracking" cannot be reached when the output does not change
  with the instruction; this is "No reliable gain" by a stronger route than they specified.
- **G "Write a bounded reliability failure study"** — this is where the tree puts us. D ("held-out AR claim audit") and
  F ("controlled AV prompting") are both closed by our numbers; H (selective editing) was gated on D or F (ADV:209-210).

"Possible night-one outcome" table (ADV:214-223), row by row:

| advisor row | occurred? | our number | advisor's day-two action | done? |
|---|---|---|---|---|
| Correct ≈ shuffled | No | 0.8820 vs 0.3664 / 0.3198 (M1:8-9) | checkpoint/marker/AR-head checks | n/a |
| Correct beats shuffled but loses to in-domain mean | Untested | no in-domain mean direction was scored; nearest is cos_empty 0.3471 (M1:130), which is the AR's own prior, not a corpus mean | retain only within-pair claims | — |
| Whole deletion matters; single deletions do little | Yes | Δcos_all −0.5349 vs median Δcos_i −0.0160 (M1:219, M1:236); D = 0.00578 (M1:227); fraction Δcos > 0 = 0.076 (M1:244) | paired/group deletions + controlled corruptions | corruptions yes (S3); all-claims replacement yes (R2); joint *deletion* of pairs no |
| Corruptions hurt, paraphrases stable | No | P > A (M1:272-273) | expand proposal 1 | n/a |
| **Paraphrases hurt as much as corruptions** | **Yes (more)** | P 0.00494 > A 0.00313 (M1:272-273); R2 0.01407 > 0.00754 (NS/r2_summary.md:13-14); AUROC corrupt vs paraphrase 0.4665 (M1:291) | verify paraphrases manually; role swaps; formatting controls; withhold verifier claim | manual check pending (10 verbatim examples, M1:298-366); formatting: shuffle_order −0.0147 (M1:237), shuffle_words (M1:225); role swaps not run |
| True/false separate on average, overlap heavily | Untested | no human-labelled natural claims; synthetic AUROC 0.5257 corrupt vs original (M1:289) | precision–retention curve, abstention | — |
| Source-only ≥ AV on reconstruction | No | blind 0.4286, rawctx 0.4731 vs 0.8820; fraction blind ≥ AV 0.000 (M1:603-611) | budget matching; proposal-2 comparison | not needed for this row |
| AV beats source-only | Yes | gap 0.4534 [0.4404, 0.4673] (M1:608) | check independently measured facts/behaviour before calling it an interpretability advantage | not done |
| Source-only cannot finish | No | S4 finished (M1:68) | — | — |

Advisor-recommended controls **already run**: random equal-length span (M1:221-224), whole-explanation deletion (M1:236),
word shuffle within claim (M1:225), claim-order shuffle (M1:237), deterministic corruption (M1:275), same-doc and cross-doc
shuffle (M1:126-127), empty explanation (M1:130), blind describer incl. left-only (M1:603-605), raw context (M1:606),
adjacent layers (M1:128-129), off-topic swap (M1:286, AUROC 0.9553 M1:293), joined-claims baseline (M1:287-288).
**Not run**: in-domain mean direction baseline (ADV:64, 216, 231); human-labelled supported/contradicted claims
(ADV:104); joint deletion of claim pairs (ADV:118); held-out filtering with precision/retention (ADV:116); role-reversal
corruptions as a category (ADV:106; the editor prompt allowed polarity, e.g. M1:362-363, but no count by type exists);
text-only QA reader over the default description (ADV:140); activation swaps / donor tracking (ADV:143); system-message
variants (ADV:138); leading prompts (ADV:139); matched output budgets (ADV:145); uninjected-marker control (ADV:143;
`notes/round1_decisions.md:81` queues a random-vector control).

## C. Their three proposals vs what we have

| proposal | their hypothesis | our closest evidence | verdict on their hypothesis | still missing for their version |
|---|---|---|---|---|
| Rank 1 — AR claim auditing (ADV:98-122) | (a) corruption worsens reconstruction more than an equal paraphrase; (b) a deletion score improves held-out factual precision at useful retention | (a) A − P = −0.00181 [−0.00279, −0.00080], n = 490 (M1:274); det −0.00137 (M1:276); R1 S_AR −0.04945 (NS/r1_summary.md:14); R2 −0.00653 (NS/r2_summary.md:15). Note A_i ≡ cos(z) − cos(z*) by construction (M1:628), so our A − P *is* their "corruption margin" in cos units (ADV:112). (b) Δcos_i vs random span D = 0.00578 (M1:227) is their "deletion contribution" (ADV:114) with a length-matched control. | (a) **unsupported** on this checkpoint/corpus/edit type; (b) **untested** (no labels, no held-out threshold) | independent supported/contradicted labels blind to scores; dev/eval split by source family; threshold at 80 % retention; precision/retention on held-out; joint deletions |
| Rank 2 — AV prompting (ADV:124-151) | a neutral aspect instruction elicits correct omitted information, tracks donor swaps, beats default + text-only QA at matched budget | S5: instruction ignored 0/80 mechanical, 0/120 judged, same_referent 40/40 per variant (M1:375-379); V3 "one word" outputs 84–113 words (M1:383); V4 French fraction 0.072 (M1:381); cos unchanged to ±0.0035 | **unsupported** at the prerequisite step (no instruction effect to measure a gain from); their primary endpoint untested | matched pairs with one upstream attribute changed; donor swaps; uninjected marker; text-only QA reader; matched 128-token budget; system-message and leading arms |
| Rank 3 — selective causal editing (ADV:153-169) | AR(d*) − AR(d) edits change the intended target behaviour more than paraphrase/unrelated edits | none; the AR difference between corrupted and original text is 0.003 cos (M1:282), and the target's own representation of the claim text moves 3× more under paraphrase (NS/r1_summary.md:12) | **untested**; the advisor's own gate (strong Rank-1 or Rank-2 signal, ADV:169) is not met | working target-model hook, donor-patch gate, coefficient grid, two-attribute contexts |

## D. Where our results contradict, confirm, or go beyond the advisor

- **Contradicts their gate assumption.** The tree treats "corruptions hurt more than paraphrases" as the pivot (ADV:204). Our
  data land on the opposite side: paraphrase costs more than corruption at single-claim (M1:272-273), all-claims (NS/r2_summary.md:13-14)
  and single-sentence AR level (NS/r1_summary.md:14). Their listed interpretation for this row is "wording dependence or information
  accidentally lost in rewrites" (ADV:219).
- **Beyond them: locus.** R1 shows the same ordering *inside the target model*: last-token layer-20 representation of the claim text,
  d_para_T 0.13357 vs d_corr_T 0.03952 (ratio of means 0.296), and mean-pooled 0.00134 vs 0.00013 (NS/r1_summary.md:12-13);
  per-triple rho(S_T, S_AR) = −0.0098 (NS/r1_summary.md:28). The advisor did not propose this comparison. Their warning that
  "failure to elicit a fact does not show the fact is absent from the target activation" (ADV:69) is about AV read-out; R1 is
  the complementary question for the AR side — whether the *text encoder's* insensitivity is already present in the target's own
  encoding of the sentence. Numbers only; the human decides what a last-token cos on a sentence means.
- **Confirms their injection note; they did not predict total instruction-blindness.** "A changed instruction need not misplace
  injection" (ADV:90): confirmed — the marker asserts passed for every variant and parse_ok was 1.000 (M1:650, M1:374-379). But
  the AV then produced the same kind of output under every instruction: 0/200 followed across V1–V5 (M1:375-379), including
  "answer NOUN/VERB/OTHER first" (first words: 'Historical' 13, 'British' 3 … M1:382). The advisor's pilot design (ADV:132-147)
  assumes at least some instruction effect to measure; that assumption is not met for this checkpoint.
- **Confirms "deletion demonstration is a replication" (ADV:29).** S2 reproduces small per-claim effects with a length-matched
  control: D = 0.00578 (M1:227), fraction Δcos > 0 = 0.076, first-claim 0.150 vs last-claim 0.0125 (M1:244-247).
- **Confirms Hu & Greenblatt-style caution as they relay it (ADV:64).** Shuffle controls separate by ~0.5 cos while the factual
  distinction moves 0.003 — "generic shuffled pairs are insufficient for small distinctions" describes our numbers exactly.
- **Beyond them: coarse topic sensitivity exists.** Off-topic claim swap costs 0.11417 [0.10443, 0.12337] with AUROC 0.9553
  (M1:286, M1:293), vs 0.003 for a one-fact change — the AR distinguishes topic, not fact, at this resolution.
- **Beyond them: redundancy/position.** R3: last claim alone reaches median lift 0.9253; first claim alone 0.2251 (NS/r3_summary.md:12);
  Spearman(relative claim position, cos_alone) 0.7638 (NS/r3_summary.md:47). The advisor asked "which information is lost" under
  compression (ADV:68); we have the position curve but no content labelling of what the dropped claims contained.
- **Confirms their normalisation note.** mse = 2(1 − cos) is reported as identical information (P1:128; ADV:108).
- **Diverges from their AV-beats-source follow-up.** They ask for independently measured facts/behaviour before calling the
  0.45 gap an interpretability advantage (ADV:222); nothing of that kind has been run.

## E. Literature the advisor cites — all UNVERIFIED by us (no web search performed)

| item (as cited, ADV line) | why it matters to our result | status |
|---|---|---|
| Hu & Greenblatt, June 2026 (ADV:64) | claims NLA reconstruction loses to a dataset-mean direction; we have no in-domain mean baseline, only cos_empty 0.347 | UNVERIFIED |
| Zhang & Turner, July 2026 (ADV:65) | implausible-explanation NLAs reconstruct equally well; bears on reading our P > A as "meaning is not what the AR reads" | UNVERIFIED |
| Jakkli, Rajamanoharan & Nanda, March 2026 (ADV:66) | activation-swap / no-activation / text-inversion controls; the missing controls in our S5 | UNVERIFIED |
| Building Better Activation Oracles, 2026 (ADV:67) | AObench, question framing; frame for why S5 instruction-blindness is checkpoint-specific | UNVERIFIED |
| Shorter NLA explanations, June 2026 (ADV:68) | length-penalised training; our R3 truncation curve and Spearman(n_tokens, cos) −0.19 (M1:138) sit next to it | UNVERIFIED |
| When Activation Oracles Learn Not to Read, July 2026 (ADV:69) | "not verbalised ≠ not decodable"; the caveat for every S5/R1 sentence | UNVERIFIED |
| The Model Organism Lottery, July 2026 (ADV:70) | warns against toy-organism generalisation; relevant only if a day-2 organism is built | UNVERIFIED |
| Scaling Activation Oracles, Aug 2026 (ADV:71) | "avoid treating early negatives as universal"; the hedge our write-up needs | UNVERIFIED |
| Cycle-Consistent Activation Oracles (ADV:73) | independent verbalizer/reconstructor cycle; prior-art positioning | UNVERIFIED |
| HARP (ADV:73) | strong retrieval/probing baselines; the cheap-probe alternative the advisor floats at ADV:195 | UNVERIFIED |
| Tri-lens, R-Lens, "The First Token Is a Clue" (ADV:16) | J-Lens comparators from the un-pasted companion report; J-Lens is the advisor's fallback if both NLA branches fail | UNVERIFIED |
| NLA paper confabulation analysis, initialization study, LatentQA, AOs, Patchscopes, SelfIE, PCDs, Jacovi & Goldberg, SAEBench, Hewitt & Liang (ADV:29-59, 149) | the framing citations; `notes/mats_paper_index.md` may already cover some — not checked here | UNVERIFIED |

Not found in our notes: the companion J-Lens report `jlens_and_nla_research_strategy.md` (ADV:6 says it was not pasted).

## F. Open questions for the human (ordered by how much they change the write-up)

1. Read the 10 S3 verbatim triples (M1:298-366): are the corruptions real contradictions and the paraphrases meaning-preserving? If not, K3/R2 are about the editor, not the AR.
2. Is the write-up's finding "the AR does not separate one-fact corruption from paraphrase (A − P = −0.0018)" or "the target's layer-20 sentence encoding is itself rewording-dominated (R1)"? Which is the headline figure?
3. Should the in-domain mean-direction baseline (ADV:64, 216) be run before writing? It is one AR-free computation on cached activations.
4. Does the S5 0/200 result go in as a finding (checkpoint is not promptable at inference) or as a scoping note, and is the uninjected/random-vector control (round1_decisions.md:81) needed first?
5. Label natural claims by hand (blind to Δ) as queued in round1_decisions.md:77-78, or drop the verifier framing entirely given AUROC 0.4665?
6. Which of the advisor's UNVERIFIED citations must be read in full before being cited (time budget: ~16 h total human work)?
7. Merge `nightshift/round2` into main now, or after the human re-derives one round-2 number (e.g. mean S_AR from `r1_scores.csv`)?
8. Is a role-reversal corruption arm (ADV:106, 219) worth one more AR-only pass, given R2 already amplified to every claim?

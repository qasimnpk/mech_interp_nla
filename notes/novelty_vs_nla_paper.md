# Where we stand relative to the NLA paper, and what would add research value by Sept 11 (desk, 2026-09-07 05:30)

Sources: `notes/nla_paper_2026_text.txt` (full paper), the second half pasted by the human on 2026-09-07,
`notes/nla_paper_card.md`. New numbers below come from `notes/quote_census.csv` and `notes/snippet_faithfulness.csv`
(pure text over `overnight/explanations.jsonl` and the full prefixes; no model runs). Human verification owed.

## A. What the paper already did that touches our work (inventory)

| paper item | what they did | where we stand |
|---|---|---|
| AR as verifier (confabulation section) | Opus 4.6 NLA, natural claims judged true/false by Haiku 4.5; deleting true claims hurts MSE more than false; related-false hurt more than unrelated; "noisy, weak per-claim verifier" | Ours is the controlled version: same claim, one fact changed, paraphrase null. Truth-specific component < paraphrase (0.003 vs 0.005). Their relevance gradient reproduces (off-topic 0.114) |
| claim taxonomy | theme / entity / detail; thematic claims more often true; false claims usually related | Not yet recut by type on our data (cheap, N2 below) |
| recurrence across tokens ↔ truth | true claims recur at more positions | Untested here (needs multi-position runs; round-4 idea) |
| steganography transforms | shuffle, light/aggressive paraphrase, French → small FVE drops; coherence rewrite, summary → large drops | Replicated in miniature: paraphrase 0.005, reorder −0.026, truncation curve. Our addition: a one-fact edit drops less than a paraphrase, and the last bullet alone gives 88% of the lift |
| factual-accuracy rate | AVs make false context claims at a substantial, flat rate over training | On the released 7B: quoted spans ≥3 words, 4.2 per explanation; 1.8% occur verbatim in the prefix the activation saw; 17% share any 3-gram (eval n=671 spans). Quotes are reconstructions, not inversions |
| confabulation origin hypotheses (Discussion) | (1) SFT warm-start summaries written by Sonnet from context; (2) the objective rewards a thematically matched wrong specific over omitting it | (2) is directly testable with the AR alone on our 490 claims (N3). We have "wrong specific ≈ right specific"; we lack "no specific" |
| inference-time methods (future work) | best-of-N against the AR; per-claim ablation "experimented with"; per-bullet AR | Per-claim ablation with controls is our S2/R3/C1. Best-of-N untested (N6). Note: the released open NLAs were trained with GRPO, G=8 samples scored by the AR, so best-of-N is the training signal |
| AOs from AV (QA SFT) | phrasing sensitivity ±10%; AOs hallucinate around the question cue; "unprompted outputs carry more evidential weight than prompted" | Our inference-only analogue: instruction text changes nothing (S5); yes/no format useless (0.55) but candidate continuation works (0.75 raw, 0.94 corrected); phrasing held up on one held-out prefix |
| layer choice | NLAs at two-thirds depth; layer sensitivity shown on the reward-model organism; multi-layer NLA as future work | The released 7B pair is block 20 of 28 (hidden_states[21], 0.75 by completed blocks). Layer dependence of fact-vs-phrasing displacement in the target is testable in 5 min (N4) |
| open-model release (appendix) | Qwen2.5-7B, Gemma-3-12B/27B, Llama-3.3-70B; SFT summaries from Sonnet 4.6, "2–3 bullets", ordered "by what is most important for predicting the next tokens"; GRPO; 150-token cap | The NLA paper reports no confabulation, steganography or verifier analysis of the open NLAs, but **Dingeto (arXiv 2607.20379, Jul/Aug 2026) already audits this exact pair** (≈2% of specific claims grounded; paraphrase keeps 0.89 of the score). See `notes/response_to_reframing_2026-09-07.md`. Ours is a replication with a paired design plus the decomposition and readout results |

Not ours to touch by Sept 11: anything needing training (per-bullet AR, RL penalties, multi-layer NLA), across-checkpoint
claims (we have final AV/AR only), eval awareness or auditing (no transcripts), SAE consistency.

## B. The human's five thoughts, answered

**1. "The paper already used the score to discriminate claims. How do we make peace?"**
Their test is observational: natural claims, truth judged after the fact, so truth is confounded with specificity,
relevance, recurrence and wording (their own table: false claims are mostly specific details, recur less, and are
"usually related"). Ours is interventional and paired: same claim, same position, one fact changed, with a
paraphrase as the wording null. Both are right. The paired test says the truth-specific part of their "weak
verifier" signal is smaller than the wording noise, and the part that survives is relevance (off-topic swap 0.114,
AUROC 0.955). Write-up sentence: "The paper reports that removing true claims hurts reconstruction more than removing
false ones, and that related false claims matter more than unrelated ones. Holding the claim fixed and changing one
fact, we find the effect of the factual change is smaller than the effect of rewording; the relevance gradient
reproduces, the truth gradient does not."

**2. "Editing AV outputs doesn't show the AV is incentivized to be inaccurate."**
Correct: the text-edit tests measure the AR's sensitivity, not the AV's incentives. Two things do speak to incentive.
(a) The released NLAs were trained by GRPO with the AR as the reward, so whatever the AR rewards is what the AV was
pushed toward; our decomposition says the reward is dominated by the final-token bullet, so context claims are cheap
to get wrong. (b) The paper's own hypothesis 2 ("guessing 490 reconstructs better than omitting a number") is a
statement about the AR and can be tested with the AR alone: compare a wrong specific against no specific (N3). We
have half of it already: wrong specific ≈ right specific. Separately, 1.8% verbatim quotes says the objective did not
push this AV toward input inversion at this layer (their Discussion worries about that failure mode).

**3. "How do their true/false, related/unrelated and claim-type results square with ours; look beyond their types?"**
Related/unrelated squares directly (relevance gradient). True/false squares as in (1). Claim type: we can recut our
490 corruptions by the type of the changed word (theme word / named entity / number-date-quote) with no model runs
(N2) and predict, from their relevance finding, theme > entity > detail in corruption cost. Beyond their types: the
verbalizability question (emotion, syntax, "meta" concepts) is T4's territory; a matched-dose map across concept
classes is a small real contribution (N7) but is evaluation-heavy and third in priority.

**4. "Does syntax drive the score more than semantics, and is that the layer?"**
First correct the premise. Paraphrase does not hurt "a lot": 0.005 on a 0.88 score with a 0.35 floor, and the paper's
own steganography test found the same small drop for paraphrase and French. The accurate statement: the score is
dominated by one bullet (the final token and its expected continuation), and among the context claims, small text
changes produce small changes whether or not meaning changed. The activation side says the same thing: an upstream
entity swap moves the block-20 vector by 1−cos 0.034, a one-word rephrase by 0.024. Whether that is specific to
two-thirds depth is a 5-minute target-only test (N4: the same displacement ratio across all 28 layers). The
"form is maintained at all depths" story predicts a flat ratio; the "semantics emerge late" story predicts the fact
displacement growing with depth. Either result is a figure.

**5. "How are we building on the paper?"**
Six concrete ways, all on the released checkpoint the paper itself shipped:
(i) the controlled, paired version of their AR-verifier test, with a paraphrase null and CIs;
(ii) a decomposition of the reconstruction score by bullet, with a position control: the final-token bullet carries
88% of the lift and keeps 79% of it when moved;
(iii) the source-edit side (C2/C3): the score detects a changed representation without preferring fact over phrasing;
(iv) an inference-only test of the "ask the AV a question" idea they pursue by training AOs: prompts fail,
prefilled likelihoods work for topic, weakly for entities;
(v) mechanical faithfulness numbers no one has published for this checkpoint: quotes 1.8% verbatim; the quoted final
token correct in 82% of explanations; the "expecting" candidates name the target's true top-1 next token in 44% of
explanations (no text-only baseline yet, N5);
(vi) the direct test of their confabulation hypothesis 2 (N3) and of their proposed best-of-N method (N6), if run.

## C. Candidate additions, ranked by value per hour, with what each would take

| id | question | cost | novelty vs paper | pre-registrable kill |
|---|---|---|---|---|
| N1 (done, verify) | what in these explanations is mechanically verifiable: quote verbatim rate, final-token accuracy, expecting-vs-top-1 | 0 (human 20 min to verify 10 rows) | new numbers for a released NLA; ties to their factual-accuracy and inversion discussion | none; descriptive |
| N2 | corruption cost by type of changed word (theme / entity / detail) | agent 30 min, no runs | squares our result with their taxonomy | descriptive; predict theme > entity > detail |
| N3 | wrong specific vs omitted specific (their confabulation hypothesis 2) | AR only, ≈15 min; deterministic "generalize" edit on the 402 det rows: number → "a number", name → "a place/person" | tests a hypothesis stated in their Discussion | CI of [cost(omit) − cost(wrong)] ≤ 0 → MET (no evidence the objective prefers a wrong specific over none) |
| N4 | fact-vs-phrasing displacement across all 28 layers (C2/C3 contexts; optionally R1 claim texts) | target only, ≈5–10 min | answers the layer question; figure | descriptive; report the layer where fact/phrasing ratio peaks |
| N5 | text-only baseline for N1's 44%: base model given the prefix, asked for three likely next tokens | target only, ≈5 min | makes N1 citable (AV vs text guesser) | CI of [AV hit − text hit] ≤ 0 → MET |
| N6 | best-of-8 by AR: does AR selection reduce verifiable confabulation (quote rate, final-token accuracy) or only sharpen the snippet? Also gives the T=0.7 noise floor S5 lacks | AV 320 gens ≈ 55 min + AR | tests their proposed inference-time method; GRPO makes it the training signal | CI of [verifiable-accuracy(AR-best) − (random sample)] ≤ 0 → MET |
| N7 | verbalizability map: emotion / syntax / meta directions at matched rotation angle (T4 extension) | ≈55 min AV | their "characterize what NLAs cannot verbalize" future direction | mention rate < 0.25 at the sports-matched dose → MET per class |

Recommendation under the current human plan (write-up first, no experiment as a dependency): put N1 and N2 into
the write-up now (they are analysis of existing outputs, which the plan allows); pre-register N3 + N4 + N5 as one
30-minute bench run for the first evening the rough draft exists, since together they answer thoughts 2, 4 and 5
and each has a one-line kill; N6 only if a night is free; N7 and the 27B stay as named extensions.

## D. Paragraph for the write-up ("relation to the NLA paper"), to rewrite in your voice
The NLA paper characterises confabulation on Claude models and reports that its reconstructor is a weak per-claim
verifier: removing true claims hurts more than removing false ones, and related false claims matter more than
unrelated ones. We ran the controlled version of that test on the released Qwen2.5-7B checkpoint. Holding a claim
fixed and changing one fact costs less than rewording it; swapping in an off-topic claim costs thirty times more.
The relevance gradient reproduces; a truth gradient does not appear. Decomposing the score shows why: one bullet, the
final token and its expected continuation, carries most of the reconstruction, and that bullet is the part of the
explanation that is verifiably about the model's state (its quoted token is right 82% of the time and its predicted
continuation names the model's actual top-1 in 44% of cases), while the context claims are reconstructions whose
quoted spans almost never occur in the text. The paper proposes asking the verbalizer questions by training oracles;
we find that on this checkpoint prompts change nothing but prefilled likelihoods read the topic out reliably and an
upstream entity only weakly. None of this bears on the paper's audit findings, which concern much larger models;
it bears on what the reconstruction score can and cannot be used for.

## E. Framing decision, 2026-09-08 ~15:00 EDT (desk, answering the human's question)

**Question asked:** "Should our experiment design look at the experiments designed and run in the NLA paper, reference them
and build upon them, or is our current approach to be preferred? Which is the stronger contribution / MATS application?"

**Answer: false choice.** The current design already is the paper's confabulation-section experiment, run with controls on
the checkpoint the paper released, plus direct tests of things the paper hypothesised or listed as future work. The stronger
application is the existing one, written so the lineage is visible in the first paragraph. Do not pivot.

**Why this is the stronger application (each point traceable):**
1. Neel's FAQ names this exact experiment. `notes/neel_drive/mats12_admissions_procedure_faq.md` L719–721, verbatim:
   "[Natural language autoencoders] try to autoencode activations as natural language and back … What can you do with them?
   Do they actually work for tasks of interest? · Key resource: This Qwen 3.6 27B NLA from my scholar Celeste … · I'm
   particularly interested in using the activation reconstructor to measure the quality of a description, e.g. figuring out
   which claims can be removed and improve reconstruction accuracy to help reduce hallucinations, as briefly explored
   [NLA paper, characterizing-nla-confabulations]." That is S2, S3, R2, R3, C1 and X3.
2. It is a well-analysed negative on a named positive idea. FAQ L431–436: "Negative or inconclusive results that are
   well-analysed are much better than a poorly supported positive result"; L491: "Building on a phenomenon without first
   checking it replicates in your setting … If the effect isn't there for your setup, everything downstream is noise."
   Past-example verdicts praise "built well on existing work" (L524).
3. Every finding maps onto a paper item (inventory in §A above). Compact map for the write-up:

| paper item | our test | what we add |
|---|---|---|
| claim deletion → "weak per-claim verifier" (observational: natural claims, Haiku judge, truth confounded with specificity/relevance/recurrence) | S2 deletion vs length-matched span; S3 paired same-claim corruption vs paraphrase; R2 every-claim; off-topic swap | interventional and paired; the relevance gradient reproduces, the tested one-fact edits do not register; both penalties small |
| steganography transforms (shuffle, paraphrase, French → small FVE drop; coherence rewrite, summary → large) | one-claim paraphrase cost, reorder (C1), truncation curve (R3) | reproduced in miniature; the final-token bullet carries 88% of the lift and keeps 79% when moved |
| confabulation hypothesis 2 (objective rewards a wrong specific over omission) | N3 wrong / generic / omitted on the frozen AR | wrong ≈ generic, omission costs far more; a property of the frozen scorer, INCONCLUSIVE on the kill |
| "ask the AV" via trained activation oracles | inference-only prefilled likelihood (T2/T2a/T2c) with un-finetuned-model control (U1), donor swaps, held-out prefix | learned, activation-dependent readout: topic reliably, entities weakly; text-only 0.988 bounds the claim |
| late-layer NLA applied to earlier layers "less coherent" | X1 / X1b across blocks 16/20/24/27 | readout transfers (entities best at 24); fluency and verified readout come apart in both directions |
| future work: per-claim ablation, best-of-N | ablation = S2/R3/C1; best-of-N not run (N6) | name best-of-N and recurrence as future work, not as tested |

**What not to do:** reproduce the paper's five prediction tasks or the full steganography suite. They are informativeness-
over-training results on Claude models with ground truth by construction; impossible with final checkpoints only, and a
budget sink the FAQ flags ("spreading yourself too thin").

**Two weaknesses to state plainly, one sentence each, in the main text:** finding 2 overlaps Dingeto 2026 on the same
released pair (cite first; ours is a different instrument); Celeste's Qwen3.6-27B is Neel's named key resource and does not
fit this machine (48 GB; `notes/nla_setup/README.md`), so the study is on the paper's own released 7B pair — the 27B
replication is the named next step (`notes/27b_extension_brief.md`).

**Write-up consequences (now in `human-plan.md` §1 opening, §3 rows/checkboxes, §6 lineage line, §9):** open with the paper's
weak-verifier sentence → Neel's question → the answer; cite the paper and Dingeto before our numbers on finding 2; use their
theme/entity/detail taxonomy as a descriptive appendix recut; say once that their metric is FVE/MSE and ours cosine on the
direction-only scorer (MSE = 2(1 − cos) for unit vectors).

## F. Pending: setup-comparability audit against the paper (spec for the human's paper-setups agent)

The human has a separate agent extracting the exact experimental setups from the NLA paper so we can check whether ours are
comparable. Useful, with these rules so the output is directly usable and does not cost review time:

- **Scope:** the confabulations section (claim extraction, truth judging, claim deletion, related/unrelated split, recurrence
  across positions), the steganography/transform section (each transform, how FVE change was computed), the AO/QA section
  (how questions were posed, prompt sensitivity), the open-model appendix (Qwen2.5-7B: layer, SFT data source and format,
  "2–3 bullets", ordering rule, GRPO group size, token cap, injection scalar α, KL coefficient), and the AV/AR prompts. Also
  **Dingeto 2026 §3.1 + App. E** (`notes/dingeto_2026_train_the_model_text.txt`) — that is the *number*-comparable setup,
  since it uses the same released pair; the NLA paper's confabulation numbers are on Claude NLAs and are only
  *design*-comparable.
- **Format:** one row per experiment with columns: paper item · location (section/appendix anchor and, if possible, a line
  number in `notes/nla_paper_2026_text.txt`) · target model and layer · stimuli/data and n · intervention or edit · metric
  (FVE / MSE / judge accuracy) · judge or labeler · verbatim quote supporting each cell. Cells the paper does not state are
  marked "not stated", never filled in from memory. The interactive figures were lost in the text dump; anything that lived
  only in a figure is "figure-only, unrecoverable".
- **Known non-equivalences to expect** (state, do not paper over): FVE vs cosine (MSE = 2(1 − cos) only for unit vectors;
  the released scorer is direction-only); natural true/false claims judged post hoc vs our paired same-claim edits; deletion
  of a claim vs substitution within a claim; Haiku 4.5 judge vs our LLM editor + deterministic swaps; Claude Opus NLA
  (4–5 snippets) vs the released 7B (2–3 bullets); their per-token FVE on Claude vs our 200 wikitext-2 positions.
- **What the desk does with it:** joins each row to our `overnight/PLAN.md` stage and `overnight/<stage>_settings.json`
  (prompt ids, injection norm 150, marker position, scorer) into `notes/setup_comparability.md` with a final column
  same / differs how; every "differs" that could change a conclusion becomes one stated sentence in the methods paragraph.
  Human review of the joined table ≤ 20 min (counted time).

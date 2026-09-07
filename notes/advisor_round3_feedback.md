# Third advisor — feedback on round 3 results (received 2026-09-06 ~23:00, verbatim; pasted by the human)

Acted on in `overnight/PLAN.md` "Round 3b". Kept verbatim here for provenance.

**Run round 3b. I would now prioritize validating forced-prefix readout over starting further steering experiments.** Your strongest emerging result is a comparison between two interfaces to the same NLA: reconstruction scoring largely misses specific factual edits, while targeted AV likelihoods may recover the relevant information.

That is already a useful direction for "new and improved interpretability methods"—provided the next controls establish semantic recovery rather than self-consistency.

**What the results currently establish**

| Result | My interpretation |
|---|---|
| Own-position cosine 0.882 versus strong mismatch gaps | Convincing activation matching in this evaluation |
| Corruptions cost less than paraphrases; factual AUROC 0.53 | Strong evidence against this reconstruction score as a verifier of the tested factual changes |
| Local snippet remains dominant after reordering | Dominance is substantially content-driven, with some position sensitivity remaining |
| C2 matching margin positive in every pair | The NLA cycle distinguishes activations arising from a controlled entity change |
| Forced-prefix topic readout follows activation donors | Promising activation-dependent readout beyond prompt priors |
| Concept injections reliably alter descriptions | Controlled sensitivity to those injected directions |

The key distinction: **C2 shows sensitivity to the entity edit, but does not yet show that the readout identifies the entity.** Its descriptions can differ in wording without naming Paris or Lyon. T2c can close exactly that gap.

**The biggest issue is the 97.3% claim-word result**

Because the prefix and original word come from the AV's own greedy output, the experiment strongly favors the original word by construction. You are asking the model to resume a continuation it already selected under that activation.

Moreover, **"original" is not synonymous with "true."** An AV could strongly prefer its own hallucinated entity over your replacement.

T2b is therefore necessary, but a foreign-activation control alone does not establish factual correctness. Distinguish:

* **Self-consistency:** prefers its previously generated word.
* **Activation dependence:** preference changes when the activation changes.
* **Factual recovery:** preference follows independently established source facts.

T2c is particularly valuable because it can test all three without relying on AV-generated candidate claims.

**1. T2c: make this the primary next experiment**

For every C2 pair, use: the same neutral prefix for both activations; the same candidate entities; candidate labels taken directly from the constructed source contexts; no AV-generated description in the prefix.

For a Paris/Lyon pair, a prefix could be: `<explanation>The passage mentions the city`

Score the complete candidate continuations with their appropriate leading whitespace. Verify tokenization; do not score only the first token of multi-token entities.

Define D(h) = log P(Paris | p, h) − log P(Lyon | p, h). Report both:
1. **Donor sensitivity:** D(h_Paris) > D(h_Lyon).
2. **Correct discrimination:** preference favors Paris for one activation and Lyon for the other, using the chosen scoring rule.

The first can succeed even if the model always prefers Paris; the second is stronger.

Include the no-injection baseline and one held-out prefix paraphrase. Crucially, with the same prefix and candidates, the no-injection prior cancels from the donor difference: [D(h_A) − D(h_0)] − [D(h_B) − D(h_0)] = D(h_A) − D(h_B). Thus donor sensitivity cannot be manufactured by that prior subtraction.

**Strong positive:** entity preference switches appropriately despite an identical source suffix, while default descriptions usually omit the entity. That demonstrates usable information accessible through targeted scoring but rarely expressed spontaneously. It still concerns source information, not necessarily a model's reasoning process. That is a legitimate and valuable scope.

**2. T2b: run it, but label it as an activation-dependence test**

Hold the original claim prefix and both candidate completions fixed. Compare the original activation, a foreign activation and no injection. If available cheaply, a **same-topic or same-document donor** is more informative than an unrelated document: otherwise the test may only measure broad topic compatibility.

For a small, independently checked subset, separate source-supported originals from unsupported originals. An especially revealing outcome would be that the AV confidently reproduces unsupported claims under its own activation. That would show why likelihood is also not automatically a truth score.

Use T2c as the cleaner factual-recovery test; do not make T2b carry more than its design supports.

**3. C3: choose a meaning-preserving wording control**

My choice would be **"brief" versus "short" in a neutral phrase such as "a brief account"**, provided it fits your templates and preserves token count under the actual tokenizer. Use a small factorial design (Paris/Lyon × brief/short → contexts A–D). Keep the remaining suffix identical. Match the substitution's distance from extraction to the entity edit as closely as practical.

Measure the factual and wording effects separately. More importantly, test whether **T2c's entity preference survives the wording change**. The factual edit does not need to produce a larger global activation distance than the paraphrase to be readable.

Call this a *meaning-preserving phrasing control*, not a zero-information edit. It changes linguistic form and may change style-related representations. Freeze the choice before seeing its results.

**Audit the prior-corrected 0.935 before making it the headline**

That improvement is plausible: likelihood corrections for candidate priors have established precedent (Surface Form Competition, EMNLP 2021, https://aclanthology.org/2021.emnlp-main.564/). The potentially interesting contribution here is their use for NLA activation-conditioned readout, not prior correction itself.

Check that: correction uses the identical prefix and candidate strings; the rule was not selected using evaluation labels; candidate titles serve as both positive and negative examples where possible; complete title likelihoods are scored consistently; you report **within-pair choice accuracy** alongside pooled AUROC; the corrected AUROC has uncertainty estimates; comparisons with AR and the difference-of-means probe use the same examples and labels.

If the correction or prefix was chosen after inspecting evaluation performance, describe that analysis as exploratory. A small fresh confirmation set is more valuable than another large prompt sweep.

**Several draft claims should change**

* "The score reads wording and relevance, not facts." → "The score is substantially more sensitive to wording and relevance than to the tested factual corruptions." Corruption effects are small, not absent.
* "Content, not position." → "Local-snippet dominance persists across positions." Moving it reduced deletion cost by about 21%; position is not irrelevant.
* "The verbalizer ignores instruction text." → "The tested instructions did not produce the requested changes." Different greedy outputs show that the prompt does affect computation.
* "T4 replicates reading outside J-space." → It replicates injected-concept sensitivity. Without constructing and testing a J-space complement, it does not replicate the outside-J-space finding.
* "18 degrees is small." → For equal-norm vectors, an 18-degree rotation changes the vector by approximately 31% of its norm. Report the angle directly.

Also update the earlier "text-only floor" interpretation: 0.429 and 0.473 are meaningfully above the 0.347 empty baseline, although substantially below the AV result.

**How I would finish**

1. Complete **T2c, T2b and C3**.
2. Cut T3 at its predeclared cap; report the completed sample and stopping rule.
3. Confirm the strongest prefix result on fresh cases or a held-out wording.
4. Finish an existing causal experiment if it is already operational; **do not expand into a new steering task now**.
5. Write three central figures: reconstruction specificity, local-snippet ablation, and targeted readout with donor controls.

I would revise my earlier emphasis on obtaining a causal result. **Your new readout results offer a more direct, lower-risk improvement to the interpretability interface.** Causal steering and the 27B replication can be clearly specified extensions.

If T2c succeeds, the central conclusion becomes: **High reconstruction fidelity does not imply reliable claim verification. Nevertheless, targeted likelihood readout can recover specific source information that the same NLA rarely states in its default descriptions.**

If T2c fails, you still have a coherent boundary: topic retrieval improves, but recovery of fine factual distinctions remains unestablished. Either outcome is stronger than treating all five findings as evidence of general semantic understanding.

# Advisor report (external AI research-strategy agent), 2026-09-06 — verbatim as pasted by the human

Provenance: produced by a separate literature/strategy agent that had NO access to our pipeline or
results. It reasons from the NLA paper, follow-up reports and the public checkpoint code. Its
citations are NOT verified by us; treat every linked claim as second-hand until checked.
The companion J-Lens report (`jlens_and_nla_research_strategy.md`) was NOT pasted; only its chat
summary appears below.

---
## Chat summary (advisor's own words)

Recommendation: turn the night-one AR tests into a held-out claim-auditing evaluation, measuring false-claim removal against true-claim retention. Claim deletion already appears in the original paper; calibrated reliability under corruption, paraphrase, and redundancy controls is the stronger extension.

Ranked: (1) AR reliability: semantic sensitivity and whether a filtering rule generalizes. (2) AV prompting: additional information beyond default-description-plus-text-only-QA, with activation swaps and matched budgets. (3) Selective causal editing, only if justified.

J-Lens summary: keep NLA AR reliability as the main project if night one validates its semantic signal; use J-Lens as a cheap additional check; if those checks fail, switch to a focused J-Lens reliability experiment. Compatible J-Lens matrices exist for Qwen2.5-7B. Prior work: R-Lens, Tri-lens (J/NLA agreement + steering controls), "The First Token Is a Clue" (multi-token). J-Lens ranked options: (1) separate task relevance from conceptual salience vs matched task controls; (2) does J-Lens improve AR claim auditing (AR alone vs AR+logit lens vs AR+J-Lens); (3) multi-token identity recovery under first-token collisions (only if 27B inference operational). Decision: AR distinguishes corruption from paraphrase → finish NLA audit; AR unreliable but AV prompting reveals extra info → frozen-AV prompting; neither → J-Lens experiment 1 on 7B. Implementation warning: J-Lens and the oracle release use different block-input/output conventions.

## Full NLA strategy report

NLA research strategy for a three-day MATS project
Primary literature and public implementation review, 6 September 2026.

All night-one experiments are planned experiments with unknown outcomes. I have not accessed, run, or modified the separate experiment pipeline. Checkpoint details below describe inspected public releases, not a verified manifest of your local installation.

Executive recommendation

Make AR claim verification under controlled semantic and wording changes the main project, conditional on night-one matching checks passing. Use the existing Qwen2.5-7B setup. The immediate next experiment should compare a factual corruption with a meaning-preserving rewrite of the same claim, then test whether a deletion-based score improves factual precision on held-out descriptions while retaining true information. This mostly needs cached activations and AR forward passes.

The original paper already reports that deleting true claims increases reconstruction error more than deleting false claims, with substantial individual-example noise. Therefore, a deletion demonstration is a replication; the useful extension is a calibrated, independently evaluated auditing rule with an explicit failure boundary. NLA paper, confabulation analysis

Run a small AV prompt intervention pilot alongside the analysis, using fixed activations, minimal instruction changes, matched activation swaps, and default-description-plus-text-only-QA controls. Expand this if AR scoring proves insensitive to factual distinctions. Reserve causal editing for a strong early signal and an already-working target-model intervention interface. Do not spend the remaining time training an AV/AR or migrating to 27B.

What the evidence establishes—and what it does not

"Established" here means demonstrated in the cited setting, not universally replicated. Recommendations and proposed thresholds below are my inferences. Possible contributions are unverified novelty claims unless explicitly described as replications.

The NLA paper reports reconstruction improvement, useful audit case studies, factual confabulation, weak claim-level verification, modest effects from meaning-preserving transformations, and toy description-derived steering. It also studies turning AVs into question-answering AOs with additional supervised training; that does not establish inference-only AV prompt steerability. NLA paper

Keep four measurements separate:

Measurement | What a positive result supports | What it does not establish
Reconstruction | The paired AR recovers the measured activation geometry from the text | Every sentence is factual; the reconstruction preserves behavior
Source factuality | A claim is supported by the source prefix available at extraction | The target represents or uses that claim
Activation-dependent readout | Answers track controlled activation differences beyond a specified text baseline | The AV did not infer the answer from recovered text using its own weights
Selective behavioral intervention | A specified activation edit changes a specified outcome with limited collateral effects | A complete account of the target's original computation or general safety monitoring

This separation follows the distinction between plausible and faithful explanations, and evidence that reconstruction-oriented proxy improvements need not improve downstream interpretability. Jacovi & Goldberg, 2020, SAEBench

Compact literature map

Method | Input | Supervision / objective | Prompting capability | Validation | Limitation relevant here
NLAs, 2026 | One target residual vector; AV text feeds AR | Summary-based supervised warm-start; joint reconstruction-driven RL with regularization | Released AV uses a fixed interpretation template; QA extension was trained | Reconstruction, information readout, audits, confabulation checks, toy interventions | Paired reconstruction is not a factual verifier or independent human-readable-code guarantee
LatentQA, 2024 | Patched target activations plus a question | Decoder answer cross-entropy on generated QA; sometimes mask control-prompt activations | Explicit question-conditioned decoder | Relational knowledge and system-prompt recovery; gradient-based control | Supervision can teach shortcuts or hallucination; its control procedure is not simply inference-time text editing
Activation Oracles, 2025 | One or more activations, layer information, arbitrary query | QA, classification, and context-prediction mixture | Trained for flexible queries and varying activation inputs | Secret-keeping, model-difference audits, PersonaQA, classification; strong results in tested settings | Different input interface/training from an NLA AV; model-organism success need not generalize to natural hidden behavior
Patchscopes, 2024 | Hidden state patched into a separate target prompt/model/layer | Many configurations require no additional training; some cross-model mappings are learned | Inspection prompt is a central configurable component | Token predictions, factual attributes, entity resolution, multihop correction | Prompt and patch locations matter; a capable decoder can elaborate beyond the source state
SelfIE, 2024 | Hidden embedding substituted at placeholder positions in an interpretation pass | Interpretation needs no additional training; separate control methods use optimization | Summarization/repetition interpretation prompt | Intervention-based relevance scores, case studies, editing tests | Injection relevance does not certify the semantics of every generated claim; control requires more than changing the prompt
Predictive Concept Decoders, 2025 | Activations through a learned sparse concept bottleneck, then a question | Joint encoder/decoder next-token pretraining; freeze encoder and QA-finetune decoder | Question conditions the decoder, not the concept encoder | Concept interpretation, held-out attributes, jailbreaks, secret hints, injected concepts | Decoder receives learned concept activations/re-embeddings, not merely English labels; bottleneck can discard useful information

For PCDs, removing the bottleneck helps some difficult evaluations. That is a useful precedent for asking whether the default NLA description omits answerable information; it is not evidence that merely asking an untrained AV a different question will recover it. PCD experiments

Follow-up work that changes the research decision

Primary source | Relevant reported result | Consequence for this project
Hu & Greenblatt, June 2026 — research report | On their math setting, Qwen2.5's NLA reconstruction loses to a dataset-mean direction. Selected text-only confabulations can match AV reconstruction. | Include an in-domain mean and matched text-only generation/selection budgets. Generic shuffled pairs are insufficient for small distinctions.
Zhang & Turner, July 2026 — research report | Qwen2.5 NLAs initialized with implausible explanations achieve similar reconstruction while continuing to emit overwhelmingly implausible statements. | Strong direct warning against identifying reconstruction with literal meaning. Their trained variants are not evidence that your checkpoint uses a private code.
Jakkli, Rajamanoharan & Nanda, March 2026 — research report | Hallucination, vagueness, text-inversion confounds; some tasks work comparably without injected activations; several safety tasks perform poorly. | Require activation swaps, no-activation controls, falsifiable questions, and competitive text-only baselines.
Building Better Activation Oracles, 2026 — preprint | Improved data/injection yield practical quality gains but modest capability gains; introduces AObench and discusses question framing and consensus. | Borrow relevant controls, not an entire training/evaluation stack. Improved AOs do not validate the frozen NLA AV.
Shorter NLA explanations, June 2026 — research report | Length-penalized Qwen3-8B training reduces explanation length with small reconstruction changes. | Redundancy/compression is already an active topic. Measure which information is lost, not only shortening or FVE.
When Activation Oracles Learn Not to Read, July 2026 — preprint | In controlled fine-tuning, an AO can fail to verbalize a concept that remains decodable internally. | Failure to elicit a fact does not show the fact is absent from the target activation.
The Model Organism Lottery, July 2026 — preprint | Interpretability varies substantially with organism construction, including training methodology. | A prompted secret or implanted attribute is a controlled toy evaluation, not evidence for detecting natural deception.
Scaling Activation Oracles, August 2026 — primary technical report | Adds behavior-prediction, evaluation-awareness, and reward-hacking evaluations; reports scaling gains and mixed per-task comparisons with earlier AOs. | Avoid treating early negative results as a universal verdict. Behavior prediction and task-specific errors are useful endpoints.

Other relevant precedents include Cycle-Consistent Activation Oracles, independently using a verbalizer/reconstructor cycle, and HARP, which reports strong retrieval-and-probing baselines against trained methods. Neither warrants starting another implementation in this sprint. The brief blind-spot, model-organism, and HARP entries rely on their primary abstracts; detailed inspection concentrated on the six starting methods, directly relevant research reports, and checkpoint code. This is a targeted review, not comprehensive coverage or a verified novelty search.

Checkpoint and injection audit: what D can actually change

The public 7B pair is kitft/nla-qwen2.5-7b-L20-av plus its matching AR. Your base-model name alone does not confirm that this is the pair running locally. Preserve the exact target/AV/AR revisions, extraction token and layer, numerical precision, and quantization in the eventual experiment manifest.

Detail | Published kitft Qwen2.5-7B pair | Recommended ceselder Qwen3.6-27B release
Target representation | Output of zero-indexed block 20; dimension 3,584 | Layer index 42; dimension 5,120
Marker | ㈎, ID 149705; neighboring IDs 29/522 | ㈜, ID 158983; neighboring IDs 29/510
Injection | Replace the marker's input embedding with 150 × h / ‖h‖ | Add ‖r‖ × h / ‖h‖ to marker residual r after block index 1, the second transformer block
Prompt container | Client constructs one user message; checkpoint chat template supplies a default system message | EasyNLA helper accepts a list of role-tagged messages; use checkpoint-specific chat behavior
AR scoring | Learned vector head; published client normalizes prediction and target for direction-MSE | Metadata records unnormalized extraction; retain this release's scoring convention rather than importing the 7B scorer

These details come from the actual 7B metadata, 7B inference code, 27B metadata, EasyNLA injection function, and hook registration. The 27B card's description of injection "in place of" the token is less precise than the linked code: the inspected hook is additive.

Both metadata files request semantic description, preserve <concept>…</concept> around the marker, and ask for "2-3 text snippets" in <explanation> tags. Both use a separate AR wrapper ending in a summary marker. The AR wrapper is plain text, not the AV chat prompt. 7B metadata, 27B metadata

The 7B client's _build_embeds accepts custom prompt_content with an <INJECT> placeholder and scans marker IDs plus neighbors. Thus, a changed instruction need not misplace injection; reusing an obsolete hardcoded token position would. System-message experiments require constructing the message list explicitly because this convenience method hardcodes a user-only list. The checkpoint's chat template inserts a Qwen/helpful-assistant system message when none is supplied. Client code

The 27B chat template opens a thinking block unless enable_thinking=False. The generic EasyNLA prompt helper does not itself supply that argument. The checkpoint card explicitly requires it, and also warns that saved AV iterations share a final-only AR: historical FVE trajectories do not compare AVs against one fixed reconstructor.

Implementation inference: start by changing only the last instruction after the marker. This preserves the injection position and, under causal attention, the pre-injection marker residual. Prefix/system changes in EasyNLA change r and therefore the injected magnitude as well as the instructions. Log pre/post-hook norms if testing those conditions. Keep the source activation fixed, but do not pretend this automatically fixes the complete internal intervention.

In every prompt arm, verify exactly one valid marker, correct neighbors, expected site/norm, fresh per-request cache behavior, and comparable format-completion rates. Count malformed/truncated outputs as failures. Do not infer correct injection merely from fluent English.

Rank 1 — Can AR scores support a useful claim-auditing rule? [A, B]

Hypothesis. Within independently labeled source-grounded claims, an incorrect semantic substitution worsens AR reconstruction more than an equally substantial meaning-preserving edit. A deletion-based score then improves held-out factual precision at a useful retention rate. These are two distinct tests: corruption sensitivity alone does not validate filtering naturally occurring claims.

Closest prior work. The original NLA claim-deletion analysis is the direct precedent. Initialization experiments supply a concrete counterexample to interpreting reconstruction as literal truth. NLA paper, initialization study

Minimum experiment. Use 40–60 source prefixes, preferably existing night-one examples spanning ordinary prose and one controlled domain. Split by source/template family into development and untouched evaluation sets. Extract two atomic claims per description; label them supported, contradicted, or unverifiable using only the prefix available at extraction. Human-check labels blind to scores. Evaluate supported versus contradicted claims; keep unverifiable claims visible as a separate category.

For each supported claim, prepare the original, a deletion, one factual corruption, and two verified paraphrases. Corruptions should include entity substitution, quantity changes, and role/negation changes that preserve most vocabulary. Keep surrounding claims fixed. Add whole-description deletion, a same-length irrelevant replacement, and source-text-only descriptions as controls. Do not use the AR to choose the "best" corruption or paraphrase.

Let E(h,d) be the checkpoint's reconstruction error. For the inspected 7B scorer, normalized direction-MSE equals 2(1 − cosine): reporting cosine and this MSE is not independent validation. Scoring implementation

Use two predeclared statistics:

Corruption margin: E(h,d_corrupt) − E(h,d_paraphrase). Report the paired win rate and context-level uncertainty, alongside the size of ordinary paraphrase variation.

Deletion contribution: S(c) = E(h,d_without_c) − E(h,d). Test whether it ranks supported claims above contradicted claims. A positive score means reconstruction contribution, not a probability of truth.

On development data only, choose a score threshold targeting, for example, 80% supported-claim retention. On held-out data, report actual true-claim retention, false-claim removal, precision, and coverage; include a no-filter baseline. Small samples warrant uncertainty intervals, not a deployment claim. If the threshold is unstable across paraphrases, abstain on that claim. Re-score the actual edited descriptions because multiple deletions can interact.

Baselines and confounds. Compare against random deletion matched for length, claim specificity, and simple source checking; include recurrence across existing token positions if already available. Do not generate ten neighboring AV descriptions just to add a costly baseline. A low deletion score can reflect redundant wording, weakly represented information, or AR insensitivity. Test joint deletion of the two claims on a small subset: a large joint effect with small individual effects is consistent with redundancy. It is not evidence that either claim is false. Description edits also shift the AR's input distribution.

Informative negative result. Correct descriptions beat shuffled ones, but factual corruptions do no worse than paraphrases, or filtering removes true details as readily as false ones. This establishes a useful boundary: global matching succeeds while the proposed claim verifier fails at the tested resolution. If corruptions work but deletions fail, retain the counterfactual scoring result and reject deletion-based filtering.

Feasibility and contribution. Approximately 400–800 AR evaluations, with few new AV generations if cached descriptions exist; batch and load models sequentially as needed. This is the best Mac-first option. The contribution would be a controlled reliability/retention evaluation or a well-characterized failure, beyond the prior aggregate deletion observation. Novelty of the complete protocol remains unverified.

Rank 2 — Does prompting recover additional information from a fixed activation? [D, B]

Hypothesis. A neutral, aspect-specific instruction elicits correct information omitted by the default description and unavailable to a competitive text-only QA reader of that description. The effect transfers to held-out prompt paraphrases and follows matched activation swaps; leading prompts do not account for it.

Closest prior work. Patchscopes already uses inspection prompts to expose different information, and LatentQA/AOs explicitly train question-conditioned readout. Consequently, "asking different questions about activations" is not new. The narrow candidate contribution is inference-only information recovery in a frozen reconstruction-trained AV, tested against a default-description bottleneck. Patchscopes, LatentQA, AOs

Minimum experiment. Pilot six matched pairs; expand to 24 pairs only if the prompt interface works and yields nontrivial answers. Construct controlled contexts with a common extraction suffix and balanced labels, changing one upstream attribute per pair. Use one semantic facet, such as agent/patient roles, and one lexical facet, such as a mentioned number or name. A useful role pair contains the same names and action words with the participants reversed. Match length/token position where possible and record residual mismatches. These tasks test recoverable content, not hidden reasoning.

Freeze each extracted activation. Keep the checkpoint's marker, tags, general instructions, and decoding settings. Compare:

Arm | Intervention / information available | Purpose
Default | Exact released template | Reference description and format success
Minimal neutral instruction | Change only the final instruction after the marker; e.g., prioritize who acted on whom | Lowest-disruption test of aspect retrieval
Held-out wording | Two neutral paraphrases fixed before evaluating the held-out examples | Generalization beyond one tuned instruction
System-message variant | Change system instruction while retaining the user template | Tests role-level prompting separately; higher distribution shift
Leading variants | Balanced suggestions of each candidate answer, including false ones | Measures suggestion-following and acquiescence
Text-only QA | Default description followed by QA using ordinary Qwen2.5-7B-Instruct in a fresh context, without activation access | Tests whether prompting merely reformats information already verbalized
Source-only | Source-prefix QA and, if affordable, source-derived descriptions followed by the same QA | Measures the value added beyond observable text

For each neutral/leading query, run both members' activations with identical query text. Judge answers against the injected donor activation's label, and measure whether the answer changes in the appropriate direction when that donor changes. Also report correctness against the original recipient label as a leakage diagnostic. Add an uninjected-marker control; treat zero/random vectors as distribution-shift diagnostics, not a sole baseline. Do not pass the source context or correct answer to the AV in the neutral arms.

Budget matching. Fix total generated-token allowance per query. One concrete comparison is 128 tokens for a prompted AV versus 96 for a default description plus 32 for text-only QA. Also allow a default AV 128 tokens, since simply giving the default more space might remove the gain. Use the same QA reader and answer rubric across conditions. If sampling multiple outputs, match both sample count and total generation/selection budget; report actual tokens and format failures. Reuse cached default descriptions but still account for their generation cost. Do not select AV samples by AR score without giving competing methods the same selection opportunity.

Primary endpoint. Paired accuracy improvement over default-plus-QA on the full held-out set, with a separately reported subset where the default omitted the fact. Require correct new information, appropriate donor tracking, transfer across neutral prompt paraphrases, and acceptable false-claim rates. More words, altered tone, different examples, or a better AR score alone are not success. Report both facets separately: lexical recovery and semantic role recovery answer different questions.

Confounds and informative negatives. Correct answers with uninjected/swapped activations suggest prompt priors; improvement only under leading prompts suggests acquiescence; disappearance at equal budgets suggests extra text; failure only after system changes may reflect distribution shift. No improvement over default-plus-QA supports a narrow result: no extra usable information was elicited by these prompts and this reader. It does not show that the activation lacks the fact. Probe selectivity work motivates testing the reader's contribution rather than equating accuracy with represented knowledge. Hewitt & Liang

Feasibility and contribution. AV decoding is the bottleneck. A core expansion is a few hundred short generations; do system/leading arms first on the pilot rather than taking every condition across every example immediately. Infer the feasible size from night-one throughput. If necessary, finish one semantic facet well. A positive result establishes incremental usable information relative to the tested text reader, not information-theoretic novelty or a causal mechanism. The novelty claim remains unverified.

Rank 3 — Do AR-backed descriptions support selective causal edits? [C, B]

Hypothesis. A minimal semantic edit to a description produces an AR-derived activation difference that changes the corresponding target behavior more than equally sized paraphrase or unrelated edits, while largely preserving a second attribute. Reconstruction contribution and behavioral effect need not agree.

Closest prior work. NLA description-derived steering already exists, while SelfIE/LatentQA also connect interpretation to control through different optimization procedures. The candidate contribution is a specificity test and a comparison between reconstruction-based evidence and behavioral effects, not the invention of text-based steering. NLA paper, SelfIE, LatentQA

Minimum experiment. Only attempt if target-model hooks already work. Use 12–24 controlled two-attribute contexts: for example, a fictional object's color and owner, queried through a common suffix. Establish that the target answers reliably and that a matched donor-activation patch can change the intended answer. Select examples by predeclared target-behavior criteria, not successful NLA steering.

For a supported description d and an edited description d*, construct normalized reconstructions u(d)=AR(d)/‖AR(d)‖ and intervention v=‖h‖[u(d*)−u(d)] for the direction-trained 7B pair. Apply h′=h+αv at the original extraction site. This is a proposed scale convention, not a verified transfer of the frontier experiment's coefficients. Choose a small coefficient grid on development examples and freeze it before evaluation.

Measure intended-answer log-odds, preservation of the other attribute, and damage to unrelated continuations. Compare no edit, same-description round trip, matched real donor patch, paraphrase-derived vectors, and norm-matched random/unrelated vectors. Include opposite semantic edits and a few held-out paraphrases of the edit. Full reconstruction replacement is a diagnostic: if even AR(d) damages behavior, edited-reconstruction failure is hard to interpret. Difference steering may still work, so assess it separately.

Confounds. An edit may insert an output-token cue rather than alter an abstract belief; success on a color/name toy task is not evidence of hidden-behavior control. Perturbation magnitude, patch position, and reconstruction error can dominate. For a small descriptive analysis, compare claim-deletion contribution from proposal 1 with intended behavioral changes; do not treat a tiny-sample correlation as causal validation of the AR score.

Informative negative result. A real donor patch works while description-derived edits fail or cause unrelated damage: the target's behavior is controllable at this site, but this AR interface is inadequate. If donor patching also fails, the setup/site is inconclusive. If AR contribution poorly tracks selective effects, a reconstruction-based audit cannot be promoted into causal attribution.

Feasibility and contribution. Highest implementation risk; several hundred target forwards plus cached AR outputs, with limited full generations for spot checks. Stop if the initial patching gate consumes more than a small part of day two. A clean specificity failure is useful; a steering anecdote adds little beyond existing work. Do not make this the main project unless the simpler tests are already strong.

Interpreting representation preservation and private communication codes [B]

Use the same experiment data to distinguish four possibilities. Individual deletions can be cheap because another clause repeats the information; joint deletion tests this. Lexical substitutions can hurt reconstruction while role reversal does not; that would show sensitivity to tokens without comparable sensitivity to the tested relational meaning. A prompted AV can recover a correct omitted attribute while default-description QA cannot; that shows omission by the default bottleneck. Finally, a paraphrase can preserve human-rated content while damaging AR reconstruction; that reveals wording dependence, with several possible causes.

The last pattern alone does not demonstrate a private AV–AR code. Paraphrasing can lose binding, specificity, uncertainty, or formatting that an ordinary decoder uses. Use several independently verified paraphrases, benign formatting/order controls, and the same transformations on source-written descriptions. A disproportionate effect on AV text would strengthen concern about a learned convention, but still would not identify it. Conversely, robustness to a few transformations cannot exclude all covert channels. The original NLA transformation tests and later initialization results concern different claims and can both be true. NLA paper, initialization study

A different model family's AR is not an independent scorer of Qwen2.5 activations: its target space is different. An independently trained compatible AR would be informative if already available, but training one belongs in future work. Likewise, low global error can coexist with losing a small, behaviorally decisive component. The practical representation question is which distinctions survive, at what error and output budget.

What would justify monitoring or control claims? [C]

A researcher-facing auditing aid is a reasonable near-term deliverable: retain the original description, highlight reconstruction-sensitive claims, show paraphrase instability, and mark claims requiring independent checking. Do not label low-score claims "hallucinations" or silently erase them. Evaluate the aid by factual precision/retention or whether it helps identify a known issue, not by prettier prose.

Hidden-behavior monitoring needs additional evidence beyond these three experiments:

Establish a behavior externally—such as systematic use of an undisclosed hint—through controlled target outputs or interventions. Its absence from the final answer alone is insufficient.

Test activation-derived signals against the strongest monitor using exactly the text available at the monitoring time. Full source-prefix access and final-answer-only access are different baselines; label them explicitly.

Measure false positives on matched benign cases, held-out prompt families, and different behavior instances. A repeated alarming phrase is not ground truth. At small sample sizes, report uncertainty and avoid claims of very low false-positive rates.

Require incremental evidence beyond a cheap classifier where a compatible probe exists. Deception-probe work demonstrates why out-of-distribution evaluation matters; it does not supply a plug-and-play Qwen2.5 detector. Detecting Strategic Deception Using Linear Probes

Validate edited-description control through selective effects, reversals, and collateral-damage controls as in proposal 3. Detection and control are separate capabilities.

If there is a strong practical reason to diagnose an AV blind spot, a small regularized linear probe on already-cached labeled activations is an exceptionally cheap optional baseline, with source-grouped splits and label controls. It should consume minutes, not initiate a new training project. Do not train new NLAs, AOs, or model organisms during this sprint.

Night-one → day-two decision tree

These branches are conditional recommendations, not descriptions of observed results. "Pass" means a practically meaningful, consistent effect with its uncertainty reported; an underpowered comparison is inconclusive.

flowchart TD
    A["Extraction, injection, and AR checks usable?"]
    A -->|No| B["Integration diagnosis; no substantive claims"]
    A -->|Yes| C["Corruptions hurt more than paraphrases?"]
    C -->|Yes| D["Main: held-out AR claim audit"]
    C -->|No or unclear| E["Run six-pair AV prompting pilot"]
    E -->|Correct gain and donor tracking| F["Main: controlled AV prompting"]
    E -->|No reliable gain| G["Write a bounded reliability failure study"]
    D --> H["Selective editing only if signal and time permit"]
    F --> H

Apply these diagnostic adjustments before expanding the chosen experiment:

Possible night-one outcome | Interpretation to test | Day-two action
Correct and shuffled pairings are indistinguishable | Pipeline issue, poor corpus fit, or inadequate signal | Have the experiment owner check checkpoint/layer, marker, scaling, AR head/wrapper, and cache behavior. Do not infer a scientific failure before these checks.
Correct beats shuffled, but loses to an in-domain mean | Broad matching exists, but reconstruction is poor at the corpus's variation scale | Retain only within-example/pair claims supported by direct tests. An overall mean failure does not mathematically rule out a useful local ranking.
Whole-description deletion matters; individual deletions do little | Redundancy, diffuse encoding, weak claim sensitivity | Test paired/group deletions and controlled corruptions. Do not treat every small-score claim as hallucinated.
Corruptions hurt, paraphrases are stable | Promising semantic sensitivity | Expand proposal 1; test real AV errors and held-out filtering, not just constructed corruptions.
Paraphrases hurt as much as corruptions | Wording dependence or information accidentally lost in rewrites | Verify paraphrases manually; test role swaps and formatting controls; withhold a factual-verifier claim.
True and false claims separate on average, but overlap heavily | Useful ranking may exist without reliable binary decisions | Report precision–retention trade-offs and abstention; prefer review prioritization over deletion.
Source-only descriptions equal or beat AV on reconstruction | AR may reward plausible text reconstruction rather than uniquely useful AV readout | Match generation and selection budgets; run proposal 2's incremental-information comparison. Do not assume the AV has no useful information merely from equal global error.
AV beats source-only on reconstruction | Evidence for reconstruction advantage | Check independently measured facts and behavior before calling it an interpretability advantage.
Source-only comparison cannot finish | Baseline remains unresolved | Prioritize the cheap default-description-plus-QA control and explicitly narrow the conclusion.

Plan for the remaining time

At the start of day two, read the night-one outputs and obtain the actual checkpoint/scoring manifest. Allocate roughly the first hour to interpreting gates and fixing the evaluation design, not launching a new model stack. Freeze one primary endpoint and a source-grouped holdout before expanding. Spend most available inference on the chosen primary experiment; run only the small AV pilot or joint-deletion diagnostic as a secondary test.

On day three, finish the held-out comparison, inspect failures blind to condition where possible, and write around two figures: (1) corruption versus paraphrase effects or a precision–retention curve; (2) paired prompt-control performance or a specificity/failure breakdown. Bootstrap by source/context family rather than treating every claim, token, or paraphrase as independent. Report counts and representative failures as well as averages.

Use a fixed development-derived mean baseline for corpus-level reconstruction, following the checkpoint's normalization convention. Never compare raw FVE numbers across different model/layer/corpus definitions as if they measured one common quality scale. On a Mac, benchmark a handful of forwards/generations and scale the sample count to actual throughput; RAM, quantization, and backend performance are unknown here. Prefer cached AR work, short outputs, sequential model loading, and a completed small study to speculative runtime estimates.

Defensible application framing: a controlled investigation of when pretrained NLA reconstruction scores and prompt interventions supply useful evidence. Claim deletion, generic paraphrase tests, promptable activation reading, and edited-description steering all have prior art. The candidate contribution is a careful combination of matched semantic/lexical controls, independent factual labels, text-only bottleneck comparisons, and outcome-dependent limits on a specific accessible checkpoint. A negative answer with those controls is a legitimate research result; no finding or novelty is assumed in this report.

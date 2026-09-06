# NLA seed — what the previous project already knew about natural language autoencoders

Extracted 2026-09-06 from the tool-conflict project (`mech_interp`: `notes/lit_tool_conflict.md`
and `three-bets.html`, Fallback C). These are the only NLA-relevant passages that project produced.
Verification status is carried over as written there: the audit card is **second-hand**. Re-verify
every number against the primary source before it goes in a brief.

## Definition (from the old brief's glossary)
A natural language autoencoder (NLA) is a pair of models: a **verbalizer** that reads one activation
vector and writes an English description of it, and a **reconstructor** that reads that description
back into a vector. Trained only to make the round-trip vector match; readable prose is an emergent
side effect. A way to "ask an activation what it contains."

## Paper card: NLA "Misreported Tool Calls" — Fraser-Taliente, Kantamneni, Ong, Mossing et al.; Transformer Circuits, 7 May 2026
**Second-hand** — every direct fetch truncated before this section; below is from the search index
quoting the page plus one third-party write-up. Opus 4.6 got an arithmetic problem with answer 491
and a code-execution tool rigged to return 492; it reported 491 with no mention of the disagreement.
The attribution graph shows an "ends in 92" feature on the tool output outcompeted by an "ends in 91"
feature from a pre-tool-call answer the model computed while reading the question — no layer indices
visible. NLA verbalisations surface deception/incorrectness references **only at the misreported-answer
token, not the tokens before it**, read as registering the discrepancy rather than planning deception.
Sampled with a redacted system prompt framing tool outputs as hidden from the user for security
reasons while instructing the model to report results accurately, so the silence is not obviously
strategic concealment.

The same audit reportedly found cases where the model believed it was being tested but did not say so.
The audit is closed-weights, attribution-graph, n = 1 for the tool-call anecdote.

Open verification items carried over: the 491/492 and "ends in 91"/"ends in 92" details, the
redacted-system-prompt wording, and the paper's own confabulation section were never read at the
primary source.

## Released checkpoint pointer
The old brief states that **Qwen2.5-7B-Instruct has a released natural-language autoencoder at
layer 20**, and that the verbalizer and reconstructor are themselves 7B-class models. Consequence
for the 48 GB box: target + verbalizer + reconstructor do not all fit comfortably; budget for it.
The originals were trained with sixteen H100s and days of RL — **use published weights, never train.**
(Repo ids were not recorded; find and record them in `CLAUDE.md` → Code.)

## Design seed: "NLA information gain" (old Fallback C, never run)
**Question.** When a model writes an English description of another model's internal state, how much
of that description required looking inside at all, versus what you would have written from reading
the prompt?

**Worry.** The verbalizer sees an activation that encodes its surrounding context, so a large share of
what it writes might be a paraphrase of the prompt — guessable without ever looking inside. If so, a
good reconstruction score is not evidence that the explanation tells you anything specific about the
internals.

**Design.**
- Path 1 (the method): activation at layer 20 → verbalizer → description → reconstructor → score.
- Path 2 (blind baseline): prompt text only → a plain model asked to write the same kind of
  description → the *same* released reconstructor → score.
- The result is the gap: real explanation minus blind baseline. Not real minus a floor that
  reconstructs nothing — beating the floor is trivial.
- Second control: take the explanation for a *different position* in the same prompt. If the
  reconstructor cannot tell the difference, the explanations are about the prompt as a whole, not a
  specific moment — and audits always make claims about specific moments.
- Methodological heart: the blind baseline must be as strong as possible before comparing. A weak
  baseline manufactures a big gap. Tune the baseline to beat our own hypothesis, and say so.

**Outcomes, either way.** Small gap: explanations are largely context paraphrase; reconstruction
quality is not evidence of activation-specific content, which qualifies the flagship audit result.
Large gap: we have supplied the quantitative control the method lacks. Either way, a reusable control
protocol any future NLA paper should run.

**Lighter variant (old primary's optional add-on).** Run the verbalizer at end-of-question,
end-of-result and first-answer positions of a tool-conflict prompt: does the description name the
pre-tool answer before the tool result appears, and does that mention predict a causal (patching)
outcome better than the transcript does? Two-sided: the description tracks a causal fact we
measured, or it restates the prompt and invents a number.

**Scoop risk noted in the old brief.** CHIVE, RECAP and the autoencoder paper's own confabulation
section are already a wave of "this metric is weaker than it looks"; a fourth entry in the same wave
is not a strong opening move. Position against them explicitly, or find the angle they do not cover.

## What the old project measured that an NLA study could reuse
Qwen2.5-7B-Instruct, 1–2 digit arithmetic with a rigged calculator tool (50 minimal pairs, 200
cells): follows the wrong tool 13/100; unaided accuracy 100%; own-answer token never in the top-10
of the logit lens at end-of-question at any layer; tool-span patch recovers ≈1.0 of the answer
margin through layer 15 (depth 0.57) and 0.43 at layer 18 (depth 0.68). Harness, stimuli and CSVs
live in the old repo under `overnight/` on branch `nightshift/bench-gate` (merged into `main` there).
Useful only if the NLA project wants a behaviour with a causal label already computed on the same
model at the same layer band.

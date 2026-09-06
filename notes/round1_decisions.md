# Round 1 — decision log (2026-09-06)

Record of the planning discussion between the human (director / reviewer) and the desk agent
that produced `overnight/PLAN.md` at commit `b01221e`. This is the provenance trail the write-up
needs: what the human decided, what the agent drafted, what an outside reviewer changed.
**Agent-drafted; the human's decisions are marked ▶.** Rewrite in your own voice before any of
this goes into the application.

## Starting point
- Neel's suggested direction: do NLAs work for useful tasks; in particular use the activation
  reconstructor (AR) to assess descriptions — does removing claims improve reconstruction and
  reduce hallucination. Suggested checkpoint: Celeste's Qwen3.6-27B NLA.
- Human's own candidate ideas: prompt-steerable AV; aspect-specific reconstruction objective;
  explanation-length trade-off.
- Prior-project seed (`nla_seed.md`): the blind-describer "information gain" control.

## Decisions
1. ▶ **Checkpoint: kitft Qwen2.5-7B-Instruct layer-20 pair, not the 27B.** Forced by hardware:
   the 27B verbalizer is 54 GB bf16 and the AR 35 GB; the box has 48 GB and no bitsandbytes on
   MPS. A separate agent verified the 7B round trip end-to-end (`notes/nla_setup/README.md`,
   `scripts/nla7b_roundtrip.py`): cos 0.87–0.91 on the released example, ~10 s per explanation.
   The write-up must say the choice was hardware-forced, and that only the 7B pair's *final* AV/AR
   are available (no across-training comparison).
2. ▶ **Primary question for round 1: is per-claim reconstruction delta a usable "claim usefulness
   score", and does it respond to factual corruption more than to superficial edits?** Chosen
   because it is Neel's stated interest and can be answered with one checkpoint, no training.
3. ▶ **Steering stage kept (S5)** despite the reviewer suggesting to drop it — the human wants
   at least one inference-time promptability probe with recorded examples. Constrained to the
   pilot set; agent-rubric judging is labelled as such.
4. ▶ **Blind-describer baseline made optional and last (S4)**, per reviewer; interpretation
   narrowed to "reconstruction is achievable from visible context", not "AV ignores activations".
5. Explanation-length trade-off gets no stage; Spearman(n_tokens, cos) falls out of S1.
6. Deferred to round 2 (listed at the end of PLAN.md): chat-style stimuli, LLM/human claim
   labelling with annotators blinded to AR scores, sampling temperature, random-vector control
   for steering, anything on the 27B.

## Reviewer feedback that changed the plan (all adopted)
- "Lie detector" framing replaced by "claim usefulness score"; truth-sensitivity is the hypothesis,
  not an assumption.
- S2 kill test changed from an absolute magnitude threshold to a comparison against equal-length
  random-span deletion; whole-explanation deletion added as positive control.
- S3 "planted foreign claim" replaced by contradictory-fact edits with matched wording + a
  meaning-preserving paraphrase as the null; primary statistic is the paired
  Δ(remove corrupted) − Δ(remove original). Foreign-claim swap kept only as a weak third arm.
- Operational rules added: fixed pilot (0–39) / evaluation (40–199) split; cluster bootstrap by
  source explanation; three-way outcomes (MET / NOT MET / INCONCLUSIVE); per-stage settings
  file; raw outputs always saved; hard stop 7 h or 07:30; `FOLLOWUPS.md` queue instead of
  autonomous pivots.
- Reviewer's caution carried into the write-up: success on synthetic corruptions justifies
  testing natural hallucinations, it does not validate a detector; a strong text-only baseline
  is a finding whose weight depends on gap, controls and prior work (CHIVE, RECAP, the NLA
  paper's own confabulation section).

## What the human must verify by hand in the morning (Neel: "sanity-check your agent")
- Re-derive one headline number with a fresh one-liner from the CSVs (e.g. mean cos on the
  evaluation set; mean A − P in S3).
- Read the S3 verbatim examples: did the editor actually produce contradictions? Read the S5
  examples: do the steered outputs obey, and are they still about the same activation?
- Read 5 raw explanations against their context windows.
- Check `DISCONFIRMATION.md` outcomes against the thresholds table in PLAN.md yourself.
- Log what you checked in `notes/human_log.md`.

## Loop launch
Worktree `../mech_interp_nla-nightshift`, branch `nightshift/round1`, merge commit `99f8f95`,
launched 2026-09-06 late evening with the `/loop` prompt recorded in `notes/human_log.md`.

## Round 2 candidates (queued 2026-09-06 03:05, while round 1 ran; triage after MORNING1)
Observations from S1 that motivate them: empty-explanation cos 0.35 ≈ both shuffle controls
(0.32–0.37), so the AR has a strong prior direction and every score should be reported as lift
over that floor; Spearman(n_tokens, cos) = −0.19 (p = 0.016), longer explanations do slightly
worse; block 20 beats 19 and 21 by ~0.05, layer confirmed.
- **Truncation sweep (AR-only, cheap):** score the first k claims for k = 1..n; where does the
  curve saturate? Directly answers the length idea without new generation.
- **Report lift over floor:** `(cos_own − cos_empty) / (1 − cos_empty)` alongside raw cos.
- **Short-instruction variant of S5:** if V3 (one word) keeps most of the lift, ask the AV for
  "one claim only" and compare to the full explanation's best single claim from S2.
- **Natural-hallucination labelling (day 2, human):** if S3 is NOT MET, label claims in the 5+10
  verbatim examples against context, blinded to Δ, then check whether Δ separates the labels.
- **Chat-style stimuli:** one WildChat-like slice (needs a download decision) to check the
  wikitext numbers transfer to the training distribution's other half.
- **Random-vector control for steering:** same six prompts with a random unit vector at norm 150.

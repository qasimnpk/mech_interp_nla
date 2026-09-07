# State of knowledge after rounds 1–3b (agent draft, 2026-09-07 01:00; for the human to share with an advisor)

Numbers trace to `overnight/*_summary.md` and `DISCONFIRMATION.md` (rounds 1–3 in main; round 3b in
`../mech_interp_nla-nightshift/overnight/`, branch `nightshift/round3b`, unmerged). Setup as in
`notes/summary_rounds1-3.md`. Wording follows the advisor's corrections (`notes/advisor_round3_feedback.md`).

## What we know, precisely

**1. Reconstruction is faithful and position-specific.** cos 0.882 [0.875, 0.889] own; 0.366 same
document other position; 0.320 other document; 0.347 empty explanation; 0.429 blind describer, 0.473 raw
context (both well above the empty floor, well below the AV). Adjacent layers 0.835.

**2. Reconstruction is more sensitive to the tested explanation paraphrases and off-topic substitutions
than to factual corrupt­ions.** (Rewritten 2026-09-07 after advisor review; the earlier heading conflated two tests.)
- Text side (activation fixed, description edited): changing a fact in an explanation reduced reconstruction cosine
  less than a meaning-preserving paraphrase did: 0.0031 vs 0.0049, paired difference −0.0018 [−0.0028, −0.0008],
  n=490. Every-claim corruption 0.0075 vs paraphrase 0.0141. Off-topic substitutions cost 0.114 (AUROC 0.955);
  one-fact corruption AUROC 0.53.
- Source-edit side (C2/C3: the passage is edited, so activation and description are both regenerated; the task is
  matching descriptions to their own activation, not verifying a claim): reconstruction matching is sensitive to
  both factual and meaning-preserving source edits. Matched entity edits gave a larger mean margin than wording
  edits (0.0175 vs 0.0097, C3 estimates) but the paired difference is inconclusive (0.0078 [−0.0035, 0.0241]).
  This establishes sensitivity to both edit types, not preferential sensitivity to factual content.
- Descriptive, post hoc (`notes/diagnostics_round3b.md`): across the 160 C3 margins the matching margin tracks
  activation distance (Spearman 0.77); in the 16 cells where the phrasing edit moved the activation more than the
  entity edit, the phrasing margin is larger (0.014 vs 0.005), and the reverse holds in the other 24. Consistent
  with "margin scales with activation displacement whatever caused it"; not a test of that mechanism.
- The useful distinction: detecting a changed representation (supported) vs checking whether a particular claim
  accurately describes it (not supported for the tested corruptions).

**3. Local-snippet dominance persists across positions.** Last claim alone recovers 88% of the lift;
deletion cost 0.125 vs 0.010 (first claim). Moved to the front it keeps 79% of its cost (0.099 vs 0.125);
reversed order 0.132. Corrupting the snippet costs 0.0048 vs paraphrasing it 0.0055.

**4. The verbalizer's output is hard to redirect by text or by its own residual stream, easy by the
vector.** Tested instructions produced none of the requested changes (0/200; outputs differ like a
sampling seed). Residual-stream steering toward French inside the AV (T3, 35/40 pilot): the only dose that
kept the explanation format gave 5.7% French; every higher dose broke the format (parse_ok 0) → MET.
Mixing a target-model concept direction into the injected vector (T4): sports words in 100% of
descriptions at an 18° rotation (≈31% of the norm), baseline 12.5%, random direction 17.5%.

**5. Forced-prefix likelihood readout recovers coarse source information reliably and fine upstream
facts weakly but selectively.**
| readout | statistic | value |
|---|---|---|
| topic, round-3 prefix | raw AUROC / prior-corrected / pair accuracy | 0.752 / 0.935 / 0.775 |
| topic, held-out prefix (T2a) | raw AUROC [CI] | 0.761 [0.713, 0.806] |
| | prior-corrected AUROC [CI] (exploratory rule, replicated) | 0.943 [0.921, 0.964] |
| | pair accuracy raw / prior-corrected | 0.781 / 0.944 |
| | no injection / foreign swap prefers foreign | 0.486 / 0.786 |
| entity on C2 twins (T2c, p1) | donor sensitivity D(h_a) − D(h_b), nats [CI by template] | 1.74 [0.63, 3.28]; 77.5% of pairs > 0 |
| | both-correct rate raw / prior-centred | 0.225 / 0.150 |
| | choice accuracy over 80 activations raw / centred | 0.600 [0.525, 0.688] / 0.562 [0.487, 0.650] |
| | paired AUROC | 0.65 [0.57, 0.75] |
| | held-out prefix p2 donor sensitivity | 1.83 [0.76, 3.00] |
| entity under phrasing change (C3) | donor sensitivity at w2; entity / wording main effects | 1.77 [0.72, 3.22]; +1.76 / −0.02 (interaction −0.02) |
| claim word, AV's own prefix (T2b) | d = lp(orig) − lp(corrupt): own / same-doc donor / foreign / none | 13.0 / 5.6 / 2.9 / 2.7 |
| | own − same-doc donor [CI] | 7.35 [6.56, 8.14] |
| | fraction preferring original: own / same-doc / foreign / none | 0.973 / 0.792 / 0.645 / 0.712 |
| | original word visible in left context: 192/691; d_own when visible / not | 18.2 / 11.0 |

Readings:
- Topic: strong, activation-dependent, replicated on a held-out wording. The prior-corrected number is
  legitimate but was chosen after seeing round-3 data; the held-out replication is what makes it citable.
- Entity: the likelihood shifts in the correct direction when the activation is swapped, in most pairs, and
  the shift is caused by the entity alone (a same-sized phrasing change has zero main effect). But the shift
  (≈1.7 nats) is smaller than the prefix's own bias in most pairs (D(h_0) > 0 in 62.5%), so absolute
  identification is near chance. The readout says "which of two activations has more Paris in it", not
  "this activation contains Paris". Heterogeneous by template: "The story is set in {city}" 7.4 nats, 75%
  both-correct; capital city 1.2; instruments, animals, weekdays ≈ 0 (n=4 per template, descriptive only).
- Claim word: mostly self-consistency. A foreign activation is no better than no activation (2.9 vs 2.7
  nats) and the AV still prefers its own word in 65% of rows. About 7 of the 13 nats are specific to the
  exact position, 3 to the document. 499/691 "original" words are not in the visible left context and the
  AV prefers them by 11 nats under its own activation; whether those are inferences or confabulations needs
  the 30-row human labelling sheet (`t2b_support_sheet.csv`, still unlabelled).

## The one-paragraph story (draft)
On the released Qwen2.5-7B layer-20 NLA, reconstruction fidelity is high and position-specific, but the
reconstruction score is a poor claim verifier: it is more sensitive to wording and relevance than to the
tested factual corruptions, on the text side and on the activation side, and most of it comes from the
local "final token … expecting …" snippet. The same activation, read by forced-prefix likelihood in the
verbalizer instead of by reconstruction, yields the document's topic reliably (pair accuracy 0.78 raw,
0.94 prior-corrected, replicated on a held-out prefix) and an upstream entity weakly: the likelihood moves
the right way when the activation changes and is unmoved by a phrasing change, but the shift is too small
to identify the entity outright. The verbalizer does not follow instructions or residual steering at doses
that keep it fluent, yet reliably reports concept directions mixed into the vector. Net: high fidelity
does not imply verification; the interface, not the information, is the limit for coarse facts; for fine
facts the information is present but marginal at this position.

## What I would do next (for the advisor to rank)
Cheap, sharpening, before writing (each ≤ 15 min compute; all on cached activations):
1. **T2d, calibrated entity readout.** Replace the no-injection prior with the mean D under the other
   activations of the same template (7 other contexts). This is the standard contrast for likelihood
   readouts and removes the per-template prefix bias that swamps the 1.7-nat shift. 640 AV forwards.
   Kill: calibrated choice accuracy CI includes 0.5 → MET.
2. **T2e, locality curve for the entity.** Read the same pairs at the token right after the entity
   (the period), at +4, and at the final token. If accuracy falls with distance, the weakness is a
   position choice, not an interface limit, and the write-up can say where the fact is readable.
   80 TARGET forwards per position, 480 AV forwards per position.
3. **Human: label `t2b_support_sheet.csv`** (30 rows, ~20 min). Split d_own by supported / unsupported.
   If unsupported words are preferred as strongly as supported ones, that is the "likelihood is not a
   truth score" example the write-up needs.
4. **Desk: the three figures.** Reconstruction specificity (finding 1 bars); snippet ablation (R3 curve +
   C1 positions); readout with donor controls (T2a topic own/swap/none; T2c per-pair D(h_a) vs D(h_b)
   with the C3 factorial).

Not now: round-4 distributed steering; 27B replication; more prompt sweeps. Both are extensions to name.

## Files owed / housekeeping
- Merge `nightshift/round3b` after review (`git merge --no-commit --no-ff nightshift/round3b && git
  checkout HEAD -- CLAUDE.md`, then commit); copy `overnight/out/c3_acts.npz` first.
- Human log: re-derive one round-3b number by hand (e.g. mean D(h_a) − D(h_b) from `t2c_pairs.csv`).

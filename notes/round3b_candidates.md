# Round 3b candidates — SUPERSEDED by overnight/PLAN.md "Round 3b stages" (2026-09-06 23:25, after advisor feedback in notes/advisor_round3_feedback.md). Drafted 2026-09-06 22:50 while T3 was still running (desk; nothing here has run)

Three short stages that round-3 results make worth running. All reuse cached artifacts; total
compute ≈ 35 min plus model loads. Listed in priority order. Numbers only, same rules as PLAN.md.
Written here rather than in the worktree because a loop is running there.

## T2b — swap control for the T2 claim-corruption readout (AV forward only, ~10 min)
**Why.** T2-claims is the strongest "semantics are still accessible" number of the round
(injected lp_orig − lp_corrupt 9.78 vs 1.39 with no injection, frac 0.973; t2_summary.md). But the
prefix is the claim's own greedy prefix, and the "original" word is the word the AV itself emitted
from that activation. The no-injection arm removes the activation entirely (raw marker embedding),
which is out of distribution. The control that separates "the activation carries the fact" from
"the AV continues its own prefix" is the same prefix under a *foreign* activation, exactly as the
topic test already had (swap prefers foreign 0.77).
- For every T2 claim row (691 single-word pairs), recompute lp_orig − lp_corrupt with the foreign
  stimulus's activation h_{(i+100) mod 200} injected (same pairing as t0_topics.csv). Also under the
  same-document other-position activation `h20_pos2` from acts_L20.npz (nearer null: same text, other
  token).
- Report: d_swap (mean, CI by explanation), d_inj − d_swap paired, frac d_swap > 0; the same split
  LLM-corrupt / deterministic / last-claims-only as in t2_summary.md.
- **Kill T2b:** CI of mean(d_inj − d_swap_foreign) ≤ 0 → MET (the preference for the original word is
  the prefix, not the activation). Report d_inj − d_swap_pos2 alongside, not as a kill.
- Build: extend `t2_prefix.py` logic into `t2b_swap.py`; outputs `t2b_claims.csv`, `t2b_summary.md`.

## T2c — forced-prefix entity readout on the C2 matched activation pairs (AV forward only, ~5 min)
**Why.** C2 showed the score separates one-fact activation pairs (M = 0.019, 40/40 > 0) although
66/80 descriptions mention neither entity. T2 showed a prefilled continuation reads the topic out of
the activation. Put them together: can the AV's likelihood read *which* entity is in h_a vs h_b when
the description never says it? This is the cleanest version of "accessible but not verbalized".
- For each of the 40 pairs: prefill `<explanation>\nThe passage mentions` and compare summed
  log-prob of ` {e_a}` vs ` {e_b}` under h_a, under h_b, and with no injection. Also the two
  descriptions' own text as prefix is NOT used (keeps the test description-free).
- Score per pair: Δ_a = lp(e_a|h_a) − lp(e_b|h_a), Δ_b = lp(e_b|h_b) − lp(e_a|h_b). Report mean
  Δ_a + Δ_b (cluster by template), frac > 0, AUROC of Δ under h_a vs under h_b, and the same after
  subtracting the no-injection prior (commoner-word bias).
- **Kill T2c:** CI of mean(Δ_a + Δ_b), cluster by template, ≤ 0 → MET (the entity 11–17 tokens
  upstream is not readable from the final-token activation by forced prefix).
- Build: `t2c_entity.py` over `out/c2_acts.npz` + `c2_pairs.csv`; outputs `t2c_pairs.csv`,
  `t2c_summary.md` with all 40 rows.

## C3 — activation-side wording null for C2 (TARGET + AV + AR, ~20 min)
**Why.** C2 has no null. A description generated from h_a will fit h_a better than a description
generated from any other activation, fact or no fact, because greedy generation is a function of h.
The text-side test (S3) had a paraphrase null; the activation-side test needs one too: change one
*non-factual* token at the same distance from the end, keep the entity.
- Same 10 templates, same 4 entity pairs, but the pair now differs in one function/adjective word
  before the entity, with the entity fixed at entity a, e.g. `The capital of the country is Paris.
  Tourists arrive at the main station` vs `… arrive at the central station …`. Assert equal token
  counts and the same shared suffix. 40 pairs, 80 AV generations, 200 AR forwards.
- Report M_wording exactly as C2's M, and cos(h_a, h_b) for the wording pairs, next to C2's
  M_fact = 0.019 and cos 0.966. Paired by template.
- **Kill C3:** CI of mean(M_fact − M_wording), cluster by template, ≤ 0 → MET (the score's
  discrimination between the two activations is not specific to the fact: a same-sized non-factual
  change is discriminated as well). Report the cos(h_a,h_b) difference between the two pair types,
  since a larger activation change trivially gives a larger M.
- Research choices for the human: which non-factual word to change (fixed list per template), and
  whether to match cos(h_a,h_b) between pair types rather than token count.
- Build: `c3_wording.py` reusing `c2_matched.py`; outputs `c3_pairs.csv`, `c3_descriptions.jsonl`,
  `c3_summary.md`.

## Not proposed
- A T4 dose-response below β = 0.25 (sports already 1.000 at 18° rotation): descriptive only.
- More T1 wordings: T1 sits at 0.61 against a RepE probe at 0.74–0.81; the matched-claim contrast
  already gives the number that matters (true−corrupt 0.015 < true−para 0.036).
- T5 stays superseded by the round-4 steering design.

## How to run
Option A (after MORNING3 lands, recommended): merge round 3, append these three stages to
`overnight/PLAN.md` on main as "Round 3b" with execution order T2b → T2c → C3 → T7 (MORNING3b.md),
fresh worktree `nightshift/round3b`, hard stop 1.5 h.
Option B (tonight, before T6): add the stages to the running worktree's PLAN.md and STATE.md before
T3 hits its cap (~23:28). This breaks the "never edit the worktree while a loop runs" rule and the
orchestrator may already be mid-T6; the human decides.

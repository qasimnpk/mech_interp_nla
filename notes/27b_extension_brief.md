

## 8. OPTIONAL after §7 is submission-ready: bounded 27B replication on RunPod [AI setup and run; YOU ≤ 90 min]
Purpose (advisor): does the separation between reconstruction sensitivity and targeted factual readout appear
in a second released NLA? A replication across two systems (target family, training, layer and interpreter all
change), not a scaling experiment. Do not spend money to look serious; spend it only for this question.
- [ ] Authorize: one on-demand **H200 141 GB** on runpod.io (listed ≈$4.59/h; confirm the quote), persistent
      volume, **one 12 h session** with a scheduled stop, spend cap ≈$60 + storage. No preemptible, no vast.ai.
- [ ] Brief the setup agent (copy into its task):
      separate branch `cloud/27b`; never touch the frozen 7B artifacts; checkpoint
      `ceselder/qwen3.6-27b-nla-rl` only (Qwen3.6-27B, layer 42, AV base + RL adapter, separate AR, 64 example
      activations); inspect the released reference code for extraction site, injection hook, normalization,
      templates and AR head; load models sequentially target → AV → AR, bf16, small batches; run the supplied
      examples first, then a small fresh-data end-to-end check; record exact revisions, dependencies, hardware and
      every adaptation; **stop setup after 3 elapsed hours** if valid AV generation and AR scoring are not both
      working, and do not start a second model port; **stop the pod at 12 elapsed hours** regardless, exporting
      all artifacts; no pushes.
- [ ] Gate: YOU approve the pilot's raw examples (10 explanations read against their contexts) before the
      evaluation runs. [YOU, 20 min]
- [ ] Frozen scope, ≈40 source positions and 40 controlled entity pairs, subject to measured throughput:
      | priority | measurement | controls |
      |---|---|---|
      | required | reconstruction specificity | own, shuffled same-doc, empty |
      | primary | AR response to factual corruption vs paraphrase | validated edits; keep surrounding wording and final tokens |
      | secondary | forced-prefix entity readout on matched contexts | both donors, no injection, one held-out prefix; accuracy and donor sensitivity |
      | optional | local-snippet contribution | only if the 27B explanations contain comparable snippets |
      Do not impose the 7B three-claim format; report how many outputs permit valid edits; inspect examples before
      trusting the splitter. Pre-declare adapter, scoring rule, exclusions and endpoints in `overnight/PLAN.md`
      as a "Round 27B" block before the evaluation starts.
- [ ] Interpretation, pre-committed: similar dissociation → limitation extends beyond the first checkpoint;
      better factual discrimination → a boundary on the 7B conclusion; weak or inconclusive → small replication,
      limited precision; setup fails validation → no conclusion, stays future work. Whatever happens, the 7B
      report does not depend on it; add one paragraph and one figure at most.
- [ ] Elapsed-time note: the agent's setup can start early in parallel (it costs you nothing until the gate), but
      your attention on it stays after §7.

---
Suggested elapsed windows (advisor): first 3 h §0–3 (agent may begin §8 setup in parallel); by hour 12 §4–6 drafted;
hours 12–24 freeze experiments and finish the write-up; final 12 h sleep, review, form questions, submit with buffer.

# Findings so far (agent-drafted, 2026-09-06 ~10:00; every number traces to overnight/*.md or a one-liner noted here)

## Advisor-facing progress summary (share this; rewrite in your own voice first)
We ran the released Qwen2.5-7B-Instruct layer-20 natural language autoencoder end-to-end on 200 wikitext positions. The pipeline reproduces and is highly position-specific: 0.88 cosine on the right activation, 0.37 on a different position of the same document, and 0.35 with no explanation at all. The reconstructor treats claims as real units, since deleting one costs more than deleting a random span of the same length, and almost nothing you delete ever helps. But it is nearly blind to facts: changing europium to lead or Charles I to Charles II moves the score by 0.003, a meaning-preserving paraphrase moves it by 0.005, and this holds even when every claim in the explanation is corrupted at once, while a claim about a different activation is caught easily (AUROC 0.96). Almost the entire score is carried by the final "this token ends X, expecting Y" snippet (88% of the lift on its own); the topical claims a human would fact-check are nearly invisible to the reconstructor, and the target model's own layer-20 encoding of the claim sentences shows the same wording dominance. The verbalizer ignores every instruction we gave it (0/200), so inference-time prompting cannot pull out more. A describer that never sees the activation lands at the floor, so reconstruction genuinely needs the activation even though it does not track truth. Net: using the reconstructor to remove hallucinated claims does not work on this checkpoint, and the reason is interpretable: it scores a single-token residual whose description is dominated by local wording.


Checkpoint: kitft Qwen2.5-7B-Instruct block-20 NLA pair (Anthropic release). 200 wikitext positions, 160 evaluation. All CIs cluster-bootstrap by explanation.

## 1. The pipeline reproduces and is position-specific (round 1, S1)
cos own 0.882; same-document other position 0.366; other document 0.320; empty explanation 0.347; blind describer from context 0.429; raw context 0.473. Adjacent layers 0.835. (MORNING1, s1/s4 summaries.)

## 2. The reconstructor reads wording, not facts (rounds 1–2)
- One-fact corruption costs 0.0031; meaning-preserving paraphrase costs 0.0049 (A−P = −0.0018, CI [−0.0028, −0.0008], n=490). K3 MET. (s3_summary)
- Corrupting EVERY claim costs 0.0075; paraphrasing every claim costs 0.0141 (R2 MET, n=160). (r2_summary)
- Off-topic claim swap is detected easily: AUROC 0.955; one-fact corruption AUROC 0.53 (chance). (s3_summary:36-40)
- Deterministic number/name swaps give the same picture. (s3, r1)

## 3. The blindness is not the AR's alone: the target's own encoding of the claim text behaves the same way (round 2, R1)
Target layer-20 last-token distance: corruption 0.040, paraphrase 0.134 (S_T = −0.094). AR value-head: 0.022 vs 0.071. Mean-pooled target: 0.00013 vs 0.00134. (r1_summary:8-16)
**Caveat (desk, not yet in any bench file):** the last-token comparison is confounded — c and c* usually share their final tokens, c~ does not, and a single-token residual is dominated by local wording. Mean-pooling removes that confound and leaves both effects tiny and paraphrase still 10× larger. Read R1 as "the target's sentence encoding is wording-dominated too", not as a clean localisation.

## 4. Where the reconstruction score comes from: the last snippet (round 2 R3 + desk breakdown)
- Last claim alone recovers 88% of the lift over floor (cos 0.822); first claim alone 23% (cos 0.467); first three claims 94%. (r3_summary:10-20)
- Deleting the last claim costs 0.125; the first 0.010; middle 0.017. (desk one-liner over s2_claims.csv, eval, 2026-09-06)
- The last snippet in this checkpoint's format is the "Final token X ends … strongly expecting …" claim: local token + next-token prediction. The topical claims (article genre, subject) barely move the score.
- Even corrupting the LAST claim costs only 0.0048 vs paraphrase 0.0055 (desk one-liner over s3_scores.csv joined to s2_claims.csv). So the AR reads the local snippet's wording, not its stated facts, either.

## 5. The verbalizer does not follow instructions at inference (round 1, S5)
0/80 mechanical compliance (one word, French), 0/120 agent-judged (opposite, angry, POS); cos unchanged (±0.003). Injection asserts pass on every variant. (s5_summary)
**Correction (desk check 2026-09-06 18:45, over s5_outputs.jsonl):** outputs are NOT literally identical to the default — 0/40 exact matches for every variant; word-sequence similarity to V0 is 0.55–0.59 (vs 0.17 between explanations of different stimuli); first sentence identical in 0–7 of 40. So the instruction text perturbs the greedy token stream the way a different sampling seed would, but content, format and length stay the default. "Trained to ignore all but the vector" is the right reading; a clean noise floor (V0 resampled at T=0.7, 40 gens, ~7 min) has not been run.

## 6. Length
Spearman(n_tokens, cos) = −0.19 across explanations (longer slightly worse), but Spearman(claim words, cos_alone) = +0.70 within claims (longer claims carry more). (s1, r3)

## One-paragraph story (draft for the human to rewrite)
The released Qwen2.5-7B NLA reconstructs its own position's activation well and is strongly position-specific, but its reconstruction score is a wording-match score, not a truth score: changing a fact in a claim costs less than rephrasing it, even when every claim is corrupted, while a claim about a different activation is caught easily. Nearly all of the score is carried by the final "what token is this and what comes next" snippet; the topical claims that a human would fact-check are almost invisible to the reconstructor. The target model's own layer-20 encoding of the claim sentences shows the same wording dominance, so the blindness is a property of single-token residual descriptions, not a bug in the reconstructor. The verbalizer ignores instruction text entirely, so inference-time prompting cannot pull out more. Net: using the reconstructor to remove hallucinated claims does not work on this checkpoint, for an interpretable reason.

## Relation to the NLA paper's own deletion test (primary source read 2026-09-06; `notes/nla_paper_card.md`)
The paper reports that removing true claims hurts more than removing false ones, that context-relevant false claims hurt more than unrelated ones, that both trends are "noisy on individual transcripts", and that "the AR is only a weak per-claim verifier". We did not run their natural true/false test; ours is the paired one-fact-corruption vs paraphrase test. Our results are consistent with theirs and sharpen them: the relevance gradient reproduces (off-topic AUROC 0.955), while a thematically faithful false claim — the paper's own characterisation of a typical confabulation — is invisible (AUROC 0.53). Do not write "failed to reproduce"; write "the verifier detects relevance, not truth, and confabulations are by their own account thematically faithful".

## Not yet done (see notes/progress_vs_advisor.md §B/§F)
In-domain mean-direction baseline; human labelling of natural claims blind to Δ; role-reversal corruptions; random-vector control for S5; any 27B replication.

## Desk check 2026-09-06 ~10:30 — does corruption cost depend on where the fact sits? (crude, word-overlap)
Split the 402 accepted corruptions by whether the swapped-out word appears within ~80 chars before the target token ("near", n=62), elsewhere in the 64-token left context ("ctx", n=27), or not in the context at all ("absent", n=313). Corruption cost: near 0.0036, ctx 0.0032, absent 0.0022 (medians ≈0.001 in all three). Weak gradient in the expected direction, all far below the paraphrase cost of ~0.005. Word-overlap heuristic only; not a substitute for a real locality experiment.

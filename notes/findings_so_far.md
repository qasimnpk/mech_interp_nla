# Findings so far (agent-drafted, 2026-09-06 ~10:00; every number traces to overnight/*.md or a one-liner noted here)

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

## 5. The verbalizer is not promptable at inference (round 1, S5)
0/80 mechanical compliance (one word, French), 0/120 agent-judged (opposite, angry, POS); outputs near-identical to default under every instruction, cos unchanged (±0.003). Injection asserts pass on every variant. (s5_summary)

## 6. Length
Spearman(n_tokens, cos) = −0.19 across explanations (longer slightly worse), but Spearman(claim words, cos_alone) = +0.70 within claims (longer claims carry more). (s1, r3)

## One-paragraph story (draft for the human to rewrite)
The released Qwen2.5-7B NLA reconstructs its own position's activation well and is strongly position-specific, but its reconstruction score is a wording-match score, not a truth score: changing a fact in a claim costs less than rephrasing it, even when every claim is corrupted, while a claim about a different activation is caught easily. Nearly all of the score is carried by the final "what token is this and what comes next" snippet; the topical claims that a human would fact-check are almost invisible to the reconstructor. The target model's own layer-20 encoding of the claim sentences shows the same wording dominance, so the blindness is a property of single-token residual descriptions, not a bug in the reconstructor. The verbalizer ignores instruction text entirely, so inference-time prompting cannot pull out more. Net: using the reconstructor to remove hallucinated claims does not work on this checkpoint, for an interpretable reason.

## Not yet done (see notes/progress_vs_advisor.md §B/§F)
In-domain mean-direction baseline; human labelling of natural claims blind to Δ; role-reversal corruptions; random-vector control for S5; any 27B replication.

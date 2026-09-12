# Paper card — "Natural Language Autoencoders Produce Unsupervised Explanations of LLM Activations" (Transformer Circuits, 2026)
Primary source: the paper at https://transformer-circuits.pub/2026/nla/index.html (read 2026-09-06; quotes verbatim). The full text and the recovered figure data were kept locally while working and are not redistributed here.

## What the paper says that bears on our results
- **AR as verifier (their claim-deletion test):** "We test this by deleting individual claims from AV explanations and measuring the change in reconstruction error. Removing true claims hurts MSE more than removing false claims, and removing context-relevant false claims hurts more than removing unrelated ones. These trends hold in aggregate but are noisy on individual transcripts, so the AR is only a weak per-claim verifier."
- **Recurrence heuristic:** "True claims recur more often. We find that true claims are more likely to appear across multiple token positions than false claims."
- **Confabulations are thematically faithful:** "while NLA claims can be false in their specifics, they are typically thematically faithful to the context. For instance, given text referencing a historical dynasty, NLA explanations might falsely claim that a specific king from that dynasty is mentioned."
- **Steganography / paraphrase:** "Meaning-preserving transformations, like shuffling bullet points, paraphrasing, or translating the explanation to French, cause only small drops in FVE ... The coherence and paragraph-summary transformations do reduce FVE substantially."
- **Format:** Claude NLAs use "4-5 text snippets"; the released open pair uses 2-3 (its nla_meta.yaml). Warm-start is a summarisation proxy task: summaries "of the text up to that token", "short paragraphs with bolded topic headings".
- **Limitations listed:** confabulation; lack of mechanistic grounding; "Excessive expressivity: Because the AV is a full language model, it has the capacity to make additional inferences beyond what is stored in an activation."

## How our results relate (desk reading, 2026-09-06)
- We did **not** run their test (natural true vs false claims, human-labelled). We ran a sharper, label-free one: one-fact corruption vs paraphrase of the *same* claim. Ours is not a failed replication; it is a refinement of their "weak per-claim verifier".
- Their gradient "unrelated false < context-relevant false < true" matches ours: off-topic swap is caught (AUROC 0.955), a thematically faithful false claim (their own description of a typical confabulation) is not (AUROC 0.53, costs less than paraphrase). Reading: the AR scores *relevance and wording*, not truth — which is exactly the case their verifier cannot handle, since confabulations are "thematically faithful".
- Their paraphrase result (small FVE drop) matches ours (0.005 cost); our contribution is the paired comparison showing the fact change costs even less.
- Their recurrence heuristic ("true claims recur across positions") is the paper's own version of the cross-position idea; a locality/recurrence experiment would test it directly on the open checkpoint.

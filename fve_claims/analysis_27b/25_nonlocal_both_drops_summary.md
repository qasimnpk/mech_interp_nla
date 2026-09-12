# 27B: FVE drops after excluding local claims from both truth classes

Local means a claim about the source prefix's final sentence, its event/attribute/entity slots, its syntax/completeness, or its final word/token. A wrong or invented replacement of a final-sentence fact is still local. Global subject identity, article-wide properties, earlier facts, and genuinely mixed earlier/final content are retained unless the claim explicitly concerns the final wording or structure. Position in the generated explanation alone is not a locality label.

Operational rule: For BOTH truth classes, exclude any explicit final_token/final_word subtype or any claim with nonempty evidence entirely in the source final sentence. Then add text-reviewed final-sentence/token claims that this rule misses. Thus a few broad/mixed claims with narrowly annotated evidence are excluded by the shared evidence proxy; borderline notes identify these.

Locality review is agent-produced, not human-validated. Existing truth labels and scored rewrites are unchanged. The review uses text, not FVE, to decide exclusions.

Removed 404/863 true claims and 229/445 false claims; retained 459 true and 216 false. The true exclusions include 15 explicit final-sentence/word-reference claims missed by the previous evidence-only filter.

FVE drops below are percentage points. Intervals are mean ± 1.96 claim-level SEM, assuming independent claims. Positive drop means the edit reduced FVE.

| Type | Truth | n | Deletion drop [95% CI] | Heavy-paraphrase drop [95% CI] |
|---|---|---:|---:|---:|
| all | true | 459 | 0.213 [0.090, 0.335] | -0.036 [-0.097, 0.024] |
| all | false | 216 | 0.345 [0.113, 0.578] | -0.143 [-0.267, -0.018] |
| theme | true | 374 | 0.171 [0.031, 0.311] | -0.068 [-0.129, -0.007] |
| theme | false | 35 | 0.138 [-0.123, 0.400] | -0.145 [-0.315, 0.026] |
| entity | true | 6 | 0.693 [-0.140, 1.526] | -0.251 [-0.624, 0.122] |
| entity | false | 89 | 0.479 [0.045, 0.913] | -0.140 [-0.344, 0.065] |
| detail | true | 79 | 0.373 [0.120, 0.626] | 0.129 [-0.062, 0.320] |
| detail | false | 92 | 0.295 [-0.040, 0.630] | -0.145 [-0.352, 0.062] |

Overall true-minus-false differences:
- deletion_drop: -0.133 pp, 95% CI [-0.395, +0.130].
- paraphrase_drop: +0.107 pp, 95% CI [-0.032, +0.245].

Neither overall mean difference excludes zero. True claims have a slightly larger mean deletion drop within each type, whereas the aggregate is smaller because the truth classes have different type compositions. No AUROC or classifier analysis was run.

Audit: `25_nonlocal_both_drops_audit.csv`; annotation decisions: `25_locality_review.json`; full tables and a four-claim mixed/global-retention sensitivity check: `25_nonlocal_both_drops_results.csv`. In that sensitivity check, false mean deletion drop is 0.277 pp and false mean paraphrase drop is -0.114 pp.

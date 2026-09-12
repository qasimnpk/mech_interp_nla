# human-plan.md — claim-deletion application, last 3 hours (revised 2026-09-11)

**Deadline:** Fri Sept 11, 11:59pm PT. Form answers don't count toward the 20 h; the write-up does.
Your entry (2026-09-09): Hours used now `_10_`; permitted remaining `_10_` (of 16, hard max 20) + 2 h for the exec summary. Protected sleep window `_10_`.

**Focus:** the claim-deletion study on Re-DocRED, 7B and 27B. Rounds 1–5 are side material (bottom).
**After every step:** one line in `notes/human_log.md` — what you did, how, the result. Run commands from `~/repos/mech_interp_nla`.

## Plan (3 h: checks, then 2 h of writing)

| # | task | time |
|---|---|---|
| 1 | §1 Checks | 45 min |
| 2 | §2 Form answers — the filter, so they get the most time | 50 min |
| 3 | §3 Exec summary + random examples | 35 min |
| 4 | §3 Write-up, short; the table is the figure | 20 min |
| 5 | §4 Final pass and submit | 15 min |
| — | Buffer | 15 min |

## Headline

**Primary finding:** heavy paraphrasing is not a better indicator of a claim's truth than deletion — its FVE drop is the same
for true and false claims in both models. Deletion *is* an indicator: deleting a true claim drops FVE more than deleting a
false one (clear on the 7B; on the 27B only for detail claims — see uncertainty).

Table (image: `fve_claims/graphs & images/fve_true_false_deletion_vs_heavy_paraphrase.png`; means over claims, all types,
irrelevant excluded, local FVE denominators):

| model | claims | n | original FVE % | after deletion % | after heavy paraphrase % | deletion drop pp | paraphrase drop pp |
|---|---|---|---|---|---|---|---|
| 7B | true | 519 | 64.667 | 63.084 | 47.374 | 1.583 | 17.293 |
| 7B | false | 649 | 63.593 | 62.650 | 46.080 | 0.943 | 17.513 |
| 27B | true | 863 | 68.172 | 64.025 | 68.084 | 4.147 | 0.088 |
| 27B | false | 445 | 67.198 | 64.542 | 66.996 | 2.656 | 0.202 |

**Uncertainty** (agent-computed with `fve_claims/audit/headline_table.py`; true − false, document-bootstrap 95% CI, documents where true > false):
- 7B deletion: 0.64 pp [0.35, 0.96]; 68/100 documents (p = 0.0004).
- 27B deletion: 1.49 pp [−0.25, 3.03]; 59/99 documents (p = 0.07) — **not significant pooled over types.** On 27B detail
  claims it is: 4.73 pp within documents, 57/91 documents (p = 0.021).
- Paraphrase: 7B −0.22 pp [−2.91, 2.30]; 27B −0.11 pp [−0.54, 0.16] — no difference in either model.

**AUROC (secondary):** _to be recomputed / provided by you._

Setup: [fve_claims_baseline_protocol.md](notes/fve_claims_baseline_protocol.md) (sentence-unit version; claims are now atomic)
· [ANNOTATION_GUIDE.md](fve_claims/ANNOTATION_GUIDE.md) · [REWRITE_GUIDE.md](fve_claims/REWRITE_GUIDE.md) (heavy paraphrase rules).

## 1. Checks — 45 min [YOU]

- [ ] **Labels, blind (25 min).** `uv run python fve_claims/audit/make_spotcheck.py` writes `notes/claim_spotcheck_BLIND.md`:
  17 detail claims (3 true + 3 false at random per model, plus the 5 largest 27B detail deletion drops), shuffled. Label each
  from its passage and [ANNOTATION_GUIDE.md](fve_claims/ANNOTATION_GUIDE.md) without opening the KEY, then
  `uv run python fve_claims/audit/score_spotcheck.py`. If you disagree on 2+ random items for a model, or on any
  largest-drop item, put the agreement rate in the limitations.
- [ ] **Heavy paraphrases (5 min).** `uv run python fve_claims/audit/paraphrase_samples.py` writes `notes/paraphrase_samples.md`:
  5 random claims per model, the text before and after the rewrite. Same meaning and specifics? If not, the paraphrase
  column measures something else — say so.
- [ ] **Numbers (10 min).** Write your own one-liner for one cell first. The script below prints the table rows
  (27B true after deletion recomputes to 64.024; the table's 64.025 is rounding):
```sh
uv run python - << 'EOF'
import glob, json
import pandas as pd

KEYS = ["pilot_id", "claim_id"]


def read_labels(pattern):
    rows = [json.loads(line) for path in sorted(glob.glob(pattern)) for line in open(path)]
    return pd.DataFrame(rows)[KEYS + ["truth"]]


def table(claims, original, deleted, paraphrased):
    claims = claims[claims.truth.isin(["true", "false"])]
    fve = pd.DataFrame({
        "truth": claims.truth,
        "original": claims[original],
        "after deletion": claims[deleted],
        "after heavy paraphrase": claims[paraphrased],
        "deletion drop": claims[original] - claims[deleted],
        "paraphrase drop": claims[original] - claims[paraphrased],
    })
    out = (fve.groupby("truth").mean() * 100).round(3)
    out.insert(0, "n", fve.truth.value_counts())
    return out.loc[["true", "false"]]


# 27B: one score file
scores = pd.read_csv("fve_claims/04_06_scores_27b_full.csv")
labels = read_labels("fve_claims/tasks/02_atoms_27b_doc*.jsonl")
print("27B")
print(table(scores.merge(labels, on=KEYS), "fve_z", "fve_del", "fve_heavy").to_string())

# 7B: deletion and heavy-paraphrase scores are in separate files
paths = sorted(glob.glob("fve_claims/04_scores_7b_b*.csv"))
scores = pd.concat(pd.read_csv(path) for path in paths)
heavy = pd.read_csv("fve_claims/06_scores_7b_paraphrase.csv")[KEYS + ["fve_heavy_local"]]
labels = read_labels("fve_claims/tasks/02_atoms_7b_doc*.jsonl")
claims = scores.merge(heavy, on=KEYS).merge(labels, on=KEYS)
print("7B")
print(table(claims, "fve_z_local", "fve_del_local", "fve_heavy_local").to_string())
EOF

# confidence intervals and per-document counts for the uncertainty lines
uv run python fve_claims/audit/headline_table.py
```

- [ ] **Code (5 min).** Read how the numbers are made: `fve`, `P_orig` and `fve_heavy` in `fve_claims/04_06_score_27b_full.py`;
  `fve_claims/06_score_paraphrase.py` (7B heavy); deletion by exact text span, no LLM, in `fve_claims/gen_deletions_27b.py`.

**Where results go:** agreement rates and the paraphrase check → LLM-use and limitations answers, and the write-up's "What I
verified"; re-derived numbers and code read → "What I verified"; the uncertainty lines → conclusions and evidence-against
answers; all of it → `human_log.md`.

## 2. Form answers — 50 min [YOU]

Neel reads these first and filters on them. Write them before anything else, then reuse them for the summary and the doc.
Words, at the low end: question 50 · why 80 · conclusions 150–200 · setup 200 · evidence against 80 · limitations 120 ·
LLM use 200 · prior experience 50 · other evidence ~100 · why Neel 50 (about 1,100 total). Specifics: the models, the
experiment, the surprising number (paraphrase drop identical for true and false; 7B paraphrase drop ~17 pp vs 27B ~0.1 pp).

## 3. Exec summary (35 min) and write-up (20 min) [YOU]

- [ ] The table is the figure: insert the PNG after checking its cells against §1.
- [ ] Random examples: `uv run python fve_claims/audit/random_examples.py` → `notes/claim_random_examples.md` (2 random
  documents, both models, every claim with label and drop). Read it; don't re-roll the seed; paste after the exec summary.
- Exec summary ≤ 600 words (aim ~400): problem (the paper's "weak per-claim verifier"; Neel's FAQ L721), method, the finding,
  the table. Then the random examples.
- Write-up, ~1,000 words: setup (reuse the technical-setup answer), results, "What I verified" from `human_log.md`,
  limitations. Rounds 1–5: one sentence and a pointer, or leave out.

## 4. Final pass and submit — 15 min [YOU]

- [ ] Numbers in the form = exec summary = doc = §1 outputs.
- [ ] Doc viewable by anyone with the link; code link only if the repo is public; Toggl screenshot; submit; save the confirmation.

## Wording

- "Deleting a true claim lowers FVE more than deleting a false one, on average": say it for the 7B; for the 27B, only for
  detail claims (pooled over types the CI includes zero).
- "Heavy paraphrasing does not separate true from false claims in either model", so it is not a better indicator than deletion.
- The two models react to heavy paraphrase very differently: ~17 pp drop for any claim on the 7B, ~0.1 pp on the 27B.
- Means are over claims, all types, irrelevant excluded. FVE = 1 − squared distance / D on unit-length activations;
  D = total variance (27B 0.3709 from 100 activations, with av_base as TARGET; 7B 0.6208).
- AUROC is secondary; numbers pending.
- Labels are Claude's under a written guide, checked by you on 17 detail claims.

## Side material (optional)

Rounds 1–5: experiment table, findings, one-liners and audits in `git show 34672e6:human-plan.md`. Your notes from 2026-09-09:
- 3. `b1_review_blind.csv`~~, all 8 rows: confirm the explanations describe only "The record ends here." (finding 2).~~ **DONE 2026-09-09: 8/8** `neither`**, agree with key 8/8; logged in** `notes/human_log.md`**.**
- ```
  # B1: pair similarity and omission (expect cos 0.9927; asserting sentences 0 of 192) — DONE 2026-09-09, got 0.9927 0 192, in human_log.md
  uv run python -c "import pandas as pd;c=pd.read_csv('overnight/b1_contexts.csv');s=pd.read_csv('overnight/b1_slots.csv');print(c.cos_hA_hB.mean().round(4),(s.asserts.isin(['A','B'])).sum(),len(s))"
  ```
  **B1 in prose (closed 2026-09-09; paste into the write-up as finding 2's second half and the limitations line):**
  B1 was the controlled version of the round-3 C2 test: 32 pairs of passages identical except for one fact — a recipient, an
  order, a count or an outcome — each ending with the neutral sentence "The record ends here.", with the activation read at
  that final period. The verbalizer described the closing sentence in all 64 explanations and never stated the fact one
  sentence earlier; the two activations of a pair agreed at cosine 0.993. With no explanation asserting either meaning there
  was nothing to swap or score, and the pre-registered statistic was never computed (INCONCLUSIVE, n = 0). This is a design
  failure rather than a null: the shared-suffix design moves the extraction point off the fact, and this verbalizer reports
  what is local to the extraction point. C2 worked in round 3 because its contexts ended on the fact. The test can be run at
  the period that closes the fact sentence, the secondary position round 4 cut for time.

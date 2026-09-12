# fve_claims — atomic claim annotation and deletion FVE

Current protocol: **atomic-v1**. Source activations and AV explanations are unchanged.
The earlier sentence labels, tasks, and any sentence scores are legacy artifacts and cannot
be reused as atomic annotations. Atomic outputs use separate filenames.

## Annotation
Read [ANNOTATION_GUIDE.md](ANNOTATION_GUIDE.md). One record describes one independently
checkable proposition, deduplicated within an explanation with all AV occurrence spans.
Truth uses only the exact visible prefix. Types are entity, detail, theme, and forecast.
Tasks are score-blind; sentences supply context IDs, never claim boundaries.

```sh
python3 fve_claims/02_claims.py --batch 0 --start 0 --end 25
python3 fve_claims/02_claims.py --batch 1 --start 25 --end 50
python3 fve_claims/02_claims.py --batch 2 --start 50 --end 75
python3 fve_claims/02_claims.py --batch 3 --start 75 --end 100
# After annotators write the atomic JSONL records:
python3 fve_claims/02_claims.py --labels fve_claims/tasks/02_atoms_7b_batch*.jsonl
```

Task files: `tasks/02_atomic_tasks_7b_batchN.json`. Merged annotations: `legacy/02_atoms_7b.jsonl`.

**Note.** The per-document files `tasks/02_atoms_{7b,27b}_doc*.jsonl` and `tasks/04_rewrites_*_doc*.jsonl` are the labels and
edits the reported results use. Everything in `legacy/` is from the earlier sentence-level protocol and is kept only for provenance.
`--output` overrides either destination. The merger validates IDs, labels, exact source
spans, evidence, and rationale format and reports documents without annotations.
Annotators must check semantic atomicity, equivalence, complete occurrence coverage, and
truth; code cannot establish these from offsets. All labels remain provisional for review.
The old `02b_entity_check.py` is only a legacy sentence-level diagnostic, not evidence or a labeler.

## Later deletion scoring
Provenance is not a deletion instruction. Prepare `legacy/04_deletions_7b.jsonl` as described in
the guide, with an explicit edited explanation and a recorded review that it removes all
occurrences of the atom while preserving every other proposition. The scorer rejects
unreviewed, unchanged, empty, or stale counterfactuals before loading the model.

```sh
python3 fve_claims/04_score.py
python3 fve_claims/05_analyze.py
# Human labels can be substituted, keeping claim IDs/propositions fixed:
python3 fve_claims/05_analyze.py --labels path/to/reviewed_atoms.jsonl --split eval
```

Outputs: `legacy/04_atomic_scores_7b.csv`, `legacy/04_atomic_expl_7b.csv`, `legacy/04_atomic_settings.json`,
`05_atomic_summary_<split>.md`, and `fig/fve_drop_atomic_7b_<split>.png`.
Analysis joins on document and claim IDs, rejects unmatched scores and duplicate keys,
and reports all four types × all three truth labels, with document-cluster bootstrap CIs
(1000 draws, seed 0). Means weight claims equally. Relatedness is not collected in this
revision. Unscored claims are not included in deletion statistics; counts show coverage.

Score remains `cos = cos(h, AR(z))`, `FVE = 1 - 2(1-cos)/D` and
`drop = FVE(z) - FVE(edited z)`, reported in percentage points. Denominators are the
released 7B value 0.7335 and local variance of sqrt(d)-normalized pilot activations.
Changing D rescales drops and CI endpoints. It does not change ranks.

The 100 Re-DocRED prefixes, dev IDs 0–19 / eval IDs 20–99, and original 7B generation setup
remain documented in `data/redocred_pilot/README.md` and the historical
`notes/fve_claims_baseline_protocol.md`. Scripts 00/01 produce the activations and greedy AV
explanations. The model classes still come from `overnight/nla_lib.py`.
The 27B run and paraphrase experiments remain future work. Legacy sentence paraphrase
entry points (03/04b) are disabled pending a separate atomic paraphrase protocol.

## Tests
```sh
.venv/bin/python -m unittest discover -s fve_claims -p 'test_*.py' -v
```
Tests cover provenance, deduplication keys, conflicting claims, forecast/token restrictions,
reviewed-deletion requirements, real task preparation, and scoring/analysis with a fake AR.
No model inference is needed for these checks.

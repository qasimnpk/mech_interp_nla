"""27B FVE drops after removing source-final-sentence/local-token true claims.

Operational filter: remove true claims with all annotated evidence in the source
prefix's final DocRED sentence, OR subtype final_token/final_word. All false claims
remain. Evidence spans are a proxy for locality, not an exhaustive semantic audit.
No classifier fitting or AUROC analysis. CI = mean +/- 1.96 claim-level SEM.
"""
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parents[1]
ANALYSIS = HERE / "analysis_27b"
spec = importlib.util.spec_from_file_location("pilot_builder", HERE.parent / "scripts/redocred_pilot.py")
pilot_builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot_builder)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=pilot_builder.DEFAULT_RAW)
    args = parser.parse_args()
    raw = {}
    for split in ["dev", "test"]:
        path = args.raw_dir / f"{split}_revised.json"
        assert pilot_builder.sha256(path) == pilot_builder.EXPECTED_SHA256[path.name]
        raw[split] = json.loads(path.read_text())
    sources = {}
    for line in (HERE.parent / "data/redocred_pilot/pilot.jsonl").read_text().splitlines():
        p = json.loads(line)
        text, _, boundaries = pilot_builder.detokenize(raw[p["source_split"]][p["source_index"]]["sents"])
        assert text.startswith(p["prefix_text"])
        start = boundaries[p["n_sents_kept"] - 1][0]
        sources[p["pilot_id"]] = (p["prefix_text"], start)
    atoms = {}
    for path in sorted((HERE / "tasks").glob("02_atoms_27b_doc*.jsonl")):
        for line in path.read_text().splitlines():
            a = json.loads(line)
            if a["truth"] not in ["true", "false"]:
                continue
            prefix, start = sources[a["pilot_id"]]
            evidence = a["prefix_evidence"]
            for span in evidence:
                assert prefix[span["start"]:span["end"]] == span["text"]
            if a["truth"] == "true":
                assert evidence
            final_only = bool(evidence) and all(span["start"] >= start for span in evidence)
            explicit_token = a["subtype"] in ["final_token", "final_word"]
            a["evidence_only_in_source_final_sentence"] = final_only
            a["explicit_final_token_or_word"] = explicit_token
            a["exclude_local_true"] = a["truth"] == "true" and (final_only or explicit_token)
            a["source_final_sentence_start"] = start
            a["source_final_sentence"] = prefix[start:]
            a["prefix_evidence_json"] = json.dumps(evidence, ensure_ascii=False)
            atoms[a["pilot_id"], a["claim_id"]] = a
    df = pd.read_csv(HERE / "04_06_scores_27b_full.csv").merge(
        pd.DataFrame(atoms.values()), on=["pilot_id", "claim_id"], validate="one_to_one")
    df["deletion_drop"] = df.fve_z - df.fve_del
    df["paraphrase_drop"] = df.fve_z - df.fve_heavy
    df = df.dropna(subset=["deletion_drop", "paraphrase_drop"])
    kept = df[~df.exclude_local_true]
    assert len(kept[kept.truth == "false"]) == len(df[df.truth == "false"]) == 445
    rows = []
    for cohort, subset in [("unfiltered", df), ("filtered", kept)]:
        for claim_type in ["all", "theme", "entity", "detail"]:
            typed = subset if claim_type == "all" else subset[subset.type == claim_type]
            for truth in ["true", "false"]:
                group = typed[typed.truth == truth]
                if group.empty:
                    continue
                row = {"cohort": cohort, "type": claim_type, "truth": truth, "n": len(group),
                       "documents": int(group.pilot_id.nunique())}
                for feature in ["fve_z", "fve_del", "fve_heavy", "deletion_drop", "paraphrase_drop", "P_heavy"]:
                    values = group[feature].to_numpy() * 100
                    mean = float(values.mean())
                    se = float(values.std(ddof=1) / np.sqrt(len(values))) if len(values) > 1 else float("nan")
                    row[feature] = mean
                    row[f"{feature}_ci95_low"] = mean - 1.96 * se
                    row[f"{feature}_ci95_high"] = mean + 1.96 * se
                rows.append(row)
    table = pd.DataFrame(rows)
    output = {
        "filter": "Remove true claims with all evidence in source final sentence OR subtype final_token/final_word; keep all false claims.",
        "locality_limitation": "Uses annotated evidence locality, not exhaustive semantic review; multi-sentence evidence claims retained unless explicit final-token/word subtype.",
        "units": "FVE percentages; drops in percentage points; 27B local denominator.",
        "ci_method": "Mean +/- 1.96 SEM over claims, independent-claim assumption.",
        "counts": {"original_true": int((df.truth == "true").sum()),
                   "excluded_true": int(df.exclude_local_true.sum()),
                   "retained_true": int((kept.truth == "true").sum()),
                   "retained_false": int((kept.truth == "false").sum()),
                   "excluded_by_final_sentence": int(((df.truth == "true") & df.evidence_only_in_source_final_sentence).sum()),
                   "additional_explicit_token_exclusions": int(((df.truth == "true") & ~df.evidence_only_in_source_final_sentence & df.explicit_final_token_or_word).sum())},
        "tables": rows,
    }
    (ANALYSIS / "23_nonlocal_true_drops_results.json").write_text(json.dumps(output, indent=2) + "\n")
    table.to_csv(ANALYSIS / "23_nonlocal_true_drops_results.csv", index=False)
    audit_columns = ["pilot_id", "claim_id", "truth", "type", "subtype", "proposition",
                     "exclude_local_true", "evidence_only_in_source_final_sentence", "explicit_final_token_or_word",
                     "source_final_sentence_start", "source_final_sentence", "prefix_evidence_json",
                     "deletion_drop", "paraphrase_drop"]
    df[audit_columns].sort_values(["pilot_id", "claim_id"]).to_csv(ANALYSIS / "23_nonlocal_true_drops_audit.csv", index=False)
    print(json.dumps(output["counts"], indent=2))
    print(table[["cohort", "type", "truth", "n", "deletion_drop", "deletion_drop_ci95_low", "deletion_drop_ci95_high",
                 "paraphrase_drop", "paraphrase_drop_ci95_low", "paraphrase_drop_ci95_high"]].to_string(index=False))


if __name__ == "__main__":
    main()

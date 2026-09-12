"""FVE-drop comparison after a locality exclusion applied to both truth classes.

Uses experiment 23's exact source sentence boundaries and verified evidence spans.
Shared rule: final-word/token subtype OR all nonempty evidence in the final source
sentence; add reviewed local references, including false claims without evidence.
See 25_locality_review.json for score-independent decisions and limitations.
No AUROC analysis. CIs use mean +/- 1.96 claim-level SEM, matching experiment 23.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    review = json.loads((HERE / "25_locality_review.json").read_text())
    df = pd.read_csv(HERE / "23_nonlocal_true_drops_audit.csv", dtype={"truth": str})
    assert len(df) == 1308 and df.truth.value_counts().to_dict() == {"true": 863, "false": 445}
    assert set(df.evidence_only_in_source_final_sentence.unique()) <= {True, False}
    assert set(df.explicit_final_token_or_word.unique()) <= {True, False}
    df["shared_automatic_local"] = df.evidence_only_in_source_final_sentence | df.explicit_final_token_or_word
    false_local = {(int(d), c) for d, ids in review["false_local_claim_ids_by_document"].items() for c in ids}
    true_extra = {tuple(map(int, key.split("/"))) for key in review["additional_true_local_claims"]}
    false_keys = set(zip(df.loc[df.truth == "false", "pilot_id"], df.loc[df.truth == "false", "claim_id"]))
    true_keys = set(zip(df.loc[df.truth == "true", "pilot_id"], df.loc[df.truth == "true", "claim_id"]))
    assert false_local <= false_keys and true_extra <= true_keys
    assert set(review["false_local_claim_ids_by_document"]) == {str(i) for i in range(100)}
    df["text_review_local"] = [(p, c) in false_local | true_extra for p, c in zip(df.pilot_id, df.claim_id)]
    df["exclude_local"] = df.shared_automatic_local | df.text_review_local
    notes = []
    for _, row in df.iterrows():
        key = f"{row.pilot_id}/{row.claim_id}"
        if key in review["additional_true_local_claims"]:
            note = review["additional_true_local_claims"][key]
        elif key in review["borderline_decisions"]:
            note = review["borderline_decisions"][key]
        elif row.explicit_final_token_or_word:
            note = "Explicit final-word/token claim, excluded regardless of truth."
        elif row.evidence_only_in_source_final_sentence:
            note = "All nonempty cited evidence lies in the final source sentence; shared automatic exclusion."
        elif row.text_review_local:
            note = "Text review: assertion refers to the final source sentence's event, entity, attribute, or syntax; excluded despite missing/earlier evidence."
        else:
            note = "Retained: earlier/global/mixed content; no additional final-sentence/token locality identified."
        notes.append(note)
    df["locality_rationale"] = notes
    df["locality_review_flag"] = [f"{p}/{c}" in review["borderline_decisions"] for p, c in zip(df.pilot_id, df.claim_id)]
    raw = pd.read_csv(HERE.parent / "04_06_scores_27b_full.csv")
    df = df.merge(raw[["pilot_id", "claim_id", "fve_z", "fve_del", "fve_heavy", "P_heavy"]],
                  on=["pilot_id", "claim_id"], validate="one_to_one")
    assert np.allclose(df.deletion_drop, df.fve_z-df.fve_del)
    assert np.allclose(df.paraphrase_drop, df.fve_z-df.fve_heavy)
    df["sensitivity_exclude_local"] = df.exclude_local
    # A transparent sensitivity variant: keep the four manually judged mixed/global
    # false claims whose only reason for exclusion is narrow contradictory evidence.
    mixed_keys = {(8, 14), (53, 7), (87, 1), (96, 9)}
    df.loc[[(p, c) in mixed_keys for p, c in zip(df.pilot_id, df.claim_id)], "sensitivity_exclude_local"] = False
    cohorts = {
        "unfiltered": df,
        "previous_true_only": df[~df.exclude_local_true],
        "both_automatic_only": df[~df.shared_automatic_local],
        "both_filtered": df[~df.exclude_local],
        "both_filtered_mixed_retained_sensitivity": df[~df.sensitivity_exclude_local],
    }
    counts = []
    for truth in ["true", "false"]:
        group = df[df.truth == truth]
        counts.append({"truth": truth, "original": len(group),
                       "automatic_exclusions": int(group.shared_automatic_local.sum()),
                       "additional_text_exclusions": int((group.text_review_local & ~group.shared_automatic_local).sum()),
                       "total_excluded": int(group.exclude_local.sum()),
                       "retained": int((~group.exclude_local).sum())})
    rows, gaps = [], []
    for cohort, subset in cohorts.items():
        for typ in ["all", "theme", "entity", "detail"]:
            typed = subset if typ == "all" else subset[subset.type == typ]
            for truth in ["true", "false"]:
                group = typed[typed.truth == truth]
                if group.empty:
                    continue
                row = {"cohort": cohort, "type": typ, "truth": truth, "n": len(group), "documents": int(group.pilot_id.nunique())}
                for feature in ["fve_z", "fve_del", "fve_heavy", "deletion_drop", "paraphrase_drop", "P_heavy"]:
                    values = group[feature].to_numpy() * 100
                    mean = float(values.mean())
                    se = float(values.std(ddof=1)/np.sqrt(len(values)))
                    row[feature] = mean
                    row[f"{feature}_ci95_low"] = mean - 1.96*se
                    row[f"{feature}_ci95_high"] = mean + 1.96*se
                rows.append(row)
            for feature in ["deletion_drop", "paraphrase_drop"]:
                t = typed.loc[typed.truth == "true", feature].to_numpy()*100
                f = typed.loc[typed.truth == "false", feature].to_numpy()*100
                if len(t)>1 and len(f)>1:
                    difference = float(t.mean()-f.mean())
                    se = float(np.sqrt(t.var(ddof=1)/len(t)+f.var(ddof=1)/len(f)))
                    gaps.append({"cohort": cohort, "type": typ, "feature": feature,
                                 "true_minus_false": difference, "ci95": [difference-1.96*se, difference+1.96*se]})
    result = {"definition": review["definition"], "shared_automatic_rule": review["shared_automatic_rule"],
              "limitations": "Agent-reviewed locality; evidence offsets are a proxy and some narrowly cited global/mixed claims are excluded. Scores/truth labels unchanged. Claim-level CIs assume independence.",
              "units": "FVE percentages and drops in percentage points, 27B local denominator.",
              "ci_method": "Mean +/- 1.96 claim-level SEM; gaps use independent-group mean standard errors.",
              "counts": counts, "tables": rows, "mean_gaps": gaps}
    (HERE / "25_nonlocal_both_drops_results.json").write_text(json.dumps(result, indent=2)+"\n")
    table = pd.DataFrame(rows)
    table.to_csv(HERE / "25_nonlocal_both_drops_results.csv", index=False)
    df.sort_values(["pilot_id", "claim_id"]).to_csv(HERE / "25_nonlocal_both_drops_audit.csv", index=False)
    print(json.dumps(counts, indent=2))
    cols = ["cohort", "type", "truth", "n", "deletion_drop", "deletion_drop_ci95_low", "deletion_drop_ci95_high", "paraphrase_drop", "paraphrase_drop_ci95_low", "paraphrase_drop_ci95_high"]
    print(table[(table.cohort == "both_filtered") | ((table.type == "all") & table.cohort.isin(["unfiltered", "previous_true_only", "both_filtered_mixed_retained_sensitivity"]))][cols].to_string(index=False))
    print(json.dumps([g for g in gaps if g["cohort"] == "both_filtered" and g["type"] == "all"],indent=2))


if __name__ == "__main__":
    main()

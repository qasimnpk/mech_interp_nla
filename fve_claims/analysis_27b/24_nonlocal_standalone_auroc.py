"""Fixed standalone scores on the filtered set: D versus -H, true = positive.

No tuning or fitted classifier. Report each of five stratified test folds and the
full-sample AUROC (pooling is valid here because the scores do not vary by fold).
DeLong inference treats claims as independent; p-values are two-sided/unadjusted.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("delong", HERE / "21_split_comparison_delong.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def evaluate(df, label):
    y = (df.truth == "true").to_numpy().astype(int)
    scores = np.column_stack([df.deletion_drop, -df.paraphrase_drop])
    result = module.paired_delong(y, scores)
    assert np.allclose(result["aucs"], [roc_auc_score(y, scores[:, j]) for j in range(2)])
    row = {"sample": label, "n": len(df), "true": int(y.sum()), "false": int((1-y).sum())}
    for j, name in enumerate(["deletion", "heavy_paraphrase"]):
        value = result["aucs"][j]
        se = np.sqrt(result["covariance"][j][j])
        row[f"{name}_auroc"] = value
        row[f"{name}_ci95_low"] = float(value - norm.ppf(0.975) * se)
        row[f"{name}_ci95_high"] = float(value + norm.ppf(0.975) * se)
        row[f"{name}_p_vs_chance_two_sided"] = float(2 * norm.sf(abs((value-0.5)/se)))
    row["heavy_minus_deletion"] = result["difference"]
    row["difference_ci95_low"], row["difference_ci95_high"] = result["difference_ci95"]
    row["paired_delong_p_two_sided"] = result["p_two_sided"]
    row["relative_improvement_percent"] = 100 * result["difference"] / result["aucs"][0]
    return row


def main():
    df = pd.read_csv(HERE / "23_nonlocal_true_drops_audit.csv", dtype={"truth": str})
    assert set(df.exclude_local_true.unique()) <= {True, False}
    df = df[~df.exclude_local_true].sort_values(["pilot_id", "claim_id"]).reset_index(drop=True)
    assert df.truth.value_counts().to_dict() == {"true": 474, "false": 445}
    rows, assignments = [], []
    coverage = np.zeros(len(df), dtype=int)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    for fold, (tr, te) in enumerate(cv.split(df, df.truth), start=1):
        assert not np.intersect1d(tr, te).size
        coverage[te] += 1
        rows.append(evaluate(df.iloc[te], f"fold_{fold}"))
        assignment = df.iloc[te][["pilot_id", "claim_id", "truth", "deletion_drop", "paraphrase_drop"]].copy()
        assignment["fold"] = fold
        assignments.append(assignment)
    assert np.all(coverage == 1)
    full = evaluate(df, "all_claims")
    output = {
        "seed": 0, "filter": "Same audited exclusion as experiment 23; all false claims retained.",
        "score_directions": {"deletion": "+deletion_drop", "heavy_paraphrase": "-paraphrase_drop"},
        "positive_class": "true", "fitted_parameters": 0,
        "inference": "Claim-level DeLong normal-approximation 95% CIs; two-sided unadjusted tests. Full-sample pooling valid for these fixed scores. Exploratory filtered analysis.",
        "folds": rows, "all_claims": full,
        "fold_means": {name: float(np.mean([r[name] for r in rows])) for name in ["deletion_auroc", "heavy_paraphrase_auroc", "heavy_minus_deletion"]},
    }
    (HERE / "24_nonlocal_standalone_auroc_results.json").write_text(json.dumps(output, indent=2) + "\n")
    table = pd.DataFrame(rows + [full])
    table.to_csv(HERE / "24_nonlocal_standalone_auroc_results.csv", index=False)
    pd.concat(assignments).sort_values(["pilot_id", "claim_id"]).to_csv(HERE / "24_nonlocal_standalone_auroc_folds.csv", index=False)
    print(table.to_string(index=False))


if __name__ == "__main__":
    main()

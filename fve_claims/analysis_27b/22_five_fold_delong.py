"""Five-fold claim-level stratified CV, with training-only scaling/weight selection.

Per-fold paired DeLong inference treats claims as independent and weights as fixed.
Fold means are descriptive: overlapping training sets preclude treating fold results
as independent replicates. Predictions from different fitted folds are not pooled.
"""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

HERE = Path(__file__).resolve().parents[1]
ANALYSIS = HERE / "analysis_27b"
spec = importlib.util.spec_from_file_location("split_delong", ANALYSIS / "21_split_comparison_delong.py")
delong_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delong_module)


def main():
    atoms = {}
    for path in sorted((HERE / "tasks").glob("02_atoms_27b_doc*.jsonl")):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            atoms[row["pilot_id"], row["claim_id"]] = row
    df = pd.read_csv(HERE / "04_06_scores_27b_full.csv").merge(
        pd.DataFrame(atoms.values())[["pilot_id", "claim_id", "truth"]],
        on=["pilot_id", "claim_id"], validate="one_to_one",
    )
    df = df[df.truth.isin(["true", "false"])].copy()
    df["D"] = df.fve_z - df.fve_del
    df["H"] = df.fve_z - df.fve_heavy
    df = df.dropna(subset=["D", "H"]).sort_values(["pilot_id", "claim_id"]).reset_index(drop=True)
    df["y"] = (df.truth == "true").astype(int)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
    weights = np.arange(301) / 100
    records, predictions = [], []
    coverage = np.zeros(len(df), dtype=int)
    for fold, (tr, te) in enumerate(cv.split(df, df.y), start=1):
        assert not np.intersect1d(tr, te).size
        coverage[te] += 1
        train, test = df.iloc[tr], df.iloc[te]
        scale = float(train.D.mean() / train.H.mean())
        assert np.isfinite(scale)
        train_aucs = np.array([roc_auc_score(train.y, train.D - w * scale * train.H) for w in weights])
        best = int(np.argmax(train_aucs))
        weight = float(weights[best])
        scores = np.column_stack([test.D, test.D - weight * scale * test.H])
        result = delong_module.paired_delong(test.y.to_numpy(), scores)
        aucs = result["aucs"]
        assert np.allclose(aucs, [roc_auc_score(test.y, scores[:, j]) for j in range(2)])
        record = {
            "fold": fold, "train_n": len(train), "test_n": len(test),
            "test_true": int(test.y.sum()), "test_false": int((1 - test.y).sum()),
            "train_mean_D": float(train.D.mean()), "train_mean_H": float(train.H.mean()),
            "scale": scale, "lambda": weight, "effective_H_coefficient": -weight * scale,
            "lambda_at_upper_boundary": bool(weight == weights[-1]),
            "train_deletion_auroc": float(roc_auc_score(train.y, train.D)),
            "train_combined_auroc": float(train_aucs[best]),
            "test_deletion_auroc": aucs[0], "test_combined_auroc": aucs[1],
            "absolute_improvement": result["difference"],
            "relative_improvement_percent": 100 * result["difference"] / aucs[0],
            "difference_ci95_low": result["difference_ci95"][0],
            "difference_ci95_high": result["difference_ci95"][1],
            "delong_p_two_sided": result["p_two_sided"],
            "delong_difference_se": result["standard_error"],
        }
        for j, name in enumerate(["deletion", "combined"]):
            radius = norm.ppf(0.975) * np.sqrt(result["covariance"][j][j])
            record[f"{name}_ci95_low"] = float(aucs[j] - radius)
            record[f"{name}_ci95_high"] = float(aucs[j] + radius)
        records.append(record)
        prediction = test[["pilot_id", "claim_id", "truth", "D", "H"]].copy()
        prediction["fold"] = fold
        prediction["combined"] = scores[:, 1]
        predictions.append(prediction)
    assert np.all(coverage == 1)
    table = pd.DataFrame(records)
    summary = {
        "mean_deletion_auroc": float(table.test_deletion_auroc.mean()),
        "mean_combined_auroc": float(table.test_combined_auroc.mean()),
        "mean_absolute_improvement": float(table.absolute_improvement.mean()),
        "mean_fold_relative_improvement_percent": float(table.relative_improvement_percent.mean()),
        "relative_improvement_of_mean_aurocs_percent": float(100 * (table.test_combined_auroc.mean() / table.test_deletion_auroc.mean() - 1)),
    }
    result = {
        "seed": 0, "n_folds": 5, "n_claims": len(df),
        "split": "Claim-level StratifiedKFold by truth; shuffled; each claim tested once.",
        "score": "D - lambda * mean_train(D)/mean_train(H) * H",
        "weight_selection": "Maximize training AUROC on lambda=0,0.01,...,3; smallest lambda wins ties.",
        "inference": "Per-fold, two-sided paired DeLong, independent-claim assumption, fixed trained weights; unadjusted p-values and 95% CIs.",
        "summary_note": "Descriptive equal-weight fold means; no pooled AUROC or aggregate p-value because training sets overlap and score functions differ.",
        "folds": records, "summary": summary,
    }
    (ANALYSIS / "22_five_fold_delong_results.json").write_text(json.dumps(result, indent=2) + "\n")
    table.to_csv(ANALYSIS / "22_five_fold_delong_results.csv", index=False)
    pd.concat(predictions).sort_values(["pilot_id", "claim_id"]).to_csv(
        ANALYSIS / "22_five_fold_delong_predictions.csv", index=False)
    columns = ["fold", "test_n", "scale", "lambda", "test_deletion_auroc", "test_combined_auroc",
               "absolute_improvement", "relative_improvement_percent", "difference_ci95_low",
               "difference_ci95_high", "delong_p_two_sided"]
    print(table[columns].to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

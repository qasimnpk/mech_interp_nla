"""Compare 85/15 and 70/30 claim splits with the same training-only weight search.

Paired DeLong covariance uses positive/negative placement values, with ties = 0.5:
https://pubmed.ncbi.nlm.nih.gov/3203132/
Claims are treated as independent. Test predictions and trained weights stay fixed.
The 70/30 run is an exploratory sensitivity check after inspecting the 85/15 run.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parents[1]


def paired_delong(y, scores):
    """Columns are deletion and combined scores; larger predicts y=1."""
    positive, negative = scores[y == 1], scores[y == 0]
    kernels = (positive[:, None, :] > negative[None, :, :]).astype(float)
    kernels += 0.5 * (positive[:, None, :] == negative[None, :, :])
    v_positive, v_negative = kernels.mean(axis=1), kernels.mean(axis=0)
    aucs = kernels.mean(axis=(0, 1))
    covariance = (np.cov(v_positive, rowvar=False, ddof=1) / len(positive)
                  + np.cov(v_negative, rowvar=False, ddof=1) / len(negative))
    contrast = np.array([-1.0, 1.0])
    delta = float(contrast @ aucs)
    se = float(np.sqrt(max(0.0, contrast @ covariance @ contrast)))
    z = delta / se if se else (0.0 if delta == 0 else np.copysign(np.inf, delta))
    radius = norm.ppf(0.975) * se
    return {
        "aucs": aucs.tolist(), "covariance": covariance.tolist(),
        "difference": delta, "standard_error": se, "z": float(z),
        "p_two_sided": float(2 * norm.sf(abs(z))),
        "difference_ci95": [float(delta - radius), float(delta + radius)],
    }


def auc(positive, negative):
    n, m = len(positive), len(negative)
    ranks = rankdata(np.concatenate([positive, negative]), method="average")
    return (ranks[:n].sum() - n * (n + 1) / 2) / (n * m)


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
    df = df.dropna(subset=["D", "H"]).sort_values(["pilot_id", "claim_id"])
    df["y"] = (df.truth == "true").astype(int)
    results = {"seed": 0, "bootstrap_draws": 5000,
               "assumptions": "Independent claims, truth-stratified split, fixed trained weights for inference; exploratory split comparison.",
               "score": "D - lambda * scale * H", "lambda_grid": "0 to 3, step 0.01"}
    for label, fraction in [("85_15", 0.15), ("70_30", 0.30)]:
        train, test = train_test_split(df, test_size=fraction, stratify=df.y, random_state=0)
        scale = float(train.D.mean() / train.H.mean())
        weights = np.arange(301) / 100
        train_aucs = np.array([roc_auc_score(train.y, train.D - w * scale * train.H) for w in weights])
        weight = float(weights[np.argmax(train_aucs)])
        run = {"scale": scale, "lambda": weight, "effective_H_coefficient": -weight * scale,
               "optimality": "Maximum training AUROC on specified grid, smallest lambda wins ties."}
        for name, subset in [("train", train), ("test", test)]:
            run[name] = {
                "n": len(subset), "true": int(subset.y.sum()), "false": int((1-subset.y).sum()),
                "deletion_auroc": float(roc_auc_score(subset.y, subset.D)),
                "combined_auroc": float(roc_auc_score(subset.y, subset.D - weight * scale * subset.H)),
            }
        scores = np.column_stack([test.D, test.D - weight * scale * test.H])
        y = test.y.to_numpy()
        delong = paired_delong(y, scores)
        assert np.allclose(delong["aucs"], [run["test"]["deletion_auroc"], run["test"]["combined_auroc"]])
        run["test"]["paired_delong"] = delong
        run["test"]["relative_improvement_percent"] = 100 * (delong["aucs"][1] / delong["aucs"][0] - 1)
        pos, neg = scores[y == 1], scores[y == 0]
        rng = np.random.default_rng(0)
        boot = np.empty((5000, 2))
        for i in range(len(boot)):
            p = pos[rng.integers(len(pos), size=len(pos))]
            n = neg[rng.integers(len(neg), size=len(neg))]
            boot[i] = [auc(p[:, j], n[:, j]) for j in range(2)]
        run["test"]["bootstrap_ci95"] = {
            "deletion_auroc": np.percentile(boot[:, 0], [2.5, 97.5]).tolist(),
            "combined_auroc": np.percentile(boot[:, 1], [2.5, 97.5]).tolist(),
            "paired_difference": np.percentile(boot[:, 1] - boot[:, 0], [2.5, 97.5]).tolist(),
        }
        results[label] = run
    old = json.loads((HERE / "analysis_27b/19_simple_paraphrase_weight_results.json").read_text())
    assert results["85_15"]["lambda"] == old["selected_lambda"]
    for name in ["train", "test"]:
        for metric in ["deletion_auroc", "combined_auroc"]:
            assert np.isclose(results["85_15"][name][metric], old[name][metric])
    output = HERE / "analysis_27b/21_split_comparison_delong_results.json"
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()

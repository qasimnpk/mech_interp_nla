"""Claim-level uncertainty for experiment 19; fixed trained weight, no document grouping.

Mean-drop CIs: normal approximation, mean +/- 1.96 SEM.
AUROC CIs: 5,000 truth-stratified paired bootstrap samples, percentile intervals.
Training AUROC intervals are descriptive and do not correct for weight selection.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parents[1]
previous = json.loads((HERE / "analysis_27b/19_simple_paraphrase_weight_results.json").read_text())
atoms = {}
for path in sorted((HERE / "tasks").glob("02_atoms_27b_doc*.jsonl")):
    for line in path.read_text().splitlines():
        row = json.loads(line)
        atoms[row["pilot_id"], row["claim_id"]] = row
df = pd.read_csv(HERE / "04_06_scores_27b_full.csv").merge(
    pd.DataFrame(atoms.values())[["pilot_id", "claim_id", "truth", "type"]],
    on=["pilot_id", "claim_id"], validate="one_to_one",
)
df = df[df.truth.isin(["true", "false"])].copy()
df["D"] = df.fve_z - df.fve_del
df["H"] = df.fve_z - df.fve_heavy
df = df.dropna(subset=["D", "H"]).sort_values(["pilot_id", "claim_id"])
df["combined"] = df.D + previous["effective_H_coefficient"] * df.H
df["y"] = (df.truth == "true").astype(int)
train, test = train_test_split(df, test_size=0.15, stratify=df.y, random_state=0)


def interval(estimate, draws):
    return {"estimate": float(estimate), "ci95": np.percentile(draws, [2.5, 97.5]).tolist()}


def auc(positive, negative):
    n, m = len(positive), len(negative)
    ranks = rankdata(np.concatenate([positive, negative]), method="average")
    return (ranks[:n].sum() - n * (n + 1) / 2) / (n * m)


result = {"bootstrap_draws": 5000, "seed": 0,
          "assumption": "Claims treated as independent; trained weights fixed in bootstrap.",
          "mean_drop_units": "percentage points", "mean_drops": {}}
for truth in ["true", "false"]:
    subset = df[df.truth == truth]
    result["mean_drops"][truth] = {"n": len(subset)}
    for feature in ["D", "H"]:
        values = subset[feature].to_numpy() * 100
        mean, se = values.mean(), values.std(ddof=1) / np.sqrt(len(values))
        result["mean_drops"][truth][feature] = {
            "mean": float(mean), "ci95": [float(mean - 1.96 * se), float(mean + 1.96 * se)]}

for name, subset in [("train", train), ("test", test)]:
    rng = np.random.default_rng(0)
    pos = subset.loc[subset.y == 1, ["D", "combined"]].to_numpy()
    neg = subset.loc[subset.y == 0, ["D", "combined"]].to_numpy()
    point = np.array([auc(pos[:, j], neg[:, j]) for j in range(2)])
    assert np.allclose(point, [previous[name]["deletion_auroc"], previous[name]["combined_auroc"]])
    boot = np.empty((5000, 2))
    for i in range(len(boot)):
        p = pos[rng.integers(len(pos), size=len(pos))]
        n = neg[rng.integers(len(neg), size=len(neg))]
        boot[i] = [auc(p[:, j], n[:, j]) for j in range(2)]
    result[name] = {
        "deletion_auroc": interval(point[0], boot[:, 0]),
        "combined_auroc": interval(point[1], boot[:, 1]),
        "paired_auroc_change": interval(point[1] - point[0], boot[:, 1] - boot[:, 0]),
        "relative_improvement_percent": interval(
            100 * (point[1] / point[0] - 1), 100 * (boot[:, 1] / boot[:, 0] - 1)),
        "type_truth_counts": {str(k): int(v) for k, v in subset.groupby(["type", "truth"]).size().items()},
        "mean_drops_pp": subset.groupby("truth")[["D", "H"]].mean().mul(100).to_dict(),
    }
path = HERE / "analysis_27b/20_simple_confidence_intervals_results.json"
path.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

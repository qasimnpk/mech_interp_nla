"""Claim-level 85/15 truth-stratified split; select one weight by training AUROC.

Run: .venv/bin/python fve_claims/analysis_27b/19_simple_paraphrase_weight.py
Score = deletion - lambda * (mean_train_deletion / mean_train_sensitivity)
        * paraphrase_sensitivity. No document grouping or fitted classifier.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parents[1]
atoms = {}
for path in sorted((HERE / "tasks").glob("02_atoms_27b_doc*.jsonl")):
    for line in path.read_text().splitlines():
        row = json.loads(line)
        atoms[row["pilot_id"], row["claim_id"]] = row
labels = pd.DataFrame(atoms.values())
df = pd.read_csv(HERE / "04_06_scores_27b_full.csv").merge(
    labels[["pilot_id", "claim_id", "truth"]],
    on=["pilot_id", "claim_id"], validate="one_to_one",
)
df = df[df.truth.isin(["true", "false"])].copy()
df["D"] = df.fve_z - df.fve_del
df["H"] = df.fve_z - df.fve_heavy
df = df.dropna(subset=["D", "H"]).sort_values(["pilot_id", "claim_id"])
df["y"] = (df.truth == "true").astype(int)
train, test = train_test_split(df, test_size=0.15, stratify=df.y, random_state=0)
scale = float(train.D.mean() / train.H.mean())
weights = np.arange(301) / 100  # 0 through 3 inclusive; smallest weight wins ties.
aucs = np.array([
    roc_auc_score(train.y, train.D - weight * scale * train.H)
    for weight in weights
])
best_index = int(np.argmax(aucs))
weight = float(weights[best_index])
result = {
    "seed": 0,
    "split": "85/15 claim-level, stratified by truth; all claim types",
    "features": {"D": "fve_z - fve_del", "H": "fve_z - fve_heavy"},
    "score": "D - lambda * scale * H",
    "train_mean_D": float(train.D.mean()),
    "train_mean_H": float(train.H.mean()),
    "scale": scale,
    "lambda_grid": {"min": 0, "max": 3, "step": 0.01},
    "selected_lambda": weight,
    "effective_H_coefficient": -weight * scale,
    "optimality": "Maximum training AUROC on this grid; no population or held-out optimality guarantee.",
    "maximizing_grid_weights": weights[aucs == aucs.max()].tolist(),
}
for name, subset in [("train", train), ("test", test)]:
    baseline = roc_auc_score(subset.y, subset.D)
    combined = roc_auc_score(subset.y, subset.D - weight * scale * subset.H)
    result[name] = {
        "n": len(subset), "true": int(subset.y.sum()),
        "false": int((1 - subset.y).sum()),
        "deletion_auroc": float(baseline), "combined_auroc": float(combined),
        "auroc_change": float(combined - baseline),
    }
output = HERE / "analysis_27b" / "19_simple_paraphrase_weight_results.json"
output.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))

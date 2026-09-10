"""27B, 100 docs: within-document paired true-vs-false difference. Per document d and category c:
diff_d = mean(P | true, d, c) - mean(P | false, d, c), defined only when d has >=1 true AND >=1 false
claim in c. Report mean over qualifying documents (each document weighted equally), bootstrap CI over
documents. Compared against the naive pooled difference from the previous table."""
import glob, json
import numpy as np, pandas as pd

import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

atoms = {}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r = json.loads(l); atoms[(r["pilot_id"], r["claim_id"])] = r
atoms_df = pd.DataFrame(atoms.values())

sc = pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
df = sc.merge(atoms_df[["pilot_id", "claim_id", "type", "truth"]], on=["pilot_id", "claim_id"], how="inner")
df = df[df.truth.isin(["true", "false"])]
df["type_merged"] = df["type"].replace({"entity": "detail"})
df["all"] = "all"

def per_doc_diffs(sub, col):
    """returns (diffs, n_true, n_false) per qualifying document"""
    rows = []
    for pid, g in sub.groupby("pilot_id"):
        t, f = g[g.truth == "true"][col], g[g.truth == "false"][col]
        if len(t) and len(f):
            rows.append((pid, t.mean() - f.mean(), len(t), len(f)))
    return pd.DataFrame(rows, columns=["pilot_id", "diff", "n_true", "n_false"])

def boot_ci(vals, n_boot=2000, seed=0):
    vals = np.asarray(vals, float)
    if len(vals) == 0: return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    b = [vals[rng.integers(0, len(vals), len(vals))].mean() for _ in range(n_boot)]
    return float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

def pooled_diff(sub, col):
    t, f = sub[sub.truth == "true"][col], sub[sub.truth == "false"][col]
    if not len(t) or not len(f): return np.nan
    return t.mean() - f.mean()

for col, label in [("P_orig", "P_orig (deletion)"), ("P_heavy", "P_heavy (heavy paraphrase)")]:
    d = df.dropna(subset=[col])
    print(f"\n=== {label} — within-document paired difference (pp) ===")
    print(f"{'category':30s} {'docs':>5s} {'within-doc mean diff [95% CI]':>34s} {'pooled diff':>12s} {'claims used':>14s} {'frac docs>0':>12s}")
    cats = [("type", "theme"), ("type", "entity"), ("type", "detail"),
            ("type_merged", "detail"), ("all", "all")]
    for grouping, t in cats:
        sub = d[d[grouping] == t]
        pd_ = per_doc_diffs(sub, col)
        name = "detail+entity merged" if (grouping == "type_merged" and t == "detail") else t
        if len(pd_) == 0:
            print(f"{name:30s} {0:>5d} {'n/a (no doc has both)':>34s}"); continue
        lo, hi = boot_ci(pd_["diff"].values)
        m = pd_["diff"].mean()
        used = f"{int(pd_.n_true.sum())}T/{int(pd_.n_false.sum())}F"
        frac = (pd_["diff"] > 0).mean()
        print(f"{name:30s} {len(pd_):>5d} {f'{m*100:8.2f} [{lo*100:7.2f},{hi*100:7.2f}]':>34s} "
              f"{pooled_diff(sub, col)*100:>12.2f} {used:>14s} {frac:>12.2f}")

# how much of the sample survives the pairing requirement
print("\n=== coverage: claims retained by the paired estimator ===")
d = df.dropna(subset=["P_orig"])
for grouping, t in [("type", "theme"), ("type", "entity"), ("type", "detail"), ("type_merged", "detail"), ("all", "all")]:
    sub = d[d[grouping] == t]
    p = per_doc_diffs(sub, "P_orig")
    name = "detail+entity merged" if (grouping == "type_merged" and t == "detail") else t
    kept = int(p.n_true.sum() + p.n_false.sum()) if len(p) else 0
    print(f"{name:24s} total claims {len(sub):5d} in {sub.pilot_id.nunique():3d} docs -> "
          f"paired keeps {kept:5d} claims in {len(p):3d} docs ({kept/max(len(sub),1)*100:.0f}% of claims)")

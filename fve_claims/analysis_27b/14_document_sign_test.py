"""Document-level sign test on the paired differences: how often does the true-claim mean exceed the
false-claim mean within a document? Robust to the magnitude outliers that dominate the mean."""
import glob, json
import numpy as np, pandas as pd
from scipy import stats

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
df["type_merged"] = df["type"].replace({"entity": "detail"}); df["all"] = "all"

for col in ["P_orig", "P_heavy"]:
    d = df.dropna(subset=[col])
    print(f"\n=== {col}: document-level sign test (H0: true-mean > false-mean in 50% of docs) ===")
    print(f"{'category':24s} {'docs':>5s} {'pos':>5s} {'frac':>6s} {'sign p':>9s} {'median diff (pp)':>18s} {'Wilcoxon p':>11s}")
    for grouping, t in [("type","theme"),("type","entity"),("type","detail"),("type_merged","detail"),("all","all")]:
        sub = d[d[grouping] == t]
        diffs = []
        for pid, g in sub.groupby("pilot_id"):
            a, b = g[g.truth=="true"][col], g[g.truth=="false"][col]
            if len(a) and len(b): diffs.append(a.mean() - b.mean())
        diffs = np.array(diffs)
        if len(diffs) == 0: continue
        pos = int((diffs > 0).sum()); n = len(diffs)
        p_sign = stats.binomtest(pos, n, 0.5).pvalue
        p_w = stats.wilcoxon(diffs).pvalue if n > 5 else np.nan
        name = "detail+entity merged" if (grouping=="type_merged" and t=="detail") else t
        print(f"{name:24s} {n:>5d} {pos:>5d} {pos/n:>6.2f} {p_sign:>9.4f} {np.median(diffs)*100:>18.2f} {p_w:>11.4f}")

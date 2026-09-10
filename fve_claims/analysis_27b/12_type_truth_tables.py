"""27B, full 100 docs: type x truth FVE table for P_orig and P_heavy, with a second grouping where
entity claims are folded into detail (scoring only -- underlying atom type field is untouched)."""
import glob, json
import numpy as np, pandas as pd

import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

atoms = {}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r = json.loads(l)
        atoms[(r["pilot_id"], r["claim_id"])] = r
atoms_df = pd.DataFrame(atoms.values())

sc = pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
df = sc.merge(atoms_df[["pilot_id", "claim_id", "type", "truth"]], on=["pilot_id", "claim_id"], how="inner")
df = df[df.truth.isin(["true", "false"])]  # irrelevant excluded, matches prior tables

# grouping variant: entity folded into detail (label only, for this table)
df["type_merged"] = df["type"].replace({"entity": "detail"})

def ci(vals, clusters, n_boot=1000, seed=0):
    vals = np.asarray(vals, float); clusters = np.asarray(clusters)
    if len(vals) == 0:
        return dict(mean=np.nan, lo=np.nan, hi=np.nan, n=0, k=0)
    k = int(len(np.unique(clusters)))
    uniq, inv = np.unique(clusters, return_inverse=True)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq))
        m_ = np.concatenate([np.flatnonzero(inv == p) for p in pick])
        boots.append(vals[m_].mean())
    return dict(mean=float(vals.mean()), lo=float(np.percentile(boots, 2.5)),
                hi=float(np.percentile(boots, 97.5)), n=int(len(vals)), k=k)

def fmt(c):
    return f"{c['mean']*100:.2f} [{c['lo']*100:.2f},{c['hi']*100:.2f}] (n={c['n']}, docs={c['k']})" if c["n"] else "n=0"

def auroc_ci(vals, labels, clusters, n_boot=1000, seed=0):
    vals = np.asarray(vals, float); labels = np.asarray(labels); clusters = np.asarray(clusters)
    def auc(v, l):
        pos, neg = v[l == "true"], v[l == "false"]
        if len(pos) == 0 or len(neg) == 0:
            return np.nan
        return float(np.mean(pos[:, None] > neg[None, :]) + 0.5 * np.mean(pos[:, None] == neg[None, :]))
    point = auc(vals, labels)
    uniq, inv = np.unique(clusters, return_inverse=True)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq))
        m_ = np.concatenate([np.flatnonzero(inv == p) for p in pick])
        a = auc(vals[m_], labels[m_])
        if not np.isnan(a):
            boots.append(a)
    if not boots:
        return dict(auc=point, lo=np.nan, hi=np.nan, n=len(vals))
    return dict(auc=point, lo=float(np.percentile(boots, 2.5)), hi=float(np.percentile(boots, 97.5)), n=len(vals))

for col, label in [("P_orig", "P_orig (deletion)"), ("P_heavy", "P_heavy (heavy paraphrase)")]:
    d = df.dropna(subset=[col])
    print(f"\n=== {label}, n={len(d)}, {d.pilot_id.nunique()} docs ===")
    print(f"{'type':22s} {'true':38s} {'false':38s} {'true-false':>10s}  {'AUROC':>28s}")
    for grouping, types in [("type", ["theme", "entity", "detail"]),
                             ("type_merged", ["theme", "detail"])]:
        tag = " (entity folded into detail)" if grouping == "type_merged" else ""
        for t in types:
            s = d[d[grouping] == t]
            ct = ci(s[s.truth == "true"][col], s[s.truth == "true"].pilot_id)
            cf = ci(s[s.truth == "false"][col], s[s.truth == "false"].pilot_id)
            a = auroc_ci(s[col].values, s.truth.values, s.pilot_id.values)
            gap = f"{(ct['mean']-cf['mean'])*100:.2f}" if ct["n"] and cf["n"] else "-"
            auc_str = f"{a['auc']:.3f} [{a['lo']:.3f},{a['hi']:.3f}]" if not np.isnan(a["auc"]) else "n/a"
            name = f"{t}{tag}" if t == "detail" and grouping == "type_merged" else t
            print(f"{name:22s} {fmt(ct):38s} {fmt(cf):38s} {gap:>10s}  {auc_str:>28s}")
        print()

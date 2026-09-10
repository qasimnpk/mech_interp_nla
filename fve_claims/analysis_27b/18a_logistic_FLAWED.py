"""Does combining P_orig and P_heavy discriminate true/false better than either alone?
Out-of-sample via document-grouped 5-fold CV (claims from one document never span train/test),
repeated over 20 seeds. Delta-AUROC CI by document-clustered bootstrap on out-of-fold predictions.
Also the in-sample nested likelihood-ratio test for reference."""
import glob, json, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from scipy import stats
warnings.filterwarnings("ignore")

import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
atoms = {}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r = json.loads(l); atoms[(r["pilot_id"], r["claim_id"])] = r
a = pd.DataFrame(atoms.values())
sc = pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
df = sc.merge(a[["pilot_id","claim_id","type","truth"]], on=["pilot_id","claim_id"], how="inner")
df = df[df.truth.isin(["true","false"])].dropna(subset=["P_orig","P_heavy"]).copy()
df["y"] = (df.truth == "true").astype(int)
df["type_merged"] = df["type"].replace({"entity":"detail"}); df["all"] = "all"

def auc(v, y):
    pos, neg = v[y==1], v[y==0]
    if len(pos)==0 or len(neg)==0: return np.nan
    return float(np.mean(pos[:,None] > neg[None,:]) + 0.5*np.mean(pos[:,None]==neg[None,:]))

def oof(sub, feats, seeds=20, folds=5):
    """mean out-of-fold predicted prob over seeds, so the AUROC is out-of-sample"""
    X, y, g = sub[feats].values, sub.y.values, sub.pilot_id.values
    acc = np.zeros(len(sub))
    for s in range(seeds):
        rng = np.random.default_rng(s)
        docs = np.unique(g); perm = {d:i for i,d in enumerate(rng.permutation(docs))}
        order = np.array([perm[x] for x in g])
        p = np.zeros(len(sub))
        for tr, te in GroupKFold(n_splits=folds).split(X, y, groups=order):
            if len(np.unique(y[tr])) < 2: p[te] = y[tr].mean(); continue
            m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
            m.fit(X[tr], y[tr]); p[te] = m.predict_proba(X[te])[:,1]
        acc += p
    return acc/seeds

def delta_ci(sub, pa, pb, n_boot=2000, seed=0):
    """document-clustered bootstrap of AUROC(b) - AUROC(a) on the same claims"""
    g = sub.pilot_id.values; y = sub.y.values
    uniq, inv = np.unique(g, return_inverse=True); rng = np.random.default_rng(seed); d = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(uniq), len(uniq))
        m = np.concatenate([np.flatnonzero(inv==p) for p in pick])
        x1, x2 = auc(pa[m], y[m]), auc(pb[m], y[m])
        if not (np.isnan(x1) or np.isnan(x2)): d.append(x2-x1)
    return float(np.percentile(d,2.5)), float(np.percentile(d,97.5))

print(f"corr(P_orig, P_heavy) overall = {df.P_orig.corr(df.P_heavy):.4f}")
print(f"corr within detail            = {df[df.type=='detail'].P_orig.corr(df[df.type=='detail'].P_heavy):.4f}")

for grouping, t, label in [("all","all","ALL claims"), ("type_merged","detail","detail+entity merged"),
                            ("type","detail","detail only"), ("type","entity","entity only")]:
    sub = df[df[grouping]==t]
    if sub.y.nunique() < 2 or len(sub) < 30: continue
    print(f"\n=== {label} (n={len(sub)}, {sub.pilot_id.nunique()} docs, {sub.y.sum()} true / {(1-sub.y).sum():.0f} false) ===")
    p1 = oof(sub, ["P_orig"]); p2 = oof(sub, ["P_heavy"]); p12 = oof(sub, ["P_orig","P_heavy"])
    a1, a2, a12 = auc(p1, sub.y.values), auc(p2, sub.y.values), auc(p12, sub.y.values)
    lo1, hi1 = delta_ci(sub, p1, p12); lo2, hi2 = delta_ci(sub, p2, p12)
    print(f"  out-of-sample AUROC  P_orig alone   {a1:.4f}")
    print(f"                       P_heavy alone  {a2:.4f}")
    print(f"                       both together  {a12:.4f}")
    print(f"  delta vs P_orig alone   {a12-a1:+.4f}  [{lo1:+.4f},{hi1:+.4f}]")
    print(f"  delta vs P_heavy alone  {a12-a2:+.4f}  [{lo2:+.4f},{hi2:+.4f}]")
    # in-sample nested LR test: does P_heavy add beyond P_orig?
    import statsmodels.api as sm
    Xs = StandardScaler().fit_transform(sub[["P_orig","P_heavy"]].values)
    m1 = sm.Logit(sub.y.values, sm.add_constant(Xs[:,[0]])).fit(disp=0)
    m2 = sm.Logit(sub.y.values, sm.add_constant(Xs)).fit(disp=0)
    lr = 2*(m2.llf - m1.llf); p = stats.chi2.sf(lr, 1)
    print(f"  in-sample LR test (P_heavy added to P_orig): chi2={lr:.2f}, p={p:.4f}"
          f"   coefs both-model: P_orig {m2.params[1]:+.3f}, P_heavy {m2.params[2]:+.3f}")

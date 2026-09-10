"""Corrected: AUROC computed WITHIN each held-out fold (predictions are only rank-comparable inside the
fold that produced them), then averaged over folds and 20 seeds. Paired delta computed fold-by-fold."""
import glob, json, warnings
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
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
df["y"]=(df.truth=="true").astype(int)
df["type_merged"]=df["type"].replace({"entity":"detail"}); df["all"]="all"
df["S_sens"]=df.fve_z - df.fve_heavy

def auc(v,y):
    pos,neg=v[y==1],v[y==0]
    if len(pos)==0 or len(neg)==0: return np.nan
    return float(np.mean(pos[:,None]>neg[None,:])+0.5*np.mean(pos[:,None]==neg[None,:]))

MODELS={"P_orig alone":["P_orig"],"P_heavy alone":["P_heavy"],
        "both (P_orig+P_heavy)":["P_orig","P_heavy"],
        "P_orig + S_sensitivity":["P_orig","S_sens"]}

for grouping,t,label in [("all","all","ALL claims"),("type_merged","detail","detail+entity merged"),
                          ("type","detail","detail only")]:
    sub=df[df[grouping]==t]; y,g=sub.y.values, sub.pilot_id.values
    print(f"\n=== {label} (n={len(sub)}, {sub.pilot_id.nunique()} docs) ===")
    print(f"  raw feature AUROC (no model): P_orig {auc(sub.P_orig.values,y):.4f}  P_heavy {auc(sub.P_heavy.values,y):.4f}")
    per={k:[] for k in MODELS}; deltas=[]
    for s in range(20):
        rng=np.random.default_rng(s); docs=np.unique(g)
        perm={d:i for i,d in enumerate(rng.permutation(docs))}; order=np.array([perm[x] for x in g])
        for tr,te in GroupKFold(n_splits=5).split(sub[["P_orig"]].values,y,groups=order):
            if len(np.unique(y[tr]))<2 or len(np.unique(y[te]))<2: continue
            fold={}
            for name,feats in MODELS.items():
                X=sub[feats].values
                m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)).fit(X[tr],y[tr])
                v=m.predict_proba(X[te])[:,1]; A=auc(v,y[te])
                if not np.isnan(A): per[name].append(A); fold[name]=A
            if "both (P_orig+P_heavy)" in fold and "P_orig alone" in fold:
                deltas.append(fold["both (P_orig+P_heavy)"]-fold["P_orig alone"])
    for name in MODELS:
        v=np.array(per[name]); print(f"  held-out fold AUROC  {name:24s} {v.mean():.4f}  (sd across folds {v.std():.3f}, {len(v)} folds)")
    d=np.array(deltas)
    lo,hi=np.percentile(d,2.5),np.percentile(d,97.5)
    print(f"  delta (both - P_orig alone), per fold: mean {d.mean():+.4f}, 95% of folds in [{lo:+.4f},{hi:+.4f}], "
          f"frac folds improved {np.mean(d>0):.2f}")

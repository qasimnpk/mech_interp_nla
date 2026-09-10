"""Why are the OOF AUROCs below 0.5? Check fold-to-fold coefficient sign stability and compare against
the raw-feature AUROC on the identical samples."""
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
df["y"] = (df.truth=="true").astype(int)
df["type_merged"] = df["type"].replace({"entity":"detail"}); df["all"]="all"

def auc(v,y):
    pos,neg = v[y==1], v[y==0]
    return float(np.mean(pos[:,None]>neg[None,:]) + 0.5*np.mean(pos[:,None]==neg[None,:]))

for grouping,t,label in [("all","all","ALL"),("type_merged","detail","detail+entity"),("type","detail","detail")]:
    sub = df[df[grouping]==t]
    y,g = sub.y.values, sub.pilot_id.values
    print(f"\n=== {label} (n={len(sub)}) ===")
    print(f"  raw-feature AUROC  P_orig {auc(sub.P_orig.values,y):.4f}   P_heavy {auc(sub.P_heavy.values,y):.4f}")
    signs = {"P_orig":[], "both_Porig":[], "both_Pheavy":[]}
    for s in range(20):
        rng = np.random.default_rng(s); docs=np.unique(g)
        perm={d:i for i,d in enumerate(rng.permutation(docs))}; order=np.array([perm[x] for x in g])
        for tr,te in GroupKFold(n_splits=5).split(sub[["P_orig"]].values,y,groups=order):
            m1=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)).fit(sub[["P_orig"]].values[tr],y[tr])
            m2=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)).fit(sub[["P_orig","P_heavy"]].values[tr],y[tr])
            signs["P_orig"].append(m1[-1].coef_[0][0])
            signs["both_Porig"].append(m2[-1].coef_[0][0]); signs["both_Pheavy"].append(m2[-1].coef_[0][1])
    for k,v in signs.items():
        v=np.array(v)
        print(f"  {k:12s} coef across 100 folds: mean {v.mean():+.3f}, frac positive {np.mean(v>0):.2f}, "
              f"min {v.min():+.2f}, max {v.max():+.2f}")

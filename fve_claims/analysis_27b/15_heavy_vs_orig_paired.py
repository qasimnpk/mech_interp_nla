"""Is P_heavy's within-document true-false gap genuinely larger than P_orig's? Compare them PAIRED
(same documents, same claims), not by overlapping CIs. Per document d:
  D_orig(d)  = mean(P_orig | true,d)  - mean(P_orig | false,d)
  D_heavy(d) = mean(P_heavy| true,d)  - mean(P_heavy| false,d)
  delta(d)   = D_heavy(d) - D_orig(d)
Note delta(d) == -[mean(S_sens|true,d) - mean(S_sens|false,d)] since P_orig - P_heavy = S_sensitivity."""
import glob, json
import numpy as np, pandas as pd
from scipy import stats

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
df["type_merged"]=df["type"].replace({"entity":"detail"}); df["all"]="all"

def boot(v,n=5000,seed=0):
    v=np.asarray(v,float); rng=np.random.default_rng(seed)
    b=[v[rng.integers(0,len(v),len(v))].mean() for _ in range(n)]
    return float(np.percentile(b,2.5)), float(np.percentile(b,97.5))

print(f"{'category':22s} {'docs':>5s} {'D_orig':>8s} {'D_heavy':>8s} {'delta=H-O':>10s} "
      f"{'delta 95% CI':>20s} {'paired p':>9s} {'docs H>O':>9s}")
for grouping,t in [("type","theme"),("type","entity"),("type","detail"),("type_merged","detail"),("all","all")]:
    sub=df[df[grouping]==t]
    rows=[]
    for pid,g in sub.groupby("pilot_id"):
        tt,ff = g[g.truth=="true"], g[g.truth=="false"]
        if len(tt) and len(ff):
            rows.append((tt.P_orig.mean()-ff.P_orig.mean(), tt.P_heavy.mean()-ff.P_heavy.mean()))
    if not rows: continue
    D=np.array(rows); do,dh = D[:,0], D[:,1]; delta = dh-do
    lo,hi = boot(delta)
    p = stats.wilcoxon(delta).pvalue if len(delta)>5 else np.nan
    name = "detail+entity merged" if (grouping=="type_merged" and t=="detail") else t
    print(f"{name:22s} {len(D):>5d} {do.mean()*100:>8.2f} {dh.mean()*100:>8.2f} {delta.mean()*100:>10.2f} "
          f"{f'[{lo*100:.2f},{hi*100:.2f}]':>20s} {p:>9.4f} {f'{np.mean(delta>0)*100:.0f}%':>9s}")

print("\n--- what drives the merged/all rows: per-document delta decomposed by which claims enter ---")
sub=df[df.type_merged=="detail"]
big=[]
for pid,g in sub.groupby("pilot_id"):
    tt,ff=g[g.truth=="true"],g[g.truth=="false"]
    if len(tt) and len(ff):
        d=(tt.P_heavy.mean()-ff.P_heavy.mean())-(tt.P_orig.mean()-ff.P_orig.mean())
        big.append((pid,d*100,len(tt),len(ff),int((g.type=="entity").sum())))
b=pd.DataFrame(big,columns=["pilot_id","delta_pp","n_true","n_false","n_entity"]).sort_values("delta_pp")
print("most negative 5:"); print(b.head(5).to_string(index=False))
print("most positive 5:"); print(b.tail(5).to_string(index=False))
print(f"\nmedian delta {b.delta_pp.median():.3f} pp, mean {b.delta_pp.mean():.3f} pp, "
      f"|delta|>1pp in {int((b.delta_pp.abs()>1).sum())}/{len(b)} docs")

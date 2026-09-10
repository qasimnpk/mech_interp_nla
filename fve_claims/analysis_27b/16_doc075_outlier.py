import glob, json
import numpy as np, pandas as pd
import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
atoms={}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r=json.loads(l); atoms[(r["pilot_id"],r["claim_id"])]=r
a=pd.DataFrame(atoms.values())
sc=pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
df=sc.merge(a[["pilot_id","claim_id","type","truth","proposition"]],on=["pilot_id","claim_id"],how="inner")
df=df[df.truth.isin(["true","false"])].dropna(subset=["P_orig","P_heavy"]).copy()
df["type_merged"]=df["type"].replace({"entity":"detail"}); df["all"]="all"

print("=== doc 75, all scored claims ===")
d=df[df.pilot_id==75][["claim_id","type","truth","fve_z","fve_del","fve_heavy","P_orig","P_heavy"]]
pd.set_option("display.width",200)
print(d.to_string(index=False, float_format=lambda x: f"{x*100:8.2f}" if abs(x)<10 else f"{x:8.2f}"))

def boot(v,n=5000,seed=0):
    v=np.asarray(v,float); rng=np.random.default_rng(seed)
    b=[v[rng.integers(0,len(v),len(v))].mean() for _ in range(n)]
    return float(np.percentile(b,2.5)),float(np.percentile(b,97.5))

print("\n=== within-doc gaps, WITH vs WITHOUT doc 75 ===")
for grouping,t in [("type_merged","detail"),("all","all")]:
    for drop in [False,True]:
        sub=df[df[grouping]==t]
        if drop: sub=sub[sub.pilot_id!=75]
        do,dh=[],[]
        for pid,g in sub.groupby("pilot_id"):
            tt,ff=g[g.truth=="true"],g[g.truth=="false"]
            if len(tt) and len(ff):
                do.append(tt.P_orig.mean()-ff.P_orig.mean()); dh.append(tt.P_heavy.mean()-ff.P_heavy.mean())
        do,dh=np.array(do),np.array(dh)
        lo_o,hi_o=boot(do); lo_h,hi_h=boot(dh)
        name="detail+entity merged" if t=="detail" else "all"
        print(f"  {name:22s} {'without doc75' if drop else 'with doc75   '}  docs={len(do):3d}  "
              f"P_orig {do.mean()*100:6.2f} [{lo_o*100:6.2f},{hi_o*100:6.2f}]   "
              f"P_heavy {dh.mean()*100:6.2f} [{lo_h*100:6.2f},{hi_h*100:6.2f}]")

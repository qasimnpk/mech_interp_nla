"""Average the two cosine drops per claim, convert with the same global D, call it FVE.
Check (1) whether this differs from averaging the FVE-based P scores, (2) how it scores,
(3) the genuinely different variant: use heavy paraphrase as a SECOND baseline instead."""
import glob, json
import numpy as np, pandas as pd
from scipy import stats

import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=0.3708867995284306
atoms={}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r=json.loads(l); atoms[(r["pilot_id"],r["claim_id"])]=r
a=pd.DataFrame(atoms.values())
sc=pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
df=sc.merge(a[["pilot_id","claim_id","type","truth"]],on=["pilot_id","claim_id"],how="inner")
df=df[df.truth.isin(["true","false"])].dropna(subset=["P_orig","P_heavy","cos_heavy"]).copy()
df["type_merged"]=df["type"].replace({"entity":"detail"}); df["all"]="all"

# --- the user's construction, done literally in cosine space ---
dcos_del   = df.cos_z    - df.cos_del      # cosine drop from deleting
dcos_heavy = df.cos_heavy - df.cos_del     # cosine drop from heavy paraphrase (vs same baseline)
avg_dcos   = (dcos_del + dcos_heavy)/2
df["P_avgcos"] = (2/D)*avg_dcos            # convert with the same dumb-baseline denominator

# --- averaging the FVE-based P scores instead ---
df["P_avgfve"] = (df.P_orig + df.P_heavy)/2

print("(1) Is 'average cosines then convert' different from 'convert then average'?")
print(f"    max |P_avgcos - P_avgfve| = {np.abs(df.P_avgcos-df.P_avgfve).max():.3e}   -> identical\n")

# --- genuinely different variant: heavy as a SECOND baseline ---
df["P_twobase"] = (2/D)*(df.cos_z - (df.cos_del + df.cos_heavy)/2)
print("(2) A variant that is NOT the same thing: treat heavy paraphrase as a second baseline,")
print("    i.e. compare the intact explanation against mean(cos_del, cos_heavy).")
print(f"    equals (P_orig + S_sensitivity)/2 : max diff "
      f"{np.abs(df.P_twobase - (df.P_orig + (df.fve_z-df.fve_heavy))/2).max():.3e}\n")

def auc(v,y):
    pos,neg=v[y==1],v[y==0]
    if len(pos)==0 or len(neg)==0: return np.nan
    return float(np.mean(pos[:,None]>neg[None,:])+0.5*np.mean(pos[:,None]==neg[None,:]))
def auc_ci(v,y,g,n=1000,seed=0):
    uniq,inv=np.unique(g,return_inverse=True); rng=np.random.default_rng(seed); b=[]
    for _ in range(n):
        pick=rng.integers(0,len(uniq),len(uniq)); m=np.concatenate([np.flatnonzero(inv==p) for p in pick])
        x=auc(v[m],y[m])
        if not np.isnan(x): b.append(x)
    return auc(v,y), float(np.percentile(b,2.5)), float(np.percentile(b,97.5))

y=(df.truth=="true").astype(int).values
print("(3) AUROC (document-clustered bootstrap):")
print(f"    {'stratum':22s} {'P_orig':>22s} {'P_heavy':>22s} {'P_avg (your idea)':>22s} {'P_twobase':>22s}")
for grouping,t in [("all","all"),("type_merged","detail"),("type","detail"),("type","entity")]:
    s=df[df[grouping]==t]; ys=(s.truth=="true").astype(int).values; g=s.pilot_id.values
    cells=[]
    for col in ["P_orig","P_heavy","P_avgcos","P_twobase"]:
        A,lo,hi=auc_ci(s[col].values,ys,g)
        cells.append(f"{A:.3f} [{lo:.3f},{hi:.3f}]")
    name="detail+entity" if (grouping=="type_merged" and t=="detail") else t
    print(f"    {name:22s} " + " ".join(f"{c:>22s}" for c in cells))

print("\n(4) within-document paired true-false gap (pp), bootstrap CI over docs:")
def boot(v,n=5000,seed=0):
    v=np.asarray(v,float); rng=np.random.default_rng(seed)
    b=[v[rng.integers(0,len(v),len(v))].mean() for _ in range(n)]
    return float(np.percentile(b,2.5)),float(np.percentile(b,97.5))
print(f"    {'stratum':22s} {'P_orig':>24s} {'P_avg (your idea)':>24s} {'P_twobase':>24s}")
for grouping,t in [("all","all"),("type_merged","detail"),("type","detail")]:
    s=df[df[grouping]==t]; cells=[]
    for col in ["P_orig","P_avgcos","P_twobase"]:
        diffs=[]
        for pid,g_ in s.groupby("pilot_id"):
            tt,ff=g_[g_.truth=="true"],g_[g_.truth=="false"]
            if len(tt) and len(ff): diffs.append(tt[col].mean()-ff[col].mean())
        diffs=np.array(diffs); lo,hi=boot(diffs)
        cells.append(f"{diffs.mean()*100:6.2f} [{lo*100:6.2f},{hi*100:6.2f}]")
    name="detail+entity" if (grouping=="type_merged" and t=="detail") else t
    print(f"    {name:22s} " + " ".join(f"{c:>24s}" for c in cells))

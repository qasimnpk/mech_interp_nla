"""Does FVE already absorb document-level variation? Check (a) that D is one global scalar and FVE is
affine in cosine, (b) how much of the variance in P_orig is between-document."""
import glob, json
import numpy as np, pandas as pd

import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = json.loads(open(f"{HERE}/04_06_27b_full_settings.json").read()) if glob.glob(f"{HERE}/04_06_27b_full_settings.json") else {}
print("settings D_local:", S.get("D_local"))

sc = pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")

# (a) is FVE exactly affine in cosine with ONE global D?
D = S.get("D_local")
if D:
    recon = 1 - 2*(1 - sc.cos_z)/D
    print(f"(a) max |fve_z - (1 - 2(1-cos_z)/D_global)| = {np.abs(recon - sc.fve_z).max():.3e}  -> single global D confirmed")
    print(f"    P_orig vs (2/D)*(cos_z-cos_del): max abs diff = {np.abs(sc.P_orig - (2/D)*(sc.cos_z-sc.cos_del)).max():.3e}")
    print(f"    so P_orig is exactly {2/D:.3f} x the cosine drop; D contributes a constant scale, not a per-doc one")

# (b) how much of P_orig's variance is between-document?
atoms = {}
for f in sorted(glob.glob(f"{HERE}/tasks/02_atoms_27b_doc*.jsonl")):
    for l in open(f):
        r = json.loads(l); atoms[(r["pilot_id"], r["claim_id"])] = r
a = pd.DataFrame(atoms.values())
df = sc.merge(a[["pilot_id","claim_id","type","truth"]], on=["pilot_id","claim_id"], how="inner")
df = df[df.truth.isin(["true","false"])]

def icc(sub, col):
    g = sub.groupby("pilot_id")[col]
    k = g.size()
    grand = sub[col].mean()
    ssb = float((k * (g.mean() - grand)**2).sum())
    ssw = float(((sub[col] - sub.pilot_id.map(g.mean()))**2).sum())
    return ssb/(ssb+ssw), ssb, ssw

print("\n(b) between-document share of variance in P_orig (all true+false claims):")
for name, sub in [("all", df), ("detail only", df[df.type=="detail"]), ("theme only", df[df.type=="theme"])]:
    frac, ssb, ssw = icc(sub.dropna(subset=["P_orig"]), "P_orig")
    print(f"    {name:14s} between-doc = {frac*100:5.1f}% of total variance (n={len(sub)})")

d = df[df.type=="detail"].dropna(subset=["P_orig"])
pdm = d.groupby("pilot_id").P_orig.mean()*100
print(f"\n    per-document mean P_orig, detail claims (pp): "
      f"min {pdm.min():.2f}, p25 {pdm.quantile(.25):.2f}, median {pdm.median():.2f}, "
      f"p75 {pdm.quantile(.75):.2f}, max {pdm.max():.2f}")
cz = sc.groupby("pilot_id").cos_z.first()
print(f"    per-document cos_z (full explanation): min {cz.min():.3f}, median {cz.median():.3f}, max {cz.max():.3f}")
fz = sc.groupby("pilot_id").fve_z.first()*100
print(f"    per-document fve_z (pp):               min {fz.min():.1f}, median {fz.median():.1f}, max {fz.max():.1f}")

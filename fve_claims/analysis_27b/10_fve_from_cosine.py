"""Walk the raw activation -> FVE chain on the real 27B data, checking each step numerically."""
import torch, numpy as np, pandas as pd
import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
acts={}
for f in ["acts_27b_25.pt","acts_27b_25_50.pt","acts_27b_50_100.pt"]:
    d=torch.load(f"{HERE}/out/{f}")
    for i,pid in enumerate(d["pilot_id"]): acts[int(pid)]=d["h"][i]
H=torch.stack([acts[i] for i in range(100)]).double()
d_model=H.shape[1]
print(f"STEP 1  raw activations: {H.shape[0]} documents x {d_model} dims (one vector per document)")
print(f"        raw norms ||h||: min {H.norm(dim=1).min():.1f}, median {H.norm(dim=1).median():.1f}, max {H.norm(dim=1).max():.1f}")
print(f"        -> norms vary a lot, so we normalize before measuring spread\n")

Hn = H / H.norm(dim=1,keepdim=True) * (d_model**0.5)
print(f"STEP 2  normalize every vector to the same length sqrt(d)={d_model**0.5:.2f}")
print(f"        all norms now: {Hn.norm(dim=1).min():.3f} .. {Hn.norm(dim=1).max():.3f}  (per-dim squared length = 1.0)\n")

mean_vec = Hn.mean(0)
D = float(((Hn-mean_vec)**2).sum(1).mean()/d_model)
print(f"STEP 3  D = average squared distance from the mean activation, per dimension")
print(f"        D_local = {D:.4f}")
print(f"        sanity: ||mean_vec||^2/d = {float((mean_vec**2).sum()/d_model):.4f}, and D + that = {D + float((mean_vec**2).sum()/d_model):.4f} (should be 1.0)")
print(f"        -> D<1 because all 100 activations share a big common direction (residual-stream anisotropy).")
print(f"           Only {D*100:.0f}% of each vector's length is 'what makes this document different'.\n")

print(f"STEP 4  the AR predicts h_hat from the TEXT alone. We score it with cosine similarity.")
print(f"        If h and h_hat are both length L, then squared error = 2*L^2*(1-cos).")
print(f"        Per dimension (L^2=d): squared error = 2*(1-cos)\n")

print(f"STEP 5  FVE = 1 - (error) / (spread) = 1 - 2*(1-cos)/D")
print(f"        with D={D:.4f}: FVE = 1 - {2/D:.3f}*(1-cos)\n")

sc=pd.read_csv(f"{HERE}/04_06_scores_27b_full.csv")
row=sc[sc.pilot_id==0].iloc[0]
c=row.cos_z; hand=1-2*(1-c)/D
print(f"CHECK   document 0: cos_z = {c:.6f}")
print(f"        by hand 1 - 2*(1-{c:.4f})/{D:.4f} = {hand:.6f}")
print(f"        stored fve_z                      = {row.fve_z:.6f}   diff {abs(hand-row.fve_z):.2e}\n")

print("WHAT THE NUMBERS MEAN")
for c_ in [1.0, 0.9722, 0.945, 0.90, 0.8146, 0.70]:
    f_=1-2*(1-c_)/D
    tag = {1.0:"perfect reconstruction", 0.945:"median doc here"}.get(c_,"")
    if abs(f_)<1e-9 or (c_==0.8146): tag="FVE=0: no better than guessing the average activation"
    print(f"        cos {c_:.4f} -> FVE {f_*100:7.2f}%   {tag}")
print(f"\n        break-even cosine (FVE=0) is cos = 1 - D/2 = {1-D/2:.4f}")
print(f"        so on this dataset you need cos > {1-D/2:.3f} just to beat the trivial mean baseline.")
print(f"        doc 75 after deleting claim 6 scored FVE = -51%: its reconstruction was WORSE")
print(f"        than predicting the dataset-average activation.")

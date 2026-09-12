"""Headline table: mean FVE before and after deletion and heavy paraphrase, by claim truth, both models, all claim types
(irrelevant excluded), local FVE denominators. Then, per drop, true − false with a document-bootstrap 95% CI and the
number of documents where true > false. Run from the repo root."""
import glob, json
import numpy as np, pandas as pd
from scipy import stats

SEED, DRAWS = 0, 2000


def labels(patterns):
    recs = {}
    for pat in patterns:
        for f in sorted(glob.glob(pat)):
            for l in open(f):
                r = json.loads(l); recs[(r["pilot_id"], r["claim_id"])] = r
    return pd.DataFrame(recs.values())[["pilot_id", "claim_id", "truth", "type"]]


def load_27b():
    s = pd.read_csv("fve_claims/04_06_scores_27b_full.csv").merge(labels(["fve_claims/tasks/02_atoms_27b_doc*.jsonl"]), on=["pilot_id", "claim_id"])
    return s.assign(z=s.fve_z, dl=s.fve_del, hv=s.fve_heavy)


def load_7b():
    s = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("fve_claims/04_scores_7b_b*.csv"))])
    s = s.merge(pd.read_csv("fve_claims/06_scores_7b_paraphrase.csv")[["pilot_id", "claim_id", "fve_heavy_local"]], on=["pilot_id", "claim_id"])
    s = s.merge(labels(["fve_claims/tasks/02_atoms_7b_doc*.jsonl"]), on=["pilot_id", "claim_id"])
    return s.assign(z=s.fve_z_local, dl=s.fve_del_local, hv=s.fve_heavy_local)


for name, s in [("7B", load_7b()), ("27B", load_27b())]:
    s = s[s.truth.isin(["true", "false"])].sort_values(["pilot_id", "claim_id"])
    s = s.assign(deletion=s.z - s.dl, paraphrase=s.z - s.hv)
    t = (s.groupby("truth")[["z", "dl", "hv", "deletion", "paraphrase"]].mean() * 100).round(3)
    t.insert(0, "n", s.truth.value_counts())
    t.columns = ["n", "original FVE %", "after deletion %", "after heavy paraphrase %", "deletion drop pp", "paraphrase drop pp"]
    print(f"=== {name} ===\n{t.loc[['true', 'false']].to_string()}")
    docs = np.sort(s.pilot_id.unique()); by_doc = {d: g for d, g in s.groupby("pilot_id")}
    rng = np.random.default_rng(SEED)
    for col in ["deletion", "paraphrase"]:
        diff = lambda d: (d[d.truth == "true"][col].mean() - d[d.truth == "false"][col].mean()) * 100
        boots = [diff(pd.concat([by_doc[d] for d in rng.choice(docs, len(docs))])) for _ in range(DRAWS)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        w = s.groupby(["pilot_id", "truth"])[col].mean().unstack().dropna()
        k, lower = int((w["true"] > w["false"]).sum()), int((w["true"] < w["false"]).sum())
        ties = len(w) - k - lower  # identical scores (e.g. one heavy paraphrase shared by several claims) are left out of the sign test
        print(f"  {col:10s} true − false {diff(s):6.3f} pp, document-bootstrap 95% CI [{lo:.2f}, {hi:.2f}]; "
              f"documents with true > false {k}/{k + lower}, ties {ties} (sign test p {stats.binomtest(k, k + lower).pvalue:.2g})")

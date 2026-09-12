"""Per-claim AUROC of the deletion and paraphrase drops (true vs false) with document-cluster
bootstrap CIs, and the deletion drop split by whether the claim touches the verbalizer's final
sentence. Re-derives findings 1 and 2 of the README from the scored CSVs and the claim labels.
The 7B final_sentence tag comes from 07_tag_final_sentence.py; the 27B tag is recomputed here the
same way (max av_spans sentence_id == last sentence of the explanation). Run from the repo root."""
import sys, glob, json
sys.path.insert(0, "fve_claims")
import numpy as np, pandas as pd
from atomic import sentence_spans

SEED, DRAWS = 0, 4000

def labels(patterns, extra=()):
    recs = {}
    for pat in patterns:
        for f in sorted(glob.glob(pat)):
            for l in open(f):
                r = json.loads(l); recs[(r["pilot_id"], r["claim_id"])] = r
    df = pd.DataFrame(recs.values())
    keep = ["pilot_id", "claim_id", "truth", "type", "av_spans"] + list(extra)
    return df[[c for c in keep if c in df.columns]]

def load_27b():
    s = pd.read_csv("fve_claims/04_06_scores_27b_full.csv").merge(
        labels(["fve_claims/tasks/02_atoms_27b_doc*.jsonl"]), on=["pilot_id", "claim_id"])
    return s.assign(z=s.fve_z, dl=s.fve_del, hv=s.fve_heavy), "fve_claims/01_av_27b_*.jsonl"

def load_7b():
    s = pd.concat([pd.read_csv(f) for f in sorted(glob.glob("fve_claims/04_scores_7b_b*.csv"))])
    s = s.merge(pd.read_csv("fve_claims/06_scores_7b_paraphrase.csv")[["pilot_id","claim_id","fve_heavy_local"]],
                on=["pilot_id","claim_id"])
    s = s.merge(labels(["fve_claims/tasks/02_atoms_7b_doc*.jsonl"], extra=["final_sentence"]),
                on=["pilot_id","claim_id"])
    return s.assign(z=s.fve_z_local, dl=s.fve_del_local, hv=s.fve_heavy_local), "fve_claims/01_av_7b.jsonl"

def nsents(pat):
    out = {}
    for f in sorted(glob.glob(pat)):
        for l in open(f):
            g = json.loads(l)
            z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
            out[g["pilot_id"]] = len(sentence_spans(z))
    return out

def auroc(pos, neg):
    """Mann-Whitney AUROC with ties at 0.5."""
    if len(pos) == 0 or len(neg) == 0: return np.nan
    allv = np.concatenate([pos, neg])
    r = pd.Series(allv).rank().values
    return (r[:len(pos)].sum() - len(pos)*(len(pos)+1)/2) / (len(pos)*len(neg))

for name, (s, avpat) in [("7B", load_7b()), ("27B", load_27b())]:
    s = s[s.truth.isin(["true","false"])].copy()
    if "final_sentence" not in s.columns:
        ns = nsents(avpat)
        s["final_sentence"] = [max(x["sentence_id"] for x in sp) == ns[p]-1
                               for p, sp in zip(s.pilot_id, s.av_spans)]
    s["deletion"] = s.z - s.dl
    s["paraphrase"] = s.z - s.hv
    docs = np.sort(s.pilot_id.unique()); by_doc = {d: g for d, g in s.groupby("pilot_id")}
    print(f"\n=== {name} ===  n={len(s)}  ({(s.truth=='true').sum()} true / {(s.truth=='false').sum()} false)")
    for col in ["deletion", "paraphrase"]:
        f = lambda d: auroc(d[d.truth=="true"][col].values, d[d.truth=="false"][col].values)
        rng = np.random.default_rng(SEED)
        boots = np.array([f(pd.concat([by_doc[d] for d in rng.choice(docs, len(docs))])) for _ in range(DRAWS)])
        boots = boots[~np.isnan(boots)]
        lo, hi = np.percentile(boots, [2.5, 97.5])
        print(f"  AUROC({col:10s}) = {f(s):.4f}   document-bootstrap 95% CI [{lo:.3f}, {hi:.3f}]   "
              f"P(boot<=0.5) = {(boots<=0.5).mean():.3f}")
    # final-sentence split
    print("  --- deletion drop pp by position ---")
    for fs_flag, lab in [(True, "final sentence"), (False, "elsewhere")]:
        g = s[s.final_sentence == fs_flag]
        t, fa = g[g.truth=="true"].deletion*100, g[g.truth=="false"].deletion*100
        rng = np.random.default_rng(SEED)
        gd = np.sort(g.pilot_id.unique()); gby = {d: gg for d, gg in g.groupby("pilot_id")}
        dboot = []
        for _ in range(DRAWS):
            b = pd.concat([gby[d] for d in rng.choice(gd, len(gd))])
            bt, bf = b[b.truth=="true"].deletion, b[b.truth=="false"].deletion
            if len(bt) and len(bf): dboot.append((bt.mean()-bf.mean())*100)
        lo, hi = np.percentile(dboot, [2.5, 97.5])
        print(f"    {lab:15s} n={len(g):4d}  true {t.mean():7.3f} (n={len(t)})  false {fa.mean():7.3f} (n={len(fa)})  "
              f"diff {t.mean()-fa.mean():7.3f} pp  CI [{lo:.2f}, {hi:.2f}]")

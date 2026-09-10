"""Step 4 (atomic-v1, truth v2): AR scores for every explanation z and for every per-claim deletion rewrite z\\c
(tasks/04_rewrites_7b_doc*.jsonl, reviewed minimal edits). FVE = 1 − 2(1 − cos)/D under D_released (0.7335) and D_local
(per-element variance of the √d-normalised pilot activations). Writes 04_scores_7b.csv (one row per claim) and 04_expl_7b.csv.
Resume-safe via an AR prediction cache keyed by text hash (out/ar_cache_7b.npz)."""
import argparse, csv, glob, hashlib, json
import numpy as np
from common import *

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=100); a = ap.parse_args()
    doc_range = range(a.start, a.end)
    A = np.load(OUT / "acts_7b.npz"); acts = {int(i): A["h20"][k] for k, i in enumerate(A["pilot_id"])}
    H = A["h20"].astype(np.float64); d = H.shape[1]
    Hn = H / np.linalg.norm(H, axis=1, keepdims=True) * np.sqrt(d)
    D_local = float(((Hn - Hn.mean(0)) ** 2).sum(1).mean() / d)
    gens = {g["pilot_id"]: g for g in read_jsonl(HERE / "01_av_7b.jsonl")}
    all_rewrites = [json.loads(l) for f in sorted(glob.glob(str(HERE / "tasks/04_rewrites_7b_doc*.jsonl"))) for l in open(f) if json.loads(l)["pilot_id"] in doc_range]
    rewrites = [r for r in all_rewrites if r.get("removes_claim") is True and r.get("preserves_other_propositions") is True]
    n_excluded_nested = len(all_rewrites) - len(rewrites)
    S = settings(f"04_b{a.start}_{a.end}", model="7b", doc_range=[a.start, a.end], D_released=FVE_DENOM_RELEASED_7B, D_local=D_local, fve="1 - 2(1-cos)/D", n_rewrites=len(rewrites), n_rewrites_total=len(all_rewrites), n_excluded_nested=n_excluded_nested,
                 deletion="reviewed manual minimal edit per atomic claim (tasks/04_rewrites_7b_doc*.jsonl)")
    cache_p = OUT / "ar_cache_7b.npz"
    cache = {k: v for k, v in np.load(cache_p).items()} if cache_p.exists() else {}
    ar = L.AR()
    def pred(text):
        k = hashlib.sha256(text.encode()).hexdigest()
        if k not in cache: cache[k] = ar.predict(text).numpy()
        return cache[k]
    expl_rows = []
    for pid, g in sorted(gens.items()):
        if pid not in doc_range: continue
        z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        c = L.cos(pred(z), acts[pid])
        expl_rows.append({"pilot_id": pid, "split": g["split"], "cos_z": c, "fve_z_released": fve(c, FVE_DENOM_RELEASED_7B), "fve_z_local": fve(c, D_local), "n_chars": len(z)})
    out = []
    for r in rewrites:
        pid = r["pilot_id"]; g = gens[pid]; z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        assert r["original_explanation"] == z, (pid, r["claim_id"])
        h = acts[pid]; cz = L.cos(pred(z), h); cd = L.cos(pred(r["deleted_text"]), h)
        rec = {"pilot_id": pid, "claim_id": r["claim_id"], "split": g["split"], "reviewer": r.get("reviewer"), "preserves_other": r.get("preserves_other_propositions"),
               "cos_z": cz, "cos_del": cd, "d_cos": cz - cd}
        for name, D in (("released", FVE_DENOM_RELEASED_7B), ("local", D_local)):
            rec[f"fve_z_{name}"] = fve(cz, D); rec[f"fve_del_{name}"] = fve(cd, D); rec[f"fve_drop_{name}"] = fve(cz, D) - fve(cd, D)
        out.append(rec)
        if len(out) % 100 == 0:
            L.log(f"{len(out)}/{len(rewrites)} scored"); np.savez(cache_p, **cache)
    ar.free(); np.savez(cache_p, **cache)
    with open(HERE / f"04_scores_7b_b{a.start}_{a.end}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    with open(HERE / f"04_expl_7b_b{a.start}_{a.end}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(expl_rows[0])); w.writeheader(); w.writerows(expl_rows)
    finish(f"04_b{a.start}_{a.end}", S, n_claims_scored=len(out), n_docs=len({r["pilot_id"] for r in out}), ar_forwards=ar.n_forward,
           fve_z_released_mean=float(np.mean([r["fve_z_released"] for r in expl_rows])), fve_z_local_mean=float(np.mean([r["fve_z_local"] for r in expl_rows])))
    print("04 DONE", len(out), "claims;", len({r["pilot_id"] for r in out}), "docs; D_local", round(D_local, 4))

if __name__ == "__main__":
    main()

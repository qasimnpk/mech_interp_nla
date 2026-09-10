"""Paraphrase-averaged deletion score. For every claim with light_text and heavy_text (docs 0-49), AR-score both
variants and compute, against the SAME deletion baseline already in 04_scores_7b_b*.csv:
  P_orig  = fve(z)       - fve(z_del)
  P_light = fve(z_light) - fve(z_del)
  P_heavy = fve(z_heavy) - fve(z_del)
  P_avg   = mean(P_orig, P_light, P_heavy)
Writes 06_scores_7b_paraphrase.csv (one row per claim, both denominators). Resumable via the shared AR prediction
cache (out/ar_cache_7b.npz)."""
import csv, glob, hashlib, json
import numpy as np
from common import *

def main():
    A = np.load(OUT / "acts_7b.npz"); acts = {int(i): A["h20"][k] for k, i in enumerate(A["pilot_id"])}
    H = A["h20"].astype(np.float64); d = H.shape[1]
    Hn = H / np.linalg.norm(H, axis=1, keepdims=True) * np.sqrt(d)
    D_local = float(((Hn - Hn.mean(0)) ** 2).sum(1).mean() / d)
    Ds = {"released": FVE_DENOM_RELEASED_7B, "local": D_local}

    base = {}  # (pilot_id, claim_id) -> row from the baseline scores
    for f in sorted(glob.glob(str(HERE / "04_scores_7b_b*.csv"))):
        for r in csv.DictReader(open(f)):
            base[(int(r["pilot_id"]), int(r["claim_id"]))] = r

    rewrites = [json.loads(l) for i in range(0, 50) for l in open(HERE / f"tasks/04_rewrites_7b_doc{i:03d}.jsonl")]
    todo = [r for r in rewrites if r.get("light_text") and r.get("heavy_text")]
    S = settings("06", model="7b", n_candidates=len(rewrites), n_scored=len(todo), D=Ds,
                 formula="P_x = fve(z_x) - fve(z_del); P_avg = mean(P_orig, P_light, P_heavy)")

    cache_p = OUT / "ar_cache_7b.npz"
    cache = {k: v for k, v in np.load(cache_p).items()} if cache_p.exists() else {}
    ar = L.AR()
    def pred(text):
        k = hashlib.sha256(text.encode()).hexdigest()
        if k not in cache: cache[k] = ar.predict(text).numpy()
        return cache[k]

    out = []
    for i, r in enumerate(todo):
        pid, cid = r["pilot_id"], r["claim_id"]
        b = base.get((pid, cid))
        if b is None:
            continue  # claim excluded from baseline (overlap) -- skip paraphrase scoring too
        h = acts[pid]
        c_light = L.cos(pred(r["light_text"]), h)
        c_heavy = L.cos(pred(r["heavy_text"]), h)
        rec = {"pilot_id": pid, "claim_id": cid, "cos_z": float(b["cos_z"]), "cos_del": float(b["cos_del"]),
               "cos_light": c_light, "cos_heavy": c_heavy}
        for name, D in Ds.items():
            fz, fd = fve(rec["cos_z"], D), fve(rec["cos_del"], D)
            fl, fh = fve(c_light, D), fve(c_heavy, D)
            P_orig, P_light, P_heavy = fz - fd, fl - fd, fh - fd
            rec[f"fve_light_{name}"] = fl; rec[f"fve_heavy_{name}"] = fh
            rec[f"P_orig_{name}"] = P_orig; rec[f"P_light_{name}"] = P_light; rec[f"P_heavy_{name}"] = P_heavy
            rec[f"P_avg_{name}"] = (P_orig + P_light + P_heavy) / 3
            rec[f"noise_light_{name}"] = fz - fl  # wording-only movement, for reference
            rec[f"noise_heavy_{name}"] = fz - fh
        out.append(rec)
        if (i + 1) % 100 == 0:
            L.log(f"{i+1}/{len(todo)} scored"); np.savez(cache_p, **cache)
    ar.free(); np.savez(cache_p, **cache)

    with open(HERE / "06_scores_7b_paraphrase.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    finish("06", S, n_written=len(out), ar_forwards=ar.n_forward)
    print("06 DONE", len(out), "claims scored (light+heavy); D_local", round(D_local, 4))

if __name__ == "__main__":
    main()

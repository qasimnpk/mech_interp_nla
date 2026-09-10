"""27B variant of 04_score.py: AR scores for every explanation and every per-claim deletion rewrite,
documents 0-24. No shipped FVE denominator for this model; cosine is primary, plus a locally-computed
denominator (variance of the 25 extracted activations, same convention as the 7B's D_local)."""
import csv, glob, hashlib, json
from pathlib import Path
import torch
from common_27b import AR, cos, settings, finish, log, OUT, HERE


def fve(c: float, D: float) -> float:
    return 1.0 - 2.0 * (1.0 - c) / D


def main():
    data = torch.load(OUT / "acts_27b_25.pt")
    acts = {pid: data["h"][i] for i, pid in enumerate(data["pilot_id"])}
    H = data["h"].double()
    Hn = H / H.norm(dim=1, keepdim=True) * (H.shape[1] ** 0.5)
    D_local = float(((Hn - Hn.mean(0)) ** 2).sum(1).mean() / H.shape[1])
    log(f"D_local (27B, 25 docs) = {D_local:.4f}")

    gens = {json.loads(l)["pilot_id"]: json.loads(l) for l in open(HERE / "01_av_27b_25.jsonl")}
    all_rewrites = [json.loads(l) for f in sorted(glob.glob(str(HERE / "tasks/04_rewrites_27b_doc*.jsonl"))) for l in open(f)]
    rewrites = [r for r in all_rewrites if r.get("removes_claim") is True and r.get("preserves_other_propositions") is True]
    n_excluded = len(all_rewrites) - len(rewrites)

    S = settings("04_27b", n_docs=25, D_local=D_local, n_rewrites=len(rewrites), n_rewrites_total=len(all_rewrites),
                 n_excluded_overlap=n_excluded, fve="1 - 2(1-cos)/D_local (cosine is primary; no shipped denominator)")

    cache_p = OUT / "ar_cache_27b.pt"
    cache = torch.load(cache_p) if cache_p.exists() else {}
    ar = AR()

    def pred(text: str) -> torch.Tensor:
        k = hashlib.sha256(text.encode()).hexdigest()
        if k not in cache:
            cache[k] = ar.predict(text)
        return cache[k]

    expl_rows = []
    for pid, g in sorted(gens.items()):
        z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        c = cos(pred(z), acts[pid])
        expl_rows.append({"pilot_id": pid, "split": g["split"], "cos_z": c, "fve_z": fve(c, D_local), "n_chars": len(z)})

    out = []
    for r in rewrites:
        pid = r["pilot_id"]
        g = gens[pid]
        z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        assert r["original_explanation"] == z, (pid, r["claim_id"])
        h = acts[pid]
        cz = cos(pred(z), h)
        cd = cos(pred(r["deleted_text"]), h)
        rec = {"pilot_id": pid, "claim_id": r["claim_id"], "cos_z": cz, "cos_del": cd, "d_cos": cz - cd,
               "fve_z": fve(cz, D_local), "fve_del": fve(cd, D_local), "fve_drop": fve(cz, D_local) - fve(cd, D_local)}
        out.append(rec)
        if len(out) % 50 == 0:
            log(f"{len(out)}/{len(rewrites)} scored")
            torch.save(cache, cache_p)
    torch.save(cache, cache_p)

    with open(HERE / "04_scores_27b_25.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    with open(HERE / "04_expl_27b_25.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(expl_rows[0])); w.writeheader(); w.writerows(expl_rows)

    finish("04_27b", S, n_claims_scored=len(out), n_docs=len({r["pilot_id"] for r in out}), ar_forwards=ar.n_forward,
           fve_z_mean=sum(r["fve_z"] for r in expl_rows) / len(expl_rows),
           cos_z_mean=sum(r["cos_z"] for r in expl_rows) / len(expl_rows))
    print(f"DONE {len(out)} claims scored across {len({r['pilot_id'] for r in out})} docs; D_local {D_local:.4f}")


if __name__ == "__main__":
    main()

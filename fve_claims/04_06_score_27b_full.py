"""27B full-dataset scoring, documents 0-99. Merges the three activation files, scores every explanation
(fve_z), every deletion rewrite (fve_del), and every heavy-paraphrase rewrite (fve_heavy) in one AR
loading pass. D_local computed once from all 100 activations (more stable than the 25-doc-only version
used earlier)."""
import csv, glob, hashlib, json
import torch
from common_27b import AR, cos, settings, finish, log, OUT, HERE


def fve(c: float, D: float) -> float:
    return 1.0 - 2.0 * (1.0 - c) / D


def main():
    acts = {}
    for f in ["acts_27b_25.pt", "acts_27b_25_50.pt", "acts_27b_50_100.pt"]:
        d = torch.load(OUT / f)
        for i, pid in enumerate(d["pilot_id"]):
            acts[int(pid)] = d["h"][i]
    assert len(acts) == 100, f"expected 100 activations, got {len(acts)}"
    H = torch.stack([acts[i] for i in range(100)]).double()
    Hn = H / H.norm(dim=1, keepdim=True) * (H.shape[1] ** 0.5)
    D_local = float(((Hn - Hn.mean(0)) ** 2).sum(1).mean() / H.shape[1])
    log(f"merged {len(acts)} activations; D_local (100 docs) = {D_local:.4f}")

    gens = {}
    for f in ["01_av_27b_25.jsonl", "01_av_27b_25_50.jsonl", "01_av_27b_50_100.jsonl"]:
        for l in open(HERE / f):
            g = json.loads(l)
            gens[g["pilot_id"]] = g
    assert len(gens) == 100, f"expected 100 explanations, got {len(gens)}"

    all_rewrites = [json.loads(l) for f in sorted(glob.glob(str(HERE / "tasks/04_rewrites_27b_doc*.jsonl"))) for l in open(f)]
    rewrites = [r for r in all_rewrites if r.get("removes_claim") is True and r.get("preserves_other_propositions") is True]
    n_excluded = len(all_rewrites) - len(rewrites)
    n_heavy = sum(1 for r in rewrites if r.get("heavy_text"))
    log(f"{len(all_rewrites)} total rewrites, {len(rewrites)} with clean deletion baseline, "
        f"{n_excluded} excluded (overlap), {n_heavy} with heavy_text")

    S = settings("04_06_27b_full", n_docs=100, D_local=D_local, n_rewrites_total=len(all_rewrites),
                 n_rewrites_scored=len(rewrites), n_excluded_overlap=n_excluded, n_heavy_scored=n_heavy,
                 fve="1 - 2(1-cos)/D_local; D_local from all 100 docs")

    cache_p = OUT / "ar_cache_27b_full.pt"
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
        expl_rows.append({"pilot_id": pid, "cos_z": c, "fve_z": fve(c, D_local), "n_chars": len(z)})

    out = []
    for i, r in enumerate(rewrites):
        pid, cid = r["pilot_id"], r["claim_id"]
        z = gens[pid]["explanation"] if gens[pid]["parse_ok"] else gens[pid]["raw_generation"]
        assert r["original_explanation"] == z, (pid, cid)
        h = acts[pid]
        cz = cos(pred(z), h)
        cd = cos(pred(r["deleted_text"]), h)
        rec = {"pilot_id": pid, "claim_id": cid, "cos_z": cz, "cos_del": cd,
               "fve_z": fve(cz, D_local), "fve_del": fve(cd, D_local), "P_orig": fve(cz, D_local) - fve(cd, D_local)}
        if r.get("heavy_text"):
            ch = cos(pred(r["heavy_text"]), h)
            rec["cos_heavy"] = ch
            rec["fve_heavy"] = fve(ch, D_local)
            rec["P_heavy"] = rec["fve_heavy"] - rec["fve_del"]
            rec["S_sensitivity"] = rec["fve_z"] - rec["fve_heavy"]
        out.append(rec)
        if (i + 1) % 100 == 0:
            log(f"{i+1}/{len(rewrites)} scored")
            torch.save(cache, cache_p)
    torch.save(cache, cache_p)

    fieldnames = sorted({k for r in out for k in r})
    with open(HERE / "04_06_scores_27b_full.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames); w.writeheader(); w.writerows(out)
    with open(HERE / "04_expl_27b_full.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(expl_rows[0])); w.writeheader(); w.writerows(expl_rows)

    finish("04_06_27b_full", S, n_claims_scored=len(out), n_docs=len({r["pilot_id"] for r in out}),
           n_with_heavy=sum(1 for r in out if "fve_heavy" in r), ar_forwards=ar.n_forward)
    print(f"DONE {len(out)} claims scored across {len({r['pilot_id'] for r in out})} docs; "
          f"{sum(1 for r in out if 'fve_heavy' in r)} with heavy; D_local {D_local:.4f}")


if __name__ == "__main__":
    main()

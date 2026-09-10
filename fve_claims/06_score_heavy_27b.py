"""27B heavy-paraphrase scoring, documents 0-24. Scores heavy_text against the same deletion baseline
already in 04_scores_27b_25.csv: P_orig = fve_z - fve_del, P_heavy = fve_heavy - fve_del, S_sensitivity =
fve_z - fve_heavy (signed). Only claims with a clean deletion score (same convention as the 7B pipeline)."""
import csv, glob, hashlib, json
import torch
from common_27b import AR, cos, settings, finish, log, OUT, HERE


def fve(c: float, D: float) -> float:
    return 1.0 - 2.0 * (1.0 - c) / D


def main():
    data = torch.load(OUT / "acts_27b_25.pt")
    acts = {pid: data["h"][i] for i, pid in enumerate(data["pilot_id"])}
    D_local = json.loads((HERE / "04_27b_settings.json").read_text())["D_local"]
    log(f"D_local (reused from deletion scoring) = {D_local:.4f}")

    base = {(int(r["pilot_id"]), int(r["claim_id"])): r for r in csv.DictReader(open(HERE / "04_scores_27b_25.csv"))}
    rewrites = [json.loads(l) for i in range(0, 25) for l in open(HERE / f"tasks/04_rewrites_27b_doc{i:03d}.jsonl")]
    todo = [r for r in rewrites if r.get("heavy_text") and (r["pilot_id"], r["claim_id"]) in base]
    S = settings("06_27b", n_candidates=len(rewrites), n_scored=len(todo), D_local=D_local,
                 formula="P_heavy = fve_heavy - fve_del; S_sensitivity = fve_z - fve_heavy")

    cache_p = OUT / "ar_cache_27b.pt"
    cache = torch.load(cache_p) if cache_p.exists() else {}
    ar = AR()

    def pred(text: str) -> torch.Tensor:
        k = hashlib.sha256(text.encode()).hexdigest()
        if k not in cache:
            cache[k] = ar.predict(text)
        return cache[k]

    out = []
    for i, r in enumerate(todo):
        pid, cid = r["pilot_id"], r["claim_id"]
        b = base[(pid, cid)]
        h = acts[pid]
        c_heavy = cos(pred(r["heavy_text"]), h)
        cz, cd = float(b["cos_z"]), float(b["cos_del"])
        fz, fd, fh = fve(cz, D_local), fve(cd, D_local), fve(c_heavy, D_local)
        out.append({
            "pilot_id": pid, "claim_id": cid, "cos_z": cz, "cos_del": cd, "cos_heavy": c_heavy,
            "fve_z": fz, "fve_del": fd, "fve_heavy": fh,
            "P_orig": fz - fd, "P_heavy": fh - fd, "S_sensitivity": fz - fh,
        })
        if (i + 1) % 50 == 0:
            log(f"{i+1}/{len(todo)} scored")
            torch.save(cache, cache_p)
    torch.save(cache, cache_p)

    with open(HERE / "06_scores_27b_25.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    finish("06_27b", S, n_written=len(out), ar_forwards=ar.n_forward)
    print(f"DONE {len(out)} claims scored (heavy paraphrase)")


if __name__ == "__main__":
    main()

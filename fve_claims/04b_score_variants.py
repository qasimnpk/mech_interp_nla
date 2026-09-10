"""Step 4b (second step of the plan): AR-score z_light / z_aggr per sentence from 03_texts_7b.jsonl and compute the three
penalties against the same deletion: P_orig = fve(z) − fve(z_del), P_light, P_aggr, and P_avg = mean of the available ones.
Reuses 04_scores_7b.csv for fve(z) and fve(z_del); writes 04b_scores_7b.csv."""
import csv, json
import numpy as np
from common import *

def main():
    raise SystemExit("Legacy sentence paraphrase experiment: disabled pending an atomic paraphrase protocol.")
    A = np.load(OUT / "acts_7b.npz"); acts = {int(i): A["h20"][k] for k, i in enumerate(A["pilot_id"])}
    base = {(r["pilot_id"], r["sent_no"]): r for r in csv.DictReader(open(HERE / "04_scores_7b.csv")) if r["deleted_ok"] == "True"}
    D = {k: json.loads((HERE / "04_settings.json").read_text())[f"D_{k}"] for k in ("released", "local")}
    texts = read_jsonl(HERE / "03_texts_7b.jsonl")
    S = settings("04b", n=len(texts), D=D)
    ar = L.AR(); out = []
    for t in texts:
        b = base.get((str(t["pilot_id"]), str(t["sent_no"])))
        if b is None: continue
        h = acts[t["pilot_id"]]
        rec = {"pilot_id": t["pilot_id"], "sent_no": t["sent_no"], "cos_z": float(b["cos_z"]), "cos_del": float(b["cos_del"])}
        for kind in ("light", "aggressive"):
            rec[f"cos_{kind}"] = L.cos(ar.predict(t[f"z_{kind}"]).numpy(), h) if t.get(f"z_{kind}") else np.nan
        for name, d in D.items():
            f0, fd = fve(rec["cos_z"], d), fve(rec["cos_del"], d)
            P = {"orig": f0 - fd}
            for kind in ("light", "aggressive"):
                P[kind] = (fve(rec[f"cos_{kind}"], d) - fd) if not np.isnan(rec[f"cos_{kind}"]) else np.nan
            rec.update({f"P_orig_{name}": P["orig"], f"P_light_{name}": P["light"], f"P_aggr_{name}": P["aggressive"],
                        f"P_avg_{name}": float(np.nanmean([P["orig"], P["light"], P["aggressive"]])),
                        f"noise_light_{name}": f0 - fve(rec["cos_light"], d) if not np.isnan(rec["cos_light"]) else np.nan,
                        f"noise_aggr_{name}": f0 - fve(rec["cos_aggressive"], d) if not np.isnan(rec["cos_aggressive"]) else np.nan})
        out.append(rec)
    ar.free()
    with open(HERE / "04b_scores_7b.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    finish("04b", S, n_scored=len(out), ar_forwards=ar.n_forward); print("04b DONE", len(out))

if __name__ == "__main__":
    main()

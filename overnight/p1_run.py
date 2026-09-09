"""P1 (round 5): greedy 7B AV explanation (200 new tokens, released prompt, marker embedding replaced at norm 150) for each of
the 8 activations; then AR scores: cos_own, cos_shuffled ((i+1) mod 8), cos_own_27b_text (the 27B explanation through the 7B AR)."""
import json, sys, time
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nla_lib as L

def main():
    src = Path(__file__).resolve().parents[1] / "notes/nla_setup/nla27b_smoke_examples_full.json"
    rows = json.loads(src.read_text())
    A = np.load(L.OVERNIGHT / "out/p0_acts.npz")["h20"]
    n = len(rows)
    S = L.Settings("p1", inputs=str(src), n=n, decoding="greedy", max_new_tokens=200, prompt="released AV template (nla_meta.yaml)",
                   injection="marker embedding replaced by vec rescaled to injection_scale", shuffled_control="(i+1) mod n")
    av = L.AV()
    S.update(injection_scale=av.scale, prompt_tokens=int(av.prompt(None)[0].shape[1]), marker_pos=int(av.prompt(None)[1]))
    gens = []
    with open(L.OVERNIGHT / "p1_av.jsonl", "w") as f:
        for i, r in enumerate(rows):
            g = av.verbalize(torch.from_numpy(A[i]), max_new_tokens=200)
            rec = {"idx": r["idx"], "doc_id": r["doc_id"], "explanation_7b": g["explanation"], "raw_generation": g["raw_generation"],
                   "parse_ok": g["parse_ok"], "cjk": g["cjk"], "gen_tokens": g["n_tokens"], "gen_s": round(g["gen_s"], 1)}
            gens.append(rec); f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            L.log(f"idx {r['idx']}: {g['n_tokens']} tok {g['gen_s']:.0f}s parse_ok={g['parse_ok']} cjk={g['cjk']}")
    av.free()
    ar = L.AR()
    out = []
    for i, r in enumerate(rows):
        z7 = gens[i]["explanation_7b"] if gens[i]["parse_ok"] else gens[i]["raw_generation"]
        p7 = ar.predict(z7).numpy()
        p27 = ar.predict(r["explanation"]).numpy()
        j = (i + 1) % n
        out.append({"idx": r["idx"], "cos_own": L.cos(p7, A[i]), "cos_shuffled": L.cos(p7, A[j]), "shuffled_partner": rows[j]["idx"],
                    "cos_own_27b_text": L.cos(p27, A[i]), "cos_shuffled_27b_text": L.cos(p27, A[j]),
                    "pred_norm": float(np.linalg.norm(p7)), "pred_norm_27b_text": float(np.linalg.norm(p27)),
                    "parse_ok": gens[i]["parse_ok"], "cjk": gens[i]["cjk"]})
    ar.free()
    import csv
    with open(L.OVERNIGHT / "p1_scores.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    diff = [o["cos_own"] - o["cos_shuffled"] for o in out]
    ci = L.cluster_bootstrap_mean(diff, [o["idx"] for o in out])
    outcome = L.outcome_ci_at_or_below(ci, 0.0, min_n=30)
    obs = (f"mean(cos_own − cos_shuffled)={ci['mean']:.4f} [{ci['lo']:.4f},{ci['hi']:.4f}] n={n} k={n}; "
           f"cos_own mean {np.mean([o['cos_own'] for o in out]):.4f}; cos_shuffled mean {np.mean([o['cos_shuffled'] for o in out]):.4f}; "
           f"cos_own_27b_text mean {np.mean([o['cos_own_27b_text'] for o in out]):.4f}; parse_ok {sum(o['parse_ok'] for o in out)}/{n}; cjk {sum(o['cjk'] for o in out)}/{n}")
    line = L.append_disconfirmation("P1", "P1", "CI95 (by example) of mean(cos_own − cos_shuffled) ≤ 0 → MET; > 0 → NOT MET; straddles or n < 30 → INCONCLUSIVE (n = 8 by design)",
                                    obs, outcome, "descriptive; n = 8 by design so INCONCLUSIVE by n is expected; never 'information absent'")
    S.finish(kill=line, ci=ci, outcome=outcome, ar_forwards=ar.n_forward)
    print("P1 DONE", outcome, obs)

if __name__ == "__main__":
    main()

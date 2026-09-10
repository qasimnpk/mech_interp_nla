"""Step 0: 7B TARGET activation (block 20 output, hidden_states[21]) at the pilot position for every pilot prefix.
Tokenization: raw prefix_text, no chat template, add_special_tokens=False (the round-1 convention). Asserts the token count
matches the pilot record. Writes out/acts_7b.npz (h20 [N, 3584], pilot_id) and 00_positions.csv."""
import csv, time
import numpy as np, torch
from common import *

def main():
    rows = load_pilot()
    S = settings("00", model="7b", n=len(rows), tokenization="raw text, no chat template, add_special_tokens=False", hidden_states_index=L.LAYER + 1)
    tgt = L.Target()
    acts, info = [], []
    for r in rows:
        ids = tgt.tok(r["prefix_text"], return_tensors="pt", add_special_tokens=False)["input_ids"]
        T = ids.shape[1]
        assert T == r["n_tokens_prefix"], (r["pilot_id"], T, r["n_tokens_prefix"])
        assert r["position"] == T - 1, (r["pilot_id"], r["position"], T)
        h = L.to_cpu_f32(tgt.hidden_states(ids)[L.LAYER + 1][0, -1])
        acts.append(h.numpy())
        info.append({"pilot_id": r["pilot_id"], "split": r["split"], "n_tokens": T, "position": T - 1, "last_token": tgt.tok.decode(ids[0, -1:]), "final_word": r["final_word"], "norm": round(float(h.norm()), 2)})
        L.log(f"pilot {r['pilot_id']}: {T} tok, last {info[-1]['last_token']!r}, norm {info[-1]['norm']}")
    tgt.free()
    A = np.stack(acts); assert np.isfinite(A).all()
    np.savez(OUT / "acts_7b.npz", h20=A, pilot_id=np.array([r["pilot_id"] for r in rows]))
    with open(HERE / "00_positions.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(info[0])); w.writeheader(); w.writerows(info)
    finish("00", S, n_done=len(info), norms_mean=float(np.linalg.norm(A, axis=1).mean()))
    print("00 DONE", len(info))

if __name__ == "__main__":
    main()

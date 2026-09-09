"""P0 (round 5): tokenize the 8 texts from the 27B smoke run with the TARGET tokenizer (raw text, no chat template,
add_special_tokens=False — the round-1 convention), extract hidden_states[21] at the LAST token, save out/p0_acts.npz."""
import json, sys, time
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nla_lib as L

def main():
    src = Path(__file__).resolve().parents[1] / "notes/nla_setup/nla27b_smoke_examples_full.json"
    rows = json.loads(src.read_text())
    S = L.Settings("p0", inputs=str(src), n_texts=len(rows), position="last token of source_text_full",
                   tokenization="raw text, no chat template, add_special_tokens=False", hidden_states_index=L.LAYER + 1)
    tgt = L.Target()
    acts, info = [], []
    for r in rows:
        ids = tgt.tok(r["source_text_full"], return_tensors="pt", add_special_tokens=False)["input_ids"]
        T = ids.shape[1]
        t0 = time.time()
        hs = tgt.hidden_states(ids)
        h = L.to_cpu_f32(hs[L.LAYER + 1][0, -1])
        acts.append(h.numpy())
        last_tok = tgt.tok.decode(ids[0, -1:])
        info.append({"idx": r["idx"], "doc_id": r["doc_id"], "n_tokens_7b": T, "n_raw_tokens_27b": r.get("n_raw_tokens"),
                     "last_token_str": last_tok, "norm": float(h.norm()), "ge_50": bool(T >= 50), "gt_2048": bool(T > 2048),
                     "fwd_s": round(time.time() - t0, 2)})
        L.log(f"idx {r['idx']}: {T} tok, last {last_tok!r}, norm {float(h.norm()):.1f}")
    tgt.free()
    A = np.stack(acts)
    assert A.shape == (len(rows), 3584) and np.isfinite(A).all()
    (L.OVERNIGHT / "out").mkdir(exist_ok=True)
    np.savez(L.OVERNIGHT / "out/p0_acts.npz", h20=A, idx=np.array([r["idx"] for r in rows]))
    (L.OVERNIGHT / "p0_tokens.json").write_text(json.dumps(info, indent=2, ensure_ascii=False))
    S.finish(tokens=info, gate="8 activations, finite norms: PASS", norms=[float(x) for x in np.linalg.norm(A, axis=1)])
    print("P0 DONE", [i["n_tokens_7b"] for i in info])

if __name__ == "__main__":
    main()

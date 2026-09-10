"""27B baseline, documents 0-24: extract block-42 activations from av_base, one greedy AV explanation each.
Preserves target activations (out/acts_27b_25.pt) and raw AV outputs (01_av_27b_25.jsonl), matching the
7B pipeline's 01_av_7b.jsonl schema so downstream atomic.py/02_claims.py work unchanged. No AR scoring
here -- that happens after local labeling, once deletion rewrites exist too.
"""
import json
from pathlib import Path
import torch
from common_27b import Target, AV, settings, finish, log, OUT, HERE

import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--end", type=int, default=25)
    a = ap.parse_args()
    N = a.end - a.start
    pilot = [json.loads(l) for l in open(HERE.parent / "data/redocred_pilot/pilot.jsonl")][a.start:a.end]
    tag = f"{a.start}_{a.end}"
    S = settings(f"01_27b_{tag}", n=N, start=a.start, end=a.end, note="27B baseline, TARGET=av_base, deletion-only (no paraphrase)")

    tgt = Target()
    acts, info = [], []
    for r in pilot:
        pid = r["pilot_id"]
        n_tok = tgt.n_tokens(r["prefix_text"])
        h = tgt.activation(r["prefix_text"])
        acts.append(h)
        info.append({"pilot_id": pid, "n_tokens_27b": n_tok, "n_tokens_27b_pilot": r["n_tokens_prefix_27b"],
                     "norm": round(float(h.norm()), 2)})
        if n_tok != r["n_tokens_prefix_27b"]:
            log(f"WARNING pilot {pid}: tokenization mismatch {n_tok} vs {r['n_tokens_prefix_27b']}")
    tgt.free()
    log(f"extracted {N} activations; norm range {min(i['norm'] for i in info):.1f}-{max(i['norm'] for i in info):.1f}")
    torch.save({"h": torch.stack(acts), "pilot_id": [r["pilot_id"] for r in pilot]}, OUT / f"acts_27b_{tag}.pt")
    (HERE / f"00_positions_27b_{tag}.json").write_text(json.dumps(info, indent=2))

    av = AV()
    with open(HERE / f"01_av_27b_{tag}.jsonl", "w") as f:
        for i, r in enumerate(pilot):
            g = av.verbalize(acts[i], max_new_tokens=200)
            rec = {"pilot_id": r["pilot_id"], "split": "dev" if r["pilot_id"] < 20 else "eval",
                   "explanation": g["explanation"], "raw_generation": g["raw_generation"],
                   "parse_ok": g["parse_ok"], "cjk": g["cjk"], "gen_tokens": g["n_tokens"],
                   "gen_s": round(g["gen_s"], 1), "inject_hits": g["inject_hits"]}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            log(f"pilot {r['pilot_id']}: {g['n_tokens']} tok {g['gen_s']:.0f}s parse_ok={g['parse_ok']} cjk={g['cjk']}")
    av.free()

    gens = [json.loads(l) for l in open(HERE / f"01_av_27b_{tag}.jsonl")]
    finish(f"01_27b_{tag}", S, n_done=N, parse_ok=sum(g["parse_ok"] for g in gens), cjk=sum(g["cjk"] for g in gens),
           norms=[i["norm"] for i in info])
    print(f"DONE {N} docs; parse_ok {sum(g['parse_ok'] for g in gens)}/{N}; cjk {sum(g['cjk'] for g in gens)}/{N}")

if __name__ == "__main__":
    main()

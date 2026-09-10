"""Step 1: one greedy 7B AV explanation (200 new tokens, released prompt, marker embedding replaced at norm 150) per pilot
activation. Resume-safe: skips pilot_ids already in 01_av_7b.jsonl. Raw generations kept, parse failures / CJK flagged."""
import argparse, json
import numpy as np, torch
from common import *

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--overwrite", action="store_true", help="Regenerate every explanation, replacing the existing file")
    a = ap.parse_args()
    rows = load_pilot()
    A = np.load(OUT / "acts_7b.npz"); acts = {int(i): A["h20"][k] for k, i in enumerate(A["pilot_id"])}
    outp = HERE / "01_av_7b.jsonl"
    done = set() if a.overwrite else {r["pilot_id"] for r in read_jsonl(outp)}
    S = settings("01", model="7b", decoding="greedy", max_new_tokens=200, n=len(rows), resumed_from=len(done))
    av = L.AV()
    S.update(injection_scale=av.scale, prompt_tokens=int(av.prompt(None)[0].shape[1]))
    with open(outp, "w" if a.overwrite else "a") as f:
        for r in rows:
            if r["pilot_id"] in done: continue
            g = av.verbalize(torch.from_numpy(acts[r["pilot_id"]]), max_new_tokens=200)
            rec = {"pilot_id": r["pilot_id"], "split": r["split"], "explanation": g["explanation"], "raw_generation": g["raw_generation"],
                   "parse_ok": g["parse_ok"], "cjk": g["cjk"], "gen_tokens": g["n_tokens"], "gen_s": round(g["gen_s"], 1)}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            L.log(f"pilot {r['pilot_id']}: {g['n_tokens']} tok {g['gen_s']:.0f}s parse_ok={g['parse_ok']} cjk={g['cjk']}")
    av.free()
    gens = read_jsonl(outp)
    finish("01", S, n_done=len(gens), parse_ok=sum(g["parse_ok"] for g in gens), cjk=sum(g["cjk"] for g in gens))
    print("01 DONE", len(gens))

if __name__ == "__main__":
    main()

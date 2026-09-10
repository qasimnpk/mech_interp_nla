"""Validation gate: 5 documents only (pilot_id 0-4). Extract from av_base at each document's 27B position,
one greedy AV explanation each, AR-score by cosine. Output schema matches 01_av_7b.jsonl's fields (pilot_id,
explanation, raw_generation, parse_ok, cjk, gen_tokens, gen_s) so downstream atomic.py/02_claims.py/
04_score.py need minimal changes later. Does NOT run past 5 documents -- that needs separate approval.
"""
import json
from pathlib import Path
import torch
from common_27b import Target, AV, AR, cos, settings, finish, log, OUT, HERE

N = 5

def main():
    pilot = [json.loads(l) for l in open(HERE.parent / "data/redocred_pilot/pilot.jsonl")][:N]
    S = settings("00_01_val5", n=N, note="validation gate, pilot_id 0-4 only")

    tgt = Target()
    acts, info = [], []
    for r in pilot:
        pid = r["pilot_id"]
        n_tok = tgt.n_tokens(r["prefix_text"])
        expected_pos = r["n_tokens_prefix_27b"] - 1
        h = tgt.activation(r["prefix_text"])
        acts.append(h)
        info.append({
            "pilot_id": pid, "title": r["title"], "n_tokens_27b_ours": n_tok,
            "n_tokens_27b_pilot": r["n_tokens_prefix_27b"], "expected_position": expected_pos,
            "final_word": r["final_word"], "norm": round(float(h.norm()), 2),
        })
        log(f"pilot {pid}: tok(ours)={n_tok} tok(pilot)={r['n_tokens_prefix_27b']} norm={float(h.norm()):.1f}")
        if n_tok != r["n_tokens_prefix_27b"]:
            log(f"  WARNING: tokenization mismatch for pilot {pid} -- position formula may be off")
    tgt.free()

    shipped_lo, shipped_hi = 84.6, 101.8
    for i in info:
        i["norm_in_shipped_range"] = shipped_lo <= i["norm"] <= shipped_hi
    n_in_range = sum(i["norm_in_shipped_range"] for i in info)
    log(f"activation norms in shipped-example range [{shipped_lo},{shipped_hi}]: {n_in_range}/{N}")

    av = AV()
    gens = []
    for i, r in enumerate(pilot):
        g = av.verbalize(acts[i], max_new_tokens=200)
        rec = {
            "pilot_id": r["pilot_id"], "explanation": g["explanation"], "raw_generation": g["raw_generation"],
            "parse_ok": g["parse_ok"], "cjk": g["cjk"], "gen_tokens": g["n_tokens"],
            "gen_s": round(g["gen_s"], 1), "inject_hits": g["inject_hits"],
        }
        gens.append(rec)
        log(f"pilot {r['pilot_id']}: {g['n_tokens']} tok {g['gen_s']:.0f}s parse_ok={g['parse_ok']} "
            f"cjk={g['cjk']} inject_hits={g['inject_hits']}")
        print(f"\n### pilot {r['pilot_id']} ({r['title']})\nSOURCE TAIL: ...{r['prefix_text'][-200:]!r}\n"
              f"EXPLANATION: {g['explanation']}\n", flush=True)
    av.free()

    ar = AR()
    for i, r in enumerate(pilot):
        z = gens[i]["explanation"] if gens[i]["parse_ok"] else gens[i]["raw_generation"]
        pred = ar.predict(z)
        c = cos(pred, acts[i])
        j = (i + 1) % N
        c_shuffled = cos(pred, acts[j])
        gens[i].update({"cos_own": round(c, 4), "cos_shuffled": round(c_shuffled, 4), "shuffled_partner": pilot[j]["pilot_id"]})
        log(f"pilot {r['pilot_id']}: cos_own={c:.4f} cos_shuffled={c_shuffled:.4f}")
    ar.free()

    with open(HERE / "01_av_27b_val5.jsonl", "w") as f:
        for g in gens:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    np_out = OUT / "acts_27b_val5.pt"
    torch.save({"h": torch.stack(acts), "pilot_id": [r["pilot_id"] for r in pilot]}, np_out)
    (HERE / "00_positions_27b_val5.json").write_text(json.dumps(info, indent=2))

    cos_own_mean = sum(g["cos_own"] for g in gens) / N
    cos_shuf_mean = sum(g["cos_shuffled"] for g in gens) / N
    finish("00_01_val5", S, n_done=N, parse_ok=sum(g["parse_ok"] for g in gens), cjk=sum(g["cjk"] for g in gens),
           cos_own_mean=round(cos_own_mean, 4), cos_shuffled_mean=round(cos_shuf_mean, 4),
           n_norms_in_shipped_range=n_in_range)
    print(f"\nVALIDATION SUMMARY: 5/5 docs, parse_ok {sum(g['parse_ok'] for g in gens)}/5, "
          f"cos_own mean {cos_own_mean:.4f}, cos_shuffled mean {cos_shuf_mean:.4f}, "
          f"norms in shipped range {n_in_range}/5", flush=True)

if __name__ == "__main__":
    main()

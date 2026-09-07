"""T3 — residual-stream steering of the verbalizer itself (PLAN.md round 3; AV + AR; pilot set 0-39).

  uv run python overnight/t3_avsteer.py

Directions (difference of means INSIDE the AV, computed once; sentences in t34_sentences.py): run the AV on
plain text (no chat template, no injection, add_special_tokens=False) and take the mean last-token residual
at block l (hidden_states[l+1]) over 32 French minus 32 English sentences ('french'), and 32 one-word
answers minus 32 long sentences ('terse'); l in {8, 14}.
Steering: add alpha * d/||d|| * mean||h_l|| (mean last-token norm at block l over the 64 sentences of that
direction) to the output of block l at every generated position — in the prefill pass only at the final
prompt position (whose logits produce the first generated token; the injected marker row and all earlier
prompt positions are untouched, asserted), and at every position of every decode step.  alpha in {1, 2, 4}.
Greedy, 200 tokens, injection exactly as nla_lib.
Measures: French mechanical pass (S5 rule, stoplist fraction >= 0.15), word count, parse_ok, cjk,
cos(AR(output), h) vs the S5 V0 cos for the same stimulus, topic preservation (detok(topic_true) in output),
word-sequence similarity (difflib) and Jaccard to the V0 explanation.
Kill T3 (pre-registered): French pass rate < 0.25 at every (l, alpha) with parse_ok >= 0.5 -> MET;
INCONCLUSIVE if no cell reaches parse_ok >= 0.5.  Three-way with CIs by stimulus: MET if every eligible
french cell has CI hi < 0.25; NOT MET if any eligible french cell has CI lo >= 0.25; else INCONCLUSIVE.
Stimulus-outer loop (12 cells per stimulus); generation stops at the stage cap so every cell has equal n.
"""
from __future__ import annotations

import difflib
import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight import t34_sentences as T  # noqa: E402
from overnight.t1_arprobe import detok  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

THRESH = 0.25
LAYERS = [8, 14]
ALPHAS = [1.0, 2.0, 4.0]
DIRS = ["french", "terse"]
N_PILOT = 40
CAP_S = 85 * 60
FIXED = [0, 7, 19, 33]
CELLS = [(d, l, a) for d in DIRS for l in LAYERS for a in ALPHAS]


def words(s):
    return (s or "").lower().split()


class Steer:
    """Forward hook on AV block l: adds vec to positions >= start (prefill) / all positions (decode)."""

    def __init__(self, model, layer: int, vec: torch.Tensor, prompt_len: int):
        self.vec = vec.to(L.DEVICE, torch.bfloat16); self.prompt_len = prompt_len; self.n_calls = 0
        self.handle = model.model.layers[layer].register_forward_hook(self.hook)

    def hook(self, _mod, _inp, output):
        h = output[0] if isinstance(output, tuple) else output
        if h.shape[1] > 1:                       # prefill: only the final prompt position
            assert h.shape[1] == self.prompt_len, h.shape
            h = h.clone(); h[:, self.prompt_len - 1:] = h[:, self.prompt_len - 1:] + self.vec
        else:                                    # decode step
            h = h + self.vec
        self.n_calls += 1
        return (h, *output[1:]) if isinstance(output, tuple) else h

    def remove(self):
        self.handle.remove()


def directions(av: L.AV, timings: dict):
    tok, model = av.tok, av.model
    sets = {"french": ([f for _, f in T.FRENCH_EN_PAIRS], [e for e, _ in T.FRENCH_EN_PAIRS]), "terse": (T.TERSE, T.LONG)}
    t0 = time.time(); out = {}; acts = {}
    for name, (pos, neg) in sets.items():
        H = {l: [] for l in LAYERS}
        for grp, sents in [("pos", pos), ("neg", neg)]:
            for s in sents:
                ids = tok(s, return_tensors="pt", add_special_tokens=False)["input_ids"].to(L.DEVICE)
                with torch.inference_mode():
                    hs = model(ids, output_hidden_states=True, use_cache=False).hidden_states
                for l in LAYERS:
                    H[l].append((grp, L.to_cpu_f32(hs[l + 1][0, -1]).numpy()))
        for l in LAYERS:
            P = np.stack([v for g, v in H[l] if g == "pos"]); N = np.stack([v for g, v in H[l] if g == "neg"])
            d = P.mean(0) - N.mean(0); mean_norm = float(np.linalg.norm(np.concatenate([P, N]), axis=1).mean())
            out[(name, l)] = {"d": d, "unit": d / (np.linalg.norm(d) + 1e-30), "mean_norm": mean_norm, "norm_d": float(np.linalg.norm(d))}
            acts[f"{name}_L{l}_pos"] = P; acts[f"{name}_L{l}_neg"] = N
    timings["direction_s"] = time.time() - t0
    np.savez(L.OUT / "t3_dirs.npz", **acts, **{f"dir_{n}_L{l}": v["d"] for (n, l), v in out.items()})
    return out


def main():
    S = L.Settings("t3", threshold=THRESH, layers=LAYERS, alphas=ALPHAS, directions=DIRS, n_pilot=N_PILOT, cap_s=CAP_S, cells=CELLS, fixed_examples=FIXED,
                   direction_rule="AV on plain text, hidden_states[l+1] last token; mean(pos) - mean(neg); scale = alpha * mean last-token norm over the 64 sentences at block l",
                   steering_positions="prefill: final prompt position only (marker row untouched, asserted); decode: every generated position",
                   av_max_new_tokens=200, decoding="greedy", french_rule="S5 V4: stoplist fraction >= 0.15",
                   outcome_rule="eligible = french cells with parse_ok >= 0.5; MET if all eligible CI hi < 0.25; NOT MET if any eligible CI lo >= 0.25; else INCONCLUSIVE; INCONCLUSIVE if no eligible cell")
    timings = {}
    acts = np.load(L.OUT / "acts_L20.npz"); h20 = acts["h20"]
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    s5 = pd.read_csv(L.OVERNIGHT / "s5_recon.csv"); v0cos = s5[s5.variant == "V0"].set_index("stim_idx").cos.to_dict()
    expl = {}
    for line in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); expl[r["stim_idx"]] = r["explanation"] or ""

    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    D = directions(av, timings)
    S.update(direction_geometry={f"{n}_L{l}": {"norm_d": v["norm_d"], "mean_norm": v["mean_norm"]} for (n, l), v in D.items()},
             cos_french_terse={f"L{l}": L.cos(D[("french", l)]["d"], D[("terse", l)]["d"]) for l in LAYERS})
    L.log("directions built: " + ", ".join(f"{n}_L{l} ||d||={v['norm_d']:.1f} mean||h||={v['mean_norm']:.1f}" for (n, l), v in D.items()))
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0
    ids, inj_pos, base = av.prompt(None); prompt_len = int(ids.shape[1])

    rows = []; t_start = time.time(); stopped = None
    with open(L.OVERNIGHT / "t3_outputs.jsonl", "w") as f:
        for i in range(N_PILOT):
            if time.time() - t_start > CAP_S:
                stopped = i; L.log(f"stage cap reached before stimulus {i}; stopping generation"); break
            h = h20[i]; topic = detok(top.topic_true[i]); v0 = expl[i]
            for direction, l, a in CELLS:
                dd = D[(direction, l)]
                vec = torch.from_numpy((a * dd["unit"] * dd["mean_norm"]).astype(np.float32))
                rec = {"stim_idx": i, "direction": direction, "layer": l, "alpha": a, "vec_norm": float(vec.norm()), "topic_true": topic, "error": None}
                st = Steer(av.model, l, vec, prompt_len)
                try:
                    before = base[0, inj_pos].clone()
                    r = av.verbalize(torch.from_numpy(h)); rec.update(r)
                    assert torch.equal(av.prompt(None)[2][0, inj_pos], before)  # cached prompt embeddings untouched
                    rec["hook_calls"] = st.n_calls
                    e = r["explanation"]
                    rec.update({"french_frac": T.french_frac(e), "french_pass": T.french_frac(e) >= T.FRENCH_PASS_THRESHOLD, "n_words": len(e.split()),
                                "topic_preserved": topic.lower() in e.lower(), "seq_sim_v0": difflib.SequenceMatcher(None, words(v0), words(e)).ratio(),
                                "jaccard_v0": len(set(words(v0)) & set(words(e))) / max(1, len(set(words(v0)) | set(words(e))))})
                    rec["cos_ar_h"] = L.cos(ar.predict(e).numpy(), h); rec["cos_v0_s5"] = float(v0cos[i]); rec["dcos_v0"] = rec["cos_ar_h"] - rec["cos_v0_s5"]
                except Exception:
                    rec["error"] = traceback.format_exc(); L.log(f"FAILED stim {i} {direction} L{l} a={a}")
                finally:
                    st.remove()
                rows.append(rec); f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            L.log(f"stim {i + 1}/{N_PILOT} done, {len(rows)} items, {(time.time() - t_start) / len(rows):.1f} s/item")
    timings["s_per_item"] = (time.time() - t_start) / max(1, len(rows)); timings["n_items"] = len(rows); timings["stopped_at_stimulus"] = stopped
    av.free(); ar.free()

    df = pd.DataFrame(rows); ok = df[df.error.isna()]

    def ci(vals, cl):
        return L.cluster_bootstrap_mean(np.asarray(vals, float), cl)

    def cell(d, l, a):
        return ok[(ok.direction == d) & (ok.layer == l) & (ok.alpha == a)]

    cells = {}
    for d, l, a in CELLS:
        c = cell(d, l, a)
        if not len(c):
            continue
        cells[(d, l, a)] = {"n": len(c), "parse_ok": float(c.parse_ok.mean()), "french": ci(c.french_pass, c.stim_idx), "french_frac": float(c.french_frac.mean()),
                            "words": float(c.n_words.mean()), "cjk": float(c.cjk.mean()), "topic": float(c.topic_preserved.mean()), "seq": float(c.seq_sim_v0.mean()),
                            "jac": float(c.jaccard_v0.mean()), "cos": float(c.cos_ar_h.mean()), "dcos": float(c.dcos_v0.mean()), "dcos_med": float(c.dcos_v0.median())}
    elig = {k: v for k, v in cells.items() if k[0] == "french" and v["parse_ok"] >= 0.5}
    if not elig or any(v["n"] < 10 for v in elig.values()):
        out = "INCONCLUSIVE"
    elif all(v["french"]["hi"] < THRESH for v in elig.values()):
        out = "MET"
    elif any(v["french"]["lo"] >= THRESH for v in elig.values()):
        out = "NOT MET"
    else:
        out = "INCONCLUSIVE"
    L.append_disconfirmation("T3", "T3", "French pass rate < 0.25 at every (ℓ, α) with parse_ok ≥ 0.5 (pilot, french direction, CI by stimulus)",
                             "; ".join(f"L{l} α={a:g}: pass {v['french']['mean']:.3f} [{v['french']['lo']:.3f},{v['french']['hi']:.3f}] parse_ok {v['parse_ok']:.2f} n={v['n']}" for (d, l, a), v in cells.items() if d == "french")
                             + f"; eligible cells {len(elig)}/{sum(1 for k in cells if k[0] == 'french')}",
                             out, "MET would mean the AV is not steerable by residual addition either, at doses that keep it fluent")
    best = max(elig.items(), key=lambda kv: kv[1]["french"]["mean"])[0] if elig else (max(cells.items(), key=lambda kv: kv[1]["french"]["mean"])[0] if cells else None)

    lines = ["# T3 summary — residual-stream steering of the verbalizer (pilot 0–39; AV + AR)", "",
             f"git {L.git_hash()[:8]}; settings in t3_settings.json; items in t3_outputs.jsonl; directions in out/t3_dirs.npz", "",
             f"- items {len(df)} (errors {int(df.error.notna().sum())}); {timings['s_per_item']:.1f} s/item; stopped at stimulus {stopped} (None = all {N_PILOT} done); prompt {prompt_len} tokens, marker at {inj_pos}",
             "- directions: " + ", ".join(f"{n}_L{l} ||d||={v['norm_d']:.1f}, mean||h||={v['mean_norm']:.1f}" for (n, l), v in D.items()),
             f"- baseline (round-1 explanations, pilot): french pass {np.mean([T.french_frac(expl[i]) >= T.FRENCH_PASS_THRESHOLD for i in range(N_PILOT)]):.3f}, mean words {np.mean([len(expl[i].split()) for i in range(N_PILOT)]):.1f}, topic preserved {np.mean([detok(top.topic_true[i]).lower() in expl[i].lower() for i in range(N_PILOT)]):.3f}",
             "", "## Kill T3", "", f"- eligible french cells (parse_ok ≥ 0.5): {len(elig)}; outcome → **{out}**", "",
             "## Grid", "", "| direction | ℓ | α | n | parse_ok | French pass [CI] | French frac | words | cjk | topic preserved | seq-sim V0 | Jaccard V0 | mean cos(AR,h) | mean Δcos vs V0 | median Δcos |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in cells.items():
        d, l, a = k; fr = v["french"]
        lines.append(f"| {d} | {l} | {a:g} | {v['n']} | {v['parse_ok']:.3f} | {fr['mean']:.3f} [{fr['lo']:.3f},{fr['hi']:.3f}] | {v['french_frac']:.3f} | {v['words']:.1f} | {v['cjk']:.3f} | {v['topic']:.3f} | {v['seq']:.3f} | {v['jac']:.3f} | {v['cos']:.4f} | {v['dcos']:+.4f} | {v['dcos_med']:+.4f} |")
    lines += ["", f"## Four fixed examples (stimuli 0, 7, 19, 33) for the best cell {best}", ""]
    if best:
        for i in FIXED:
            r = df[(df.stim_idx == i) & (df.direction == best[0]) & (df.layer == best[1]) & (df.alpha == best[2])]
            lines += [f"### stim {i} — topic {detok(top.topic_true[i])}", "", "**V0 (round 1):**", "```", expl[i], "```"]
            if len(r):
                r = r.iloc[0]
                lines += [f"**steered {best}** (parse_ok={r.get('parse_ok')}, french_frac={r.get('french_frac', float('nan')):.2f}, words={r.get('n_words')}, cos(AR,h)={r.get('cos_ar_h', float('nan')):.3f}):",
                          "```", str(r.get("explanation") if r.get("parse_ok") else r.get("raw_generation")), "```"]
            lines.append("")
    (L.OVERNIGHT / "t3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_T3={"outcome": out, "eligible": {f"{k[0]}_L{k[1]}_a{k[2]:g}": v for k, v in elig.items()}},
             cells={f"{k[0]}_L{k[1]}_a{k[2]:g}": v for k, v in cells.items()}, n_items=len(df), n_errors=int(df.error.notna().sum()), stopped_at_stimulus=stopped)
    L.log(f"T3 done: {out}")


if __name__ == "__main__":
    main()

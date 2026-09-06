"""S4 (OPTIONAL) — blind-describer and raw-context baselines on the 160 evaluation positions.

  uv run python overnight/s4_blind.py

TARGET (plain Qwen2.5-7B-Instruct, chat template, greedy, 200 new tokens) describes the activation
from the visible context only; a left-only variant on the first 100 evaluation positions; a
raw-context "explanation" (context_left_64 + token_str) fed straight to AR. TARGET + AR co-resident.
Kill test K4 on the paired gap cos_AV − cos_blind.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

MAX_NEW = 200
N_LEFT = 100
K4_THRESHOLD = 0.05
BLIND_PROMPT = ("You are a meticulous AI researcher conducting an important investigation into activation vectors from a language "
                "model. The model read the following text, and we are looking at its internal activation at the token marked with [[ ]].\n\n"
                "<text>{context_left_64}[[{token_str}]]{context_right_16}</text>\n\n"
                "Describe the semantic content that this activation most likely encodes. Produce an explanation enclosed within "
                "<explanation> tags, consisting of 2-3 text snippets describing that vector, in the same style a trained activation "
                "verbalizer would use.")

S = L.Settings("s4", max_new_tokens=MAX_NEW, decoding="greedy", n_left_only=N_LEFT, k4_threshold=K4_THRESHOLD,
               blind_prompt=BLIND_PROMPT, left_only="same prompt with context_right_16 removed, first 100 evaluation positions",
               rawctx="context_left_64 + token_str fed verbatim to AR as the explanation",
               bootstrap="cluster by position, 1000 draws, seed 0")


def main():
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    s1 = pd.read_csv(L.OVERNIGHT / "s1_recon.csv").set_index("stim_idx")
    ev = [i for i in range(len(df)) if L.split_of(i) == "eval"]
    out_path = L.OVERNIGHT / "s4_blind.jsonl"
    done = {}
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line); done[r["stim_idx"]] = r
    tgt = L.Target()
    t0 = time.time(); n_gen = 0
    with open(out_path, "a") as f:
        for k, i in enumerate(ev):
            if i in done:
                continue
            s = df.iloc[i]
            rec = {"stim_idx": i, "doc_idx": int(s.doc_idx), "pos": int(s.pos), "token_str": s.token_str, "error": None,
                   "blind_raw": None, "blind_explanation": None, "blind_parse_ok": False,
                   "blind_left_raw": None, "blind_left_explanation": None, "blind_left_parse_ok": None}
            try:
                raw = tgt.chat_generate(BLIND_PROMPT.format(context_left_64=s.context_left_64, token_str=s.token_str, context_right_16=s.context_right_16), MAX_NEW)
                rec["blind_raw"] = raw; rec["blind_explanation"], rec["blind_parse_ok"] = L.parse_explanation(raw); n_gen += 1
                if k < N_LEFT:
                    raw = tgt.chat_generate(BLIND_PROMPT.format(context_left_64=s.context_left_64, token_str=s.token_str, context_right_16=""), MAX_NEW)
                    rec["blind_left_raw"] = raw; rec["blind_left_explanation"], rec["blind_left_parse_ok"] = L.parse_explanation(raw); n_gen += 1
            except Exception as e:
                rec["error"] = traceback.format_exc(); L.log(f"blind FAILED {i}: {e}")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); done[i] = rec
            L.log(f"blind {k}/{len(ev)} stim {i} {s.token_str!r} parse_ok={rec['blind_parse_ok']} ({(time.time()-t0)/max(1,n_gen):.1f}s/gen)")
    S.update(blind_wall_s=time.time() - t0, blind_n_generated=n_gen)
    tgt.free()
    ar = L.AR()
    rows = []
    for i in ev:
        r = done[i]; s = df.iloc[i]
        def sc(text):
            try:
                return L.cos(ar.predict(text).numpy(), h20[i]) if text is not None else np.nan
            except Exception:
                return np.nan
        rows.append({"stim_idx": i, "doc_idx": int(s.doc_idx), "pos": int(s.pos), "cos_AV": float(s1.loc[i, "cos_own"]),
                     "cos_blind": sc(r["blind_explanation"]), "cos_blind_left": sc(r["blind_left_explanation"]),
                     "cos_rawctx": sc(s.context_left_64 + s.token_str), "blind_parse_ok": r["blind_parse_ok"],
                     "act_norm": float(np.linalg.norm(h20[i]))})
    ar.free()
    rc = pd.DataFrame(rows)
    rc["gap"] = rc.cos_AV - rc.cos_blind
    rc.to_csv(L.OVERNIGHT / "s4_recon.csv", index=False)
    ok = rc.dropna(subset=["gap"])
    ci = L.cluster_bootstrap_mean(ok.gap, ok.stim_idx)
    if ci["n"] < len(ev):
        out = "INCONCLUSIVE"
    elif ci["hi"] < K4_THRESHOLD:
        out = "MET"
    elif ci["lo"] >= K4_THRESHOLD:
        out = "NOT MET"
    else:
        out = "INCONCLUSIVE"
    k4 = L.append_disconfirmation("S4", "K4", f"CI95 of mean(cos_AV − cos_blind) entirely < {K4_THRESHOLD}",
                                  f"mean gap={ci['mean']:.4f} CI95=[{ci['lo']:.4f},{ci['hi']:.4f}] n={ci['n']}; mean cos_AV={ok.cos_AV.mean():.4f} mean cos_blind={ok.cos_blind.mean():.4f}",
                                  out, "a strong blind score shows reconstruction can be achieved from visible context; it does not show the verbalizer ignores the activation")
    lines = ["# S4 summary — blind-describer and raw-context baselines (evaluation set)", "", f"git {L.git_hash()[:8]}; settings in s4_settings.json", "",
             "| column | mean | median | n |", "|---|---|---|---|"]
    for c in ["cos_AV", "cos_blind", "cos_blind_left", "cos_rawctx"]:
        lines.append(f"| {c} | {rc[c].mean():.4f} | {rc[c].median():.4f} | {int(rc[c].notna().sum())} |")
    left = rc.dropna(subset=["cos_blind_left"])
    lines += ["", f"- mean gap (cos_AV − cos_blind): {ci['mean']:.4f} CI95 [{ci['lo']:.4f}, {ci['hi']:.4f}] n={ci['n']}",
              f"- mean cos_AV − cos_blind_left (first {len(left)} eval positions): {(left.cos_AV - left.cos_blind_left).mean():.4f}",
              f"- mean cos_AV − cos_rawctx: {(rc.cos_AV - rc.cos_rawctx).mean():.4f}",
              f"- fraction blind ≥ AV: {(ok.cos_blind >= ok.cos_AV).mean():.4f}; fraction rawctx ≥ AV: {(rc.cos_rawctx >= rc.cos_AV).mean():.4f}",
              f"- blind parse_ok rate: {rc.blind_parse_ok.mean():.3f}", ""]
    for name, key in [("act_norm", "act_norm"), ("pos", "pos")]:
        terc = pd.qcut(ok[key], 3, labels=["low", "mid", "high"])
        lines += [f"| {name} tercile | range | mean gap | mean cos_AV | mean cos_blind | n |", "|---|---|---|---|---|---|"]
        for t in ["low", "mid", "high"]:
            sub = ok[terc == t]
            lines.append(f"| {t} | {sub[key].min():.1f}–{sub[key].max():.1f} | {sub.gap.mean():.4f} | {sub.cos_AV.mean():.4f} | {sub.cos_blind.mean():.4f} | {len(sub)} |")
        lines.append("")
    lines += ["## Kill test", "", f"- {k4}", ""]
    (L.OVERNIGHT / "s4_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(k4=ci)
    L.log("S4 done")


if __name__ == "__main__":
    main()

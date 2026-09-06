"""S1 — baseline round trip on 200 positions (PLAN.md round 1).

  uv run python overnight/s1_roundtrip.py

AV: verbalize all 200 stimuli (greedy, 200 new tokens; stimuli 0-15 reused from S0 when the
prompt and decoding settings are byte-identical; resumes from a partial explanations.jsonl).
AR: reconstruct every explanation -> overnight/out/recon_L20.npz; score against own h20,
a random other document's h20 (seed 0), the same document's second position, and h19/h21.
Kill tests K1a (mean cos_own on evaluation set) and K1b (same-doc position specificity).
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
import torch  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

MAX_NEW = 200
N_EVAL_MIN = 160
K1A_THRESHOLD = 0.50
K1B_MARGIN = 0.05
EXPL_PATH = L.OVERNIGHT / "explanations.jsonl"

S = L.Settings("s1", max_new_tokens=MAX_NEW, decoding="greedy", n_eval_min=N_EVAL_MIN,
               k1a_threshold=K1A_THRESHOLD, k1b_margin=K1B_MARGIN,
               shuffled_doc_rng="np.random.default_rng(0): j=integers(0,200) redrawn while j==i, in stim order",
               bootstrap="cluster by explanation (=row), 1000 draws, seed 0",
               example_rng="np.random.default_rng(0).choice(eval rows, 5, replace=False)")
timings = {}


def load_existing() -> dict[int, dict]:
    have = {}
    if EXPL_PATH.exists():
        for line in EXPL_PATH.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("error") is None and r.get("raw_generation") is not None:
                    have[r["stim_idx"]] = r
    return have


def main():
    df, acts = L.load_stimuli()
    n = len(df)
    assert n == 200, n
    h20 = acts["h20"]

    # ---------------- AV
    have = load_existing()
    s0_settings = json.loads((L.OVERNIGHT / "s0_settings.json").read_text())
    s0_path = L.OVERNIGHT / "s0_explanations.jsonl"
    reused_s0 = 0
    t0 = time.time()
    av = L.AV()
    timings["av_load_s"] = time.time() - t0
    timings["rss_after_av_G"] = L.rss_mb() / 1024
    S.update(av_prompt_verbatim=av.default_prompt)
    if (s0_path.exists() and s0_settings.get("av_prompt_verbatim") == av.default_prompt
            and s0_settings.get("max_new_tokens") == MAX_NEW and s0_settings.get("decoding") == "greedy"):
        for line in s0_path.read_text().splitlines():
            r = json.loads(line)
            if r.get("error") is None and r["stim_idx"] not in have:
                r["reused_from_s0"] = True
                have[r["stim_idx"]] = r
                reused_s0 += 1
    L.log(f"AV: {len(have)} explanations already available ({reused_s0} reused from S0); generating {n - len(have)}")
    gen_s = []
    with open(EXPL_PATH, "w") as f:
        for i in range(n):
            if i in have:
                rec = have[i]
            else:
                rec = {"stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "token_str": df.token_str[i],
                       "reused_from_s0": False}
                try:
                    rec.update(av.verbalize(torch.from_numpy(h20[i]), None, MAX_NEW))
                    rec["error"] = None
                    gen_s.append(rec["gen_s"])
                except Exception as e:
                    rec.update({"raw_generation": None, "explanation": None, "parse_ok": False, "cjk": False,
                                "n_tokens": 0, "gen_s": float("nan"), "error": traceback.format_exc()})
                    L.log(f"AV FAILED on {i}: {e}")
                L.log(f"AV {i}/{n} {rec['token_str']!r} n_tok={rec['n_tokens']} {rec['gen_s']:.1f}s parse_ok={rec['parse_ok']} cjk={rec['cjk']}")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            have[i] = rec
    timings["av_sec_per_explanation"] = float(np.mean(gen_s)) if gen_s else float("nan")
    timings["av_n_generated"] = len(gen_s)
    av.free()
    timings["rss_after_av_free_G"] = L.rss_mb() / 1024

    # ---------------- AR
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    d = h20.shape[1]
    pred = np.full((n, d), np.nan, np.float32)
    t0 = time.time()
    for i in range(n):
        r = have[i]
        text = r["explanation"] if r.get("explanation") is not None else (r.get("raw_generation") or "")
        try:
            pred[i] = ar.predict(text).numpy()
        except Exception as e:
            r["error"] = (r.get("error") or "") + traceback.format_exc()
            L.log(f"AR FAILED on {i}: {e}")
    pred_empty = ar.predict("").numpy()
    timings["ar_sec_per_score"] = (time.time() - t0) / n
    ar.free()
    np.savez(L.OUT / "recon_L20.npz", pred=pred, pred_empty=pred_empty, stim_idx=np.arange(n))

    # ---------------- scoring
    rng = np.random.default_rng(0)
    rows = []
    for i in range(n):
        j = int(rng.integers(0, n))
        while j == i:
            j = int(rng.integers(0, n))
        r = have[i]
        ok = not np.isnan(pred[i]).any()
        rows.append({
            "stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "split": L.split_of(i),
            "cos_own": L.cos(pred[i], h20[i]) if ok else np.nan,
            "cos_shuffled_doc": L.cos(pred[i], h20[j]) if ok else np.nan, "shuffled_doc_stim_idx": j,
            "cos_shuffled_samedoc": L.cos(pred[i], acts["h20_pos2"][i]) if ok else np.nan,
            "cos_L19": L.cos(pred[i], acts["h19"][i]) if ok else np.nan,
            "cos_L21": L.cos(pred[i], acts["h21"][i]) if ok else np.nan,
            "cos_empty": L.cos(pred_empty, h20[i]),
            "n_tokens": r.get("n_tokens", 0), "act_norm": float(np.linalg.norm(h20[i])),
            "parse_ok": bool(r.get("parse_ok", False)), "cjk": bool(r.get("cjk", False)),
            "error": r.get("error") is not None,
        })
    rc = pd.DataFrame(rows)
    rc.to_csv(L.OVERNIGHT / "s1_recon.csv", index=False)
    ev = rc[rc.split == "eval"]
    ev_ok = ev.dropna(subset=["cos_own"])

    # ---------------- kill tests (evaluation set)
    ci_own = L.cluster_bootstrap_mean(ev_ok.cos_own, ev_ok.stim_idx)
    if ci_own["n"] < N_EVAL_MIN:
        k1a_out = "INCONCLUSIVE"
    elif ci_own["hi"] < K1A_THRESHOLD:
        k1a_out = "MET"
    elif ci_own["lo"] >= K1A_THRESHOLD:
        k1a_out = "NOT MET"
    else:
        k1a_out = "INCONCLUSIVE"
    k1a = L.append_disconfirmation("S1", "K1a", f"mean cos_own<{K1A_THRESHOLD} (eval n>={N_EVAL_MIN})",
                                   f"mean cos_own={ci_own['mean']:.4f} CI95=[{ci_own['lo']:.4f},{ci_own['hi']:.4f}] n={ci_own['n']}",
                                   k1a_out, "pipeline fidelity on wikitext stimuli vs published 0.752 FVE on WildChat+FineWeb")
    diff = ev_ok.cos_own - ev_ok.cos_shuffled_samedoc
    ci_d = L.cluster_bootstrap_mean(diff, ev_ok.stim_idx)
    if ci_d["n"] < N_EVAL_MIN:
        k1b_out = "INCONCLUSIVE"
    elif ci_d["hi"] <= K1B_MARGIN:
        k1b_out = "MET"
    elif ci_d["lo"] > K1B_MARGIN:
        k1b_out = "NOT MET"
    else:
        k1b_out = "INCONCLUSIVE"
    ci_x = L.cluster_bootstrap_mean(ev_ok.cos_own - ev_ok.cos_shuffled_doc, ev_ok.stim_idx)
    k1b = L.append_disconfirmation("S1", "K1b", f"mean cos_shuffled_samedoc >= mean cos_own-{K1B_MARGIN}",
                                   f"mean cos_own={ev_ok.cos_own.mean():.4f} mean cos_shuffled_samedoc={ev_ok.cos_shuffled_samedoc.mean():.4f} "
                                   f"paired diff={ci_d['mean']:.4f} CI95=[{ci_d['lo']:.4f},{ci_d['hi']:.4f}] n={ci_d['n']}; "
                                   f"cross-doc: mean cos_shuffled_doc={ev_ok.cos_shuffled_doc.mean():.4f} diff={ci_x['mean']:.4f} CI95=[{ci_x['lo']:.4f},{ci_x['hi']:.4f}]",
                                   k1b_out, "position specificity: MET would mean explanations reconstruct another position of the same context about as well as their own")

    # ---------------- report
    def dist(s):
        s = s.dropna()
        return f"mean {s.mean():.4f} | median {s.median():.4f} | p10 {s.quantile(0.1):.4f} | p90 {s.quantile(0.9):.4f} | n {len(s)}"
    lines = ["# S1 summary — baseline round trip (200 positions; headline numbers on evaluation set 40–199)", "",
             f"git {L.git_hash()[:8]}; settings in s1_settings.json", "", "## Timings", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    lines += ["", "## Evaluation set (n=160)", "", "| column | distribution |", "|---|---|"]
    for c in ["cos_own", "cos_shuffled_samedoc", "cos_shuffled_doc", "cos_L19", "cos_L21", "cos_empty"]:
        lines.append(f"| {c} | {dist(ev[c])} |")
    lines += ["", f"- mean cos_own − mean cos_empty (positive control, whole explanation deleted): {ev_ok.cos_own.mean() - ev_ok.cos_empty.mean():.4f}",
              f"- mean cos_own CI95 (cluster bootstrap): [{ci_own['lo']:.4f}, {ci_own['hi']:.4f}]",
              f"- paired cos_own − cos_shuffled_samedoc: {ci_d['mean']:.4f} CI95 [{ci_d['lo']:.4f}, {ci_d['hi']:.4f}]",
              f"- paired cos_own − cos_shuffled_doc: {ci_x['mean']:.4f} CI95 [{ci_x['lo']:.4f}, {ci_x['hi']:.4f}]",
              f"- fraction cos_L19 > cos_own: {(ev_ok.cos_L19 > ev_ok.cos_own).mean():.3f}; fraction cos_L21 > cos_own: {(ev_ok.cos_L21 > ev_ok.cos_own).mean():.3f}",
              f"- parse_ok fraction: {ev.parse_ok.mean():.3f}; cjk fraction: {ev.cjk.mean():.3f}; AV/AR errors: {int(ev.error.sum())}"]
    rho = spearmanr(ev_ok.n_tokens, ev_ok.cos_own)
    lines.append(f"- Spearman(n_tokens, cos_own): rho={rho.statistic:.4f} p={rho.pvalue:.3g}")
    terc = pd.qcut(ev_ok.act_norm, 3, labels=["low", "mid", "high"])
    lines += ["", "| act_norm tercile | act_norm range | mean cos_own | n |", "|---|---|---|---|"]
    for t in ["low", "mid", "high"]:
        sub = ev_ok[terc == t]
        lines.append(f"| {t} | {sub.act_norm.min():.1f}–{sub.act_norm.max():.1f} | {sub.cos_own.mean():.4f} | {len(sub)} |")
    lines += ["", "## Pilot set (n=40, for reference)", "", "| column | distribution |", "|---|---|"]
    pi = rc[rc.split == "pilot"]
    for c in ["cos_own", "cos_shuffled_samedoc", "cos_shuffled_doc", "cos_L19", "cos_L21", "cos_empty"]:
        lines.append(f"| {c} | {dist(pi[c])} |")
    lines += ["", "## Kill tests", "", f"- {k1a}", f"- {k1b}", "",
              "## 5 evaluation explanations chosen by seed 0 (verbatim)", ""]
    pick = np.random.default_rng(0).choice(ev.stim_idx.values, 5, replace=False)
    for i in sorted(pick):
        r = have[int(i)]; s = df.iloc[int(i)]; sc = rc.iloc[int(i)]
        lines += [f"### stim {i} (doc {s.doc_idx}, pos {s.pos}) token={s.token_str!r} cos_own={sc.cos_own:.3f} cos_samedoc={sc.cos_shuffled_samedoc:.3f} parse_ok={r.get('parse_ok')}",
                  "", "context: " + json.dumps(s.context_left_64) + " [[" + json.dumps(s.token_str) + "]] " + json.dumps(s.context_right_16), "",
                  "```", str(r.get("explanation") if r.get("explanation") is not None else r.get("raw_generation")), "```", ""]
    (L.OVERNIGHT / "s1_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, k1a=ci_own, k1b=ci_d, k1b_crossdoc=ci_x, reused_from_s0=reused_s0)
    L.log("S1 done")


if __name__ == "__main__":
    main()

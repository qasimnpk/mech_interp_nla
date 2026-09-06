"""S0 — library + stimuli + 16-position smoke on wikitext (PLAN.md round 1).

  uv run python overnight/s0_smoke.py

1. Build the fixed 200-position stimulus set (wikitext-2-raw-v1 train, >=300 TARGET tokens,
   shuffle seed 0, first 200, truncate 512, pos ~ U{16..L-1}, pos2 same stream with |pos2-pos|>=8).
   Cache h19/h20/h21 at pos and h20 at pos2 -> overnight/out/acts_L20.npz.  TARGET only, then free.
2. K0: verbalize stimuli 0-15 with AV (greedy, 200 new tokens); cjk_rate over the 16.
3. AR-score the 16 -> overnight/s0_smoke.csv.  Report -> overnight/s0_summary.md.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from datasets import load_dataset  # noqa: E402

N_STIM = 200
MIN_DOC_TOKENS = 300
MAX_LEN = 512
POS_MIN = 16
MIN_SEP = 8
N_SMOKE = 16
MAX_NEW = 200
K0_THRESHOLD = 0.25

S = L.Settings("s0", n_stim=N_STIM, min_doc_tokens=MIN_DOC_TOKENS, max_len=MAX_LEN, pos_min=POS_MIN,
               min_sep=MIN_SEP, n_smoke=N_SMOKE, max_new_tokens=MAX_NEW, decoding="greedy",
               shuffle_rng="np.random.default_rng(0).permutation(eligible_doc_indices)",
               position_rng="np.random.default_rng(0); per doc in order: pos=integers(16, L); pos2 redrawn same call until |pos2-pos|>=8",
               dataset={"repo": "EleutherAI/wikitext_document_level", "config": "wikitext-2-raw-v1", "split": "train"},
               k0_threshold=K0_THRESHOLD, cjk_regex=L.CJK_RE.pattern)
timings = {}


def build_stimuli(tgt: L.Target) -> pd.DataFrame:
    t0 = time.time()
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]
    tok = tgt.tok
    lens = []
    all_ids = []
    for i in range(len(ds)):
        ids = tok(ds[i]["page"], add_special_tokens=False)["input_ids"]
        all_ids.append(ids)
        lens.append(len(ids))
    lens = np.array(lens)
    eligible = np.nonzero(lens >= MIN_DOC_TOKENS)[0]
    perm = np.random.default_rng(0).permutation(eligible)
    chosen = perm[:N_STIM]
    assert len(chosen) == N_STIM, len(chosen)
    rng = np.random.default_rng(0)
    rows = []
    for stim_idx, doc_idx in enumerate(chosen):
        ids = all_ids[doc_idx][:MAX_LEN]
        Lseq = len(ids)
        pos = int(rng.integers(POS_MIN, Lseq))
        while True:
            pos2 = int(rng.integers(POS_MIN, Lseq))
            if abs(pos2 - pos) >= MIN_SEP:
                break
        rows.append({"stim_idx": stim_idx, "doc_idx": int(doc_idx), "pos": pos, "pos2": pos2,
                     "token_str": tok.decode([ids[pos]]),
                     "context_left_64": tok.decode(ids[max(0, pos - 64):pos]),
                     "context_right_16": tok.decode(ids[pos + 1:pos + 17]),
                     "seq_len": Lseq, "doc_tokens": int(lens[doc_idx]), "_ids": ids})
    S.update(n_docs_train=int(len(ds)), n_eligible=int(len(eligible)))
    timings["stimuli_build_s"] = time.time() - t0
    L.log(f"stimuli: {len(ds)} docs, {len(eligible)} eligible, chose {N_STIM}; {timings['stimuli_build_s']:.0f}s")
    return pd.DataFrame(rows)


def cache_acts(tgt: L.Target, df: pd.DataFrame) -> dict:
    t0 = time.time()
    d = tgt.model.config.hidden_size
    h19 = np.zeros((N_STIM, d), np.float32); h20 = np.zeros_like(h19)
    h21 = np.zeros_like(h19); h20_pos2 = np.zeros_like(h19)
    for r in df.itertuples():
        ids = torch.tensor([df["_ids"].iloc[r.Index]])
        hs = tgt.hidden_states(ids)
        h19[r.stim_idx] = L.to_cpu_f32(hs[L.LAYER][0, r.pos]).numpy()
        h20[r.stim_idx] = L.to_cpu_f32(hs[L.LAYER + 1][0, r.pos]).numpy()
        h21[r.stim_idx] = L.to_cpu_f32(hs[L.LAYER + 2][0, r.pos]).numpy()
        h20_pos2[r.stim_idx] = L.to_cpu_f32(hs[L.LAYER + 1][0, r.pos2]).numpy()
        if r.stim_idx % 50 == 0:
            L.log(f"acts {r.stim_idx}/{N_STIM} seq_len={r.seq_len} pos={r.pos} norm20={np.linalg.norm(h20[r.stim_idx]):.1f}")
    arrs = {"h20": h20, "h19": h19, "h21": h21, "h20_pos2": h20_pos2,
            "stim_idx": df["stim_idx"].values, "doc_idx": df["doc_idx"].values,
            "pos": df["pos"].values, "pos2": df["pos2"].values}
    L.OUT.mkdir(exist_ok=True)
    np.savez(L.OUT / "acts_L20.npz", **arrs)
    timings["acts_cache_s"] = time.time() - t0
    L.log(f"acts cached in {timings['acts_cache_s']:.0f}s")
    return arrs


def main():
    rss0 = L.rss_mb()
    # ---------------- phase 1: TARGET
    t0 = time.time()
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    timings["rss_after_target_G"] = L.rss_mb() / 1024
    df = build_stimuli(tgt)
    acts = cache_acts(tgt, df)
    out_df = df.drop(columns=["_ids"])
    out_df.to_csv(L.OVERNIGHT / "stimuli.csv", index=False)
    tgt.free()
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024

    # ---------------- phase 2: AV (K0)
    t0 = time.time()
    av = L.AV()
    timings["av_load_s"] = time.time() - t0
    timings["rss_after_av_G"] = L.rss_mb() / 1024
    S.update(av_prompt_verbatim=av.default_prompt, av_prompt_len_tokens=int(av.prompt(None)[0].shape[1]),
             av_marker_pos=int(av.prompt(None)[1]), injection_scale=av.scale)
    expl = []
    with open(L.OVERNIGHT / "s0_explanations.jsonl", "w") as f:
        for i in range(N_SMOKE):
            rec = {"stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "token_str": df.token_str[i]}
            try:
                rec.update(av.verbalize(torch.from_numpy(acts["h20"][i]), None, MAX_NEW))
                rec["error"] = None
            except Exception as e:  # keep failures in the file
                rec.update({"raw_generation": None, "explanation": None, "parse_ok": False, "cjk": False,
                            "n_tokens": 0, "gen_s": float("nan"), "error": traceback.format_exc()})
                L.log(f"AV FAILED on {i}: {e}")
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            expl.append(rec)
            L.log(f"AV {i} {rec['token_str']!r} n_tok={rec['n_tokens']} {rec['gen_s']:.1f}s parse_ok={rec['parse_ok']} cjk={rec['cjk']}")
    cjk_rate = float(np.mean([r["cjk"] for r in expl]))
    parse_rate = float(np.mean([r["parse_ok"] for r in expl]))
    gen_s = [r["gen_s"] for r in expl if r["error"] is None]
    timings["av_sec_per_explanation"] = float(np.mean(gen_s)) if gen_s else float("nan")
    k0 = L.append_disconfirmation("S0", "K0", f"cjk_rate>{K0_THRESHOLD}", f"cjk_rate={cjk_rate:.3f} ({int(round(cjk_rate*N_SMOKE))}/{N_SMOKE}), parse_ok={parse_rate:.3f}",
                                  "MET" if cjk_rate > K0_THRESHOLD else "NOT MET",
                                  "injection on raw-text activations: MET would mean the AV is describing the marker glyph")
    av.free()
    timings["rss_after_av_free_G"] = L.rss_mb() / 1024

    # ---------------- phase 3: AR
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    timings["rss_after_ar_G"] = L.rss_mb() / 1024
    rows = []
    t0 = time.time()
    for r in expl:
        i = r["stim_idx"]
        text = r["explanation"] if r["explanation"] is not None else (r["raw_generation"] or "")
        try:
            pred = ar.predict(text).numpy()
            c = L.cos(pred, acts["h20"][i])
        except Exception:
            c = float("nan")
            r["error"] = (r["error"] or "") + traceback.format_exc()
        rows.append({"doc_idx": r["doc_idx"], "pos": r["pos"], "cos": c, "n_tokens": r["n_tokens"],
                     "parse_ok": r["parse_ok"], "cjk": r["cjk"], "stim_idx": i, "token_str": r["token_str"],
                     "act_norm": float(np.linalg.norm(acts["h20"][i])), "error": r["error"] is not None})
        L.log(f"AR {i} cos={c:.3f}")
    timings["ar_sec_per_score"] = (time.time() - t0) / max(1, len(rows))
    ar.free()
    sm = pd.DataFrame(rows)
    sm.to_csv(L.OVERNIGHT / "s0_smoke.csv", index=False)

    # ---------------- report
    lines = ["# S0 summary — library + stimuli + 16-position smoke", "",
             f"git {L.git_hash()[:8]}; settings in s0_settings.json", "",
             "## Timings / memory", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    lines += ["", "## Stimuli", "",
              f"- train docs: {S.d['n_docs_train']}; eligible (>= {MIN_DOC_TOKENS} tokens): {S.d['n_eligible']}; chosen: {N_STIM}",
              f"- seq_len (after 512 truncation) mean {out_df.seq_len.mean():.1f}, min {out_df.seq_len.min()}, max {out_df.seq_len.max()}",
              f"- pos mean {out_df.pos.mean():.1f}, min {out_df.pos.min()}, max {out_df.pos.max()}; |pos2-pos| min {(out_df.pos2-out_df.pos).abs().min()}",
              f"- act_norm (h20) mean {np.linalg.norm(acts['h20'],axis=1).mean():.1f}, p10 {np.percentile(np.linalg.norm(acts['h20'],axis=1),10):.1f}, p90 {np.percentile(np.linalg.norm(acts['h20'],axis=1),90):.1f}, max {np.linalg.norm(acts['h20'],axis=1).max():.1f}",
              "", "## K0", "", f"- cjk_rate = {cjk_rate:.3f}; parse_ok rate = {parse_rate:.3f} (n={N_SMOKE})", f"- {k0}",
              "", "## 16 smoke positions", "", "| stim | doc | pos | token | act_norm | n_tok | parse_ok | cjk | cos |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['stim_idx']} | {r['doc_idx']} | {r['pos']} | `{r['token_str']!r}` | {r['act_norm']:.1f} | {r['n_tokens']} | {r['parse_ok']} | {r['cjk']} | {r['cos']:.3f} |")
    good = sm.cos.dropna()
    lines += ["", f"cos: mean {good.mean():.3f}, median {good.median():.3f}, min {good.min():.3f}, max {good.max():.3f} (n={len(good)})", "",
              "## Explanations (verbatim, first 16)", ""]
    for r in expl:
        lines.append(f"### stim {r['stim_idx']} token={r['token_str']!r} parse_ok={r['parse_ok']} cjk={r['cjk']}")
        lines.append("```"); lines.append(str(r["explanation"] if r["explanation"] is not None else r["raw_generation"])); lines.append("```")
    (L.OVERNIGHT / "s0_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, cjk_rate=cjk_rate, parse_ok_rate=parse_rate, rss_start_G=rss0 / 1024)
    L.log("S0 done")


if __name__ == "__main__":
    main()

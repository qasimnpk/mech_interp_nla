"""R3 — truncation curve, AR only, descriptive (PLAN.md round 2).

  uv run python overnight/r3_truncate.py

For each evaluation explanation with n claims (S2 claim split, s2_claims.csv eval rows):
score the first k claims (k = 1..n) and the last k claims (space-joined), plus each single
claim alone (cos_alone taken from S2). Report mean cos vs k, lift over floor
(cos_k − cos_empty) / (cos_z − cos_empty), the k at which the median lift first exceeds 0.9,
and Spearman(claim word count, cos_alone). No kill test.
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

LIFT_THRESHOLD = 0.9


def main():
    S = L.Settings("r3", lift_threshold=LIFT_THRESHOLD,
                   construction="first-k = ' '.join(claims[:k]); last-k = ' '.join(claims[n-k:]); claims from s2_claims.csv eval rows in claim_idx order",
                   lift="(cos_k − cos_empty) / (cos_z − cos_empty), cos_z = S1 reconstruction of the original explanation text (recon_L20.npz, R0 regeneration), cos_empty = AR('')",
                   cos_alone="from s2_claims.csv (S2 run, not recomputed)",
                   k_star="per k: median lift over explanations with n_claims >= k; k* = first k with median lift > 0.9; also per-explanation smallest k with lift > 0.9",
                   bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")
    timings = {}
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    rec = np.load(L.OUT / "recon_L20.npz")
    pred, pred_empty = rec["pred"], rec["pred_empty"]
    cl = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    cl = cl[cl.split == "eval"].copy()
    claims_by_stim = {int(i): list(g.sort_values("claim_idx").claim) for i, g in cl.groupby("stim_idx")}

    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    cache = {}

    def score(text, i):
        if text not in cache:
            cache[text] = ar.predict(text).numpy()
        return L.cos(cache[text], h20[i])

    rows = []
    t0 = time.time()
    for j, i in enumerate(sorted(claims_by_stim)):
        cs = claims_by_stim[i]; n = len(cs)
        cos_z = L.cos(pred[i], h20[i]); cos_empty = L.cos(pred_empty, h20[i])
        for k in range(1, n + 1):
            for direction, text in [("first", " ".join(cs[:k])), ("last", " ".join(cs[n - k:]))]:
                r = {"stim_idx": i, "n_claims": n, "k": k, "direction": direction, "cos_z": cos_z, "cos_empty": cos_empty,
                     "n_words": len(text.split()), "cos_k": np.nan, "lift": np.nan, "error": None}
                try:
                    r["cos_k"] = score(text, i)
                    r["lift"] = (r["cos_k"] - cos_empty) / (cos_z - cos_empty)
                except Exception as e:
                    r["error"] = traceback.format_exc(); L.log(f"FAILED on {i} k={k} {direction}: {e}")
                rows.append(r)
        if j % 40 == 0:
            L.log(f"{j}/{len(claims_by_stim)} explanations, forwards {ar.n_forward} ({(time.time()-t0)/max(1,ar.n_forward):.2f}s each)")
    timings["ar_forward_s"] = time.time() - t0
    timings["ar_n_forward"] = ar.n_forward
    ar.free()
    cv = pd.DataFrame(rows)
    cv.to_csv(L.OVERNIGHT / "r3_curve.csv", index=False)
    ok = cv[cv.error.isna()]

    # single claims alone (S2)
    cl["lift_alone"] = (cl.cos_alone - cl.stim_idx.map(lambda s: L.cos(pred_empty, h20[s]))) / (cl.cos_z - cl.stim_idx.map(lambda s: L.cos(pred_empty, h20[s])))
    rho = spearmanr(cl.n_words, cl.cos_alone)
    rho_lift = spearmanr(cl.n_words, cl.lift_alone)
    rho_idx = spearmanr(cl.claim_idx / (cl.n_claims - 1).clip(lower=1), cl.cos_alone)

    def ci_s(ci, p=4):
        return f"{ci['mean']:.{p}f} [{ci['lo']:.{p}f}, {ci['hi']:.{p}f}]"
    kmax = int(ok.k.max())
    lines = ["# R3 summary — truncation curve (first k / last k claims), AR only, evaluation explanations", "",
             f"git {L.git_hash()[:8]}; settings in r3_settings.json; AR forwards {ar.n_forward}", "",
             f"- explanations: {len(claims_by_stim)}; claims: {len(cl)}; n_claims histogram: " + ", ".join(f"{k}:{v}" for k, v in sorted(pd.Series([len(c) for c in claims_by_stim.values()]).value_counts().items())),
             f"- cos_z mean {ok.groupby('stim_idx').cos_z.first().mean():.4f}; cos_empty mean {ok.groupby('stim_idx').cos_empty.first().mean():.4f}; errors {int(cv.error.notna().sum())}", "",
             "## Mean cos and lift vs k (explanations with n_claims >= k; cluster-bootstrap CI95 by explanation)", "",
             "| k | n_expl | first-k mean cos | first-k mean lift | first-k median lift | last-k mean cos | last-k mean lift | last-k median lift |", "|---|---|---|---|---|---|---|---|"]
    k_star_first = k_star_last = None
    for k in range(1, kmax + 1):
        f = ok[(ok.k == k) & (ok.direction == "first")]; l = ok[(ok.k == k) & (ok.direction == "last")]
        if len(f) == 0:
            continue
        cf, lf = L.cluster_bootstrap_mean(f.cos_k, f.stim_idx), L.cluster_bootstrap_mean(f.lift, f.stim_idx)
        cl_, ll = L.cluster_bootstrap_mean(l.cos_k, l.stim_idx), L.cluster_bootstrap_mean(l.lift, l.stim_idx)
        mf, ml = float(f.lift.median()), float(l.lift.median())
        if k_star_first is None and mf > LIFT_THRESHOLD:
            k_star_first = k
        if k_star_last is None and ml > LIFT_THRESHOLD:
            k_star_last = k
        lines.append(f"| {k} | {len(f)} | {ci_s(cf)} | {ci_s(lf)} | {mf:.4f} | {ci_s(cl_)} | {ci_s(ll)} | {ml:.4f} |")
    # complete explanations only (k == n): sanity that all-claims joined ~ cos_z
    full = ok[(ok.k == ok.n_claims) & (ok.direction == "first")]
    ci_full = L.cluster_bootstrap_mean(full.cos_k - full.cos_z, full.stim_idx)
    # per-explanation smallest k with lift > threshold
    per = []
    for i, g in ok.groupby("stim_idx"):
        for d in ["first", "last"]:
            gg = g[g.direction == d].sort_values("k")
            hit = gg[gg.lift > LIFT_THRESHOLD]
            per.append({"stim_idx": i, "direction": d, "n_claims": int(gg.n_claims.iloc[0]),
                        "k_star": int(hit.k.iloc[0]) if len(hit) else np.nan})
    per = pd.DataFrame(per)
    # curve by fraction of claims (k/n) for the mixed-n set
    lines += ["", f"- k at which the median first-k lift first exceeds {LIFT_THRESHOLD}: {k_star_first}; last-k: {k_star_last}",
              f"- all claims joined (k = n) minus cos_z: {ci_s(ci_full, 5)} n={ci_full['n']}", "",
              "## Per-explanation smallest k with lift > 0.9", "", "| direction | n_expl | never reached | k*=1 | k*=2 | k*=3 | k*>=4 | mean k*/n |", "|---|---|---|---|---|---|---|---|"]
    for d in ["first", "last"]:
        p = per[per.direction == d]
        r_ = p.k_star / p.n_claims
        lines.append(f"| {d} | {len(p)} | {int(p.k_star.isna().sum())} | {int((p.k_star == 1).sum())} | {int((p.k_star == 2).sum())} | {int((p.k_star == 3).sum())} | {int((p.k_star >= 4).sum())} | {r_.mean():.3f} |")
    lines += ["", "## First k vs last k, paired within explanation (same k)", "", "| k | n_expl | mean cos(first k) − cos(last k) | CI95 |", "|---|---|---|---|"]
    for k in range(1, kmax + 1):
        f = ok[(ok.k == k) & (ok.direction == "first")].set_index("stim_idx"); l = ok[(ok.k == k) & (ok.direction == "last")].set_index("stim_idx")
        idx = f.index.intersection(l.index)
        sub = f.loc[idx]; d_ = sub.cos_k - l.loc[idx].cos_k
        sub = sub[sub.n_claims > k]  # k == n is identical text
        if len(sub) == 0:
            continue
        d_ = d_.loc[sub.index]
        ci = L.cluster_bootstrap_mean(d_, d_.index)
        lines.append(f"| {k} | {ci['n']} | {ci['mean']:.5f} | [{ci['lo']:.5f}, {ci['hi']:.5f}] |")
    lines += ["", "## Single claims alone (S2 cos_alone)", "",
              f"- cos_alone: mean {cl.cos_alone.mean():.4f}, median {cl.cos_alone.median():.4f}, p10 {cl.cos_alone.quantile(0.1):.4f}, p90 {cl.cos_alone.quantile(0.9):.4f} (n={len(cl)})",
              f"- lift_alone: mean {cl.lift_alone.mean():.4f}, median {cl.lift_alone.median():.4f}",
              f"- Spearman(claim word count, cos_alone): rho={rho.statistic:.4f} p={rho.pvalue:.3g} (n={len(cl)})",
              f"- Spearman(claim word count, lift_alone): rho={rho_lift.statistic:.4f} p={rho_lift.pvalue:.3g}",
              f"- Spearman(relative claim position, cos_alone): rho={rho_idx.statistic:.4f} p={rho_idx.pvalue:.3g}", "",
              "| claim position | n | mean cos_alone | mean n_words |", "|---|---|---|---|"]
    for name, m in [("first", cl.claim_idx == 0), ("middle", (cl.claim_idx > 0) & (cl.claim_idx < cl.n_claims - 1)), ("last", cl.claim_idx == cl.n_claims - 1)]:
        g = cl[m]
        lines.append(f"| {name} | {len(g)} | {g.cos_alone.mean():.4f} | {g.n_words.mean():.1f} |")
    lines += ["", "## Timings", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    (L.OVERNIGHT / "r3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, k_star_first=k_star_first, k_star_last=k_star_last,
             spearman_words_cos_alone={"rho": float(rho.statistic), "p": float(rho.pvalue)}, n_expl=len(claims_by_stim), n_rows=len(cv))
    L.log(f"R3 done: k*_first={k_star_first} k*_last={k_star_last} rho(words,cos_alone)={rho.statistic:.4f}")


if __name__ == "__main__":
    main()

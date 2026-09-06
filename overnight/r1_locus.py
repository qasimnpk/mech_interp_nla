"""R1 — fact-blindness locus: target representation vs reconstructor (PLAN.md round 2).

  uv run python overnight/r1_locus.py

Inputs: the 490 accepted S3 triples (claim c, LLM corruption c*, LLM paraphrase c~) from
s3_edits.jsonl (edit_ok), plus corrupt_det where present (numeric_ok and non-null).
Target side: each claim text through TARGET (raw text, no chat template, add_special_tokens=False),
hidden_states[LAYER+1] at the last token and mean over tokens; d = 1 - cos.
AR side: AR(claim) with the usual template; d = 1 - cos.
Kill test R1: S_T = d_corr_T - d_para_T (last token), cluster bootstrap by explanation;
MET if CI95 <= 0; INCONCLUSIVE if it straddles 0 or n < 300.
TARGET phase first, freed, then AR (each phase resumable from its own npz cache in out/).
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

MIN_N = 300
VARIANTS = ["claim", "corrupt", "paraphrase", "corrupt_det"]
EXAMPLE_RE = re.compile(r"^### accepted #(\d+) \(row (\d+),")


def load_triples() -> pd.DataFrame:
    rows = []
    for line in (L.OVERNIGHT / "s3_edits.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if not r["edit_ok"]:
            continue
        det = r.get("corrupt_det") if r.get("numeric_ok") else None
        rows.append({"row": int(r["row"]), "stim_idx": int(r["stim_idx"]), "claim_idx": int(r["claim_idx"]),
                     "n_claims": int(r["n_claims"]), "claim": r["claim"], "corrupt": r["corrupt"],
                     "paraphrase": r["paraphrase"], "corrupt_det": det, "has_det": det is not None})
    df = pd.DataFrame(rows).sort_values("row").reset_index(drop=True)
    assert len(df) == 490, len(df)
    return df


def fixed_examples() -> list[tuple[int, int]]:
    """(k, row) of the 10 fixed S3 example rows, read from s3_summary.md."""
    out = []
    for line in (L.OVERNIGHT / "s3_summary.md").read_text().splitlines():
        m = EXAMPLE_RE.match(line)
        if m:
            out.append((int(m.group(1)), int(m.group(2))))
    assert len(out) == 10, out
    return out


def texts_of(df: pd.DataFrame) -> list[str]:
    s = set()
    for v in VARIANTS:
        s.update(t for t in df[v].tolist() if t is not None)
    return sorted(s)


def target_phase(texts: list[str], timings: dict) -> dict:
    """Returns {text: (h_last, h_mean, n_tokens)} in fp32 numpy; cached in out/r1_target.npz."""
    cache_path = L.OUT / "r1_target.npz"
    if cache_path.exists():
        z = np.load(cache_path, allow_pickle=True)
        keys = list(z["texts"])
        if set(keys) == set(texts):
            L.log(f"target cache hit: {len(keys)} texts")
            return {t: (z["h_last"][i], z["h_mean"][i], int(z["n_tok"][i])) for i, t in enumerate(keys)}
    t0 = time.time()
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    h_last, h_mean, n_tok = [], [], []
    t0 = time.time()
    for k, t in enumerate(texts):
        ids = tgt.tok(t, return_tensors="pt", add_special_tokens=False)["input_ids"]
        assert ids.shape[1] >= 1, repr(t)
        hs = tgt.hidden_states(ids)[L.LAYER + 1][0]
        h_last.append(L.to_cpu_f32(hs[-1]).numpy())
        h_mean.append(L.to_cpu_f32(hs).numpy().mean(0))
        n_tok.append(int(ids.shape[1]))
        if k % 200 == 0:
            L.log(f"target {k}/{len(texts)} n_tok={ids.shape[1]}")
    timings["target_forward_s"] = time.time() - t0
    timings["target_n_forward"] = len(texts)
    tgt.free()
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    h_last = np.stack(h_last); h_mean = np.stack(h_mean); n_tok = np.array(n_tok)
    np.savez(cache_path, texts=np.array(texts, dtype=object), h_last=h_last, h_mean=h_mean, n_tok=n_tok)
    return {t: (h_last[i], h_mean[i], int(n_tok[i])) for i, t in enumerate(texts)}


def ar_phase(texts: list[str], timings: dict) -> dict:
    cache_path = L.OUT / "r1_ar.npz"
    if cache_path.exists():
        z = np.load(cache_path, allow_pickle=True)
        keys = list(z["texts"])
        if set(keys) == set(texts):
            L.log(f"AR cache hit: {len(keys)} texts")
            return {t: z["pred"][i] for i, t in enumerate(keys)}
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    preds = []
    t0 = time.time()
    for k, t in enumerate(texts):
        preds.append(ar.predict(t).numpy())
        if k % 200 == 0:
            L.log(f"AR {k}/{len(texts)}")
    timings["ar_forward_s"] = time.time() - t0
    timings["ar_n_forward"] = ar.n_forward
    ar.free()
    preds = np.stack(preds)
    np.savez(cache_path, texts=np.array(texts, dtype=object), pred=preds)
    return {t: preds[i] for i, t in enumerate(texts)}


def main():
    S = L.Settings("r1", min_n=MIN_N, inputs="s3_edits.jsonl rows with edit_ok (490); corrupt_det where numeric_ok and non-null",
                   target_encoding="raw claim text, no chat template, add_special_tokens=False, hidden_states[LAYER+1]; last token and mean over tokens",
                   ar_encoding="AR template on the single claim text, value_head output",
                   distance="d = 1 - cos(fp32)",
                   kill="S_T = d_corr_T - d_para_T (last token); MET if CI95 hi <= 0; NOT MET if lo > 0; else INCONCLUSIVE; INCONCLUSIVE if n < 300",
                   bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0",
                   examples="the 10 fixed S3 example rows parsed from s3_summary.md")
    timings = {}
    df = load_triples()
    texts = texts_of(df)
    L.log(f"{len(df)} accepted triples, {int(df.has_det.sum())} with corrupt_det, {len(texts)} distinct texts")
    S.update(n_triples=int(len(df)), n_with_det=int(df.has_det.sum()), n_distinct_texts=len(texts))

    T = target_phase(texts, timings)
    A = ar_phase(texts, timings)

    def dist(x, y):
        return 1.0 - L.cos(x, y)

    rows = []
    for r in df.itertuples():
        c = r.claim
        o = {"row": r.row, "stim_idx": r.stim_idx, "claim_idx": r.claim_idx, "n_claims": r.n_claims,
             "split": L.split_of(r.stim_idx), "has_det": r.has_det,
             "n_tok_claim": T[c][2], "n_tok_corrupt": T[r.corrupt][2], "n_tok_paraphrase": T[r.paraphrase][2]}
        for side, hidx in [("T_last", 0), ("T_mean", 1)]:
            o[f"d_corr_{side}"] = dist(T[c][hidx], T[r.corrupt][hidx])
            o[f"d_para_{side}"] = dist(T[c][hidx], T[r.paraphrase][hidx])
            o[f"d_det_{side}"] = dist(T[c][hidx], T[r.corrupt_det][hidx]) if r.has_det else np.nan
        o["d_corr_AR"] = dist(A[c], A[r.corrupt])
        o["d_para_AR"] = dist(A[c], A[r.paraphrase])
        o["d_det_AR"] = dist(A[c], A[r.corrupt_det]) if r.has_det else np.nan
        for side in ["T_last", "T_mean", "AR"]:
            o[f"S_{side}"] = o[f"d_corr_{side}"] - o[f"d_para_{side}"]
            o[f"S_det_{side}"] = o[f"d_det_{side}"] - o[f"d_para_{side}"] if r.has_det else np.nan
            o[f"ratio_{side}"] = o[f"d_corr_{side}"] / o[f"d_para_{side}"] if o[f"d_para_{side}"] > 0 else np.nan
        o["claim"] = c; o["corrupt"] = r.corrupt; o["paraphrase"] = r.paraphrase; o["corrupt_det"] = r.corrupt_det
        rows.append(o)
    sc = pd.DataFrame(rows)
    sc.to_csv(L.OVERNIGHT / "r1_scores.csv", index=False)
    ev = sc[sc.split == "eval"]
    assert len(ev) == len(sc), "all S3 triples are evaluation-set claims"

    # ---------------- kill test (computed and appended first)
    ci_ST = L.cluster_bootstrap_mean(ev.S_T_last, ev.stim_idx)
    r1_out = L.outcome_ci_at_or_below(ci_ST, 0.0, min_n=MIN_N)
    ci_dcT = L.cluster_bootstrap_mean(ev.d_corr_T_last, ev.stim_idx)
    ci_dpT = L.cluster_bootstrap_mean(ev.d_para_T_last, ev.stim_idx)
    k_r1 = L.append_disconfirmation("R1", "R1", "CI95 of mean(d_corr_T − d_para_T), last-token, n>=300, ≤ 0",
                                    f"mean d_corr_T={ci_dcT['mean']:.5f} [{ci_dcT['lo']:.5f},{ci_dcT['hi']:.5f}]; mean d_para_T={ci_dpT['mean']:.5f} [{ci_dpT['lo']:.5f},{ci_dpT['hi']:.5f}]; "
                                    f"mean S_T={ci_ST['mean']:.5f} CI95=[{ci_ST['lo']:.5f},{ci_ST['hi']:.5f}] n={ci_ST['n']} n_expl={ci_ST['n_clusters']}",
                                    r1_out, "MET would mean the target's own layer-20 representation of the claim text is no more sensitive to the factual change than to rewording (blindness upstream of the AR)")

    # ---------------- secondary statistics
    stats = {}
    for side in ["T_last", "T_mean", "AR"]:
        stats[side] = {
            "d_corr": L.cluster_bootstrap_mean(ev[f"d_corr_{side}"], ev.stim_idx),
            "d_para": L.cluster_bootstrap_mean(ev[f"d_para_{side}"], ev.stim_idx),
            "d_det": L.cluster_bootstrap_mean(ev[f"d_det_{side}"], ev.stim_idx),
            "S": L.cluster_bootstrap_mean(ev[f"S_{side}"], ev.stim_idx),
            "S_det": L.cluster_bootstrap_mean(ev[f"S_det_{side}"], ev.stim_idx),
            "frac_corr_gt_para": L.cluster_bootstrap_mean((ev[f"d_corr_{side}"] > ev[f"d_para_{side}"]).astype(float), ev.stim_idx),
            "ratio_of_means": float(ev[f"d_corr_{side}"].mean() / ev[f"d_para_{side}"].mean()),
            "median_item_ratio": float(ev[f"ratio_{side}"].median()),
            "ratio_of_means_det": float(ev[f"d_det_{side}"].mean() / ev.loc[ev.has_det, f"d_para_{side}"].mean()),
        }
        stats[side]["outcome_S"] = L.outcome_ci_at_or_below(stats[side]["S"], 0.0, min_n=MIN_N)
    from scipy.stats import spearmanr
    rho_TA_corr = spearmanr(ev.d_corr_T_last, ev.d_corr_AR)
    rho_TA_para = spearmanr(ev.d_para_T_last, ev.d_para_AR)
    rho_S = spearmanr(ev.S_T_last, ev.S_AR)

    # ---------------- report
    def ci_s(ci, p=5):
        return f"{ci['mean']:.{p}f} [{ci['lo']:.{p}f}, {ci['hi']:.{p}f}] (n={ci['n']})"
    lines = ["# R1 summary — fact-blindness locus: target layer-20 representation vs reconstructor (490 accepted S3 triples, all evaluation set)", "",
             f"git {L.git_hash()[:8]}; settings in r1_settings.json", "",
             f"- triples: {len(ev)}; with corrupt_det: {int(ev.has_det.sum())}; explanations: {ev.stim_idx.nunique()}; distinct texts scored: {len(texts)}",
             f"- claim length (TARGET tokens): mean {ev.n_tok_claim.mean():.1f}, min {ev.n_tok_claim.min()}, max {ev.n_tok_claim.max()}", "",
             "## 2x2 table: mean d = 1 − cos (cluster-bootstrap CI95 by explanation)", "",
             "| side | d_corr (c vs c*) | d_para (c vs c~) | S = d_corr − d_para | outcome(CI≤0) | ratio of means d_corr/d_para | median item ratio | frac d_corr > d_para |",
             "|---|---|---|---|---|---|---|---|"]
    names = {"T_last": "TARGET last token", "T_mean": "TARGET mean over tokens", "AR": "AR (value head)"}
    for side in ["T_last", "T_mean", "AR"]:
        s = stats[side]
        lines.append(f"| {names[side]} | {ci_s(s['d_corr'])} | {ci_s(s['d_para'])} | {ci_s(s['S'])} | {s['outcome_S']} | {s['ratio_of_means']:.4f} | {s['median_item_ratio']:.4f} | {ci_s(s['frac_corr_gt_para'], 4)} |")
    lines += ["", "## Deterministic corruption (corrupt_det; number/name swap) where present", "",
              "| side | d_det (c vs c_det) | S_det = d_det − d_para | ratio of means d_det/d_para |", "|---|---|---|---|"]
    for side in ["T_last", "T_mean", "AR"]:
        s = stats[side]
        lines.append(f"| {names[side]} | {ci_s(s['d_det'])} | {ci_s(s['S_det'])} | {s['ratio_of_means_det']:.4f} |")
    lines += ["", "## Cross-side agreement (Spearman, per triple)", "",
              f"- rho(d_corr_T_last, d_corr_AR) = {rho_TA_corr.statistic:.4f} (p={rho_TA_corr.pvalue:.3g})",
              f"- rho(d_para_T_last, d_para_AR) = {rho_TA_para.statistic:.4f} (p={rho_TA_para.pvalue:.3g})",
              f"- rho(S_T_last, S_AR) = {rho_S.statistic:.4f} (p={rho_S.pvalue:.3g})", "",
              "## Distributions (evaluation triples)", "", "| quantity | mean | median | p10 | p90 |", "|---|---|---|---|---|"]
    for col in ["d_corr_T_last", "d_para_T_last", "d_det_T_last", "d_corr_T_mean", "d_para_T_mean", "d_det_T_mean", "d_corr_AR", "d_para_AR", "d_det_AR"]:
        x = ev[col].dropna()
        lines.append(f"| {col} | {x.mean():.5f} | {x.median():.5f} | {x.quantile(0.1):.5f} | {x.quantile(0.9):.5f} |")
    lines += ["", "## Kill test", "", f"- {k_r1}", "",
              "## 10 fixed S3 example rows (verbatim) with their four d values", ""]
    byrow = sc.set_index("row")
    for k, row in fixed_examples():
        if row not in byrow.index:
            lines.append(f"### accepted #{k} (row {row}): not in the R1 triple set"); continue
        e = byrow.loc[row]
        lines += [f"### accepted #{k} (row {row}, stim {e.stim_idx}, claim {e.claim_idx}/{e.n_claims})",
                  f"- original:   {e.claim}", f"- corrupted:  {e.corrupt}", f"- paraphrase: {e.paraphrase}", f"- corrupt_det: {e.corrupt_det}",
                  f"- d_corr_T={e.d_corr_T_last:.5f}  d_para_T={e.d_para_T_last:.5f}  d_corr_AR={e.d_corr_AR:.5f}  d_para_AR={e.d_para_AR:.5f}  "
                  f"(mean-pooled: d_corr_T_mean={e.d_corr_T_mean:.5f} d_para_T_mean={e.d_para_T_mean:.5f}; det: d_det_T={e.d_det_T_last:.5f} d_det_AR={e.d_det_AR:.5f})", ""]
    lines += ["## Timings", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    (L.OVERNIGHT / "r1_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, k_r1=ci_ST, outcome=r1_out,
             stats={side: {k: v for k, v in s.items()} for side, s in stats.items()})
    L.log(f"R1 done: S_T={ci_ST['mean']:.5f} [{ci_ST['lo']:.5f},{ci_ST['hi']:.5f}] {r1_out}; S_AR={stats['AR']['S']['mean']:.5f}")


if __name__ == "__main__":
    main()

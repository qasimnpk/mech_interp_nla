"""S2 — claim deletion: does the reconstructor distinguish edit types? (PLAN.md round 1)

  uv run python overnight/s2_deletion.py

AR only. Inputs: overnight/explanations.jsonl (S1), overnight/stimuli.csv + out/acts_L20.npz (S0),
out/recon_L20.npz (S1: AR(z) prediction and the empty-explanation prediction).
Fixed claim splitter; per-claim deletion delta vs matched superficial edits (randspan x3,
shuffle_words, shuffle_order). Kill test K2 on evaluation claims.
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

SENT_RE = re.compile(r"(?<=[.!?])\s+")
MARKER_RE = re.compile(r"^\s*(\d+[.)]|[-*•])\s*")
MIN_WORDS = 3
N_RANDSPAN = 3

S = L.Settings("s2", splitter="split on newlines, then (?<=[.!?])\\s+; strip; drop leading list marker ^\\s*(\\d+[.)]|[-*•])\\s*; drop pieces < 3 words (word count taken after marker removal)",
               min_words=MIN_WORDS, n_randspan=N_RANDSPAN,
               seeds={"randspan": "np.random.default_rng(1000 + row) for draws 1..3 (row = index in s2_claims.csv)",
                      "shuffle_words": "np.random.default_rng(1000 + row) (separate rng instance)",
                      "shuffle_order": "np.random.default_rng(5000 + stim_idx)"},
               randspan_rule="words = z.split(); start ~ U{0..len-k}; redraw (<=50) if [start,start+k) equals the word span of any claim; remaining words joined by single space",
               bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")


def split_claims(text: str) -> list[str]:
    out = []
    for line in text.split("\n"):
        for piece in SENT_RE.split(line):
            p = MARKER_RE.sub("", piece.strip()).strip()
            if len(p.split()) >= MIN_WORDS:
                out.append(p)
    return out


def claim_word_spans(z_words: list[str], claims: list[str]) -> list[tuple[int, int]]:
    """Word-index span [a,b) in z.split() of each claim (first exact match); (-1,-1) if none."""
    spans = []
    cursor = 0
    for c in claims:
        cw = c.split(); k = len(cw); found = (-1, -1)
        for a in range(cursor, len(z_words) - k + 1):
            if z_words[a:a + k] == cw:
                found = (a, a + k); cursor = a + k; break
        spans.append(found)
    return spans


def main():
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    rec = np.load(L.OUT / "recon_L20.npz")
    pred, pred_empty = rec["pred"], rec["pred_empty"]
    expl = {}
    for line in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); expl[r["stim_idx"]] = r
    ar = L.AR()
    cache: dict[str, np.ndarray] = {}

    def score(text: str, i: int) -> float:
        if text not in cache:
            cache[text] = ar.predict(text).numpy()
        return L.cos(cache[text], h20[i])

    claim_rows, expl_rows = [], []
    n_excluded = 0
    t0 = time.time()
    for i in range(len(df)):
        r = expl[i]
        z = r["explanation"] if r.get("explanation") is not None else (r.get("raw_generation") or "")
        claims = split_claims(z)
        cos_z = L.cos(pred[i], h20[i]) if not np.isnan(pred[i]).any() else float("nan")
        cos_empty = L.cos(pred_empty, h20[i])
        er = {"stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "split": L.split_of(i),
              "n_claims": len(claims), "cos_z": cos_z, "cos_empty": cos_empty, "Δcos_all": cos_empty - cos_z,
              "cos_z_joined": np.nan, "cos_shuffle_order": np.nan, "cos_best_single_deletion": np.nan, "error": None}
        if len(claims) < 2:
            n_excluded += 1
            expl_rows.append(er)
            continue
        try:
            joined = " ".join(claims)
            er["cos_z_joined"] = score(joined, i)
            order = np.random.default_rng(5000 + i).permutation(len(claims))
            er["cos_shuffle_order"] = score(" ".join(claims[k] for k in order), i)
            z_words = z.split()
            spans = claim_word_spans(z_words, claims)
            best = -np.inf
            for ci, c in enumerate(claims):
                row = len(claim_rows)
                cw = c.split(); k = len(cw)
                rest = " ".join(claims[:ci] + claims[ci + 1:])
                cos_del = score(rest, i)
                best = max(best, cos_del)
                cr = {"row": row, "stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "split": L.split_of(i),
                      "claim_idx": ci, "n_claims": len(claims), "n_words": k, "cos_z": cos_z,
                      "Δcos": cos_del - cos_z, "cos_alone": score(c, i), "claim": c}
                rng = np.random.default_rng(1000 + row)
                for d in range(1, N_RANDSPAN + 1):
                    if k >= len(z_words):
                        cr[f"Δcos_randspan_{d}"] = np.nan; continue
                    for _ in range(50):
                        a = int(rng.integers(0, len(z_words) - k + 1))
                        if (a, a + k) not in spans:
                            break
                    text = " ".join(z_words[:a] + z_words[a + k:])
                    cr[f"Δcos_randspan_{d}"] = score(text, i) - cos_z
                    cr[f"randspan_{d}_start"] = a
                rng2 = np.random.default_rng(1000 + row)
                sh = " ".join(cw[j] for j in rng2.permutation(k))
                cr["Δcos_shuffle_words"] = score(" ".join(claims[:ci] + [sh] + claims[ci + 1:]), i) - cos_z
                claim_rows.append(cr)
            er["cos_best_single_deletion"] = best
        except Exception as e:
            er["error"] = traceback.format_exc()
            L.log(f"FAILED on {i}: {e}")
        expl_rows.append(er)
        if i % 20 == 0:
            L.log(f"{i}/200 claims so far {len(claim_rows)} forwards {ar.n_forward} ({(time.time()-t0)/max(1,ar.n_forward):.2f}s each)")
    ar.free()
    cl = pd.DataFrame(claim_rows); ex = pd.DataFrame(expl_rows)
    cl.to_csv(L.OVERNIGHT / "s2_claims.csv", index=False)
    ex.to_csv(L.OVERNIGHT / "s2_expl.csv", index=False)

    # ---------------- K2 on evaluation claims
    ev = cl[cl.split == "eval"].copy()
    rs_cols = [f"Δcos_randspan_{d}" for d in range(1, N_RANDSPAN + 1)]
    ev["abs_rs_mean"] = ev[rs_cols].abs().mean(axis=1)
    ev["D"] = ev["Δcos"].abs() - ev["abs_rs_mean"]
    ci_D = L.cluster_bootstrap_mean(ev.D, ev.stim_idx)
    k2_out = L.outcome_ci_at_or_below(ci_D, 0.0)
    exev = ex[(ex.split == "eval") & (ex.n_claims >= 2)]
    med_abs = float(ev["Δcos"].abs().median())
    ratio_flag = float(exev["Δcos_all"].abs().mean()) >= 5 * med_abs
    k2 = L.append_disconfirmation("S2", "K2", "CI95 of mean(|Δcos_claim| − mean|Δcos_randspan|) ≤ 0",
                                  f"mean D={ci_D['mean']:.5f} CI95=[{ci_D['lo']:.5f},{ci_D['hi']:.5f}] n_claims={ci_D['n']} n_expl={ci_D['n_clusters']}; "
                                  f"mean|Δcos_all|={exev['Δcos_all'].abs().mean():.4f} vs 5×median|Δcos_i|={5*med_abs:.4f} (>=: {ratio_flag})",
                                  k2_out, "MET would mean deleting a whole claim is indistinguishable from deleting a random equal-length span")

    # ---------------- report
    def dist(s, cluster=None):
        s = pd.Series(s).astype(float)
        m = s.notna()
        txt = f"mean {s[m].mean():.5f} | median {s[m].median():.5f} | p10 {s[m].quantile(0.1):.5f} | p90 {s[m].quantile(0.9):.5f} | n {int(m.sum())}"
        if cluster is not None:
            ci = L.cluster_bootstrap_mean(s[m], np.asarray(cluster)[m.values])
            txt += f" | CI95 [{ci['lo']:.5f}, {ci['hi']:.5f}]"
        return txt

    def frac_pos(sub):
        ind = (sub["Δcos"] > 0).astype(float)
        ci = L.cluster_bootstrap_mean(ind, sub.stim_idx)
        return f"{ci['mean']:.4f} CI95 [{ci['lo']:.4f}, {ci['hi']:.4f}] n={ci['n']}"

    lines = ["# S2 summary — claim deletion (evaluation claims unless stated)", "",
             f"git {L.git_hash()[:8]}; settings in s2_settings.json; AR forwards {ar.n_forward}, wall {time.time()-t0:.0f}s", "",
             f"- explanations: 200 total; kept (>=2 claims) {int((ex.n_claims >= 2).sum())}; excluded {n_excluded}; eval kept {len(exev)}; errors {int(ex.error.notna().sum())}",
             f"- claims: total {len(cl)}; eval {len(ev)}; pilot {int((cl.split == 'pilot').sum())}", "",
             "n_claims histogram (all 200 explanations): " + ", ".join(f"{k}:{v}" for k, v in sorted(ex.n_claims.value_counts().items())), "",
             "## Δcos (deleting claim i from z) and controls — evaluation claims", "", "| quantity | distribution |", "|---|---|",
             f"| Δcos (claim deletion) | {dist(ev['Δcos'], ev.stim_idx)} |",
             f"| \\|Δcos\\| | {dist(ev['Δcos'].abs(), ev.stim_idx)} |"]
    for c in rs_cols:
        lines.append(f"| {c} | {dist(ev[c], ev.stim_idx)} |")
    lines += [f"| mean\\|Δcos_randspan\\| (3 draws) | {dist(ev['abs_rs_mean'], ev.stim_idx)} |",
              f"| Δcos_shuffle_words | {dist(ev['Δcos_shuffle_words'], ev.stim_idx)} |",
              f"| cos_alone | {dist(ev['cos_alone'], ev.stim_idx)} |",
              f"| D = \\|Δcos\\| − mean\\|Δcos_randspan\\| | {dist(ev['D'], ev.stim_idx)} |",
              "", "### per explanation (evaluation, kept)", "", "| quantity | distribution |", "|---|---|",
              f"| cos_z | {dist(exev.cos_z)} |", f"| cos_z_joined (claims re-joined, nothing deleted) | {dist(exev.cos_z_joined)} |",
              f"| cos_empty | {dist(exev.cos_empty)} |", f"| Δcos_all = cos_empty − cos_z | {dist(exev['Δcos_all'])} |",
              f"| cos_shuffle_order − cos_z | {dist(exev.cos_shuffle_order - exev.cos_z)} |",
              f"| cos_best_single_deletion − cos_z | {dist(exev.cos_best_single_deletion - exev.cos_z)} |",
              "", f"- \\|Δcos_all\\| mean = {exev['Δcos_all'].abs().mean():.5f}; 5 × median \\|Δcos_i\\| = {5*med_abs:.5f}; mean\\|Δcos_all\\| ≥ 5×median\\|Δcos_i\\|: {ratio_flag}",
              "", "## Fraction of claims with Δcos > 0 (deletion improves reconstruction)", "",
              f"- overall: {frac_pos(ev)}",
              f"- first claim: {frac_pos(ev[ev.claim_idx == 0])}",
              f"- middle claims: {frac_pos(ev[(ev.claim_idx > 0) & (ev.claim_idx < ev.n_claims - 1)])}",
              f"- last claim: {frac_pos(ev[ev.claim_idx == ev.n_claims - 1])}"]
    for c in rs_cols + ["Δcos_shuffle_words"]:
        ind = (ev[c] > 0).astype(float); m = ev[c].notna()
        ci = L.cluster_bootstrap_mean(ind[m], ev.stim_idx[m])
        lines.append(f"- fraction {c} > 0: {ci['mean']:.4f} CI95 [{ci['lo']:.4f}, {ci['hi']:.4f}]")
    rho = spearmanr(ev.n_words, ev["Δcos"])
    lines += ["", f"- Spearman(n_words, Δcos): rho={rho.statistic:.4f} p={rho.pvalue:.3g}",
              f"- Spearman(n_words, |Δcos|): rho={spearmanr(ev.n_words, ev['Δcos'].abs()).statistic:.4f}",
              "", "## Kill test", "", f"- {k2}", ""]
    (L.OVERNIGHT / "s2_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(k2=ci_D, n_forward=ar.n_forward, n_excluded=n_excluded)
    L.log("S2 done")


if __name__ == "__main__":
    main()

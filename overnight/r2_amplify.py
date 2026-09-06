"""R2 — amplified corruption, AR only (PLAN.md round 2).

  uv run python overnight/r2_amplify.py

For each evaluation explanation with >= 2 accepted S3 claims (edit_ok):
  z**   = every accepted claim replaced by its LLM corruption (unaccepted claims kept original)
  z~~   = every accepted claim replaced by its LLM paraphrase
  z*det = every claim with corrupt_det present replaced by it (others original)
Claims and their order come from s2_claims.csv (eval rows); the edited explanation is the
space-joined claim list, exactly as S3 built z_edit. cos(z) is the S1 reconstruction of the
original explanation text (recon_L20.npz, regenerated in R0); cos(z_joined) is reported too.
Kill test R2: CI95 of mean[(cos z − cos z**) − (cos z − cos z~~)] <= 0 -> MET.
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

MIN_ACCEPTED_PER_EXPL = 2


def main():
    S = L.Settings("r2", min_accepted_per_expl=MIN_ACCEPTED_PER_EXPL,
                   construction="z** / z~~ / z*det = ' '.join(claims with every accepted (resp. det-present) claim replaced); claims from s2_claims.csv eval rows in claim_idx order; edits from s3_edits.jsonl",
                   cos_z="cos(AR(original explanation text), h20) from out/recon_L20.npz (R0 regeneration)",
                   kill="CI95 of mean[(cos z − cos z**) − (cos z − cos z~~)] <= 0 -> MET; lo > 0 -> NOT MET; else INCONCLUSIVE",
                   bootstrap="cluster by explanation (stim_idx) = one row per explanation, 1000 draws, seed 0")
    timings = {}
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    rec = np.load(L.OUT / "recon_L20.npz")
    pred, pred_empty = rec["pred"], rec["pred_empty"]
    cl = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    cl = cl[cl.split == "eval"]
    claims_by_stim = {int(i): list(g.sort_values("claim_idx").claim) for i, g in cl.groupby("stim_idx")}
    edits = {}
    for line in (L.OVERNIGHT / "s3_edits.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); edits[(int(r["stim_idx"]), int(r["claim_idx"]))] = r

    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    cache = {}

    def score(text, i):
        if text not in cache:
            cache[text] = ar.predict(text).numpy()
        return L.cos(cache[text], h20[i])

    rows = []
    n_skipped = 0
    t0 = time.time()
    for i in sorted(claims_by_stim):
        cs = claims_by_stim[i]
        n = len(cs)
        acc = [bool(edits.get((i, k), {}).get("edit_ok", False)) for k in range(n)]
        det = [(edits.get((i, k), {}).get("corrupt_det") if edits.get((i, k), {}).get("numeric_ok") else None) for k in range(n)]
        det_present = [d is not None for d in det]
        er = {"stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "n_claims": n,
              "n_accepted": int(sum(acc)), "n_det": int(sum(det_present)),
              "cos_z": L.cos(pred[i], h20[i]), "cos_empty": L.cos(pred_empty, h20[i]),
              "cos_z_joined": np.nan, "cos_z_corrupt_all": np.nan, "cos_z_para_all": np.nan, "cos_z_det_all": np.nan,
              "included": sum(acc) >= MIN_ACCEPTED_PER_EXPL, "error": None}
        if not er["included"]:
            n_skipped += 1
            rows.append(er)
            continue
        try:
            z_c = " ".join(edits[(i, k)]["corrupt"] if acc[k] else cs[k] for k in range(n))
            z_p = " ".join(edits[(i, k)]["paraphrase"] if acc[k] else cs[k] for k in range(n))
            er["cos_z_joined"] = score(" ".join(cs), i)
            er["cos_z_corrupt_all"] = score(z_c, i)
            er["cos_z_para_all"] = score(z_p, i)
            if sum(det_present) >= MIN_ACCEPTED_PER_EXPL:
                z_d = " ".join(det[k] if det_present[k] else cs[k] for k in range(n))
                er["cos_z_det_all"] = score(z_d, i)
            er["z_corrupt_all"] = z_c; er["z_para_all"] = z_p
        except Exception as e:
            er["error"] = traceback.format_exc()
            L.log(f"FAILED on {i}: {e}")
        rows.append(er)
        if len(rows) % 40 == 0:
            L.log(f"{len(rows)}/{len(claims_by_stim)} explanations, forwards {ar.n_forward} ({(time.time()-t0)/max(1,ar.n_forward):.2f}s each)")
    timings["ar_forward_s"] = time.time() - t0
    timings["ar_n_forward"] = ar.n_forward
    ar.free()
    ex = pd.DataFrame(rows)
    ex["D_corrupt"] = ex.cos_z - ex.cos_z_corrupt_all
    ex["D_para"] = ex.cos_z - ex.cos_z_para_all
    ex["D_det"] = ex.cos_z - ex.cos_z_det_all
    ex["D_corrupt_minus_para"] = ex.D_corrupt - ex.D_para
    ex["D_det_minus_para"] = ex.D_det - ex.D_para
    ex["Dj_corrupt"] = ex.cos_z_joined - ex.cos_z_corrupt_all
    ex["Dj_para"] = ex.cos_z_joined - ex.cos_z_para_all
    ex.to_csv(L.OVERNIGHT / "r2_expl.csv", index=False)
    inc = ex[ex.included & ex.error.isna()]

    # ---------------- kill test
    ci_c = L.cluster_bootstrap_mean(inc.D_corrupt, inc.stim_idx)
    ci_p = L.cluster_bootstrap_mean(inc.D_para, inc.stim_idx)
    ci_cp = L.cluster_bootstrap_mean(inc.D_corrupt_minus_para, inc.stim_idx)
    r2_out = L.outcome_ci_at_or_below(ci_cp, 0.0)
    k_r2 = L.append_disconfirmation("R2", "R2", "CI95 of mean[(cos z − cos z**) − (cos z − cos z~~)] ≤ 0",
                                    f"mean cos z − cos z**={ci_c['mean']:.5f} [{ci_c['lo']:.5f},{ci_c['hi']:.5f}]; mean cos z − cos z~~={ci_p['mean']:.5f} [{ci_p['lo']:.5f},{ci_p['hi']:.5f}]; "
                                    f"paired diff={ci_cp['mean']:.5f} CI95=[{ci_cp['lo']:.5f},{ci_cp['hi']:.5f}] n_expl={ci_cp['n']}",
                                    r2_out, "MET would mean corrupting every claim of an explanation is indistinguishable from paraphrasing every claim")

    # ---------------- secondary
    frac = L.cluster_bootstrap_mean((inc.D_corrupt > inc.D_para).astype(float), inc.stim_idx)
    dd = inc.dropna(subset=["D_det"])
    ci_d = L.cluster_bootstrap_mean(dd.D_det, dd.stim_idx)
    ci_dp = L.cluster_bootstrap_mean(dd.D_det_minus_para, dd.stim_idx)
    frac_d = L.cluster_bootstrap_mean((dd.D_det > dd.D_para).astype(float), dd.stim_idx)
    ci_jc = L.cluster_bootstrap_mean(inc.Dj_corrupt, inc.stim_idx)
    ci_jp = L.cluster_bootstrap_mean(inc.Dj_para, inc.stim_idx)
    ci_all = L.cluster_bootstrap_mean(inc.cos_z - inc.cos_empty, inc.stim_idx)

    def ci_s(ci, p=5):
        return f"{ci['mean']:.{p}f} | {ci['lo']:.{p}f} | {ci['hi']:.{p}f} | {ci['n']}"
    lines = ["# R2 summary — amplified corruption (every accepted claim replaced), AR only, evaluation explanations", "",
             f"git {L.git_hash()[:8]}; settings in r2_settings.json; AR forwards {ar.n_forward}", "",
             f"- evaluation explanations with claims (S2): {len(ex)}; included (>= {MIN_ACCEPTED_PER_EXPL} accepted claims): {len(inc)}; excluded: {n_skipped}; errors: {int(ex.error.notna().sum())}",
             f"- explanations with >= {MIN_ACCEPTED_PER_EXPL} corrupt_det claims: {len(dd)}",
             f"- per included explanation: n_claims mean {inc.n_claims.mean():.2f}; n_accepted mean {inc.n_accepted.mean():.2f}; fraction of claims replaced {inc.n_accepted.sum()/inc.n_claims.sum():.3f}; n_det mean {inc.n_det.mean():.2f}", "",
             "## Headline (paired per explanation; cluster bootstrap CI95)", "",
             "| statistic | mean | CI95 lo | CI95 hi | n_expl |", "|---|---|---|---|---|",
             f"| cos(z) − cos(z**)  [all accepted claims corrupted] | {ci_s(ci_c)} |",
             f"| cos(z) − cos(z~~)  [all accepted claims paraphrased] | {ci_s(ci_p)} |",
             f"| (cos z − cos z**) − (cos z − cos z~~) | {ci_s(ci_cp)} |",
             f"| cos(z) − cos(z*det)  [all det-corruptible claims swapped] | {ci_s(ci_d)} |",
             f"| (cos z − cos z*det) − (cos z − cos z~~)  [same explanations] | {ci_s(ci_dp)} |",
             f"| cos(z_joined) − cos(z**) | {ci_s(ci_jc)} |",
             f"| cos(z_joined) − cos(z~~) | {ci_s(ci_jp)} |",
             f"| cos(z) − cos(empty)  [scale reference] | {ci_s(ci_all)} |", "",
             f"- fraction of explanations where corruption hurts more than paraphrase (D_corrupt > D_para): {frac['mean']:.4f} CI95 [{frac['lo']:.4f}, {frac['hi']:.4f}] n={frac['n']}",
             f"- same for deterministic corruption: {frac_d['mean']:.4f} CI95 [{frac_d['lo']:.4f}, {frac_d['hi']:.4f}] n={frac_d['n']}",
             f"- for comparison, S3 single-claim: cos(z) − cos(z*) 0.00313, cos(z) − cos(z~) 0.00494, A − P −0.00181 (s3_summary.md)", "",
             "## Distributions (included explanations)", "", "| quantity | mean | median | p10 | p90 | n |", "|---|---|---|---|---|---|"]
    for col in ["cos_z", "cos_z_joined", "cos_z_corrupt_all", "cos_z_para_all", "cos_z_det_all", "cos_empty", "D_corrupt", "D_para", "D_det", "D_corrupt_minus_para"]:
        x = inc[col].dropna()
        lines.append(f"| {col} | {x.mean():.5f} | {x.median():.5f} | {x.quantile(0.1):.5f} | {x.quantile(0.9):.5f} | {len(x)} |")
    lines += ["", "## By number of replaced claims", "", "| n_accepted | n_expl | mean D_corrupt | mean D_para | mean diff |", "|---|---|---|---|---|"]
    for na, g in inc.groupby("n_accepted"):
        lines.append(f"| {na} | {len(g)} | {g.D_corrupt.mean():.5f} | {g.D_para.mean():.5f} | {g.D_corrupt_minus_para.mean():.5f} |")
    lines += ["", "## Kill test", "", f"- {k_r2}", "", "## Timings", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    lines += ["", "## 5 included explanations chosen by seed 0 (verbatim z** and z~~)", ""]
    pick = np.random.default_rng(0).choice(inc.stim_idx.values, 5, replace=False)
    for i in sorted(pick):
        e = inc[inc.stim_idx == i].iloc[0]
        lines += [f"### stim {i} n_claims={e.n_claims} n_accepted={e.n_accepted} cos_z={e.cos_z:.4f} cos_z**={e.cos_z_corrupt_all:.4f} cos_z~~={e.cos_z_para_all:.4f}",
                  "- z**: " + str(e.z_corrupt_all), "- z~~: " + str(e.z_para_all), ""]
    (L.OVERNIGHT / "r2_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, k_r2=ci_cp, outcome=r2_out, n_included=int(len(inc)), n_excluded=n_skipped,
             D_corrupt=ci_c, D_para=ci_p, D_det=ci_d, D_det_minus_para=ci_dp, frac_corrupt_worse=frac)
    L.log(f"R2 done: diff={ci_cp['mean']:.5f} [{ci_cp['lo']:.5f},{ci_cp['hi']:.5f}] {r2_out}")


if __name__ == "__main__":
    main()

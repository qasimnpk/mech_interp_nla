"""C1 — position vs content: does the last snippet dominate because of what it says or where it sits?
(PLAN.md round 3; AR only.)

  uv run python overnight/c1_position.py

For each evaluation explanation (stimuli 40-199) with >= 3 claims (claims from s2_claims.csv, in
claim_idx order; "local snippet" = the last claim, claim_idx = n_claims-1):
  z_rot   = ' '.join([claims[-1]] + claims[:-1])     last claim moved to the FRONT, rest in order
  z_rev   = ' '.join(claims[::-1])                    claims reversed
  z_rot-snip  = z_rot with the snippet deleted  (= ' '.join(claims[:-1]), the S2 `rest`, recomputed)
  z_rot-last  = z_rot with its now-last claim (claims[-2]) deleted
  z_rev-snip  = z_rev with the snippet deleted
Deletion cost = cos(text) - cos(text minus claim).  Cost in z is taken from S2 (s2_claims.csv:
-Δcos of the last claim = cos_z - cos(rest)); a joined-text version cos(z_joined) - cos(rest) is
also reported (cos_z_joined from s3_scores.csv, cos(rest) recomputed here) because z_rot is
space-joined while z carries newlines.
Kill C1 (pre-registered): paired CI of [snippet deletion cost in z_rot - in z] <= -0.05 -> MET.
Cluster bootstrap by explanation (stim_idx), 1000 draws, seed 0. Raw outputs incl. failures kept.
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

THRESH = -0.05
MIN_CLAIMS = 3


def main():
    S = L.Settings("c1", threshold=THRESH, min_claims=MIN_CLAIMS, evaluation_set="stimuli 40-199",
                   construction={"z_rot": "' '.join([claims[-1]] + claims[:-1])", "z_rev": "' '.join(claims[::-1])",
                                 "z_rot_minus_snippet": "' '.join(claims[:-1])", "z_rot_minus_newlast": "' '.join([claims[-1]] + claims[:-2])",
                                 "z_rev_minus_snippet": "' '.join(claims[:-1][::-1])"},
                   cost_definition="deletion cost = cos(text) - cos(text minus claim); cost in z from S2 = -Δcos (s2_claims.csv)",
                   bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")
    timings = {}
    cl = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    s3 = pd.read_csv(L.OVERNIGHT / "s3_scores.csv", keep_default_na=False)
    joined = s3.groupby("stim_idx").cos_z_joined.first().to_dict()
    acts = np.load(L.OUT / "acts_L20.npz")
    h20 = acts["h20"]
    ev = cl[(cl.split == "eval") & (cl.n_claims >= MIN_CLAIMS)]
    stims = sorted(ev.stim_idx.unique())
    L.log(f"eval explanations with >= {MIN_CLAIMS} claims: {len(stims)}")

    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0

    def score(text, i):
        return L.cos(ar.predict(text), h20[i])

    rows = []
    t0 = time.time()
    for i in stims:
        g = ev[ev.stim_idx == i].sort_values("claim_idx")
        cs = list(g.claim)
        n = len(cs)
        last = g[g.claim_idx == n - 1].iloc[0]
        prev = g[g.claim_idx == n - 2].iloc[0]
        row = {"stim_idx": i, "doc_idx": int(g.doc_idx.iloc[0]), "n_claims": n,
               "cos_z": float(last.cos_z), "cos_z_joined": float(joined.get(i, np.nan)),
               "cost_snippet_in_z_s2": -float(last["Δcos"]), "cost_prev_in_z_s2": -float(prev["Δcos"]),
               "snippet_n_words": int(last.n_words), "snippet_is_final_token_claim": "inal token" in last.claim,
               "z_rot": " ".join([cs[-1]] + cs[:-1]), "z_rev": " ".join(cs[::-1]),
               "z_rot_minus_snippet": " ".join(cs[:-1]), "z_rot_minus_newlast": " ".join([cs[-1]] + cs[:-2]),
               "z_rev_minus_snippet": " ".join(cs[:-1][::-1]), "error": ""}
        try:
            row["cos_z_rot"] = score(row["z_rot"], i)
            row["cos_z_rev"] = score(row["z_rev"], i)
            row["cos_z_rot_minus_snippet"] = score(row["z_rot_minus_snippet"], i)
            row["cos_z_rot_minus_newlast"] = score(row["z_rot_minus_newlast"], i)
            row["cos_z_rev_minus_snippet"] = score(row["z_rev_minus_snippet"], i)
            row["cost_snippet_in_z_rot"] = row["cos_z_rot"] - row["cos_z_rot_minus_snippet"]
            row["cost_snippet_in_z_rev"] = row["cos_z_rev"] - row["cos_z_rev_minus_snippet"]
            row["cost_newlast_in_z_rot"] = row["cos_z_rot"] - row["cos_z_rot_minus_newlast"]
            row["cost_snippet_in_z_joined"] = row["cos_z_joined"] - row["cos_z_rot_minus_snippet"]  # rest is identical text
            row["diff_rot_minus_z"] = row["cost_snippet_in_z_rot"] - row["cost_snippet_in_z_s2"]
            row["diff_rot_minus_zjoined"] = row["cost_snippet_in_z_rot"] - row["cost_snippet_in_z_joined"]
            row["diff_rev_minus_z"] = row["cost_snippet_in_z_rev"] - row["cost_snippet_in_z_s2"]
            row["diff_newlast_minus_prev"] = row["cost_newlast_in_z_rot"] - row["cost_prev_in_z_s2"]
        except Exception:
            row["error"] = traceback.format_exc()
            L.log(f"AR FAILED on {i}")
        rows.append(row)
        if len(rows) % 40 == 0:
            L.log(f"{len(rows)}/{len(stims)} forwards {ar.n_forward} ({(time.time() - t0) / max(1, ar.n_forward):.2f}s each)")
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward)
    timings["n_forward"] = ar.n_forward
    ar.free()

    df = pd.DataFrame(rows)
    df.to_csv(L.OVERNIGHT / "c1_expl.csv", index=False)
    ok = df[df.error == ""]

    def ci_of(col):
        return L.cluster_bootstrap_mean(ok[col], ok.stim_idx)

    def fmt(c, d=4):
        return f"{c['mean']:.{d}f} CI95=[{c['lo']:.{d}f},{c['hi']:.{d}f}] n={c['n']}"

    ci_main = ci_of("diff_rot_minus_z")
    out = L.outcome_ci_at_or_below(ci_main, THRESH, min_n=100)
    L.append_disconfirmation("C1", "C1", "paired CI95 of [snippet deletion cost in z_rot − in z] ≤ −0.05",
                             f"mean diff={fmt(ci_main, 5)}; cost in z (S2)={ok.cost_snippet_in_z_s2.mean():.4f}; cost in z_rot={ok.cost_snippet_in_z_rot.mean():.4f}; n_expl={len(ok)}",
                             out, "MET would mean the final snippet loses most of its weight when moved to the front: dominance is positional, not content")
    ci_joined = ci_of("diff_rot_minus_zjoined")
    out_joined = L.outcome_ci_at_or_below(ci_joined, THRESH, min_n=100)
    L.append_disconfirmation("C1", "C1-joined", "same statistic with cost in z computed from the space-joined z (secondary, not a pre-registered kill)",
                             f"mean diff={fmt(ci_joined, 5)}; cost in z_joined={ok.cost_snippet_in_z_joined.mean():.4f}; n_expl={len(ok)}",
                             out_joined, "joined-text baseline removes the newline/space formatting difference between z and z_rot")

    lines = ["# C1 summary — position vs content (evaluation explanations with >= 3 claims, AR only)", "",
             f"git {L.git_hash()[:8]}; settings in c1_settings.json; raw rows in c1_expl.csv", "",
             f"- explanations: {len(df)} (errors {int((df.error != '').sum())}); AR forwards {timings['n_forward']}; {timings['ar_s_per_score']:.2f} s/score",
             f"- snippet (last claim) is a 'Final token' claim in {int(ok.snippet_is_final_token_claim.sum())}/{len(ok)} explanations",
             "", "## Kill C1", "",
             f"- paired diff [cost_snippet_in_z_rot − cost_snippet_in_z (S2)]: {fmt(ci_main, 5)}  threshold ≤ {THRESH} → **{out}**",
             f"- secondary (joined baseline) [cost_snippet_in_z_rot − cost_snippet_in_z_joined]: {fmt(ci_joined, 5)} → {out_joined}",
             "", "## Reconstruction of the rearranged texts", "", "| text | mean cos | CI95 |", "|---|---|---|"]
    for name, col in [("z (original, S2)", "cos_z"), ("z_joined (space-joined, S3)", "cos_z_joined"), ("z_rot (snippet first)", "cos_z_rot"),
                      ("z_rev (reversed)", "cos_z_rev"), ("z_rot − snippet (= rest)", "cos_z_rot_minus_snippet"),
                      ("z_rot − new last claim", "cos_z_rot_minus_newlast"), ("z_rev − snippet", "cos_z_rev_minus_snippet")]:
        c = ci_of(col); lines.append(f"| {name} | {c['mean']:.4f} | [{c['lo']:.4f},{c['hi']:.4f}] |")
    lines += ["", "## Deletion costs (cos(text) − cos(text minus claim))", "", "| quantity | mean | CI95 | median | frac > 0 |", "|---|---|---|---|---|"]
    for name, col in [("snippet in z (S2, −Δcos)", "cost_snippet_in_z_s2"), ("snippet in z_joined", "cost_snippet_in_z_joined"),
                      ("snippet in z_rot (moved to front)", "cost_snippet_in_z_rot"), ("snippet in z_rev (first position)", "cost_snippet_in_z_rev"),
                      ("claim[-2] in z (S2)", "cost_prev_in_z_s2"), ("claim[-2] when last in z_rot", "cost_newlast_in_z_rot")]:
        c = ci_of(col); lines.append(f"| {name} | {c['mean']:.4f} | [{c['lo']:.4f},{c['hi']:.4f}] | {ok[col].median():.4f} | {(ok[col] > 0).mean():.3f} |")
    lines += ["", "## Paired differences", "", "| difference | mean | CI95 | frac < 0 |", "|---|---|---|---|"]
    for name, col in [("snippet cost: z_rot − z (kill statistic)", "diff_rot_minus_z"), ("snippet cost: z_rot − z_joined", "diff_rot_minus_zjoined"),
                      ("snippet cost: z_rev − z", "diff_rev_minus_z"), ("claim[-2] cost: when last (z_rot) − in z", "diff_newlast_minus_prev")]:
        c = ci_of(col); lines.append(f"| {name} | {c['mean']:.5f} | [{c['lo']:.5f},{c['hi']:.5f}] | {(ok[col] < 0).mean():.3f} |")
    lines += ["", "Ratio of mean snippet cost in z_rot to mean snippet cost in z (S2): "
              f"{ok.cost_snippet_in_z_rot.mean() / ok.cost_snippet_in_z_s2.mean():.3f}; to z_joined: {ok.cost_snippet_in_z_rot.mean() / ok.cost_snippet_in_z_joined.mean():.3f}",
              "", "## Five fixed rows (stim 40, 72, 104, 136, 168)", ""]
    for i in [40, 72, 104, 136, 168]:
        r = df[df.stim_idx == i].iloc[0]
        lines += [f"### stim {i} (n_claims {r.n_claims})",
                  f"- cos_z {r.cos_z:.4f}  cos_z_rot {r.get('cos_z_rot', float('nan')):.4f}  cos_z_rev {r.get('cos_z_rev', float('nan')):.4f}",
                  f"- snippet cost in z {r.cost_snippet_in_z_s2:.4f}  in z_rot {r.get('cost_snippet_in_z_rot', float('nan')):.4f}  in z_rev {r.get('cost_snippet_in_z_rev', float('nan')):.4f}",
                  f"- z_rot: {r.z_rot}", ""]
    (L.OVERNIGHT / "c1_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, n_expl=len(df), n_errors=int((df.error != "").sum()), kill_C1={"ci": ci_main, "outcome": out},
             secondary_joined={"ci": ci_joined, "outcome": out_joined})
    L.log(f"C1 done: diff={ci_main['mean']:.5f} [{ci_main['lo']:.5f},{ci_main['hi']:.5f}] -> {out}")


if __name__ == "__main__":
    main()

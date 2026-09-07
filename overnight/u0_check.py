"""U0 — round-3b artifact check + T3 closeout (PLAN.md round 3b; no model, no kill test).

  uv run python overnight/u0_check.py

Asserts the round-3 artifacts reused by T2c/T2a/T2b/C3 exist with the expected row counts, reports the
T3 closeout (completed sample, stopping rule, kill line as written) from t3_summary.md / t3_outputs.jsonl /
t3_settings.json without rerunning anything, and re-budgets round 3b from round-3 measured costs.
Writes u0_check.md and u0_settings.json.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

EXPECT = {"c2_pairs": 40, "t2_scores": 200, "t2_claims_single_word_nonerror": 691, "t0_topics": 200, "c2_desc": 80, "acts_rows": 200, "c2_acts_rows": 80, "t1_scores": 200, "stimuli": 200}
COSTS = {"av_forward_s": 0.35, "av_generation_s": 10.0, "ar_score_s": 0.36, "target_short_forward_s": 0.11}
BUDGET = {  # forwards / generations per stage, from the PLAN stage texts
    "T2c": {"av_forward": 2 * 2 * (80 + 1) + 0, "note": "2 prefixes x 2 candidates x (80 activations + no-injection) = 484 (+ no-injection cached per pair)"},
    "T2a": {"av_forward": 200 * 2 * 3, "note": "200 stimuli x 2 candidates x (own, foreign, no-injection); no-injection cached by topic (~200)"},
    "T2b": {"av_forward": 691 * 2 * 2, "note": "691 rows x 2 words x 2 donors (pos2, foreign)"},
    "C3": {"target_short_forward": 80, "av_generation": 80, "ar_score": 40 * 16, "av_forward": 4 * 2 * 40, "note": "80 new contexts; 16 AR scores per cell; p1 readout on 160 activations x 2 candidates"},
}


def main():
    S = L.Settings("u0", expected_counts=EXPECT, costs_from_round3=COSTS, budget=BUDGET)
    checks = []

    def chk(name, got, want):
        checks.append((name, got, want, got == want))
        assert got == want, (name, got, want)

    p = pd.read_csv(L.OVERNIGHT / "c2_pairs.csv"); chk("c2_pairs rows", len(p), EXPECT["c2_pairs"]); chk("c2_pairs errors", int(p.error.notna().sum()), 0)
    s = pd.read_csv(L.OVERNIGHT / "t2_scores.csv", keep_default_na=False); chk("t2_scores rows", len(s), EXPECT["t2_scores"]); chk("t2_scores errors", int((s.error != "").sum()), 0)
    c = pd.read_csv(L.OVERNIGHT / "t2_claims.csv", keep_default_na=False)
    sw = c[(c.error == "") & (c.single_word.astype(str) == "True")]
    chk("t2_claims single-word non-error rows", len(sw), EXPECT["t2_claims_single_word_nonerror"])
    chk("t2_claims LLM corrupt single-word", int((sw.edit_type == "corrupt").sum()), 298); chk("t2_claims det single-word", int((sw.edit_type == "corrupt_det").sum()), 393)
    t = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False); chk("t0_topics rows", len(t), EXPECT["t0_topics"])
    t1 = pd.read_csv(L.OVERNIGHT / "t1_scores.csv", keep_default_na=False); chk("t1_scores rows", len(t1), EXPECT["t1_scores"])
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False); chk("stimuli rows", len(st), EXPECT["stimuli"])
    nd = sum(1 for ln in (L.OVERNIGHT / "c2_descriptions.jsonl").read_text().splitlines() if ln.strip()); chk("c2_descriptions rows", nd, EXPECT["c2_desc"])
    a = np.load(L.OUT / "acts_L20.npz"); chk("acts_L20 h20 shape", tuple(a["h20"].shape), (200, 3584)); chk("acts_L20 h20_pos2 shape", tuple(a["h20_pos2"].shape), (200, 3584))
    ca = np.load(L.OUT / "c2_acts.npz"); chk("c2_acts H shape", tuple(ca["H"].shape), (40, 2, 3584)); chk("c2_acts rows", int(ca["H"].shape[0] * ca["H"].shape[1]), EXPECT["c2_acts_rows"])
    # cross-check: c2_acts pair order matches c2_pairs (cos(h_a,h_b) recomputed)
    rec = np.array([L.cos(ca["H"][i, 0], ca["H"][i, 1]) for i in range(40)])
    max_dev = float(np.max(np.abs(rec - p.cos_ha_hb.values)))
    checks.append(("c2_acts vs c2_pairs cos(h_a,h_b) max |dev|", max_dev, "<1e-4", max_dev < 1e-4)); assert max_dev < 1e-4
    # t2_prefix import-safety (Settings inside main)
    src = (L.OVERNIGHT / "t2_prefix.py").read_text()
    import_safe = "L.Settings(" in src.split("def main():")[1] and "L.Settings(" not in src.split("def main():")[0]
    checks.append(("t2_prefix.py Settings created inside main()", import_safe, True, import_safe))
    src2 = (L.OVERNIGHT / "c2_matched.py").read_text()
    import_safe2 = "L.Settings(" in src2.split("def main():")[1] and "L.Settings(" not in src2.split("def main():")[0]
    checks.append(("c2_matched.py Settings created inside main()", import_safe2, True, import_safe2))

    # ---------------- T3 closeout (report only)
    t3s = json.loads((L.OVERNIGHT / "t3_settings.json").read_text())
    t3o = [json.loads(ln) for ln in (L.OVERNIGHT / "t3_outputs.jsonl").read_text().splitlines() if ln.strip()]
    n_items = len(t3o); stims = sorted({r["stim_idx"] for r in t3o}); cells = sorted({(r["direction"], r["layer"], r["alpha"]) for r in t3o})
    per_stim = pd.Series([r["stim_idx"] for r in t3o]).value_counts().sort_index()
    kill_lines = [ln for ln in (L.OVERNIGHT / "DISCONFIRMATION.md").read_text().splitlines() if "  T3  T3  " in ln]
    runlog_t3 = [ln for ln in (L.OVERNIGHT / "RUNLOG.md").read_text().splitlines() if "  T3  " in ln]

    # ---------------- re-budget
    est = {}
    for k, v in BUDGET.items():
        est[k] = sum(v.get(m, 0) * COSTS[{"av_forward": "av_forward_s", "av_generation": "av_generation_s", "ar_score": "ar_score_s", "target_short_forward": "target_short_forward_s"}[m]]
                     for m in ["av_forward", "av_generation", "ar_score", "target_short_forward"]) / 60.0
    load_s = 6.0  # model load ~5-6 s each, from round-3 settings

    lines = ["# U0 check — round 3b artifact check + T3 closeout", "",
             f"git {L.git_hash()[:8]}; settings in u0_settings.json; no model loaded; no kill test", "",
             "## Artifact checks", "", "| check | got | expected | ok |", "|---|---|---|---|"]
    for name, got, want, ok in checks:
        lines.append(f"| {name} | {got} | {want} | {ok} |")
    lines += ["", f"- all {len(checks)} checks passed: {all(x[3] for x in checks)}",
              "", "## T3 closeout (report only; not rerun, not extended)", "",
              f"- pre-registered design: pilot stimuli 0–39 (n={t3s['n_pilot']}) × {len(t3s['directions'])} directions × {len(t3s['layers'])} layers × {len(t3s['alphas'])} α = {t3s['n_pilot'] * len(cells)} items; stage cap {t3s['cap_s']} s",
              f"- completed before the cap: {n_items} items = {len(stims)} pilot stimuli ({stims[0]}–{stims[-1]}) × {len(cells)} cells; items per stimulus min {int(per_stim.min())} max {int(per_stim.max())}; errors {t3s.get('n_errors')}; {t3s['timings']['s_per_item']:.1f} s/item; wall {t3s['wall_start']} → {t3s['wall_end']}",
              f"- stopping rule as pre-registered (PLAN round 3): stage cap (T0 re-budget: 'T3 111 min > cap, run stimulus-outer and cut at cap'); settings `stopped_at_stimulus` = {t3s['timings'].get('stopped_at_stimulus')}; round-3 PLAN execution order put T3 last ('dropped first under the hard stop')",
              f"- outcome rule as written in t3_settings.json: {t3s['outcome_rule']}",
              f"- kill T3 as written in t3_settings.json: outcome {t3s['kill_T3']['outcome']}; eligible cells {list(t3s['kill_T3']['eligible'].keys())}",
              "- kill line as written in DISCONFIRMATION.md:", "", "```"] + kill_lines + ["```", "", "- RUNLOG lines for T3:", "", "```"] + runlog_t3 + ["```", "",
              "## Re-budget from round-3 measured costs (hypotheses, not measurements)", "",
              f"- unit costs used: {COSTS}", "", "| stage | AV forwards | AV generations | AR scores | TARGET forwards | est. minutes (+ model loads) |", "|---|---|---|---|---|---|"]
    for k, v in BUDGET.items():
        lines.append(f"| {k} | {v.get('av_forward', 0)} | {v.get('av_generation', 0)} | {v.get('ar_score', 0)} | {v.get('target_short_forward', 0)} | {est[k]:.1f} |")
    lines += ["", f"- total estimated compute {sum(est.values()):.1f} min + loads; hard stop 2026-09-07T02:19:14 (2.5 h after the first round-3b RUNLOG line 2026-09-06T23:49:14); stage cap 45 min", ""]
    (L.OVERNIGHT / "u0_check.md").write_text("\n".join(lines) + "\n")
    S.finish(checks=[{"name": n, "got": str(g), "expected": str(w), "ok": bool(o)} for n, g, w, o in checks], t3_closeout={"n_items": n_items, "n_stimuli": len(stims), "n_cells": len(cells), "kill_outcome": t3s["kill_T3"]["outcome"]},
             estimate_minutes=est)
    L.log(f"U0 done: {len(checks)} checks, all ok={all(x[3] for x in checks)}; T3 closeout {n_items} items / {len(stims)} stimuli; estimate {sum(est.values()):.1f} min")


if __name__ == "__main__":
    main()

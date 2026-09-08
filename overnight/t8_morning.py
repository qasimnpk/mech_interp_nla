"""T8 — MORNING3c.md (PLAN.md round 3c). Assembles the round-3c report from the stage summaries, DISCONFIRMATION.md, RUNLOG.md,
FOLLOWUPS.md and u0c_check.md. No model, no new statistics: every number is copied from a stage artifact.

  uv run python overnight/t8_morning.py
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402

ROUND_PREFIX = "2026-09-08T"
STAGES = ["U0c", "U1", "X3", "X1", "N3", "N4", "X1b", "RT", "M", "T8"]


def read(name: str) -> str:
    p = L.OVERNIGHT / name
    return p.read_text() if p.exists() else ""


def section(md: str, start: str, end: str | None = None) -> str:
    """Lines from the line containing `start` up to (not including) the line containing `end`."""
    lines = md.splitlines(); out = []; on = False
    for ln in lines:
        if not on and start in ln:
            on = True
        elif on and end is not None and end in ln:
            break
        if on:
            out.append(ln)
    return "\n".join(out).strip()


def main():
    S = L.Settings("t8")
    disc = [ln for ln in read("DISCONFIRMATION.md").splitlines() if ln.startswith(ROUND_PREFIX)]
    runlog = [ln for ln in read("RUNLOG.md").splitlines() if ln.startswith(ROUND_PREFIX)]
    follow = [ln for ln in read("FOLLOWUPS.md").splitlines() if ln.startswith("- X3 judge") or ln.startswith("- round 3c") or "3c" in ln]
    # wall-clock per stage from RUNLOG
    times = {}
    for ln in runlog:
        parts = ln.split("  "); ts, stg, ev = parts[0], parts[1], parts[2]
        t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
        times.setdefault(stg, {}); times[stg].setdefault("events", []).append((ev, t))
        if ev == "start":
            times[stg]["start"] = t
        elif ev in ("done", "blocked", "skipped"):
            times[stg]["end"] = t; times[stg]["status"] = ev
    first = times["U0c"]["start"]; now = datetime.now()
    wall_rows = []
    for stg in STAGES:
        d = times.get(stg, {})
        if "start" in d:
            end = d.get("end", now); wall_rows.append(f"| {stg} | {d['start'].strftime('%H:%M:%S')} | {end.strftime('%H:%M:%S')} | {(end - d['start']).total_seconds() / 60:.1f} | {d.get('status', 'running')} |")
        else:
            wall_rows.append(f"| {stg} | — | — | — | not started |")
    u0c = read("u0c_check.md"); u1 = read("u1_summary.md"); x3 = read("x3_summary.md"); x1 = read("x1_summary.md"); n3 = read("n3_summary.md"); n4 = read("n4_summary.md"); x1b = read("x1b_summary.md"); rt = read("rt_summary.md"); m = read("m_summary.md")
    kill_table = ["| K | stage | statistic | MET if | observed (from DISCONFIRMATION.md) | outcome |", "|---|---|---|---|---|---|"]
    for ln in disc:
        parts = ln.split("  "); stg, kid = parts[1], parts[2]
        thr = re.search(r"threshold=(.*?)  observed=", ln); obs = re.search(r"observed=(.*?)  (MET|NOT MET|INCONCLUSIVE|PASS|FAIL)  ", ln); oc = re.search(r"  (MET|NOT MET|INCONCLUSIVE|PASS|FAIL)  ", ln)
        kill_table.append(f"| {kid} | {stg} | | {thr.group(1) if thr else ''} | {obs.group(1) if obs else ''} | **{oc.group(1) if oc else ''}** |")
    lines = ["# MORNING3c — round 3c (2026-09-08): base-model control, snippet interaction, cross-layer readout, frozen-AR rewards, layer curve, gated pilots", "",
             f"Written by T8 at {time.strftime('%Y-%m-%d %H:%M:%S')} local; git {L.git_hash()[:8]}. Numbers only; no verdicts. Every number below is copied from a stage artifact (`<stage>_summary.md`, `<stage>_settings.json`, `DISCONFIRMATION.md`, `RUNLOG.md`).",
             f"Round started {first.strftime('%Y-%m-%d %H:%M:%S')} (first round-3c RUNLOG line); hard stop was {first.strftime('%H:%M:%S')} + 9 h.", "",
             "## 1. Kill tests and gates (verbatim outcomes)", ""] + kill_table + ["", "Verbatim lines:", ""] + [f"- `{ln}`" for ln in disc] + [
             "", "## 2. U1 — base-model control (REQUIRED): un-finetuned Qwen2.5-7B-Instruct in the AV interface vs the trained AV vs text-only, identical items", "",
             section(u1, "- baseline =", "## Kill U1"), "", section(u1, "## Kill U1", "## Pre-committed reading key"), "", section(u1, "## Ten fixed rows"), "",
             "## 3. X3 — does the local snippet suppress factual discrimination? (AR only; eligibility count and n)", "",
             section(x3, "- accepted S3 triples", "## Kill X3"), "", section(x3, "## Kill X3", "## Pre-committed reading key"), "", section(x3, "## Five verbatim rows"), "",
             "## 4. X1 — cross-layer readout with the layer-20 AV (per-layer tables)", "",
             section(x1, "- layers [", "## Kill X1"), "", section(x1, "## Kill X1", "## Pre-committed reading key"), "",
             "## 5. N3 — what the frozen AR rewards: correct / wrong specific / generic / omitted (four-way table)", "",
             section(n3, "- accepted deterministic-swap", "## Kill N3"), "", section(n3, "## Kill N3"), "",
             "## 6. N4 — fact-vs-phrasing displacement across all TARGET layers (curve table; descriptive)", "",
             section(n4, "- C3 cells:"), "",
             "## 7. X1b — cross-layer full generations (optional; descriptive)", "",
             section(x1b, "- 80 generations"), "",
             "## 8. RT — round-trip relational pilot (gated)", "",
             (section(rt, "- G0") if rt else "not run"), "",
             "## 9. M — error-monitoring pilot (gated)", "",
             (section(m, "- problems:") if m else "not run"), "",
             "## 10. FOLLOWUPS added this round", ""] + (follow or ["(none)"]) + [
             "", "## 11. Provenance", "",
             "- **Pre-registered by the human (PLAN.md 'Round 3c stages', 2026-09-08):** every stage, its rows, conditions, prefixes, candidates, layers, gates, thresholds, bootstrap unit, pilot/eval split, execution order, caps and the 9 h hard stop.",
             "- **Built by the agent this round (all in `overnight/`, one process per stage, Settings created inside `main()`):** `u0c_check.py`, `u1_base.py` (class `TargetAsAV`: the AV's meta/tokenizer/prompt/injection with the TARGET's weights; `nla_lib.AV` role assert bypassed by construction; AV scores read from the round-3/3b files with token counts asserted), `x3_snippet.py`, `x1_layers.py`, `n3_generic.py`, `n4_layers.py`, `x1b_gen.py`, `rt_roundtrip.py` (residual hook copied from `src/patching.py`'s pattern), `m_monitor.py`, `t8_morning.py`.",
             "- **Agent choices inside the pre-registration (each logged in the stage's settings/summary):** X3 'changed word' = symmetric word-set difference (lower-cased, punctuation-stripped), condition-3 span drawn at claim level with the tested claim and the snippet protected; X3 judge prompts (two fixed yes/no prompts, greedy, ≤4 tokens); N3 kind rule (digit → number, else name) and the generic 'a place' for every name (the S3 swap list carries no person marker, so PLAN's else-branch applies); X1b's mechanical quoted-token / expecting-hit rules (the desk's 0.444 / 0.029 figures used an unverified rule and are quoted as such); RT perturbation seeds (SEED + 100·s + ctx_id); M raw-text prompt (no chat template), the 'Answer:' token rule and the yes/no self-check wording; U1 text-only prefix = tokens 0..pos inclusive.",
             "- **Crash fixes (RUNLOG):** U0c iteration 1 (benchmark loop bug before any output). No script was edited after seeing evaluation outputs.",
             "- **Not run / stopped as pre-declared:** RT routes (gate G2 11/16 < 12); X3 condition-3 feasibility gate FAIL (74 < 100) → I reported INCONCLUSIVE with n=74.",
             "", "## 12. Wall-clock and measured per-item costs", "", "| stage | start | end | min | status |", "|---|---|---|---|---|"] + wall_rows + [
             "", f"- total {(now - first).total_seconds() / 3600:.2f} h from the first round-3c RUNLOG line to T8", "",
             section(u0c, "## Measured costs", "## Re-budget"), "", "RUNLOG lines (verbatim):", ""] + [f"- `{ln}`" for ln in runlog] + [""]
    (L.OVERNIGHT / "MORNING3c.md").write_text("\n".join(lines) + "\n")
    S.finish(n_disc_lines=len(disc), n_runlog_lines=len(runlog))
    L.log(f"T8 done: MORNING3c.md written ({len(disc)} kill/gate lines, {len(runlog)} RUNLOG lines)")


if __name__ == "__main__":
    main()

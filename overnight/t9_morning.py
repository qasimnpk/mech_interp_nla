"""T9 — round-4 morning report: overnight/MORNING4.md (PLAN.md round 4; reserved final 30 min).

  uv run python overnight/t9_morning.py

Assembles: the round-4 kill lines from DISCONFIRMATION.md (three-way rule), each stage summary copied whole (every table, 2×2 block,
Distributions section and the 5 verbatim examples are copied, not summarised), counts and cut rules, the review-pack file list with
row counts, FOLLOWUPS, provenance, wall-clock and measured per-item costs.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402

O = L.OVERNIGHT
STAGES = ["v0", "b1", "a1", "k1", "d1"]
PACK = ["contexts.csv", "av.jsonl", "slots.csv", "candidates.jsonl", "realizations.jsonl", "texts.jsonl", "scores.csv", "summary.md", "review_blind.csv", "review_key.csv",
        "settings.json", "progress.json", "rows.csv", "carriers.csv", "paraphrase_rows.csv", "slot_stats.csv", "selection.csv", "sample.csv", "check.md", "bench.json"]


def nrows(p: Path) -> str:
    if not p.exists():
        return "absent"
    if p.suffix in (".csv", ".jsonl"):
        n = sum(1 for ln in p.read_text().splitlines() if ln.strip())
        return f"{n - 1 if p.suffix == '.csv' else n} rows"
    return f"{p.stat().st_size} bytes"


def main():
    S = L.Settings("t9")
    first = [ln for ln in (O / "RUNLOG.md").read_text().splitlines() if "  V0  start  round 4 begins" in ln]
    t_first = first[0].split("  ")[0] if first else "?"
    kills = [ln for ln in (O / "DISCONFIRMATION.md").read_text().splitlines() if ln[:10] >= "2026-09-09" and any(f"  {k}  " in ln for k in ["B1", "A1", "K1", "D1"])]
    runlog = [ln for ln in (O / "RUNLOG.md").read_text().splitlines() if ln[:10] >= "2026-09-09"]
    prog = {}
    for s in ["V0", "B1", "A1", "K1", "D1"]:
        p = O / f"{s.lower()}_progress.json"
        if p.exists():
            prog[s] = json.loads(p.read_text())
    v0 = json.loads((O / "v0_settings.json").read_text()) if (O / "v0_settings.json").exists() else {}
    lines = ["# MORNING4 — round 4 (2026-09-09): controlled pairs (B1), natural claims (A1), K-way ranking (K1), claim-direction ablation (D1)", "",
             f"Written {time.strftime('%Y-%m-%dT%H:%M:%S')} by T9. Round-4 first RUNLOG line {t_first}; hard stop 10 h later. Numbers only; every label below is PROVISIONAL (agent-judged) until the human has reviewed the `_review_blind.csv` sheets and re-run `b1_analyze.py` / `a1_analyze.py --labels`.",
             "", "## Kill lines (pre-registered three-way rule: CI entirely ≤ 0 → MET; entirely > 0 → NOT MET; straddles 0 or n below the stage minimum → INCONCLUSIVE)", "",
             "An INCONCLUSIVE or MET line means no detectable preference under this scorer at this position with this n; it is never a statement that the information is absent from the activation.", ""]
    lines += [f"- {ln}" for ln in kills] or ["- (no round-4 kill line found)"]
    lines += ["", "## Stage status, cut rules and costs", "", "| stage | phase | cumulative min (script + judgement) | judgement min | failures | blocked | cut rules |", "|---|---|---|---|---|---|---|"]
    for s, p in prog.items():
        lines.append(f"| {s} | {p.get('phase')} | {p.get('cumulative_minutes', 0):.1f} | {p.get('judgement_minutes', 0):.1f} | {p.get('failures')} | {p.get('blocked') or ''} | {'; '.join(p.get('cut_rules_applied', [])) or '—'} |")
    if v0:
        b = v0.get("bench", {})
        lines += ["", "Measured per-call costs (V0, 5 calls each, mean s): " + ", ".join(f"{k} {b[k]['mean_s']:.2f}" for k in ["target_ctx_forward_hidden", "target_256_forward_hidden", "av_sampled_200", "av_greedy_200", "ar_score"] if k in b),
                  f"Orchestrator judgement rate used for the re-budget: {json.dumps(v0.get('per_task_minutes'))} min/task ({v0.get('per_task_source')}). Cut rules applied: {'; '.join(v0.get('cut_rules_applied', []))}."]
    lines += ["", "## Human review pack (open `<stage>_review_blind.csv` first, `<stage>_review_key.csv` after)", "", "| file | rows |", "|---|---|"]
    for s in STAGES:
        for k in PACK:
            p = O / f"{s}_{k}"
            if p.exists():
                lines.append(f"| {p.name} | {nrows(p)} |")
        for p in sorted(O.glob(f"{s}_agent_tasks_*.jsonl")) + sorted(O.glob(f"{s}_agent_outputs_*.jsonl")):
            lines.append(f"| {p.name} | {nrows(p)} |")
    for p in ["out/b1_acts.npz", "out/a1_acts.npz", "out/d1_vectors.npz", "out/b1_preds.npz", "out/a1_preds.npz"]:
        if (O / p).exists():
            lines.append(f"| {p} | {(O / p).stat().st_size} bytes (gitignored) |")
    lines += ["", "Every analysis script accepts `--labels <csv>` (columns item_type,item_id,field,value) and recomputes its summary from human labels without touching raw scores.", ""]
    for s, title in [("v0", "V0 — checks, benchmark, re-budget"), ("b1", "B1 — controlled paired contexts (human-designed; PRIMARY CONTROLLED)"), ("a1", "A1 — natural AV claims (human-designed; PRIMARY NATURAL)"),
                     ("k1", "K1 — K-way alternative ranking (desk-designed)"), ("d1", "D1 — claim-direction ablation (desk-designed)")]:
        p = O / (f"{s}_check.md" if s == "v0" else f"{s}_summary.md")
        lines += ["", "---", "", f"# {title}", ""]
        if p.exists():
            body = p.read_text().splitlines()
            lines += [("#" + ln) if ln.startswith("#") else ln for ln in body]  # demote headings one level; copied verbatim otherwise
        else:
            lines += [f"(no {p.name}: stage not run or blocked — see STATE.md and RUNLOG)"]
    lines += ["", "---", "", "# Round-4 RUNLOG (verbatim)", ""] + [f"- {ln}" for ln in runlog]
    lines += ["", "# FOLLOWUPS (verbatim, whole file)", ""] + (O / "FOLLOWUPS.md").read_text().splitlines()
    lines += ["", "# Provenance", "",
              "- Human-designed (2026-09-09, revised after advisor review): A1 and B1 — design, hypotheses, edit suite, statistics, seed pairs, success criteria, cut rules, the agent-judgement protocol and the review-pack schema (PLAN.md round-4 section).",
              "- Desk-designed (2026-09-08, accepted by the human 2026-09-09 with limited claims): K1 and D1.",
              "- Agent-built overnight (this session, Claude Fable 5.1): r4_lib.py, v0_check.py, b1_pairs.py / b1_analyze.py, a1_natural.py / a1_analyze.py, k1_kway.py, d1_ablate.py, t9_morning.py; every editor / judge label (label_source=claude, provisional) in the *_agent_outputs_*.jsonl files.",
              "- Agent choices inside the pre-registration (logged in RUNLOG / settings): V0 re-budget used the uniform measured 0.14 min/task rate for every task type (per-type blocks not separable in the 20-task sample); B1 keyword sets and F2/F4 stem lists as in r4_lib.b1_pairs; B1 'same' meaning is stored under category correct_original with its truth label; A1 entity_sub pool = t2b corrupt_det name cores; A1 repeated-fact check via a second slot_verify task; K1/D1 as in their settings files; crash fixes listed in RUNLOG (none changed a measurement).",
              "- Not done, by design: no insertion arm, no second position, no second intervention strength, no French, no threshold or item-count change beyond the pre-declared V0 cut rules.", ""]
    (O / "MORNING4.md").write_text("\n".join(lines))
    S.finish(n_kill_lines=len(kills), stages=list(prog))
    L.log(f"MORNING4.md written: {len(lines)} lines, {len(kills)} kill lines")


if __name__ == "__main__":
    main()

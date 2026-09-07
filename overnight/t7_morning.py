"""T7 — assemble overnight/MORNING3b.md from the round-3b stage artifacts (PLAN.md round 3b).

  uv run python overnight/t7_morning.py [--dry]     (--dry writes out/MORNING3b_dry.md instead)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

OV = Path(__file__).resolve().parent
KILL_IDS = {"T2c", "T2a", "T2b", "C3-score", "C3-readout"}
PHRASINGS = [
    "\"substantially more sensitive to wording and relevance than to the tested factual corruptions\" (not \"reads wording, not facts\")",
    "\"local-snippet dominance persists across positions\" (moving it cut its cost by ~21%, so not \"content, not position\")",
    "\"the tested instructions did not produce the requested changes\" (not \"ignores instruction text\")",
    "T4 \"replicates injected-concept sensitivity\", not the outside-J-space result (no J-space complement was built)",
    "report rotation angles as angles (18° ≈ 31% of the norm for equal-norm vectors, not \"small\")",
    "the blind/raw-context scores 0.429/0.473 sit well above the empty baseline 0.347",
    "three things kept apart in every readout number: self-consistency (the AV prefers a word it generated itself), activation dependence (the preference changes when the activation changes), factual recovery (the preference follows an independently known source fact). T2-claims / T2b = self-consistency + activation dependence; T2c = factual recovery; C3 = a phrasing control, not a zero-information edit",
    "the prior-corrected topic AUROC (0.935 in round 3) was not pre-registered → exploratory; T2a reports the held-out wording and within-pair accuracy with CIs alongside",
]


def read(name):
    p = OV / name
    return p.read_text() if p.exists() else None


def section(md, start, end=None):
    if md is None:
        return "(missing)"
    lines = md.splitlines()
    try:
        i = next(k for k, l in enumerate(lines) if l.startswith(start))
    except StopIteration:
        return f"(section {start!r} not found)"
    j = len(lines)
    if end is not None:
        for k in range(i + 1, len(lines)):
            if lines[k].startswith(end):
                j = k; break
    return "\n".join(lines[i:j]).rstrip()


def settings(stage):
    s = read(f"{stage}_settings.json")
    return json.loads(s) if s else None


def wall(stage):
    d = settings(stage)
    return f"{d.get('wall_start')} → {d.get('wall_end')}" if d else "—"


def main():
    dry = "--dry" in sys.argv
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=OV.parent).stdout.strip()
    state = read("STATE.md") or ""
    disc_all = [l for l in (read("DISCONFIRMATION.md") or "").splitlines() if l and not l.startswith("#")]
    disc = [l for l in disc_all if re.match(r"\S+\s+(T2c|T2a|T2b|C3)\s", l)]
    runlog_all = [l for l in (read("RUNLOG.md") or "").splitlines() if l and not l.startswith("#")]
    first = next((k for k, l in enumerate(runlog_all) if re.match(r"\S+\s+U0\s+start", l)), len(runlog_all))
    runlog = runlog_all[first:]
    follow = [l for l in (read("FOLLOWUPS.md") or "").splitlines() if l and not l.startswith("#")]
    stage_status = section(state, "## Stage status", "## Blockers"); blockers = section(state, "## Blockers", "## Open decisions"); open_dec = section(state, "## Open decisions", "## Notes")
    u0, t2c, t2a, t2b, c3 = (read(n) for n in ["u0_check.md", "t2c_summary.md", "t2a_summary.md", "t2b_summary.md", "c3_summary.md"])
    t_start = runlog[0].split()[0] if runlog else "?"
    now = time.strftime("%Y-%m-%dT%H:%M:%S")

    out = ["# MORNING3b — nightshift round 3b, NLA project", "",
           f"Generated {now} at git {git}. Numbers only; every kill-test outcome is the pre-registered three-way label. The human decides what they mean. "
           "Raw outputs: `overnight/t2c_pairs.csv`, `overnight/t2a_scores.csv`, `overnight/t2b_claims.csv`, `overnight/t2b_support_sheet.csv` (human fills `label_supported`), "
           "`overnight/c3_cells.csv`, `overnight/c3_descriptions.jsonl`, `out/c3_acts.npz`; per-stage settings in `overnight/<stage>_settings.json`; logs in `out/<stage>.log`. "
           "Round-1/2/3 files were read only.", "",
           "## Kill-test log, round 3b (copied from DISCONFIRMATION.md)", ""]
    out += [f"- {l}" for l in disc] or ["(none)"]
    out += ["", "| K | stage | outcome | pre-registered kill? |", "|---|---|---|---|"]
    for l in disc:
        m = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+threshold=.*?\s{2}(MET|NOT MET|INCONCLUSIVE)\s{2}", l)
        if m:
            out.append(f"| {m.group(3)} | {m.group(2)} | {m.group(4)} | {'yes' if m.group(3) in KILL_IDS else 'no (reported alongside)'} |")
    out += ["", "## Stage status and wall-clock", "", "```", stage_status, "```", "",
            f"First round-3b RUNLOG line: {t_start}; hard stop = that + 2.5 h; stage cap 45 min; report generated {now}.", "",
            "| stage | wall-clock (settings.json) |", "|---|---|"]
    for k in ["u0", "t2c", "t2a", "t2b", "c3"]:
        out.append(f"| {k.upper()} | {wall(k)} |")
    out += ["", "RUNLOG (round 3b):", "", "```"] + runlog + ["```", "", "Blockers:", "", blockers, ""]

    out += ["## T2c — forced-prefix entity readout on the 40 C2 matched activation pairs (PRIMARY; AV forward only)", "",
            section(t2c, "- pairs", "## Full 40-row table — p2") if t2c else "(T2c not run; see STATE.md blockers)", ""]
    out += ["## T2a — audit of the round-3 topic readout + held-out wording p3", "",
            section(t2a, "- AV forwards", "## Ten fixed rows") if t2a else "(T2a not run; see STATE.md blockers)", ""]
    out += ["## T2b — activation-dependence control for the round-3 claim-word readout (NOT a truth test)", "",
            section(t2b, "**ACTIVATION-DEPENDENCE", "## Donor table split by in_ctx_right") if t2b else "(T2b not run; see STATE.md blockers)", ""]
    out += ["## C3 — meaning-preserving phrasing control for C2, factorial (TARGET → AV → AV+AR)", "",
            section(c3, "This is a *phrasing control*", "## Full cell table") if c3 else "(C3 not run or blocked before its summary was written; see STATE.md blockers and out/c3.log; partial descriptions, if any, are in c3_descriptions.jsonl)", "",
            section(c3, "## Three verbatim cells") if c3 else "", ""]
    out += ["## T3 closeout (from U0; report only, not rerun)", "", section(u0, "## T3 closeout", "## Re-budget") if u0 else "(U0 not run)", ""]
    out += ["## Write-up phrasings requested by the human in the round-3 review (PLAN.md round-3b block; verbatim, for the desk)", ""] + [f"- {p}" for p in PHRASINGS] + [""]
    out += ["## FOLLOWUPS.md (queued for the human, not acted on)", ""] + (follow or ["(none)"]) + [""]
    out += ["## OPEN DECISIONS (from STATE.md)", "", open_dec, ""]
    out += ["## Provenance", "",
            "**Pre-registered by the human (PLAN.md round 3b, 2026-09-06 23:15):** the stage list and execution order (U0 → T2c → T2a → T2b → C3 → T7), the shared readout definition "
            "(summed log-prob of every token of ' ' + candidate after the prefilled assistant turn; h_0 = no injection), the T2c nouns and both prefixes p1/p2, the T2c candidates "
            "(the pair's own entities), the held-out prefix p3, the T2b donors (h_pos2 near, h_foreign far) and the rule that own / no-injection log-probs are reused from t2_claims.csv, "
            "the in_ctx source-support proxy and the 30-row support sheet, the C3 wording pairs (primary and fallback) and the drop rule, the C3 margins and 2×2 decomposition, every kill "
            "statistic and threshold in the round-3b threshold table, the three-outcome rule, the cluster-bootstrap rule (by template for the C2-derived stages, by document / explanation "
            "otherwise; 1000 draws, seed 0), the pilot/eval split, the 45-min stage cap and the 2.5 h hard stop.", "",
            "**Written by the agent:** `u0_check.py`, `t2c_entity.py`, `t2a_audit.py`, `t2b_donor.py`, `c3_phrasing.py`, `t7_morning.py`, this file. `nla_lib.py`, `t2_prefix.py` (the `Prefix` class), "
            "`c2_matched.py` (`TEMPLATES`, `build_pairs`, `mentions`), `t1_arprobe.py` (`auroc`, `boot_auroc`, `detok`, `load_triples`) and all round-1/2/3 files were reused unchanged.", "",
            "**Choices the agent had to make (none changes a pre-registered statistic; each is logged in the stage's settings.json):**",
            "- T2c: the paired AUROC (statistic 5) is given with two bootstrap CIs, by template and by pair, because the plan says 'cluster by template' for 1–4 and 'over the 40 pairs' for 5. "
            "Within-pair choice accuracy (statistic 4) is the fraction of the 80 activations whose argmax candidate is the entity in that context, i.e. D(h_a) > 0 for side a and D(h_b) < 0 for side b. "
            "MIN pairs for a non-INCONCLUSIVE outcome = 30 (as C2). All 80 candidate strings are single tokens, so the per-token rows equal the summed rows.",
            "- T2a: the audit checks are source-string matches in t2_prefix.py plus arithmetic identities in t2_scores.csv; the 'pre-registered?' check reads the round-3 T2 stage text in PLAN.md for the words 'prior-corrected'. "
            "The swap statistic is also reported prior-corrected (same no-injection prior subtracted). Within-pair accuracy CIs are a bootstrap over stimuli (one row per document).",
            "- T2b: the kill is computed over all 691 rows pooled (the stage text says 'every non-error row'), with the LLM / deterministic / last-claim splits reported in the same line. "
            "in_ctx strips leading/trailing non-alphanumerics from word_orig before the whole-word match. The support sheet is sampled with pandas `sample(random_state=0)` from evaluation LLM-corrupt rows and sorted by row.",
            "- C3: the wording replacement is the first whole-word occurrence of w1 in the whole template (all ten primaries sit in the first sentence). A and B activations are C2's cached ones (re-derived and compared, deviation logged); "
            "A and B descriptions are C2's. M_fact(w1) is re-scored fresh by the AR and also recomputed from the c2_pairs.csv cos columns (asserted equal to the file's M; both versions of the kill statistic are reported). "
            "The 'activation-distance difference' uses 1 − cos averaged over the two fact pairs minus the two wording pairs. The verbatim cells are pairs 0, 18, 36.",
            "- Settings files are created inside `main()`; stage scripts import round-3 modules whose Settings creation is inside `main()` (checked in U0), so no earlier settings file is rewritten.", ""]
    target = (OV / "out" / "MORNING3b_dry.md") if dry else (OV / "MORNING3b.md")
    target.write_text("\n".join(out) + "\n")
    print("wrote", target.name, len(out), "lines")


if __name__ == "__main__":
    main()

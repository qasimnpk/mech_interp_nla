"""T6 — assemble overnight/MORNING3.md from the round-3 stage artifacts (PLAN.md round 3).

  uv run python overnight/t6_morning.py [--dry]     (--dry writes out/MORNING3_dry.md instead)
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

OV = Path(__file__).resolve().parent


def read(name):
    p = OV / name
    return p.read_text() if p.exists() else None


def section(md: str | None, start: str, end: str | None = None) -> str:
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


def fa(b):
    return f"{b['auroc']:.3f} [{b['lo']:.3f},{b['hi']:.3f}]" if b else "—"


def main():
    dry = "--dry" in sys.argv
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=OV.parent).stdout.strip()
    state = read("STATE.md") or ""
    disc_all = [l for l in (read("DISCONFIRMATION.md") or "").splitlines() if l and not l.startswith("#")]
    disc3 = [l for l in disc_all if re.match(r"\S+\s+(C1|C2|T1|T2|T3|T4|T5)\s", l)]
    runlog_all = [l for l in (read("RUNLOG.md") or "").splitlines() if l and not l.startswith("#")]
    first = next((k for k, l in enumerate(runlog_all) if re.match(r"\S+\s+T0\s+start", l)), len(runlog_all))
    runlog = runlog_all[first:]
    follow = [l for l in (read("FOLLOWUPS.md") or "").splitlines() if l and not l.startswith("#")]
    stage_status = section(state, "## Stage status", "## Blockers")
    blockers = section(state, "## Blockers", "## Open decisions")
    open_dec = section(state, "## Open decisions", "## Notes")
    t0, c1, c2, t1, t2, t3, t4 = (read(n) for n in ["t0_check.md", "c1_summary.md", "c2_summary.md", "t1_summary.md", "t2_summary.md", "t3_summary.md", "t4_summary.md"])
    s1, s2 = settings("t1"), settings("t2")
    t_start = runlog[0].split()[0] if runlog else "?"

    out = ["# MORNING3 — nightshift round 3, NLA project", "",
           f"Generated {time.strftime('%Y-%m-%dT%H:%M:%S')} at git {git}. Numbers only; every kill-test outcome is the pre-registered three-way label. "
           "The human decides what they mean. Raw outputs: `overnight/c*_*.csv`, `overnight/t*_*.csv|.jsonl`, `out/*.npz`, per-stage settings in "
           "`overnight/<stage>_settings.json`, logs in `out/<stage>.log`. Round-1/2 files were read only.", "",
           "## Kill-test log, round 3 (copied from DISCONFIRMATION.md)", ""]
    out += [f"- {l}" for l in disc3] or ["(none)"]
    out += ["", "| K | stage | outcome | pre-registered kill? |", "|---|---|---|---|"]
    for l in disc3:
        m = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+threshold=.*?\s{2}(MET|NOT MET|INCONCLUSIVE)\s{2}", l)
        if m:
            pre = "yes" if m.group(3) in {"C1", "C2", "T1", "T2", "T3", "T4", "T5"} else "no (reported alongside)"
            out.append(f"| {m.group(3)} | {m.group(2)} | {m.group(4)} | {pre} |")
    out += ["", "## Stage status and wall-clock", "", "```", stage_status, "```", "",
            f"First round-3 RUNLOG line: {t_start}; hard stop = that + 5 h; report generated {time.strftime('%Y-%m-%dT%H:%M:%S')}.", "",
            "| stage | wall-clock (settings.json) |", "|---|---|"]
    for k in ["t0", "c1", "c2", "t1", "t2", "t4", "t3"]:
        out.append(f"| {k.upper()} | {wall(k)} |")
    out += ["", "RUNLOG (round 3):", "", "```"] + runlog + ["```", "", "Blockers:", "", blockers, ""]

    # ---- T1 / T2 AUROC table
    out += ["## Topic readout AUROC table (evaluation stimuli 40–199, paired, bootstrap by document)", "",
            "| readout | AUROC [CI95] | control |", "|---|---|---|"]
    if s1:
        out += [f"| T1 AR probe cos(h, AR('This text is about {{topic}}.')) | {fa(s1['kill_T1']['auroc'])} | topic-absent subset {fa(s1.get('auroc_subset_topic_absent'))} |",
                f"| T1 RepE class means (TARGET L20, centred) | {fa(s1['repe']['centred'])} | uncentred {fa(s1['repe']['raw'])}; diff-direction s vs −s {fa(s1['repe']['diff'])} |"]
    if s2:
        e = s2["eval_stats"]; sub = s2["subset_stats"]
        out += [f"| T2 candidate continuation, summed log-prob | {fa(e['cc'])} | no-injection {fa(e['cc_noinj'])}; prior-corrected {fa(e['cc_corr'])}; swap prefers foreign {fa(e['cc_swap_prefers_foreign'])}; topic-absent subset {fa(sub['cc'])} |",
                f"| T2 candidate continuation, per-token | {fa(e['cc_pt'])} | no-injection {fa(e['cc_noinj_pt'])} |",
                f"| T2 yes/no logit difference | {fa(e['yn'])} | no-injection {fa(e['yn_noinj'])}; prior-corrected {fa(e['yn_corr'])}; swap prefers foreign {fa(e['yn_swap_prefers_foreign'])} |"]
    out.append("")

    out += ["## T0 — artifact check, topics, entropy sidecar, measured costs", "", section(t0, "## Artifact counts", "## Measured per-item costs") if t0 else "(T0 not run)", "",
            section(t0, "## Re-budget", "Ten fixed rows") if t0 else "", ""]
    out += ["## C1 — position vs content (snippet moved to the front / order reversed), AR only, 160 eval explanations", "",
            section(c1, "- explanations:", "## Five fixed rows") if c1 else "(C1 not run)", ""]
    out += ["## C2 — matched one-fact activation pairs (40 pairs, 10 templates), TARGET → AV → AR", "",
            section(c2, "- pairs:", "## Five verbatim pairs") if c2 else "(C2 not run)", "",
            section(c2, "### pair 0", "### pair 9") if c2 else "", ""]
    out += ["## T1 — the reconstructor as a zero-shot text probe, with RepE baseline and matched-claim contrast", "",
            section(t1, "- stimuli 200", "## Ten fixed rows") if t1 else "(T1 not run)", ""]
    out += ["## T2 — forced-prefix readout from the verbalizer (AV forward only)", "",
            section(t2, "- AV forwards", "## Ten fixed rows") if t2 else "(T2 not run)", ""]
    out += ["## T4 — perturbing the injected vector with TARGET concept directions (pilot 0–39)", "",
            section(t4, "- items", "## Four fixed examples") if t4 else "(T4 not run)", "",
            section(t4, "### stim 0", "### stim 7") if t4 else "", ""]
    out += ["## T5 — steering specificity (OPTIONAL)", "", "Skipped: STATE.md carries `T5: SKIP`, not `T5: HUMAN-CONFIRMED`. Gate G5 was not run.", ""]
    out += ["## T3 — residual-stream steering of the verbalizer (pilot 0–39; last stage, cut at the stage cap)", "",
            section(t3, "- items", "## Four fixed examples") if t3 else "(T3 not run or blocked before its summary was written; see STATE.md blockers and out/t3.log; partial items, if any, are in t3_outputs.jsonl)", "",
            section(t3, "### stim 0", "### stim 7") if t3 else "", ""]
    out += ["## FOLLOWUPS.md (queued for the human, not acted on)", ""] + (follow or ["(none)"]) + [""]
    out += ["## OPEN DECISIONS (from STATE.md)", "", open_dec, ""]
    out += ["## Provenance", "",
            "**Pre-registered by the human (PLAN.md round 3):** the stage list and execution order (T0 → C1 → C2 → T1 → T2 → T4 → T5 → T3 → T6), the T5 gate line, "
            "the pilot/eval split, every kill statistic and threshold in the round-3 threshold table, the three-outcome rule, the cluster-bootstrap rule (by explanation, "
            "by document, by template as each stage says; 1000 draws, seed 0), the probe sentences and questions (T1, T2 verbatim), the prefill strings, the C2 template "
            "design constraints (10 × 4, entity 8–20 tokens from the end, ≥ 6 shared final tokens, equal length), the direction recipes (difference of means; T3 layers 8/14 "
            "and α 1/2/4; T4 β grid and random direction), the collateral measures, the stage cap and the 5 h hard stop.", "",
            "**Written by the agent:** `t0_check.py`, `c1_position.py`, `c2_matched.py`, `t1_arprobe.py`, `t2_prefix.py`, `t3_avsteer.py`, `t4_inject.py`, "
            "`t34_sentences.py` (the fixed sentence lists), `t6_morning.py`, this file. `nla_lib.py` and all round-1/2 files were reused unchanged.", "",
            "**Choices the agent had to make (none changes a pre-registered statistic; each is logged in the stage's settings.json):**",
            "- T0: `topic_true` is the raw wikitext heading; a detokeniser (`' ( 1960 )'` → `'(1960)'`, `' @-@ '` → `'-'`, space before punctuation removed) is applied only when the topic is inserted into a probe sentence or matched against text; the raw string is kept in every CSV. The per-doc TARGET timing in T0 was taken without an MPS sync and is annotated; the wall-clock number (1.15 s/doc) was used for the re-budget.",
            "- C1: the snippet is the last S2 claim; its deletion cost in z is the pre-registered S2 value (−Δcos); a space-joined baseline is reported as a secondary line because z_rot is space-joined while z has newlines.",
            "- C2: entity pairs are template-specific (the plan's '10 templates × 4 pairs'); six pairs were replaced before any model ran so that both contexts tokenise to the same length. The cross-text swap control is only defined where the entity string occurs in the description (12/80). Bootstrap clusters = the 10 templates.",
            "- T1: the RepE 'agent-written sentences' are 16 fixed templates filled with the topic (200 topics × 16). The RepE AUROC is defined in parallel to the AR probe (positives cos(h, μ_true − μ̄), negatives cos(h, μ_foreign − μ̄), μ̄ = grand mean of the 200 topic means); the uncentred and difference-direction versions are reported too. cos is invariant to the plan's normalisation u(d). The matched-claim contrast is logged as a non-kill line.",
            "- T2: the kill statistic follows the stage text (candidate-continuation log-prob); the threshold table's 'yes−no' wording is logged as a second line. Prefill and candidate are tokenised separately and concatenated. 'Single-word corruption' = equal word count and exactly one differing whitespace token (298 of 490 LLM corruptions, 393 of 402 deterministic). A prior-corrected AUROC (log-prob minus its no-injection value) is reported as a secondary number.",
            "- T4: the random direction is drawn per stimulus (seed 1000 + stim_idx). Sports mention = whole-word match against a fixed keyword list (in settings). The three-way rule uses per-β bootstrap CIs (below / above / straddles). The LessWrong prior-art post named in the plan was fetched and is summarised in the T4 summary.",
            "- T3: 'mean‖h_ℓ‖' = mean last-token norm over the 64 direction sentences at block ℓ. Steering is applied at the final prompt position in the prefill pass and at every decode position; the injected marker row and earlier prompt positions are untouched. Cells with parse_ok < 0.5 are ineligible for the kill; the outcome uses per-cell CIs. The loop is stimulus-outer and stops at 85 min so every cell has the same n.",
            "- Settings files are created inside `main()`; `FRENCH` (S5 stoplist) is vendored into `t34_sentences.py` rather than imported from `s5_steer.py`, which would rewrite S5's settings file.", ""]
    target = (OV / "out" / "MORNING3_dry.md") if dry else (OV / "MORNING3.md")
    target.write_text("\n".join(out) + "\n")
    print("wrote", target.name, len(out), "lines")


if __name__ == "__main__":
    main()

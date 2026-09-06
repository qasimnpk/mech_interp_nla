"""R4 — assemble overnight/MORNING2.md from the round-2 stage artifacts (PLAN.md round 2).

  uv run python overnight/r4_morning.py
"""
from __future__ import annotations

import json
import re
import subprocess
import time
from pathlib import Path

OV = Path(__file__).resolve().parent


def read(name):
    p = OV / name
    return p.read_text() if p.exists() else None


def section(md: str | None, start: str, end: str | None = None) -> str:
    """Lines from the first line starting with `start` up to (not incl.) the first later line starting with `end`."""
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


def wall(stage):
    s = read(f"{stage}_settings.json")
    if not s:
        return "—"
    d = json.loads(s)
    return f"{d.get('wall_start')} → {d.get('wall_end')}"


def main():
    git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=OV.parent).stdout.strip()
    state = read("STATE.md") or ""
    disc_all = [l for l in (read("DISCONFIRMATION.md") or "").splitlines() if l and not l.startswith("#")]
    disc2 = [l for l in disc_all if re.match(r"\S+\s+R\d", l)]
    disc1 = [l for l in disc_all if l not in disc2]
    runlog_all = [l for l in (read("RUNLOG.md") or "").splitlines() if l and not l.startswith("#")]
    first_r2 = next((k for k, l in enumerate(runlog_all) if re.match(r"\S+\s+R0\s+start", l)), len(runlog_all))
    runlog = runlog_all[first_r2:]
    follow = [l for l in (read("FOLLOWUPS.md") or "").splitlines() if l and not l.startswith("#")]
    open_dec = section(state, "## Open decisions", "## Notes")
    stage_status = section(state, "## Stage status", "## Blockers")
    blockers = section(state, "## Blockers", "## Open decisions")
    r0, r1, r2, r3 = read("r0_check.md"), read("r1_summary.md"), read("r2_summary.md"), read("r3_summary.md")
    t_start = runlog[0].split()[0] if runlog else "?"

    out = ["# MORNING2 — nightshift round 2, NLA project", "",
           f"Generated {time.strftime('%Y-%m-%dT%H:%M:%S')} at git {git}. Numbers only; every kill-test outcome is the pre-registered three-way label. "
           "The human decides what they mean. Round 2 reused the round-1 artifacts (no new verbalizer generation). Raw outputs: `overnight/r*_*.csv`, "
           "`out/*.npz` (regenerated in R0), per-stage settings in `overnight/r*_settings.json`, logs in `out/r*.log`.", "",
           "## Kill-test log, round 2 (copied from DISCONFIRMATION.md)", ""]
    out += [f"- {l}" for l in disc2] or ["(none)"]
    out += ["", "| K | stage | outcome |", "|---|---|---|"]
    for l in disc2:
        m = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+threshold=.*?\s{2}(MET|NOT MET|INCONCLUSIVE)\s{2}", l)
        if m:
            out.append(f"| {m.group(3)} | {m.group(2)} | {m.group(4)} |")
    out += ["", "Round-1 kill lines these stages build on (for reference):", ""]
    out += [f"- {l}" for l in disc1 if re.search(r"\s(K3|K3-det|K2|K1a)\s", l)]
    out += ["", "## Stage status and wall-clock", "", "```", stage_status, "```", "",
            f"First round-2 RUNLOG line: {t_start}; report generated {time.strftime('%Y-%m-%dT%H:%M:%S')}.", "",
            "| stage | wall-clock (settings.json) |", "|---|---|"]
    for k in ["r0", "r1", "r2", "r3"]:
        out.append(f"| {k.upper()} | {wall(k)} |")
    out += ["", "RUNLOG (round 2):", "", "```"] + runlog + ["```", "", "Blockers:", "", blockers, ""]

    out += ["## R0 — artifact check + cache regeneration", "", section(r0, "## Artifact counts", "## Timings") if r0 else "(R0 not run)", ""]
    out += ["## R1 — fact-blindness locus: target layer-20 representation vs reconstructor (490 accepted S3 triples)", "",
            section(r1, "- triples:", "## Kill test") if r1 else "(R1 not run)", "",
            section(r1, "## 10 fixed S3 example rows", "## Timings") if r1 else "", ""]
    out += ["## R2 — amplified corruption (every accepted claim replaced), AR only", "",
            section(r2, "- evaluation explanations", "## Kill test") if r2 else "(R2 not run)", ""]
    out += ["## R3 — truncation curve (first k / last k claims), AR only, descriptive", "",
            section(r3, "- explanations:", "## Timings") if r3 else "(R3 not run)", ""]
    out += ["## FOLLOWUPS.md (queued for the human, not acted on)", ""] + ([f"{l}" for l in follow] or ["(none)"]) + [""]
    out += ["## OPEN DECISIONS (from STATE.md)", "", open_dec, ""]
    out += ["## Provenance", "",
            "**Pre-registered by the human (PLAN.md round 2):** the three questions and their stages, the R0 acceptance rule (0.8820 ± 0.002), the inputs "
            "(490 accepted S3 triples plus corrupt_det where present; S2 claim lists), the target-side encoding (raw claim text, no chat template, "
            "hidden_states[21], last token and mean over tokens), the AR-side encoding, d = 1 − cos, the R1 and R2 kill statistics and thresholds "
            "(CI ≤ 0 → MET; R1 n ≥ 300), the R3 quantities (first k / last k, lift over floor, k at median lift > 0.9, Spearman(word count, cos_alone)), "
            "the cluster bootstrap (by explanation, 1000 draws, seed 0), the INCONCLUSIVE rule, and the 5.5 h hard stop.", "",
            "**Written by the agent:** `r0_check.py`, `r1_locus.py`, `r2_amplify.py`, `r3_truncate.py`, `r4_morning.py`, this file. "
            "`nla_lib.py` and all round-1 files were reused unchanged.", "",
            "**Choices the agent had to make (none changes a pre-registered statistic):**",
            "- R0: activations rebuilt from `doc_idx`, `pos`, `pos2` in `stimuli.csv` (no re-shuffle of the corpus); the tokenisation was asserted against `seq_len` and `token_str` for every stimulus; `stimuli.csv` and `explanations.jsonl` were not rewritten. Per-row agreement with `s1_recon.csv` is reported beside the mean.",
            "- R1: TARGET then AR ran sequentially in one process (TARGET freed first) rather than co-resident; the 1860 distinct texts were scored once each. `corrupt_det` included where `numeric_ok` and non-null (402 of 490). The ratio d_corr/d_para is reported both as ratio of means and as the median per-item ratio. The same CI ≤ 0 rule is applied to the mean-pooled and AR sides as descriptive outcome labels; only the last-token target side is the pre-registered kill. The 10 example rows are the S3 fixed examples, read from `s3_summary.md`.",
            "- R2: 'accepted' = S3 `edit_ok`; z*det built on explanations with ≥ 2 det-corruptible claims (155 of 160). cos(z) is the S1 reconstruction of the original explanation text; cos(z_joined) − cos(edited) is reported alongside as in S3. No minimum-n rule was pre-registered for R2 and none was applied.",
            "- R3: per-k statistics are over explanations with n_claims ≥ k; k* = the first k at which the median lift over those explanations exceeds 0.9 (also per-explanation smallest k). `cos_alone` is taken from `s2_claims.csv` as pre-registered (S2 run), while its lift uses the regenerated cos_empty; the first-vs-last paired statistic excludes k = n (identical text).",
            "- Crash fix (RUNLOG): R1 iteration 1 died before any model load (pandas NaN for missing `corrupt_det` in the text set); the text filter now keeps only strings. No statistic touched; log kept as `out/r1_iter1_crash.log`.",
            "- Settings files are created inside `main()` (round-1 FOLLOWUP applied); importing a stage module no longer writes anything.", ""]
    (OV / "MORNING2.md").write_text("\n".join(out) + "\n")
    print("wrote MORNING2.md", len(out), "lines")


if __name__ == "__main__":
    main()

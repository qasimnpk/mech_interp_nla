"""S6 — assemble overnight/MORNING1.md from the stage artifacts (PLAN.md round 1).

  uv run python overnight/s6_morning.py
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


git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=OV.parent).stdout.strip()
state = read("STATE.md") or ""
disc = [l for l in (read("DISCONFIRMATION.md") or "").splitlines() if l and not l.startswith("#")]
runlog = [l for l in (read("RUNLOG.md") or "").splitlines() if l and not l.startswith("#")]
follow = [l for l in (read("FOLLOWUPS.md") or "").splitlines() if l and not l.startswith("#")]
open_dec = section(state, "## Open decisions", "## Notes")
stage_status = section(state, "## Stage status", "## Blockers")
blockers = section(state, "## Blockers", "## Open decisions")

s0, s1, s2, s3, s4, s5 = (read(f"s{k}_summary.md") for k in [0, 1, 2, 3, 4, 5])

out = [f"# MORNING1 — nightshift round 1, NLA project", "",
       f"Generated {time.strftime('%Y-%m-%dT%H:%M:%S')} at git {git}. Numbers only; every kill-test outcome is the pre-registered three-way label. "
       "The human decides what they mean. Raw outputs: `overnight/*.csv`, `*.jsonl`, `out/*.npz`; per-stage settings in `overnight/s*_settings.json`.", "",
       "## Kill-test log (copied from DISCONFIRMATION.md)", ""]
out += [f"- {l}" for l in disc] or ["(none)"]
out += ["", "| K | stage | outcome |", "|---|---|---|"]
for l in disc:
    m = re.match(r"(\S+)\s+(\S+)\s+(\S+)\s+threshold=.*?\s{2}(MET|NOT MET|INCONCLUSIVE)\s{2}", l)
    if m:
        out.append(f"| {m.group(3)} | {m.group(2)} | {m.group(4)} |")
out += ["", "## Stage status and wall-clock", "", "```", stage_status, "```", "", "| stage | wall-clock (settings.json) |", "|---|---|"]
for k in ["s0", "s1", "s2", "s3", "s5", "s4"]:
    out.append(f"| {k.upper()} | {wall(k)} |")
out += ["", "RUNLOG:", "", "```"] + runlog + ["```", "", "Blockers:", "", blockers, ""]

out += ["## S0 — library + stimuli + smoke", "", section(s0, "## Timings", "## 16 smoke"), "", section(s0, "cos: mean"), ""]
out += ["## S1 — baseline round trip (evaluation set n=160)", "", section(s1, "## Timings", "## Pilot set"), "", section(s1, "## 5 evaluation explanations"), ""]
out += ["## S2 — claim deletion", "", section(s2, "- explanations:", "## Kill test"), ""]
out += ["## S3 — corrupted vs paraphrased claims", "", section(s3, "## Editor acceptance", "## Kill test"), "", section(s3, "## 10 fixed examples"), ""]
out += ["## S5 — prompt steering (40 pilot stimuli)", "", section(s5, "Judge columns", "## Kill test"), "", section(s5, "## Verbatim examples"), ""]
out += ["## S4 — blind-describer and raw-context baselines (optional)", "", section(s4, "| column", "## Kill test") if s4 else "(S4 not run)", ""]
out += ["## FOLLOWUPS.md (queued for the human, not acted on)", ""] + ([f"{l}" for l in follow] or ["(none)"]) + [""]
out += ["## OPEN DECISIONS (from STATE.md)", "", open_dec, ""]
out += ["## Provenance", "",
        "**Pre-registered by the human (PLAN.md):** models, layer (block 20 = hidden_states[21]), stimulus source and sampling rules, pilot/eval split, "
        "AV/AR prompts and decoding (greedy, 200 / 120 tokens), claim splitter, every control (randspan, shuffle_words, shuffle_order, corrupt, paraphrase, "
        "corrupt_det, offtopic), the S3 editor prompts, the S5 variant wordings and mechanical checks, the S4 blind prompt, every kill-test statistic and threshold, "
        "the cluster bootstrap (by explanation, 1000 draws, seed 0), and the INCONCLUSIVE rule.", "",
        "**Written by the agent:** `overnight/nla_lib.py` (vendored from `scripts/nla7b_roundtrip.py`, all asserts kept), `s0_smoke.py`, `s1_roundtrip.py`, "
        "`s2_deletion.py`, `s3_corrupt.py`, `s5_steer.py`, `s4_blind.py`, `s6_morning.py`, the S5 judge CSV (agent rubric), this file.", "",
        "**Choices the agent had to make (none changes a pre-registered statistic):**",
        "- Stimuli: document shuffle = `np.random.default_rng(0).permutation(eligible doc indices)`; positions from a second `default_rng(0)` stream, pos then pos2 per document in order. Extra columns `stim_idx, seq_len, doc_tokens` in stimuli.csv.",
        "- K1b cross-document partner j drawn from all 200 stimuli excluding i (seed 0), not eval-only.",
        "- Outcome rule applied uniformly: MET / NOT MET only when the bootstrap CI lies wholly on one side of the threshold, INCONCLUSIVE otherwise or when n is under the stage minimum (K1: 160 eval items; K3: 100 accepted claims; K5: 80 items; K4: 160).",
        "- Claim splitter: word count taken after the list-marker strip. randspan: start uniform over word positions of z, redrawn (≤50) if the span coincides with any claim's word span; seeds 1000+row. shuffle_words seed 1000+row (separate RNG); shuffle_order seed 5000+stim_idx (PLAN gave no seed).",
        "- S2 `cos_z` is the S1 reconstruction of the original explanation text; `cos_z_joined` (claims re-joined, nothing deleted) is reported alongside.",
        "- S3: editor run on evaluation claims only (538); `z_edit` built from the S2 claim list with c_i replaced; `Δ_z` taken from S2 (original z). Joined-claims baseline columns added. Deterministic corruption: number formatting keeps the decimal places of the original; capitalised-token pool = capitalised non-sentence-initial tokens of all other evaluation explanations' claims.",
        "- S3 identity: because z*∖c_i* is the same text as z∖c_i, A_i = cos(z) − cos(z*) exactly (also logged in FOLLOWUPS).",
        "- S5: variant prompts built by replacing the default instruction sentence inside the checkpoint's own AV template (asserted V0 == default); the 200-word French stoplist and 50-word English function-word list were hard-coded by the agent; the injection asserts were run for every variant.",
        "- S5 judge: 120 items scored by the orchestrating agent reading each output next to V0 under the PLAN rubric; `followed`=0 for every V1/V2/V5 output, `same_referent`=1 for every output; one note (stim 22 V1) recorded in the CSV.",
        "- Crash fixes (logged in RUNLOG): S0 pandas `itertuples` dropped the `_ids` column (fixed before any output existed); S3 AR phase indexed a namedtuple with a string (fixed after the editor pass, before any AR score existed; editor outputs preserved and reused).",
        "- Time: hard stop fixed at 07:30 local (earlier than first RUNLOG line + 7 h).", ""]
(OV / "MORNING1.md").write_text("\n".join(out) + "\n")
print("wrote MORNING1.md", len(out), "lines")

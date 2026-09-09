"""T10 (round 5): assemble overnight/MORNING5.md from the P0/P1/P2 artifacts. Numbers only."""
import csv, json, subprocess, time
from pathlib import Path
O = Path(__file__).resolve().parent; ROOT = O.parent
src = {r["idx"]: r for r in json.loads((ROOT / "notes/nla_setup/nla27b_smoke_examples_full.json").read_text())}
gens = {json.loads(l)["idx"]: json.loads(l) for l in open(O / "p1_av.jsonl")}
scores = {int(r["idx"]): r for r in csv.DictReader(open(O / "p1_scores.csv"))}
toks = {r["idx"]: r for r in json.loads((O / "p0_tokens.json").read_text())}
kill = [l for l in open(O / "DISCONFIRMATION.md") if "  P1  P1  " in l][-1].strip()
summary = (O / "p2_summary.md").read_text()
runlog = [l.strip() for l in open(O / "RUNLOG.md") if "  P0  " in l or "  P1  " in l or "  P2  " in l or "  T10  " in l]
p1s = json.loads((O / "p1_settings.json").read_text()); p0s = json.loads((O / "p0_settings.json").read_text())
git = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()
L = []
L.append(f"# MORNING5 — round 5 (2026-09-09): the released 7B pair on the 27B's 8 example texts; claim type × truth side by side\n")
L.append(f"Written {time.strftime('%Y-%m-%dT%H:%M:%S')} by T10 (git {git}). Round-5 RUNLOG lines: {runlog[0][:19]} → now. Numbers only; every label PROVISIONAL (orchestrator for the 7B, desk subagent for the 27B) until the human reviews `p2_review_blind.csv` then `p2_review_key.csv`.\n")
L.append("## Kill line (pre-registered three-way rule; descriptive round, n = 8 by design)\n")
L.append(f"- {kill}\n")
L.append("An INCONCLUSIVE line here is the expected outcome (n = 8 < 30); it is never a statement that information is absent.\n")
L.append("## Setup\n")
L.append(f"- TARGET {p0s['models']['TARGET']['repo']} ({p0s['models']['TARGET']['snapshot'][:8]}), AV {p0s['models']['AV']['repo']} ({p0s['models']['AV']['snapshot'][:8]}), AR {p0s['models']['AR']['repo']} ({p0s['models']['AR']['snapshot'][:8]}); block 20 (`hidden_states[21]`), last token of each text; raw text, no chat template, `add_special_tokens=False`; bf16 on MPS.")
L.append(f"- AV: greedy, `max_new_tokens=200`, released prompt ({p1s['prompt_tokens']} tokens, marker at {p1s['marker_pos']}), marker embedding replaced by the vector rescaled to norm {p1s['injection_scale']}. AR: released template, last-token value head; `cos` in fp64.")
L.append("- 27B comparison run (pod, `scripts/nla27b_smoke.py`, branch `pod/mtl-setup`): ceselder/qwen3.6-27b-nla-rl av_base + adapter iter_000600, additive norm-matched injection at block 1, greedy 200 tokens, layer 42, last token; annotation `notes/nla_setup/nla27b_smoke_claims_annotated.csv`.")
L.append("- Inputs: the 27B repo's shipped `data/example_activations.parquet` texts, rows 0–7 (`doc_id` = `finefineweb_100k.parquet:train:<row>`, i.e. the 27B's RL corpus slice; provenance relative to the 7B's UltraFineWeb slice unknown).\n")
L.append("## Per-example scores and token counts\n")
L.append("| idx | doc row | 7B tokens | 27B tokens | last token | ‖h‖ | 7B gen tok / s | cos_own | cos_shuffled (partner) | cos_own of the 27B text through the 7B AR | 27B cos_own (its own AR) |")
L.append("|---|---|---|---|---|---|---|---|---|---|---|")
for i in sorted(src):
    s, g, t = scores[i], gens[i], toks[i]
    L.append(f"| {i} | {src[i]['doc_id'].split(':')[-1]} | {t['n_tokens_7b']} | {t['n_raw_tokens_27b']} | {t['last_token_str']!r} | {t['norm']:.1f} | {g['gen_tokens']} / {g['gen_s']} | {float(s['cos_own']):.4f} | {float(s['cos_shuffled']):.4f} ({s['shuffled_partner']}) | {float(s['cos_own_27b_text']):.4f} | {src[i]['cos_own']:.4f} |")
import statistics as st
L.append(f"\nMeans: cos_own {st.mean(float(s['cos_own']) for s in scores.values()):.4f}; cos_shuffled {st.mean(float(s['cos_shuffled']) for s in scores.values()):.4f}; 27B text through 7B AR {st.mean(float(s['cos_own_27b_text']) for s in scores.values()):.4f}; 27B own-AR {st.mean(src[i]['cos_own'] for i in src):.4f} (27B shuffled {st.mean(src[i]['cos_shuffled'] for i in src):.4f}). Parse 8/8, CJK 0/8.\n")
L.append("## Claim annotation (P2) — copied from p2_summary.md\n")
L.append(summary.split("\n", 2)[2])
L.append("\n## All 8 explanations verbatim, next to the last 200 characters of their source\n")
for i in sorted(src):
    L.append(f"### idx {i} (doc row {src[i]['doc_id'].split(':')[-1]})\n")
    L.append(f"SOURCE TAIL: …{src[i]['source_text_full'][-200:]!r}\n")
    L.append(f"7B:\n```\n{gens[i]['explanation_7b']}\n```\n27B:\n```\n{src[i]['explanation']}\n```\n")
L.append("## Review pack\n")
for f in ["p0_tokens.json", "p0_settings.json", "out/p0_acts.npz (gitignored)", "p1_av.jsonl", "p1_scores.csv", "p1_settings.json", "p2_claims_annotated.csv", "p2_judgement_notes.md", "p2_summary.md", "p2_review_blind.csv", "p2_review_key.csv", "p2_settings.json"]:
    p = O / f.split(" ")[0]
    n = sum(1 for _ in open(p)) if p.exists() and p.suffix in {".csv", ".jsonl", ".md"} else (p.stat().st_size if p.exists() else 0)
    L.append(f"- `{f}` — {n} {'lines' if p.suffix in {'.csv', '.jsonl', '.md'} else 'bytes'}")
L.append("\nOpen `p2_review_blind.csv` first, `p2_review_key.csv` after.\n")
L.append("## Provenance\n")
L.append("- Human: the question (same 8 texts through the 7B; like-for-like type × truth table), the texts (the 27B repo's shipped examples), the protocol reuse, the descriptive-only framing (PLAN.md 'Round 5', 2026-09-09).")
L.append("- Agent (bench): `p0_extract.py`, `p1_run.py`, `p2_annotate.py`, `t10_morning.py`; the 7B claim labels (orchestrator, before consulting the 27B rows of the same example; the 27B totals were known); the lexical verbatim-entity proxy in p2_summary (agent choice inside the pre-registration).")
L.append("- Agent (desk, earlier the same day): the 27B run and its subagent annotation.")
L.append("- Not done: no human labels yet; no sampling variants; no additional texts; no positions other than the last token.\n")
L.append("## RUNLOG (round 5)\n")
L += [f"- {l}" for l in runlog]
(O / "MORNING5.md").write_text("\n".join(L))
print("MORNING5.md", len(L), "blocks")

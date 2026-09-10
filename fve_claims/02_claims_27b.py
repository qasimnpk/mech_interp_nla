"""27B variant of 02_claims.py's task builder: same atomic-v1 protocol, same ANNOTATION_GUIDE.md, reads
01_av_27b_25.jsonl instead of 01_av_7b.jsonl. Writes one task-batch JSON for the labeling subagent.
Reuses atomic.py unchanged (model-agnostic)."""
import json
from pathlib import Path
from atomic import PROTOCOL, SUBTYPES, sentence_spans

HERE = Path(__file__).resolve().parent


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def build_tasks(av_file="01_av_27b_25.jsonl"):
    rows = {r["pilot_id"]: r for r in read_jsonl(HERE.parent / "data/redocred_pilot/pilot.jsonl")}
    tasks = {}
    for g in read_jsonl(HERE / av_file):
        r = rows[g["pilot_id"]]
        z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        tasks[g["pilot_id"]] = {
            "protocol": PROTOCOL, "pilot_id": g["pilot_id"], "split": g["split"],
            "prefix_text": r["prefix_text"], "explanation": z, "sentences": sentence_spans(z),
            "annotation_guide": (HERE / "ANNOTATION_GUIDE.md").read_text(),
            "subtypes": {k: sorted(v) for k, v in SUBTYPES.items()},
        }
    return tasks


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--av-file", default="01_av_27b_25.jsonl")
    ap.add_argument("--batch", type=int, required=True)
    a = ap.parse_args()
    tasks = build_tasks(a.av_file)
    out = HERE / "tasks" / f"02_atomic_tasks_27b_batch{a.batch}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(list(tasks.values()), indent=2, ensure_ascii=False))
    print(f"wrote {len(tasks)} tasks (pilot_id {min(tasks)}-{max(tasks)}) to {out}")

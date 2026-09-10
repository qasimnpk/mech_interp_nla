"""Mechanical deletion generator: uses each atom's exact, already-validated av_spans to remove that claim's text from
the explanation and clean up the resulting punctuation. No LLM involved — the spans are exact substrings, so removal
is a deterministic string operation. A claim whose spans overlap another claim's spans in the same document cannot be
removed cleanly; those are flagged preserves_other_propositions=false (excluded from AR scoring by 04_score.py, same
convention the manual rewriters used for genuinely nested claims) rather than forced through.

Usage: python gen_deletions.py --start 63 --end 100   (writes tasks/04_rewrites_7b_doc<NNN>.jsonl for docs with no file yet)
"""
import argparse, json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_atoms(pid: int) -> list[dict]:
    return [json.loads(l) for l in open(HERE / f"tasks/02_atoms_7b_doc{pid:03d}.jsonl")]


def clean(text: str) -> str:
    text = re.sub(r'"\s*"', "", text)
    text = re.sub(r"'\s*'", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.;:!?)])", r"\1", text)
    text = re.sub(r"([,.;:!?])\s*\1+", r"\1", text)
    text = re.sub(r"^\s*[,;:]\s*", "", text, flags=re.M)
    text = re.sub(r"[ \t]*\n[ \t]*", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def remove_spans(z: str, spans: list[tuple[int, int]]) -> str:
    # sort descending so earlier offsets stay valid as we cut
    out = z
    for a, b in sorted(spans, key=lambda s: -s[0]):
        out = out[:a] + out[b:]
    return clean(out)


def overlaps(a1, a2, b1, b2) -> bool:
    return a1 < b2 and b1 < a2


def build_doc(pid: int) -> list[dict]:
    atoms = load_atoms(pid)
    z = atoms[0]["av_spans"][0] and None  # placeholder; explanation not stored per-atom, fetch from tasks file below
    return atoms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    ap.add_argument("--force", action="store_true", help="overwrite existing rewrite files")
    a = ap.parse_args()

    tasks_by_pid = {}
    for f in sorted((HERE / "tasks").glob("02_atomic_tasks_7b_batch*.json")):
        for t in json.loads(f.read_text()):
            tasks_by_pid[t["pilot_id"]] = t

    total = 0
    for pid in range(a.start, a.end):
        outp = HERE / f"tasks/04_rewrites_7b_doc{pid:03d}.jsonl"
        if outp.exists() and not a.force:
            continue
        atoms = load_atoms(pid)
        z = tasks_by_pid[pid]["explanation"]
        records = []
        for c in atoms:
            spans = [(s["start"], s["end"]) for s in c["av_spans"]]
            for s in c["av_spans"]:
                assert z[s["start"]:s["end"]] == s["text"], (pid, c["claim_id"], "span mismatch")
            others = [o for o in atoms if o["claim_id"] != c["claim_id"]]
            overlapping = []
            for o in others:
                for os_ in o["av_spans"]:
                    if any(overlaps(a1, b1, os_["start"], os_["end"]) for a1, b1 in spans):
                        overlapping.append(o["claim_id"])
                        break
            preserves = not overlapping
            if preserves:
                deleted = remove_spans(z, spans)
                assert deleted != z
                rationale = "Mechanical span deletion (exact offsets); no overlapping claim spans in this document."
            else:
                deleted = remove_spans(z, spans)  # best-effort; flagged, excluded from scoring
                rationale = f"Span(s) overlap claim_id(s) {sorted(set(overlapping))}; cannot remove without altering another proposition."
            records.append({
                "protocol": "atomic-v1", "pilot_id": pid, "claim_id": c["claim_id"], "proposition": c["proposition"],
                "original_explanation": z, "deleted_text": deleted, "method": "mechanical-span-deletion",
                "removes_claim": True, "preserves_other_propositions": preserves,
                "reviewer": "script:gen_deletions.py", "rationale": rationale,
                "light_text": None, "heavy_text": None,
            })
        with open(outp, "w") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        total += len(records)
        print(f"doc {pid}: {len(records)} rewrites ({sum(not r['preserves_other_propositions'] for r in records)} flagged overlapping)")
    print("TOTAL", total)


if __name__ == "__main__":
    main()

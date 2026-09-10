"""Add a persistent `final_sentence` (bool) tag to every claim in its authoritative file, derived from
av_spans' sentence_id vs the explanation's actual sentence count (not assumed to always be 3 -- 2 of 100
explanations split into 4 sentences, e.g. on a "U.S." abbreviation). Idempotent: safe to rerun."""
import glob, json
from pathlib import Path
from atomic import sentence_spans

HERE = Path(__file__).resolve().parent

def authoritative_files():
    v2 = {int(Path(f).stem.split("doc")[1]): f for f in glob.glob(str(HERE / "tasks/02_atoms_v2_7b_doc*.jsonl"))}
    v1 = {int(Path(f).stem.split("doc")[1]): f for f in glob.glob(str(HERE / "tasks/02_atoms_7b_doc*.jsonl"))}
    out = dict(v1)
    out.update(v2)  # v2 overrides where present, matching load_atoms()' convention
    return out

def main():
    gens = {json.loads(l)["pilot_id"]: json.loads(l) for l in open(HERE / "01_av_7b.jsonl")}
    files = authoritative_files()
    n_tagged = 0
    counts = {}
    for pid in sorted(files):
        g = gens[pid]
        z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
        n_sents = len(sentence_spans(z))
        path = Path(files[pid])
        recs = [json.loads(l) for l in open(path)]
        for r in recs:
            last_sent_in_claim = max(s["sentence_id"] for s in r["av_spans"])
            r["final_sentence"] = bool(last_sent_in_claim == n_sents - 1)
            n_tagged += 1
            counts.setdefault(r["type"], {}).setdefault(r["truth"], [0, 0])
            counts[r["type"]][r["truth"]][int(r["final_sentence"])] += 1
        path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs))
    print(f"tagged {n_tagged} claims across {len(files)} documents\n")
    print(f"{'type':8s} {'truth':11s} {'final_sentence=False':>22s} {'final_sentence=True':>22s}")
    for t in sorted(counts):
        for tr in sorted(counts[t]):
            f0, f1 = counts[t][tr]
            print(f"{t:8s} {tr:11s} {f0:22d} {f1:22d}")

if __name__ == "__main__":
    main()

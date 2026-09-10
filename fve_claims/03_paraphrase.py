"""Step 3 (planned second step; not part of the baseline): light/aggressive paraphrase tasks per sentence, then merge the
annotators' rewrites and the equivalence verdicts into 03_texts_7b.jsonl (z, z_light, z_aggr per sentence, substituted in
place at the sentence's first exact occurrence). Usage:
  03_paraphrase.py tasks --batch 0 --start 0 --end 25     -> tasks/03_para_tasks_7b_batch0.json
  03_paraphrase.py equiv                                   -> tasks/03_equiv_tasks_7b.json (shuffled, blind to which variant)
  03_paraphrase.py merge                                   -> 03_texts_7b.jsonl (+ counts of dropped rewrites)"""
import argparse, csv, glob, json, random
from common import *

def main():
    raise SystemExit("Legacy sentence paraphrase experiment: disabled pending an atomic paraphrase protocol.")
    ap = argparse.ArgumentParser(); ap.add_argument("mode", choices=["tasks", "equiv", "merge"])
    ap.add_argument("--batch", type=int); ap.add_argument("--start", type=int); ap.add_argument("--end", type=int); a = ap.parse_args()
    sents = list(csv.DictReader(open(HERE / "02_sentences_7b.csv")))
    if a.mode == "tasks":
        rows = [s for s in sents if a.start <= int(s["pilot_id"]) < a.end]
        (HERE / "tasks").mkdir(exist_ok=True)
        (HERE / "tasks" / f"03_para_tasks_7b_batch{a.batch}.json").write_text(json.dumps([{"pilot_id": int(s["pilot_id"]), "sent_no": int(s["sent_no"]), "sentence": s["sentence"]} for s in rows], indent=1, ensure_ascii=False))
        settings(f"03_tasks_b{a.batch}", n=len(rows)); print("03 tasks batch", a.batch, len(rows), "sentences")
    elif a.mode == "equiv":
        paras = []
        for fp in sorted(glob.glob(str(HERE / "tasks" / "03_paraphrases_7b_batch*.csv"))):
            paras += list(csv.DictReader(open(fp)))
        key = {(s["pilot_id"], s["sent_no"]): s["sentence"] for s in sents}
        pairs = []
        for p in paras:
            for kind in ("light", "aggressive"):
                pairs.append({"pair_id": f"{p['pilot_id']}_{p['sent_no']}_{kind}", "a": key[(p["pilot_id"], p["sent_no"])], "b": p[kind]})
        random.Random(20260910).shuffle(pairs)
        for q in pairs: q["b"], q["a"] = (q["a"], q["b"]) if random.Random(q["pair_id"]).random() < 0.5 else (q["b"], q["a"])
        (HERE / "tasks" / "03_equiv_tasks_7b.json").write_text(json.dumps(pairs, indent=1, ensure_ascii=False))
        settings("03_equiv", n_pairs=len(pairs)); print("03 equiv tasks", len(pairs))
    else:
        gens = {g["pilot_id"]: g for g in read_jsonl(HERE / "01_av_7b.jsonl")}
        paras = {}
        for fp in sorted(glob.glob(str(HERE / "tasks" / "03_paraphrases_7b_batch*.csv"))):
            for p in csv.DictReader(open(fp)): paras[(p["pilot_id"], p["sent_no"])] = p
        equiv = {}
        for fp in sorted(glob.glob(str(HERE / "tasks" / "03_equiv_7b*.csv"))):
            for e in csv.DictReader(open(fp)): equiv[e["pair_id"]] = e["verdict"].strip().lower()
        out, dropped, missing = [], 0, 0
        with open(HERE / "03_texts_7b.jsonl", "w") as f:
            for s in sents:
                pid, sn = s["pilot_id"], s["sent_no"]; g = gens[int(pid)]
                z = g["explanation"] if g["parse_ok"] else g["raw_generation"]
                rec = {"pilot_id": int(pid), "sent_no": int(sn), "z": z, "z_del": delete_sentence(z, s["sentence"])}
                p = paras.get((pid, sn))
                for kind in ("light", "aggressive"):
                    v = equiv.get(f"{pid}_{sn}_{kind}")
                    if p is None or not p.get(kind): rec[f"z_{kind}"] = None; missing += 1; continue
                    if v not in (None, "yes"): rec[f"z_{kind}"] = None; dropped += 1; continue
                    a0 = z.find(s["sentence"]); rec[f"z_{kind}"] = z[:a0] + p[kind] + z[a0 + len(s["sentence"]):] if a0 >= 0 else None
                    rec[f"equiv_{kind}"] = v
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); out.append(rec)
        settings("03_merge", n=len(out), dropped_by_equiv=dropped, missing=missing); print("03 merged", len(out), "dropped", dropped, "missing", missing)

if __name__ == "__main__":
    main()

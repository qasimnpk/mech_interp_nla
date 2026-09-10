"""Mechanical entity audit per sentence (no labels): which document entity aliases occur verbatim in the sentence, and which
capitalised non-initial words match no alias (candidate substituted names). Writes 02b_entity_check_7b.csv from the merged
02_sentences_7b.csv. Used for review and as a cross-check of the annotators' entity/truth labels, never as a label itself."""
import csv, re
from common import *

STOP = {"The", "This", "Final", "Wikipedia", "Wiki", "Its", "It", "In", "A", "An", "British", "American", "English", "French", "German", "Australian", "Indian", "Canadian", "European", "Scientific", "Technical", "Biographical", "Historical", "Encyclopedia", "Encyclopedic", "Web", "Journalistic", "Academic", "Narrative", "Structured", "Formal", "Informal"}

def main():
    rows = {r["pilot_id"]: r for r in load_pilot()}
    sents = list(csv.DictReader(open(HERE / "02_sentences_7b.csv")))
    out = []
    for s in sents:
        r = rows[int(s["pilot_id"])]; text = s["sentence"]
        aliases = {}
        for e in r["entities"]:
            for al in set([e["name"]] + e.get("aliases", [])):
                if len(al) >= 3: aliases[al.lower()] = (e["name"], e["type"])
        hits = sorted({f"{v[0]} [{v[1]}]" for al, v in aliases.items() if re.search(r"(?<!\w)" + re.escape(al) + r"(?!\w)", text, re.I)})
        caps = re.findall(r"(?<![.!?\"“(]\s)(?<!^)(?<![\"“(])\b([A-Z][\w'\-]{2,}(?:\s+[A-Z][\w'\-]{2,})*)", text)
        unmatched = sorted({c for c in caps if c.split()[0] not in STOP and not any(re.search(r"(?<!\w)" + re.escape(al) + r"(?!\w)", c, re.I) for al in aliases) and not re.search(r"(?<!\w)" + re.escape(c) + r"(?!\w)", r["prefix_text"])})
        out.append({"pilot_id": s["pilot_id"], "sent_no": s["sent_no"], "n_alias_hits": len(hits), "alias_hits": "; ".join(hits), "n_unmatched_caps": len(unmatched), "unmatched_caps": "; ".join(unmatched), "sentence": text})
    with open(HERE / "02b_entity_check_7b.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), quoting=csv.QUOTE_ALL); w.writeheader(); w.writerows(out)
    n = len(out); print(f"02b: {n} sentences; with ≥1 alias hit {sum(o['n_alias_hits']>0 for o in out)}; with ≥1 unmatched capitalised word {sum(o['n_unmatched_caps']>0 for o in out)}")
    for o in out[:6]: print(f"  {o['pilot_id']}/{o['sent_no']} hits={o['alias_hits'] or '-'} | unmatched={o['unmatched_caps'] or '-'}")

if __name__ == "__main__":
    main()

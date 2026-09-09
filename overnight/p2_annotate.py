"""P2 (round 5): orchestrator annotation of the 8 7B explanations (p1_av.jsonl) under
notes/nla_setup/claim_annotation_protocol.md, applied verbatim; judged against source_text_full only.
The ROWS below ARE the annotation (written by the orchestrator, Claude, 2026-09-09, before consulting the 27B CSV rows of the
same example; the 27B cross-tab totals were known). Outputs: p2_claims_annotated.csv, p2_judgement_notes.md, p2_summary.md,
p2_review_blind.csv, p2_review_key.csv, p2_settings.json."""
import csv, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import nla_lib as L

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "notes/nla_setup/nla27b_smoke_examples_full.json"
CSV27 = ROOT / "notes/nla_setup/nla27b_smoke_claims_annotated.csv"

# (idx, claim_text, type, truth, evidence_span, note)
ROWS = [
 # ---- idx 0 (Sayaji crusher SEO page) ----
 (0, "Indian seller / website", "entity", "true", "Sayaji Limestone Crusher Turnkey India", "India, new delhi, kerala, baroda in text; contact block is Shanghai"),
 (0, "machinery product seller website", "theme", "true", "Crusher Parts, Crusher Spares, Crusher Spare Parts", ""),
 (0, "steel product seller", "detail", "unsupported", "", "steel appears only as jaw-plate material (super high manganese steel); products are crushers/mills"),
 (0, "multiple product listing images", "detail", "unsupported", "", "no images mentioned"),
 (0, "text blocks of product listings", "theme", "true", "Jaw Crusher Spring Cone Crusher the introduction of the new style", ""),
 (0, "mixing product details and contact info", "theme", "true", "Contact Us. Tel 86-21-58386256 Office Add Pudong New Area", ""),
 (0, "contains the phrase 'price list for cement block machine'", "detail", "false", "what is the cost of sayaji jaw crusher 20 10 see more.Price list for", "text: crushers; expl: cement block machine (same domain: machinery)"),
 (0, "'in bangalore'", "entity", "false", "sayaji crusher new delhi ... suppliers in kerala ... baroda", "text: new delhi / kerala / baroda; expl: bangalore (same domain: Indian city)"),
 (0, "query / listing format with 'price list' entries", "theme", "true", "Price list for", ""),
 (0, "'product parts' entries", "detail", "true", "jaw crusher part list of size 42 8 sayaji", ""),
 (0, "'steel mill machinery' entries", "detail", "false", "raymond mill ... Vertical hammer mill ... cement mill", "text: raymond/hammer/cement mill; expl: steel mill (same domain)"),
 (0, "likely a query or contact listing format", "theme", "true", "Contact Us ... what is the cost of sayaji jaw crusher", ""),
 (0, "final token is 'for'", "forecast", "true", "Price list for", ""),
 (0, "ends an incomplete phrase", "forecast", "true", "Price list for", ""),
 (0, "preceding text reads 'price list price list price for'", "detail", "false", "what is the cost of sayaji jaw crusher 20 10 see more.Price list for", "invented repetition; same domain"),
 (0, "part of a third listing item", "detail", "unsupported", "", "'third' not checkable"),
 (0, "expects a noun phrase like 'cement block plant' / 'old machinery parts'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 1 (Yorkshire Regiment memorial bios; Sinclair-Maclagan) ----
 (1, "British military history account", "theme", "true", "enlisted in the Yorkshire Regiment as 14136 Private Morris", ""),
 (1, "the subject is Captain Agnew", "entity", "false", "Ewen George Sinclair-Maclagan ... was promoted Captain in 1898", "text: Sinclair-Maclagan (also Morris, Barker); expl: Agnew (same domain: British surname)"),
 (1, "account of a captain's career", "detail", "true", "was promoted Captain in 1898", ""),
 (1, "biographical narrative", "theme", "true", "was born on the 24th December 1868 in Edinburgh", ""),
 (1, "detailing postings", "theme", "true", "In 1901 he was posted to Australia", ""),
 (1, "service during WWI", "detail", "true", "He was wounded in December 1915 and again in November 1916", "true for the first two bios; the section at the token is pre-WWI"),
 (1, "career continued with a captaincy", "detail", "true", "was promoted Captain in 1898", "inside an invented quotation"),
 (1, "he was posted to the Royal Marines", "entity", "false", "commissioned as 2nd Lieutenant in the Border Regiment ... Adjutant to the New South Wales Scottish Rifles", "text: Border Regiment / NSW Scottish Rifles; expl: Royal Marines (same domain)"),
 (1, "promoted to Major", "detail", "unsupported", "", "inside the invented quotation; text ends at 'Promoted'"),
 (1, "lists career promotions with dates and details", "theme", "true", "was promoted Captain in 1898", ""),
 (1, "sequence of military rank progression and service history", "theme", "true", "commissioned as 2nd Lieutenant ... promoted Captain", ""),
 (1, "final token is 'Promoted'", "forecast", "true", "Promoted", ""),
 (1, "final token is mid-sentence", "forecast", "true", "resumed regimental duty in Britain. Promoted", "new sentence, cut after one word"),
 (1, "'Promoted' immediately follows another 'Promoted' (mid-list 'Promoted... Promoted')", "detail", "false", "In 1904 Maclagan resumed regimental duty in Britain. Promoted", "no adjacent repetition; same domain"),
 (1, "part of a sequence of career promotions", "theme", "true", "was promoted Captain in 1898", ""),
 (1, "expects 'Lieutenant Colonel in 1915' / 'Major General in April 1916'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 2 (Eloisia Wild bio) ----
 (2, "British", "entity", "unsupported", "", "Durrell Institute / Outer Hebrides are UK but no nationality stated; consistent with the 27B labelling of unnamed countries"),
 (2, "adventure sports photographer", "detail", "false", "Eloisia Wild is a Conservationist", "text: Conservationist; expl: photographer (adventure theme fits; profession substituted)"),
 (2, "eco-conservation focus", "theme", "true", "wildlife conservation projects ... marine mammals", ""),
 (2, "listing her outdoor experiences", "theme", "true", "solo coast to coast cycle in high winds through the Outer Hebrides", ""),
 (2, "listing qualifications", "theme", "true", "MSc in Conservation Science ... PADI diving certifications", ""),
 (2, "for the UK Wildlife Conservation event", "entity", "false", "Eloisia Wild is a Conservationist; graduating from Durrell Institute", "no event; a bio (invented event, same domain)"),
 (2, "the subject is Sara", "entity", "false", "Eloisia Wild is a Conservationist", "text: Eloisia; expl: Sara (same domain: first name); occurs twice ('Sara is', 'Sara has'), counted once"),
 (2, "passion for adventure and conservation work", "detail", "true", "extreme weather expeditions ... wildlife conservation projects", "inside the invented quotation; 'Wildlife Photographer' there duplicates the photographer claim, counted once"),
 (2, "concluding section listing additional attributes / career highlights", "theme", "true", "Eloisia has", "final paragraph opener"),
 (2, "bio format", "theme", "true", "Eloisia Wild is a Conservationist", ""),
 (2, "content: her recent projects and goals", "detail", "true", "big icy cycle expedition planned for 2020 ... This year she has been busy", ""),
 (2, "final token is 'has'", "forecast", "true", "Eloisia has", ""),
 (2, "final token is mid-sentence", "forecast", "true", "Eloisia has", ""),
 (2, "the subject is Hannah", "entity", "false", "Eloisia has", "text: Eloisia; expl: Hannah (same domain; the 27B made the same substitution)"),
 (2, "part of a second attribute listing", "detail", "false", "Eloisia has completed ... She has also been busy ... Eloisia has", "at least the third 'has' listing"),
 (2, "expects 'a strong connection to' / 'multiple passions including'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 3 (bibliography list) ----
 (3, "scientific journal article format", "theme", "true", "CicArVarDB: SNP and InDel database for advancing genetics research", "a list of titles"),
 (3, "with abstracts", "detail", "false", "subject area of - CicArVarDB ... - Contagious Bovine", "titles only, no abstracts (same domain)"),
 (3, "academic metadata", "theme", "true", "subject area of", ""),
 (3, "scholarly content about ecology", "theme", "true", "Forest-linked livelihoods in a globalized world", ""),
 (3, "citation metrics", "theme", "true", "Geographic bias in citation rates of", ""),
 (3, "an item about publication / citation bias", "detail", "true", "Geographic bias in citation rates of", ""),
 (3, "that item is the second item", "detail", "false", "- Geographic bias in citation rates of", "it is the fifth list item"),
 (3, "the phrase is 'Gender bias in citation counts of'", "detail", "false", "Geographic bias in citation rates of", "text: Geographic bias; expl: Gender bias (same domain: bias type); occurs twice, counted once"),
 (3, "'citation counts of'", "detail", "true", "citation rates of", "near-verbatim"),
 (3, "suggests a citation analysis / academic metadata study", "theme", "true", "Geographic bias in citation rates of", ""),
 (3, "journal or country ranking study", "detail", "unsupported", "", ""),
 (3, "implies a third item or data visualization about international research output", "detail", "unsupported", "", ""),
 (3, "final token is 'of'", "forecast", "true", "citation rates of", ""),
 (3, "ends the incomplete noun phrase 'citation rates of'", "forecast", "true", "citation rates of", ""),
 (3, "part of a citation study title", "theme", "true", "Geographic bias in citation rates of", ""),
 (3, "expects 'scientific papers' / 'developing country journals'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 4 (Vibha Seattle Holi) ----
 (4, "blog post / bylined article", "theme", "true", "By: Anita Ambalavanan", ""),
 (4, "written by a student", "detail", "unsupported", "", "no student mentioned"),
 (4, "informal tone", "theme", "true", "March 19th was quite a colorful day", ""),
 (4, "personal perspective", "theme", "unsupported", "", "third-person report"),
 (4, "on Indian culture", "theme", "true", "celebrated their second big Holi Event, 'Holi Hai'", ""),
 (4, "and service / volunteering", "theme", "true", "accumulated more than 150 volunteers", ""),
 (4, "a high school student's involvement", "detail", "unsupported", "", "no student"),
 (4, "the Jewish community's charity event", "entity", "false", "Vibha Seattle successfully celebrated their second big Holi Event", "text: Vibha / Holi; expl: Jewish community (FOREIGN domain)"),
 (4, "a charity event", "detail", "true", "came out to support Vbha ... 150 volunteers", ""),
 (4, "'Her passion for the event has grown over the years'", "detail", "false", "While the Vibha Seattle action center is rather young, only launching in October of 2012", "invented subject/sentence; same domain"),
 (4, "signals information about the fundraising event's purpose", "theme", "unsupported", "", ""),
 (4, "'charity fair'", "detail", "false", "Holi Event, 'Holi Hai'", "text: Holi event; expl: charity fair (same domain)"),
 (4, "final token is 'annual'", "forecast", "true", "The annual", ""),
 (4, "mid-phrase 'the annual'", "forecast", "true", "The annual", ""),
 (4, "directly continuing the sentence about the student's fundraising event", "detail", "false", "spreading the word about Vibha. The annual", "'The annual' opens a new sentence; no student"),
 (4, "expects 'Charity Fair' / 'India Day competition'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 5 (Wellington Jump Platform water quality) ----
 (5, "Australian", "entity", "unsupported", "", "Wellington / Taranaki named, no country; same labelling as the 27B row"),
 (5, "environmental / technical report format", "theme", "true", "monitoring showed that the water quality in the area exceeded the marine guidelines", ""),
 (5, "scientific data in a structured abstract format", "theme", "true", "median enterococci concentration of 460 CFU/100 mL", ""),
 (5, "water quality monitoring results", "theme", "true", "monitoring showed that the water quality", ""),
 (5, "for a dairy farm", "entity", "false", "The Jump Platform on Wellington Waterfront is a public facility", "text: waterfront jump platform / stormwater; expl: dairy farm (FOREIGN domain; the 27B made the same substitution)"),
 (5, "E. coli levels", "detail", "false", "median enterococci concentration", "text: enterococci; expl: E. coli (same domain; the 27B made the same substitution)"),
 (5, "'the BMP program'", "detail", "false", "Following the installation of an enclosure around the Jump Platform area", "text: enclosure / baffle; expl: BMP program (same domain)"),
 (5, "levels reduced following the implementation", "detail", "true", "the enterococci concentration fell from a median value of 865 CFU/100mL prior to the baffle installation", ""),
 (5, "'mean' levels", "detail", "false", "median value of 865 CFU/100mL", "text: median; expl: mean (same domain)"),
 (5, "numerical pre/post comparison", "theme", "true", "fell from a median value of 865 CFU/100mL prior to the baffle installation, to", ""),
 (5, "a specific range is expected next", "forecast", "unsupported", "", "past truncation"),
 (5, "final token is 'to'", "forecast", "true", "prior to the baffle installation, to", ""),
 (5, "ends an incomplete numerical comparison clause", "forecast", "true", "fell from a median value of 865 CFU/100mL ... to", ""),
 (5, "'from an average count of 1,450 per litre'", "detail", "false", "median value of 865 CFU/100mL", "text: 865 CFU/100mL (and 460); expl: 1,450 per litre (same domain, unit garbled)"),
 (5, "requires a numeric value next ('a mean of 150' / 'zero')", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 6 (GRB two-component jet abstract) ----
 (6, "scientific paper abstract format", "theme", "true", "Recent observational and theoretical studies have raised the possibility", ""),
 (6, "LaTeX formatting", "detail", "unsupported", "", "Greek symbols present, no LaTeX markup"),
 (6, "discussing GRB jet models", "theme", "true", "collimated outflows in gamma-ray burst (GRB) sources have two distinct components", ""),
 (6, "using numerical simulations", "detail", "false", "Using a simple synchrotron emission model, we calculate ... derive algebraic expressions", "text: analytic model / algebraic expressions; expl: numerical simulations (same domain)"),
 (6, "observational constraints", "detail", "true", "Recent observational and theoretical studies", ""),
 (6, "on GRB afterglow emission", "theme", "true", "R-band afterglow light curves", ""),
 (6, "the model predicts time-dependent polarization", "detail", "false", "derive algebraic expressions for the flux ratios of the emission from the two jet components", "text: flux ratios; expl: polarization (same domain)"),
 (6, "of the progenitor's cold dust", "detail", "false", "narrow ... highly relativistic ... outflow ... and a wider ... moderately relativistic ... surrounding flow", "text: two jet components; expl: progenitor cold dust (same domain, foreign to the passage)"),
 (6, "concluding statement about the afterglow light curve", "theme", "true", "at the main transition times in the light curve. For viewing angles", ""),
 (6, "suggests the term 'afterglow flux'", "forecast", "unsupported", "", "past truncation"),
 (6, "final token is 'after'", "forecast", "true", "the wide component to the optical after", ""),
 (6, "final token is mid-word (after|glow)", "forecast", "unsupported", "", "past truncation; same labelling as the 27B row"),
 (6, "preceding text reads 'the cold afterglow after'", "detail", "false", "the contribution of the wide component to the optical after", "invented phrase; same domain"),
 (6, "contains the phrase 'the observed GRB optical afterglow's delayed decay'", "detail", "false", "R-band afterglow light curves", "invented phrase"),
 (6, "expects 'glow flux' / 'afterglow light curve' / 'glow decay is detected'", "forecast", "unsupported", "", "past truncation"),
 # ---- idx 7 (Boeing 787 battery AD) ----
 (7, "news release format", "theme", "true", "the FAA issued an emergency airworthiness directive (AD)", ""),
 (7, "corporate", "detail", "unsupported", "", "issuer is the FAA; 'corporate' contradicted by the claim's own 'U.S. government'"),
 (7, "U.S. government safety announcement", "theme", "true", "the FAA issued an emergency airworthiness directive", ""),
 (7, "describing a Boeing aircraft event", "entity", "true", "Boeing 787 battery incident in Japan", ""),
 (7, "factual details about autonomous vehicle testing", "detail", "false", "Boeing 787 battery incident ... lithium ion battery", "text: aircraft battery incident; expl: autonomous vehicle testing (FOREIGN domain)"),
 (7, "the incidents resulted in the release of electrolytic fluids", "detail", "true", "The battery failures resulted in release of flammable electrolytes", ""),
 (7, "the fluids were 'heated' / 'corrosive'", "detail", "false", "release of flammable electrolytes", "text: flammable; expl: heated / corrosive (same domain); three occurrences, counted once"),
 (7, "chemical hazards from the battery", "detail", "true", "potential battery fire risk ... release of flammable electrolytes", ""),
 (7, "battery cell rupture", "detail", "unsupported", "", "not stated"),
 (7, "final token is 'electrolytes'", "forecast", "true", "release of flammable electrolytes", ""),
 (7, "ends mid-clause", "forecast", "true", "release of flammable electrolytes", "truncated without a full stop"),
 (7, "part of a parenthetical example listing", "detail", "false", "The battery failures resulted in release of flammable electrolytes", "main clause, no parenthetical"),
 (7, "expects 'and smoke' / 'into the vehicle' / 'and fire'", "forecast", "unsupported", "", "past truncation"),
]

JUDGEMENT_NOTES = """# P2 judgement calls (orchestrator; one line each)
- Unnamed countries ('British' idx 2, 'Australian' idx 5): unsupported, not false, matching the 27B annotation's choice; both are wrong by world knowledge, which the protocol excludes.
- 'Final token is mid-word' (idx 6 after|glow): unsupported (past truncation), matching the 27B row; 'ends an incomplete phrase/clause' claims judged on the visible text.
- Repeated substitutions inside one explanation counted once with occurrence noted: Sara ×2 (idx 2), photographer ×2 (idx 2), Gender bias ×2 (idx 3), heated/corrosive ×3 (idx 7).
- Invented quotations split into their propositions; a proposition supported by the text is true even though the quotation is invented (idx 1 'career continued with a captaincy'; idx 2 'passion for adventure and conservation').
- idx 1 'service during WWI': true (Morris, Barker) though the token's own paragraph (Sinclair-Maclagan to 1904) is pre-WWI.
- idx 3 'scientific journal article format': true for a list of scholarly titles; 'with abstracts' false.
- idx 4 'a charity event': true on 'support Vbha' + volunteers; 'personal perspective' unsupported (third-person report).
- idx 5 'mean' vs 'median': counted as a false detail.
- idx 7 'corporate' unsupported rather than false (the claim itself says 'U.S. government'); 'chemical hazards from the battery' true, 'cell rupture' split off as unsupported.
- Forecasts naming the final token correctly are true; any prediction past the truncation is unsupported, including grammatically forced ones.
"""

def crosstab(rows):
    ct = defaultdict(Counter)
    for r in rows:
        ct[r["type"]][r["truth"]] += 1
    return ct

def per_example(rows):
    out = defaultdict(Counter)
    for r in rows:
        out[int(r["idx"])]["n"] += 1
        out[int(r["idx"])][r["truth"]] += 1
    return out

def fmt_ct(ct, title):
    types = ["entity", "detail", "theme", "forecast", "other"]
    lines = [f"**{title}**", "", "| type | true | false | unsupported | total |", "|---|---|---|---|---|"]
    tot = Counter()
    for t in types:
        c = ct.get(t, Counter()); n = sum(c.values())
        if n == 0 and t == "other":
            lines.append(f"| {t} | 0 | 0 | 0 | 0 |"); continue
        lines.append(f"| {t} | {c['true']} | {c['false']} | {c['unsupported']} | {n} |")
        tot.update(c)
    lines.append(f"| **all** | {tot['true']} | {tot['false']} | {tot['unsupported']} | {sum(tot.values())} |")
    return "\n".join(lines)

def verbatim_entities(expl, source):
    """Lexical: capitalised, non-sentence-initial tokens of the explanation (len>2) that occur verbatim in the source."""
    toks = re.findall(r"(?<![.!?\n]\s)(?<!^)\b([A-Z][A-Za-z0-9\-']{2,})\b", expl)
    stop = {"The", "This", "Final", "Wikipedia", "Wiki", "SEO", "Scientific", "Technical", "British", "American", "Australian", "Indian", "Web-scraped", "Web", "Biographical", "Military", "Academic", "Journalistic", "Narrative", "Student", "Aviation"}
    hits = sorted({t for t in toks if t not in stop and re.search(r"\b" + re.escape(t) + r"\b", source)})
    return hits

def main():
    S = L.Settings("p2", protocol="notes/nla_setup/claim_annotation_protocol.md", annotator="orchestrator (Claude Fable 5.1)",
                   inputs=["p1_av.jsonl", str(SRC)], comparison_csv=str(CSV27), label_source="claude", provisional=True)
    src = {r["idx"]: r for r in json.loads(SRC.read_text())}
    gens = {json.loads(l)["idx"]: json.loads(l) for l in open(L.OVERNIGHT / "p1_av.jsonl")}
    rows = []
    counter = Counter()
    for idx, text, typ, truth, ev, note in ROWS:
        counter[idx] += 1
        rows.append({"idx": idx, "claim_no": counter[idx], "claim_text": text, "type": typ, "truth": truth, "evidence_span": ev, "note": note})
    assert all(r["type"] in {"entity", "detail", "theme", "forecast", "other"} and r["truth"] in {"true", "false", "unsupported"} for r in rows)
    with open(L.OVERNIGHT / "p2_claims_annotated.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["idx", "claim_no", "claim_text", "type", "truth", "evidence_span", "note"], quoting=csv.QUOTE_ALL)
        w.writeheader(); w.writerows(rows)
    (L.OVERNIGHT / "p2_judgement_notes.md").write_text(JUDGEMENT_NOTES)
    rows27 = list(csv.DictReader(open(CSV27)))
    ct7, ct27 = crosstab(rows), crosstab(rows27)
    pe7, pe27 = per_example(rows), per_example(rows27)
    # review pack: blind (no labels) and key
    with open(L.OVERNIGHT / "p2_review_blind.csv", "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL); w.writerow(["idx", "claim_no", "claim_text", "source_tail_300"])
        for r in rows: w.writerow([r["idx"], r["claim_no"], r["claim_text"], src[r["idx"]]["source_text_full"][-300:]])
    with open(L.OVERNIGHT / "p2_review_key.csv", "w", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL); w.writerow(["idx", "claim_no", "type", "truth", "evidence_span", "note"])
        for r in rows: w.writerow([r["idx"], r["claim_no"], r["type"], r["truth"], r["evidence_span"], r["note"]])
    # verbatim entity mentions (lexical) for both models
    ve = {}
    for i in sorted(src):
        ve[i] = {"7b": verbatim_entities(gens[i]["explanation_7b"], src[i]["source_text_full"]),
                 "27b": verbatim_entities(src[i]["explanation"], src[i]["source_text_full"])}
    # false entity / detail lists
    def false_list(rs, model):
        return [f"- idx {r['idx']} [{r['type']}] {r['claim_text']} — {r['note']}" for r in rs if r["truth"] == "false" and r["type"] in ("entity", "detail")]
    lines = ["# P2 summary — claim type × truth, 7B (round 5) vs 27B (pod smoke, notes/nla_setup), same 8 texts, last token, greedy 200 tokens", "",
             "Labels: orchestrator (7B, this round) and a desk subagent (27B, 2026-09-09), both under notes/nla_setup/claim_annotation_protocol.md; PROVISIONAL until human review of p2_review_blind.csv.", "",
             fmt_ct(ct7, "7B — kitft/nla-qwen2.5-7b-L20 (layer 20), n = 8 explanations"), "",
             fmt_ct(ct27, "27B — ceselder/qwen3.6-27b-nla-rl adapter 600 (layer 42), n = 8 explanations"), "",
             "## Per example", "", "| idx | 7B n / true / false / unsupported | 27B n / true / false / unsupported | 7B verbatim source entities (lexical) | 27B verbatim source entities (lexical) |", "|---|---|---|---|---|"]
    for i in sorted(src):
        a, b = pe7[i], pe27[i]
        lines.append(f"| {i} | {a['n']} / {a['true']} / {a['false']} / {a['unsupported']} | {b['n']} / {b['true']} / {b['false']} / {b['unsupported']} | {', '.join(ve[i]['7b']) or '—'} | {', '.join(ve[i]['27b']) or '—'} |")
    n7v = sum(1 for i in ve if ve[i]["7b"]); n27v = sum(1 for i in ve if ve[i]["27b"])
    lines += ["", f"Explanations with ≥ 1 verbatim source entity (lexical proxy, capitalised non-initial tokens, stoplist of genre adjectives): 7B {n7v}/8, 27B {n27v}/8.", "",
              "## False entity and detail claims — 7B", *false_list(rows, "7b"), "", "## False entity and detail claims — 27B", *false_list(rows27, "27b"), "",
              "## Shared substitutions (same wrong value in both models)",
              "- idx 2: Eloisia → Hannah (both).", "- idx 5: enterococci → E. coli (both); jump platform → dairy farm (both).", "",
              "## Judgement calls", JUDGEMENT_NOTES.split("\n", 1)[1]]
    (L.OVERNIGHT / "p2_summary.md").write_text("\n".join(lines))
    S.finish(n_claims_7b=len(rows), crosstab_7b={t: dict(c) for t, c in ct7.items()}, n_claims_27b=len(rows27), crosstab_27b={t: dict(c) for t, c in ct27.items()},
             per_example_7b={i: dict(c) for i, c in pe7.items()}, verbatim_entities=ve)
    print("\n".join(lines[:40]))

if __name__ == "__main__":
    main()

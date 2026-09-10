"""Score-blind atomic annotation records and explicit deletion validation (stdlib only)."""
import re

PROTOCOL = "atomic-v1"
# Truth scheme v2 (2026-09-09 22:40, human): true | false (+ related: related|unrelated) | irrelevant (forecast / model_output)
TRUTH = {"true", "false", "irrelevant"}
RELATED = {"related", "unrelated"}
SUBTYPES = {
    "entity": {"identity", "identification", "relationship"},
    "detail": {"date", "quantity", "event", "attribute", "cause", "local_text", "exact_words", "final_word", "final_token"},
    "theme": {"topic", "genre", "language", "style", "format"},
    "forecast": {"continuation", "model_output"},
}


def sentence_spans(text):
    """Display/context boundaries only, never claim boundaries. Keep short fragments."""
    spans, start, quoted = [], 0, False
    for i, ch in enumerate(text):
        if ch in '\"“”':
            quoted = not quoted
        if ch == '\n' or (ch in '.!?' and not quoted and (i + 1 == len(text) or text[i + 1].isspace())):
            end = i if ch == '\n' else i + 1
            a, b = start, end
            while a < b and text[a].isspace(): a += 1
            while b > a and text[b - 1].isspace(): b -= 1
            if a < b: spans.append({"sentence_id": len(spans), "start": a, "end": b, "text": text[a:b]})
            start = i + 1
    if text[start:].strip():
        a = start + len(text[start:]) - len(text[start:].lstrip())
        b = len(text.rstrip())
        spans.append({"sentence_id": len(spans), "start": a, "end": b, "text": text[a:b]})
    return spans


def check_span(span, text):
    a, b = span["start"], span["end"]
    if type(a) is not int or type(b) is not int or not 0 <= a < b <= len(text):
        raise ValueError("Invalid character offsets")
    if span["text"] != text[a:b]:
        raise ValueError("Span text does not match exact source")


def validate_claims(claims, tasks):
    """Validate provenance/schema, not semantic judgments or semantic deduplication."""
    seen, propositions = set(), set()
    for c in claims:
        if c.get("protocol") != PROTOCOL:
            raise ValueError("Expected atomic-v1 annotation; sentence labels cannot be reused")
        key = (c["pilot_id"], c["claim_id"])
        if type(c["pilot_id"]) is not int or type(c["claim_id"]) is not int or c["claim_id"] < 0 or key in seen:
            raise ValueError("Invalid or duplicate claim ID")
        seen.add(key)
        t = tasks[c["pilot_id"]]
        p = c["proposition"].strip()
        norm = (c["pilot_id"], re.sub(r"\s+", " ", p).casefold())
        if not p or norm in propositions:
            raise ValueError("Empty or duplicate proposition; merge equivalent occurrences")
        propositions.add(norm)
        if c["type"] not in SUBTYPES or c["subtype"] not in SUBTYPES[c["type"]]:
            raise ValueError("Unknown type/subtype")
        if c["truth"] not in TRUTH:
            raise ValueError("Unknown truth label (v2: true | false | irrelevant)")
        if (c["type"] == "forecast" or c["subtype"] == "model_output") != (c["truth"] == "irrelevant"):
            raise ValueError("Forecast / model_output claims are exactly the 'irrelevant' class")
        if c["truth"] == "false":
            if c.get("related") not in RELATED:
                raise ValueError("False claims need related: related | unrelated")
        elif c.get("related") not in (None, "", "NA"):
            raise ValueError("related is only for false claims")
        if c["subtype"] == "final_token" and c["review_flag"] is not True:
            raise ValueError("Final-token claims must carry review_flag=True (checked against the pilot final_word)")
        if type(c["review_flag"]) is not bool:
            raise ValueError("review_flag must be boolean")
        if not re.fullmatch(r"prefix: .+; AV: .+", c["rationale"], re.S):
            raise ValueError("Use rationale 'prefix: …; AV: …'")
        if not c["av_spans"]:
            raise ValueError("Missing AV provenance")
        sentences = {s["sentence_id"]: s for s in t["sentences"]}
        for span in c["av_spans"]:
            check_span(span, t["explanation"])
            s = sentences[span["sentence_id"]]
            if not s["start"] <= span["start"] < span["end"] <= s["end"]:
                raise ValueError("AV span lies outside its sentence; use multiple spans")
        for span in c["prefix_evidence"]:
            check_span(span, t["prefix_text"])
        if c["truth"] == "true" and not c["prefix_evidence"]:
            raise ValueError("True claims require visible prefix evidence")
        if c["truth"] == "false" and not c["prefix_evidence"] and "absent" not in c["rationale"].lower():
            raise ValueError("False claims need contradicting prefix evidence, or a rationale saying the specific is absent")
    return claims


def validate_deletions(deletions, claims, tasks):
    """Require explicit reviewed counterfactuals; never delete provenance spans automatically."""
    claim_lookup = {(c["pilot_id"], c["claim_id"]): c for c in claims}
    keys = set(claim_lookup)
    seen = set()
    for d in deletions:
        key = (d["pilot_id"], d["claim_id"])
        if d.get("protocol") != PROTOCOL or key not in keys or key in seen:
            raise ValueError("Unknown, duplicate, or legacy deletion")
        seen.add(key)
        if d.get("proposition") != claim_lookup[key]["proposition"]:
            raise ValueError("Deletion reviewed against a different proposition")
        z = tasks[d["pilot_id"]]["explanation"]
        if d["original_explanation"] != z:
            raise ValueError("Deletion reviewed against a different explanation")
        if not isinstance(d["deleted_text"], str) or not d["deleted_text"].strip() or d["deleted_text"] == z:
            raise ValueError("Deletion must produce a nonempty changed explanation")
        if d.get("removes_claim") is not True or d.get("preserves_other_propositions") is not True:
            raise ValueError("Deletion needs review: remove all occurrences and preserve every other proposition")
        if not d.get("reviewer", "").strip() or not d.get("rationale", "").strip():
            raise ValueError("Deletion needs reviewer and rationale")
    return deletions

"""A1 — natural AV claims: paraphrase-averaged semantic preference (PLAN.md round 4, human-designed; PRIMARY NATURAL RESULT).

  uv run python overnight/a1_natural.py          # re-entrant; exits 0 with AWAITING_AGENT_TASKS / MISSING between phases

V0 cut rules applied: A1(a) paraphrases light1 + aggr1 only; A1(b) no negation candidate; A1(c) 40 contexts (dev 0–9, eval 10–39).
Phases: select (wikitext-2 train, rng 4, sentence rule) → target (out/a1_acts.npz) → av (sampled, seed 4000 + context_id; never
regenerated) → slots by rule → agent slot_verify (+ repeated-fact checks) → agent label (originals) → agent correction → agent
edit_check + label (corrections) → deterministic entity_sub + agent detail_sub / relation_rev → agent edit_check → agent label
(candidates) → agent rewrite → agent equiv (shuffled, seed 9000) → AR → analysis (a1_analyze.py).
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import r4_lib as R  # noqa: E402
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

STAGE, PFX = "A1", "a1"
N_CTX, N_DEV = 40, 10
TRANSFORMS = ["light1", "aggr1"]
NEGATION = False
ACTS = L.OUT / "a1_acts.npz"
PREDS = L.OUT / "a1_preds.npz"
F = {k: L.OVERNIGHT / f"{PFX}_{k}" for k in ["contexts.csv", "av.jsonl", "slots.csv", "candidates.jsonl", "realizations.jsonl", "texts.jsonl", "scores.csv", "selection.csv"]}
STOP = {"Wikipedia", "Wiki", "English", "The", "This", "A", "An", "In", "It", "Its", "I", "Final"}
MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
          "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
REL_WORDS = ["before", "after", "first", "last", "earlier", "later", "during", "until", "since", "succeeded", "failed", "won", "lost", "born", "died",
             "founded", "released", "defeated", "elected", "became", "moved", "married"]
MAX_AR_TOKENS = 1024
MIN_WORDS_SLOT = 6


def cap_noninitial(text: str) -> list[str]:
    """Capitalised tokens that are not sentence-initial (sentence = split on . ! ? and newlines)."""
    out = []
    for sent in re.split(r"(?<=[.!?])\s+|\n+", text):
        ws = R._words(sent)
        out += [w for w in ws[1:] if w[0].isupper()]
    return out


def phase_select(prog: R.Progress, tok) -> pd.DataFrame:
    if F["selection.csv"].exists() and F["contexts.csv"].exists():
        return pd.read_csv(F["contexts.csv"], keep_default_na=False)
    prog.set_phase("select")
    ds = R.wikitext_train()
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False); used = set(int(x) for x in st.doc_idx)
    cand, ntok = [], {}
    for i in range(len(ds)):
        if i in used:
            continue
        ids = tok(ds[i]["page"], add_special_tokens=False)["input_ids"]
        if len(ids) >= 256:
            cand.append(i); ntok[i] = ids
    L.log(f"A1 select: {len(cand)} candidate documents (>=256 tokens, not in stimuli)")
    order = np.random.default_rng(4).permutation(len(cand))
    rows, ctxs = [], []
    for k in order:
        i = cand[k]; ids = ntok[i]
        t_sel = None
        for t in range(255, 126, -1):
            if t + 1 >= len(ids):
                continue
            a = tok.decode([ids[t]]).strip(); b = tok.decode([ids[t + 1]])
            if a in {".", "!", "?"} and (b.startswith(" ") or b.startswith("\n") or (b[:1].isupper())):
                t_sel = t; break
        rec = {"doc_idx": i, "selection_order": len(rows), "n_doc_tokens": len(ids), "t": t_sel if t_sel is not None else -1, "skip_reason": ""}
        if t_sel is None:
            rec["skip_reason"] = "no_sentence_end_in_range"
        else:
            text = tok.decode(ids[:t_sel + 1]); ncap = len(cap_noninitial(text))
            rec["n_cap_noninitial"] = ncap
            if ncap < 3:
                rec["skip_reason"] = "lt3_capitalised_noninitial"
            else:
                cid = len(ctxs)
                ctxs.append({"context_id": cid, "split": "dev" if cid < N_DEV else "eval", "source": f"wikitext-2 train doc {i}", "doc_idx": i, "text_full": text,
                             "n_tokens": t_sel + 1, "t": t_sel, "token_id": int(ids[t_sel]), "token_str": tok.decode([ids[t_sel]]), "next_token_str": tok.decode([ids[t_sel + 1]]),
                             "n_cap_noninitial": ncap, "layer_index": 20, "hidden_states_index": 21, "weights": "TARGET", "ids": json.dumps(ids[:t_sel + 1])})
        rows.append(rec)
        if len(ctxs) >= N_CTX:
            break
    pd.DataFrame(rows).to_csv(F["selection.csv"], index=False)
    df = pd.DataFrame(ctxs); df.to_csv(F["contexts.csv"], index=False)
    prog.completed("contexts_selected", len(df))
    L.log(f"A1 select: {len(df)} contexts from {len(rows)} documents examined (skipped {sum(1 for r in rows if r['skip_reason'])})")
    return df


def phase_target(prog: R.Progress, ctx: pd.DataFrame, tgt) -> None:
    if ACTS.exists():
        return
    prog.set_phase("target")
    H = np.zeros((len(ctx), tgt.model.config.hidden_size), np.float32)
    norms = []
    for r in ctx.itertuples():
        ids = torch.tensor([json.loads(r.ids)])
        hs = tgt.hidden_states(ids)
        H[int(r.context_id)] = L.to_cpu_f32(hs[L.LAYER + 1][0, -1]).numpy(); norms.append(float(np.linalg.norm(H[int(r.context_id)])))
    ctx["act_norm"] = norms
    ctx.to_csv(F["contexts.csv"], index=False)
    np.savez(ACTS, H=H, context_id=ctx.context_id.values)
    prog.completed("activations", len(ctx))


def phase_av(prog: R.Progress, ctx: pd.DataFrame) -> dict:
    done = {int(r["context_id"]): r for r in R.read_jsonl(F["av.jsonl"]) if r.get("explanation") is not None}
    todo = [int(c) for c in ctx.context_id if int(c) not in done]
    if todo:
        prog.set_phase("av")
        H = np.load(ACTS)["H"]
        av = L.AV()
        for cid in todo:
            if prog.over_cap() or prog.over_failures():
                break
            try:
                r = {"context_id": cid, **R.verbalize_sampled(av, torch.from_numpy(H[cid]), seed=4000 + cid)}
            except Exception:
                r = {"context_id": cid, "seed": 4000 + cid, "error": traceback.format_exc(), "explanation": None, "parse_ok": False}
                prog.fail(f"av {cid}: {r['error'][-300:]}")
            R.append_jsonl(F["av.jsonl"], r)
            if r.get("explanation") is not None:
                done[cid] = r
            prog.completed("av", len(done))
        av.free()
    return done


def find_slots(cid: int, E: str) -> tuple[list[dict], list[dict]]:
    """Rule-located slots (<= 2) plus the other non-snippet sentences (for repeated-fact checks)."""
    claims = R.split_claims_quote_aware(E)
    sents = []
    for i, s in enumerate(claims):
        a, b, dup = R.sentence_span(E, s)
        sents.append({"claim_idx": i, "sentence": s, "span_a": a, "span_b": b, "dup_sentence": dup, "snippet": bool(R.SNIPPET_RE_A1.search(s)), "n_words": len(s.split())})
    remaining = [s for s in sents if not s["snippet"] and s["n_words"] >= MIN_WORDS_SLOT and s["span_a"] >= 0]
    slots = []
    ent = None
    for s in remaining:
        toks = [w for w in cap_noninitial(s["sentence"]) if w not in STOP and w not in MONTHS]
        if toks:
            ent = dict(s, slot_type="entity", focus_word=toks[0]); break
    det = None
    for s in remaining:
        if ent and s["claim_idx"] == ent["claim_idx"]:
            continue
        nums = [w for w in R._words(s["sentence"]) if w[0].isdigit() or w.lower() in R.NUM_WORD_SET]
        if nums:
            det = dict(s, slot_type="detail", focus_word=nums[0]); break
    if det is None:
        for s in remaining:
            if ent and s["claim_idx"] == ent["claim_idx"]:
                continue
            hit = [w for w in REL_WORDS if re.search(r"\b" + w + r"\b", s["sentence"], re.I)]
            if hit:
                det = dict(s, slot_type="detail", focus_word=hit[0]); break
    for k, s in enumerate([x for x in (ent, det) if x]):
        s = dict(s); s["context_id"] = cid; s["carrier_id"] = cid; s["n_claims"] = len(claims)
        s["slot_num"] = 2 * cid + (0 if s["slot_type"] == "entity" else 1); s["slot_id"] = f"c{cid}_{s['slot_type']}"
        s["repeat_sentences"] = [x["claim_idx"] for x in sents if x["claim_idx"] != s["claim_idx"] and not x["snippet"] and re.search(r"(?<![\w])" + re.escape(s["focus_word"]) + r"(?![\w])", x["sentence"])]
        slots.append(s)
    return slots, sents


def name_pool() -> list[str]:
    t2b = pd.read_csv(L.OVERNIGHT / "t2b_claims.csv", keep_default_na=False)
    det = t2b[(t2b.edit_type == "corrupt_det")]
    names = sorted({w.strip(".,;:!?\"'()") for w in det.word_orig if not re.match(r"^\d", w.strip(".,;:!?\"'()"))})
    return [n for n in names if n]


def run_agent_phases(prog: R.Progress, ctx: pd.DataFrame, av: dict, tok) -> tuple[list[dict], list[dict], list[dict]]:
    cm = {int(r.context_id): r for r in ctx.itertuples()}
    # ---------------- slots by rule
    slots, allsents = [], {}
    for cid in sorted(av):
        ss, sents = find_slots(cid, av[cid]["explanation"]); slots += ss; allsents[cid] = sents
    # ---------------- slot_verify (+ repeated-fact checks)
    prog.set_phase("slot_verify")
    tasks = []
    for s in slots:
        tasks.append({"task_id": f"a1_sv_{s['slot_id']}", "type": "slot_verify",
                      "inputs": {"sentence": s["sentence"], "focus_word": s["focus_word"], "target_fact": f"the sentence's claim about '{s['focus_word']}'", "allowed_values": ["yes", "no"],
                                 "instruction": R.TASK_INSTRUCTIONS["slot_verify"] + f" Here: does the sentence make a checkable claim involving the focus word '{s['focus_word']}'? Output asserts ∈ {{yes, no}} and other_content (≤ 15 words: what else the sentence asserts)."}})
        for j in s["repeat_sentences"]:
            other_s = allsents[s["context_id"]][j]["sentence"]
            tasks.append({"task_id": f"a1_svr_{s['slot_id']}_{j}", "type": "slot_verify",
                          "inputs": {"sentence": other_s, "focus_word": s["focus_word"], "target_fact": f"the same fact that this slot sentence asserts about '{s['focus_word']}': \"{s['sentence']}\"", "allowed_values": ["yes", "no"],
                                     "instruction": R.TASK_INSTRUCTIONS["slot_verify"] + " Here: does the sentence itself assert the same fact as the slot sentence (not merely mention the word)? Output asserts ∈ {yes, no} and other_content."}})
    sv = R.require_outputs(PFX, "slot_verify", tasks, prog)
    for s in slots:
        o = sv[f"a1_sv_{s['slot_id']}"]["output"]; s["asserts"] = o["asserts"]; s["other_content"] = o.get("other_content", "")
        s["fact_repeated_by"] = [j for j in s["repeat_sentences"] if sv[f"a1_svr_{s['slot_id']}_{j}"]["output"]["asserts"] == "yes"]
        s["label_source"] = "claude"; s["sv_task_id"] = f"a1_sv_{s['slot_id']}"
    # ---------------- label originals
    prog.set_phase("label_orig")
    tasks = [{"task_id": f"a1_lb_{s['slot_id']}", "type": "label", "inputs": {"passage": cm[s["context_id"]].text_full, "sentence": s["sentence"], "instruction": R.TASK_INSTRUCTIONS["label"]}} for s in slots]
    lb = R.require_outputs(PFX, "label_orig", tasks, prog)
    for s in slots:
        o = lb[f"a1_lb_{s['slot_id']}"]["output"]; s["label_orig"] = o["label"]; s["evidence"] = o.get("evidence", ""); s["reason"] = o.get("reason", "")
        s["evidence_found"] = bool(s["evidence"]) and s["evidence"] in cm[s["context_id"]].text_full
        s["eligible"] = s["asserts"] == "yes" and not s["dup_sentence"] and not s["fact_repeated_by"]
        s["ineligible_reason"] = "" if s["eligible"] else ("no_claim" if s["asserts"] != "yes" else ("dup_sentence" if s["dup_sentence"] else "fact_repeated"))
    # ---------------- corrections for contradicted originals
    prog.set_phase("correction")
    tasks = [{"task_id": f"a1_co_{s['slot_id']}", "type": "correction", "inputs": {"passage": cm[s["context_id"]].text_full, "sentence": s["sentence"], "instruction": R.TASK_INSTRUCTIONS["correction"] + " Output field text (or NONE if no single-fact correction exists)."}}
             for s in slots if s["eligible"] and s["label_orig"] == "contradicted"]
    co = R.require_outputs(PFX, "correction", tasks, prog)
    prog.set_phase("corrcheck")
    tasks = []
    for s in slots:
        tid = f"a1_co_{s['slot_id']}"
        if tid in co:
            txt = co[tid]["output"]["text"].strip(); s["correction_text"] = txt
            if txt.upper() != "NONE" and R.norm_text(txt) != R.norm_text(s["sentence"]):
                tasks.append({"task_id": f"a1_coec_{s['slot_id']}", "type": "edit_check", "inputs": {"original": s["sentence"], "edited": txt, "instruction": R.TASK_INSTRUCTIONS["edit_check"]}})
                tasks.append({"task_id": f"a1_colb_{s['slot_id']}", "type": "label", "inputs": {"passage": cm[s["context_id"]].text_full, "sentence": txt, "instruction": R.TASK_INSTRUCTIONS["label"]}})
    cc = R.require_outputs(PFX, "corrcheck", tasks, prog)
    # ---------------- candidates: correct meaning + false meanings
    pool = name_pool()
    cands = []
    for s in slots:
        if not s["eligible"]:
            continue
        cid = s["context_id"]; base = {"slot_id": s["slot_id"], "context_id": cid, "slot_type": s["slot_type"], "label_source": "claude"}
        if s["label_orig"] == "entailed":
            cands.append({**base, "meaning_id": f"{s['slot_id']}_correct_original", "category": "correct_original", "sentence": s["sentence"], "label": "entailed", "evidence": s["evidence"], "reason": s["reason"],
                          "edit_ok": True, "changed": "", "task_ids": [f"a1_lb_{s['slot_id']}"], "agent_raw": json.dumps(lb[f"a1_lb_{s['slot_id']}"]["output"], ensure_ascii=False), "role": "correct"})
        elif s["label_orig"] == "contradicted":
            cands.append({**base, "meaning_id": f"{s['slot_id']}_original_contradicted", "category": "original_contradicted", "sentence": s["sentence"], "label": "contradicted", "evidence": s["evidence"], "reason": s["reason"],
                          "edit_ok": True, "changed": "", "task_ids": [f"a1_lb_{s['slot_id']}"], "agent_raw": json.dumps(lb[f"a1_lb_{s['slot_id']}"]["output"], ensure_ascii=False), "role": "natural_error_original"})
            ec = cc.get(f"a1_coec_{s['slot_id']}"); lb2 = cc.get(f"a1_colb_{s['slot_id']}")
            ok = bool(ec and lb2 and ec["output"]["one_fact"] == "Yes" and lb2["output"]["label"] == "entailed")
            s["correction_valid"] = ok
            cands.append({**base, "meaning_id": f"{s['slot_id']}_correction", "category": "correction", "sentence": s.get("correction_text", ""), "label": lb2["output"]["label"] if lb2 else "",
                          "evidence": lb2["output"].get("evidence", "") if lb2 else "", "reason": lb2["output"].get("reason", "") if lb2 else "", "edit_ok": bool(ec and ec["output"]["one_fact"] == "Yes"),
                          "changed": ec["output"].get("changed", "") if ec else "", "task_ids": [f"a1_co_{s['slot_id']}", f"a1_coec_{s['slot_id']}", f"a1_colb_{s['slot_id']}"],
                          "agent_raw": json.dumps({"correction": co[f"a1_co_{s['slot_id']}"]["output"], "edit_check": ec["output"] if ec else None, "label": lb2["output"] if lb2 else None}, ensure_ascii=False),
                          "role": "correct" if ok else "invalid_correction"})
        else:  # undetermined original: no correct meaning; slot ineligible for the primary
            s["eligible"] = False; s["ineligible_reason"] = "original_undetermined"
            continue
        # entity_sub (deterministic pool swap, seed 7000 + slot_num)
        if s["slot_type"] == "entity":
            rng = np.random.default_rng(7000 + s["slot_num"]); E = av[cid]["explanation"]; ctxt = cm[cid].text_full
            excl = set(R._words(ctxt)) | set(R._words(E)) | {s["focus_word"]}
            avail = [n for n in pool if n not in excl]
            repl = avail[int(rng.integers(0, len(avail)))] if avail else None
            if repl:
                new = re.sub(r"(?<![\w])" + re.escape(s["focus_word"]) + r"(?![\w])", repl, s["sentence"], count=1)
                cands.append({**base, "meaning_id": f"{s['slot_id']}_entity_sub", "category": "entity_sub", "sentence": new, "label": "", "evidence": "", "reason": "", "edit_ok": None, "changed": f"{s['focus_word']} -> {repl}",
                              "task_ids": [], "agent_raw": "", "role": "false"})
    # agent corruption tasks: detail_sub, relation_rev (negation dropped by cut rule A1(b))
    prog.set_phase("corrupt")
    tasks = []
    for s in slots:
        if not s["eligible"]:
            continue
        tasks.append({"task_id": f"a1_ds_{s['slot_id']}", "type": "detail_sub", "inputs": {"sentence": s["sentence"], "instruction": R.TASK_INSTRUCTIONS["detail_sub"] + " Output field text (or NONE if the sentence has no such detail)."}})
        tasks.append({"task_id": f"a1_rr_{s['slot_id']}", "type": "relation_rev", "inputs": {"sentence": s["sentence"], "instruction": R.TASK_INSTRUCTIONS["relation_rev"] + " Output field text."}})
    cr = R.require_outputs(PFX, "corrupt", tasks, prog)
    for s in slots:
        if not s["eligible"]:
            continue
        for cat, key in [("detail_sub", "ds"), ("relation_rev", "rr")]:
            txt = cr[f"a1_{key}_{s['slot_id']}"]["output"]["text"].strip()
            none = txt.upper() == "NONE" or R.norm_text(txt) == R.norm_text(s["sentence"])
            cands.append({"slot_id": s["slot_id"], "context_id": s["context_id"], "slot_type": s["slot_type"], "label_source": "claude", "meaning_id": f"{s['slot_id']}_{cat}", "category": cat, "sentence": txt,
                          "label": "", "evidence": "", "reason": "", "edit_ok": None if not none else False, "changed": "", "task_ids": [f"a1_{key}_{s['slot_id']}"],
                          "agent_raw": json.dumps(cr[f"a1_{key}_{s['slot_id']}"]["output"], ensure_ascii=False), "role": "false" if not none else "dropped_NONE"})
    # duplicates among candidates of a slot
    for s in slots:
        seen = {}
        for m in [m for m in cands if m["slot_id"] == s["slot_id"]]:
            nt = R.norm_text(m["sentence"]); m["duplicate_of"] = seen.get(nt, ""); seen.setdefault(nt, m["meaning_id"])
    # edit_check for false candidates (and label)
    prog.set_phase("candcheck")
    tasks = []
    sm = {s["slot_id"]: s for s in slots}
    for m in cands:
        if m["role"] == "false" and not m["duplicate_of"]:
            tasks.append({"task_id": f"a1_ec_{m['meaning_id']}", "type": "edit_check", "inputs": {"original": sm[m["slot_id"]]["sentence"], "edited": m["sentence"], "instruction": R.TASK_INSTRUCTIONS["edit_check"]}})
    ec = R.require_outputs(PFX, "candcheck", tasks, prog)
    for m in cands:
        o = ec.get(f"a1_ec_{m['meaning_id']}")
        if o:
            m["edit_ok"] = o["output"]["one_fact"] == "Yes"; m["changed"] = o["output"].get("changed", ""); m["task_ids"].append(f"a1_ec_{m['meaning_id']}")
            m["agent_raw"] = json.dumps({"edit": json.loads(m["agent_raw"]) if m["agent_raw"] else None, "edit_check": o["output"]}, ensure_ascii=False)
    prog.set_phase("label_cand")
    tasks = [{"task_id": f"a1_lc_{m['meaning_id']}", "type": "label", "inputs": {"passage": cm[m["context_id"]].text_full, "sentence": m["sentence"], "instruction": R.TASK_INSTRUCTIONS["label"]}}
             for m in cands if m["role"] == "false" and not m["duplicate_of"] and m["edit_ok"]]
    lc = R.require_outputs(PFX, "label_cand", tasks, prog)
    for m in cands:
        o = lc.get(f"a1_lc_{m['meaning_id']}")
        if o:
            m["label"] = o["output"]["label"]; m["evidence"] = o["output"].get("evidence", ""); m["reason"] = o["output"].get("reason", ""); m["task_ids"].append(f"a1_lc_{m['meaning_id']}")
            m["role"] = "false" if m["label"] == "contradicted" else "false_descriptive"
        elif m["role"] == "false":
            m["role"] = "false_edit_rejected" if m["edit_ok"] is False else ("false_duplicate" if m["duplicate_of"] else m["role"])
    F["candidates.jsonl"].unlink(missing_ok=True)
    for m in cands:
        R.append_jsonl(F["candidates.jsonl"], m)
    pd.DataFrame(slots).to_csv(F["slots.csv"], index=False)
    prog.completed("slots", len(slots)); prog.completed("eligible_slots", sum(s["eligible"] for s in slots)); prog.completed("candidates", len(cands))
    # ---------------- rewrite for every meaning in play (correct + false + false_descriptive), then equiv
    prog.set_phase("rewrite")
    inplay = [m for m in cands if m["role"] in ("correct", "false", "false_descriptive", "natural_error_original")]
    tasks = [{"task_id": f"a1_rw_{m['meaning_id']}", "type": "rewrite", "inputs": {"candidate": m["sentence"], "fields": TRANSFORMS, "instruction": R.TASK_INSTRUCTIONS["rewrite"] + " Under cut rule A1(a) output only light1 and aggr1."}} for m in inplay]
    rw = R.require_outputs(PFX, "rewrite", tasks, prog)
    reals = []
    for m in inplay:
        o = rw[f"a1_rw_{m['meaning_id']}"]["output"]
        reals.append({"realization_id": f"{m['meaning_id']}_orig", "meaning_id": m["meaning_id"], "slot_id": m["slot_id"], "context_id": m["context_id"], "transform": "orig", "text": m["sentence"], "task_id": "", "dup_realization": False, "dup_detected": False})
        seen = set()
        for tr in TRANSFORMS:
            txt = o[tr].strip(); nt = R.norm_text(txt); dup = nt in seen or nt == R.norm_text(m["sentence"]); seen.add(nt)
            reals.append({"realization_id": f"{m['meaning_id']}_{tr}", "meaning_id": m["meaning_id"], "slot_id": m["slot_id"], "context_id": m["context_id"], "transform": tr, "text": txt,
                          "task_id": f"a1_rw_{m['meaning_id']}", "dup_realization": bool(o.get("dup_realization", False)), "dup_detected": dup})
    for s in slots:
        if s["eligible"]:
            reals.append({"realization_id": f"{s['slot_id']}_deletion", "meaning_id": f"{s['slot_id']}_deletion", "slot_id": s["slot_id"], "context_id": s["context_id"], "transform": "deletion", "text": "", "task_id": "", "dup_realization": False, "dup_detected": False})
    mm = {m["meaning_id"]: m for m in cands}
    for r in reals:
        if r["transform"] in TRANSFORMS:
            r.update(R.lexical_checks(mm[r["meaning_id"]]["sentence"], r["text"], tok))
        else:
            r.update({"names_kept": True, "numbers_kept": True, "polarity_kept": True, "len_ratio": 1.0 if r["transform"] == "orig" else 0.0, "len_ok": r["transform"] == "orig"})
    prog.set_phase("equiv")
    eq_tasks = [{"task_id": f"a1_eq_{r['realization_id']}", "type": "equiv", "inputs": {"candidate": mm[r["meaning_id"]]["sentence"], "realization": r["text"], "instruction": R.TASK_INSTRUCTIONS["equiv"]}}
                for r in reals if r["transform"] in TRANSFORMS]
    order = np.random.default_rng(9000).permutation(len(eq_tasks)); eq_tasks = [eq_tasks[i] for i in order]
    eq = R.require_outputs(PFX, "equiv", eq_tasks, prog)
    F["realizations.jsonl"].unlink(missing_ok=True)
    for r in reals:
        if r["transform"] in TRANSFORMS:
            o = eq[f"a1_eq_{r['realization_id']}"]["output"]; r["equiv"] = o["answer"]; r["equiv_reason"] = o.get("reason", ""); r["valid"] = o["answer"] == "Yes"; r["equiv_task_id"] = f"a1_eq_{r['realization_id']}"
        else:
            r["equiv"] = ""; r["equiv_reason"] = ""; r["valid"] = True; r["equiv_task_id"] = ""
        R.append_jsonl(F["realizations.jsonl"], r)
    prog.completed("realizations", len(reals))
    return slots, cands, reals


def phase_ar(prog: R.Progress, ctx: pd.DataFrame, av: dict, slots: list[dict], reals: list[dict]) -> None:
    prog.set_phase("ar")
    H = np.load(ACTS)["H"]; sm = {s["slot_id"]: s for s in slots}
    done = set(pd.read_csv(F["scores.csv"], keep_default_na=False).text_id) if F["scores.csv"].exists() else set()
    texts_done = {t["text_id"] for t in R.read_jsonl(F["texts.jsonl"])}
    preds = {}
    if PREDS.exists():
        z = np.load(PREDS, allow_pickle=True); preds = {str(k): z[k] for k in z.files}
    ar = L.AR()
    units = [{"text_id": f"c{cid}_carrier", "realization_id": "", "carrier_id": cid, "full_text": av[cid]["explanation"], "orig_ref": ""} for cid in sorted(av)]
    for r in reals:
        s = sm[r["slot_id"]]; E = av[r["context_id"]]["explanation"]
        full = R.deletion_text(E, s["span_a"], s["span_b"]) if r["transform"] == "deletion" else R.substitute(E, s["span_a"], s["span_b"], r["text"])
        units.append({"text_id": r["realization_id"], "realization_id": r["realization_id"], "carrier_id": r["context_id"], "full_text": full, "orig_ref": f"{r['meaning_id']}_orig" if r["transform"] in TRANSFORMS else ""})
    if not F["scores.csv"].exists():
        pd.DataFrame(columns=["text_id", "activation_id", "cos", "mse", "pred_norm", "V_vs_orig_wording", "carrier_id"]).to_csv(F["scores.csv"], index=False)
    t0 = time.time(); n0 = ar.n_forward
    for k, u in enumerate(units):
        if u["text_id"] in done:
            continue
        if prog.over_cap() or prog.over_failures():
            prog.incomplete("ar_texts", [x["text_id"] for x in units if x["text_id"] not in done]); break
        try:
            if u["text_id"] not in texts_done:
                nt = R.ar_input_tokens(ar, u["full_text"]); assert nt < MAX_AR_TOKENS, nt
                R.append_jsonl(F["texts.jsonl"], {"text_id": u["text_id"], "realization_id": u["realization_id"], "carrier_id": u["carrier_id"], "full_text": u["full_text"], "ar_input_tokens": nt, "ar_input_truncated": False})
            if u["text_id"] in preds:
                pred = preds[u["text_id"]]
            elif u["realization_id"].endswith("_orig") and R.norm_text(u["full_text"]) == R.norm_text(av[u["carrier_id"]]["explanation"]) and f"c{u['carrier_id']}_carrier" in preds:
                pred = preds[f"c{u['carrier_id']}_carrier"]
            else:
                pred = ar.predict(u["full_text"]).numpy()
            preds[u["text_id"]] = pred
            ref = preds.get(u["orig_ref"]) if u["orig_ref"] else None
            cs = L.cos(pred, H[u["carrier_id"]])
            pd.DataFrame([{"text_id": u["text_id"], "activation_id": u["carrier_id"], "cos": cs, "mse": L.mse_from_cos(cs), "pred_norm": float(np.linalg.norm(pred)),
                           "V_vs_orig_wording": R.movement(pred, ref) if ref is not None else float("nan"), "carrier_id": u["carrier_id"]}]).to_csv(F["scores.csv"], mode="a", header=False, index=False)
            done.add(u["text_id"])
        except Exception:
            prog.fail(f"ar {u['text_id']}: {traceback.format_exc()[-300:]}")
        if k % 50 == 49:
            np.savez(PREDS, **preds); prog.completed("ar_texts", len(done)); L.log(f"A1 ar: {len(done)}/{len(units)} ({(time.time()-t0)/max(1, ar.n_forward-n0):.2f} s/forward)")
    np.savez(PREDS, **preds); prog.completed("ar_texts", len(done)); ar.free()
    L.log(f"A1 ar done: {len(done)}/{len(units)} texts")


def main():
    prog = R.Progress(STAGE)
    S = L.Settings(PFX, n_ctx=N_CTX, n_dev=N_DEV, transforms=TRANSFORMS, negation=NEGATION, cut_rules_applied=["A1(a) paraphrases light1+aggr1", "A1(b) no negation", "A1(c) contexts 60->40"],
                   selection="wikitext-2 train, doc_idx not in stimuli.csv, >=256 TARGET tokens, rng default_rng(4) permutation, sentence rule largest t in [127,255] with '.', '!' or '?' followed by space/newline/capital; skip < 3 capitalised non-initial tokens",
                   decoding="sampled T=1.0 top_p=1 top_k=0, seed 4000 + context_id", slot_rule="entity: first non-snippet sentence (>=6 words) with a capitalised non-initial token not in the stoplist / months / weekdays; detail: first other sentence with a digit or number word, else with a relation word",
                   stoplist=sorted(STOP), relation_words=REL_WORDS, entity_sub="deterministic swap from the t2b corrupt_det name pool excluding words in the context and explanation, rng 7000 + slot_num (2*context_id + {0 entity, 1 detail})",
                   task_instructions=R.TASK_INSTRUCTIONS, agent_model=R.AGENT_MODEL, equiv_shuffle_seed=9000, bootstrap="cluster by context, 1000 draws, seed 0")
    hits = R.assert_no_av_model_calls([L.OVERNIGHT / "a1_natural.py", L.OVERNIGHT / "r4_lib.py"]); assert not hits, hits
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(L.snapshot(L.TARGET))
    ctx = phase_select(prog, tok)
    if not ACTS.exists():
        tgt = L.Target(); phase_target(prog, ctx, tgt); tgt.free()
    ctx = pd.read_csv(F["contexts.csv"], keep_default_na=False)
    av = phase_av(prog, ctx)
    if prog.over_cap() or prog.over_failures():
        prog.block("cap or failures reached during AV")
    else:
        slots, cands, reals = run_agent_phases(prog, ctx, av, tok)
        phase_ar(prog, ctx, av, slots, reals)
        if prog.over_cap() or prog.over_failures():
            prog.block("cap or failures reached during AR")
    prog.set_phase("analyze")
    from overnight import a1_analyze
    a1_analyze.run(labels=None)
    prog.set_phase("done"); S.finish(progress=prog.d)
    L.log(f"A1 done: {prog.minutes:.1f} min cumulative (cap {prog.cap})")


if __name__ == "__main__":
    main()

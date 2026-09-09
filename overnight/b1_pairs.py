"""B1 — controlled paired contexts: does the reconstructor's preference between meanings A and B reverse with the source fact?
(PLAN.md round 4, human-designed; PRIMARY CONTROLLED RESULT.)

  uv run python overnight/b1_pairs.py            # re-entrant; exits 0 with AWAITING_AGENT_TASKS / MISSING between phases

Phases: target (activations, out/b1_acts.npz) → av (sampled, b1_av.jsonl; never regenerated) → slots (keyword candidates →
agent slot_verify) → swap (agent fact_swap) → swapcheck (agent edit_check + slot_verify on the swapped sentence) → rewrite
(agent) → equiv (agent, shuffled seed 9000) → ar (11 texts per eligible carrier, cos vs h_A and h_B) → analysis (b1_analyze.py).
Cut rule B1(a) from V0: fillings f0–f3 (32 pairs, 64 contexts). Every unit is checkpointed to its file as it completes.
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

STAGE, PFX = "B1", "b1"
FILLINGS = [0, 1, 2, 3]  # V0 cut rule B1(a): drop f4
N_PAR = 4                # B1(b) not applied
TRANSFORMS = ["light1", "light2", "aggr1", "aggr2"]
ACTS = L.OUT / "b1_acts.npz"
PREDS = L.OUT / "b1_preds.npz"
F = {k: L.OVERNIGHT / f"{PFX}_{k}" for k in ["contexts.csv", "av.jsonl", "slots.csv", "candidates.jsonl", "realizations.jsonl", "texts.jsonl", "scores.csv"]}
MAX_AR_TOKENS = 1024


def contexts_list() -> list[dict]:
    rows = []
    for p in R.b1_pairs():
        if p["filling"] not in FILLINGS:
            continue
        for v in "AB":
            rows.append({"context_id": f"{p['pair_id']}{v}", "pair_id": p["pair_id"], "pair_index": p["pair_index"], "version": v,
                         "split": p["split"], "family": p["family"], "template": p["template"], "filling": p["filling"],
                         "slot_type": p["slot_type"], "name_overlap": p["name_overlap"], "meaning_A": p["meaning_A"], "meaning_B": p["meaning_B"],
                         "fact_sentence": p["fact_A"] if v == "A" else p["fact_B"], "keywords": p["keywords"],
                         "text_full": R.b1_context(p, v, False), "source": "synthetic B1 template (PLAN.md round 4)"})
    return rows


def phase_target(prog: R.Progress, ctxs: list[dict]) -> None:
    if ACTS.exists() and F["contexts.csv"].exists():
        return
    prog.set_phase("target")
    tgt = L.Target(); tok = tgt.tok
    pair_ids = sorted({c["pair_id"] for c in ctxs}, key=lambda s: [c["pair_index"] for c in ctxs if c["pair_id"] == s][0])
    H = np.zeros((len(pair_ids), 2, tgt.model.config.hidden_size), np.float32)
    rows = []
    for c in ctxs:
        ids = tok(c["text_full"], return_tensors="pt", add_special_tokens=False)["input_ids"]
        t = int(ids.shape[1]) - 1
        assert tok.decode([int(ids[0, t])]) == ".", (c["context_id"], tok.decode([int(ids[0, t])]))
        hs = tgt.hidden_states(ids)
        h = L.to_cpu_f32(hs[L.LAYER + 1][0, t]).numpy()
        H[pair_ids.index(c["pair_id"]), 0 if c["version"] == "A" else 1] = h
        rows.append({"context_id": c["context_id"], "split": c["split"], "source": c["source"], "text_full": c["text_full"], "n_tokens": t + 1, "t": t,
                     "token_id": int(ids[0, t]), "token_str": tok.decode([int(ids[0, t])]), "act_norm": float(np.linalg.norm(h)),
                     "layer_index": 20, "hidden_states_index": 21, "weights": "TARGET", "pair_id": c["pair_id"], "pair_index": c["pair_index"],
                     "version": c["version"], "family": c["family"], "template": c["template"], "filling": c["filling"], "slot_type": c["slot_type"],
                     "name_overlap": c["name_overlap"], "meaning_A": c["meaning_A"], "meaning_B": c["meaning_B"], "fact_sentence": c["fact_sentence"]})
    tgt.free()
    df = pd.DataFrame(rows)
    by = df.set_index("context_id")
    for pid in pair_ids:
        a, b = by.loc[pid + "A"], by.loc[pid + "B"]
        assert int(a.token_id) == int(b.token_id), (pid, a.token_id, b.token_id)
        df.loc[df.pair_id == pid, "len_mismatch"] = bool(a.n_tokens != b.n_tokens)
        df.loc[df.pair_id == pid, "cos_hA_hB"] = L.cos(H[pair_ids.index(pid), 0], H[pair_ids.index(pid), 1])
    np.savez(ACTS, H=H, pair_ids=np.array(pair_ids))
    df.to_csv(F["contexts.csv"], index=False)
    prog.completed("contexts", len(df))
    L.log(f"B1 target: {len(df)} contexts; min t {df.t.min()}; len_mismatch pairs {int(df.drop_duplicates('pair_id').len_mismatch.sum())}")


def load_acts():
    z = np.load(ACTS); pair_ids = list(z["pair_ids"]); H = z["H"]
    return {pid: (H[i, 0], H[i, 1]) for i, pid in enumerate(pair_ids)}


def phase_av(prog: R.Progress, ctxs: list[dict]) -> dict:
    done = {r["context_id"]: r for r in R.read_jsonl(F["av.jsonl"]) if r.get("explanation") is not None}
    todo = [c for c in ctxs if c["context_id"] not in done]
    if todo:
        prog.set_phase("av")
        acts = load_acts()
        av = L.AV()
        for c in todo:
            if prog.over_cap() or prog.over_failures():
                break
            h = acts[c["pair_id"]][0 if c["version"] == "A" else 1]
            seed = 5000 + 2 * c["pair_index"] + (0 if c["version"] == "A" else 1)
            try:
                r = R.verbalize_sampled(av, torch.from_numpy(h), seed=seed)
                r = {"context_id": c["context_id"], **r}
            except Exception:
                r = {"context_id": c["context_id"], "seed": seed, "error": traceback.format_exc(), "explanation": None, "parse_ok": False}
                prog.fail(f"av {c['context_id']}: {r['error'][-300:]}")
            R.append_jsonl(F["av.jsonl"], r)
            if r.get("explanation") is not None:
                done[c["context_id"]] = r
            prog.completed("av", len(done))
        av.free()
        L.log(f"B1 av: {len(done)}/{len(ctxs)} generations")
    return done


def candidate_slots(c: dict, E: str) -> list[dict]:
    claims = R.split_claims_quote_aware(E)
    out = []
    for i, s in enumerate(claims):
        snippet = bool(R.SNIPPET_RE_B1.search(s))
        hits = R.keyword_hit(s, c["keywords"])
        a, b, dup = R.sentence_span(E, s)
        out.append({"slot_id": f"{c['context_id']}_s{i}", "context_id": c["context_id"], "carrier_id": c["context_id"], "claim_idx": i, "n_claims": len(claims),
                    "sentence": s, "span_a": a, "span_b": b, "focus_word": "|".join(hits), "slot_type": c["slot_type"], "snippet": snippet,
                    "keyword_hit": bool(hits), "dup_sentence": dup, "candidate": bool(hits) and not snippet and a >= 0})
    return out


def phase_slots(prog: R.Progress, ctxs: list[dict], av: dict) -> tuple[list[dict], dict]:
    prog.set_phase("slots")
    slots = []
    for c in ctxs:
        if c["context_id"] in av:
            slots += candidate_slots(c, av[c["context_id"]]["explanation"])
    tasks = []
    cm = {c["context_id"]: c for c in ctxs}
    for s in slots:
        if s["candidate"]:
            c = cm[s["context_id"]]
            tasks.append({"task_id": f"b1_sv_{s['slot_id']}", "type": "slot_verify",
                          "inputs": {"sentence": s["sentence"], "meaning_A": c["meaning_A"], "meaning_B": c["meaning_B"], "allowed_values": ["A", "B", "neither"],
                                     "instruction": R.TASK_INSTRUCTIONS["slot_verify"] + " Output asserts ∈ {A, B, neither} and other_content (≤ 15 words: what else the sentence asserts)."}})
    outs = R.require_outputs(PFX, "slot_verify", tasks, prog)
    for s in slots:
        o = outs.get(f"b1_sv_{s['slot_id']}")
        s["task_id"] = f"b1_sv_{s['slot_id']}" if s["candidate"] else ""
        s["asserts"] = o["output"]["asserts"] if o else ""
        s["other_content"] = o["output"].get("other_content", "") if o else ""
        s["agent_raw"] = json.dumps(o["output"], ensure_ascii=False) if o else ""
        c = cm[s["context_id"]]
        if s["asserts"] in ("A", "B"):
            s["label_orig"] = "entailed" if s["asserts"] == c["version"] else "contradicted"
            s["evidence"] = c["fact_sentence"]; s["evidence_found"] = c["fact_sentence"] in c["text_full"]
        else:
            s["label_orig"] = "undetermined" if s["candidate"] else ""; s["evidence"] = ""; s["evidence_found"] = False
        s["label_source"] = "claude" if s["candidate"] else ""
        s["reason"] = s["other_content"]
    # carrier eligibility: exactly one asserting sentence, not duplicated
    carriers = {}
    for cid in av:
        ss = [s for s in slots if s["context_id"] == cid]
        asserting = [s for s in ss if s["asserts"] in ("A", "B")]
        c = cm[cid]
        info = {"context_id": cid, "n_candidate_slots": sum(s["candidate"] for s in ss), "n_asserting": len(asserting), "av_asserts": "", "eligible": False, "ineligible_reason": ""}
        if len(asserting) == 0:
            info["ineligible_reason"] = "omission"
        elif len(asserting) > 1:
            info["ineligible_reason"] = "redundant"; info["av_asserts"] = "|".join(s["asserts"] for s in asserting)
        elif asserting[0]["dup_sentence"]:
            info["ineligible_reason"] = "dup_sentence"; info["av_asserts"] = asserting[0]["asserts"]
        else:
            info.update({"eligible": True, "av_asserts": asserting[0]["asserts"], "slot_id": asserting[0]["slot_id"]})
        info["av_asserts_mismatch"] = bool(info["av_asserts"] and info["av_asserts"] != c["version"])
        carriers[cid] = info
    for s in slots:
        info = carriers[s["context_id"]]
        s["eligible"] = bool(info["eligible"] and info.get("slot_id") == s["slot_id"])
        s["ineligible_reason"] = "" if s["eligible"] else (info["ineligible_reason"] if s["asserts"] in ("A", "B") else ("not_asserting" if s["candidate"] else ("snippet" if s["snippet"] else "no_keyword")))
    pd.DataFrame(slots).to_csv(F["slots.csv"], index=False)
    prog.completed("eligible_carriers", sum(i["eligible"] for i in carriers.values()))
    prog.completed("omission", sum(i["ineligible_reason"] == "omission" for i in carriers.values()))
    prog.completed("redundant", sum(i["ineligible_reason"] == "redundant" for i in carriers.values()))
    L.log(f"B1 slots: {len(slots)} sentences, {sum(s['candidate'] for s in slots)} candidates; eligible carriers {sum(i['eligible'] for i in carriers.values())}/{len(carriers)}")
    return slots, carriers


def other(m: str) -> str:
    return "B" if m == "A" else "A"


def phase_swap(prog: R.Progress, ctxs: list[dict], slots: list[dict], carriers: dict) -> dict:
    """fact_swap, then edit_check + slot_verify on the swapped sentence. Returns {context_id: candidate dicts}."""
    cm = {c["context_id"]: c for c in ctxs}; sm = {s["slot_id"]: s for s in slots}
    elig = [carriers[cid] for cid in carriers if carriers[cid]["eligible"]]
    prog.set_phase("swap")
    tasks = []
    for info in elig:
        c = cm[info["context_id"]]; s = sm[info["slot_id"]]
        tasks.append({"task_id": f"b1_fs_{info['context_id']}", "type": "fact_swap",
                      "inputs": {"sentence": s["sentence"], "meaning_A": c["meaning_A"], "meaning_B": c["meaning_B"], "currently_asserts": info["av_asserts"],
                                 "target_meaning": other(info["av_asserts"]), "instruction": R.TASK_INSTRUCTIONS["fact_swap"] + " Output field text (or NONE if impossible)."}})
    fs = R.require_outputs(PFX, "fact_swap", tasks, prog)
    prog.set_phase("swapcheck")
    tasks2 = []
    for info in elig:
        c = cm[info["context_id"]]; s = sm[info["slot_id"]]
        sw = fs[f"b1_fs_{info['context_id']}"]["output"]["text"].strip()
        info["swapped_sentence"] = sw; info["swap_none"] = sw.upper() == "NONE" or R.norm_text(sw) == R.norm_text(s["sentence"])
        if info["swap_none"]:
            continue
        tasks2.append({"task_id": f"b1_ec_{info['context_id']}", "type": "edit_check",
                       "inputs": {"original": s["sentence"], "edited": sw, "instruction": R.TASK_INSTRUCTIONS["edit_check"]}})
        tasks2.append({"task_id": f"b1_sv2_{info['context_id']}", "type": "slot_verify",
                       "inputs": {"sentence": sw, "meaning_A": c["meaning_A"], "meaning_B": c["meaning_B"], "allowed_values": ["A", "B", "neither"],
                                  "instruction": R.TASK_INSTRUCTIONS["slot_verify"] + " Output asserts ∈ {A, B, neither} and other_content (≤ 15 words: what else the sentence asserts)."}})
    ck = R.require_outputs(PFX, "swapcheck", tasks2, prog)
    cands = {}
    F["candidates.jsonl"].unlink(missing_ok=True)
    for info in elig:
        cid = info["context_id"]; c = cm[cid]; s = sm[info["slot_id"]]
        m1 = info["av_asserts"]; m2 = other(m1)
        same = {"meaning_id": f"{cid}_m_same", "slot_id": s["slot_id"], "category": "correct_original", "asserts_meaning": m1, "sentence": s["sentence"],
                "label": "entailed" if m1 == c["version"] else "contradicted", "label_source": "claude", "evidence": c["fact_sentence"], "reason": s["other_content"],
                "edit_ok": True, "changed": "", "task_ids": [s["task_id"]], "agent_raw": s["agent_raw"]}
        if info["swap_none"]:
            info["swap_valid"] = False; info["swap_reason"] = "fact_swap NONE or unchanged"
            swp = {"meaning_id": f"{cid}_m_swapped", "slot_id": s["slot_id"], "category": "fact_swap", "asserts_meaning": m2, "sentence": info["swapped_sentence"],
                   "label": "", "label_source": "claude", "evidence": "", "reason": "", "edit_ok": False, "changed": "", "task_ids": [f"b1_fs_{cid}"],
                   "agent_raw": json.dumps(fs[f"b1_fs_{cid}"]["output"], ensure_ascii=False)}
        else:
            ec = ck[f"b1_ec_{cid}"]["output"]; sv = ck[f"b1_sv2_{cid}"]["output"]
            ok = ec["one_fact"] == "Yes" and sv["asserts"] == m2
            info["swap_valid"] = ok; info["swap_reason"] = "" if ok else f"edit_check={ec['one_fact']}, swapped asserts={sv['asserts']} (need {m2})"
            swp = {"meaning_id": f"{cid}_m_swapped", "slot_id": s["slot_id"], "category": "fact_swap", "asserts_meaning": m2, "sentence": info["swapped_sentence"],
                   "label": "entailed" if m2 == c["version"] else "contradicted", "label_source": "claude", "evidence": c["fact_sentence"], "reason": sv.get("other_content", ""),
                   "edit_ok": bool(ec["one_fact"] == "Yes"), "swapped_asserts": sv["asserts"], "changed": ec.get("changed", ""),
                   "task_ids": [f"b1_fs_{cid}", f"b1_ec_{cid}", f"b1_sv2_{cid}"],
                   "agent_raw": json.dumps({"fact_swap": fs[f"b1_fs_{cid}"]["output"], "edit_check": ec, "slot_verify": sv}, ensure_ascii=False)}
        dele = {"meaning_id": f"{cid}_m_deletion", "slot_id": s["slot_id"], "category": "deletion", "asserts_meaning": "", "sentence": "", "label": "", "label_source": "",
                "evidence": "", "reason": "", "edit_ok": True, "changed": "", "task_ids": [], "agent_raw": ""}
        for m in (same, swp, dele):
            m["context_id"] = cid; m["swap_valid"] = info["swap_valid"]
            R.append_jsonl(F["candidates.jsonl"], m)
        cands[cid] = {"same": same, "swapped": swp, "deletion": dele}
    prog.completed("swap_valid", sum(i.get("swap_valid", False) for i in elig))
    L.log(f"B1 swap: valid swaps {sum(i.get('swap_valid', False) for i in elig)}/{len(elig)}")
    return cands


def phase_rewrite_equiv(prog: R.Progress, cands: dict, carriers: dict, tok) -> list[dict]:
    prog.set_phase("rewrite")
    tasks = []
    for cid, cd in cands.items():
        if not carriers[cid]["swap_valid"]:
            continue
        for key in ("same", "swapped"):
            tasks.append({"task_id": f"b1_rw_{cid}_{key}", "type": "rewrite", "inputs": {"candidate": cd[key]["sentence"], "instruction": R.TASK_INSTRUCTIONS["rewrite"]}})
    rw = R.require_outputs(PFX, "rewrite", tasks, prog)
    reals = []
    for cid, cd in cands.items():
        if not carriers[cid]["swap_valid"]:
            continue
        for key in ("same", "swapped"):
            m = cd[key]; o = rw[f"b1_rw_{cid}_{key}"]["output"]
            reals.append({"realization_id": f"{m['meaning_id']}_orig", "meaning_id": m["meaning_id"], "context_id": cid, "transform": "orig", "text": m["sentence"], "task_id": "",
                          "dup_realization": False, "dup_detected": False})
            seen = {}
            for tr in TRANSFORMS:
                txt = o[tr].strip(); nt = R.norm_text(txt)
                dup_det = nt in seen or nt == R.norm_text(m["sentence"])
                seen.setdefault(nt, tr)
                reals.append({"realization_id": f"{m['meaning_id']}_{tr}", "meaning_id": m["meaning_id"], "context_id": cid, "transform": tr, "text": txt,
                              "task_id": f"b1_rw_{cid}_{key}", "dup_realization": bool(o.get("dup_realization", False)), "dup_detected": dup_det})
        d = cd["deletion"]
        reals.append({"realization_id": f"{d['meaning_id']}_deletion", "meaning_id": d["meaning_id"], "context_id": cid, "transform": "deletion", "text": "", "task_id": "",
                      "dup_realization": False, "dup_detected": False})
    # lexical checks (advisory)
    mm = {m["meaning_id"]: m for cd in cands.values() for m in cd.values()}
    for r in reals:
        if r["transform"] in TRANSFORMS:
            r.update(R.lexical_checks(mm[r["meaning_id"]]["sentence"], r["text"], tok))
        else:
            r.update({"names_kept": True, "numbers_kept": True, "polarity_kept": True, "len_ratio": 1.0 if r["transform"] == "orig" else 0.0, "len_ok": r["transform"] == "orig"})
    # equiv: separate shuffled batch, seed 9000
    prog.set_phase("equiv")
    eq_tasks = []
    for r in reals:
        if r["transform"] in TRANSFORMS:
            eq_tasks.append({"task_id": f"b1_eq_{r['realization_id']}", "type": "equiv",
                             "inputs": {"candidate": mm[r["meaning_id"]]["sentence"], "realization": r["text"], "instruction": R.TASK_INSTRUCTIONS["equiv"]}})
    order = np.random.default_rng(9000).permutation(len(eq_tasks))
    eq_tasks = [eq_tasks[i] for i in order]
    eq = R.require_outputs(PFX, "equiv", eq_tasks, prog)
    F["realizations.jsonl"].unlink(missing_ok=True)
    for r in reals:
        if r["transform"] in TRANSFORMS:
            o = eq[f"b1_eq_{r['realization_id']}"]["output"]
            r["equiv"] = o["answer"]; r["equiv_reason"] = o.get("reason", ""); r["valid"] = o["answer"] == "Yes"; r["equiv_task_id"] = f"b1_eq_{r['realization_id']}"
        else:
            r["equiv"] = ""; r["equiv_reason"] = ""; r["valid"] = True; r["equiv_task_id"] = ""
        R.append_jsonl(F["realizations.jsonl"], r)
    prog.completed("realizations", len(reals))
    L.log(f"B1 realizations: {len(reals)}; valid paraphrases {sum(r['valid'] for r in reals if r['transform'] in TRANSFORMS)}/{sum(r['transform'] in TRANSFORMS for r in reals)}")
    return reals


def phase_ar(prog: R.Progress, ctxs: list[dict], av: dict, slots: list[dict], reals: list[dict], carriers: dict) -> None:
    prog.set_phase("ar")
    acts = load_acts(); cm = {c["context_id"]: c for c in ctxs}; sm = {s["slot_id"]: s for s in slots}
    done_scores = set()
    if F["scores.csv"].exists():
        done_scores = set(pd.read_csv(F["scores.csv"], keep_default_na=False).text_id)
    texts_done = {t["text_id"]: t for t in R.read_jsonl(F["texts.jsonl"])}
    preds = {}
    if PREDS.exists():
        z = np.load(PREDS, allow_pickle=True); preds = {str(k): z[k] for k in z.files}
    ar = L.AR()
    # texts: carriers of every context (unedited) + 11 per valid carrier
    units = []
    for c in ctxs:
        if c["context_id"] in av:
            units.append({"text_id": f"{c['context_id']}_carrier", "realization_id": "", "carrier_id": c["context_id"], "full_text": av[c["context_id"]]["explanation"], "orig_ref": ""})
    slot_of = {carriers[cid]["slot_id"]: cid for cid in carriers if carriers[cid]["eligible"]}
    for r in reals:
        cid = r["context_id"]; s = sm[carriers[cid]["slot_id"]]; E = av[cid]["explanation"]
        if r["transform"] == "deletion":
            full = R.deletion_text(E, s["span_a"], s["span_b"])
        else:
            full = R.substitute(E, s["span_a"], s["span_b"], r["text"])
        units.append({"text_id": r["realization_id"], "realization_id": r["realization_id"], "carrier_id": cid, "full_text": full,
                      "orig_ref": f"{r['meaning_id']}_orig" if r["transform"] in TRANSFORMS else ""})
    n_fwd0 = ar.n_forward; t0 = time.time()
    if not F["scores.csv"].exists():
        pd.DataFrame(columns=["text_id", "activation_id", "cos", "mse", "pred_norm", "V_vs_orig_wording", "carrier_id", "pair_id", "truth_of_activation"]).to_csv(F["scores.csv"], index=False)
    for k, u in enumerate(units):
        if u["text_id"] in done_scores:
            continue
        if prog.over_cap() or prog.over_failures():
            prog.incomplete("ar_texts", [x["text_id"] for x in units if x["text_id"] not in done_scores]); break
        try:
            if u["text_id"] not in texts_done:
                nt = R.ar_input_tokens(ar, u["full_text"]); assert nt < MAX_AR_TOKENS, nt
                R.append_jsonl(F["texts.jsonl"], {"text_id": u["text_id"], "realization_id": u["realization_id"], "carrier_id": u["carrier_id"], "full_text": u["full_text"],
                                                  "ar_input_tokens": nt, "ar_input_truncated": False})
            if u["text_id"] in preds:
                pred = preds[u["text_id"]]
            elif u["realization_id"].endswith("_m_same_orig") and f"{u['carrier_id']}_carrier" in preds:
                pred = preds[f"{u['carrier_id']}_carrier"]  # identical text
            else:
                pred = ar.predict(u["full_text"]).numpy()
            preds[u["text_id"]] = pred
            c = cm[u["carrier_id"]]; hA, hB = acts[c["pair_id"]]
            ref = preds.get(u["orig_ref"]) if u["orig_ref"] else None
            V = R.movement(pred, ref) if ref is not None else float("nan")
            rows = []
            for aid, h in ((c["pair_id"] + "A", hA), (c["pair_id"] + "B", hB)):
                cs = L.cos(pred, h)
                rows.append({"text_id": u["text_id"], "activation_id": aid, "cos": cs, "mse": L.mse_from_cos(cs), "pred_norm": float(np.linalg.norm(pred)),
                             "V_vs_orig_wording": V, "carrier_id": u["carrier_id"], "pair_id": c["pair_id"], "truth_of_activation": ""})
            pd.DataFrame(rows).to_csv(F["scores.csv"], mode="a", header=False, index=False)
            done_scores.add(u["text_id"])
        except Exception:
            prog.fail(f"ar {u['text_id']}: {traceback.format_exc()[-300:]}")
            R.append_jsonl(F["texts.jsonl"], {"text_id": u["text_id"], "realization_id": u["realization_id"], "carrier_id": u["carrier_id"], "full_text": u["full_text"],
                                              "ar_input_tokens": -1, "ar_input_truncated": False, "error": traceback.format_exc()})
        if k % 50 == 49:
            np.savez(PREDS, **preds); prog.completed("ar_texts", len(done_scores))
            L.log(f"B1 ar: {len(done_scores)}/{len(units)} texts, {(time.time()-t0)/max(1, ar.n_forward-n_fwd0):.2f} s/forward")
    np.savez(PREDS, **preds); prog.completed("ar_texts", len(done_scores))
    ar.free()
    L.log(f"B1 ar done: {len(done_scores)}/{len(units)} texts, {ar.n_forward} forwards")


def main():
    prog = R.Progress(STAGE)
    S = L.Settings(PFX, fillings=FILLINGS, n_par=N_PAR, transforms=TRANSFORMS, cut_rules_applied=["B1(a) fillings 5 -> 4 (drop f4)"],
                   decoding="sampled T=1.0 top_p=1 top_k=0, seed 5000 + 2*pair_index + (0 A / 1 B)", position="last token of the context (final '.')",
                   preamble=R.PREAMBLE, filler2_applied=False, task_instructions=R.TASK_INSTRUCTIONS, agent_model=R.AGENT_MODEL,
                   keyword_rule="case-insensitive whole-word keyword hit (family sets in r4_lib.b1_pairs); snippet regex 'final token|last token|expecting|continu' never a slot",
                   eligibility="exactly one sentence with asserts in {A,B}; >=2 -> redundant; 0 -> omission; duplicated sentence -> dup_sentence",
                   swap_rule="swapped sentence accepted iff edit_check == Yes and slot_verify(swapped) == other meaning", validity="valid = (equiv == Yes); used in mu iff valid and not a detected duplicate",
                   bootstrap="cluster by pair, 1000 draws, seed 0; eval = fillings 1-3; dev = filling 0", equiv_shuffle_seed=9000)
    hits = R.assert_no_av_model_calls([L.OVERNIGHT / "b1_pairs.py", L.OVERNIGHT / "r4_lib.py"]); assert not hits, hits
    ctxs = contexts_list()
    if prog.d.get("blocked"):
        L.log(f"B1 previously blocked: {prog.d['blocked']}")
    phase_target(prog, ctxs)
    av = phase_av(prog, ctxs)
    if prog.over_cap() or prog.over_failures():
        prog.block("cap or failures reached during AV"); S.finish(progress=prog.d); L.log("B1 blocked during AV; running analysis on partial data")
    else:
        slots, carriers = phase_slots(prog, ctxs, av)
        cands = phase_swap(prog, ctxs, slots, carriers)
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(L.snapshot(L.TARGET))
        reals = phase_rewrite_equiv(prog, cands, carriers, tok)
        phase_ar(prog, ctxs, av, slots, reals, carriers)
        if prog.over_cap() or prog.over_failures():
            prog.block("cap or failures reached during AR")
    prog.set_phase("analyze")
    from overnight import b1_analyze
    b1_analyze.run(labels=None)
    prog.set_phase("done"); S.finish(progress=prog.d, ar_forwards=None)
    L.log(f"B1 done: {prog.minutes:.1f} min cumulative (cap {prog.cap})")


if __name__ == "__main__":
    main()

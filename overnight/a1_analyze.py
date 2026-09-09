"""A1 analysis — kill lines A1 and A1-nat, paraphrase sensitivity, correct-meaning ranking, 2x2 blocks, Distributions, review sheets.

  uv run python overnight/a1_analyze.py [--labels <csv>]

--labels <csv> (label_source=human): columns item_type,item_id,field,value with item_type in {slot, candidate, realization}
(slot: asserts / label_orig; candidate: edit_ok / label; realization: equiv). Human labels recompute eligibility, candidate roles and
paraphrase validity from the raw scores (never touched); output a1_summary_human.md, no DISCONFIRMATION line.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import r4_lib as R  # noqa: E402
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

PFX = "a1"
TRANSFORMS = ["light1", "aggr1"]
MIN_SLOTS, MIN_NAT = 30, 15
FALSE_CATS = ["entity_sub", "detail_sub", "relation_rev", "negation"]


def run(labels: str | None):
    O = L.OVERNIGHT
    ctx = pd.read_csv(O / f"{PFX}_contexts.csv", keep_default_na=False)
    av = {int(r["context_id"]): r for r in R.read_jsonl(O / f"{PFX}_av.jsonl")}
    slots = pd.read_csv(O / f"{PFX}_slots.csv", keep_default_na=False) if (O / f"{PFX}_slots.csv").exists() else pd.DataFrame()
    cands = R.read_jsonl(O / f"{PFX}_candidates.jsonl")
    reals = R.read_jsonl(O / f"{PFX}_realizations.jsonl")
    scores = pd.read_csv(O / f"{PFX}_scores.csv", keep_default_na=False) if (O / f"{PFX}_scores.csv").exists() else pd.DataFrame(columns=["text_id", "activation_id", "cos", "V_vs_orig_wording"])
    src = "claude"
    if labels:
        src = "human"; lab = pd.read_csv(labels, keep_default_na=False)
        for r in lab.itertuples():
            if r.item_type == "slot":
                slots.loc[slots.slot_id == r.item_id, r.field] = r.value
            elif r.item_type == "candidate":
                for m in cands:
                    if m["meaning_id"] == r.item_id:
                        m[r.field] = (r.value == "True") if r.field == "edit_ok" else r.value
            elif r.item_type == "realization":
                for x in reals:
                    if x["realization_id"] == r.item_id:
                        x["equiv"] = r.value; x["valid"] = r.value == "Yes"
    cm = ctx.set_index("context_id").to_dict("index")
    S = {(r.text_id, int(r.activation_id)): float(r.cos) for r in scores.itertuples()} if len(scores) else {}
    Vm = {(r.text_id, int(r.activation_id)): (float(r.V_vs_orig_wording) if str(r.V_vs_orig_wording) not in ("", "nan") else float("nan")) for r in scores.itertuples()} if len(scores) else {}
    rmap = {}
    for x in reals:
        rmap.setdefault(x["meaning_id"], []).append(x)
    # ---- roles recomputed from labels
    for m in cands:
        if m["category"] == "correct_original":
            m["role"] = "correct" if m["label"] == "entailed" else "original_relabelled"
        elif m["category"] == "original_contradicted":
            m["role"] = "natural_error_original" if m["label"] == "contradicted" else "original_relabelled"
        elif m["category"] == "correction":
            m["role"] = "correct" if (m["edit_ok"] and m["label"] == "entailed") else "invalid_correction"
        elif m["category"] in FALSE_CATS:
            if m.get("duplicate_of"):
                m["role"] = "false_duplicate"
            elif m["edit_ok"] is False or m["role"] == "dropped_NONE":
                m["role"] = "dropped_NONE" if m["role"] == "dropped_NONE" else "false_edit_rejected"
            elif m["edit_ok"] and m["label"] == "contradicted":
                m["role"] = "false"
            elif m["edit_ok"]:
                m["role"] = "false_descriptive"
    # ---- per-meaning μ
    def mu_of(mid, cid):
        rl = rmap.get(mid, []); orig = [x for x in rl if x["transform"] == "orig"]
        pars = [x for x in rl if x["transform"] in TRANSFORMS and x.get("valid") and not x.get("dup_detected")]
        vals = [S.get((x["realization_id"], cid), float("nan")) for x in pars]; vals = [v for v in vals if not np.isnan(v)]
        o = S.get((orig[0]["realization_id"], cid), float("nan")) if orig else float("nan")
        return (float(np.mean(vals)) if vals else float("nan")), o, len(vals)
    prows, srows, crows = [], [], []
    for s in slots.itertuples():
        cid = int(s.context_id); sid = s.slot_id
        elig = (s.asserts == "yes") and str(s.dup_sentence) != "True" and str(s.fact_repeated_by) in ("[]", "") and s.label_orig in ("entailed", "contradicted")
        ms = [m for m in cands if m["slot_id"] == sid]
        correct = [m for m in ms if m["role"] == "correct"]; false = [m for m in ms if m["role"] == "false"]
        row = {"slot_id": sid, "context_id": cid, "split": cm[cid]["split"], "slot_type": s.slot_type, "focus_word": s.focus_word, "label_orig": s.label_orig, "asserts": s.asserts,
               "eligible": bool(elig), "ineligible_reason": "" if elig else (s.ineligible_reason or ("original_undetermined" if s.label_orig == "undetermined" else "")),
               "n_false_in_play": len(false), "n_false_descriptive": sum(m["role"] == "false_descriptive" for m in ms), "has_correct": bool(correct), "in_primary": False, "natural_error": False}
        if elig and correct:
            muc, oc, nc = mu_of(correct[0]["meaning_id"], cid)
            row.update({"mu_correct": muc, "o_correct": oc, "n_par_correct": nc, "correct_category": correct[0]["category"]})
            fm = []
            for m in false:
                mu, o, n = mu_of(m["meaning_id"], cid)
                if not np.isnan(mu):
                    fm.append((m["category"], mu, o))
                    crows.append({"slot_id": sid, "context_id": cid, "split": row["split"], "slot_type": s.slot_type, "category": m["category"], "mu_false": mu, "o_false": o, "mu_correct": muc, "o_correct": oc,
                                  "diff": muc - mu, "diff_orig": oc - o, "won": float(muc > mu)})
            if not np.isnan(muc) and fm:
                row.update({"in_primary": True, "n_false_mu": len(fm), "G": muc - float(np.mean([f[1] for f in fm])), "G_orig": oc - float(np.mean([f[2] for f in fm])),
                            "correct_first": float(muc > max(f[1] for f in fm)), "correct_first_orig": float(oc > max(f[2] for f in fm)), "frac_won": float(np.mean([muc > f[1] for f in fm]))})
            else:
                row["primary_exclusion"] = "no_valid_correct_paraphrase" if np.isnan(muc) else "no_valid_false_meaning"
        elif elig:
            row["primary_exclusion"] = "no_valid_correction" if s.label_orig == "contradicted" else "no_correct_meaning"
        # natural error: contradicted original with a valid correction
        nat = [m for m in ms if m["role"] == "natural_error_original"]
        if elig and nat and correct and correct[0]["category"] == "correction":
            mu_o, o_o, n_o = mu_of(nat[0]["meaning_id"], cid); mu_c, o_c, n_c = mu_of(correct[0]["meaning_id"], cid)
            if not np.isnan(mu_o) and not np.isnan(mu_c):
                row.update({"natural_error": True, "nat_diff": mu_c - mu_o, "nat_diff_orig": o_c - o_o, "mu_original": mu_o, "mu_correction": mu_c})
        row["deletion_delta"] = S.get((f"{sid}_deletion", cid), float("nan")) - S.get((f"c{cid}_carrier", cid), float("nan"))
        row["s_carrier"] = S.get((f"c{cid}_carrier", cid), float("nan"))
        srows.append(row)
        # paraphrase rows
        for m in ms:
            if m["role"] not in ("correct", "false", "false_descriptive", "natural_error_original"):
                continue
            truth = "entailed" if m["role"] == "correct" else ("contradicted" if m["role"] in ("false", "natural_error_original") else m.get("label", ""))
            rl = rmap.get(m["meaning_id"], []); orig = [x for x in rl if x["transform"] == "orig"]
            o = S.get((orig[0]["realization_id"], cid), float("nan")) if orig else float("nan")
            for x in [x for x in rl if x["transform"] in TRANSFORMS]:
                cp = S.get((x["realization_id"], cid), float("nan"))
                prows.append({"slot_id": sid, "context_id": cid, "split": row["split"], "slot_type": s.slot_type, "meaning_id": m["meaning_id"], "category": m["category"], "role": m["role"], "truth": truth,
                              "transform": x["transform"], "group": "light" if x["transform"].startswith("light") else "aggressive", "valid": bool(x.get("valid")), "dup_detected": bool(x.get("dup_detected")),
                              "cos": cp, "cos_orig": o, "delta": cp - o, "abs_delta": abs(cp - o), "V": Vm.get((x["realization_id"], cid), float("nan"))})
    SL = pd.DataFrame(srows); P = pd.DataFrame(prows); CR = pd.DataFrame(crows)
    SL.to_csv(O / f"{PFX}_slot_stats{'_human' if labels else ''}.csv", index=False)
    if len(P):
        P.to_csv(O / f"{PFX}_paraphrase_rows{'_human' if labels else ''}.csv", index=False)
    ev = SL[(SL.split == "eval") & (SL.in_primary == True)] if len(SL) else SL
    dv = SL[(SL.split == "dev") & (SL.in_primary == True)] if len(SL) else SL
    nat = SL[(SL.split == "eval") & (SL.natural_error == True)] if len(SL) else SL
    empty = {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
    ciG = R.ci(ev.G, ev.context_id) if len(ev) else empty; outG = R.outcome(ciG, min_n=MIN_SLOTS)
    ciN = R.ci(nat.nat_diff, nat.context_id) if len(nat) else empty; outN = R.outcome(ciN, min_n=MIN_NAT)
    n_elig = int(SL.eligible.sum()) if len(SL) else 0
    cat_txt = "; ".join(f"{c} {R.fmt_ci(R.ci(g['diff'], g.context_id), 5)}" for c, g in CR[CR.split == 'eval'].groupby("category")) if len(CR) else "n/a"
    obsG = (f"mean G={R.fmt_ci(ciG, 5)} (eligible eval slots in primary {len(ev)} of {int((SL.split == 'eval').sum()) if len(SL) else 0} eval slots; {int(((SL.split == 'eval') & SL.eligible).sum()) if len(SL) else 0} eligible); "
            f"correct-ranks-first {R.fmt_ci(R.ci(ev.correct_first, ev.context_id), 3) if len(ev) else 'n/a'}; frac comparisons won {R.fmt_ci(R.ci(ev.frac_won, ev.context_id), 3) if len(ev) else 'n/a'}; "
            f"G orig-only {R.fmt_ci(R.ci(ev.G_orig, ev.context_id), 5) if len(ev) else 'n/a'}; by category (μ_correct − μ_false): {cat_txt}")
    obsN = (f"mean [μ_correction − μ_original]={R.fmt_ci(ciN, 5)} (natural-error eval slots {len(nat)}; contradicted eval originals {int(((SL.split == 'eval') & (SL.label_orig == 'contradicted')).sum()) if len(SL) else 0}; "
            f"valid corrections {int(sum(1 for m in cands if m['category'] == 'correction' and m['role'] == 'correct'))} of {int(sum(1 for m in cands if m['category'] == 'correction'))}); orig-only {R.fmt_ci(R.ci(nat.nat_diff_orig, nat.context_id), 5) if len(nat) else 'n/a'}")
    already = [ln for ln in (O / "DISCONFIRMATION.md").read_text().splitlines() if "  A1  A1  threshold=" in ln or "  A1  A1-nat  threshold=" in ln]
    if labels is None and already:
        kG = [ln for ln in already if "  A1  A1  " in ln][-1] + "  (already appended by the first analysis run; not duplicated)"
        kN = [ln for ln in already if "  A1  A1-nat  " in ln][-1] + "  (already appended by the first analysis run; not duplicated)"
    elif labels is None:
        kG = L.append_disconfirmation("A1", "A1", "CI95 (cluster by context, eval) of mean G = μ_correct − mean_false μ_m over valid paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval slots < 30 → INCONCLUSIVE", obsG, outG,
                                      "MET/INCONCLUSIVE = no detectable preference for the correct meaning under this scorer with this n (never 'the information is absent')")
        kN = L.append_disconfirmation("A1", "A1-nat", "CI95 (by context, eval) of mean [μ_correction − μ_original] on natural-error slots ≤ 0 → MET; > 0 → NOT MET; straddles or natural-error eval slots < 15 → INCONCLUSIVE (count reported; injected errors never substituted)", obsN, outN,
                                      "MET/INCONCLUSIVE = the scorer does not detectably prefer the corrected version of the AV's own errors at this n")
    else:
        kG = f"(human labels) A1 observed={obsG} {outG}"; kN = f"(human labels) A1-nat observed={obsN} {outN}"
    # ---- report
    def cirow(name, vals, clus, d=5):
        c = R.ci(vals, clus) if len(vals) else empty
        return f"| {name} | {c['mean']:.{d}f} | {c['lo']:.{d}f} | {c['hi']:.{d}f} | {c['n']} | {c['n_clusters']} |"
    H = ["| statistic | mean | CI lo | CI hi | n | clusters |", "|---|---|---|---|---|---|"]
    roles = pd.Series([m["role"] for m in cands]).value_counts().to_dict() if cands else {}
    cats = pd.Series([m["category"] for m in cands]).value_counts().to_dict() if cands else {}
    inv_by_tr = {tr: int(sum(1 for x in reals if x["transform"] == tr and not x.get("valid"))) for tr in TRANSFORMS}
    lines = [f"# A1 summary — natural AV claims, paraphrase-averaged semantic preference ({src} labels)", "",
             f"git {L.git_hash()[:8]}; settings in a1_settings.json; progress in a1_progress.json; cut rules A1(a)(b)(c) applied (V0)", "",
             "## Kill tests", "", f"- {kG}", f"- {kN}", "", "## Counts", "",
             f"- contexts {len(ctx)} (dev {int((ctx.split == 'dev').sum())}, eval {int((ctx.split == 'eval').sum())}); generations {len(av)} (parse_ok {sum(1 for r in av.values() if r.get('parse_ok'))}, cjk {sum(1 for r in av.values() if r.get('cjk'))}, errors {sum(1 for r in av.values() if r.get('error'))})",
             f"- slots {len(SL)} (entity {int((SL.slot_type == 'entity').sum()) if len(SL) else 0}, detail {int((SL.slot_type == 'detail').sum()) if len(SL) else 0}); contexts with 0/1/2 slots: " + (", ".join(f"{k}:{v}" for k, v in sorted(SL.groupby('context_id').size().value_counts().items())) if len(SL) else "n/a") + f"; contexts without any slot {len(av) - (SL.context_id.nunique() if len(SL) else 0)}",
             f"- slot_verify asserts yes {int((SL.asserts == 'yes').sum()) if len(SL) else 0} / no {int((SL.asserts == 'no').sum()) if len(SL) else 0}; ineligible: " + (json.dumps(SL[SL.eligible == False].ineligible_reason.value_counts().to_dict()) if len(SL) else "{}"),
             f"- label_orig: " + (json.dumps(SL.label_orig.value_counts().to_dict()) if len(SL) else "{}") + f"; evidence_found rate {slots.evidence_found.astype(str).eq('True').mean() if len(slots) else float('nan'):.2f}",
             f"- eligible slots {n_elig}; in primary {int(SL.in_primary.sum()) if len(SL) else 0} (eval {len(ev)}, dev {len(dv)}); primary exclusions " + (json.dumps(SL[(SL.eligible == True) & (SL.in_primary == False)].primary_exclusion.value_counts().to_dict()) if len(SL) else "{}"),
             f"- candidates {len(cands)} by category {json.dumps(cats)}; by role {json.dumps(roles)}",
             f"- natural-error slots (contradicted original with a valid correction and paraphrases): {int(SL.natural_error.sum()) if len(SL) else 0} (eval {len(nat)})",
             f"- realizations {len(reals)}; paraphrases {sum(1 for x in reals if x['transform'] in TRANSFORMS)}; invalid (equiv No) by transform {json.dumps(inv_by_tr)}; detected duplicates {sum(1 for x in reals if x.get('dup_detected'))}",
             "", "## (B) Primary: correct-meaning preference (eval, in-primary slots; cluster by context)", ""] + H + [
             cirow("G = μ_correct − mean_false μ_m", ev.G, ev.context_id), cirow("G (orig only)", ev.G_orig, ev.context_id),
             cirow("correct-ranks-first rate", ev.correct_first, ev.context_id, 3), cirow("correct-ranks-first (orig only)", ev.correct_first_orig, ev.context_id, 3),
             cirow("fraction of correct-vs-false comparisons won", ev.frac_won, ev.context_id, 3), cirow("G, dev", dv.G, dv.context_id),
             cirow("G, entity slots", ev[ev.slot_type == "entity"].G, ev[ev.slot_type == "entity"].context_id), cirow("G, detail slots", ev[ev.slot_type == "detail"].G, ev[ev.slot_type == "detail"].context_id),
             cirow("G, slots whose correct meaning is the original (entailed)", ev[ev.correct_category == "correct_original"].G, ev[ev.correct_category == "correct_original"].context_id) if len(ev) else "| G, original-correct | n/a | | | 0 | 0 |",
             cirow("G, slots whose correct meaning is a correction", ev[ev.correct_category == "correction"].G, ev[ev.correct_category == "correction"].context_id) if len(ev) else "| G, correction-correct | n/a | | | 0 | 0 |",
             "", "### By corruption category (eval; μ_correct − μ_false per (slot, false meaning); cluster by context)", "", "| category | n | mean diff | CI lo | CI hi | frac won | diff orig-only |", "|---|---|---|---|---|---|---|"]
    if len(CR):
        for c, g in CR[CR.split == "eval"].groupby("category"):
            a = R.ci(g["diff"], g.context_id); w = R.ci(g.won, g.context_id); o = R.ci(g.diff_orig, g.context_id)
            lines.append(f"| {c} | {a['n']} | {a['mean']:.5f} | {a['lo']:.5f} | {a['hi']:.5f} | {w['mean']:.3f} [{w['lo']:.3f},{w['hi']:.3f}] | {o['mean']:.5f} [{o['lo']:.5f},{o['hi']:.5f}] |")
    lines += ["", "## (C) Natural errors (eval; μ_correction − μ_original; cluster by context)", ""] + H + [
              cirow("μ_correction − μ_original", nat.nat_diff, nat.context_id), cirow("orig-only", nat.nat_diff_orig, nat.context_id),
              cirow("frac correction > original", (nat.nat_diff > 0).astype(float), nat.context_id, 3) if len(nat) else "| frac correction > original | n/a | | | 0 | 0 |"]
    if len(P):
        Pe = P[(P.split == "eval") & P.valid & ~P.dup_detected]
        lines += ["", "## (A) Paraphrase sensitivity (eval, valid paraphrases; cluster by context)", "", "| group × truth | n | mean abs Δ | CI lo | CI hi | signed Δ mean | signed CI |", "|---|---|---|---|---|---|---|"]
        for grp in ["light", "aggressive", "all"]:
            for tr in ["entailed", "contradicted"]:
                g = Pe[(Pe.truth == tr) & ((Pe.group == grp) if grp != "all" else True)]
                if len(g):
                    a = R.ci(g.abs_delta, g.context_id); sgn = R.ci(g.delta, g.context_id)
                    lines.append(f"| {grp} × {tr} | {a['n']} | {a['mean']:.5f} | {a['lo']:.5f} | {a['hi']:.5f} | {sgn['mean']:.5f} | [{sgn['lo']:.5f},{sgn['hi']:.5f}] |")
                else:
                    lines.append(f"| {grp} × {tr} | 0 | | | | | |")
        pc = Pe[Pe.role == "correct"].groupby("slot_id").abs_delta.mean(); pf = Pe[Pe.role == "false"].groupby("slot_id").abs_delta.mean()
        both = pd.concat([pc.rename("c"), pf.rename("f")], axis=1).dropna()
        if len(both):
            cid_of = SL.set_index("slot_id").context_id
            lines += ["", "P_correct − P_false within slot (paired, cluster by context): " + R.fmt_ci(R.ci(both.c - both.f, [cid_of[s] for s in both.index]), 5)]
        lines += ["", "## 2×2 blocks (eval, valid paraphrases in in-primary and natural-error slots; truth entailed / contradicted × slot type entity / detail)", ""]
        Pp = Pe[Pe.slot_id.isin(set(ev.slot_id) | set(nat.slot_id))]
        for stat, col, d in [("μ (cos of valid paraphrases)", "cos", 5), ("P: |Δ| vs orig", "abs_delta", 5), ("P: signed Δ vs orig", "delta", 5), ("V (reconstruction movement vs orig wording)", "V", 5)]:
            lines += [f"### {stat}", "", "| truth \\ slot type | entity | detail |", "|---|---|---|"]
            for tr in ["entailed", "contradicted"]:
                cells = []
                for stp in ["entity", "detail"]:
                    g = Pp[(Pp.truth == tr) & (Pp.slot_type == stp)]
                    cells.append((lambda c: f"n={c['n']} mean {c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]")(R.ci(g[col], g.context_id)) if len(g) else "n=0")
                lines.append(f"| {tr} | {cells[0]} | {cells[1]} |")
            lines += ["", "Distributions for the four cells:", ""] + R.DIST_HEADER
            for tr in ["entailed", "contradicted"]:
                for stp in ["entity", "detail"]:
                    g = Pp[(Pp.truth == tr) & (Pp.slot_type == stp)]; lines.append(R.dist_row(f"{stat} / {tr} × {stp}", g[col]))
            lines.append("")
        lines += ["### G by slot type (eval, in-primary)", ""] + H + [cirow("G / entity", ev[ev.slot_type == "entity"].G, ev[ev.slot_type == "entity"].context_id), cirow("G / detail", ev[ev.slot_type == "detail"].G, ev[ev.slot_type == "detail"].context_id)]
    lines += ["", "## (D) Deletion and movement", ""] + H + [cirow("deletion Δ = cos(deletion) − cos(carrier), eligible eval slots", SL[(SL.split == 'eval') & SL.eligible].deletion_delta, SL[(SL.split == 'eval') & SL.eligible].context_id) if len(SL) else "| deletion Δ | n/a | | | 0 | 0 |"]
    if len(P):
        for tr in TRANSFORMS:
            g = Pe[Pe["transform"] == tr]; lines.append(cirow(f"V, {tr} (eval, valid)", g.V, g.context_id))
    lines += ["", f"- s(h, own explanation): mean {SL.drop_duplicates('context_id').s_carrier.mean() if len(SL) else float('nan'):.5f} over {SL.context_id.nunique() if len(SL) else 0} contexts with slots"]
    par = [x for x in reals if x["transform"] in TRANSFORMS]
    if par:
        lines += ["", "## Lexical checks (advisory; agreement with equiv)", "", "| transform | n | equiv Yes | names_kept | numbers_kept | polarity_kept | len_ok | all four & Yes | all four & No |", "|---|---|---|---|---|---|---|---|---|"]
        for tr in TRANSFORMS:
            g = [x for x in par if x["transform"] == tr]; allf = lambda x: bool(x["names_kept"] and x["numbers_kept"] and x["polarity_kept"] and x["len_ok"])
            lines.append(f"| {tr} | {len(g)} | {sum(x['valid'] for x in g)} | {np.mean([x['names_kept'] for x in g]):.2f} | {np.mean([x['numbers_kept'] for x in g]):.2f} | {np.mean([x['polarity_kept'] for x in g]):.2f} | {np.mean([x['len_ok'] for x in g]):.2f} | {sum(allf(x) and x['valid'] for x in g)} | {sum(allf(x) and not x['valid'] for x in g)} |")
    lines += ["", "## Distributions", ""] + R.DIST_HEADER
    if len(ev):
        for nm, col in [("G (eval)", ev.G), ("G orig-only (eval)", ev.G_orig), ("μ_correct (eval)", ev.mu_correct), ("frac_won (eval)", ev.frac_won)]:
            lines.append(R.dist_row(nm, col))
    if len(nat):
        lines.append(R.dist_row("μ_correction − μ_original (eval natural errors)", nat.nat_diff))
    if len(CR):
        for c, g in CR[CR.split == "eval"].groupby("category"):
            lines.append(R.dist_row(f"μ_correct − μ_false / {c} (eval)", g["diff"]))
    if len(P):
        for tr in TRANSFORMS:
            lines.append(R.dist_row(f"|Δ| vs orig, {tr} (eval, valid)", Pe[Pe["transform"] == tr].abs_delta)); lines.append(R.dist_row(f"V, {tr} (eval, valid)", Pe[Pe["transform"] == tr].V))
    if len(SL):
        lines.append(R.dist_row("deletion Δ (eligible eval slots)", SL[(SL.split == 'eval') & SL.eligible].deletion_delta))
    lines += ["", "## 5 fixed verbatim examples (seed 0; eval in-primary slots)", ""]
    if len(ev):
        rng = np.random.default_rng(0); pick = list(rng.choice(ev.slot_id.values, size=min(5, len(ev)), replace=False)); sl = slots.set_index("slot_id")
        for sid in pick:
            r = ev[ev.slot_id == sid].iloc[0]; cid = int(r.context_id)
            lines += [f"### {sid} (context {cid}, {r.slot_type}, focus '{r.focus_word}', label_orig {r.label_orig})", "", f"- prefix tail (last 400 chars): {cm[cid]['text_full'][-400:]!r}",
                      f"- explanation: {av[cid]['explanation']!r}", f"- slot sentence: {sl.loc[sid].sentence!r}", f"- G = {r.G:.5f}; correct-first {r.correct_first}; μ_correct {r.mu_correct:.5f}"]
            for m in [m for m in cands if m["slot_id"] == sid]:
                lines.append(f"  - candidate [{m['category']} / role {m['role']} / label {m.get('label')} / edit_ok {m.get('edit_ok')}]: {m['sentence']!r}")
                for x in rmap.get(m["meaning_id"], []):
                    lines.append(f"    - [{x['transform']}] valid={x.get('valid')} cos={S.get((x['realization_id'], cid), float('nan')):.5f}: {x['text']!r}")
            lines.append(f"  - deletion: cos={S.get((f'{sid}_deletion', cid), float('nan')):.5f}; carrier cos={S.get((f'c{cid}_carrier', cid), float('nan')):.5f}")
            lines.append("")
    # review sheets
    if labels is None and len(SL):
        blind, key = [], []
        def add(row, extra):
            blind.append(dict(row, human_label="", human_note="")); key.append({**row, **extra})
        for m in [m for m in cands if m["category"] == "correction"]:
            s = SL[SL.slot_id == m["slot_id"]].iloc[0]; cid = int(m["context_id"]); orig = [x for x in cands if x["slot_id"] == m["slot_id"] and x["category"] == "original_contradicted"]
            row = {"item_id": m["meaning_id"], "item_type": "candidate", "context_id": cid, "prefix_text": cm[cid]["text_full"], "sentence": orig[0]["sentence"] if orig else "", "candidate_text": m["sentence"], "realization_text": "", "transform": "correction"}
            add(row, {"provisional_label_orig": s.label_orig, "provisional_label": m.get("label"), "edit_ok": m.get("edit_ok"), "role": m["role"], "cos_orig": S.get((f"{orig[0]['meaning_id']}_orig", cid), float("nan")) if orig else float("nan"), "cos_candidate": S.get((f"{m['meaning_id']}_orig", cid), float("nan"))})
        rng = np.random.default_rng(0)
        others = [("slot", s) for s in SL.itertuples() if not any(b["item_id"].startswith(s.slot_id + "_correction") for b in blind)]
        pars = [("real", x) for x in reals if x["transform"] in TRANSFORMS]
        pool = others + pars; order = rng.permutation(len(pool))
        for i in order:
            if len(blind) >= 60:
                break
            kind, x = pool[i]
            if kind == "slot":
                cid = int(x.context_id); sl_row = slots[slots.slot_id == x.slot_id].iloc[0]
                row = {"item_id": x.slot_id, "item_type": "slot", "context_id": cid, "prefix_text": cm[cid]["text_full"], "sentence": sl_row.sentence, "candidate_text": "", "realization_text": "", "transform": f"slot ({x.slot_type}, focus '{x.focus_word}')"}
                add(row, {"provisional_label_orig": x.label_orig, "provisional_asserts": x.asserts, "evidence": sl_row.evidence, "eligible": x.eligible, "s_carrier": x.s_carrier})
            else:
                cid = int(x["context_id"]); m = [m for m in cands if m["meaning_id"] == x["meaning_id"]][0]
                row = {"item_id": x["realization_id"], "item_type": "realization", "context_id": cid, "prefix_text": "", "sentence": m["sentence"], "candidate_text": "", "realization_text": x["text"], "transform": x["transform"]}
                add(row, {"equiv": x.get("equiv"), "valid": x.get("valid"), "category": m["category"], "role": m["role"], "cos": S.get((x["realization_id"], cid), float("nan")), "cos_orig": S.get((f"{m['meaning_id']}_orig", cid), float("nan"))})
        pd.DataFrame(blind).to_csv(O / f"{PFX}_review_blind.csv", index=False); pd.DataFrame(key).to_csv(O / f"{PFX}_review_key.csv", index=False)
        lines += ["", f"- review sheets: a1_review_blind.csv ({len(blind)} rows: every natural-error / correction pair first, then slots and realizations, seed 0) — open first; a1_review_key.csv after"]
    (O / f"{PFX}_summary{'_human' if labels else ''}.md").write_text("\n".join(lines) + "\n")
    L.log(f"A1 analysis written ({src}); A1 {outG} (n={len(ev)}), A1-nat {outN} (n={len(nat)})")
    return outG, outN


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--labels", default=None)
    a = ap.parse_args(); run(a.labels)

"""B1 analysis — kill line, headline tables, per-family and 2x2 blocks, Distributions, review sheets (PLAN.md round 4).

  uv run python overnight/b1_analyze.py [--labels <csv>]

--labels <csv> (label_source=human) has columns item_type,item_id,field,value with item_type in {slot, candidate, realization}
(slot: field asserts; candidate: fields edit_ok / swapped_asserts; realization: field equiv). Human labels recompute eligibility,
swap validity and paraphrase validity, then every table, from the raw scores (never touched); the output goes to
b1_summary_human.md and no DISCONFIRMATION line is appended.
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

PFX = "b1"
TRANSFORMS = ["light1", "light2", "aggr1", "aggr2"]
MIN_ELIGIBLE = 32


def fam_name(f):
    return {1: "F1 entity/recipient", 2: "F2 relation/order", 3: "F3 numerical detail", 4: "F4 outcome/polarity"}[int(f)]


def run(labels: str | None):
    O = L.OVERNIGHT
    ctx = pd.read_csv(O / f"{PFX}_contexts.csv", keep_default_na=False)
    av = {r["context_id"]: r for r in R.read_jsonl(O / f"{PFX}_av.jsonl")}
    slots = pd.read_csv(O / f"{PFX}_slots.csv", keep_default_na=False) if (O / f"{PFX}_slots.csv").exists() else pd.DataFrame()
    cands = R.read_jsonl(O / f"{PFX}_candidates.jsonl")
    reals = R.read_jsonl(O / f"{PFX}_realizations.jsonl")
    scores = pd.read_csv(O / f"{PFX}_scores.csv", keep_default_na=False) if (O / f"{PFX}_scores.csv").exists() else pd.DataFrame(columns=["text_id", "activation_id", "cos"])
    label_source = "claude"
    if labels:
        label_source = "human"
        lab = pd.read_csv(labels, keep_default_na=False)
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
    # ---- carriers (eligibility recomputed from slot labels)
    carriers = {}
    for cid in av:
        if av[cid].get("explanation") is None:
            continue
        ss = slots[slots.context_id == cid] if len(slots) else slots
        asserting = ss[ss.asserts.isin(["A", "B"])] if len(ss) else ss
        c = cm[cid]
        info = {"context_id": cid, "pair_id": c["pair_id"], "split": c["split"], "family": int(c["family"]), "slot_type": c["slot_type"], "version": c["version"],
                "name_overlap": str(c["name_overlap"]) == "True", "cos_hA_hB": float(c["cos_hA_hB"]), "n_candidate_slots": int(ss.candidate.astype(str).eq("True").sum()) if len(ss) else 0,
                "n_asserting": len(asserting), "av_asserts": "", "eligible": False, "ineligible_reason": "", "slot_id": ""}
        if len(slots) == 0:
            info["ineligible_reason"] = "no_slot_phase"
        elif len(asserting) == 0:
            info["ineligible_reason"] = "omission"
        elif len(asserting) > 1:
            info["ineligible_reason"] = "redundant"; info["av_asserts"] = "|".join(asserting.asserts)
        elif str(asserting.dup_sentence.iloc[0]) == "True":
            info["ineligible_reason"] = "dup_sentence"; info["av_asserts"] = asserting.asserts.iloc[0]
        else:
            info.update({"eligible": True, "av_asserts": asserting.asserts.iloc[0], "slot_id": asserting.slot_id.iloc[0]})
        info["av_asserts_mismatch"] = bool(info["av_asserts"] and info["av_asserts"] != c["version"])
        carriers[cid] = info
    # ---- swap validity from candidate labels
    mcand = {m["meaning_id"]: m for m in cands}
    for cid, info in carriers.items():
        sw = mcand.get(f"{cid}_m_swapped")
        info["swap_valid"] = bool(sw and sw.get("edit_ok") and sw.get("swapped_asserts") == sw.get("asserts_meaning")) if info["eligible"] else False
        info["has_swap_data"] = sw is not None
    # ---- per-realization scores
    sc = scores.copy()
    if len(sc):
        sc["cos"] = sc.cos.astype(float)
    S = {(r.text_id, r.activation_id): float(r.cos) for r in sc.itertuples()} if len(sc) else {}
    Vmap = {(r.text_id, r.activation_id): float(r.V_vs_orig_wording) if str(r.V_vs_orig_wording) not in ("", "nan") else float("nan") for r in sc.itertuples()} if len(sc) else {}
    rmap = {}
    for x in reals:
        rmap.setdefault(x["meaning_id"], []).append(x)
    rows, prows, vrows = [], [], []
    for cid, info in carriers.items():
        pid = info["pair_id"]; hA, hB = pid + "A", pid + "B"
        info["s_carrier_hA"] = S.get((f"{cid}_carrier", hA), float("nan")); info["s_carrier_hB"] = S.get((f"{cid}_carrier", hB), float("nan"))
        info["in_primary"] = False; info["primary_exclusion"] = info["ineligible_reason"] or ("" if info["swap_valid"] else "swap_invalid")
        if not (info["eligible"] and info["swap_valid"]):
            rows.append(info); continue
        mu, mu_o, npar = {}, {}, {}
        for key in ("same", "swapped"):
            mid = f"{cid}_m_{key}"; m = mcand[mid]; A = m["asserts_meaning"]
            rl = rmap.get(mid, [])
            orig = [x for x in rl if x["transform"] == "orig"]
            pars = [x for x in rl if x["transform"] in TRANSFORMS and x.get("valid") and not x.get("dup_detected")]
            npar[A] = len(pars)
            for act in (hA, hB):
                truth = "entailed" if A == act[-1] else "contradicted"
                co = S.get((orig[0]["realization_id"], act), float("nan")) if orig else float("nan")
                mu_o[(A, act)] = co
                vals = [S.get((x["realization_id"], act), float("nan")) for x in pars]
                mu[(A, act)] = float(np.nanmean(vals)) if len(vals) and not all(np.isnan(vals)) else float("nan")
                for x in [x for x in rl if x["transform"] in TRANSFORMS]:
                    cp = S.get((x["realization_id"], act), float("nan"))
                    prows.append({"context_id": cid, "pair_id": pid, "split": info["split"], "family": info["family"], "slot_type": info["slot_type"], "meaning": A, "activation": act,
                                  "truth": truth, "transform": x["transform"], "group": "light" if x["transform"].startswith("light") else "aggressive",
                                  "valid": bool(x.get("valid")), "dup_detected": bool(x.get("dup_detected")), "cos": cp, "cos_orig": co, "delta": cp - co, "abs_delta": abs(cp - co),
                                  "V": Vmap.get((x["realization_id"], act), float("nan"))})
            for x in [x for x in rl if x["transform"] in TRANSFORMS]:
                vrows.append({"context_id": cid, "pair_id": pid, "split": info["split"], "meaning": A, "transform": x["transform"], "valid": bool(x.get("valid")), "V": Vmap.get((x["realization_id"], hA), float("nan"))})
        info.update({"n_par_A": npar.get("A", 0), "n_par_B": npar.get("B", 0),
                     "mu_A_hA": mu.get(("A", hA)), "mu_B_hA": mu.get(("B", hA)), "mu_A_hB": mu.get(("A", hB)), "mu_B_hB": mu.get(("B", hB)),
                     "o_A_hA": mu_o.get(("A", hA)), "o_B_hA": mu_o.get(("B", hA)), "o_A_hB": mu_o.get(("A", hB)), "o_B_hB": mu_o.get(("B", hB))})
        ok = all(not np.isnan(info[k]) for k in ("mu_A_hA", "mu_B_hA", "mu_A_hB", "mu_B_hB"))
        info["in_primary"] = ok; info["primary_exclusion"] = "" if ok else "no_valid_paraphrase"
        if ok:
            info["D"] = (info["mu_A_hA"] - info["mu_B_hA"]) - (info["mu_A_hB"] - info["mu_B_hB"])
            info["both_sides_correct"] = float(info["mu_A_hA"] > info["mu_B_hA"] and info["mu_B_hB"] > info["mu_A_hB"])
        else:
            info["D"] = float("nan"); info["both_sides_correct"] = float("nan")
        if all(not np.isnan(info[k]) for k in ("o_A_hA", "o_B_hA", "o_A_hB", "o_B_hB")):
            info["D_orig"] = (info["o_A_hA"] - info["o_B_hA"]) - (info["o_A_hB"] - info["o_B_hB"])
            info["both_sides_correct_orig"] = float(info["o_A_hA"] > info["o_B_hA"] and info["o_B_hB"] > info["o_A_hB"])
        else:
            info["D_orig"] = float("nan"); info["both_sides_correct_orig"] = float("nan")
        dele = S.get((f"{cid}_m_deletion_deletion", cid), float("nan"))
        info["deletion_delta_own"] = dele - S.get((f"{cid}_carrier", cid), float("nan"))
        rows.append(info)
    C = pd.DataFrame(rows)
    for col in ["D", "D_orig", "both_sides_correct", "both_sides_correct_orig", "mu_A_hA", "mu_B_hA", "mu_A_hB", "mu_B_hB", "o_A_hA", "o_B_hA", "o_A_hB", "o_B_hB", "deletion_delta_own", "n_par_A", "n_par_B"]:
        if col not in C:
            C[col] = np.nan  # no carrier reached the primary (e.g. every context an omission)
    for col in ["in_primary", "eligible", "swap_valid", "av_asserts_mismatch", "name_overlap"]:
        if col not in C:
            C[col] = False
    for col in ["primary_exclusion", "ineligible_reason", "av_asserts", "slot_id", "split", "pair_id", "family", "slot_type", "version"]:
        if col not in C:
            C[col] = ""
    P = pd.DataFrame(prows); Vd = pd.DataFrame(vrows)
    C.to_csv(O / f"{PFX}_carriers{'_human' if labels else ''}.csv", index=False)
    if len(P):
        P.to_csv(O / f"{PFX}_paraphrase_rows{'_human' if labels else ''}.csv", index=False)
    # ---- statistics
    ev = C[(C.split == "eval") & (C.in_primary == True)] if len(C) else C
    dv = C[(C.split == "dev") & (C.in_primary == True)] if len(C) else C
    n_elig_eval = int(len(ev))
    ciD = R.ci(ev.D, ev.pair_id) if n_elig_eval else {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
    out = R.outcome(ciD, min_n=MIN_ELIGIBLE)
    n_omit = int((C.ineligible_reason == "omission").sum()) if len(C) else 0
    n_red = int((C.ineligible_reason == "redundant").sum()) if len(C) else 0
    n_mis = int(C.av_asserts_mismatch.sum()) if len(C) else 0
    n_swap_inv = int(((C.eligible == True) & (C.swap_valid == False)).sum()) if len(C) else 0
    inv_by_tr = {tr: int(sum(1 for x in reals if x["transform"] == tr and not x.get("valid"))) for tr in TRANSFORMS}
    bsc = R.ci(ev.both_sides_correct, ev.pair_id) if n_elig_eval else ciD
    ciDo = R.ci(ev.D_orig, ev.pair_id) if n_elig_eval else ciD
    fam_txt = "; ".join(f"F{f} {R.fmt_ci(R.ci(g.D, g.pair_id), 5)}" for f, g in ev.groupby("family")) if n_elig_eval else "n/a"
    observed = (f"mean D={R.fmt_ci(ciD, 5)} (eligible eval carriers in primary {n_elig_eval}, of {int((C.split == 'eval').sum()) if len(C) else 0} eval contexts); "
                f"both-sides-correct {R.fmt_ci(bsc, 3)}; D orig-only {R.fmt_ci(ciDo, 5)}; by family: {fam_txt}; mean cos(h_A,h_B) {C.drop_duplicates('pair_id').cos_hA_hB.mean() if len(C) else float('nan'):.4f}; "
                f"omission {n_omit} redundant {n_red} dup_sentence {int((C.ineligible_reason == 'dup_sentence').sum()) if len(C) else 0} swap_invalid {n_swap_inv} no_valid_paraphrase {int((C.primary_exclusion == 'no_valid_paraphrase').sum()) if len(C) else 0}; "
                f"av_asserts mismatch {n_mis}; invalid realizations by transform {json.dumps(inv_by_tr)}")
    kill_line = None
    already = [ln for ln in (O / "DISCONFIRMATION.md").read_text().splitlines() if "  B1  B1  threshold=" in ln]
    if labels is None and already:
        kill_line = already[-1] + "  (already appended by the first analysis run; not duplicated)"
    elif labels is None:
        kill_line = L.append_disconfirmation("B1", "B1", "CI95 (cluster by pair, eval) of mean D = [μ_A(h_A) − μ_B(h_A)] − [μ_A(h_B) − μ_B(h_B)] over valid English paraphrases (orig excluded) ≤ 0 → MET; > 0 → NOT MET; straddles or eligible eval carriers < 32 → INCONCLUSIVE",
                                            observed, out, "MET/INCONCLUSIVE = no detectable preference reversal under this scorer at this position with this n (never 'the fact is absent from the activation')")
    else:
        kill_line = f"(human labels) B1 threshold=as pre-registered observed={observed} {out}"
    # ---- report
    def cirow(name, vals, clus, d=5):
        c = R.ci(vals, clus) if len(vals) else {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
        return f"| {name} | {c['mean']:.{d}f} | {c['lo']:.{d}f} | {c['hi']:.{d}f} | {c['n']} | {c['n_clusters']} |"
    H = ["| statistic | mean | CI lo | CI hi | n | clusters |", "|---|---|---|---|---|---|"]
    lines = [f"# B1 summary — controlled paired contexts, meanings A/B ({label_source} labels)", "",
             f"git {L.git_hash()[:8]}; settings in b1_settings.json; progress in b1_progress.json", "",
             "## Kill test", "", f"- {kill_line}", "",
             "## Counts", "",
             f"- contexts {len(ctx)} (dev {int((ctx.split == 'dev').sum())}, eval {int((ctx.split == 'eval').sum())}); pairs {ctx.pair_id.nunique()}; generations {len(av)} (parse_ok {sum(1 for r in av.values() if r.get('parse_ok'))}, cjk {sum(1 for r in av.values() if r.get('cjk'))}, errors {sum(1 for r in av.values() if r.get('error'))})",
             f"- candidate slots {int(slots.candidate.astype(str).eq('True').sum()) if len(slots) else 0} of {len(slots)} sentences; asserting sentences {int(slots.asserts.isin(['A', 'B']).sum()) if len(slots) else 0}",
             f"- carriers: eligible {int(C.eligible.sum()) if len(C) else 0}; omission {n_omit}; redundant {n_red}; dup_sentence {int((C.ineligible_reason == 'dup_sentence').sum()) if len(C) else 0}; av_asserts mismatch (AV asserted the other meaning) {n_mis}; swap invalid {n_swap_inv}; in primary {int(C.in_primary.sum()) if len(C) else 0} (eval {n_elig_eval}, dev {len(dv)})",
             f"- realizations {len(reals)}; paraphrases {sum(1 for x in reals if x['transform'] in TRANSFORMS)}; invalid (equiv No) by transform {json.dumps(inv_by_tr)}; detected duplicates {sum(1 for x in reals if x.get('dup_detected'))}; dup_realization flagged by the editor {sum(1 for x in reals if x.get('dup_realization'))}",
             f"- eligibility by pair table: eval pairs with both contexts in primary {int(ev.groupby('pair_id').size().eq(2).sum()) if n_elig_eval else 0}",
             "", "## Primary statistics (eval, in-primary carriers; cluster bootstrap by pair)", ""] + H + [
             cirow("D (paraphrase-averaged μ, orig excluded)", ev.D, ev.pair_id), cirow("D (orig only)", ev.D_orig, ev.pair_id),
             cirow("both-sides-correct rate", ev.both_sides_correct, ev.pair_id, 3), cirow("both-sides-correct rate (orig only)", ev.both_sides_correct_orig, ev.pair_id, 3),
             cirow("μ_A(h_A) − μ_B(h_A)", ev.mu_A_hA - ev.mu_B_hA, ev.pair_id), cirow("μ_B(h_B) − μ_A(h_B)", ev.mu_B_hB - ev.mu_A_hB, ev.pair_id),
             cirow("deletion Δ (cos(deletion) − cos(carrier), own activation)", ev.deletion_delta_own, ev.pair_id)]
    if n_elig_eval:
        nn = ev[ev.name_overlap == False]
        lines += [cirow("D, eval without name_overlap pairs", nn.D, nn.pair_id), cirow("D, dev (filling 0)", dv.D, dv.pair_id) if len(dv) else "| D, dev | n/a | | | 0 | 0 |"]
        lines += [cirow("D, AV-asserted-correct carriers only (av_asserts == version)", ev[ev.av_asserts_mismatch == False].D, ev[ev.av_asserts_mismatch == False].pair_id),
                  cirow("D, AV-error carriers only (av_asserts != version)", ev[ev.av_asserts_mismatch == True].D, ev[ev.av_asserts_mismatch == True].pair_id)]
    lines += ["", "## By family (eval, in-primary)", "", "| family | n | D mean | CI lo | CI hi | both-sides-correct | D orig-only | n pairs |", "|---|---|---|---|---|---|---|---|"]
    for f in [1, 2, 3, 4]:
        g = ev[ev.family == f] if n_elig_eval else ev
        if len(g):
            c1 = R.ci(g.D, g.pair_id); c2 = R.ci(g.both_sides_correct, g.pair_id); c3 = R.ci(g.D_orig, g.pair_id)
            lines.append(f"| {fam_name(f)} | {len(g)} | {c1['mean']:.5f} | {c1['lo']:.5f} | {c1['hi']:.5f} | {c2['mean']:.3f} [{c2['lo']:.3f},{c2['hi']:.3f}] | {c3['mean']:.5f} [{c3['lo']:.5f},{c3['hi']:.5f}] | {g.pair_id.nunique()} |")
        else:
            lines.append(f"| {fam_name(f)} | 0 | | | | | | 0 |")
    lines += ["", "## 2×2 blocks (eval, in-primary; truth = meaning entailed / contradicted by the activation's context; slot type entity = F1, detail = F2–F4)", ""]
    if len(P):
        Pe = P[(P.split == "eval") & P.valid & ~P.dup_detected & P.context_id.isin(ev.context_id)]
        for stat, col, d in [("μ (cos of valid paraphrases)", "cos", 5), ("P: |Δ| vs orig", "abs_delta", 5), ("P: signed Δ vs orig", "delta", 5), ("V (reconstruction movement vs orig wording)", "V", 5)]:
            lines += [f"### {stat}", "", "| truth \\ slot type | entity | detail |", "|---|---|---|"]
            for tr in ["entailed", "contradicted"]:
                cells = []
                for stp in ["entity", "detail"]:
                    g = Pe[(Pe.truth == tr) & (Pe.slot_type == stp)]
                    if len(g):
                        c = R.ci(g[col], g.pair_id); cells.append(f"n={c['n']} mean {c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]")
                    else:
                        cells.append("n=0")
                lines.append(f"| {tr} | {cells[0]} | {cells[1]} |")
            lines += ["", "Distributions for the four cells:", ""] + R.DIST_HEADER
            for tr in ["entailed", "contradicted"]:
                for stp in ["entity", "detail"]:
                    g = Pe[(Pe.truth == tr) & (Pe.slot_type == stp)]
                    lines.append(R.dist_row(f"{stat} / {tr} × {stp}", g[col]))
            lines.append("")
        lines += ["### D by slot type (eval, in-primary)", ""] + H
        for stp in ["entity", "detail"]:
            g = ev[ev.slot_type == stp]; lines.append(cirow(f"D / {stp}", g.D, g.pair_id))
        lines += ["", "### Paraphrase sensitivity by transform group × truth (eval, valid paraphrases; |Δ| vs orig)", "", "| group | entailed | contradicted |", "|---|---|---|"]
        for grp in ["light", "aggressive"]:
            cells = []
            for tr in ["entailed", "contradicted"]:
                g = Pe[(Pe.group == grp) & (Pe.truth == tr)]
                c = R.ci(g.abs_delta, g.pair_id) if len(g) else None
                cells.append(f"n={c['n']} mean {c['mean']:.5f} [{c['lo']:.5f},{c['hi']:.5f}]" if c else "n=0")
            lines.append(f"| {grp} | {cells[0]} | {cells[1]} |")
        pe_ent = Pe[Pe.truth == "entailed"].groupby("context_id").abs_delta.mean(); pe_con = Pe[Pe.truth == "contradicted"].groupby("context_id").abs_delta.mean()
        both = pd.concat([pe_ent.rename("e"), pe_con.rename("c")], axis=1).dropna()
        if len(both):
            pid_of = ev.set_index("context_id").pair_id
            lines += ["", "P_entailed − P_contradicted within carrier (paired, cluster by pair): " + R.fmt_ci(R.ci(both.e - both.c, [pid_of[c] for c in both.index]), 5)]
    lines += ["", "## Per-context absolute scores", "", "| quantity | n | mean | min | max |", "|---|---|---|---|---|"]
    if len(C):
        for nm, col in [("s(h_own, carrier) = cos(h, AR(own explanation))", None)]:
            own = [r.s_carrier_hA if r.version == "A" else r.s_carrier_hB for r in C.itertuples()]
            oth = [r.s_carrier_hB if r.version == "A" else r.s_carrier_hA for r in C.itertuples()]
            lines.append(f"| {nm} | {len(own)} | {np.nanmean(own):.5f} | {np.nanmin(own):.5f} | {np.nanmax(own):.5f} |")
            lines.append(f"| s(h_other, carrier) | {len(oth)} | {np.nanmean(oth):.5f} | {np.nanmin(oth):.5f} | {np.nanmax(oth):.5f} |")
            lines.append(f"| cos(h_A, h_B) per pair | {C.pair_id.nunique()} | {C.drop_duplicates('pair_id').cos_hA_hB.mean():.5f} | {C.drop_duplicates('pair_id').cos_hA_hB.min():.5f} | {C.drop_duplicates('pair_id').cos_hA_hB.max():.5f} |")
        lines += ["", f"- t (extraction position) per context: min {ctx.t.min()} max {ctx.t.max()}; len_mismatch pairs {int(ctx.drop_duplicates('pair_id').len_mismatch.astype(str).eq('True').sum())}"]
    # lexical agreement (advisory)
    par = [x for x in reals if x["transform"] in TRANSFORMS]
    if par:
        lines += ["", "## Lexical checks (advisory; agreement with equiv)", "", "| transform | n | equiv Yes | names_kept | numbers_kept | polarity_kept | len_ok | all four & equiv Yes | all four & equiv No |", "|---|---|---|---|---|---|---|---|---|"]
        for tr in TRANSFORMS:
            g = [x for x in par if x["transform"] == tr]
            allf = lambda x: bool(x["names_kept"] and x["numbers_kept"] and x["polarity_kept"] and x["len_ok"])
            lines.append(f"| {tr} | {len(g)} | {sum(x['valid'] for x in g)} | {np.mean([x['names_kept'] for x in g]):.2f} | {np.mean([x['numbers_kept'] for x in g]):.2f} | {np.mean([x['polarity_kept'] for x in g]):.2f} | {np.mean([x['len_ok'] for x in g]):.2f} | {sum(allf(x) and x['valid'] for x in g)} | {sum(allf(x) and not x['valid'] for x in g)} |")
    # Distributions
    lines += ["", "## Distributions", ""] + R.DIST_HEADER
    if n_elig_eval:
        for nm, col in [("D (eval)", ev.D), ("D orig-only (eval)", ev.D_orig), ("μ_A(h_A)−μ_B(h_A) (eval)", ev.mu_A_hA - ev.mu_B_hA), ("μ_B(h_B)−μ_A(h_B) (eval)", ev.mu_B_hB - ev.mu_A_hB),
                        ("deletion Δ own (eval)", ev.deletion_delta_own), ("cos(h_A,h_B) (all pairs)", C.drop_duplicates("pair_id").cos_hA_hB)]:
            lines.append(R.dist_row(nm, col))
    if len(P):
        Pe2 = P[(P.split == "eval") & P.valid]
        for tr in TRANSFORMS:
            lines.append(R.dist_row(f"|Δ| vs orig, {tr} (eval, valid)", Pe2[Pe2.transform == tr].abs_delta))
        for tr in TRANSFORMS:
            lines.append(R.dist_row(f"V, {tr} (eval, valid)", Pe2[Pe2.transform == tr].V))
    # fixed examples
    lines += ["", "## 5 fixed verbatim examples (seed 0; eval in-primary carriers)", ""]
    if n_elig_eval:
        rng = np.random.default_rng(0); pick = list(rng.choice(ev.context_id.values, size=min(5, n_elig_eval), replace=False))
        sl = slots.set_index("slot_id") if len(slots) else None
        for cid in pick:
            info = ev[ev.context_id == cid].iloc[0]; c = cm[cid]; pid = info.pair_id
            lines += [f"### {cid} (pair {pid}, family {info.family}, {info.slot_type}, version {info.version}, av_asserts {info.av_asserts})", "",
                      f"- context (last 400 chars): {c['text_full'][-400:]!r}", f"- explanation: {av[cid]['explanation']!r}",
                      f"- slot sentence: {sl.loc[info.slot_id].sentence!r}", f"- D = {info.D:.5f}; both-sides-correct = {info.both_sides_correct}; μ_A(h_A) {info.mu_A_hA:.5f} μ_B(h_A) {info.mu_B_hA:.5f} μ_A(h_B) {info.mu_A_hB:.5f} μ_B(h_B) {info.mu_B_hB:.5f}"]
            for key in ("same", "swapped", "deletion"):
                mid = f"{cid}_m_{key}"
                for x in rmap.get(mid, []):
                    lines.append(f"  - [{key}/{x['transform']}] valid={x.get('valid')} equiv={x.get('equiv')} cos(h_A)={S.get((x['realization_id'], pid + 'A'), float('nan')):.5f} cos(h_B)={S.get((x['realization_id'], pid + 'B'), float('nan')):.5f}: {x['text']!r}")
            lines.append("")
    # review sheets (blind first: no scores, no provisional labels)
    if labels is None and len(C):
        blind, key = [], []
        sl = slots.set_index("slot_id") if len(slots) else None
        for r in C[C.eligible == True].itertuples():
            cid = r.context_id; c = cm[cid]
            same = mcand.get(f"{cid}_m_same", {}); sw = mcand.get(f"{cid}_m_swapped", {})
            row = {"item_id": f"{cid}_slot", "item_type": "slot", "context_id": cid, "prefix_text": c["text_full"], "sentence": same.get("sentence", ""),
                   "candidate_A": c["meaning_A"], "candidate_B": c["meaning_B"], "realization_text": sw.get("sentence", ""), "transform": "fact_swap", "human_label": "", "human_note": ""}
            blind.append(row)
            key.append({**row, "provisional_asserts": r.av_asserts, "provisional_swapped_asserts": sw.get("swapped_asserts", ""), "edit_ok": sw.get("edit_ok", ""),
                        "s_carrier_hA": r.s_carrier_hA, "s_carrier_hB": r.s_carrier_hB, "D": getattr(r, "D", float("nan"))})
        # candidate (keyword-hit) sentences that were judged, eligible or not: the human checks the provisional asserts label blind
        if len(slots):
            for sr in slots[slots.candidate.astype(str) == "True"].itertuples():
                if any(b["item_id"] == f"{sr.context_id}_slot" for b in blind) or len(blind) >= 60:
                    continue
                c = cm[sr.context_id]
                row = {"item_id": sr.slot_id, "item_type": "candidate_slot", "context_id": sr.context_id, "prefix_text": c["text_full"], "sentence": sr.sentence,
                       "candidate_A": c["meaning_A"], "candidate_B": c["meaning_B"], "realization_text": "", "transform": "slot_verify (does the sentence assert A, B or neither?)", "human_label": "", "human_note": ""}
                blind.append(row)
                key.append({**row, "provisional_asserts": sr.asserts, "provisional_other_content": sr.other_content, "edit_ok": "", "s_carrier_hA": S.get((f"{sr.context_id}_carrier", c["pair_id"] + "A"), float("nan")),
                            "s_carrier_hB": S.get((f"{sr.context_id}_carrier", c["pair_id"] + "B"), float("nan")), "D": float("nan")})
        rng = np.random.default_rng(0)
        pars = [x for x in reals if x["transform"] in TRANSFORMS]
        for i in rng.permutation(len(pars)):
            if len(blind) >= 60:
                break
            x = pars[i]; cid = x["context_id"]; c = cm[cid]; m = mcand[x["meaning_id"]]
            row = {"item_id": x["realization_id"], "item_type": "realization", "context_id": cid, "prefix_text": "", "sentence": m["sentence"], "candidate_A": "", "candidate_B": "",
                   "realization_text": x["text"], "transform": x["transform"], "human_label": "", "human_note": ""}
            blind.append(row)
            key.append({**row, "provisional_asserts": "", "provisional_swapped_asserts": "", "edit_ok": "", "equiv": x.get("equiv"), "valid": x.get("valid"),
                        "cos_hA": S.get((x["realization_id"], c["pair_id"] + "A"), float("nan")), "cos_hB": S.get((x["realization_id"], c["pair_id"] + "B"), float("nan")),
                        "cos_orig_hA": S.get((f"{x['meaning_id']}_orig", c["pair_id"] + "A"), float("nan"))})
        pd.DataFrame(blind).to_csv(O / f"{PFX}_review_blind.csv", index=False)
        pd.DataFrame(key).to_csv(O / f"{PFX}_review_key.csv", index=False)
        lines += ["", f"- review sheets: b1_review_blind.csv ({len(blind)} rows: every eligible fact slot first, then realizations, seed 0) — open first; b1_review_key.csv after"]
    (O / f"{PFX}_summary{'_human' if labels else ''}.md").write_text("\n".join(lines) + "\n")
    L.log(f"B1 analysis written ({label_source}); kill: {out}; eligible eval in primary {n_elig_eval}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--labels", default=None)
    a = ap.parse_args(); run(a.labels)

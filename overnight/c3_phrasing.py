"""C3 — meaning-preserving phrasing control for C2, factorial (PLAN.md round 3b; TARGET -> AV -> AV+AR co-resident).

  uv run python overnight/c3_phrasing.py

Cells: for each of the 40 C2 pairs, A = (a, w1), B = (b, w1) (existing; activations from out/c2_acts.npz, descriptions
from c2_descriptions.jsonl), C = (a, w2), D = (b, w2) (new: TARGET block-20 final-token activations, AV greedy 200-token
descriptions). The wording pair (w1 -> w2) is frozen in PLAN per template (primary; fallback if the primary changes the
token count under the TARGET tokenizer; drop the template if both fail — never a third pair). Replacement = first
whole-word occurrence of w1 in the template. Assertions per cell: all four contexts tokenise to the same length; the
new pair (C, D) satisfies C2's shared-suffix (>= 6) and entity-distance (8-20) rules.
Reconstruction margins (AR): all four descriptions against all four activations (16 per cell).
  M_fact(w1) = C2's M (recomputed from c2_pairs.csv cos columns, asserted equal; also re-scored fresh);
  M_fact(w2) = [cos(h_C,d_C) - cos(h_C,d_D)] + [cos(h_D,d_D) - cos(h_D,d_C)];
  M_wording(a) = [cos(h_A,d_A) - cos(h_A,d_C)] + [cos(h_C,d_C) - cos(h_C,d_A)];  M_wording(b) likewise on B, D.
Readout (AV forward, p1 from T2c): D(h) = lp(' e_a'|p1,h) - lp(' e_b'|p1,h) for all four activations.
Kill C3-score: CI95 (cluster by template) of mean [mean(M_fact(w1), M_fact(w2)) - mean(M_wording(a), M_wording(b))] <= 0 -> MET.
Kill C3-readout: CI95 (cluster by template) of mean [D(h_C) - D(h_D)] <= 0 -> MET.
Memory: TARGET alone -> free -> AV (generation) -> AR loaded alongside AV (allowed pair) -> both freed.
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.c2_matched import TEMPLATES, build_pairs, mentions, MIN_SHARED_SUFFIX, DIST_RANGE  # noqa: E402  (import-safe, checked in U0)
from overnight.t2_prefix import Prefix  # noqa: E402
from overnight.t2c_entity import NOUNS, P1  # noqa: E402  (Settings inside main)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

PRIMARY = [("country", "nation"), ("calls", "asks"), ("moved", "shifted"), ("orchestra", "ensemble"), ("pure", "solid"),
           ("story", "tale"), ("was", "got"), ("worked", "served"), ("team's", "club's"), ("shows", "depicts")]
FALLBACK = [("Tourists", "Visitors"), ("Stir", "Mix"), ("printed", "typed"), ("plays", "performs"), ("carefully", "gently"),
            ("during", "in"), ("explained", "described"), ("leaves", "exits"), ("wave", "raise"), ("painting", "picture")]
N_BOOT, SEED = 1000, 0
FIXED_CELLS = [0, 18, 36]
MAX_NEW_TOKENS = 200


def reword(tpl: str, w1: str, w2: str) -> str:
    pat = re.compile(r"(?<![A-Za-z])" + re.escape(w1) + r"(?![A-Za-z])")
    assert pat.search(tpl), (tpl, w1)
    return pat.sub(w2, tpl, count=1)


def ci(vals, clusters):
    return L.cluster_bootstrap_mean(vals, clusters, n_boot=N_BOOT, seed=SEED)


def fm(c, d=5):
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"


def main():
    S = L.Settings("c3", wording_primary=PRIMARY, wording_fallback=FALLBACK, replacement_rule="first whole-word occurrence of w1 in the template", prefix_p1=P1, nouns=NOUNS,
                   av_max_new_tokens=MAX_NEW_TOKENS, decoding="greedy", n_boot=N_BOOT, seed=SEED, fixed_cells=FIXED_CELLS,
                   kill_score="CI95 by template of mean[mean(M_fact(w1), M_fact(w2)) − mean(M_wording(a), M_wording(b))] ≤ 0 → MET",
                   kill_readout="CI95 by template of mean[D(h_C) − D(h_D)] under p1 ≤ 0 → MET")
    timings = {}
    c2 = pd.read_csv(L.OVERNIGHT / "c2_pairs.csv").sort_values("pair_id").reset_index(drop=True); assert len(c2) == 40
    H2 = np.load(L.OUT / "c2_acts.npz")["H"]; assert H2.shape == (40, 2, 3584)
    d2 = {(r["pair_id"], r["side"]): r for r in (json.loads(ln) for ln in (L.OVERNIGHT / "c2_descriptions.jsonl").read_text().splitlines() if ln.strip())}
    assert len(d2) == 80
    t2c = pd.read_csv(L.OVERNIGHT / "t2c_pairs.csv").sort_values("pair_id").reset_index(drop=True) if (L.OVERNIGHT / "t2c_pairs.csv").exists() else None
    # M_fact(w1) recomputed from the C2 file's cos columns, asserted equal to the file's M
    M_w1_file = (c2.cos_ha_da - c2.cos_ha_db) + (c2.cos_hb_db - c2.cos_hb_da)
    assert np.max(np.abs(M_w1_file - c2.M)) < 1e-9

    # ---------------- build cells under the TARGET tokenizer
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0
    tok = tgt.tok
    base_pairs = build_pairs(tok)  # re-asserts C2's construction; same order as c2_pairs
    assert [p["context_a"] for p in base_pairs] == c2.context_a.tolist()
    chosen, dropped, cells = {}, [], []
    for ti, (tpl, ents) in enumerate(TEMPLATES):
        pick = None
        for kind, (w1, w2) in [("primary", PRIMARY[ti]), ("fallback", FALLBACK[ti])]:
            tpl2 = reword(tpl, w1, w2)
            ok = True
            for a, b in ents:
                n = [len(tok(t, add_special_tokens=False)["input_ids"]) for t in [tpl.format(E=a), tpl.format(E=b), tpl2.format(E=a), tpl2.format(E=b)]]
                if len(set(n)) != 1:
                    ok = False; L.log(f"template {ti} {kind} ({w1}->{w2}) changes token count for {a}/{b}: {n}"); break
            if ok:
                pick = (kind, w1, w2, tpl2); break
        if pick is None:
            dropped.append(ti); L.log(f"template {ti}: primary and fallback both change the token count -> DROPPED"); continue
        chosen[ti] = pick
    for p in base_pairs:
        ti = p["template_id"]
        if ti not in chosen:
            continue
        kind, w1, w2, tpl2 = chosen[ti]
        cC, cD = tpl2.format(E=p["entity_a"]), tpl2.format(E=p["entity_b"])
        iA, iB, iC, iD = [tok(t, add_special_tokens=False)["input_ids"] for t in [p["context_a"], p["context_b"], cC, cD]]
        assert len(iA) == len(iB) == len(iC) == len(iD)
        suf = 0
        while suf < len(iC) and iC[-1 - suf] == iD[-1 - suf]:
            suf += 1
        assert suf >= MIN_SHARED_SUFFIX, (ti, suf)
        dCD = [k for k in range(len(iC)) if iC[k] != iD[k]]; dist_ent = len(iC) - dCD[0]
        assert DIST_RANGE[0] <= dist_ent <= DIST_RANGE[1], (ti, dist_ent)
        dAC = [k for k in range(len(iA)) if iA[k] != iC[k]]; dist_w = len(iA) - dAC[0]
        cells.append({**{k: p[k] for k in ["pair_id", "template_id", "entity_a", "entity_b", "context_a", "context_b", "n_tokens", "dist_to_end"]}, "cos_ha_hb": float(c2.cos_ha_hb[p["pair_id"]]),
                      "wording_kind": kind, "w1": w1, "w2": w2, "context_c": cC, "context_d": cD, "entity_dist_to_end_w2": dist_ent, "shared_suffix_cd": suf,
                      "wording_dist_to_end": dist_w, "n_wording_diff_tokens": len(dAC), "noun": NOUNS[ti], "error": ""})
    S.update(wording_chosen={ti: {"kind": k, "w1": w1, "w2": w2} for ti, (k, w1, w2, _) in chosen.items()}, templates_dropped=dropped, n_cells=len(cells))
    L.log(f"{len(cells)} cells from {len(chosen)} templates (dropped {dropped}); wording kinds {pd.Series([c['wording_kind'] for c in cells]).value_counts().to_dict()}")

    # ---------------- TARGET activations for C, D (and A, B re-derived as a sanity check against c2_acts)
    d = tgt.model.config.hidden_size
    H = np.zeros((len(cells), 4, d), np.float32)  # A, B, C, D
    t0 = time.time(); dev_ab = []
    for n, c in enumerate(cells):
        for j, ctx in enumerate([c["context_a"], c["context_b"], c["context_c"], c["context_d"]]):
            ids = tok(ctx, return_tensors="pt", add_special_tokens=False)["input_ids"]
            H[n, j] = L.to_cpu_f32(tgt.hidden_states(ids)[L.LAYER + 1][0, -1]).numpy()
        dev_ab.append(max(1 - L.cos(H[n, 0], H2[c["pair_id"], 0]), 1 - L.cos(H[n, 1], H2[c["pair_id"], 1])))
        H[n, 0], H[n, 1] = H2[c["pair_id"], 0], H2[c["pair_id"], 1]  # use C2's cached A, B exactly
        c["cos_hA_hB"] = L.cos(H[n, 0], H[n, 1]); c["cos_hA_hC"] = L.cos(H[n, 0], H[n, 2]); c["cos_hB_hD"] = L.cos(H[n, 1], H[n, 3]); c["cos_hC_hD"] = L.cos(H[n, 2], H[n, 3])
        c["cos_hA_hD"] = L.cos(H[n, 0], H[n, 3]); c["cos_hB_hC"] = L.cos(H[n, 1], H[n, 2]); c["norm_hC"] = float(np.linalg.norm(H[n, 2])); c["norm_hD"] = float(np.linalg.norm(H[n, 3]))
    timings["target_s_per_context"] = (time.time() - t0) / (4 * len(cells)); timings["max_1_minus_cos_AB_rederived_vs_c2_acts"] = float(max(dev_ab))
    tgt.free(); timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    np.savez(L.OUT / "c3_acts.npz", H=H, pair_id=np.array([c["pair_id"] for c in cells]))
    L.log(f"activations cached; A/B re-derivation max(1−cos) vs c2_acts {max(dev_ab):.2e}; mean cos(hA,hC) {np.mean([c['cos_hA_hC'] for c in cells]):.4f} cos(hA,hB) {np.mean([c['cos_hA_hB'] for c in cells]):.4f}")

    # ---------------- AV descriptions for C, D
    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    desc = {}
    t0 = time.time()
    with open(L.OVERNIGHT / "c3_descriptions.jsonl", "w") as f:
        for n, c in enumerate(cells):
            for j, side in [(2, "c"), (3, "d")]:
                own, other = (c["entity_a"], c["entity_b"]) if side == "c" else (c["entity_b"], c["entity_a"])
                rec = {"pair_id": c["pair_id"], "template_id": c["template_id"], "side": side, "wording": c["w2"], "entity_own": own, "entity_other": other, "context": c[f"context_{side}"], "error": None}
                try:
                    r = av.verbalize(torch.from_numpy(H[n, j]), max_new_tokens=MAX_NEW_TOKENS); rec.update(r)
                    rec["mentions_own"] = mentions(r["explanation"], own); rec["mentions_other"] = mentions(r["explanation"], other)
                    rec["mentions_w1"] = mentions(r["explanation"], c["w1"]); rec["mentions_w2"] = mentions(r["explanation"], c["w2"])
                except Exception:
                    rec["error"] = traceback.format_exc(); rec["explanation"] = None; rec["parse_ok"] = False; L.log(f"AV FAILED on cell {n} {side}")
                desc[(c["pair_id"], side)] = rec
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if n % 10 == 9:
                L.log(f"AV {n + 1}/{len(cells)} cells, {(time.time() - t0) / (2 * (n + 1)):.1f} s/gen")
    timings["av_s_per_gen"] = (time.time() - t0) / (2 * len(cells))

    # ---------------- AR (loaded alongside AV) + AV readout
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0; timings["rss_av_ar_G"] = L.rss_mb() / 1024
    P = Prefix(av)
    rows = []; t0 = time.time()
    for n, c in enumerate(cells):
        i = c["pair_id"]; row = dict(c)
        D_ = {"a": d2[(i, "a")], "b": d2[(i, "b")], "c": desc[(i, "c")], "d": desc[(i, "d")]}
        row.update({f"parse_ok_{s}": D_[s].get("parse_ok") for s in "abcd"}); row.update({f"mentions_own_{s}": D_[s].get("mentions_own") for s in "abcd"}); row.update({f"mentions_other_{s}": D_[s].get("mentions_other") for s in "abcd"})
        row["identical_cd"] = D_["c"].get("explanation") == D_["d"].get("explanation"); row["identical_ac"] = D_["a"].get("explanation") == D_["c"].get("explanation"); row["identical_bd"] = D_["b"].get("explanation") == D_["d"].get("explanation")
        try:
            texts = {s: (D_[s].get("explanation") or "") for s in "abcd"}
            R = {s: ar.predict(texts[s]).numpy() for s in "abcd"}
            hs = {"A": H[n, 0], "B": H[n, 1], "C": H[n, 2], "D": H[n, 3]}
            for hk, hv in hs.items():
                for s in "abcd":
                    row[f"cos_h{hk}_d{s}"] = L.cos(hv, R[s])
            row["M_fact_w1_file"] = float(c2.M[i]); row["M_fact_w1"] = (row["cos_hA_da"] - row["cos_hA_db"]) + (row["cos_hB_db"] - row["cos_hB_da"])
            row["M_fact_w2"] = (row["cos_hC_dc"] - row["cos_hC_dd"]) + (row["cos_hD_dd"] - row["cos_hD_dc"])
            row["M_wording_a"] = (row["cos_hA_da"] - row["cos_hA_dc"]) + (row["cos_hC_dc"] - row["cos_hC_da"])
            row["M_wording_b"] = (row["cos_hB_db"] - row["cos_hB_dd"]) + (row["cos_hD_dd"] - row["cos_hD_db"])
            row["M_fact_mean"] = 0.5 * (row["M_fact_w1"] + row["M_fact_w2"]); row["M_wording_mean"] = 0.5 * (row["M_wording_a"] + row["M_wording_b"]); row["M_fact_minus_wording"] = row["M_fact_mean"] - row["M_wording_mean"]
            row["M_fact_minus_wording_filew1"] = 0.5 * (row["M_fact_w1_file"] + row["M_fact_w2"]) - row["M_wording_mean"]
            # readout p1 on all four activations
            pre = P1.format(noun=c["noun"]); ca, cb = " " + c["entity_a"], " " + c["entity_b"]
            for hk, hv in hs.items():
                la, na = P.cont_logprob(torch.from_numpy(hv), pre, ca); lb, nb = P.cont_logprob(torch.from_numpy(hv), pre, cb)
                row[f"lp_a_h{hk}"] = la; row[f"lp_b_h{hk}"] = lb; row[f"D_h{hk}"] = la - lb
            row["donor_w1"] = row["D_hA"] - row["D_hB"]; row["donor_w2"] = row["D_hC"] - row["D_hD"]
            row["entity_effect"] = 0.5 * (row["D_hA"] + row["D_hC"]) - 0.5 * (row["D_hB"] + row["D_hD"]); row["wording_effect"] = 0.5 * (row["D_hA"] + row["D_hB"]) - 0.5 * (row["D_hC"] + row["D_hD"])
            row["interaction"] = 0.5 * ((row["D_hA"] - row["D_hB"]) - (row["D_hC"] - row["D_hD"]))
            row["both_correct_w1"] = (row["D_hA"] > 0) and (row["D_hB"] < 0); row["both_correct_w2"] = (row["D_hC"] > 0) and (row["D_hD"] < 0)
            if t2c is not None:
                row["D_hA_t2c"] = float(t2c.p1_D_a[i]); row["D_hB_t2c"] = float(t2c.p1_D_b[i])
        except Exception:
            row["error"] = traceback.format_exc(); L.log(f"AR/readout FAILED on cell {n}")
        rows.append(row)
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward + P.n_forward); timings["n_ar_forward"] = ar.n_forward; timings["n_av_forward"] = P.n_forward
    ar.free(); av.free()

    df = pd.DataFrame(rows); df.to_csv(L.OVERNIGHT / "c3_cells.csv", index=False)
    ok = df[df.error == ""].reset_index(drop=True)
    assert np.max(np.abs(ok.M_fact_w1_file - ok.M_fact_w1)) < 0.02, "fresh AR re-score of the C2 descriptions deviates from c2_pairs.csv by > 0.02"
    ci_score = ci(ok.M_fact_minus_wording, ok.template_id); out_score = L.outcome_ci_at_or_below(ci_score, 0.0, min_n=30)
    ci_score_file = ci(ok.M_fact_minus_wording_filew1, ok.template_id)
    ci_fw1, ci_fw2, ci_wa, ci_wb = ci(ok.M_fact_w1, ok.template_id), ci(ok.M_fact_w2, ok.template_id), ci(ok.M_wording_a, ok.template_id), ci(ok.M_wording_b, ok.template_id)
    ci_dist = ci(0.5 * ((1 - ok.cos_hA_hB) + (1 - ok.cos_hC_hD)) - 0.5 * ((1 - ok.cos_hA_hC) + (1 - ok.cos_hB_hD)), ok.template_id)
    L.append_disconfirmation("C3", "C3-score", "CI95 (cluster by template) of mean [mean(M_fact(w1), M_fact(w2)) − mean(M_wording(a), M_wording(b))] ≤ 0",
                             f"mean diff={fm(ci_score)} n={ci_score['n']} n_templates={ci_score['n_clusters']} (with file M_fact(w1): {fm(ci_score_file)}); M_fact(w1) {ci_fw1['mean']:.5f} M_fact(w2) {ci_fw2['mean']:.5f} M_wording(a) {ci_wa['mean']:.5f} M_wording(b) {ci_wb['mean']:.5f}; "
                             f"frac cells fact>wording {(ok.M_fact_minus_wording > 0).mean():.3f}; activation distance (1−cos): fact edit {np.mean(0.5 * ((1 - ok.cos_hA_hB) + (1 - ok.cos_hC_hD))):.5f} wording edit {np.mean(0.5 * ((1 - ok.cos_hA_hC) + (1 - ok.cos_hB_hD))):.5f} diff {fm(ci_dist)}; dropped templates {dropped}",
                             out_score, "MET would mean the reconstruction score discriminates a one-word phrasing change as well as a one-word fact change")
    ci_read = ci(ok.donor_w2, ok.template_id); out_read = L.outcome_ci_at_or_below(ci_read, 0.0, min_n=30)
    ci_read_w1, ci_ent, ci_word, ci_int = ci(ok.donor_w1, ok.template_id), ci(ok.entity_effect, ok.template_id), ci(ok.wording_effect, ok.template_id), ci(ok.interaction, ok.template_id)
    L.append_disconfirmation("C3", "C3-readout", "CI95 (cluster by template) of mean [D(h_C) − D(h_D)] under p1 (the T2c entity readout at the rephrased contexts) ≤ 0",
                             f"mean donor sensitivity at w2={fm(ci_read, 4)} n={ci_read['n']} n_templates={ci_read['n_clusters']}; at w1 (T2c contexts, re-scored) {fm(ci_read_w1, 4)}; frac>0 w2 {(ok.donor_w2 > 0).mean():.3f}; "
                             f"both-correct w2 {ok.both_correct_w2.mean():.3f} w1 {ok.both_correct_w1.mean():.3f}; 2×2: entity main effect {fm(ci_ent, 4)} wording main effect {fm(ci_word, 4)} interaction {fm(ci_int, 4)}",
                             out_read, "MET would mean the T2c entity preference does not survive a meaning-preserving phrasing change (only meaningful if T2c was NOT MET)")

    dl = pd.DataFrame(list(desc.values()))
    lines = ["# C3 summary — meaning-preserving phrasing control for C2, factorial (TARGET → AV → AV+AR)", "",
             f"git {L.git_hash()[:8]}; settings in c3_settings.json; cells in c3_cells.csv; new descriptions in c3_descriptions.jsonl; activations in out/c3_acts.npz (A, B, C, D)", "",
             "This is a *phrasing control*, not a zero-information edit: (w1 → w2) is a one-word, meaning-preserving wording change in the same sentence as the entity.", "",
             f"- cells {len(df)} (errors {int((df.error != '').sum())}); templates used {ok.template_id.nunique()}, dropped {dropped}; wording kinds {df.wording_kind.value_counts().to_dict()}",
             f"- wording pairs used: " + "; ".join(f"t{ti} {k}: {w1}→{w2}" for ti, (k, w1, w2, _) in chosen.items()),
             f"- wording word distance to end (tokens): {ok.wording_dist_to_end.min()}–{ok.wording_dist_to_end.max()} (mean {ok.wording_dist_to_end.mean():.1f}); entity distance {ok.entity_dist_to_end_w2.min()}–{ok.entity_dist_to_end_w2.max()} (mean {ok.entity_dist_to_end_w2.mean():.1f}); shared suffix C/D {ok.shared_suffix_cd.min()}–{ok.shared_suffix_cd.max()}; wording diff tokens {ok.n_wording_diff_tokens.min()}–{ok.n_wording_diff_tokens.max()}",
             f"- new AV descriptions: parse_ok {int(dl.parse_ok.fillna(False).astype(bool).sum())}/{len(dl)}, cjk {int(dl.cjk.fillna(False).astype(bool).sum())}/{len(dl)}, errors {int(dl.error.notna().sum())}; {timings['av_s_per_gen']:.1f} s/gen; AR forwards {timings['n_ar_forward']}; AV readout forwards {timings['n_av_forward']}",
             f"- A/B re-derivation vs c2_acts max(1−cos) {timings['max_1_minus_cos_AB_rederived_vs_c2_acts']:.2e}; fresh AR re-score of C2 descriptions: max |M_fact(w1) − file M| {np.max(np.abs(ok.M_fact_w1_file - ok.M_fact_w1)):.5f}",
             f"- identical descriptions: C=D {int(ok.identical_cd.sum())}/{len(ok)}; A=C {int(ok.identical_ac.sum())}/{len(ok)}; B=D {int(ok.identical_bd.sum())}/{len(ok)}",
             f"- entity mentions in the new descriptions (C, D): own {int(dl.mentions_own.fillna(False).astype(bool).sum())}/{len(dl)}, other {int(dl.mentions_other.fillna(False).astype(bool).sum())}/{len(dl)}; w2 word mentioned {int(dl.mentions_w2.fillna(False).astype(bool).sum())}/{len(dl)}, w1 word {int(dl.mentions_w1.fillna(False).astype(bool).sum())}/{len(dl)}; C2 (A, B) own-mention was 11/80",
             "", "## Kill C3-score", "",
             f"- mean [mean(M_fact) − mean(M_wording)]: {fm(ci_score)} n={ci_score['n']} clusters={ci_score['n_clusters']} → **{out_score}** (with the file's M_fact(w1): {fm(ci_score_file)})",
             "", "| margin | mean [CI by template] | frac > 0 |", "|---|---|---|",
             f"| M_fact(w1) (C2 pairs, re-scored) | {fm(ci_fw1)} | {(ok.M_fact_w1 > 0).mean():.3f} |", f"| M_fact(w2) (new pairs) | {fm(ci_fw2)} | {(ok.M_fact_w2 > 0).mean():.3f} |",
             f"| M_wording(a) | {fm(ci_wa)} | {(ok.M_wording_a > 0).mean():.3f} |", f"| M_wording(b) | {fm(ci_wb)} | {(ok.M_wording_b > 0).mean():.3f} |",
             f"| fact − wording (per cell) | {fm(ci_score)} | {(ok.M_fact_minus_wording > 0).mean():.3f} |",
             "", "## Activation distance per edit type", "", "| pair | mean cos | mean 1−cos | min cos | max cos |", "|---|---|---|---|---|"]
    for name, col in [("fact edit, w1: cos(h_A,h_B)", "cos_hA_hB"), ("fact edit, w2: cos(h_C,h_D)", "cos_hC_hD"), ("wording edit, a: cos(h_A,h_C)", "cos_hA_hC"), ("wording edit, b: cos(h_B,h_D)", "cos_hB_hD"), ("both edits: cos(h_A,h_D)", "cos_hA_hD"), ("both edits: cos(h_B,h_C)", "cos_hB_hC")]:
        lines.append(f"| {name} | {ok[col].mean():.4f} | {(1 - ok[col]).mean():.5f} | {ok[col].min():.4f} | {ok[col].max():.4f} |")
    lines += [f"", f"- activation-distance difference (fact − wording, 1−cos): {fm(ci_dist)}",
              "", "## Kill C3-readout (p1 entity readout on all four activations)", "",
              f"- mean [D(h_C) − D(h_D)] (donor sensitivity at w2): {fm(ci_read, 4)} n={ci_read['n']} → **{out_read}**",
              f"- at w1 (T2c contexts re-scored here): {fm(ci_read_w1, 4)}" + (f"; max |D − T2c D| = {max(np.max(np.abs(ok.D_hA - ok.D_hA_t2c)), np.max(np.abs(ok.D_hB - ok.D_hB_t2c))):.4f}" if t2c is not None else ""),
              f"- both-correct rate: w1 {ok.both_correct_w1.mean():.3f}, w2 {ok.both_correct_w2.mean():.3f}; frac donor>0: w1 {(ok.donor_w1 > 0).mean():.3f}, w2 {(ok.donor_w2 > 0).mean():.3f}",
              "", "### 2×2 table of mean D(h) (rows: entity; columns: wording)", "", "| | w1 | w2 |", "|---|---|---|",
              f"| entity a | {ok.D_hA.mean():+.4f} (A) | {ok.D_hC.mean():+.4f} (C) |", f"| entity b | {ok.D_hB.mean():+.4f} (B) | {ok.D_hD.mean():+.4f} (D) |",
              "", f"- entity main effect mean[D(h_A)+D(h_C)]/2 − mean[D(h_B)+D(h_D)]/2: {fm(ci_ent, 4)}", f"- wording main effect mean[D(h_A)+D(h_B)]/2 − mean[D(h_C)+D(h_D)]/2: {fm(ci_word, 4)}", f"- interaction ½[(D_A − D_B) − (D_C − D_D)]: {fm(ci_int, 4)}",
              "", "## Per-template table", "", "| template | wording | n | M_fact(w1) | M_fact(w2) | M_wording(a) | M_wording(b) | fact−wording | cos(hA,hB) | cos(hA,hC) | donor w1 | donor w2 | both-correct w2 | own-mention C/D |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for ti, g in ok.groupby("template_id"):
        gd = dl[dl.template_id == ti]
        lines.append(f"| {ti} | {g.w1.iloc[0]}→{g.w2.iloc[0]} ({g.wording_kind.iloc[0]}) | {len(g)} | {g.M_fact_w1.mean():.4f} | {g.M_fact_w2.mean():.4f} | {g.M_wording_a.mean():.4f} | {g.M_wording_b.mean():.4f} | {g.M_fact_minus_wording.mean():.4f} | {g.cos_hA_hB.mean():.4f} | {g.cos_hA_hC.mean():.4f} | "
                     f"{g.donor_w1.mean():.3f} | {g.donor_w2.mean():.3f} | {g.both_correct_w2.mean():.2f} | {gd.mentions_own.fillna(False).astype(bool).mean():.2f} |")
    lines += ["", "## Full cell table", "", "| pair | tpl | e_a/e_b | w1→w2 | M_fact w1 | M_fact w2 | M_word a | M_word b | cos(hA,hB) | cos(hA,hC) | cos(hB,hD) | D_A | D_B | D_C | D_D | own-mention a/b/c/d |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        if r.error:
            lines.append(f"| {r.pair_id} | {r.template_id} | {r.entity_a}/{r.entity_b} | {r.w1}→{r.w2} | ERROR | | | | | | | | | | | |"); continue
        lines.append(f"| {r.pair_id} | {r.template_id} | {r.entity_a}/{r.entity_b} | {r.w1}→{r.w2} | {r.M_fact_w1:.4f} | {r.M_fact_w2:.4f} | {r.M_wording_a:.4f} | {r.M_wording_b:.4f} | {r.cos_hA_hB:.4f} | {r.cos_hA_hC:.4f} | {r.cos_hB_hD:.4f} | {r.D_hA:+.2f} | {r.D_hB:+.2f} | {r.D_hC:+.2f} | {r.D_hD:+.2f} | {r.mentions_own_a}/{r.mentions_own_b}/{r.mentions_own_c}/{r.mentions_own_d} |")
    lines += ["", "## Three verbatim cells", ""]
    for i in FIXED_CELLS:
        sel = df[df.pair_id == i]
        if not len(sel):
            lines.append(f"### pair {i}: not in the cell set (template dropped)"); continue
        r = sel.iloc[0]
        lines += [f"### pair {i} (template {r.template_id}): {r.entity_a} / {r.entity_b}; {r.w1} → {r.w2}; M_fact(w1)={r.get('M_fact_w1', float('nan')):.4f} M_fact(w2)={r.get('M_fact_w2', float('nan')):.4f} M_wording(a)={r.get('M_wording_a', float('nan')):.4f} M_wording(b)={r.get('M_wording_b', float('nan')):.4f}"]
        for s, ctx in [("a", r.context_a), ("b", r.context_b), ("c", r.context_c), ("d", r.context_d)]:
            dd = d2[(i, s)] if s in "ab" else desc[(i, s)]
            lines += [f"- context_{s}: {ctx}", f"- d_{s} (mentions own={dd.get('mentions_own')}, other={dd.get('mentions_other')}): {dd.get('explanation')}"]
        lines.append("")
    (L.OVERNIGHT / "c3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, n_cells=len(df), n_errors=int((df.error != "").sum()), kill_C3_score={"ci": ci_score, "outcome": out_score, "ci_with_file_w1": ci_score_file}, kill_C3_readout={"ci": ci_read, "outcome": out_read},
             margins={"M_fact_w1": ci_fw1, "M_fact_w2": ci_fw2, "M_wording_a": ci_wa, "M_wording_b": ci_wb, "activation_distance_diff": ci_dist},
             readout={"donor_w1": ci_read_w1, "entity_effect": ci_ent, "wording_effect": ci_word, "interaction": ci_int, "both_correct_w1": float(ok.both_correct_w1.mean()), "both_correct_w2": float(ok.both_correct_w2.mean())})
    L.log(f"C3 done: score {fm(ci_score)} -> {out_score}; readout {fm(ci_read, 4)} -> {out_read}")


if __name__ == "__main__":
    main()

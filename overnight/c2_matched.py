"""C2 — matched semantic discrimination: two activations that differ in one fact (PLAN.md round 3).

  uv run python overnight/c2_matched.py

Stimuli: 10 fixed templates x 4 entity pairs (template-specific pairs, hard-coded below) = 40 pairs.
Both contexts of a pair are identical except the entity, which sits 8-20 tokens before the end; the
final 6+ tokens are identical; both contexts tokenize to the same length (asserted). h_a, h_b =
TARGET block-20 output (hidden_states[21]) at the shared final token (raw text, no special tokens).
Verbalize both with the default AV prompt (greedy, 200 tokens) -> d_a, d_b. Record whether each
description mentions its own entity / the other entity / neither (case-insensitive word match).
AR scores: cos(h_x, AR(d_y)) for x,y in {a,b}; four-way margin
  M = [cos(h_a,AR(d_a)) - cos(h_a,AR(d_b))] + [cos(h_b,AR(d_b)) - cos(h_b,AR(d_a))]
Cross-text control (round-1-style text edit): d_a with entity a replaced by b (and d_b with b -> a),
scored against its own activation; NA when the entity string does not occur in the description.
Kill C2 (pre-registered): CI95 of mean M, cluster bootstrap by template (1000 draws, seed 0) <= 0 -> MET.
Models are loaded sequentially in this process: TARGET -> free -> AV -> free -> AR.
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

TEMPLATES = [
    ("The capital of the country is {E}. Tourists arrive at the main station and walk to the",
     [("Paris", "Lyon"), ("Rome", "Milan"), ("Madrid", "Lisbon"), ("Berlin", "Munich")]),
    ("The recipe calls for two cups of {E}. Stir everything together in a large bowl and then",
     [("flour", "sugar"), ("rice", "milk"), ("butter", "cream"), ("water", "wine")]),
    ("The meeting has been moved to {E}. Everyone should bring the printed report and arrive at the",
     [("Monday", "Friday"), ("Tuesday", "Thursday"), ("March", "April"), ("noon", "dusk")]),
    ("She plays the {E} in the school orchestra. After every rehearsal the students pack up their things and",
     [("violin", "guitar"), ("flute", "horn"), ("piano", "drums"), ("trumpet", "organ")]),
    ("The ring was made of pure {E}. The jeweller placed it carefully in a small box on the",
     [("gold", "iron"), ("silver", "copper"), ("platinum", "bronze"), ("steel", "brass")]),
    ("The story is set in {E} during the winter. The main character wakes up early and looks out of the",
     [("London", "Tokyo"), ("Moscow", "Cairo"), ("Boston", "Denver"), ("Sydney", "Dublin")]),
    ("The patient was diagnosed with {E} last year. The doctor explained the treatment plan and asked the family to",
     [("asthma", "diabetes"), ("cancer", "arthritis"), ("malaria", "pneumonia"), ("measles", "influenza")]),
    ("He has worked as a {E} for twenty years. Every morning he leaves the house before sunrise and drives to the",
     [("teacher", "plumber"), ("lawyer", "farmer"), ("nurse", "baker"), ("pilot", "chef")]),
    ("The team's mascot is a {E}. Fans wave flags in the stands and sing loudly whenever the players",
     [("tiger", "dolphin"), ("bear", "eagle"), ("lion", "shark"), ("wolf", "hawk")]),
    ("The painting shows a {E} under a clear sky. Visitors to the gallery often stop in front of it and",
     [("river", "castle"), ("bridge", "forest"), ("garden", "desert"), ("mountain", "village")]),
]
MIN_SHARED_SUFFIX = 6
DIST_RANGE = (8, 20)
FIXED_EXAMPLES = [0, 9, 18, 27, 36]  # pair ids shown verbatim


def mentions(text: str, ent: str) -> bool:
    return re.search(r"\b" + re.escape(ent.lower()) + r"\b", (text or "").lower()) is not None


def build_pairs(tok) -> list[dict]:
    pairs = []
    for ti, (tpl, ents) in enumerate(TEMPLATES):
        for a, b in ents:
            ca, cb = tpl.format(E=a), tpl.format(E=b)
            ia = tok(ca, add_special_tokens=False)["input_ids"]; ib = tok(cb, add_special_tokens=False)["input_ids"]
            assert len(ia) == len(ib), (ti, a, b, len(ia), len(ib))
            diff = [k for k in range(len(ia)) if ia[k] != ib[k]]
            suf = 0
            while suf < len(ia) and ia[-1 - suf] == ib[-1 - suf]:
                suf += 1
            assert suf >= MIN_SHARED_SUFFIX, (ti, a, b, suf)
            dist = len(ia) - diff[0]
            assert DIST_RANGE[0] <= dist <= DIST_RANGE[1], (ti, a, b, dist)
            pairs.append({"pair_id": len(pairs), "template_id": ti, "template": tpl, "entity_a": a, "entity_b": b,
                          "context_a": ca, "context_b": cb, "n_tokens": len(ia), "n_diff_tokens": len(diff),
                          "diff_first_pos": diff[0], "dist_to_end": dist, "shared_suffix_tokens": suf,
                          "final_token": tok.decode([ia[-1]])})
    assert len(pairs) == 40
    return pairs


def main():
    S = L.Settings("c2", templates=TEMPLATES, min_shared_suffix=MIN_SHARED_SUFFIX, dist_range=DIST_RANGE,
                   av_max_new_tokens=200, decoding="greedy", activation="hidden_states[21] at the final token, raw text, add_special_tokens=False",
                   mention_rule="case-insensitive whole-word regex match of the entity in the parsed explanation",
                   cross_text_rule="str.replace of entity a by b (case-sensitive, first-letter case preserved as written) in d_a; NA if absent",
                   bootstrap="cluster by template_id (10 clusters), 1000 draws, seed 0", fixed_examples=FIXED_EXAMPLES)
    timings = {}
    # ---------------- TARGET activations
    t0 = time.time()
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    pairs = build_pairs(tgt.tok)
    d = tgt.model.config.hidden_size
    H = np.zeros((40, 2, d), np.float32)
    t0 = time.time()
    for p in pairs:
        for j, ctx in enumerate([p["context_a"], p["context_b"]]):
            ids = tgt.tok(ctx, return_tensors="pt", add_special_tokens=False)["input_ids"]
            hs = tgt.hidden_states(ids)
            H[p["pair_id"], j] = L.to_cpu_f32(hs[L.LAYER + 1][0, -1]).numpy()
        p["cos_ha_hb"] = L.cos(H[p["pair_id"], 0], H[p["pair_id"], 1])
        p["norm_ha"] = float(np.linalg.norm(H[p["pair_id"], 0])); p["norm_hb"] = float(np.linalg.norm(H[p["pair_id"], 1]))
    timings["target_s_per_context"] = (time.time() - t0) / 80
    tgt.free()
    np.savez(L.OUT / "c2_acts.npz", H=H, pair_id=np.arange(40))
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    L.log(f"80 activations cached; mean cos(h_a,h_b)={np.mean([p['cos_ha_hb'] for p in pairs]):.4f}")

    # ---------------- AV descriptions
    t0 = time.time()
    av = L.AV()
    timings["av_load_s"] = time.time() - t0
    desc = []
    t0 = time.time()
    with open(L.OVERNIGHT / "c2_descriptions.jsonl", "w") as f:
        for p in pairs:
            for j, side in enumerate(["a", "b"]):
                rec = {"pair_id": p["pair_id"], "template_id": p["template_id"], "side": side,
                       "entity_own": p[f"entity_{side}"], "entity_other": p["entity_b" if side == "a" else "entity_a"],
                       "context": p[f"context_{side}"], "error": None}
                try:
                    r = av.verbalize(torch.from_numpy(H[p["pair_id"], j]))
                    rec.update(r)
                    rec["mentions_own"] = mentions(r["explanation"], rec["entity_own"])
                    rec["mentions_other"] = mentions(r["explanation"], rec["entity_other"])
                except Exception:
                    rec["error"] = traceback.format_exc(); rec["explanation"] = None; rec["parse_ok"] = False
                    L.log(f"AV FAILED on pair {p['pair_id']} {side}")
                desc.append(rec)
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if p["pair_id"] % 10 == 9:
                L.log(f"AV {p['pair_id'] + 1}/40 pairs, {(time.time() - t0) / (2 * (p['pair_id'] + 1)):.1f} s/gen")
    timings["av_s_per_gen"] = (time.time() - t0) / 80
    av.free()
    timings["rss_after_av_free_G"] = L.rss_mb() / 1024

    # ---------------- AR scoring
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    D = {(r["pair_id"], r["side"]): r for r in desc}
    rows = []
    t0 = time.time()
    for p in pairs:
        i = p["pair_id"]
        da, db = D[(i, "a")], D[(i, "b")]
        row = dict(p)
        row.update({"parse_ok_a": da.get("parse_ok"), "parse_ok_b": db.get("parse_ok"), "cjk_a": da.get("cjk"), "cjk_b": db.get("cjk"),
                    "mentions_own_a": da.get("mentions_own"), "mentions_other_a": da.get("mentions_other"),
                    "mentions_own_b": db.get("mentions_own"), "mentions_other_b": db.get("mentions_other"),
                    "identical_descriptions": (da.get("explanation") == db.get("explanation")), "error": ""})
        try:
            ta, tb = da["explanation"] or "", db["explanation"] or ""
            ra, rb = ar.predict(ta).numpy(), ar.predict(tb).numpy()
            ha, hb = H[i, 0], H[i, 1]
            row["cos_ha_da"] = L.cos(ha, ra); row["cos_ha_db"] = L.cos(ha, rb)
            row["cos_hb_db"] = L.cos(hb, rb); row["cos_hb_da"] = L.cos(hb, ra)
            row["M_a"] = row["cos_ha_da"] - row["cos_ha_db"]; row["M_b"] = row["cos_hb_db"] - row["cos_hb_da"]
            row["M"] = row["M_a"] + row["M_b"]
            row["cos_da_db_pred"] = L.cos(ra, rb)
            # cross-text control: swap the entity string in the description
            for side, own, other, h, txt in [("a", p["entity_a"], p["entity_b"], ha, ta), ("b", p["entity_b"], p["entity_a"], hb, tb)]:
                if re.search(re.escape(own), txt):
                    sw = re.sub(re.escape(own), other, txt)
                    sw = re.sub(re.escape(own.lower()), other.lower(), sw) if own.lower() != own else sw
                    row[f"cos_h{side}_d{side}_swapped"] = L.cos(h, ar.predict(sw).numpy())
                    row[f"swap_delta_{side}"] = row[f"cos_h{side}_d{side}"] - row[f"cos_h{side}_d{side}_swapped"]
                    row[f"swap_n_{side}"] = len(re.findall(re.escape(own), txt))
                else:
                    row[f"cos_h{side}_d{side}_swapped"] = np.nan; row[f"swap_delta_{side}"] = np.nan; row[f"swap_n_{side}"] = 0
        except Exception:
            row["error"] = traceback.format_exc()
            L.log(f"AR FAILED on pair {i}")
        rows.append(row)
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward)
    timings["n_ar_forward"] = ar.n_forward
    ar.free()

    df = pd.DataFrame(rows)
    df.to_csv(L.OVERNIGHT / "c2_pairs.csv", index=False)
    ok = df[df.error == ""]

    def ci_of(vals, clusters):
        return L.cluster_bootstrap_mean(vals, clusters)

    def fmt(c, d=4):
        return f"{c['mean']:.{d}f} CI95=[{c['lo']:.{d}f},{c['hi']:.{d}f}] n={c['n']}"

    ci_M = ci_of(ok.M, ok.template_id)
    out = L.outcome_ci_at_or_below(ci_M, 0.0, min_n=30)
    frac_pos = float((ok.M > 0).mean())
    L.append_disconfirmation("C2", "C2", "CI95 of mean four-way margin M (cluster by template) ≤ 0",
                             f"mean M={fmt(ci_M, 5)} n_templates={ci_M['n_clusters']}; frac M>0={frac_pos:.3f}; mean cos(h_a,h_b)={ok.cos_ha_hb.mean():.4f}; "
                             f"mean cos own={np.mean(list(ok.cos_ha_da) + list(ok.cos_hb_db)):.4f} cross={np.mean(list(ok.cos_ha_db) + list(ok.cos_hb_da)):.4f}",
                             out, "MET would mean the score cannot tell which of two one-fact-different activations a description belongs to")

    ci_Ma = ci_of(ok.M_a, ok.template_id); ci_Mb = ci_of(ok.M_b, ok.template_id)
    swap = pd.concat([ok[["template_id", "swap_delta_a"]].rename(columns={"swap_delta_a": "v"}), ok[["template_id", "swap_delta_b"]].rename(columns={"swap_delta_b": "v"})]).dropna()
    ci_swap = ci_of(swap.v, swap.template_id) if len(swap) else {"mean": np.nan, "lo": np.nan, "hi": np.nan, "n": 0, "n_clusters": 0}
    # one-sided margins in the same units as the swap control: cos(h_a,d_a) − cos(h_a,d_b) per side
    side = pd.concat([ok[["template_id", "M_a"]].rename(columns={"M_a": "v"}), ok[["template_id", "M_b"]].rename(columns={"M_b": "v"})])
    ci_side = ci_of(side.v, side.template_id)
    dl = pd.DataFrame(desc)
    mo = dl.mentions_own.fillna(False).astype(bool); mt = dl.mentions_other.fillna(False).astype(bool)
    lines = ["# C2 summary — matched one-fact activation pairs (TARGET → AV → AR)", "",
             f"git {L.git_hash()[:8]}; settings in c2_settings.json; rows in c2_pairs.csv; descriptions in c2_descriptions.jsonl; activations in out/c2_acts.npz", "",
             f"- pairs: {len(df)} (errors {int((df.error != '').sum())}); templates {df.template_id.nunique()}; tokens per context {df.n_tokens.min()}–{df.n_tokens.max()}; "
             f"entity distance to end {df.dist_to_end.min()}–{df.dist_to_end.max()} tokens; shared suffix {df.shared_suffix_tokens.min()}–{df.shared_suffix_tokens.max()} tokens",
             f"- AV: parse_ok {int(dl.parse_ok.fillna(False).sum())}/80, cjk {int(dl.cjk.fillna(False).sum())}/80, errors {int(dl.error.notna().sum())}; {timings['av_s_per_gen']:.1f} s/gen",
             f"- identical descriptions within a pair: {int(ok.identical_descriptions.sum())}/{len(ok)}",
             "", "## Kill C2", "",
             f"- mean M (four-way margin): {fmt(ci_M, 5)}, clusters={ci_M['n_clusters']} templates; threshold ≤ 0 → **{out}**",
             f"- fraction of pairs with M > 0: {frac_pos:.3f} ({int((ok.M > 0).sum())}/{len(ok)})",
             f"- M_a = cos(h_a,d_a) − cos(h_a,d_b): {fmt(ci_Ma, 5)}; M_b = cos(h_b,d_b) − cos(h_b,d_a): {fmt(ci_Mb, 5)}",
             "", "## Activation geometry", "",
             f"- cos(h_a, h_b): mean {ok.cos_ha_hb.mean():.4f} min {ok.cos_ha_hb.min():.4f} max {ok.cos_ha_hb.max():.4f}; norms mean {ok.norm_ha.mean():.1f}",
             f"- cos(AR(d_a), AR(d_b)): mean {ok.cos_da_db_pred.mean():.4f}",
             "", "## Reconstruction scores", "", "| quantity | mean | min | max |", "|---|---|---|---|",
             f"| cos(h_a, AR(d_a)) own | {ok.cos_ha_da.mean():.4f} | {ok.cos_ha_da.min():.4f} | {ok.cos_ha_da.max():.4f} |",
             f"| cos(h_b, AR(d_b)) own | {ok.cos_hb_db.mean():.4f} | {ok.cos_hb_db.min():.4f} | {ok.cos_hb_db.max():.4f} |",
             f"| cos(h_a, AR(d_b)) cross | {ok.cos_ha_db.mean():.4f} | {ok.cos_ha_db.min():.4f} | {ok.cos_ha_db.max():.4f} |",
             f"| cos(h_b, AR(d_a)) cross | {ok.cos_hb_da.mean():.4f} | {ok.cos_hb_da.min():.4f} | {ok.cos_hb_da.max():.4f} |",
             "", "## Text-edit control (entity swapped inside the description, same activation) vs activation edit", "",
             f"- swap available (entity string present in description): {len(swap)}/{2 * len(ok)} descriptions",
             f"- cos(h, AR(d)) − cos(h, AR(d with entity swapped)): {fmt(ci_swap, 5)}",
             f"- per-side activation-edit margin cos(h_x,AR(d_x)) − cos(h_x,AR(d_y)) on all {len(side)} sides: {fmt(ci_side, 5)}",
             "", "## Entity mentions in the descriptions (80 descriptions)", "",
             f"- mentions own entity: {int(mo.sum())}/80; mentions other entity: {int(mt.sum())}/80; mentions neither: {int((~mo & ~mt).sum())}/80; both: {int((mo & mt).sum())}/80",
             "", "| template | own-mention rate | mean M | frac M>0 | mean cos(h_a,h_b) |", "|---|---|---|---|---|"]
    for ti, g in ok.groupby("template_id"):
        gd = dl[dl.template_id == ti]
        lines.append(f"| {ti} | {gd.mentions_own.fillna(False).astype(bool).mean():.2f} | {g.M.mean():.4f} | {(g.M > 0).mean():.2f} | {g.cos_ha_hb.mean():.4f} |")
    lines += ["", "## Five verbatim pairs", ""]
    for i in FIXED_EXAMPLES:
        r = df[df.pair_id == i].iloc[0]; da, db = D[(i, "a")], D[(i, "b")]
        lines += [f"### pair {i} (template {r.template_id}): {r.entity_a} / {r.entity_b}; cos(h_a,h_b)={r.cos_ha_hb:.4f}; M={r.get('M', float('nan')):.4f}",
                  f"- context_a: {r.context_a}", f"- context_b: {r.context_b}",
                  f"- d_a (mentions own={da.get('mentions_own')}, other={da.get('mentions_other')}; cos own {r.get('cos_ha_da', float('nan')):.4f}, cross {r.get('cos_ha_db', float('nan')):.4f}): {da.get('explanation')}",
                  f"- d_b (mentions own={db.get('mentions_own')}, other={db.get('mentions_other')}; cos own {r.get('cos_hb_db', float('nan')):.4f}, cross {r.get('cos_hb_da', float('nan')):.4f}): {db.get('explanation')}", ""]
    (L.OVERNIGHT / "c2_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, n_pairs=len(df), n_errors=int((df.error != "").sum()), kill_C2={"ci": ci_M, "outcome": out, "frac_M_pos": frac_pos},
             swap_control=ci_swap, per_side_margin=ci_side, mentions={"own": int(mo.sum()), "other": int(mt.sum())})
    L.log(f"C2 done: M={ci_M['mean']:.5f} [{ci_M['lo']:.5f},{ci_M['hi']:.5f}] -> {out}; frac M>0 {frac_pos:.3f}")


if __name__ == "__main__":
    main()

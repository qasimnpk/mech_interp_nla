"""K1 — K-way alternative ranking on the existing deterministic-swap claims (PLAN.md round 4, desk-designed; AR only; ~45 min).

  uv run python overnight/k1_kway.py         # re-entrant; rows scored in `row` order until the 45-min cap

What K1 measures: the reconstructor's preference for the word the AV originally wrote over 7 matched alternatives differing in that
one word (not a truth label); `in_full_prefix` is a string proxy for grounding. Outputs k1_rows.csv, k1_texts.jsonl, k1_summary.md,
k1_review_blind.csv / k1_review_key.csv (20 rows), k1_settings.json, k1_progress.json.
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

STAGE, PFX = "K1", "k1"
K_ALT = 7
MIN_ROWS = 80
NUM_RE = re.compile(r"^\d[\d.,]*$")
PUNCT = ".,;:!?\"'()[]"
F = {k: L.OVERNIGHT / f"{PFX}_{k}" for k in ["rows.csv", "texts.jsonl", "summary.md", "review_blind.csv", "review_key.csv"]}


def load_rows() -> pd.DataFrame:
    t2b = pd.read_csv(L.OVERNIGHT / "t2b_claims.csv", keep_default_na=False)
    det = t2b[t2b.edit_type == "corrupt_det"].copy()
    p = pd.read_csv(L.REPO_ROOT / "notes" / "t2b_in_full_prefix.csv"); p = p[p.edit_type == "corrupt_det"][["row", "in_full_prefix"]]
    det = det.merge(p, on="row", how="left"); assert det.in_full_prefix.notna().all() and len(det) == 393
    det["is_last"] = det.is_last.astype(str) == "True"
    det["core_orig"] = det.word_orig.map(lambda w: str(w).strip(PUNCT))
    det["slot_type"] = det.core_orig.map(lambda w: "detail" if NUM_RE.match(w) else "entity")
    det["stratum"] = np.where(det.is_last, "positive_control_last", np.where(det.in_full_prefix, "nonlast_in_prefix", "nonlast_not_in_prefix"))
    return det.sort_values("row").reset_index(drop=True)


def number_alts(core: str) -> list[str]:
    """{n+1, n+7, n+13, 2n, 3n, n+100, n−1 (n+2 if n = 0)} in the same digit format; decimals perturb the integer part."""
    has_comma = "," in core; dec = core.split(".")[1] if "." in core else None
    ip = core.replace(",", "").split(".")[0]; n = int(ip)
    vals = [n + 1, n + 7, n + 13, 2 * n, 3 * n, n + 100, (n - 1) if n != 0 else n + 2]
    out = []
    for v in vals:
        s = f"{v:,}" if has_comma else str(v)
        if dec is not None:
            s = f"{s}.{dec}"
        out.append(s)
    return out


def main():
    prog = R.Progress(STAGE)
    S = L.Settings(PFX, k_alt=K_ALT, min_rows=MIN_ROWS, seed="6000 + row", name_pool="word_orig of corrupt_det name rows of OTHER explanations (t2b_claims), excluding words in this row's prefix or explanation and word_corrupt",
                   number_rule="{n+1, n+7, n+13, 2n, 3n, n+100, n-1 (n+2 if n=0)} same digit format; decimals perturb the integer part",
                   replace_rule="first whole-word occurrence of word_orig (punctuation-stripped core) in the claim; claim substituted at its span in the explanation; assert exactly one word differs between any two of the 8 texts",
                   original_cache="s2_claims.cos_z reused iff 20 recomputed originals agree to 1e-6", bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")
    det = load_rows()
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False).set_index("row")
    expl = {r["stim_idx"]: r for r in R.read_jsonl(L.OVERNIGHT / "explanations.jsonl")}
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(L.snapshot(L.TARGET)); ds = R.wikitext_train()
    prefixes = {}
    for i in sorted(set(det.stim_idx)):
        prefixes[i], _ = R.stimulus_prefix(tok, ds, int(st.doc_idx[i]), int(st.pos[i]))
    name_rows = det[det.slot_type == "entity"]
    done = {}
    if F["rows.csv"].exists():
        for r in pd.read_csv(F["rows.csv"], keep_default_na=False).to_dict("records"):
            done[int(r["row"])] = r
    prog.set_phase("ar")
    ar = L.AR()
    # ---- original cache check on 20 rows
    cache_ok = prog.d.get("original_cache_ok")
    if cache_ok is None:
        devs = []
        for r in det.head(20).itertuples():
            z = expl[int(r.stim_idx)]["explanation"]; c = L.cos(ar.predict(z).numpy(), h20[int(r.stim_idx)])
            devs.append(abs(c - float(s2.loc[int(r.row), "cos_z"])))
        cache_ok = bool(max(devs) < 1e-6); prog.d["original_cache_ok"] = cache_ok; prog.d["original_cache_max_dev"] = float(max(devs)); prog.tick()
        L.log(f"K1 original cache check: max |dev| {max(devs):.2e} -> reuse s2 cos_z = {cache_ok}")
    orig_cache = {}
    t0 = time.time(); n0 = ar.n_forward
    for r in det.itertuples():
        row = int(r.row)
        if row in done:
            continue
        if prog.over_cap() or prog.over_failures():
            prog.incomplete("rows", [int(x) for x in det.row if int(x) not in done]); break
        i = int(r.stim_idx); E = expl[i]["explanation"]; claim = str(r.claim); core = r.core_orig
        rec = {"row": row, "stim_idx": i, "claim_idx": int(r.claim_idx), "n_claims": int(r.n_claims), "is_last": bool(r.is_last), "in_full_prefix": bool(r.in_full_prefix),
               "stratum": r.stratum, "slot_type": r.slot_type, "word_orig": r.word_orig, "core_orig": core, "word_corrupt": r.word_corrupt, "claim": claim, "error": "", "pool_short": False}
        try:
            a, b, dup = R.sentence_span(E, claim); assert a >= 0, "claim not found in explanation"
            rec["span_a"], rec["span_b"], rec["dup_sentence"] = a, b, dup
            m = re.search(r"(?<![\w])" + re.escape(core) + r"(?![\w])", claim); assert m, "word_orig not found in claim"
            rng = np.random.default_rng(6000 + row)
            if r.slot_type == "detail":
                alts, seen = [], {core}
                for a_ in number_alts(core):  # duplicates (e.g. 2n = 3n = 0 when n = 0) and the original are dropped; flagged as pool_short
                    if a_ not in seen:
                        alts.append(a_); seen.add(a_)
                rec["pool_short"] = len(alts) < K_ALT
            else:
                excl = set(w.strip(PUNCT) for w in prefixes[i].split()) | set(w.strip(PUNCT) for w in E.split()) | {str(r.word_corrupt).strip(PUNCT), core}
                pool = sorted({w for w in name_rows[name_rows.stim_idx != i].core_orig if w and w not in excl})
                k = min(K_ALT, len(pool)); rec["pool_short"] = k < K_ALT; rec["pool_size"] = len(pool)
                alts = [pool[j] for j in rng.choice(len(pool), size=k, replace=False)]
            texts = {"orig": E}
            for j, alt in enumerate(alts):
                new_claim = claim[:m.start()] + alt + claim[m.end():]
                texts[f"alt{j}"] = R.substitute(E, a, b, new_claim)
            ws = {k: v.split() for k, v in texts.items()}
            keys = list(texts)
            for x in range(len(keys)):
                for y in range(x + 1, len(keys)):
                    wa, wb = ws[keys[x]], ws[keys[y]]
                    assert len(wa) == len(wb) and sum(p != q for p, q in zip(wa, wb)) == 1, f"texts {keys[x]} / {keys[y]} differ in != 1 word"
            cos = {}
            for k, txt in texts.items():
                if k == "orig" and cache_ok:
                    cos[k] = float(s2.loc[row, "cos_z"])
                else:
                    if k == "orig" and i in orig_cache:
                        cos[k] = orig_cache[i]
                    else:
                        cos[k] = L.cos(ar.predict(txt).numpy(), h20[i])
                        if k == "orig":
                            orig_cache[i] = cos[k]
            R.append_jsonl(F["texts.jsonl"], {"row": row, "alts": alts, "texts": texts, "cos": cos})
            altc = [cos[f"alt{j}"] for j in range(len(alts))]
            rank = 1 + sum(c > cos["orig"] for c in altc)
            rec.update({"n_alts": len(alts), "alts": "|".join(alts), "cos_orig": cos["orig"], "cos_alts_mean": float(np.mean(altc)), "cos_alts_max": float(max(altc)), "cos_alts_min": float(min(altc)),
                        "rank": rank, "top1": float(rank == 1), "rr": 1.0 / rank, "gap": cos["orig"] - float(np.mean(altc)), "gap_max": cos["orig"] - float(max(altc)), "spread": float(max(altc + [cos["orig"]]) - min(altc + [cos["orig"]]))})
        except Exception:
            rec["error"] = traceback.format_exc()[-400:]; prog.fail(f"row {row}: {rec['error'][-200:]}")
        pd.DataFrame([rec]).to_csv(F["rows.csv"], mode="a", header=not F["rows.csv"].exists(), index=False)
        done[row] = rec
        if len(done) % 50 == 0:
            prog.completed("rows", len(done)); L.log(f"K1: {len(done)}/{len(det)} rows, {(time.time()-t0)/max(1, ar.n_forward-n0):.2f} s/forward")
    prog.completed("rows", len(done)); ar.free()
    # ---------------- statistics
    df = pd.read_csv(F["rows.csv"], keep_default_na=False)
    ok = df[df.error == ""].copy()
    for c in ["top1", "rr", "gap", "gap_max", "spread", "cos_orig", "cos_alts_mean", "rank"]:
        ok[c] = ok[c].astype(float)
    ok["is_last"] = ok.is_last.astype(str) == "True"; ok["in_full_prefix"] = ok.in_full_prefix.astype(str) == "True"
    g = ok[ok.stratum == "nonlast_in_prefix"]
    ci = R.ci(g.top1 - 0.125, g.stim_idx) if len(g) else {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
    out = R.outcome(ci, min_n=MIN_ROWS)
    def strat(name):
        s = ok[ok.stratum == name]
        if not len(s):
            return f"{name}: n=0"
        t = R.ci(s.top1 - 0.125, s.stim_idx); gp = R.ci(s.gap, s.stim_idx)
        return f"{name}: n={len(s)} top1−0.125 {R.fmt_ci(t, 4)} (top1 {s.top1.mean():.3f}) MRR {s.rr.mean():.3f} gap {R.fmt_ci(gp, 5)} frac gap>0 {(s.gap > 0).mean():.3f}"
    obs = "; ".join(strat(n) for n in ["nonlast_in_prefix", "nonlast_not_in_prefix", "positive_control_last"]) + f"; rows completed {len(ok)}/{len(det)} (errors {int((df.error != '').sum())}); original cache reused {cache_ok}"
    kill = L.append_disconfirmation("K1", "K1", "CI95 (cluster by explanation) of (top-1 rate − 0.125) on non-last in_full_prefix rows (n=107) ≤ 0 → MET; > 0 → NOT MET; straddles or < 80 rows completed → INCONCLUSIVE", obs, out,
                                    "preference for the AV's original word among 8 one-word variants; not a truth label; in_full_prefix is a string proxy")
    H = ["| stratum | n | n_expl | top1 | top1−0.125 CI | MRR | mean gap | gap CI | frac gap>0 | mean gap_max | mean spread |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    lines = ["# K1 summary — K-way alternative ranking on deterministic-swap claims (AR only)", "", f"git {L.git_hash()[:8]}; settings in k1_settings.json; progress in k1_progress.json", "",
             "## Kill test", "", f"- {kill}", "", "## Counts", "",
             f"- rows {len(det)} (non-last in-prefix {int((det.stratum == 'nonlast_in_prefix').sum())}, non-last not-in-prefix {int((det.stratum == 'nonlast_not_in_prefix').sum())}, last {int((det.stratum == 'positive_control_last').sum())}); completed {len(ok)}; errors {int((df.error != '').sum())}; pool_short {int(ok.pool_short.astype(str).eq('True').sum())}; dup_sentence {int(ok.dup_sentence.astype(str).eq('True').sum()) if 'dup_sentence' in ok else 0}",
             f"- slot type: non-last entity {int(((~ok.is_last) & (ok.slot_type == 'entity')).sum())}, non-last detail {int(((~ok.is_last) & (ok.slot_type == 'detail')).sum())}",
             f"- original cos cache: reused s2 cos_z = {cache_ok} (max |dev| on 20 rows {prog.d.get('original_cache_max_dev'):.2e})",
             "", "## Per stratum (cluster by explanation)", ""] + H
    for name in ["nonlast_in_prefix", "nonlast_not_in_prefix", "positive_control_last"]:
        s = ok[ok.stratum == name]
        if len(s):
            t = R.ci(s.top1 - 0.125, s.stim_idx); gp = R.ci(s.gap, s.stim_idx)
            lines.append(f"| {name} | {len(s)} | {s.stim_idx.nunique()} | {s.top1.mean():.3f} | [{t['lo']:.4f},{t['hi']:.4f}] | {s.rr.mean():.3f} | {gp['mean']:.5f} | [{gp['lo']:.5f},{gp['hi']:.5f}] | {(s.gap > 0).mean():.3f} | {s.gap_max.mean():.5f} | {s.spread.mean():.5f} |")
    lines += ["", "## 2×2 (non-last rows): in_full_prefix × slot type", "", "| in_full_prefix \\ slot type | entity | detail |", "|---|---|---|"]
    nl = ok[~ok.is_last]
    for ip in [True, False]:
        cells = []
        for stp in ["entity", "detail"]:
            s = nl[(nl.in_full_prefix == ip) & (nl.slot_type == stp)]
            if len(s):
                t = R.ci(s.top1, s.stim_idx); gp = R.ci(s.gap, s.stim_idx); cells.append(f"n={len(s)} top1 {t['mean']:.3f} [{t['lo']:.3f},{t['hi']:.3f}] gap {gp['mean']:.5f} [{gp['lo']:.5f},{gp['hi']:.5f}]")
            else:
                cells.append("n=0")
        lines.append(f"| {ip} | {cells[0]} | {cells[1]} |")
    lines += ["", "Distributions for the four cells (gap):", ""] + R.DIST_HEADER
    for ip in [True, False]:
        for stp in ["entity", "detail"]:
            s = nl[(nl.in_full_prefix == ip) & (nl.slot_type == stp)]; lines.append(R.dist_row(f"gap / in_full_prefix={ip} × {stp}", s.gap))
    lines += ["", "## Distributions", ""] + R.DIST_HEADER
    for name in ["nonlast_in_prefix", "nonlast_not_in_prefix", "positive_control_last"]:
        s = ok[ok.stratum == name]
        for c in ["gap", "gap_max", "spread", "rank", "cos_orig", "cos_alts_mean"]:
            lines.append(R.dist_row(f"{c} / {name}", s[c]))
    lines += ["", "## Rank histogram of the original among 8 (per stratum)", ""]
    for name in ["nonlast_in_prefix", "nonlast_not_in_prefix", "positive_control_last"]:
        s = ok[ok.stratum == name]; lines.append(f"- {name}: " + ", ".join(f"rank {int(k)}: {v}" for k, v in sorted(s["rank"].value_counts().items())))
    # examples + review sheets (20 rows)
    lines += ["", "## 5 fixed verbatim examples (seed 0; non-last in-prefix rows)", ""]
    texts = {t["row"]: t for t in R.read_jsonl(F["texts.jsonl"])}
    rng = np.random.default_rng(0)
    if len(g):
        for row in rng.choice(g.row.values, size=min(5, len(g)), replace=False):
            r = ok[ok.row == row].iloc[0]; t = texts[int(row)]
            lines += [f"### row {row} (stim {r.stim_idx}, claim {r.claim_idx}/{r.n_claims}, {r.slot_type}, word_orig {r.word_orig!r})", "",
                      f"- prefix tail (last 400 chars): {prefixes[int(r.stim_idx)][-400:]!r}", f"- claim: {r.claim!r}",
                      f"- cos orig {t['cos']['orig']:.5f}; alternatives: " + ", ".join(f"{a} {t['cos'][f'alt{j}']:.5f}" for j, a in enumerate(t["alts"])), f"- rank {int(r['rank'])}, gap {r.gap:.5f}", ""]
    blind, key = [], []
    pick = rng.choice(ok.row.values, size=min(20, len(ok)), replace=False)
    for row in pick:
        r = ok[ok.row == row].iloc[0]; t = texts[int(row)]
        words = [r.core_orig] + list(t["alts"]); order = np.random.default_rng(int(row)).permutation(len(words))
        b = {"item_id": f"k1_row_{row}", "item_type": "k1_row", "context_id": int(r.stim_idx), "prefix_text": prefixes[int(r.stim_idx)], "sentence": r.claim, "candidate_words_shuffled": "|".join(words[j] for j in order),
             "transform": "one-word alternatives (which of the words is grounded in the prefix?)", "human_label": "", "human_note": ""}
        blind.append(b)
        key.append({**b, "word_orig": r.word_orig, "in_full_prefix": r.in_full_prefix, "is_last": r.is_last, "stratum": r.stratum, "rank": r["rank"], "gap": r.gap,
                    "cos_by_word": json.dumps({r.core_orig: t["cos"]["orig"], **{a: t["cos"][f"alt{j}"] for j, a in enumerate(t["alts"])}})})
    pd.DataFrame(blind).to_csv(F["review_blind.csv"], index=False); pd.DataFrame(key).to_csv(F["review_key.csv"], index=False)
    lines += ["", f"- review sheets: k1_review_blind.csv (20 rows, seed 0) — open first; k1_review_key.csv after", ""]
    F["summary.md"].write_text("\n".join(lines))
    prog.set_phase("done"); S.finish(progress=prog.d, kill=ci, outcome=out, rows_completed=len(ok))
    L.log(f"K1 done: {out}; {len(ok)} rows; {prog.minutes:.1f} min")


if __name__ == "__main__":
    main()

"""X3 — does the dominant local snippet suppress factual discrimination? (PLAN.md round 3c; AR only + TARGET judge).

  uv run python overnight/x3_snippet.py

Rows: accepted S3 triples (corrupt and paraphrase both edit_ok; all are evaluation claims) whose claim is not the last
claim (claim_idx < n_claims − 1) and whose changed words do not occur in any other claim of the explanation. Changed
words = (words of the original claim not in the corruption) ∪ (words of the corruption not in the original), compared
lower-cased with surrounding punctuation stripped; a row is excluded if any changed word occurs as a whole word in any
other claim (the snippet included). For each row and condition c: T_c = explanation with the original claim, F_c = with
the corruption, P_c = with the paraphrase; claims are joined by one space (S3's z_joined convention).
Conditions: (1) full explanation; (2) local snippet removed = the last claim deleted; (3) equal-length non-local removal
= a random contiguous span of words, of the snippet's word count, deleted from the claims that are neither the tested
claim nor the snippet (rng seed 1000 + row; the span is drawn on the word sequence of the full explanation with the tested
claim and the snippet protected, may cross a boundary between two adjacent unprotected claims, and is applied at claim
level so that the same deletion is used for T, F and P). Feasibility gate: rows with ≥ snippet-word-count words in the
unprotected claims (reported), and rows with a valid contiguous span (reported); if < 100 rows, condition (3) runs on
what is eligible and I is reported INCONCLUSIVE with n.
G_c = cos(AR(T_c), h) − cos(AR(F_c), h); I = (G_2 − G_1) − (G_3 − G_1) = G_2 − G_3.
Kill X3 (pre-registered): CI (cluster bootstrap by explanation, 1000 draws, seed 0) of mean I ≤ 0 → MET.
Validity subset (reported, not a filter): TARGET as judge (chat template, greedy, ≤ 4 new tokens) on the document
prefix tokens 0..pos: original claim supported (Yes/No) and corruption contradicts (Yes/No); raw outputs stored.
Models: AR alone (scoring) → free → TARGET alone (judge).
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
from overnight.t1_arprobe import load_triples, auroc  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

MAX_LEN = 512
N_BOOT, SEED = 1000, 0
MIN_ELIGIBLE = 100
JUDGE_MAX_NEW = 4
JUDGE_SUPPORT = ("Here is the beginning of a document:\n<passage>\n{prefix}\n</passage>\n\nHere is a claim about this document — about its content, its format, or what is likely to come next:\n<claim>{claim}</claim>\n\n"
                 "Is the claim supported by the document? Answer with exactly one word: Yes or No.")
JUDGE_CONTRA = ("Here is the beginning of a document:\n<passage>\n{prefix}\n</passage>\n\nHere is a claim about this document — about its content, its format, or what is likely to come next:\n<claim>{claim}</claim>\n\n"
                "Does the claim contradict the document? Answer with exactly one word: Yes or No.")
FIXED_EXAMPLES = 5


def words_norm(text: str) -> list[str]:
    return [w.strip(".,;:!?\"'()[]{}“”‘’") .lower() for w in text.split()]


def changed_words(a: str, b: str) -> set[str]:
    wa, wb = set(words_norm(a)), set(words_norm(b))
    return {w for w in (wa ^ wb) if w}


def occurs(word: str, claim: str) -> bool:
    return word in set(words_norm(claim))


def judge_parse(raw: str) -> str:
    m = re.search(r"\b(yes|no)\b", (raw or "").strip().lower())
    return m.group(1) if m else "unparsed"


def build_row(r, claims: list[str], rng) -> dict:
    """Deletion plan for condition 3 as per-claim word ranges; returns eligibility info."""
    ci, n = int(r.claim_idx), len(claims)
    snip_k = len(claims[-1].split())
    protected = {ci, n - 1}
    seq = []  # (claim_idx, word_idx) for every word in order
    for k, c in enumerate(claims):
        seq += [(k, w) for w in range(len(c.split()))]
    unprot = [k for k, (c, _) in enumerate(seq) if c not in protected]
    avail = len(unprot)
    starts = [s for s in range(len(seq) - snip_k + 1) if all(seq[s + t][0] not in protected for t in range(snip_k))]
    plan = None
    if starts:
        s = int(starts[int(rng.integers(0, len(starts)))])
        plan = {}
        for t in range(snip_k):
            c, w = seq[s + t]; plan.setdefault(c, []).append(w)
    return {"snippet_words": snip_k, "available_words": avail, "avail_ok": avail >= snip_k, "span_ok": plan is not None, "span_plan": plan, "n_starts": len(starts)}


def compose(claims: list[str], ci: int, tested_text: str, cond: int, plan) -> str:
    cs = list(claims); cs[ci] = tested_text
    if cond == 2:
        cs = cs[:-1]
    if cond == 3:
        out = []
        for k, c in enumerate(cs):
            ws = c.split()
            if plan and k in plan:
                drop = set(plan[k]); ws = [w for i, w in enumerate(ws) if i not in drop]
            out.append(" ".join(ws))
        cs = out
    return " ".join(x for x in cs if x)


def main():
    S = L.Settings("x3", judge_prompts={"support": JUDGE_SUPPORT, "contradict": JUDGE_CONTRA}, judge_max_new_tokens=JUDGE_MAX_NEW, judge_decoding="greedy, chat template",
                   row_rule="accepted S3 triples (edit_ok), claim_idx < n_claims-1, no changed word (symmetric word-set difference orig vs corrupt, lower-cased, punctuation-stripped) occurs in any other claim",
                   join="claims joined by one space (S3 z_joined convention)", cond3="random contiguous span of snippet word count over the non-tested non-snippet claims, rng 1000+row, applied at claim level for T/F/P",
                   min_eligible=MIN_ELIGIBLE, n_boot=N_BOOT, seed=SEED, kill="CI (cluster by explanation) of mean I = G_2 − G_3 ≤ 0 → MET; INCONCLUSIVE if eligible rows for condition 3 < 100 or the CI straddles 0")
    timings = {}
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    tri = load_triples()  # 490 accepted, all eval
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    claims_by_stim = {i: list(g.sort_values("claim_idx").claim) for i, g in s2.groupby("stim_idx")}
    rows = []; n_last = n_repeat = 0
    for r in tri.itertuples():
        claims = claims_by_stim[int(r.stim_idx)]; assert len(claims) == int(r.n_claims) and claims[int(r.claim_idx)] == r.claim
        if int(r.claim_idx) >= int(r.n_claims) - 1:
            n_last += 1; continue
        cw = changed_words(r.claim, r.corrupt)
        others = [c for k, c in enumerate(claims) if k != int(r.claim_idx)]
        if any(occurs(w, c) for w in cw for c in others):
            n_repeat += 1; continue
        info = build_row(r, claims, np.random.default_rng(1000 + int(r.row)))
        rows.append({"row": int(r.row), "stim_idx": int(r.stim_idx), "claim_idx": int(r.claim_idx), "n_claims": int(r.n_claims), "claim": r.claim, "corrupt": r.corrupt, "paraphrase": r.paraphrase,
                     "changed_words": json.dumps(sorted(cw)), **{k: (json.dumps(v) if k == "span_plan" else v) for k, v in info.items()}, "_plan": info["span_plan"], "_claims": claims, "error": ""})
    n_avail = sum(r["avail_ok"] for r in rows); n_span = sum(r["span_ok"] for r in rows)
    L.log(f"rows: {len(tri)} accepted → {len(rows)} eligible (excluded last-claim {n_last}, repeated changed word {n_repeat}); condition-3 feasibility: available≥snippet {n_avail}, valid span {n_span}")
    S.update(n_accepted=len(tri), n_rows=len(rows), n_excluded_last=n_last, n_excluded_repeat=n_repeat, n_cond3_avail=n_avail, n_cond3_span=n_span)
    gate_ok = n_span >= MIN_ELIGIBLE
    L.append_disconfirmation("X3", "X3-gate", f"feasibility: rows with a valid equal-length non-local deletion (condition 3) ≥ {MIN_ELIGIBLE}",
                             f"eligible rows {len(rows)} (of 490 accepted; last-claim {n_last}, repeated changed word {n_repeat} excluded); available words ≥ snippet words: {n_avail}; valid contiguous span: {n_span}",
                             "PASS" if gate_ok else "FAIL", "if FAIL, condition 3 runs on the eligible rows and I is reported INCONCLUSIVE with n")

    # ---------------- AR scoring
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0
    cache = {}

    def score(text, i):
        k = (text, i)
        if k not in cache:
            cache[k] = L.cos(ar.predict(text).numpy(), h20[i])
        return cache[k]
    t0 = time.time()
    for n, r in enumerate(rows):
        i = r["stim_idx"]; ci = r["claim_idx"]; cl = r["_claims"]
        try:
            for cond in [1, 2, 3]:
                if cond == 3 and not r["span_ok"]:
                    for v in "TFP":
                        r[f"cos_{v}_{cond}"] = np.nan
                    continue
                for v, txt in [("T", r["claim"]), ("F", r["corrupt"]), ("P", r["paraphrase"])]:
                    z = compose(cl, ci, txt, cond, r["_plan"]); r[f"text_{v}_{cond}"] = z; r[f"cos_{v}_{cond}"] = score(z, i)
            for cond in [1, 2, 3]:
                r[f"G_{cond}"] = r[f"cos_T_{cond}"] - r[f"cos_F_{cond}"]; r[f"Pm_{cond}"] = r[f"cos_T_{cond}"] - r[f"cos_P_{cond}"]; r[f"AmP_{cond}"] = r[f"G_{cond}"] - r[f"Pm_{cond}"]
            r["I"] = r["G_2"] - r["G_3"]; r["G2_minus_G1"] = r["G_2"] - r["G_1"]; r["G3_minus_G1"] = r["G_3"] - r["G_1"]
        except Exception:
            r["error"] = traceback.format_exc(); L.log(f"X3 AR FAILED on row {r['row']}")
        if n % 50 == 49:
            L.log(f"AR {n + 1}/{len(rows)} rows, forwards {ar.n_forward} ({(time.time() - t0) / max(1, ar.n_forward):.2f} s each)")
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward); timings["n_ar_forward"] = ar.n_forward
    ar.free()

    # ---------------- kill statistic (before the judge)
    def strip_row(r):
        return {k: v for k, v in r.items() if not k.startswith("_")}
    df = pd.DataFrame([strip_row(r) for r in rows]); df.to_csv(L.OVERNIGHT / "x3_scores.csv", index=False)
    ok = df[df.error == ""].reset_index(drop=True); ok3 = ok[ok.span_ok.astype(bool)].reset_index(drop=True)

    def ci(v, c):
        return L.cluster_bootstrap_mean(np.asarray(v, float), c, n_boot=N_BOOT, seed=SEED)

    def fm(c, d=5):
        return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"

    def block(e):
        d = {"I": ci(e.I, e.stim_idx), "G2_minus_G1": ci(e.G2_minus_G1, e.stim_idx), "G3_minus_G1": ci(e.G3_minus_G1, e.stim_idx)}
        for c in [1, 2, 3]:
            d[f"G_{c}"] = ci(e[f"G_{c}"], e.stim_idx); d[f"Pm_{c}"] = ci(e[f"Pm_{c}"], e.stim_idx); d[f"AmP_{c}"] = ci(e[f"AmP_{c}"], e.stim_idx)
            d[f"cosT_{c}"] = ci(e[f"cos_T_{c}"], e.stim_idx); d[f"frac_G_{c}_pos"] = float((e[f"G_{c}"] > 0).mean())
            d[f"auroc_{c}"] = auroc(e[f"G_{c}"].dropna(), e[f"Pm_{c}"].dropna())
        d["n"] = int(len(e)); d["n_expl"] = int(e.stim_idx.nunique())
        return d
    B_all = block(ok3)
    out = L.outcome_ci_at_or_below(B_all["I"], 0.0, min_n=MIN_ELIGIBLE)
    if not gate_ok:
        out = "INCONCLUSIVE"
    L.append_disconfirmation("X3", "X3", "CI (cluster bootstrap by explanation) of mean I = (G_2 − G_1) − (G_3 − G_1), G_c = cos(AR(T_c),h) − cos(AR(F_c),h) ≤ 0; INCONCLUSIVE if condition-3 rows < 100",
                             f"mean I={fm(B_all['I'])} n={B_all['n']} n_expl={B_all['n_expl']}; G_1 {fm(B_all['G_1'])} G_2 {fm(B_all['G_2'])} G_3 {fm(B_all['G_3'])}; G_2−G_1 {fm(B_all['G2_minus_G1'])} G_3−G_1 {fm(B_all['G3_minus_G1'])}; "
                             f"A−P margins: c1 {B_all['AmP_1']['mean']:.5f} c2 {B_all['AmP_2']['mean']:.5f} c3 {B_all['AmP_3']['mean']:.5f}; AUROC(Δcorrupt vs Δparaphrase) c1 {B_all['auroc_1']:.4f} c2 {B_all['auroc_2']:.4f} c3 {B_all['auroc_3']:.4f}; "
                             f"mean cos(T) c1 {B_all['cosT_1']['mean']:.4f} c2 {B_all['cosT_2']['mean']:.4f} c3 {B_all['cosT_3']['mean']:.4f}; eligible {len(rows)} (cond-3 valid {n_span})",
                             out, "MET would mean removing the snippet does not improve factual discrimination more than removing comparable other text; this is a property of the frozen scorer, not of training")

    # ---------------- judge (TARGET)
    from datasets import load_dataset
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0
    prefix_cache = {}
    jrows = []; t0 = time.time()
    with open(L.OVERNIGHT / "x3_judge.jsonl", "w") as f:
        for n, r in enumerate(rows):
            i = r["stim_idx"]
            if i not in prefix_cache:
                ids = tgt.tok(ds[int(st.doc_idx[i])]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
                assert len(ids) == int(st.seq_len[i]); prefix_cache[i] = tgt.tok.decode(ids[: int(st.pos[i]) + 1])
            rec = {"row": r["row"], "stim_idx": i, "claim": r["claim"], "corrupt": r["corrupt"], "error": ""}
            try:
                rec["judge_support_raw"] = tgt.chat_generate(JUDGE_SUPPORT.format(prefix=prefix_cache[i], claim=r["claim"]), JUDGE_MAX_NEW)
                rec["judge_contra_raw"] = tgt.chat_generate(JUDGE_CONTRA.format(prefix=prefix_cache[i], claim=r["corrupt"]), JUDGE_MAX_NEW)
                rec["support"] = judge_parse(rec["judge_support_raw"]); rec["contradict"] = judge_parse(rec["judge_contra_raw"])
                rec["judge_valid"] = rec["support"] == "yes" and rec["contradict"] == "yes"
            except Exception:
                rec["error"] = traceback.format_exc(); rec["judge_valid"] = False; L.log(f"judge FAILED on row {r['row']}")
            jrows.append(rec); f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if n % 50 == 49:
                L.log(f"judge {n + 1}/{len(rows)} ({(time.time() - t0) / (2 * (n + 1)):.2f} s/gen)")
    timings["judge_s_per_gen"] = (time.time() - t0) / max(1, 2 * len(rows))
    tgt.free()
    jd = pd.DataFrame(jrows)
    df = df.merge(jd[["row", "support", "contradict", "judge_valid"]], on="row", how="left"); df.to_csv(L.OVERNIGHT / "x3_scores.csv", index=False)
    ok = df[df.error == ""].reset_index(drop=True); ok3 = ok[ok.span_ok.astype(bool)].reset_index(drop=True)
    val = ok3[ok3.judge_valid.astype(bool)].reset_index(drop=True)
    B_val = block(val) if len(val) else None
    B_full = block(ok.assign(**{c: ok[c] for c in ok.columns}))  # all rows incl. those without condition 3 (NaN-robust means for c1/c2)

    def tbl(B, name):
        ls = [f"### {name} (n={B['n']} rows, {B['n_expl']} explanations)", "", "| condition | G = cos(T) − cos(F) [CI] | frac G>0 | P-margin cos(T) − cos(P) | A − P | AUROC(Δcorrupt vs Δparaphrase) | mean cos(T) |", "|---|---|---|---|---|---|---|"]
        for c, nm in [(1, "1 full explanation"), (2, "2 snippet (last claim) removed"), (3, "3 equal-length non-local removal")]:
            ls.append(f"| {nm} | {fm(B[f'G_{c}'])} | {B[f'frac_G_{c}_pos']:.3f} | {fm(B[f'Pm_{c}'])} | {fm(B[f'AmP_{c}'])} | {B[f'auroc_{c}']:.4f} | {B[f'cosT_{c}']['mean']:.4f} |")
        ls += ["", f"- G_2 − G_1: {fm(B['G2_minus_G1'])}; G_3 − G_1: {fm(B['G3_minus_G1'])}; **I = G_2 − G_3: {fm(B['I'])}**", ""]
        return ls
    lines = ["# X3 summary — does the dominant local snippet suppress factual discrimination? (AR only; TARGET judge)", "",
             f"git {L.git_hash()[:8]}; settings in x3_settings.json; rows in x3_scores.csv; judge outputs in x3_judge.jsonl", "",
             f"- accepted S3 triples 490 → eligible {len(rows)} (excluded: last-claim {n_last}, changed word repeated in another claim {n_repeat}); condition-3 feasibility: available words ≥ snippet words {n_avail}, valid contiguous span {n_span} (gate ≥ {MIN_ELIGIBLE}: {'PASS' if gate_ok else 'FAIL'})",
             f"- AR forwards {timings['n_ar_forward']} ({timings['ar_s_per_score']:.2f} s each); judge generations {2 * len(rows)} ({timings['judge_s_per_gen']:.2f} s each); errors {int((df.error != '').sum())}",
             f"- snippet word count: mean {ok.snippet_words.mean():.1f} (min {ok.snippet_words.min()}, max {ok.snippet_words.max()}); condition-3 candidate starts per row: mean {ok.n_starts.mean():.1f}",
             f"- judge: support yes {int((jd.support == 'yes').sum())} / no {int((jd.support == 'no').sum())} / unparsed {int((jd.support == 'unparsed').sum())}; contradict yes {int((jd.contradict == 'yes').sum())} / no {int((jd.contradict == 'no').sum())} / unparsed {int((jd.contradict == 'unparsed').sum())}; judge-valid (both yes) {int(jd.judge_valid.sum())}",
             "", "## Kill X3", "", f"- mean I = G_2 − G_3 (rows with condition 3): {fm(B_all['I'])} n={B_all['n']} → **{out}**", ""]
    lines += tbl(B_all, "All rows with a valid condition 3 (primary)")
    lines += tbl(B_val, "Judge-valid subset (original supported AND corruption contradicts)") if B_val else ["### Judge-valid subset: 0 rows", ""]
    lines += tbl(B_full, "All eligible rows (conditions 1 and 2 on every row; condition 3 where valid)")
    lines += ["## Pre-committed reading key (from PLAN; the numbers decide)", "", "I > 0 with G_2 > G_1 → consistent with the snippet suppressing discrimination; G_2 ≈ G_3 > G_1 → general context/length effect; no change → snippet dominance does not explain the insensitivity; cos collapse under (2) → out-of-distribution caveat.", "",
              "## Five verbatim rows (first five eligible rows with condition 3)", ""]
    for r in [x for x in rows if x["span_ok"] and not x["error"]][:FIXED_EXAMPLES]:
        j = jd[jd.row == r["row"]].iloc[0]
        lines += [f"### row {r['row']} (stim {r['stim_idx']}, claim {r['claim_idx']}/{r['n_claims']}; changed words {r['changed_words']}; judge support={j.support} contradict={j.contradict})",
                  f"- original: {r['claim']}", f"- corrupt: {r['corrupt']}", f"- paraphrase: {r['paraphrase']}",
                  f"- snippet (last claim, {r['snippet_words']} words): {r['_claims'][-1]}",
                  f"- condition 3 text (T): {r['text_T_3']}",
                  f"- cos T/F/P: c1 {r['cos_T_1']:.4f}/{r['cos_F_1']:.4f}/{r['cos_P_1']:.4f}; c2 {r['cos_T_2']:.4f}/{r['cos_F_2']:.4f}/{r['cos_P_2']:.4f}; c3 {r['cos_T_3']:.4f}/{r['cos_F_3']:.4f}/{r['cos_P_3']:.4f}; G_1 {r['G_1']:+.5f} G_2 {r['G_2']:+.5f} G_3 {r['G_3']:+.5f} I {r['I']:+.5f}", ""]
    (L.OVERNIGHT / "x3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, gate={"ok": gate_ok, "n_span": n_span, "n_avail": n_avail}, kill_X3={"ci": B_all["I"], "outcome": out}, stats_all={k: v for k, v in B_all.items()},
             stats_judge_valid=({k: v for k, v in B_val.items()} if B_val else None), judge_counts={"valid": int(jd.judge_valid.sum()), "n": len(jd)})
    L.log(f"X3 done: I={fm(B_all['I'])} -> {out}; G1 {B_all['G_1']['mean']:.5f} G2 {B_all['G_2']['mean']:.5f} G3 {B_all['G_3']['mean']:.5f}")


if __name__ == "__main__":
    main()

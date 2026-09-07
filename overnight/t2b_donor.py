"""T2b — activation-dependence control for the round-3 claim-word readout (PLAN.md round 3b; AV forward only).

  uv run python overnight/t2b_donor.py

ACTIVATION-DEPENDENCE TEST, NOT A TRUTH TEST: the prefix and the "original" word are the AV's own greedy output.
Rows: every non-error single-word row of t2_claims.csv (298 LLM corrupt + 393 deterministic). Prefix and both candidate
words exactly as round-3 T2 (PREFILL_CLAIM + words of the claim before the changed word; ' ' + word, no space when the
changed word is the first word); asserted against word_orig / word_corrupt in the file. lp_* under own activation and
under no injection are REUSED from t2_claims.csv (not recomputed).
Donors: h_pos2 = same document, other position (acts_L20.npz['h20_pos2']) — near donor, the kill statistic;
        h_foreign = h20 of stimulus (i+100) mod 200 — far donor.
Scores: d = lp_orig - lp_corrupt under own (file), pos2, foreign, no-injection (file). Paired d_own - d_pos2 and
d_own - d_foreign; fraction d > 0 under each; splits LLM / deterministic / LLM last-claim-only; CIs cluster by explanation.
Source-support proxy: in_ctx = word_orig (stripped of leading/trailing non-alphanumerics) occurs as a whole word,
case-insensitive, in context_left_64 + token_str; in_ctx_right adds context_right_16.
Kill T2b (pre-registered): CI95 (cluster by explanation) of mean (d_own - d_pos2) <= 0 -> MET (all 691 rows; LLM and
deterministic splits reported in the same line).
Support sheet: 30 evaluation LLM-corrupt rows sampled with seed 0, label_supported left EMPTY for the human.
"""
from __future__ import annotations

import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix, PREFILL_CLAIM, single_word_diff  # noqa: E402  (import-safe, checked in U0)
from overnight.t1_arprobe import load_triples  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

N_BOOT, SEED = 1000, 0
SHEET_N, SHEET_SEED = 30, 0


def in_ctx(word: str, text: str) -> bool:
    w = re.sub(r"^[^A-Za-z0-9]+|[^A-Za-z0-9]+$", "", word or "")
    if not w:
        return False
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(w.lower()) + r"(?![A-Za-z0-9])", (text or "").lower()) is not None


def ci(vals, clusters):
    return L.cluster_bootstrap_mean(vals, clusters, n_boot=N_BOOT, seed=SEED)


def fm(c, d=4):
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"


def main():
    S = L.Settings("t2b", label="ACTIVATION-DEPENDENCE TEST, NOT A TRUTH TEST (prefix and original word are the AV's own greedy output)",
                   prefill_claim=PREFILL_CLAIM, donors={"pos2": "acts_L20.npz['h20_pos2'][stim_idx] (same document, other position)", "foreign": "acts_L20.npz['h20'][(stim_idx+100) % 200]"},
                   reused_from_t2_claims=["lp_orig", "lp_corrupt", "d_inj (=d_own)", "lp_orig_noinj", "lp_corrupt_noinj", "d_noinj"],
                   in_ctx_rule="word_orig stripped of leading/trailing non-alphanumerics; whole-word case-insensitive match in context_left_64 + token_str (in_ctx) and + context_right_16 (in_ctx_right)",
                   kill="CI95 (cluster bootstrap by explanation = stim_idx) of mean (d_own − d_pos2) over all non-error single-word rows ≤ 0 → MET", n_boot=N_BOOT, seed=SEED,
                   support_sheet={"n": SHEET_N, "seed": SHEET_SEED, "population": "evaluation rows, edit_type == corrupt (LLM), non-error single-word", "label_column": "label_supported (empty; human fills)"})
    timings = {}
    cl = pd.read_csv(L.OVERNIGHT / "t2_claims.csv", keep_default_na=False)
    cl = cl[(cl.error == "") & (cl.single_word.astype(str) == "True")].reset_index(drop=True)
    assert len(cl) == 691, len(cl)
    for c in ["lp_orig", "lp_corrupt", "d_inj", "lp_orig_noinj", "lp_corrupt_noinj", "d_noinj", "word_pos"]:
        cl[c] = pd.to_numeric(cl[c])
    cl["word_pos"] = cl.word_pos.astype(int); cl["stim_idx"] = cl.stim_idx.astype(int); cl["is_last"] = cl.is_last.astype(str) == "True"
    tri = load_triples().set_index("row")
    stim = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False).set_index("stim_idx")
    acts = np.load(L.OUT / "acts_L20.npz"); h20, hp2 = acts["h20"], acts["h20_pos2"]
    assert h20.shape == hp2.shape == (200, 3584)

    # reconstruct prefixes and assert against the file
    pre, lead = [], []
    for r in cl.itertuples():
        t = tri.loc[int(r.row)]
        txt = t.corrupt if r.edit_type == "corrupt" else t.corrupt_det
        sw = single_word_diff(t.claim, txt); assert sw is not None, r.row
        k, prefix, w_o, w_c = sw
        assert k == r.word_pos and w_o == r.word_orig and w_c == r.word_corrupt, (r.row, k, w_o, w_c, r.word_pos, r.word_orig, r.word_corrupt)
        pre.append(PREFILL_CLAIM + prefix); lead.append(" " if k > 0 else "")
    cl["prefill"] = pre; cl["lead"] = lead
    cl["split"] = [L.split_of(i) for i in cl.stim_idx]
    cl["foreign_stim_idx"] = (cl.stim_idx + 100) % 200
    cl["context_left_64"] = [stim.loc[i, "context_left_64"] for i in cl.stim_idx]; cl["token_str"] = [stim.loc[i, "token_str"] for i in cl.stim_idx]; cl["context_right_16"] = [stim.loc[i, "context_right_16"] for i in cl.stim_idx]
    cl["in_ctx"] = [in_ctx(w, a + b) for w, a, b in zip(cl.word_orig, cl.context_left_64, cl.token_str)]
    cl["in_ctx_right"] = [in_ctx(w, a + b + c) for w, a, b, c in zip(cl.word_orig, cl.context_left_64, cl.token_str, cl.context_right_16)]
    cl["corrupt_in_ctx"] = [in_ctx(w, a + b) for w, a, b in zip(cl.word_corrupt, cl.context_left_64, cl.token_str)]
    cl["claim"] = [tri.loc[int(r), "claim"] for r in cl.row]
    L.log(f"{len(cl)} rows; prefixes match the file; in_ctx {int(cl.in_ctx.sum())}, in_ctx_right {int(cl.in_ctx_right.sum())}, corrupt_in_ctx {int(cl.corrupt_in_ctx.sum())}")

    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    P = Prefix(av); S.update(prompt_tokens=int(P.ids.shape[1]), marker_pos=P.inj_pos)
    out_cols = {c: [] for c in ["lp_orig_pos2", "lp_corrupt_pos2", "lp_orig_foreign", "lp_corrupt_foreign", "t2b_error"]}
    t0 = time.time()
    for n, r in enumerate(cl.itertuples()):
        try:
            hp = torch.from_numpy(hp2[r.stim_idx]); hf = torch.from_numpy(h20[r.foreign_stim_idx])
            lo_p, _ = P.cont_logprob(hp, r.prefill, r.lead + r.word_orig); lc_p, _ = P.cont_logprob(hp, r.prefill, r.lead + r.word_corrupt)
            lo_f, _ = P.cont_logprob(hf, r.prefill, r.lead + r.word_orig); lc_f, _ = P.cont_logprob(hf, r.prefill, r.lead + r.word_corrupt)
            vals = [lo_p, lc_p, lo_f, lc_f, ""]
        except Exception:
            vals = [np.nan] * 4 + [traceback.format_exc()]; L.log(f"T2b FAILED on row {r.row}")
        for c, v in zip(out_cols, vals):
            out_cols[c].append(v)
        if n % 100 == 99:
            L.log(f"row {n + 1}/{len(cl)}, forwards {P.n_forward} ({(time.time() - t0) / max(1, P.n_forward):.2f}s each)")
    timings["av_s_per_forward"] = (time.time() - t0) / max(1, P.n_forward); timings["n_av_forward"] = P.n_forward
    av.free()
    for c, v in out_cols.items():
        cl[c] = v
    cl["d_own"] = cl.d_inj; cl["d_pos2"] = cl.lp_orig_pos2 - cl.lp_corrupt_pos2; cl["d_foreign"] = cl.lp_orig_foreign - cl.lp_corrupt_foreign
    cl["own_minus_pos2"] = cl.d_own - cl.d_pos2; cl["own_minus_foreign"] = cl.d_own - cl.d_foreign; cl["pos2_minus_noinj"] = cl.d_pos2 - cl.d_noinj; cl["foreign_minus_noinj"] = cl.d_foreign - cl.d_noinj
    cl.to_csv(L.OVERNIGHT / "t2b_claims.csv", index=False)
    ok = cl[cl.t2b_error == ""].reset_index(drop=True)

    # support sheet (human fills label_supported)
    pop = ok[(ok.split == "eval") & (ok.edit_type == "corrupt")]
    sheet = pop.sample(n=min(SHEET_N, len(pop)), random_state=SHEET_SEED).sort_values("row")
    sheet = sheet[["row", "stim_idx", "claim", "word_orig", "word_corrupt", "context_left_64", "token_str", "context_right_16", "d_own", "d_pos2", "d_foreign", "d_noinj"]].copy()
    sheet["label_supported"] = ""
    sheet.to_csv(L.OVERNIGHT / "t2b_support_sheet.csv", index=False)

    subsets = {"all": ok, "LLM corrupt": ok[ok.edit_type == "corrupt"], "deterministic": ok[ok.edit_type == "corrupt_det"], "LLM last claim only": ok[(ok.edit_type == "corrupt") & ok.is_last],
               "eval only": ok[ok.split == "eval"], "eval LLM corrupt": ok[(ok.split == "eval") & (ok.edit_type == "corrupt")]}

    def block(g):
        return {"n": int(len(g)), "n_expl": int(g.stim_idx.nunique()),
                "d_own": ci(g.d_own, g.stim_idx), "d_pos2": ci(g.d_pos2, g.stim_idx), "d_foreign": ci(g.d_foreign, g.stim_idx), "d_noinj": ci(g.d_noinj, g.stim_idx),
                "own_minus_pos2": ci(g.own_minus_pos2, g.stim_idx), "own_minus_foreign": ci(g.own_minus_foreign, g.stim_idx), "pos2_minus_noinj": ci(g.pos2_minus_noinj, g.stim_idx), "foreign_minus_noinj": ci(g.foreign_minus_noinj, g.stim_idx),
                "frac_own": float((g.d_own > 0).mean()), "frac_pos2": float((g.d_pos2 > 0).mean()), "frac_foreign": float((g.d_foreign > 0).mean()), "frac_noinj": float((g.d_noinj > 0).mean()),
                "frac_own_gt_pos2": float((g.own_minus_pos2 > 0).mean()), "frac_own_gt_foreign": float((g.own_minus_foreign > 0).mean())}

    R = {k: block(g) for k, g in subsets.items()}
    Rc = {(k, flag): block(g[g.in_ctx == flag]) for k, g in subsets.items() for flag in [True, False]}
    Rr = {(k, flag): block(g[g.in_ctx_right == flag]) for k, g in subsets.items() for flag in [True, False]}
    k0 = R["all"]
    out = L.outcome_ci_at_or_below(k0["own_minus_pos2"], 0.0, min_n=100)
    L.append_disconfirmation("T2b", "T2b", "CI95 (cluster by explanation) of mean (d_own − d_pos2), d = lp_orig − lp_corrupt after the AV's own claim prefix, near donor = same document other position, all 691 single-word rows ≤ 0 (activation-dependence test, not a truth test)",
                             f"mean d_own−d_pos2={fm(k0['own_minus_pos2'])} n={k0['n']} n_expl={k0['n_expl']}; d_own {k0['d_own']['mean']:.4f} d_pos2 {k0['d_pos2']['mean']:.4f} d_foreign {k0['d_foreign']['mean']:.4f} d_noinj {k0['d_noinj']['mean']:.4f}; "
                             f"frac d>0 own {k0['frac_own']:.3f} pos2 {k0['frac_pos2']:.3f} foreign {k0['frac_foreign']:.3f} noinj {k0['frac_noinj']:.3f}; d_own−d_foreign {fm(k0['own_minus_foreign'])}; "
                             f"LLM (n={R['LLM corrupt']['n']}) own−pos2 {fm(R['LLM corrupt']['own_minus_pos2'])}; det (n={R['deterministic']['n']}) {fm(R['deterministic']['own_minus_pos2'])}; "
                             f"in_ctx=True (n={Rc[('all', True)]['n']}) {fm(Rc[('all', True)]['own_minus_pos2'])}, in_ctx=False (n={Rc[('all', False)]['n']}) {fm(Rc[('all', False)]['own_minus_pos2'])}",
                             out, "MET would mean the preference for the original word does not depend on which activation of the same document is injected: self-consistency, not readout")

    hdr = ["| subset | n | n_expl | mean d_own | mean d_pos2 [CI] | mean d_foreign [CI] | mean d_noinj | d_own − d_pos2 [CI] | d_own − d_foreign [CI] | d_pos2 − d_noinj [CI] | d_foreign − d_noinj [CI] | frac d>0 own / pos2 / foreign / noinj | frac own>pos2 | frac own>foreign |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def rowline(name, b):
        if b["n"] == 0:
            return f"| {name} | 0 | | | | | | | | | | | | |"
        return (f"| {name} | {b['n']} | {b['n_expl']} | {b['d_own']['mean']:.3f} | {fm(b['d_pos2'], 3)} | {fm(b['d_foreign'], 3)} | {b['d_noinj']['mean']:.3f} | {fm(b['own_minus_pos2'], 3)} | {fm(b['own_minus_foreign'], 3)} | "
                f"{fm(b['pos2_minus_noinj'], 3)} | {fm(b['foreign_minus_noinj'], 3)} | {b['frac_own']:.3f} / {b['frac_pos2']:.3f} / {b['frac_foreign']:.3f} / {b['frac_noinj']:.3f} | {b['frac_own_gt_pos2']:.3f} | {b['frac_own_gt_foreign']:.3f} |")

    lines = ["# T2b summary — activation-dependence control for the round-3 claim-word readout (AV forward only)", "",
             "**ACTIVATION-DEPENDENCE TEST, NOT A TRUTH TEST.** The prefix and the \"original\" word are the AV's own greedy output; d_own and d_noinj are reused from t2_claims.csv.", "",
             f"git {L.git_hash()[:8]}; settings in t2b_settings.json; rows in t2b_claims.csv; human labelling sheet t2b_support_sheet.csv ({len(sheet)} rows, label_supported empty)", "",
             f"- rows {len(cl)} (LLM corrupt {int((cl.edit_type == 'corrupt').sum())}, deterministic {int((cl.edit_type == 'corrupt_det').sum())}); errors {int((cl.t2b_error != '').sum())}; AV forwards {timings['n_av_forward']} ({timings['av_s_per_forward']:.2f} s each); prompt {int(P.ids.shape[1])} tokens, marker at {P.inj_pos}",
             f"- prefixes reconstructed from s3_edits.jsonl and asserted equal to the file's word_orig / word_corrupt / word_pos for all {len(cl)} rows",
             f"- in_ctx (word_orig in context_left_64 + token_str): {int(cl.in_ctx.sum())}/{len(cl)}; in_ctx_right (+ context_right_16): {int(cl.in_ctx_right.sum())}/{len(cl)}; corrupt word in left context: {int(cl.corrupt_in_ctx.sum())}/{len(cl)}",
             f"- in_ctx by edit type: LLM {int(cl[cl.edit_type == 'corrupt'].in_ctx.sum())}/{int((cl.edit_type == 'corrupt').sum())}, det {int(cl[cl.edit_type == 'corrupt_det'].in_ctx.sum())}/{int((cl.edit_type == 'corrupt_det').sum())}",
             "", "## Kill T2b", "",
             f"- mean (d_own − d_pos2), all rows, cluster by explanation: {fm(k0['own_minus_pos2'])} n={k0['n']} n_expl={k0['n_expl']}; threshold ≤ 0 → **{out}**",
             f"- LLM corrupt: {fm(R['LLM corrupt']['own_minus_pos2'])} → {L.outcome_ci_at_or_below(R['LLM corrupt']['own_minus_pos2'], 0.0, min_n=100)}; deterministic: {fm(R['deterministic']['own_minus_pos2'])} → {L.outcome_ci_at_or_below(R['deterministic']['own_minus_pos2'], 0.0, min_n=100)} (splits, reported)",
             f"- far donor (reported, not a kill): mean (d_own − d_foreign) {fm(k0['own_minus_foreign'])}",
             "", "## Donor table (all rows)", ""] + hdr + [rowline(k, b) for k, b in R.items()]
    lines += ["", "## Donor table split by in_ctx (word_orig visible in context_left_64 + token_str)", ""] + hdr
    for k in subsets:
        for flag in [True, False]:
            lines.append(rowline(f"{k}, in_ctx={flag}", Rc[(k, flag)]))
    lines += ["", "## Donor table split by in_ctx_right (+ context_right_16)", ""] + hdr
    for k in subsets:
        for flag in [True, False]:
            lines.append(rowline(f"{k}, in_ctx_right={flag}", Rr[(k, flag)]))
    lines += ["", "## Ten fixed rows (every 69th row of t2b_claims.csv)", "", "| row | stim | edit | word_orig | word_corrupt | in_ctx | d_own | d_pos2 | d_foreign | d_noinj | prefix (tail) |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for n in range(0, len(cl), 69):
        r = cl.iloc[n]
        lines.append(f"| {r.row} | {r.stim_idx} | {r.edit_type} | {r.word_orig} | {r.word_corrupt} | {r.in_ctx} | {r.d_own:+.2f} | {r.d_pos2:+.2f} | {r.d_foreign:+.2f} | {r.d_noinj:+.2f} | …{r.prefill[-60:].replace(chr(10), ' ')!s} |")
    lines.append("")
    (L.OVERNIGHT / "t2b_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, n_rows=len(cl), n_errors=int((cl.t2b_error != "").sum()), kill_T2b={"ci": k0["own_minus_pos2"], "outcome": out}, subsets=R,
             by_in_ctx={f"{k}|in_ctx={f}": v for (k, f), v in Rc.items()}, by_in_ctx_right={f"{k}|in_ctx_right={f}": v for (k, f), v in Rr.items()},
             in_ctx_counts={"in_ctx": int(cl.in_ctx.sum()), "in_ctx_right": int(cl.in_ctx_right.sum()), "corrupt_in_ctx": int(cl.corrupt_in_ctx.sum())})
    L.log(f"T2b done: own−pos2 {fm(k0['own_minus_pos2'])} -> {out}; own−foreign {fm(k0['own_minus_foreign'])}; frac d>0 own {k0['frac_own']:.3f} pos2 {k0['frac_pos2']:.3f} foreign {k0['frac_foreign']:.3f}")


if __name__ == "__main__":
    main()

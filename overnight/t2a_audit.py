"""T2a — audit of the round-3 topic readout + held-out wording confirmation (PLAN.md round 3b; AV forward only).

  uv run python overnight/t2a_audit.py

Audit (no model): from t2_scores.csv and t2_prefix.py source — the prior-corrected statistic used the identical
prefix (PREFILL_CC) and candidate strings (' ' + topic) for injected and no-injection runs (source inspection +
cc_*_corr == cc_* - cc_*_noinj in the file); the prior-corrected AUROC was NOT pre-registered in the round-3 PLAN
(exploratory); the (i+100) mod 200 pairing makes every title both a true and a foreign candidate; within-pair choice
accuracy with CI by document for raw, prior-corrected and swap; prior-corrected AUROC recomputed with CI.
Held-out wording (frozen in PLAN, never seen by any model before this run):
  p3 = '<explanation>\nThe document is about'
scored as ' ' + topic_true vs ' ' + topic_foreign on all 200 stimuli under own activation, foreign activation
((i+100) mod 200) and no injection. Topics detokenised exactly as round-3 T2 (t1_arprobe.detok).
Kill T2a (pre-registered): raw AUROC of p3 candidate continuation (own activation, eval n=160, paired bootstrap by
document) <= 0.60 -> MET. Prior-corrected AUROC, within-pair accuracy, swap AUROC reported alongside.
Same-items table on the 160 evaluation stimuli: AR probe (T1), RepE centred and direction (T1), T2 PREFILL_CC raw and
prior-corrected, p3 raw and prior-corrected; row sets asserted identical.
"""
from __future__ import annotations

import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix, PREFILL_CC  # noqa: E402  (import-safe, checked in U0)
from overnight.t1_arprobe import auroc, boot_auroc, detok, auroc_outcome  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

P3 = "<explanation>\nThe document is about"
THRESH = 0.60
N_BOOT, SEED = 1000, 0


def boot_frac(ind, seed=SEED):
    """Bootstrap CI of a proportion over stimuli (one row per document; cluster = stimulus)."""
    return L.cluster_bootstrap_mean(np.asarray(ind, dtype=float), np.arange(len(ind)), n_boot=N_BOOT, seed=seed)


def fa(b):
    return f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"


def ff(c):
    return f"{c['mean']:.3f} [{c['lo']:.3f},{c['hi']:.3f}]"


def main():
    S = L.Settings("t2a", threshold=THRESH, prefix_p3=P3, prefix_round3=PREFILL_CC, candidate_rule="' ' + detok(topic); tokenised separately, appended after the prefill; summed log-prob (per-token also recorded)",
                   no_injection="marker row left as the raw embedding of token 149705 (asserted in Prefix.inject)", foreign_rule="(i + 100) mod 200",
                   kill="raw AUROC of p3 summed log-prob ' topic_true' vs ' topic_foreign', own activation, eval n=160, paired bootstrap by document <= 0.60 -> MET", n_boot=N_BOOT, seed=SEED)
    timings = {}
    t2 = pd.read_csv(L.OVERNIGHT / "t2_scores.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    t1 = pd.read_csv(L.OVERNIGHT / "t1_scores.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    assert len(t2) == 200 and (t2.error == "").all() and len(t1) == 200 and len(top) == 200

    # ---------------- audit (no model)
    audit = []
    src = (L.OVERNIGHT / "t2_prefix.py").read_text()
    a1 = bool(re.search(r"noinj_cc\[t\] = P\.cont_logprob\(None, PREFILL_CC, \" \" \+ t\)", src))
    a2 = bool(re.search(r"P\.cont_logprob\(h, PREFILL_CC, \" \" \+ tt\)", src)) and bool(re.search(r"P\.cont_logprob\(h, PREFILL_CC, \" \" \+ tf\)", src))
    a3 = bool(re.search(r"row\[\"cc_true_corr\"\] = lt - noinj_cc\[tt\]\[0\]", src))
    audit.append(("t2_prefix.py: no-injection candidate scored with PREFILL_CC and ' ' + topic (source)", a1))
    audit.append(("t2_prefix.py: injected candidates scored with PREFILL_CC and ' ' + topic (source)", a2))
    audit.append(("t2_prefix.py: cc_true_corr = cc_true − cc_true_noinj (source)", a3))
    d1 = float(np.max(np.abs(t2.cc_true_corr - (t2.cc_true - t2.cc_true_noinj)))); d2 = float(np.max(np.abs(t2.cc_foreign_corr - (t2.cc_foreign - t2.cc_foreign_noinj))))
    audit.append((f"t2_scores.csv: cc_*_corr == cc_* − cc_*_noinj (max |dev| {max(d1, d2):.2e})", max(d1, d2) < 1e-9))
    pair_ok = bool(((t2.foreign_stim_idx == (t2.stim_idx + 100) % 200)).all()) and bool((top.foreign_stim_idx == (top.stim_idx + 100) % 200).all())
    audit.append(("foreign_stim_idx == (i+100) mod 200 for all 200 stimuli (t2_scores and t0_topics)", pair_ok))
    perm_ok = bool((t2.foreign_stim_idx.values[t2.foreign_stim_idx.values] == t2.stim_idx.values).all())
    audit.append(("pairing is an involution (foreign of foreign = self): every title is exactly once a true and once a foreign candidate", perm_ok))
    same_multiset = sorted(t2.topic_true.tolist()) == sorted(t2.topic_foreign.tolist())
    audit.append(("multiset of true topics == multiset of foreign topics (200 rows)", same_multiset))
    ev_titles_as_foreign_in_eval = int(t2[t2.split == "eval"].foreign_stim_idx.isin(t2[t2.split == "eval"].stim_idx).sum())
    audit.append((f"evaluation rows whose foreign partner is also an evaluation row: {ev_titles_as_foreign_in_eval}/160 (pairs (i, i+100) with 40<=i<100 both in eval; 100<=i<140 partners 0-39 are pilot)", True))
    plan = (L.OVERNIGHT / "PLAN.md").read_text()
    t2_block = plan.split("### T2 — forced-prefix yes/no readout")[1].split("### T3")[0]
    prereg_prior_corr = ("prior-corrected" in t2_block) or ("prior corrected" in t2_block)
    audit.append((f"round-3 PLAN T2 stage text asks for a prior-corrected AUROC: {prereg_prior_corr} (it asks for the no-injection AUROC and mean yes−no under no injection) → prior-corrected AUROC 0.9347 is EXPLORATORY, not pre-registered", not prereg_prior_corr))
    for name, ok in audit:
        assert ok, name

    ev2 = t2[t2.split == "eval"].reset_index(drop=True)
    acc_raw = boot_frac(ev2.cc_true > ev2.cc_foreign); acc_corr = boot_frac(ev2.cc_true_corr > ev2.cc_foreign_corr); acc_swap = boot_frac(ev2.cc_foreign_swap > ev2.cc_true_swap)
    acc_noinj = boot_frac(ev2.cc_true_noinj > ev2.cc_foreign_noinj)
    au_raw = boot_auroc(ev2.cc_true, ev2.cc_foreign); au_corr = boot_auroc(ev2.cc_true_corr, ev2.cc_foreign_corr); au_swap = boot_auroc(ev2.cc_foreign_swap, ev2.cc_true_swap); au_noinj = boot_auroc(ev2.cc_true_noinj, ev2.cc_foreign_noinj)
    # prior-corrected swap: under the foreign activation, prefer the foreign topic after subtracting the same prior
    au_swap_corr = boot_auroc(ev2.cc_foreign_swap - ev2.cc_foreign_noinj, ev2.cc_true_swap - ev2.cc_true_noinj); acc_swap_corr = boot_frac((ev2.cc_foreign_swap - ev2.cc_foreign_noinj) > (ev2.cc_true_swap - ev2.cc_true_noinj))
    L.log(f"audit OK ({len(audit)} checks); round-3 PREFILL_CC eval: raw AUROC {fa(au_raw)}, prior-corrected {fa(au_corr)}, acc raw {ff(acc_raw)} corr {ff(acc_corr)} swap {ff(acc_swap)}")

    # ---------------- held-out prefix p3
    topics = [detok(t) for t in top.topic_true]; foreign = list(top.foreign_stim_idx)
    assert topics == [detok(t) for t in t2.topic_true]
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    P = Prefix(av); S.update(prompt_tokens=int(P.ids.shape[1]), marker_pos=P.inj_pos)
    noinj = {}
    t0 = time.time()
    for t in sorted(set(topics)):
        noinj[t] = P.cont_logprob(None, P3, " " + t)
    L.log(f"no-injection cache: {len(noinj)} topics, {P.n_forward} forwards in {time.time() - t0:.0f}s")
    rows = []; t0 = time.time(); n0 = P.n_forward
    for i in range(200):
        j = foreign[i]; tt, tf = topics[i], topics[j]
        h = torch.from_numpy(h20[i]); hj = torch.from_numpy(h20[j])
        row = {"stim_idx": i, "doc_idx": int(top.doc_idx[i]), "split": L.split_of(i), "topic_true": tt, "topic_foreign": tf, "foreign_stim_idx": j,
               "topic_in_default_explanation": bool(top.topic_in_default_explanation[i]), "error": ""}
        try:
            lt, nt = P.cont_logprob(h, P3, " " + tt); lf, nf = P.cont_logprob(h, P3, " " + tf)
            st, _ = P.cont_logprob(hj, P3, " " + tt); sf, _ = P.cont_logprob(hj, P3, " " + tf)
            l0t, l0f = noinj[tt][0], noinj[tf][0]
            row.update({"p3_true": lt, "p3_foreign": lf, "n_tok_true": nt, "n_tok_foreign": nf, "p3_true_pt": lt / nt, "p3_foreign_pt": lf / nf,
                        "p3_true_swap": st, "p3_foreign_swap": sf, "p3_true_noinj": l0t, "p3_foreign_noinj": l0f, "p3_true_noinj_pt": l0t / nt, "p3_foreign_noinj_pt": l0f / nf,
                        "p3_true_corr": lt - l0t, "p3_foreign_corr": lf - l0f, "p3_true_swap_corr": st - l0t, "p3_foreign_swap_corr": sf - l0f})
        except Exception:
            row["error"] = traceback.format_exc(); L.log(f"T2a FAILED on stim {i}")
        rows.append(row)
        if i % 50 == 49:
            L.log(f"stim {i + 1}/200, forwards {P.n_forward} ({(time.time() - t0) / max(1, P.n_forward - n0):.2f}s each)")
    timings["av_s_per_forward"] = (time.time() - t0) / max(1, P.n_forward - n0); timings["n_av_forward"] = P.n_forward
    av.free()
    df = pd.DataFrame(rows); df.to_csv(L.OVERNIGHT / "t2a_scores.csv", index=False)
    ok = df[df.error == ""]

    def p3stats(e):
        d = {"n": int(len(e))}
        d["raw"] = boot_auroc(e.p3_true, e.p3_foreign); d["raw_pt"] = boot_auroc(e.p3_true_pt, e.p3_foreign_pt)
        d["noinj"] = boot_auroc(e.p3_true_noinj, e.p3_foreign_noinj); d["noinj_pt"] = boot_auroc(e.p3_true_noinj_pt, e.p3_foreign_noinj_pt)
        d["corr"] = boot_auroc(e.p3_true_corr, e.p3_foreign_corr)
        d["swap"] = boot_auroc(e.p3_foreign_swap, e.p3_true_swap); d["swap_corr"] = boot_auroc(e.p3_foreign_swap_corr, e.p3_true_swap_corr)
        d["acc_raw"] = boot_frac(e.p3_true > e.p3_foreign); d["acc_corr"] = boot_frac(e.p3_true_corr > e.p3_foreign_corr)
        d["acc_swap"] = boot_frac(e.p3_foreign_swap > e.p3_true_swap); d["acc_noinj"] = boot_frac(e.p3_true_noinj > e.p3_foreign_noinj)
        return d

    ev = ok[ok.split == "eval"].reset_index(drop=True); pi = ok[ok.split == "pilot"].reset_index(drop=True); sub = ev[~ev.topic_in_default_explanation].reset_index(drop=True)
    st_ev, st_pi, st_sub = p3stats(ev), p3stats(pi), p3stats(sub)
    out = auroc_outcome(st_ev["raw"])
    L.append_disconfirmation("T2a", "T2a", "raw AUROC of held-out prefix p3 '<explanation>\\nThe document is about' candidate continuation (' topic_true' vs ' topic_foreign'), own activation, eval, CI95 by document ≤ 0.60",
                             f"AUROC={fa(st_ev['raw'])} n={st_ev['n']}; per-token {fa(st_ev['raw_pt'])}; no-injection {fa(st_ev['noinj'])}; prior-corrected {fa(st_ev['corr'])}; swap prefers foreign {fa(st_ev['swap'])}; "
                             f"within-pair acc raw {ff(st_ev['acc_raw'])} prior-corrected {ff(st_ev['acc_corr'])} swap {ff(st_ev['acc_swap'])}; pilot raw {fa(st_pi['raw'])} n={st_pi['n']}; "
                             f"round-3 PREFILL_CC on the same 160: raw {fa(au_raw)} prior-corrected {fa(au_corr)} (prior-corrected NOT pre-registered in round 3)",
                             out, "MET would mean the round-3 topic readout does not hold up on a held-out wording")

    # ---------------- same-items comparison (160 eval, same labels)
    e1 = t1[t1.split == "eval"].reset_index(drop=True)
    assert set(e1.stim_idx) == set(ev2.stim_idx) == set(ev.stim_idx) and len(ev) == 160, (len(e1), len(ev2), len(ev))
    assert (e1.topic_true.values == ev2.topic_true.values).all() and (e1.foreign_stim_idx.values == ev2.foreign_stim_idx.values).all() and (ev2.foreign_stim_idx.values == ev.foreign_stim_idx.values).all()
    comp = [("AR probe `This text is about {topic}.` (T1)", boot_auroc(e1.cos_topic_true, e1.cos_topic_foreign), boot_frac(e1.cos_topic_true > e1.cos_topic_foreign)),
            ("RepE class means, centred (T1)", boot_auroc(e1.repe_cos_true_centred, e1.repe_cos_foreign_centred), boot_frac(e1.repe_cos_true_centred > e1.repe_cos_foreign_centred)),
            ("RepE difference direction s vs −s (T1)", boot_auroc(e1.repe_s_diff, -e1.repe_s_diff), boot_frac(e1.repe_s_diff > 0)),
            ("T2 `The passage concerns` raw (round 3)", au_raw, acc_raw),
            ("T2 `The passage concerns` prior-corrected (round 3; exploratory)", au_corr, acc_corr),
            ("T2 `The passage concerns` no injection (round 3)", au_noinj, acc_noinj),
            ("T2 `The passage concerns` swap, prefers foreign (round 3)", au_swap, acc_swap),
            ("p3 `The document is about` raw (held-out, this stage)", st_ev["raw"], st_ev["acc_raw"]),
            ("p3 `The document is about` prior-corrected", st_ev["corr"], st_ev["acc_corr"]),
            ("p3 `The document is about` no injection", st_ev["noinj"], st_ev["acc_noinj"]),
            ("p3 `The document is about` swap, prefers foreign", st_ev["swap"], st_ev["acc_swap"])]
    # agreement between the two prefixes per item
    agree_raw = float(((ev2.cc_true > ev2.cc_foreign) == (ev.p3_true > ev.p3_foreign)).mean())
    sp = float(pd.Series(ev2.cc_true - ev2.cc_foreign).corr(pd.Series(ev.p3_true - ev.p3_foreign), method="spearman"))
    sp_corr = float(pd.Series(ev2.cc_true_corr - ev2.cc_foreign_corr).corr(pd.Series(ev.p3_true_corr - ev.p3_foreign_corr), method="spearman"))

    lines = ["# T2a summary — audit of the round-3 topic readout + held-out wording p3 (AV forward only)", "",
             f"git {L.git_hash()[:8]}; settings in t2a_settings.json; rows in t2a_scores.csv (200 stimuli; p3 own / foreign-swap / no-injection log-probs)", "",
             f"- AV forwards {timings['n_av_forward']} ({timings['av_s_per_forward']:.2f} s each); errors {int((df.error != '').sum())}; prompt {int(P.ids.shape[1])} tokens, marker at {P.inj_pos}",
             f"- p3 = `{P3!r}` (frozen in PLAN 2026-09-06 23:15; first run here); round-3 prefix = `{PREFILL_CC!r}`; candidates ' ' + detok(topic) in both",
             f"- token counts (' ' + topic): true mean {ev.n_tok_true.mean():.2f}, foreign mean {ev.n_tok_foreign.mean():.2f}",
             "", "## Audit of the round-3 statistic (no model)", ""]
    for name, okk in audit:
        lines.append(f"- [{'x' if okk else ' '}] {name}")
    lines += ["", "- **The prior-corrected AUROC (0.9347 in DISCONFIRMATION.md, reported there without a CI) was not pre-registered in the round-3 PLAN; it is exploratory.** Recomputed on the same 160 items with CI by document: "
              f"{fa(au_corr)}; raw {fa(au_raw)}; no-injection {fa(au_noinj)}; swap prefers foreign {fa(au_swap)}; swap prior-corrected {fa(au_swap_corr)}",
              f"- within-pair choice accuracy (own activation, eval, CI by document): raw {ff(acc_raw)}; prior-corrected {ff(acc_corr)}; swap (foreign activation prefers foreign topic) {ff(acc_swap)}; swap prior-corrected {ff(acc_swap_corr)}; no injection {ff(acc_noinj)}",
              "", "## Kill T2a — held-out prefix p3 (evaluation n=160, own activation, paired bootstrap by document)", "",
              f"- raw AUROC ' topic_true' vs ' topic_foreign': {fa(st_ev['raw'])} → **{out}**",
              f"- per-token normalised: {fa(st_ev['raw_pt'])}",
              f"- no injection (prior only): {fa(st_ev['noinj'])}; per-token {fa(st_ev['noinj_pt'])}",
              f"- prior-corrected (lp − lp_noinj): {fa(st_ev['corr'])}",
              f"- swap control (foreign activation; AUROC that it prefers the foreign topic): {fa(st_ev['swap'])}; prior-corrected {fa(st_ev['swap_corr'])}",
              f"- within-pair choice accuracy: raw {ff(st_ev['acc_raw'])}; prior-corrected {ff(st_ev['acc_corr'])}; swap {ff(st_ev['acc_swap'])}; no injection {ff(st_ev['acc_noinj'])}",
              f"- pilot (n={st_pi['n']}): raw {fa(st_pi['raw'])}; prior-corrected {fa(st_pi['corr'])}; swap {fa(st_pi['swap'])}",
              f"- topic-absent subset (topic_true not in default explanation; n={st_sub['n']}): raw {fa(st_sub['raw'])}; prior-corrected {fa(st_sub['corr'])}; no-injection {fa(st_sub['noinj'])}",
              f"- per-item agreement of raw choice between the two prefixes: {agree_raw:.3f}; Spearman of the raw margins {sp:+.3f}; of the prior-corrected margins {sp_corr:+.3f}",
              "", "## Same-items comparison (160 evaluation stimuli, identical true/foreign labels; AUROC paired bootstrap by document; accuracy = fraction of items where the true topic wins)", "",
              "| readout | AUROC [CI95] | within-pair accuracy [CI95] |", "|---|---|---|"]
    for name, a, c in comp:
        lines.append(f"| {name} | {fa(a)} | {ff(c)} |")
    lines += ["", "## Ten fixed rows (eval rows 0,16,…,144)", "", "| stim | topic_true | topic_foreign | p3 true | p3 foreign | p3 true noinj | p3 foreign noinj | p3 true swap | p3 foreign swap | T2 cc true | T2 cc foreign |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in range(40, 200, 16):
        r = df[df.stim_idx == i].iloc[0]; q = t2[t2.stim_idx == i].iloc[0]
        lines.append(f"| {i} | {r.topic_true} | {r.topic_foreign} | {r.get('p3_true', float('nan')):.2f} | {r.get('p3_foreign', float('nan')):.2f} | {r.get('p3_true_noinj', float('nan')):.2f} | {r.get('p3_foreign_noinj', float('nan')):.2f} | "
                     f"{r.get('p3_true_swap', float('nan')):.2f} | {r.get('p3_foreign_swap', float('nan')):.2f} | {q.cc_true:.2f} | {q.cc_foreign:.2f} |")
    lines.append("")
    (L.OVERNIGHT / "t2a_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, audit=[{"check": n, "ok": bool(o)} for n, o in audit], kill_T2a={"stats": st_ev["raw"], "outcome": out}, p3_eval=st_ev, p3_pilot=st_pi, p3_topic_absent=st_sub,
             round3_recomputed={"raw": au_raw, "corr": au_corr, "noinj": au_noinj, "swap": au_swap, "swap_corr": au_swap_corr, "acc_raw": acc_raw, "acc_corr": acc_corr, "acc_swap": acc_swap},
             comparison=[{"readout": n, "auroc": a, "acc": c} for n, a, c in comp], agreement={"raw_choice": agree_raw, "spearman_raw": sp, "spearman_corr": sp_corr})
    L.log(f"T2a done: p3 raw AUROC {fa(st_ev['raw'])} -> {out}; prior-corrected {fa(st_ev['corr'])}; swap {fa(st_ev['swap'])}")


if __name__ == "__main__":
    main()

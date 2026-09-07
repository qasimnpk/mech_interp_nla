"""T1 — the reconstructor as a zero-shot text probe (PLAN.md round 3).

  uv run python overnight/t1_arprobe.py

Probe score for any sentence s and activation h: cos(h, AR(s)) (cos is invariant to the
normalisation u(d) = AR(d)/||AR(d)|| in the plan). Activations h = out/acts_L20.npz h20 (block 20 at pos).
  topic:      'This text is about {topic}.' for topic_true and topic_foreign (t0_topics.csv)
  confidence: 'The model is highly confident about the next token.' vs 'The model is uncertain about the next token.'
  conflict:   'The model is torn between two continuations.' vs 'The model has one clear continuation in mind.'
  fillers:    'This is a sentence.', 'Text.'
  matched claims: the 490 accepted S3 triples (claim c, corruption c*, paraphrase c~, + corrupt_det where present),
                  each scored ALONE against its own stimulus activation.
Standard-probe baseline (RepE / difference of means): in the TARGET at block 20 (last token), 16 fixed
sentence templates filled with the topic (200 topics x 16 = 3200 short forwards); mu_topic = mean of the 16.
  d_i = mu_true_i - mu_foreign_i; s_repe_i = cos(h_i, d_i).
  paired AUROC analogue: positives cos(h_i, mu_true_i - mu_bar) vs negatives cos(h_i, mu_foreign_i - mu_bar),
  mu_bar = mean over the 200 topic means (uncentred version also reported).
Kill T1 (pre-registered): AUROC of cos(h,AR(true)) vs cos(h,AR(foreign)) over the 160 evaluation stimuli
(paired: each stimulus contributes one positive and one negative), 95% bootstrap CI by document
(= by stimulus, 1000 draws, seed 0) <= 0.60 -> MET; NOT MET if lo > 0.60; else INCONCLUSIVE.
TARGET phase first (freed), then AR. Raw outputs kept in t1_scores.csv, t1_claims.csv, out/t1_repe.npz.
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
from scipy.stats import rankdata, spearmanr  # noqa: E402

THRESH = 0.60
MIN_N = 100
TOPIC_SENT = "This text is about {topic}."
PROBES = {"confident": "The model is highly confident about the next token.",
          "uncertain": "The model is uncertain about the next token.",
          "torn": "The model is torn between two continuations.",
          "clear": "The model has one clear continuation in mind.",
          "filler1": "This is a sentence.", "filler2": "Text."}
REPE_TEMPLATES = [
    "This text is about {topic}.", "The following passage discusses {topic}.", "{topic} is the subject of this article.",
    "Here is some information about {topic}.", "The article describes {topic} in detail.", "Everything below concerns {topic}.",
    "The topic of the document is {topic}.", "This section covers {topic}.", "The writer is explaining {topic}.",
    "Facts about {topic} are listed here.", "The main subject here is {topic}.", "Let me tell you about {topic}.",
    "The document is an encyclopedia entry on {topic}.", "Readers will learn about {topic} from this text.",
    "A short summary of {topic} follows.", "The paragraph gives background on {topic}.",
]
FIXED_ROWS = list(range(40, 200, 16))
N_BOOT = 1000


def detok(t: str) -> str:
    """Undo wikitext spacing: ' ( x )' -> ' (x)', ' , ' -> ', ', ' @-@ ' -> '-', ' @,@ ' -> ',', ' @.@ ' -> '.'."""
    t = t.replace(" @-@ ", "-").replace(" @,@ ", ",").replace(" @.@ ", ".")
    t = re.sub(r"\s+([,;:.!?%)])", r"\1", t)
    t = re.sub(r"([(\[])\s+", r"\1", t)
    t = t.replace(" 's", "'s").replace(" n't", "n't")
    return re.sub(r"\s+", " ", t).strip()


def auroc(pos, neg) -> float:
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def boot_auroc(pos, neg, seed=0) -> dict:
    """Paired bootstrap by stimulus: pos[i], neg[i] belong to stimulus i."""
    pos = np.asarray(pos, float); neg = np.asarray(neg, float); n = len(pos)
    rng = np.random.default_rng(seed)
    vals = [auroc(pos[idx], neg[idx]) for idx in rng.integers(0, n, size=(N_BOOT, n))]
    return {"auroc": auroc(pos, neg), "lo": float(np.percentile(vals, 2.5)), "hi": float(np.percentile(vals, 97.5)), "n": int(n)}


def boot_spearman(x, y, seed=0) -> dict:
    x = np.asarray(x, float); y = np.asarray(y, float); n = len(x)
    if n < 5:
        return {"rho": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": int(n), "p": float("nan")}
    rng = np.random.default_rng(seed)
    vals = []
    for idx in rng.integers(0, n, size=(N_BOOT, n)):
        r = spearmanr(x[idx], y[idx]).statistic
        vals.append(r if np.isfinite(r) else 0.0)
    sr = spearmanr(x, y)
    return {"rho": float(sr.statistic), "lo": float(np.percentile(vals, 2.5)), "hi": float(np.percentile(vals, 97.5)), "n": int(n), "p": float(sr.pvalue)}


def auroc_outcome(b: dict) -> str:
    if b["n"] < MIN_N:
        return "INCONCLUSIVE"
    if b["hi"] <= THRESH:
        return "MET"
    if b["lo"] > THRESH:
        return "NOT MET"
    return "INCONCLUSIVE"


def load_triples() -> pd.DataFrame:
    rows = []
    for line in (L.OVERNIGHT / "s3_edits.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if not r["edit_ok"]:
            continue
        det = r.get("corrupt_det") if r.get("numeric_ok") else None
        rows.append({"row": int(r["row"]), "stim_idx": int(r["stim_idx"]), "claim_idx": int(r["claim_idx"]), "n_claims": int(r["n_claims"]),
                     "claim": r["claim"], "corrupt": r["corrupt"], "paraphrase": r["paraphrase"], "corrupt_det": det, "has_det": det is not None})
    df = pd.DataFrame(rows).sort_values("row").reset_index(drop=True)
    assert len(df) == 490, len(df)
    return df


def target_phase(topics: list[str], timings: dict) -> np.ndarray:
    t0 = time.time()
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    d = tgt.model.config.hidden_size
    R = np.zeros((len(topics), len(REPE_TEMPLATES), d), np.float32)
    t0 = time.time()
    for ti, topic in enumerate(topics):
        for k, tpl in enumerate(REPE_TEMPLATES):
            ids = tgt.tok(tpl.format(topic=topic), return_tensors="pt", add_special_tokens=False)["input_ids"]
            hs = tgt.hidden_states(ids)
            R[ti, k] = L.to_cpu_f32(hs[L.LAYER + 1][0, -1]).numpy()
        if ti % 50 == 0:
            L.log(f"RepE {ti}/{len(topics)} ({(time.time() - t0) / max(1, ti * 16 + 16):.3f} s/sentence)")
    timings["target_s_per_short"] = (time.time() - t0) / (len(topics) * len(REPE_TEMPLATES))
    tgt.free()
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    np.savez(L.OUT / "t1_repe.npz", R=R, topics=np.array(topics, dtype=object))
    return R


def main():
    S = L.Settings("t1", threshold=THRESH, min_n=MIN_N, topic_sentence=TOPIC_SENT, probes=PROBES, repe_templates=REPE_TEMPLATES,
                   topic_normalisation="detok(): undo wikitext spacing ( ' ( x )'->' (x)', ' , '->', ', ' @-@ '->'-' ) before filling sentences; raw heading kept in t1_scores.csv",
                   auroc="paired: positives cos(h_i,AR(true_i)), negatives cos(h_i,AR(foreign_i)), i over evaluation stimuli; bootstrap by stimulus (=document), 1000 draws, seed 0",
                   repe="d_i = mean_k TARGET_L20_last(template_k(true_i)) - same for foreign_i; s_repe = cos(h_i, d_i); paired AUROC uses class means centred by the grand mean of the 200 topic means",
                   claims="490 accepted S3 triples scored ALONE: cos(h_stim, AR(text)); cluster bootstrap by explanation (stim_idx)",
                   spearman="Spearman(s_conf, -entropy_nats) and Spearman(s_conflict, entropy_nats); bootstrap by stimulus; pooled and per token_type (t0_entropy.csv)",
                   fixed_rows=FIXED_ROWS, evaluation_set="stimuli 40-199")
    timings = {}
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    ent = pd.read_csv(L.OVERNIGHT / "t0_entropy.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    acts = np.load(L.OUT / "acts_L20.npz"); h20 = acts["h20"]
    s1 = pd.read_csv(L.OVERNIGHT / "s1_recon.csv")
    triples = load_triples()
    topics_raw = list(top.topic_true)
    topics = [detok(t) for t in topics_raw]
    foreign_idx = list(top.foreign_stim_idx)

    # ---------------- TARGET: RepE class means
    R = target_phase(topics, timings)
    MU = R.mean(1)                     # [200, d]
    mu_bar = MU.mean(0)

    # ---------------- AR
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    cache: dict[str, np.ndarray] = {}

    def pred(text: str) -> np.ndarray:
        if text not in cache:
            cache[text] = ar.predict(text).numpy()
        return cache[text]

    t0 = time.time()
    P = {k: pred(v) for k, v in PROBES.items()}
    topic_pred = [pred(TOPIC_SENT.format(topic=t)) for t in topics]
    L.log(f"topic + probe sentences scored: {ar.n_forward} forwards")
    rows = []
    for i in range(200):
        h = h20[i]; j = foreign_idx[i]
        row = {"stim_idx": i, "doc_idx": int(top.doc_idx[i]), "split": L.split_of(i), "token_str": ent.token_str[i], "token_type": ent.token_type[i],
               "entropy_nats": float(ent.entropy_nats[i]), "top1_prob": float(ent.top1_prob[i]),
               "topic_true_raw": topics_raw[i], "topic_true": topics[i], "topic_foreign": topics[j], "foreign_stim_idx": j,
               "topic_in_default_explanation": bool(top.topic_in_default_explanation[i]),
               "cos_topic_true": L.cos(h, topic_pred[i]), "cos_topic_foreign": L.cos(h, topic_pred[j]),
               "cos_own_explanation_s1": float(s1.cos_own.iloc[i]), "cos_empty_s1": float(s1.cos_empty.iloc[i])}
        for k in PROBES:
            row[f"cos_{k}"] = L.cos(h, P[k])
        row["s_topic"] = row["cos_topic_true"] - row["cos_topic_foreign"]
        row["s_conf"] = row["cos_confident"] - row["cos_uncertain"]
        row["s_conflict"] = row["cos_torn"] - row["cos_clear"]
        # RepE baseline
        dvec = MU[i] - MU[j]
        row["repe_s_diff"] = L.cos(h, dvec)
        row["repe_cos_true_centred"] = L.cos(h, MU[i] - mu_bar); row["repe_cos_foreign_centred"] = L.cos(h, MU[j] - mu_bar)
        row["repe_cos_true_raw"] = L.cos(h, MU[i]); row["repe_cos_foreign_raw"] = L.cos(h, MU[j])
        row["repe_cos_mu_true_mu_foreign"] = L.cos(MU[i], MU[j])
        row["cos_ar_true_ar_foreign"] = L.cos(topic_pred[i], topic_pred[j])
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(L.OVERNIGHT / "t1_scores.csv", index=False)

    # matched claims
    crow = []
    for r in triples.itertuples():
        h = h20[r.stim_idx]
        rec = {"row": r.row, "stim_idx": r.stim_idx, "claim_idx": r.claim_idx, "n_claims": r.n_claims, "is_last": r.claim_idx == r.n_claims - 1,
               "has_det": r.has_det, "error": ""}
        try:
            rec["cos_claim"] = L.cos(h, pred(r.claim)); rec["cos_corrupt"] = L.cos(h, pred(r.corrupt)); rec["cos_paraphrase"] = L.cos(h, pred(r.paraphrase))
            rec["cos_corrupt_det"] = L.cos(h, pred(r.corrupt_det)) if r.has_det else np.nan
            rec["d_true_corrupt"] = rec["cos_claim"] - rec["cos_corrupt"]; rec["d_true_para"] = rec["cos_claim"] - rec["cos_paraphrase"]
            rec["d_para_corrupt"] = rec["cos_paraphrase"] - rec["cos_corrupt"]
            rec["d_true_det"] = rec["cos_claim"] - rec["cos_corrupt_det"] if r.has_det else np.nan
        except Exception:
            rec["error"] = traceback.format_exc(); L.log(f"AR FAILED on claim row {r.row}")
        crow.append(rec)
        if len(crow) % 100 == 0:
            L.log(f"claims {len(crow)}/490, forwards {ar.n_forward}")
    cl = pd.DataFrame(crow)
    cl.to_csv(L.OVERNIGHT / "t1_claims.csv", index=False)
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward); timings["n_ar_forward"] = ar.n_forward
    ar.free()

    # ---------------- statistics
    ev = df[df.split == "eval"].reset_index(drop=True)
    b_topic = boot_auroc(ev.cos_topic_true, ev.cos_topic_foreign)
    out = auroc_outcome(b_topic)
    L.append_disconfirmation("T1", "T1", "AUROC cos(h,AR(true topic)) vs cos(h,AR(foreign topic)), eval, CI95 by document ≤ 0.60",
                             f"AUROC={b_topic['auroc']:.4f} CI95=[{b_topic['lo']:.4f},{b_topic['hi']:.4f}] n={b_topic['n']}; frac s_topic>0={(ev.s_topic > 0).mean():.3f}; mean cos true={ev.cos_topic_true.mean():.4f} foreign={ev.cos_topic_foreign.mean():.4f}",
                             out, "MET would mean text-specified topic probing through the AR fails for these wordings, this template and these positions")
    b_topic_all = boot_auroc(df.cos_topic_true, df.cos_topic_foreign)
    b_repe_c = boot_auroc(ev.repe_cos_true_centred, ev.repe_cos_foreign_centred)
    b_repe_r = boot_auroc(ev.repe_cos_true_raw, ev.repe_cos_foreign_raw)
    b_repe_d = boot_auroc(ev.repe_s_diff, -ev.repe_s_diff)
    ci_stopic = L.cluster_bootstrap_mean(ev.s_topic, ev.stim_idx)
    ci_repe = L.cluster_bootstrap_mean(ev.repe_s_diff, ev.stim_idx)
    sub = ev[~ev.topic_in_default_explanation]
    b_topic_sub = boot_auroc(sub.cos_topic_true, sub.cos_topic_foreign) if len(sub) >= 5 else None

    sp = {}
    for name, x, y in [("conf_vs_negentropy", "s_conf", -ev.entropy_nats), ("conflict_vs_entropy", "s_conflict", ev.entropy_nats),
                       ("conf_vs_top1prob", "s_conf", ev.top1_prob), ("cos_confident_vs_negentropy", "cos_confident", -ev.entropy_nats),
                       ("cos_uncertain_vs_entropy", "cos_uncertain", ev.entropy_nats), ("cos_own_expl_vs_negentropy", "cos_own_explanation_s1", -ev.entropy_nats)]:
        sp[name] = {"pooled": boot_spearman(ev[x], y)}
        for tt in ["punctuation", "word_initial", "word_piece"]:
            m = (ev.token_type == tt).values
            sp[name][tt] = boot_spearman(ev[x][m], np.asarray(y)[m])

    cok = cl[cl.error == ""]
    ci_tc = L.cluster_bootstrap_mean(cok.d_true_corrupt, cok.stim_idx); ci_tp = L.cluster_bootstrap_mean(cok.d_true_para, cok.stim_idx)
    ci_pc = L.cluster_bootstrap_mean(cok.d_para_corrupt, cok.stim_idx)
    det = cok[cok.has_det]; ci_td = L.cluster_bootstrap_mean(det.d_true_det, det.stim_idx)
    last = cok[cok.is_last]; ci_tc_last = L.cluster_bootstrap_mean(last.d_true_corrupt, last.stim_idx); ci_tp_last = L.cluster_bootstrap_mean(last.d_true_para, last.stim_idx)
    L.append_disconfirmation("T1", "T1-claims", "matched-claim contrast (reported, not a pre-registered kill): CI95 of mean[cos(h,AR(c)) − cos(h,AR(c*))] − mean[cos(h,AR(c)) − cos(h,AR(c~))]",
                             f"true−corrupt={ci_tc['mean']:.5f} [{ci_tc['lo']:.5f},{ci_tc['hi']:.5f}]; true−para={ci_tp['mean']:.5f} [{ci_tp['lo']:.5f},{ci_tp['hi']:.5f}]; "
                             f"para−corrupt={ci_pc['mean']:.5f} [{ci_pc['lo']:.5f},{ci_pc['hi']:.5f}] n={ci_pc['n']} n_expl={ci_pc['n_clusters']}; frac true>corrupt={(cok.d_true_corrupt > 0).mean():.3f} true>para={(cok.d_true_para > 0).mean():.3f}",
                             L.outcome_ci_at_or_below(ci_pc, 0.0, min_n=300), "≤0 would mean the claim-alone probe prefers the true claim over its one-fact corruption no more than over a paraphrase")

    def fa(b):
        return f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}] n={b['n']}"

    def fs(b):
        return f"{b['rho']:+.4f} [{b['lo']:+.4f},{b['hi']:+.4f}] n={b['n']}"

    def fc(c, d=5):
        return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}] n={c['n']}"

    lines = ["# T1 summary — the reconstructor as a zero-shot text probe (AR only; RepE baseline in the TARGET)", "",
             f"git {L.git_hash()[:8]}; settings in t1_settings.json; per-stimulus rows in t1_scores.csv; claim rows in t1_claims.csv; RepE activations in out/t1_repe.npz", "",
             f"- stimuli 200 (eval 160); AR forwards {timings['n_ar_forward']} ({timings['ar_s_per_score']:.3f} s each); RepE 3200 TARGET forwards ({timings['target_s_per_short']:.3f} s each)",
             "", "## Kill T1 — topic AUROC (evaluation, paired, bootstrap by document)", "",
             f"- AR probe `{TOPIC_SENT}`: AUROC {fa(b_topic)} → **{out}**",
             f"- all 200 stimuli: {fa(b_topic_all)}",
             f"- paired difference s_topic = cos(true) − cos(foreign): {fc(ci_stopic)}; fraction > 0: {(ev.s_topic > 0).mean():.3f}",
             f"- subset where topic_true is NOT in the default explanation (n={len(sub)}): {fa(b_topic_sub) if b_topic_sub else 'n/a'}",
             f"- mean cos(h, AR(true)) {ev.cos_topic_true.mean():.4f}; cos(h, AR(foreign)) {ev.cos_topic_foreign.mean():.4f}; cos(AR(true), AR(foreign)) {ev.cos_ar_true_ar_foreign.mean():.4f}",
             "", "## RepE / difference-of-means baseline (TARGET block 20, 16 templates per topic)", "",
             "| probe | AUROC (eval) | CI95 |", "|---|---|---|",
             f"| AR probe (kill statistic) | {b_topic['auroc']:.4f} | [{b_topic['lo']:.4f},{b_topic['hi']:.4f}] |",
             f"| RepE class means, centred by grand mean | {b_repe_c['auroc']:.4f} | [{b_repe_c['lo']:.4f},{b_repe_c['hi']:.4f}] |",
             f"| RepE class means, uncentred | {b_repe_r['auroc']:.4f} | [{b_repe_r['lo']:.4f},{b_repe_r['hi']:.4f}] |",
             f"| RepE difference direction s vs −s | {b_repe_d['auroc']:.4f} | [{b_repe_d['lo']:.4f},{b_repe_d['hi']:.4f}] |",
             "", f"- RepE s = cos(h, mu_true − mu_foreign): {fc(ci_repe)}; fraction > 0: {(ev.repe_s_diff > 0).mean():.3f}",
             f"- cos(mu_true, mu_foreign) mean {ev.repe_cos_mu_true_mu_foreign.mean():.4f} (how similar the two class means are before centring)",
             f"- Spearman(s_topic AR, s_repe) over eval: {spearmanr(ev.s_topic, ev.repe_s_diff).statistic:+.4f}",
             "", "## Matched nearby contrast — 490 accepted S3 triples scored alone (cluster bootstrap by explanation)", "",
             "| difference | mean | CI95 | frac > 0 |", "|---|---|---|---|",
             f"| cos(h,AR(c)) − cos(h,AR(c*)) true − corrupt | {ci_tc['mean']:.5f} | [{ci_tc['lo']:.5f},{ci_tc['hi']:.5f}] | {(cok.d_true_corrupt > 0).mean():.3f} |",
             f"| cos(h,AR(c)) − cos(h,AR(c~)) true − paraphrase | {ci_tp['mean']:.5f} | [{ci_tp['lo']:.5f},{ci_tp['hi']:.5f}] | {(cok.d_true_para > 0).mean():.3f} |",
             f"| paraphrase − corrupt | {ci_pc['mean']:.5f} | [{ci_pc['lo']:.5f},{ci_pc['hi']:.5f}] | {(cok.d_para_corrupt > 0).mean():.3f} |",
             f"| true − corrupt_det (n={ci_td['n']}) | {ci_td['mean']:.5f} | [{ci_td['lo']:.5f},{ci_td['hi']:.5f}] | {(det.d_true_det > 0).mean():.3f} |",
             f"| last claims only (n={ci_tc_last['n']}): true − corrupt | {ci_tc_last['mean']:.5f} | [{ci_tc_last['lo']:.5f},{ci_tc_last['hi']:.5f}] | {(last.d_true_corrupt > 0).mean():.3f} |",
             f"| last claims only: true − paraphrase | {ci_tp_last['mean']:.5f} | [{ci_tp_last['lo']:.5f},{ci_tp_last['hi']:.5f}] | {(last.d_true_para > 0).mean():.3f} |",
             "", f"- mean cos alone: claim {cok.cos_claim.mean():.4f}, corrupt {cok.cos_corrupt.mean():.4f}, paraphrase {cok.cos_paraphrase.mean():.4f}; errors {int((cl.error != '').sum())}",
             "", "## Confidence / conflict probes vs next-token entropy (evaluation; Spearman, bootstrap by stimulus)", "",
             "| statistic | pooled | punctuation | word_initial | word_piece |", "|---|---|---|---|---|"]
    for name in sp:
        lines.append(f"| {name} | " + " | ".join(fs(sp[name][k]) for k in ["pooled", "punctuation", "word_initial", "word_piece"]) + " |")
    lines += ["", "| sentence | mean cos (eval) | sd |", "|---|---|---|"]
    for k in PROBES:
        lines.append(f"| {k}: {PROBES[k]} | {ev[f'cos_{k}'].mean():.4f} | {ev[f'cos_{k}'].std():.4f} |")
    lines += [f"| topic_true sentence | {ev.cos_topic_true.mean():.4f} | {ev.cos_topic_true.std():.4f} |",
              f"| topic_foreign sentence | {ev.cos_topic_foreign.mean():.4f} | {ev.cos_topic_foreign.std():.4f} |",
              f"| (S1) own full explanation | {ev.cos_own_explanation_s1.mean():.4f} | {ev.cos_own_explanation_s1.std():.4f} |",
              f"| (S1) empty explanation | {ev.cos_empty_s1.mean():.4f} | {ev.cos_empty_s1.std():.4f} |",
              "", f"- mean s_conf {ev.s_conf.mean():+.5f} (sd {ev.s_conf.std():.5f}); mean s_conflict {ev.s_conflict.mean():+.5f} (sd {ev.s_conflict.std():.5f})",
              "", "## Ten fixed rows (eval rows 0,16,…,144)", "",
              "| stim | topic_true | topic_foreign | cos true | cos foreign | repe s | entropy | s_conf |", "|---|---|---|---|---|---|---|---|"]
    for i in FIXED_ROWS:
        r = df[df.stim_idx == i].iloc[0]
        lines.append(f"| {i} | {r.topic_true} | {r.topic_foreign} | {r.cos_topic_true:.4f} | {r.cos_topic_foreign:.4f} | {r.repe_s_diff:+.4f} | {r.entropy_nats:.3f} | {r.s_conf:+.4f} |")
    lines.append("")
    (L.OVERNIGHT / "t1_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_T1={"auroc": b_topic, "outcome": out}, auroc_all=b_topic_all, auroc_subset_topic_absent=b_topic_sub,
             repe={"centred": b_repe_c, "raw": b_repe_r, "diff": b_repe_d, "s_ci": ci_repe}, s_topic_ci=ci_stopic,
             claims={"true_corrupt": ci_tc, "true_para": ci_tp, "para_corrupt": ci_pc, "true_det": ci_td}, spearman=sp)
    L.log(f"T1 done: AUROC={b_topic['auroc']:.4f} [{b_topic['lo']:.4f},{b_topic['hi']:.4f}] -> {out}; RepE centred {b_repe_c['auroc']:.4f}")


if __name__ == "__main__":
    main()

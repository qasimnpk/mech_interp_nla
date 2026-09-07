"""T2 — forced-prefix readout from the verbalizer (PLAN.md round 3; AV forward only, no generation).

  uv run python overnight/t2_prefix.py

Construction: default AV prompt with the activation injected exactly as nla_lib.AV.verbalize does
(marker row overwritten by v * 150 / ||v||), then the assistant turn is PREFILLED with text and the
next-token logits are read.  Prefill and candidate are tokenised separately (add_special_tokens=False)
and concatenated; the candidate carries a leading space.
Format 1 (yes/no):  prefill '<explanation>\nQuestion: {q} Answer:' ; score = logit(' Yes') - logit(' No').
  q_true    = 'Is this activation from a text about {topic_true}?'
  q_foreign = 'Is this activation from a text about {topic_foreign}?'
  q_conf    = 'Is the model confident about the next token?'
  q_torn    = 'Is the model torn between two continuations?'
Format 2 (candidate continuation): prefill '<explanation>\nThe passage concerns' ; summed log-prob of
  ' {topic_true}' vs ' {topic_foreign}' (unnormalised and per-token), under (a) the stimulus's own
  activation, (b) the foreign stimulus's activation (swap control), (c) no injection (raw marker embedding,
  asserted).  Claims: for the accepted S3 pairs whose corruption changes exactly one word (same word
  count), prefill '<explanation>\n' + claim words before the changed word, compare log-prob of the
  original vs the corrupted word (injected and no-injection).  corrupt_det pairs likewise where present.
Kill T2 (pre-registered, stage text): AUROC of the candidate-continuation score (unnormalised summed
log-prob) true vs foreign topic over the 160 evaluation stimuli, paired bootstrap by document <= 0.60 -> MET.
The yes/no AUROC is logged against the same threshold as 'T2-yesno' (threshold-table wording).
Every statistic is also reported on the subset where topic_true does NOT appear in the default explanation.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t1_arprobe import auroc, boot_auroc, boot_spearman, detok, load_triples, auroc_outcome  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

THRESH = 0.60
PREFILL_YN = "<explanation>\nQuestion: {q} Answer:"
PREFILL_CC = "<explanation>\nThe passage concerns"
PREFILL_CLAIM = "<explanation>\n"
Q = {"true": "Is this activation from a text about {topic}?", "foreign": "Is this activation from a text about {topic}?",
     "conf": "Is the model confident about the next token?", "torn": "Is the model torn between two continuations?"}
FIXED_ROWS = list(range(40, 200, 16))


class Prefix:
    def __init__(self, av: L.AV):
        self.av = av
        self.ids, self.inj_pos, self.base = av.prompt(None)
        self.marker_id = av.meta["tokens"]["injection_token_id"]
        assert int(self.ids[0, self.inj_pos]) == self.marker_id
        self.yes = av.tok.encode(" Yes", add_special_tokens=False); self.no = av.tok.encode(" No", add_special_tokens=False)
        self.yes_ok = len(self.yes) == 1 and len(self.no) == 1
        self._emb_cache: dict[str, torch.Tensor] = {}
        self.n_forward = 0

    def inject(self, vec: torch.Tensor | None) -> torch.Tensor:
        e = self.base.clone()
        if vec is None:
            raw = self.av.embed(torch.tensor([[self.marker_id]], device=L.DEVICE))[0, 0]
            assert torch.equal(e[0, self.inj_pos], raw), "no-injection control: marker embedding is not the raw embedding"
            return e
        v = vec.float()
        e[0, self.inj_pos] = (v / v.norm().clamp_min(1e-12) * self.av.scale).to(L.DEVICE, torch.bfloat16)
        return e

    def emb(self, text: str) -> tuple[torch.Tensor, list[int]]:
        ids = self.av.tok(text, add_special_tokens=False)["input_ids"]
        with torch.inference_mode():
            return self.av.embed(torch.tensor([ids], device=L.DEVICE)), ids

    def logits_after(self, vec, prefill: str) -> torch.Tensor:
        """Next-token logits (fp32 CPU [V]) after prompt(+injection) + prefill."""
        pe, _ = self.emb(prefill)
        x = torch.cat([self.inject(vec), pe], 1)
        with torch.inference_mode():
            lg = self.av.model(inputs_embeds=x, attention_mask=torch.ones(x.shape[:2], device=L.DEVICE, dtype=torch.long), use_cache=False).logits[0, -1]
        self.n_forward += 1
        return lg.float().cpu()

    def yesno(self, vec, q: str) -> float:
        lg = self.logits_after(vec, PREFILL_YN.format(q=q))
        return float(lg[self.yes[0]] - lg[self.no[0]]) if self.yes_ok else float(torch.logsumexp(lg[self.yes], 0) - torch.logsumexp(lg[self.no], 0))

    def cont_logprob(self, vec, prefill: str, cand: str) -> tuple[float, int]:
        """Summed log-prob of cand tokens (tokenised separately, appended after prefill)."""
        pe, pids = self.emb(prefill)
        ce, cids = self.emb(cand)
        assert len(cids) >= 1, cand
        x = torch.cat([self.inject(vec), pe, ce], 1)
        with torch.inference_mode():
            lg = self.av.model(inputs_embeds=x, attention_mask=torch.ones(x.shape[:2], device=L.DEVICE, dtype=torch.long), use_cache=False).logits[0]
        self.n_forward += 1
        n_prompt = self.ids.shape[1] + len(pids)
        lp = torch.log_softmax(lg[n_prompt - 1: n_prompt - 1 + len(cids)].float(), -1).cpu()
        return float(sum(lp[k, cids[k]] for k in range(len(cids)))), len(cids)


def single_word_diff(a: str, b: str):
    wa, wb = a.split(), b.split()
    if len(wa) != len(wb):
        return None
    d = [k for k in range(len(wa)) if wa[k] != wb[k]]
    if len(d) != 1:
        return None
    k = d[0]
    return k, " ".join(wa[:k]), wa[k], wb[k]


def main():
    S = L.Settings("t2", threshold=THRESH, prefill_yesno=PREFILL_YN, prefill_cc=PREFILL_CC, prefill_claim=PREFILL_CLAIM, questions=Q,
                   tokenisation="prefill and candidate tokenised separately with add_special_tokens=False and concatenated; candidate has a leading space (none when the changed word is the first word)",
                   no_injection="marker row left as the raw embedding of token 149705 (asserted equal)",
                   kill="AUROC of unnormalised summed log-prob of ' {topic_true}' vs ' {topic_foreign}' after PREFILL_CC with own activation, eval, paired bootstrap by stimulus; per-token version reported",
                   claim_rule="accepted S3 pairs with equal word count and exactly one differing word (str.split); prefix = words before it", fixed_rows=FIXED_ROWS, evaluation_set="stimuli 40-199")
    timings = {}
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    ent = pd.read_csv(L.OVERNIGHT / "t0_entropy.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    acts = np.load(L.OUT / "acts_L20.npz"); h20 = acts["h20"]
    triples = load_triples()
    topics = [detok(t) for t in top.topic_true]; foreign = list(top.foreign_stim_idx)

    t0 = time.time()
    av = L.AV()
    timings["av_load_s"] = time.time() - t0
    P = Prefix(av)
    S.update(yes_ids=P.yes, no_ids=P.no, yes_no_single_token=P.yes_ok, prompt_tokens=int(P.ids.shape[1]), marker_pos=P.inj_pos)
    L.log(f"' Yes'={P.yes} ' No'={P.no} single-token={P.yes_ok}")

    # ---------------- no-injection caches (topic-dependent quantities are stimulus-independent without injection)
    noinj_yn_topic = {}; noinj_cc = {}
    t0 = time.time()
    for t in sorted(set(topics)):
        noinj_yn_topic[t] = P.yesno(None, Q["true"].format(topic=t))
        noinj_cc[t] = P.cont_logprob(None, PREFILL_CC, " " + t)
    noinj_conf = P.yesno(None, Q["conf"]); noinj_torn = P.yesno(None, Q["torn"])
    L.log(f"no-injection cache: {P.n_forward} forwards in {time.time() - t0:.0f}s")

    rows = []
    t0 = time.time()
    for i in range(200):
        j = foreign[i]; tt, tf = topics[i], topics[j]
        h = torch.from_numpy(h20[i]); hj = torch.from_numpy(h20[j])
        row = {"stim_idx": i, "doc_idx": int(top.doc_idx[i]), "split": L.split_of(i), "token_type": ent.token_type[i], "entropy_nats": float(ent.entropy_nats[i]),
               "top1_prob": float(ent.top1_prob[i]), "topic_true": tt, "topic_foreign": tf, "foreign_stim_idx": j,
               "topic_in_default_explanation": bool(top.topic_in_default_explanation[i]), "error": ""}
        try:
            row["yn_true"] = P.yesno(h, Q["true"].format(topic=tt)); row["yn_foreign"] = P.yesno(h, Q["foreign"].format(topic=tf))
            row["yn_conf"] = P.yesno(h, Q["conf"]); row["yn_torn"] = P.yesno(h, Q["torn"])
            row["yn_true_noinj"] = noinj_yn_topic[tt]; row["yn_foreign_noinj"] = noinj_yn_topic[tf]; row["yn_conf_noinj"] = noinj_conf; row["yn_torn_noinj"] = noinj_torn
            row["yn_true_swap"] = P.yesno(hj, Q["true"].format(topic=tt)); row["yn_foreign_swap"] = P.yesno(hj, Q["foreign"].format(topic=tf))
            lt, nt = P.cont_logprob(h, PREFILL_CC, " " + tt); lf, nf = P.cont_logprob(h, PREFILL_CC, " " + tf)
            row.update({"cc_true": lt, "cc_foreign": lf, "n_tok_true": nt, "n_tok_foreign": nf, "cc_true_pt": lt / nt, "cc_foreign_pt": lf / nf})
            st, _ = P.cont_logprob(hj, PREFILL_CC, " " + tt); sf, _ = P.cont_logprob(hj, PREFILL_CC, " " + tf)
            row.update({"cc_true_swap": st, "cc_foreign_swap": sf, "cc_true_swap_pt": st / nt, "cc_foreign_swap_pt": sf / nf})
            row.update({"cc_true_noinj": noinj_cc[tt][0], "cc_foreign_noinj": noinj_cc[tf][0], "cc_true_noinj_pt": noinj_cc[tt][0] / nt, "cc_foreign_noinj_pt": noinj_cc[tf][0] / nf})
            row["cc_true_corr"] = lt - noinj_cc[tt][0]; row["cc_foreign_corr"] = lf - noinj_cc[tf][0]
        except Exception:
            row["error"] = traceback.format_exc(); L.log(f"T2 FAILED on stim {i}")
        rows.append(row)
        if i % 25 == 24:
            L.log(f"stim {i + 1}/200, forwards {P.n_forward} ({(time.time() - t0) / max(1, P.n_forward):.2f}s each)")
    df = pd.DataFrame(rows)
    df.to_csv(L.OVERNIGHT / "t2_scores.csv", index=False)
    timings["av_s_per_forward_topics"] = (time.time() - t0) / max(1, P.n_forward)

    # ---------------- claims: single-word corruptions
    crow = []
    t0 = time.time(); n0 = P.n_forward
    for r in triples.itertuples():
        for et, txt in [("corrupt", r.corrupt), ("corrupt_det", r.corrupt_det if r.has_det else None)]:
            if txt is None:
                continue
            sw = single_word_diff(r.claim, txt)
            rec = {"row": r.row, "stim_idx": r.stim_idx, "claim_idx": r.claim_idx, "n_claims": r.n_claims, "is_last": r.claim_idx == r.n_claims - 1,
                   "edit_type": et, "single_word": sw is not None, "error": ""}
            if sw is None:
                crow.append(rec); continue
            k, prefix, w_orig, w_corr = sw
            rec.update({"word_pos": k, "word_orig": w_orig, "word_corrupt": w_corr})
            try:
                h = torch.from_numpy(h20[r.stim_idx])
                lead = " " if k > 0 else ""
                pre = PREFILL_CLAIM + prefix
                lo, no_ = P.cont_logprob(h, pre, lead + w_orig); lc, nc = P.cont_logprob(h, pre, lead + w_corr)
                lo0, _ = P.cont_logprob(None, pre, lead + w_orig); lc0, _ = P.cont_logprob(None, pre, lead + w_corr)
                rec.update({"lp_orig": lo, "lp_corrupt": lc, "n_tok_orig": no_, "n_tok_corrupt": nc, "d_inj": lo - lc,
                            "lp_orig_noinj": lo0, "lp_corrupt_noinj": lc0, "d_noinj": lo0 - lc0, "d_inj_minus_noinj": (lo - lc) - (lo0 - lc0)})
            except Exception:
                rec["error"] = traceback.format_exc(); L.log(f"T2 claim FAILED on row {r.row}")
            crow.append(rec)
        if len(crow) % 200 == 0:
            L.log(f"claims {len(crow)} rows, forwards {P.n_forward}")
    cl = pd.DataFrame(crow)
    cl.to_csv(L.OVERNIGHT / "t2_claims.csv", index=False)
    timings["av_s_per_forward_claims"] = (time.time() - t0) / max(1, P.n_forward - n0); timings["n_av_forward"] = P.n_forward
    av.free()

    # ---------------- statistics
    ok = df[df.error == ""]
    ev = ok[ok.split == "eval"].reset_index(drop=True)
    sub = ev[~ev.topic_in_default_explanation].reset_index(drop=True)

    def stats(e):
        d = {}
        d["cc"] = boot_auroc(e.cc_true, e.cc_foreign); d["cc_pt"] = boot_auroc(e.cc_true_pt, e.cc_foreign_pt)
        d["cc_noinj"] = boot_auroc(e.cc_true_noinj, e.cc_foreign_noinj); d["cc_noinj_pt"] = boot_auroc(e.cc_true_noinj_pt, e.cc_foreign_noinj_pt)
        d["cc_corr"] = boot_auroc(e.cc_true_corr, e.cc_foreign_corr)
        d["cc_swap_prefers_foreign"] = boot_auroc(e.cc_foreign_swap, e.cc_true_swap); d["cc_swap_prefers_foreign_pt"] = boot_auroc(e.cc_foreign_swap_pt, e.cc_true_swap_pt)
        d["frac_cc_true_gt_foreign"] = float((e.cc_true > e.cc_foreign).mean()); d["frac_cc_swap_foreign_gt_true"] = float((e.cc_foreign_swap > e.cc_true_swap).mean())
        d["frac_cc_noinj_true_gt_foreign"] = float((e.cc_true_noinj > e.cc_foreign_noinj).mean())
        d["yn"] = boot_auroc(e.yn_true, e.yn_foreign); d["yn_noinj"] = boot_auroc(e.yn_true_noinj, e.yn_foreign_noinj)
        d["yn_swap_prefers_foreign"] = boot_auroc(e.yn_foreign_swap, e.yn_true_swap)
        d["yn_corr"] = boot_auroc(e.yn_true - e.yn_true_noinj, e.yn_foreign - e.yn_foreign_noinj)
        d["frac_yn_true_gt_foreign"] = float((e.yn_true > e.yn_foreign).mean())
        d["mean_yn"] = {k: float(e[f"yn_{k}"].mean()) for k in ["true", "foreign", "conf", "torn", "true_noinj", "foreign_noinj", "conf_noinj", "torn_noinj"]}
        d["sp_conf"] = boot_spearman(e.yn_conf, -e.entropy_nats); d["sp_torn"] = boot_spearman(e.yn_torn, e.entropy_nats)
        d["sp_conf_bins"] = {tt: boot_spearman(e.yn_conf[e.token_type == tt], -e.entropy_nats[e.token_type == tt]) for tt in ["punctuation", "word_initial", "word_piece"]}
        d["sp_torn_bins"] = {tt: boot_spearman(e.yn_torn[e.token_type == tt], e.entropy_nats[e.token_type == tt]) for tt in ["punctuation", "word_initial", "word_piece"]}
        d["n"] = int(len(e))
        return d

    st_ev, st_sub = stats(ev), stats(sub)
    out = auroc_outcome(st_ev["cc"])
    L.append_disconfirmation("T2", "T2", "AUROC of candidate-continuation log-prob (' {topic_true}' vs ' {topic_foreign}' after '<explanation>\\nThe passage concerns'), eval, CI95 by document ≤ 0.60",
                             f"AUROC={st_ev['cc']['auroc']:.4f} CI95=[{st_ev['cc']['lo']:.4f},{st_ev['cc']['hi']:.4f}] n={st_ev['cc']['n']}; per-token {st_ev['cc_pt']['auroc']:.4f} [{st_ev['cc_pt']['lo']:.4f},{st_ev['cc_pt']['hi']:.4f}]; "
                             f"no-injection {st_ev['cc_noinj']['auroc']:.4f} [{st_ev['cc_noinj']['lo']:.4f},{st_ev['cc_noinj']['hi']:.4f}]; prior-corrected {st_ev['cc_corr']['auroc']:.4f}; swap prefers foreign {st_ev['cc_swap_prefers_foreign']['auroc']:.4f}; "
                             f"topic-absent subset (n={st_sub['n']}) {st_sub['cc']['auroc']:.4f} [{st_sub['cc']['lo']:.4f},{st_sub['cc']['hi']:.4f}]",
                             out, "MET would mean the prefilled-continuation readout cannot tell the document's own topic from a foreign one")
    out_yn = auroc_outcome(st_ev["yn"])
    L.append_disconfirmation("T2", "T2-yesno", "AUROC of yes−no logit for the true vs foreign topic question, eval, CI95 by document ≤ 0.60 (threshold-table wording; reported alongside)",
                             f"AUROC={st_ev['yn']['auroc']:.4f} CI95=[{st_ev['yn']['lo']:.4f},{st_ev['yn']['hi']:.4f}] n={st_ev['yn']['n']}; no-injection {st_ev['yn_noinj']['auroc']:.4f}; "
                             f"mean yes−no under no injection: true-q {st_ev['mean_yn']['true_noinj']:+.3f} foreign-q {st_ev['mean_yn']['foreign_noinj']:+.3f} conf {st_ev['mean_yn']['conf_noinj']:+.3f} torn {st_ev['mean_yn']['torn_noinj']:+.3f}",
                             out_yn, "a general preference for Yes or for the commoner noun is not evidence; compare with the no-injection AUROC")

    cok = cl[(cl.error == "") & cl.single_word]
    cc_ = cok[cok.edit_type == "corrupt"]; cd_ = cok[cok.edit_type == "corrupt_det"]
    ci_c = L.cluster_bootstrap_mean(cc_.d_inj, cc_.stim_idx); ci_c0 = L.cluster_bootstrap_mean(cc_.d_noinj, cc_.stim_idx); ci_cm = L.cluster_bootstrap_mean(cc_.d_inj_minus_noinj, cc_.stim_idx)
    ci_d = L.cluster_bootstrap_mean(cd_.d_inj, cd_.stim_idx); ci_d0 = L.cluster_bootstrap_mean(cd_.d_noinj, cd_.stim_idx); ci_dm = L.cluster_bootstrap_mean(cd_.d_inj_minus_noinj, cd_.stim_idx)
    L.append_disconfirmation("T2", "T2-claims", "single-word claim corruptions (reported, not a pre-registered kill): CI95 of mean[(lp_orig − lp_corrupt) injected − same with no injection]",
                             f"LLM corrupt n={ci_cm['n']} n_expl={ci_cm['n_clusters']}: injected {ci_c['mean']:.4f} [{ci_c['lo']:.4f},{ci_c['hi']:.4f}], no-inj {ci_c0['mean']:.4f}, diff {ci_cm['mean']:.4f} [{ci_cm['lo']:.4f},{ci_cm['hi']:.4f}], frac orig>corrupt inj {(cc_.d_inj > 0).mean():.3f} noinj {(cc_.d_noinj > 0).mean():.3f}; "
                             f"det n={ci_dm['n']}: diff {ci_dm['mean']:.4f} [{ci_dm['lo']:.4f},{ci_dm['hi']:.4f}]",
                             L.outcome_ci_at_or_below(ci_cm, 0.0, min_n=100), "≤0 would mean the injected activation does not raise the original word over its corruption beyond the prompt-only prior")

    def fa(b):
        return f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"

    def fs(b):
        return f"{b['rho']:+.4f} [{b['lo']:+.4f},{b['hi']:+.4f}] n={b['n']}"

    lines = ["# T2 summary — forced-prefix readout from the verbalizer (AV forward only)", "",
             f"git {L.git_hash()[:8]}; settings in t2_settings.json; rows in t2_scores.csv (per stimulus) and t2_claims.csv", "",
             f"- AV forwards {timings['n_av_forward']} ({timings['av_s_per_forward_topics']:.2f} s each on topics, {timings['av_s_per_forward_claims']:.2f} s on claims); errors {int((df.error != '').sum())} stimuli, {int((cl.error != '').sum())} claim rows",
             f"- ' Yes' ids {P.yes}, ' No' ids {P.no}, single-token: {P.yes_ok}; prompt {int(P.ids.shape[1])} tokens, marker at {P.inj_pos}",
             f"- eval n={st_ev['n']}; topic-absent subset (topic_true not in default explanation) n={st_sub['n']}",
             "", "## Kill T2 — candidate continuation (evaluation, paired AUROC, bootstrap by document)", "",
             f"- summed log-prob ' {{topic_true}}' vs ' {{topic_foreign}}', own activation: {fa(st_ev['cc'])} → **{out}**",
             f"- per-token normalised: {fa(st_ev['cc_pt'])}",
             f"- no injection (prior only): {fa(st_ev['cc_noinj'])}; per-token {fa(st_ev['cc_noinj_pt'])}; frac true>foreign {st_ev['frac_cc_noinj_true_gt_foreign']:.3f}",
             f"- prior-corrected (lp − lp_noinj): {fa(st_ev['cc_corr'])}",
             f"- swap control (foreign activation injected; AUROC that it prefers the foreign topic): {fa(st_ev['cc_swap_prefers_foreign'])}; per-token {fa(st_ev['cc_swap_prefers_foreign_pt'])}; frac {st_ev['frac_cc_swap_foreign_gt_true']:.3f}",
             f"- fraction cc_true > cc_foreign (own activation): {st_ev['frac_cc_true_gt_foreign']:.3f}",
             f"- topic token counts: true mean {ev.n_tok_true.mean():.2f}, foreign mean {ev.n_tok_foreign.mean():.2f}",
             "", "## Yes/no format (evaluation)", "",
             f"- AUROC yes−no true-q vs foreign-q, injected: {fa(st_ev['yn'])} → {out_yn} (threshold-table wording); no injection {fa(st_ev['yn_noinj'])}; prior-corrected {fa(st_ev['yn_corr'])}; swap prefers foreign {fa(st_ev['yn_swap_prefers_foreign'])}; frac true>foreign {st_ev['frac_yn_true_gt_foreign']:.3f}",
             "", "| question | mean yes−no injected | mean yes−no no injection |", "|---|---|---|"]
    for k in ["true", "foreign", "conf", "torn"]:
        lines.append(f"| {k} | {st_ev['mean_yn'][k]:+.3f} | {st_ev['mean_yn'][k + '_noinj']:+.3f} |")
    lines += ["", "## Same statistics on the topic-absent subset", "",
              f"- cc AUROC {fa(st_sub['cc'])}; per-token {fa(st_sub['cc_pt'])}; no-inj {fa(st_sub['cc_noinj'])}; prior-corrected {fa(st_sub['cc_corr'])}; swap prefers foreign {fa(st_sub['cc_swap_prefers_foreign'])}",
              f"- yes/no AUROC {fa(st_sub['yn'])}; no-inj {fa(st_sub['yn_noinj'])}; prior-corrected {fa(st_sub['yn_corr'])}",
              f"- Spearman(yn_conf, −entropy) {fs(st_sub['sp_conf'])}; Spearman(yn_torn, entropy) {fs(st_sub['sp_torn'])}",
              "", "## Confidence / conflict questions vs next-token entropy (evaluation)", "",
              "| statistic | pooled | punctuation | word_initial | word_piece |", "|---|---|---|---|---|",
              f"| Spearman(yes−no conf, −entropy) | {fs(st_ev['sp_conf'])} | " + " | ".join(fs(st_ev['sp_conf_bins'][t]) for t in ["punctuation", "word_initial", "word_piece"]) + " |",
              f"| Spearman(yes−no torn, entropy) | {fs(st_ev['sp_torn'])} | " + " | ".join(fs(st_ev['sp_torn_bins'][t]) for t in ["punctuation", "word_initial", "word_piece"]) + " |",
              "", "## Single-word claim corruptions (claim prefix prefilled; log-prob of original vs corrupted word)", "",
              f"- S3 pairs: corrupt {int((cl.edit_type == 'corrupt').sum())} (single-word {int(((cl.edit_type == 'corrupt') & cl.single_word).sum())}); corrupt_det {int((cl.edit_type == 'corrupt_det').sum())} (single-word {int(((cl.edit_type == 'corrupt_det') & cl.single_word).sum())})",
              "", "| edit | n | n_expl | mean lp_orig − lp_corrupt injected | CI95 | no injection | diff (inj − noinj) | CI95 | frac orig>corrupt inj / noinj |", "|---|---|---|---|---|---|---|---|---|",
              f"| LLM corrupt | {ci_c['n']} | {ci_c['n_clusters']} | {ci_c['mean']:.4f} | [{ci_c['lo']:.4f},{ci_c['hi']:.4f}] | {ci_c0['mean']:.4f} | {ci_cm['mean']:.4f} | [{ci_cm['lo']:.4f},{ci_cm['hi']:.4f}] | {(cc_.d_inj > 0).mean():.3f} / {(cc_.d_noinj > 0).mean():.3f} |",
              f"| deterministic | {ci_d['n']} | {ci_d['n_clusters']} | {ci_d['mean']:.4f} | [{ci_d['lo']:.4f},{ci_d['hi']:.4f}] | {ci_d0['mean']:.4f} | {ci_dm['mean']:.4f} | [{ci_dm['lo']:.4f},{ci_dm['hi']:.4f}] | {(cd_.d_inj > 0).mean():.3f} / {(cd_.d_noinj > 0).mean():.3f} |"]
    if len(cc_):
        lc = cc_[cc_.is_last]; ci_l = L.cluster_bootstrap_mean(lc.d_inj_minus_noinj, lc.stim_idx)
        lines.append(f"| LLM corrupt, last claims only | {ci_l['n']} | {ci_l['n_clusters']} | {lc.d_inj.mean():.4f} | | {lc.d_noinj.mean():.4f} | {ci_l['mean']:.4f} | [{ci_l['lo']:.4f},{ci_l['hi']:.4f}] | {(lc.d_inj > 0).mean():.3f} / {(lc.d_noinj > 0).mean():.3f} |")
    lines += ["", "## Ten fixed rows (eval rows 0,16,…,144)", "",
              "| stim | topic_true | topic_foreign | cc true | cc foreign | cc true noinj | cc foreign noinj | yn true | yn foreign | yn conf | entropy |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in FIXED_ROWS:
        r = df[df.stim_idx == i].iloc[0]
        lines.append(f"| {i} | {r.topic_true} | {r.topic_foreign} | {r.get('cc_true', float('nan')):.2f} | {r.get('cc_foreign', float('nan')):.2f} | {r.get('cc_true_noinj', float('nan')):.2f} | {r.get('cc_foreign_noinj', float('nan')):.2f} | "
                     f"{r.get('yn_true', float('nan')):+.2f} | {r.get('yn_foreign', float('nan')):+.2f} | {r.get('yn_conf', float('nan')):+.2f} | {r.entropy_nats:.3f} |")
    lines.append("")
    (L.OVERNIGHT / "t2_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_T2={"stats": st_ev["cc"], "outcome": out}, yesno_outcome=out_yn, eval_stats=st_ev, subset_stats=st_sub,
             claims={"corrupt": {"inj": ci_c, "noinj": ci_c0, "diff": ci_cm}, "det": {"inj": ci_d, "noinj": ci_d0, "diff": ci_dm}})
    L.log(f"T2 done: cc AUROC={st_ev['cc']['auroc']:.4f} [{st_ev['cc']['lo']:.4f},{st_ev['cc']['hi']:.4f}] -> {out}; yes/no {st_ev['yn']['auroc']:.4f}; no-inj cc {st_ev['cc_noinj']['auroc']:.4f}")


if __name__ == "__main__":
    main()

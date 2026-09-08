"""U1 — does NLA training improve targeted activation readout? Base-model control (PLAN.md round 3c; REQUIRED).

  uv run python overnight/u1_base.py

"Baseline" = the un-finetuned Qwen/Qwen2.5-7B-Instruct weights driven through the AV interface: identical prompt token
ids (AV tokenizer, asserted equal under the TARGET tokenizer), marker position, injection rescale to norm 150, attention
mask/positions, candidate strings, likelihood aggregation (summed log-prob of every token of ' ' + c; per-token mean also
recorded), dtype bf16, scoring code (t2_prefix.Prefix, unchanged). The only difference is the weights: the TargetAsAV class
below builds nla_lib.AV's state from the AV checkpoint's nla_meta/tokenizer and loads the model from the TARGET snapshot
(the role assert of nla_lib.AV is bypassed and logged). The AV's own scores are NOT recomputed: they are read from
t2a_scores.csv (p3), t2_scores.csv (PREFILL_CC) and t2c_pairs.csv (p1, p2), which used the same code path and the same
activations; the candidate token counts are asserted equal.
Conditions: own activation, matched swapped activation (topic: (i+100) mod 200; entity: the twin), no injection
(prior; each interpreter corrected with its own no-injection run).
Text-only reference (reported, no kill): the un-finetuned model reads the document prefix tokens 0..pos (inclusive) as
plain text (no chat template) followed by '\nThe document is about', scoring the same two titles; prior = the same
prompt with the prefix removed.
Kill U1 (pre-registered): CI (cluster bootstrap by document, 1000 draws, seed 0) of the paired difference
[AV − baseline] in RAW p3 within-pair choice accuracy over the 160 evaluation documents ≤ 0 → MET.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix, PREFILL_CC  # noqa: E402
from overnight.t2a_audit import P3  # noqa: E402
from overnight.t2c_entity import NOUNS, P1, P2  # noqa: E402
from overnight.t1_arprobe import auroc, boot_auroc, detok  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: E402

TEXT_SUFFIX = "\nThe document is about"
MAX_LEN = 512
N_BOOT, SEED = 1000, 0
FIXED_ROWS = list(range(40, 200, 16))
MIN_N = 100


class TargetAsAV(L.AV):
    """nla_lib.AV with the un-finetuned TARGET weights; everything else (meta, tokenizer, prompt, injection) from the AV checkpoint."""

    def __init__(self):
        ckpt = L.snapshot(L.AV_REPO)
        self.meta = L.load_meta(ckpt)
        assert self.meta["role"] == "av" and self.meta["extraction_layer_index"] == L.LAYER  # meta is the AV's; the model below is NOT (role assert bypassed by construction)
        self.scale = float(self.meta["extraction"]["injection_scale"])
        self.tok = AutoTokenizer.from_pretrained(ckpt)
        tgt_ckpt = L.snapshot(L.TARGET)
        self.model = AutoModelForCausalLM.from_pretrained(tgt_ckpt, dtype=torch.bfloat16, device_map=L.DEVICE).eval()
        assert self.model.config.num_hidden_layers == 28
        self.embed = self.model.get_input_embeddings()
        self.default_prompt = self.meta["prompt_templates"]["av"].format(injection_char=self.meta["tokens"]["injection_char"])
        self._cache = {}
        ids, p, _ = self.prompt(None)
        # identical prompt ids under the TARGET's own tokenizer
        ttok = AutoTokenizer.from_pretrained(tgt_ckpt)
        text = ttok.apply_chat_template([{"role": "user", "content": self.default_prompt}], tokenize=False, add_generation_prompt=True)
        tids = ttok(text, add_special_tokens=False)["input_ids"]
        assert tids == ids[0].tolist(), "TARGET tokenizer gives different prompt ids than the AV tokenizer"
        self.target_tok = ttok
        L.log(f"TargetAsAV loaded: TARGET weights ({Path(tgt_ckpt).name}) in the AV interface; prompt {ids.shape[1]} tok, marker at {p}, injection_scale={self.scale}; nla_lib.AV role assert BYPASSED by construction")


def boot_mean(vals, clusters):
    return L.cluster_bootstrap_mean(np.asarray(vals, float), clusters, n_boot=N_BOOT, seed=SEED)


def fm(c, d=3):
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"


def fa(b):
    return f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"


def main():
    S = L.Settings("u1", prefixes={"p3": P3, "cc": PREFILL_CC, "p1": P1, "p2": P2}, nouns=NOUNS, text_suffix=TEXT_SUFFIX, max_len=MAX_LEN,
                   baseline="Qwen/Qwen2.5-7B-Instruct weights loaded from the cached snapshot into nla_lib.AV's interface (TargetAsAV); AV meta/tokenizer/prompt/injection unchanged; role assert bypassed by construction (logged)",
                   av_scores_source={"p3": "t2a_scores.csv", "cc": "t2_scores.csv", "p1/p2": "t2c_pairs.csv"},
                   candidate_rule="' ' + detok(topic) / ' ' + entity, tokenised separately (add_special_tokens=False), appended after the prefill; summed log-prob; per-token mean recorded",
                   no_injection="marker row left as the raw embedding of token 149705 (asserted in Prefix.inject); each interpreter's prior from its own run",
                   text_only="doc ids[0..pos] (inclusive) + tok('\\nThe document is about') + tok(' ' + title), no chat template, no special tokens; prior = tok('\\nThe document is about') + tok(' ' + title)",
                   kill="CI (cluster bootstrap by document, 1000 draws, seed 0) of paired [AV − baseline] raw p3 within-pair choice accuracy, eval n=160 ≤ 0 → MET",
                   n_boot=N_BOOT, seed=SEED, fixed_rows=FIXED_ROWS, evaluation_set="stimuli 40-199")
    timings = {}
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    t2a = pd.read_csv(L.OVERNIGHT / "t2a_scores.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    t2 = pd.read_csv(L.OVERNIGHT / "t2_scores.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    t2c = pd.read_csv(L.OVERNIGHT / "t2c_pairs.csv").sort_values("pair_id").reset_index(drop=True)
    assert len(t2a) == 200 and (t2a.error == "").all() and len(t2) == 200 and (t2.error == "").all() and len(t2c) == 40 and t2c.error.isna().all()
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]; H = np.load(L.OUT / "c2_acts.npz")["H"]
    topics = [detok(t) for t in top.topic_true]; foreign = list(top.foreign_stim_idx)
    assert topics == list(t2a.topic_true) and foreign == list(t2a.foreign_stim_idx) and list(t2.foreign_stim_idx) == foreign
    from datasets import load_dataset
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]

    t0 = time.time(); base = TargetAsAV(); timings["load_s"] = time.time() - t0
    P = Prefix(base)
    assert int(P.ids.shape[1]) == 125 and P.inj_pos == 111, (P.ids.shape, P.inj_pos)  # as in t2/t2a/t2c settings
    S.update(prompt_tokens=int(P.ids.shape[1]), marker_pos=P.inj_pos, target_snapshot=Path(L.snapshot(L.TARGET)).name)
    noinj = {}

    def lp0(prefill, cand):
        k = (prefill, cand)
        if k not in noinj:
            noinj[k] = P.cont_logprob(None, prefill, cand)
        return noinj[k]

    # ---------------- topic: p3 (primary) and PREFILL_CC (secondary)
    rows = []; t0 = time.time()
    for i in range(200):
        j = foreign[i]; tt, tf = topics[i], topics[j]
        h = torch.from_numpy(h20[i]); hj = torch.from_numpy(h20[j])
        row = {"stim_idx": i, "doc_idx": int(top.doc_idx[i]), "split": L.split_of(i), "topic_true": tt, "topic_foreign": tf, "foreign_stim_idx": j, "error": ""}
        try:
            for px, pre in [("p3", P3), ("cc", PREFILL_CC)]:
                lt, nt = P.cont_logprob(h, pre, " " + tt); lf, nf = P.cont_logprob(h, pre, " " + tf)
                s_t, _ = P.cont_logprob(hj, pre, " " + tt); s_f, _ = P.cont_logprob(hj, pre, " " + tf)
                l0t, _ = lp0(pre, " " + tt); l0f, _ = lp0(pre, " " + tf)
                row.update({f"{px}_n_tok_true": nt, f"{px}_n_tok_foreign": nf, f"base_{px}_true": lt, f"base_{px}_foreign": lf, f"base_{px}_true_swap": s_t, f"base_{px}_foreign_swap": s_f,
                            f"base_{px}_true_noinj": l0t, f"base_{px}_foreign_noinj": l0f, f"base_{px}_true_pt": lt / nt, f"base_{px}_foreign_pt": lf / nf})
            # AV's numbers from the round-3/3b files (same code path, same activations)
            a = t2a.iloc[i]; c = t2.iloc[i]
            assert a.n_tok_true == row["p3_n_tok_true"] and a.n_tok_foreign == row["p3_n_tok_foreign"] and c.n_tok_true == row["cc_n_tok_true"] and c.n_tok_foreign == row["cc_n_tok_foreign"], i
            row.update({"av_p3_true": a.p3_true, "av_p3_foreign": a.p3_foreign, "av_p3_true_swap": a.p3_true_swap, "av_p3_foreign_swap": a.p3_foreign_swap, "av_p3_true_noinj": a.p3_true_noinj, "av_p3_foreign_noinj": a.p3_foreign_noinj,
                        "av_cc_true": c.cc_true, "av_cc_foreign": c.cc_foreign, "av_cc_true_swap": c.cc_true_swap, "av_cc_foreign_swap": c.cc_foreign_swap, "av_cc_true_noinj": c.cc_true_noinj, "av_cc_foreign_noinj": c.cc_foreign_noinj})
            # text-only reference (plain text; TARGET weights; no injection)
            ids = base.tok(ds[int(st.doc_idx[i])]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
            assert len(ids) == int(st.seq_len[i]) and base.tok.decode([ids[int(st.pos[i])]]) == st.token_str[i]
            prefix_ids = ids[: int(st.pos[i]) + 1]
            suf_ids = base.tok(TEXT_SUFFIX, add_special_tokens=False)["input_ids"]
            for nm, title in [("true", tt), ("foreign", tf)]:
                cids = base.tok(" " + title, add_special_tokens=False)["input_ids"]
                x = torch.tensor([prefix_ids + suf_ids + cids], device=L.DEVICE)
                with torch.inference_mode():
                    lg = base.model(input_ids=x, use_cache=False).logits[0]
                n0 = len(prefix_ids) + len(suf_ids)
                lp = torch.log_softmax(lg[n0 - 1: n0 - 1 + len(cids)].float(), -1).cpu()
                row[f"text_{nm}"] = float(sum(lp[k, cids[k]] for k in range(len(cids))))
                key = ("__text_prior__", title)
                if key not in noinj:
                    x0 = torch.tensor([suf_ids + cids], device=L.DEVICE)
                    with torch.inference_mode():
                        lg0 = base.model(input_ids=x0, use_cache=False).logits[0]
                    lp0_ = torch.log_softmax(lg0[len(suf_ids) - 1: len(suf_ids) - 1 + len(cids)].float(), -1).cpu()
                    noinj[key] = (float(sum(lp0_[k, cids[k]] for k in range(len(cids)))), len(cids))
                row[f"text_{nm}_noinj"] = noinj[key][0]; row[f"text_n_tok_{nm}"] = len(cids)
            row["text_prefix_tokens"] = len(prefix_ids)
        except Exception:
            row["error"] = traceback.format_exc(); L.log(f"U1 topic FAILED on stim {i}")
        rows.append(row)
        if i % 25 == 24:
            L.log(f"topic {i + 1}/200, AV-interface forwards {P.n_forward} ({(time.time() - t0) / max(1, i + 1):.1f} s/stim)")
    timings["topic_s_per_stim"] = (time.time() - t0) / 200; timings["n_forward_after_topic"] = P.n_forward
    df = pd.DataFrame(rows); df.to_csv(L.OVERNIGHT / "u1_topic.csv", index=False)

    # ---------------- entity: p1 (primary) and p2
    erows = []; t0 = time.time(); n0f = P.n_forward
    for r in t2c.itertuples():
        i = r.pair_id; noun = NOUNS[r.template_id]
        ha, hb = torch.from_numpy(H[i, 0]), torch.from_numpy(H[i, 1]); ca, cb = " " + r.entity_a, " " + r.entity_b
        row = {"pair_id": i, "template_id": r.template_id, "noun": noun, "entity_a": r.entity_a, "entity_b": r.entity_b, "error": ""}
        try:
            for px, tpl in [("p1", P1), ("p2", P2)]:
                pre = tpl.format(noun=noun)
                assert getattr(r, f"{px}_prefix") == pre
                la_a, na = P.cont_logprob(ha, pre, ca); lb_a, nb = P.cont_logprob(ha, pre, cb)
                la_b, _ = P.cont_logprob(hb, pre, ca); lb_b, _ = P.cont_logprob(hb, pre, cb)
                la_0, _ = lp0(pre, ca); lb_0, _ = lp0(pre, cb)
                assert na == getattr(r, f"{px}_n_tok_a") and nb == getattr(r, f"{px}_n_tok_b")
                row.update({f"{px}_n_tok_a": na, f"{px}_n_tok_b": nb, f"base_{px}_lp_a_given_ha": la_a, f"base_{px}_lp_b_given_ha": lb_a, f"base_{px}_lp_a_given_hb": la_b, f"base_{px}_lp_b_given_hb": lb_b,
                            f"base_{px}_lp_a_given_h0": la_0, f"base_{px}_lp_b_given_h0": lb_0, f"base_{px}_D_a": la_a - lb_a, f"base_{px}_D_b": la_b - lb_b, f"base_{px}_D_0": la_0 - lb_0,
                            f"av_{px}_D_a": getattr(r, f"{px}_D_a"), f"av_{px}_D_b": getattr(r, f"{px}_D_b"), f"av_{px}_D_0": getattr(r, f"{px}_D_0")})
        except Exception:
            row["error"] = traceback.format_exc(); L.log(f"U1 entity FAILED on pair {i}")
        erows.append(row)
    timings["entity_s_per_forward"] = (time.time() - t0) / max(1, P.n_forward - n0f); timings["n_forward_total"] = P.n_forward
    ed = pd.DataFrame(erows); ed.to_csv(L.OVERNIGHT / "u1_entity.csv", index=False)
    base.free()

    # ---------------- statistics: topic
    ok = df[df.error == ""].reset_index(drop=True); ev = ok[ok.split == "eval"].reset_index(drop=True)
    tx = ev[["stim_idx", "doc_idx", "topic_true", "topic_foreign", "text_true", "text_foreign", "text_true_noinj", "text_foreign_noinj", "text_prefix_tokens"]].copy(); tx.to_csv(L.OVERNIGHT / "u1_text.csv", index=False)
    pd.DataFrame(ok[["stim_idx", "split", "text_true", "text_foreign", "text_true_noinj", "text_foreign_noinj", "text_prefix_tokens"]]).to_csv(L.OVERNIGHT / "u1_text.csv", index=False)

    def topic_stats(e, who, px):
        g = lambda c: e[f"{who}_{px}_{c}"].values  # noqa: E731
        t, f, ts, fs, t0_, f0 = g("true"), g("foreign"), g("true_swap"), g("foreign_swap"), g("true_noinj"), g("foreign_noinj")
        d = {"acc_raw": (t > f).astype(float), "acc_corr": ((t - t0_) > (f - f0)).astype(float), "swap_raw": (fs > ts).astype(float), "swap_corr": ((fs - f0) > (ts - t0_)).astype(float), "acc_noinj": (t0_ > f0).astype(float)}
        out = {k: boot_mean(v, e.stim_idx.values) for k, v in d.items()}
        out["auroc_raw"] = boot_auroc(t, f); out["auroc_corr"] = boot_auroc(t - t0_, f - f0); out["auroc_swap"] = boot_auroc(fs, ts); out["auroc_noinj"] = boot_auroc(t0_, f0)
        out["_ind"] = d
        return out

    def text_stats(e):
        t, f, t0_, f0 = e.text_true.values, e.text_foreign.values, e.text_true_noinj.values, e.text_foreign_noinj.values
        d = {"acc_raw": (t > f).astype(float), "acc_corr": ((t - t0_) > (f - f0)).astype(float), "acc_noinj": (t0_ > f0).astype(float)}
        out = {k: boot_mean(v, e.stim_idx.values) for k, v in d.items()}
        out["auroc_raw"] = boot_auroc(t, f); out["auroc_corr"] = boot_auroc(t - t0_, f - f0); out["auroc_noinj"] = boot_auroc(t0_, f0); out["_ind"] = d
        return out

    TS = {(who, px): topic_stats(ev, who, px) for who in ["av", "base"] for px in ["p3", "cc"]}
    TX = text_stats(ev)
    paired = {}
    for px in ["p3", "cc"]:
        for k in ["acc_raw", "acc_corr", "swap_raw", "swap_corr"]:
            paired[(px, k)] = boot_mean(TS[("av", px)]["_ind"][k] - TS[("base", px)]["_ind"][k], ev.stim_idx.values)
        for k in ["acc_raw", "acc_corr"]:
            paired[(px, k + "_av_minus_text")] = boot_mean(TS[("av", px)]["_ind"][k] - TX["_ind"][k], ev.stim_idx.values)
            paired[(px, k + "_base_minus_text")] = boot_mean(TS[("base", px)]["_ind"][k] - TX["_ind"][k], ev.stim_idx.values)
    kill = paired[("p3", "acc_raw")]
    out = L.outcome_ci_at_or_below(kill, 0.0, min_n=MIN_N)

    # ---------------- statistics: entity
    eok = ed[ed.error == ""].reset_index(drop=True)

    def ent_stats(who, px):
        Da, Db, D0 = eok[f"{who}_{px}_D_a"].values, eok[f"{who}_{px}_D_b"].values, eok[f"{who}_{px}_D_0"].values; cl = eok.template_id.values
        acc = np.concatenate([Da > 0, Db < 0]).astype(float); accc = np.concatenate([(Da - D0) > 0, (Db - D0) < 0]).astype(float); cl2 = np.concatenate([cl, cl])
        d = {"donor": boot_mean(Da - Db, cl), "donor_frac_pos": boot_mean((Da - Db > 0).astype(float), cl), "both_raw": boot_mean(((Da > 0) & (Db < 0)).astype(float), cl),
             "both_corr": boot_mean((((Da - D0) > 0) & ((Db - D0) < 0)).astype(float), cl), "acc_raw": boot_mean(acc, cl2), "acc_corr": boot_mean(accc, cl2),
             "auroc": auroc(Da, Db), "mean_D0": float(D0.mean()), "_donor": Da - Db, "_acc": acc, "_accc": accc, "_cl2": cl2}
        return d

    ES = {(who, px): ent_stats(who, px) for who in ["av", "base"] for px in ["p1", "p2"]}
    epaired = {}
    for px in ["p1", "p2"]:
        epaired[(px, "donor")] = boot_mean(ES[("av", px)]["_donor"] - ES[("base", px)]["_donor"], eok.template_id.values)
        epaired[(px, "acc_raw")] = boot_mean(ES[("av", px)]["_acc"] - ES[("base", px)]["_acc"], ES[("av", px)]["_cl2"])
        epaired[(px, "acc_corr")] = boot_mean(ES[("av", px)]["_accc"] - ES[("base", px)]["_accc"], ES[("av", px)]["_cl2"])

    a3, b3 = TS[("av", "p3")], TS[("base", "p3")]
    L.append_disconfirmation("U1", "U1", "CI (cluster bootstrap by document) of paired [AV − baseline(un-finetuned Qwen2.5-7B-Instruct in the AV interface)] RAW p3 within-pair topic-choice accuracy, eval n=160 ≤ 0",
                             f"paired diff raw={fm(kill)} n={kill['n']}; AV raw acc {fm(a3['acc_raw'])} baseline raw acc {fm(b3['acc_raw'])}; prior-corrected: diff {fm(paired[('p3', 'acc_corr')])} (AV {a3['acc_corr']['mean']:.3f} base {b3['acc_corr']['mean']:.3f}); "
                             f"AUROC raw AV {a3['auroc_raw']['auroc']:.4f} base {b3['auroc_raw']['auroc']:.4f}; swap-following raw AV {a3['swap_raw']['mean']:.3f} base {b3['swap_raw']['mean']:.3f}; "
                             f"entity p1 donor sensitivity AV {fm(ES[('av', 'p1')]['donor'], 4)} base {fm(ES[('base', 'p1')]['donor'], 4)} paired diff {fm(epaired[('p1', 'donor')], 4)}; text-only raw acc {fm(TX['acc_raw'])} corr {fm(TX['acc_corr'])}",
                             out, "MET would mean NLA training does not improve this readout under the tested interface (not equivalence); if baseline matches the AV and both follow the donor, the readout is activation-dependent while the training advantage is not established")

    # ---------------- summary
    lines = ["# U1 summary — base-model control for the likelihood readout (TARGET weights in the AV interface)", "",
             f"git {L.git_hash()[:8]}; settings in u1_settings.json; rows in u1_topic.csv (200 stimuli), u1_entity.csv (40 pairs), u1_text.csv", "",
             f"- baseline = `{L.TARGET}` (snapshot {Path(L.snapshot(L.TARGET)).name[:8]}) loaded into `nla_lib.AV`'s interface via `TargetAsAV`; AV meta / tokenizer / prompt ids (125 tok, marker at 111, asserted equal under the TARGET tokenizer) / injection (norm 150, marker row replaced) / scoring code (`t2_prefix.Prefix`) unchanged; **the role assert of `nla_lib.AV` was bypassed by construction**",
             f"- AV scores are read from t2a_scores.csv (p3), t2_scores.csv (`The passage concerns`), t2c_pairs.csv (p1, p2) — same code path and activations; candidate token counts asserted equal per item",
             f"- baseline forwards {timings['n_forward_total']} in the AV interface ({timings['topic_s_per_stim']:.1f} s per stimulus incl. text-only; entity {timings['entity_s_per_forward']:.2f} s/forward); topic errors {int((df.error != '').sum())}, entity errors {int((ed.error != '').sum())}; eval n={len(ev)}",
             "", "## Kill U1 (p3, raw within-pair choice accuracy, eval, paired by document)", "",
             f"- paired [AV − baseline] raw accuracy: {fm(kill)} n={kill['n']} → **{out}**",
             "", "## Side-by-side on identical items (160 evaluation documents; accuracy = fraction of documents where the true title wins; CI by document; AUROC paired bootstrap by document)", "",
             "| readout | interpreter | acc raw | acc prior-corrected | acc no-injection | swap-following raw | swap-following corr | AUROC raw | AUROC corr | AUROC no-inj | AUROC swap |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for px, name in [("p3", "p3 `The document is about` (injected)"), ("cc", "`The passage concerns` (injected)")]:
        for who, lab in [("av", "trained AV"), ("base", "un-finetuned TARGET")]:
            s = TS[(who, px)]
            lines.append(f"| {name} | {lab} | {fm(s['acc_raw'])} | {fm(s['acc_corr'])} | {fm(s['acc_noinj'])} | {fm(s['swap_raw'])} | {fm(s['swap_corr'])} | {fa(s['auroc_raw'])} | {fa(s['auroc_corr'])} | {fa(s['auroc_noinj'])} | {fa(s['auroc_swap'])} |")
    lines.append(f"| text-only: prefix tokens 0..pos + `\\nThe document is about` (no injection) | un-finetuned TARGET | {fm(TX['acc_raw'])} | {fm(TX['acc_corr'])} | {fm(TX['acc_noinj'])} | — | — | {fa(TX['auroc_raw'])} | {fa(TX['auroc_corr'])} | {fa(TX['auroc_noinj'])} | — |")
    lines += ["", "### Paired differences by document (eval 160)", "", "| prefix | statistic | AV − baseline | AV − text | baseline − text |", "|---|---|---|---|---|"]
    for px in ["p3", "cc"]:
        for k, nm in [("acc_raw", "acc raw"), ("acc_corr", "acc prior-corrected")]:
            lines.append(f"| {px} | {nm} | {fm(paired[(px, k)])} | {fm(paired[(px, k + '_av_minus_text')])} | {fm(paired[(px, k + '_base_minus_text')])} |")
        for k, nm in [("swap_raw", "swap-following raw"), ("swap_corr", "swap-following corr")]:
            lines.append(f"| {px} | {nm} | {fm(paired[(px, k)])} | — | — |")
    lines += ["", "## Entity readout on the 40 C2 pairs (80 activations; CI by template)", "", "| prefix | interpreter | donor sensitivity mean [CI] | frac>0 | both-correct raw | both-correct corr | choice acc raw (80) | choice acc corr (80) | AUROC D(h_a) vs D(h_b) | mean D(h_0) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for px in ["p1", "p2"]:
        for who, lab in [("av", "trained AV"), ("base", "un-finetuned TARGET")]:
            s = ES[(who, px)]
            lines.append(f"| {px} | {lab} | {fm(s['donor'], 4)} | {s['donor_frac_pos']['mean']:.3f} | {fm(s['both_raw'])} | {fm(s['both_corr'])} | {fm(s['acc_raw'])} | {fm(s['acc_corr'])} | {s['auroc']:.4f} | {s['mean_D0']:.3f} |")
    lines += ["", "| prefix | paired AV − baseline: donor sensitivity | choice acc raw | choice acc corr |", "|---|---|---|---|"]
    for px in ["p1", "p2"]:
        lines.append(f"| {px} | {fm(epaired[(px, 'donor')], 4)} | {fm(epaired[(px, 'acc_raw')])} | {fm(epaired[(px, 'acc_corr')])} |")
    lines += ["", "## Pre-committed reading key (from PLAN; the numbers above decide, not this text)", "",
              "AV > baseline with donor sensitivity → training improves the readout; similar and both follow the donor → useful readout exists, training advantage not established; baseline > AV → training may impair this readout; neither follows the donor → priors/confounds may explain apparent performance.",
              "", "## Ten fixed rows (eval rows 40, 56, …, 184; p3 summed log-probs)", "",
              "| stim | topic_true | topic_foreign | AV true | AV foreign | base true | base foreign | AV true noinj | base true noinj | text true | text foreign | text true prior | text foreign prior |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in FIXED_ROWS:
        r = df[df.stim_idx == i].iloc[0]
        if r.error:
            lines.append(f"| {i} | {r.topic_true} | {r.topic_foreign} | ERROR | | | | | | | | | |"); continue
        lines.append(f"| {i} | {r.topic_true} | {r.topic_foreign} | {r.av_p3_true:.2f} | {r.av_p3_foreign:.2f} | {r.base_p3_true:.2f} | {r.base_p3_foreign:.2f} | {r.av_p3_true_noinj:.2f} | {r.base_p3_true_noinj:.2f} | {r.text_true:.2f} | {r.text_foreign:.2f} | {r.text_true_noinj:.2f} | {r.text_foreign_noinj:.2f} |")
    lines.append("")
    (L.OVERNIGHT / "u1_summary.md").write_text("\n".join(lines) + "\n")
    strip = lambda d: {k: v for k, v in d.items() if not k.startswith("_")}  # noqa: E731
    S.finish(timings=timings, kill_U1={"ci": kill, "outcome": out}, topic={f"{w}_{p}": strip(s) for (w, p), s in TS.items()}, text=strip(TX),
             paired={f"{p}_{k}": v for (p, k), v in paired.items()}, entity={f"{w}_{p}": strip(s) for (w, p), s in ES.items()}, entity_paired={f"{p}_{k}": v for (p, k), v in epaired.items()},
             n_errors={"topic": int((df.error != "").sum()), "entity": int((ed.error != "").sum())})
    L.log(f"U1 done: paired raw p3 acc diff {fm(kill)} -> {out}; AV {a3['acc_raw']['mean']:.3f} base {b3['acc_raw']['mean']:.3f} text {TX['acc_raw']['mean']:.3f}")


if __name__ == "__main__":
    main()

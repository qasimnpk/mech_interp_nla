"""X1 — cross-layer readout with the fixed layer-20 AV (PLAN.md round 3c; TARGET then AV).

  uv run python overnight/x1_layers.py

Layers (frozen): blocks 16, 20, 24, 27 = hidden_states[17, 21, 25, 28] of the TARGET. Injection unchanged (marker row
:= v * 150 / ||v||, exactly as nla_lib / t2_prefix.Prefix); no whitening, no learned map.
TARGET forward on the 80 C2 contexts (final token) and the 200 stimuli documents (512-token window, position pos, exactly
as S0/T0); the four layers are saved to out/x1_acts.npz; the block-20 rows are asserted against out/c2_acts.npz and
out/acts_L20.npz (1 − cos < 1e-3).
Readouts at each layer, separately: entity p1 (h_a, h_b, h_0; candidates ' ' + e_a / ' ' + e_b; 40 pairs) and topic p3
(own / foreign (i+100 mod 200) / no injection; ' ' + detok(topic); eval 160). No-injection scores are layer-independent
and computed once. Per layer: donor sensitivity mean [D(h_a) − D(h_b)] (CI by template), both-correct, choice accuracy raw
and prior-centred (80 activations); topic AUROC and accuracy raw and prior-corrected (CI by document), swap-following.
Kill X1 (pre-registered): entity donor-sensitivity CI ≤ 0 at every non-training layer (16, 24, 27) → MET; NOT MET if at
least one of the three CIs lies entirely above 0; INCONCLUSIVE otherwise.
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix  # noqa: E402
from overnight.t2a_audit import P3  # noqa: E402
from overnight.t2c_entity import NOUNS, P1  # noqa: E402
from overnight.t1_arprobe import auroc, boot_auroc, detok  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

LAYERS = [16, 20, 24, 27]
MAX_LEN = 512
N_BOOT, SEED = 1000, 0
MIN_PAIRS = 30


def ci(v, c):
    return L.cluster_bootstrap_mean(np.asarray(v, float), c, n_boot=N_BOOT, seed=SEED)


def fm(c, d=4):
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"


def fa(b):
    return f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"


def main():
    S = L.Settings("x1", layers=LAYERS, hidden_states_indices=[l + 1 for l in LAYERS], prefixes={"p1": P1, "p3": P3}, nouns=NOUNS, max_len=MAX_LEN, n_boot=N_BOOT, seed=SEED,
                   injection="marker row := v*150/||v|| at every layer (nla_lib / t2_prefix.Prefix); no whitening, no learned map", candidate_rule="' ' + entity / ' ' + detok(topic), summed log-prob; per-token recorded",
                   kill="entity donor-sensitivity CI (by template) ≤ 0 at blocks 16, 24 and 27 → MET; NOT MET if any of the three CIs is entirely > 0; INCONCLUSIVE otherwise")
    timings = {}
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    c2 = pd.read_csv(L.OVERNIGHT / "c2_pairs.csv").sort_values("pair_id").reset_index(drop=True)
    t2c = pd.read_csv(L.OVERNIGHT / "t2c_pairs.csv").sort_values("pair_id").reset_index(drop=True)
    t2a = pd.read_csv(L.OVERNIGHT / "t2a_scores.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    H2 = np.load(L.OUT / "c2_acts.npz")["H"]; h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    topics = [detok(t) for t in top.topic_true]; foreign = list(top.foreign_stim_idx)
    from datasets import load_dataset
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]

    # ---------------- TARGET activations at the four layers
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0
    d = tgt.model.config.hidden_size; nl = len(LAYERS)
    Hc2 = np.zeros((40, 2, nl, d), np.float32); Hst = np.zeros((200, nl, d), np.float32)
    t0 = time.time()
    for r in c2.itertuples():
        for j, ctx in enumerate([r.context_a, r.context_b]):
            hs = tgt.hidden_states(tgt.tok(ctx, return_tensors="pt", add_special_tokens=False)["input_ids"])
            for k, l in enumerate(LAYERS):
                Hc2[r.pair_id, j, k] = L.to_cpu_f32(hs[l + 1][0, -1]).numpy()
    timings["target_s_per_c2_context"] = (time.time() - t0) / 80
    dev_c2 = max(1 - L.cos(Hc2[i, j, LAYERS.index(20)], H2[i, j]) for i in range(40) for j in range(2)); assert dev_c2 < 1e-3, dev_c2
    t0 = time.time()
    for i in range(200):
        ids = tgt.tok(ds[int(st.doc_idx[i])]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
        assert len(ids) == int(st.seq_len[i]) and tgt.tok.decode([ids[int(st.pos[i])]]) == st.token_str[i]
        hs = tgt.hidden_states(torch.tensor([ids]))
        for k, l in enumerate(LAYERS):
            Hst[i, k] = L.to_cpu_f32(hs[l + 1][0, int(st.pos[i])]).numpy()
        if i % 50 == 49:
            L.log(f"TARGET docs {i + 1}/200 ({(time.time() - t0) / (i + 1):.2f} s each)")
    timings["target_s_per_doc"] = (time.time() - t0) / 200
    dev_st = max(1 - L.cos(Hst[i, LAYERS.index(20)], h20[i]) for i in range(200)); assert dev_st < 1e-3, dev_st
    tgt.free(); timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    np.savez(L.OUT / "x1_acts.npz", H_c2=Hc2, H_stim=Hst, layers=np.array(LAYERS))
    norms = {l: {"c2": float(np.linalg.norm(Hc2[:, :, k], axis=-1).mean()), "stim": float(np.linalg.norm(Hst[:, k], axis=-1).mean())} for k, l in enumerate(LAYERS)}
    cos20 = {l: {"c2": float(np.mean([L.cos(Hc2[i, j, k], Hc2[i, j, LAYERS.index(20)]) for i in range(40) for j in range(2)])), "stim": float(np.mean([L.cos(Hst[i, k], Hst[i, LAYERS.index(20)]) for i in range(200)]))} for k, l in enumerate(LAYERS)}
    S.update(block20_max_1_minus_cos={"c2": float(dev_c2), "stim": float(dev_st)}, mean_norm_per_layer=norms, mean_cos_to_block20=cos20)
    L.log(f"activations cached; block-20 max(1−cos) c2 {dev_c2:.1e} stim {dev_st:.1e}; norms {norms}")

    # ---------------- AV readouts
    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    P = Prefix(av); noinj = {}

    def lp0(pre, cand):
        k = (pre, cand)
        if k not in noinj:
            noinj[k] = P.cont_logprob(None, pre, cand)[0]
        return noinj[k]
    erows = []; t0 = time.time()
    for r in t2c.itertuples():
        i = r.pair_id; pre = P1.format(noun=NOUNS[r.template_id]); ca, cb = " " + r.entity_a, " " + r.entity_b
        l0a, l0b = lp0(pre, ca), lp0(pre, cb)
        for k, l in enumerate(LAYERS):
            row = {"pair_id": i, "template_id": r.template_id, "layer": l, "entity_a": r.entity_a, "entity_b": r.entity_b, "lp_a_h0": l0a, "lp_b_h0": l0b, "D_0": l0a - l0b, "t2c_D_a": r.p1_D_a, "t2c_D_b": r.p1_D_b, "t2c_D_0": r.p1_D_0, "error": ""}
            try:
                ha, hb = torch.from_numpy(Hc2[i, 0, k]), torch.from_numpy(Hc2[i, 1, k])
                laa, na = P.cont_logprob(ha, pre, ca); lba, nb = P.cont_logprob(ha, pre, cb); lab, _ = P.cont_logprob(hb, pre, ca); lbb, _ = P.cont_logprob(hb, pre, cb)
                row.update({"n_tok_a": na, "n_tok_b": nb, "lp_a_ha": laa, "lp_b_ha": lba, "lp_a_hb": lab, "lp_b_hb": lbb, "D_a": laa - lba, "D_b": lab - lbb})
                row["donor"] = row["D_a"] - row["D_b"]; row["D_a_cen"] = row["D_a"] - row["D_0"]; row["D_b_cen"] = row["D_b"] - row["D_0"]
            except Exception:
                row["error"] = traceback.format_exc(); L.log(f"X1 entity FAILED pair {i} layer {l}")
            erows.append(row)
        if i % 10 == 9:
            L.log(f"entity {i + 1}/40 pairs, forwards {P.n_forward} ({(time.time() - t0) / max(1, P.n_forward):.2f} s each)")
    ed = pd.DataFrame(erows); ed.to_csv(L.OVERNIGHT / "x1_entity.csv", index=False)
    trows = []; t0 = time.time(); n0 = P.n_forward
    for i in range(40, 200):
        j = foreign[i]; tt, tf = topics[i], topics[j]
        l0t, l0f = lp0(P3, " " + tt), lp0(P3, " " + tf)
        for k, l in enumerate(LAYERS):
            row = {"stim_idx": i, "layer": l, "topic_true": tt, "topic_foreign": tf, "foreign_stim_idx": j, "true_noinj": l0t, "foreign_noinj": l0f, "t2a_true": t2a.p3_true[i], "t2a_foreign": t2a.p3_foreign[i], "error": ""}
            try:
                h, hj = torch.from_numpy(Hst[i, k]), torch.from_numpy(Hst[j, k])
                lt, nt = P.cont_logprob(h, P3, " " + tt); lf, nf = P.cont_logprob(h, P3, " " + tf); s_t, _ = P.cont_logprob(hj, P3, " " + tt); s_f, _ = P.cont_logprob(hj, P3, " " + tf)
                row.update({"n_tok_true": nt, "n_tok_foreign": nf, "true": lt, "foreign": lf, "true_swap": s_t, "foreign_swap": s_f, "true_corr": lt - l0t, "foreign_corr": lf - l0f})
            except Exception:
                row["error"] = traceback.format_exc(); L.log(f"X1 topic FAILED stim {i} layer {l}")
            trows.append(row)
        if i % 40 == 39:
            L.log(f"topic {i - 39}/160 docs, forwards {P.n_forward} ({(time.time() - t0) / max(1, P.n_forward - n0):.2f} s each)")
    timings["av_s_per_forward"] = (time.time() - t0) / max(1, P.n_forward - n0); timings["n_av_forward"] = P.n_forward
    td = pd.DataFrame(trows); td.to_csv(L.OVERNIGHT / "x1_topic.csv", index=False)
    av.free()

    # ---------------- statistics per layer
    ES, TS = {}, {}
    for l in LAYERS:
        e = ed[(ed.layer == l) & (ed.error == "")].reset_index(drop=True); cl = e.template_id.values
        Da, Db, D0 = e.D_a.values, e.D_b.values, e.D_0.values; cl2 = np.concatenate([cl, cl])
        ES[l] = {"n": int(len(e)), "donor": ci(Da - Db, cl), "donor_frac_pos": float((Da - Db > 0).mean()), "both_raw": ci(((Da > 0) & (Db < 0)).astype(float), cl), "both_cen": ci((((Da - D0) > 0) & ((Db - D0) < 0)).astype(float), cl),
                 "acc_raw": ci(np.concatenate([Da > 0, Db < 0]).astype(float), cl2), "acc_cen": ci(np.concatenate([(Da - D0) > 0, (Db - D0) < 0]).astype(float), cl2), "auroc": auroc(Da, Db),
                 "mean_D_a": float(Da.mean()), "mean_D_b": float(Db.mean()), "max_dev_vs_t2c": float(max(np.max(np.abs(Da - e.t2c_D_a.values)), np.max(np.abs(Db - e.t2c_D_b.values)))) if l == 20 else None}
        t = td[(td.layer == l) & (td.error == "")].reset_index(drop=True)
        TS[l] = {"n": int(len(t)), "auroc_raw": boot_auroc(t["true"], t["foreign"]), "auroc_corr": boot_auroc(t.true_corr, t.foreign_corr), "auroc_swap": boot_auroc(t.foreign_swap, t.true_swap),
                 "acc_raw": ci((t["true"] > t["foreign"]).astype(float), t.stim_idx.values), "acc_corr": ci((t.true_corr > t.foreign_corr).astype(float), t.stim_idx.values),
                 "swap_raw": ci((t.foreign_swap > t.true_swap).astype(float), t.stim_idx.values), "swap_corr": ci(((t.foreign_swap - t.foreign_noinj) > (t.true_swap - t.true_noinj)).astype(float), t.stim_idx.values),
                 "max_dev_vs_t2a": float(max(np.max(np.abs(t["true"] - t.t2a_true)), np.max(np.abs(t["foreign"] - t.t2a_foreign)))) if l == 20 else None}
    non = [16, 24, 27]
    all_le = all(ES[l]["donor"]["hi"] <= 0 for l in non); any_gt = any(ES[l]["donor"]["lo"] > 0 for l in non)
    enough = all(ES[l]["n"] >= MIN_PAIRS for l in non)
    out = "INCONCLUSIVE" if not enough else ("MET" if all_le else ("NOT MET" if any_gt else "INCONCLUSIVE"))
    best_acc = max(LAYERS, key=lambda l: ES[l]["acc_raw"]["mean"]); best_top = max(LAYERS, key=lambda l: TS[l]["acc_raw"]["mean"])
    L.append_disconfirmation("X1", "X1", "entity donor-sensitivity CI (by template) under p1 ≤ 0 at every non-training block (16, 24, 27) → MET; NOT MET if any of the three CIs is entirely > 0",
                             "; ".join(f"L{l}: donor {fm(ES[l]['donor'])} acc raw {ES[l]['acc_raw']['mean']:.3f} both {ES[l]['both_raw']['mean']:.3f} topic AUROC raw {TS[l]['auroc_raw']['auroc']:.3f} corr {TS[l]['auroc_corr']['auroc']:.3f} acc raw {TS[l]['acc_raw']['mean']:.3f}" for l in LAYERS)
                             + f"; best entity acc L{best_acc}, best topic acc L{best_top}; L20 max |dev| vs t2c {ES[20]['max_dev_vs_t2c']:.3f}, vs t2a {TS[20]['max_dev_vs_t2a']:.3f}",
                             out, "MET would mean no readable transfer of the layer-20 AV's entity readout to other layers")

    lines = ["# X1 summary — cross-layer readout with the fixed layer-20 AV (TARGET → AV)", "",
             f"git {L.git_hash()[:8]}; settings in x1_settings.json; rows in x1_entity.csv (40 pairs x 4 layers), x1_topic.csv (160 eval x 4 layers); activations in out/x1_acts.npz", "",
             f"- layers {LAYERS} (hidden_states {[l + 1 for l in LAYERS]}); block-20 rows vs cached: max(1−cos) c2 {dev_c2:.1e}, stimuli {dev_st:.1e}; AV forwards {timings['n_av_forward']} ({timings['av_s_per_forward']:.2f} s); errors entity {int((ed.error != '').sum())} topic {int((td.error != '').sum())}",
             f"- mean activation norm per layer (c2 / stimuli): " + ", ".join(f"L{l} {norms[l]['c2']:.0f}/{norms[l]['stim']:.0f}" for l in LAYERS) + "; mean cos to the block-20 activation: " + ", ".join(f"L{l} {cos20[l]['c2']:.3f}/{cos20[l]['stim']:.3f}" for l in LAYERS),
             f"- layer-20 re-run vs round-3b files: entity max |ΔD| {ES[20]['max_dev_vs_t2c']:.4f} (t2c), topic max |Δlp| {TS[20]['max_dev_vs_t2a']:.4f} (t2a)",
             "", "## Kill X1", "", f"- entity donor-sensitivity CIs at L16 {fm(ES[16]['donor'])}, L24 {fm(ES[24]['donor'])}, L27 {fm(ES[27]['donor'])} → **{out}**",
             "", "## Per-layer table — entity (p1; 40 pairs; CI by template)", "", "| block | donor sensitivity [CI] | frac>0 | both-correct raw | both-correct centred | choice acc raw (80) | choice acc centred (80) | AUROC D(h_a) vs D(h_b) | mean D(h_a) | mean D(h_b) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for l in LAYERS:
        s = ES[l]; lines.append(f"| {l}{' (training layer)' if l == 20 else ''} | {fm(s['donor'])} | {s['donor_frac_pos']:.3f} | {fm(s['both_raw'], 3)} | {fm(s['both_cen'], 3)} | {fm(s['acc_raw'], 3)} | {fm(s['acc_cen'], 3)} | {s['auroc']:.4f} | {s['mean_D_a']:+.3f} | {s['mean_D_b']:+.3f} |")
    lines += ["", "## Per-layer table — topic (p3; eval 160; CI by document)", "", "| block | AUROC raw | AUROC prior-corrected | AUROC swap prefers foreign | acc raw | acc prior-corrected | swap-following raw | swap-following corr |", "|---|---|---|---|---|---|---|---|"]
    for l in LAYERS:
        s = TS[l]; lines.append(f"| {l}{' (training layer)' if l == 20 else ''} | {fa(s['auroc_raw'])} | {fa(s['auroc_corr'])} | {fa(s['auroc_swap'])} | {fm(s['acc_raw'], 3)} | {fm(s['acc_corr'], 3)} | {fm(s['swap_raw'], 3)} | {fm(s['swap_corr'], 3)} |")
    lines += ["", f"- layer maximising entity choice accuracy: {best_acc}; topic accuracy: {best_top}", "",
              "## Pre-committed reading key (from PLAN; the numbers decide)", "", "accuracy better elsewhere → training layer is not the best extraction layer for this task; donor sensitivity up without accuracy → distribution shift changes the readout without making it useful; both down → a measurable transfer limit.", ""]
    (L.OVERNIGHT / "x1_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_X1={"outcome": out, "donor_by_layer": {l: ES[l]["donor"] for l in LAYERS}}, entity={l: ES[l] for l in LAYERS}, topic={l: TS[l] for l in LAYERS})
    L.log(f"X1 done: {out}; donor " + ", ".join(f"L{l} {ES[l]['donor']['mean']:.3f}" for l in LAYERS))


if __name__ == "__main__":
    main()

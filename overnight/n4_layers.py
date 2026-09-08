"""N4 — fact-vs-phrasing displacement across all layers in the TARGET (PLAN.md round 3c; TARGET only; descriptive, no kill).

  uv run python overnight/n4_layers.py

(1) The 40 C3 cells (contexts A = (a, w1), B = (b, w1), C = (a, w2), D = (b, w2); raw text, no special tokens): hidden_states[l]
at the final token for l = 1..28 (block l−1 output); per layer mean (1 − cos) for the entity edit (A vs B, C vs D) and the
phrasing edit (A vs C, B vs D), their ratio, CI by template. The block-20 rows are asserted against out/c3_acts.npz.
(2) The 490 accepted S3 claim texts (c, c*, c~ as raw text; last token): per layer d_corr = 1 − cos(h_l(c), h_l(c*)),
d_para = 1 − cos(h_l(c), h_l(c~)), ratio, CI by explanation (the R1 distances per layer). Outputs n4_curve.csv, n4_summary.md.
"""
from __future__ import annotations

import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t1_arprobe import load_triples  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

N_BOOT, SEED = 1000, 0


def ci(v, c):
    return L.cluster_bootstrap_mean(np.asarray(v, float), c, n_boot=N_BOOT, seed=SEED)


def main():
    S = L.Settings("n4", layers="hidden_states[1..28] at the last token (raw text, add_special_tokens=False)", n_boot=N_BOOT, seed=SEED, no_kill=True)
    timings = {}
    c3 = pd.read_csv(L.OVERNIGHT / "c3_cells.csv").sort_values("pair_id").reset_index(drop=True); assert len(c3) == 40 and c3.error.isna().all()
    H3 = np.load(L.OUT / "c3_acts.npz")["H"]
    tri = load_triples()
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0
    d = tgt.model.config.hidden_size

    def last_all_layers(text: str) -> np.ndarray:
        ids = tgt.tok(text, return_tensors="pt", add_special_tokens=False)["input_ids"]
        hs = tgt.hidden_states(ids)
        return np.stack([L.to_cpu_f32(hs[l][0, -1]).numpy() for l in range(1, 29)])  # [28, d]
    # ---------------- C3 cells
    t0 = time.time(); cell_rows = []; dev = 0.0
    for r in c3.itertuples():
        try:
            Hs = {s: last_all_layers(getattr(r, f"context_{s}")) for s in "abcd"}
            for j, s in enumerate("abcd"):
                dev = max(dev, 1 - L.cos(Hs[s][20], H3[r.pair_id, j]))
            for l in range(28):
                cell_rows.append({"pair_id": r.pair_id, "template_id": r.template_id, "block": l, "d_entity_w1": 1 - L.cos(Hs["a"][l], Hs["b"][l]), "d_entity_w2": 1 - L.cos(Hs["c"][l], Hs["d"][l]),
                                  "d_phrasing_a": 1 - L.cos(Hs["a"][l], Hs["c"][l]), "d_phrasing_b": 1 - L.cos(Hs["b"][l], Hs["d"][l]), "norm_a": float(np.linalg.norm(Hs["a"][l])), "error": ""})
        except Exception:
            cell_rows.append({"pair_id": r.pair_id, "template_id": r.template_id, "block": -1, "error": traceback.format_exc()}); L.log(f"N4 cell FAILED {r.pair_id}")
    timings["target_s_per_context"] = (time.time() - t0) / 160
    assert dev < 1e-3, dev
    L.log(f"cells done; block-20 max(1−cos) vs c3_acts {dev:.1e}")
    # ---------------- S3 claims
    t0 = time.time(); claim_rows = []
    for n, r in enumerate(tri.itertuples()):
        try:
            Hc, Hx, Hp = last_all_layers(r.claim), last_all_layers(r.corrupt), last_all_layers(r.paraphrase)
            for l in range(28):
                claim_rows.append({"row": r.row, "stim_idx": r.stim_idx, "block": l, "d_corr": 1 - L.cos(Hc[l], Hx[l]), "d_para": 1 - L.cos(Hc[l], Hp[l]), "norm_c": float(np.linalg.norm(Hc[l])), "error": ""})
        except Exception:
            claim_rows.append({"row": r.row, "stim_idx": r.stim_idx, "block": -1, "error": traceback.format_exc()}); L.log(f"N4 claim FAILED {r.row}")
        if n % 100 == 99:
            L.log(f"claims {n + 1}/{len(tri)} ({(time.time() - t0) / (3 * (n + 1)):.2f} s/text)")
    timings["target_s_per_claim_text"] = (time.time() - t0) / (3 * len(tri))
    tgt.free()
    cd = pd.DataFrame(cell_rows); qd = pd.DataFrame(claim_rows)
    cd.to_csv(L.OVERNIGHT / "n4_cells_long.csv", index=False); qd.to_csv(L.OVERNIGHT / "n4_claims_long.csv", index=False)
    cok = cd[cd.error == ""]; qok = qd[qd.error == ""]
    curve = []
    for l in range(28):
        c = cok[cok.block == l]; q = qok[qok.block == l]
        ent = ci(0.5 * (c.d_entity_w1 + c.d_entity_w2), c.template_id); phr = ci(0.5 * (c.d_phrasing_a + c.d_phrasing_b), c.template_id)
        rat = ci((0.5 * (c.d_entity_w1 + c.d_entity_w2)) / (0.5 * (c.d_phrasing_a + c.d_phrasing_b) + 1e-12), c.template_id); dif = ci(0.5 * (c.d_entity_w1 + c.d_entity_w2) - 0.5 * (c.d_phrasing_a + c.d_phrasing_b), c.template_id)
        dc = ci(q.d_corr, q.stim_idx); dp = ci(q.d_para, q.stim_idx); dd = ci(q.d_corr - q.d_para, q.stim_idx); rq = ci(q.d_corr / (q.d_para + 1e-12), q.stim_idx)
        curve.append({"block": l, "hidden_states_index": l + 1, "c3_n_cells": int(c.pair_id.nunique()), "c3_d_entity": ent["mean"], "c3_d_entity_lo": ent["lo"], "c3_d_entity_hi": ent["hi"], "c3_d_phrasing": phr["mean"], "c3_d_phrasing_lo": phr["lo"], "c3_d_phrasing_hi": phr["hi"],
                      "c3_ratio_entity_over_phrasing": rat["mean"], "c3_ratio_lo": rat["lo"], "c3_ratio_hi": rat["hi"], "c3_entity_minus_phrasing": dif["mean"], "c3_entity_minus_phrasing_lo": dif["lo"], "c3_entity_minus_phrasing_hi": dif["hi"], "c3_mean_norm": float(c.norm_a.mean()),
                      "s3_n": int(len(q)), "s3_d_corr": dc["mean"], "s3_d_corr_lo": dc["lo"], "s3_d_corr_hi": dc["hi"], "s3_d_para": dp["mean"], "s3_d_para_lo": dp["lo"], "s3_d_para_hi": dp["hi"], "s3_corr_minus_para": dd["mean"], "s3_corr_minus_para_lo": dd["lo"], "s3_corr_minus_para_hi": dd["hi"],
                      "s3_ratio_corr_over_para": rq["mean"], "s3_ratio_lo": rq["lo"], "s3_ratio_hi": rq["hi"], "s3_mean_norm": float(q.norm_c.mean())})
    cv = pd.DataFrame(curve); cv.to_csv(L.OVERNIGHT / "n4_curve.csv", index=False)
    lines = ["# N4 summary — fact-vs-phrasing displacement across all layers in the TARGET (descriptive; no kill)", "",
             f"git {L.git_hash()[:8]}; settings in n4_settings.json; per-layer table in n4_curve.csv; long tables n4_cells_long.csv, n4_claims_long.csv", "",
             f"- C3 cells: {cok.pair_id.nunique()} (errors {int((cd.error != '').sum())}); block-20 max(1−cos) vs c3_acts {dev:.1e}; S3 triples: {qok.row.nunique()} (errors {int((qd.error != '').sum())}); {timings['target_s_per_context']:.2f} s/context, {timings['target_s_per_claim_text']:.2f} s/claim text",
             "", "## Per-layer curve (1 − cos at the last token; C3: entity edit = mean(A vs B, C vs D), phrasing edit = mean(A vs C, B vs D), CI by template; S3: claim vs corruption / paraphrase, CI by explanation)", "",
             "| block | C3 d_entity [CI] | C3 d_phrasing [CI] | C3 entity − phrasing [CI] | C3 ratio entity/phrasing [CI] | S3 d_corr [CI] | S3 d_para [CI] | S3 corr − para [CI] | S3 ratio corr/para [CI] | mean norm C3 / S3 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in cv.itertuples():
        lines.append(f"| {r.block} | {r.c3_d_entity:.5f} [{r.c3_d_entity_lo:.5f},{r.c3_d_entity_hi:.5f}] | {r.c3_d_phrasing:.5f} [{r.c3_d_phrasing_lo:.5f},{r.c3_d_phrasing_hi:.5f}] | {r.c3_entity_minus_phrasing:+.5f} [{r.c3_entity_minus_phrasing_lo:+.5f},{r.c3_entity_minus_phrasing_hi:+.5f}] | {r.c3_ratio_entity_over_phrasing:.3f} [{r.c3_ratio_lo:.3f},{r.c3_ratio_hi:.3f}] | "
                     f"{r.s3_d_corr:.5f} [{r.s3_d_corr_lo:.5f},{r.s3_d_corr_hi:.5f}] | {r.s3_d_para:.5f} [{r.s3_d_para_lo:.5f},{r.s3_d_para_hi:.5f}] | {r.s3_corr_minus_para:+.5f} [{r.s3_corr_minus_para_lo:+.5f},{r.s3_corr_minus_para_hi:+.5f}] | {r.s3_ratio_corr_over_para:.3f} [{r.s3_ratio_lo:.3f},{r.s3_ratio_hi:.3f}] | {r.c3_mean_norm:.0f} / {r.s3_mean_norm:.0f} |")
    b20 = cv[cv.block == 20].iloc[0]
    lines += ["", f"- block 20 (the NLA layer): C3 entity {b20.c3_d_entity:.5f} vs phrasing {b20.c3_d_phrasing:.5f} (ratio {b20.c3_ratio_entity_over_phrasing:.3f}); S3 corr {b20.s3_d_corr:.5f} vs para {b20.s3_d_para:.5f} (ratio {b20.s3_ratio_corr_over_para:.3f}); round-2 R1 at block 20 reported d_corr_T 0.0395, d_para_T 0.1336",
              f"- layer with the largest C3 entity−phrasing difference: block {int(cv.loc[cv.c3_entity_minus_phrasing.idxmax(), 'block'])} ({cv.c3_entity_minus_phrasing.max():+.5f}); largest C3 ratio: block {int(cv.loc[cv.c3_ratio_entity_over_phrasing.idxmax(), 'block'])} ({cv.c3_ratio_entity_over_phrasing.max():.3f}); largest S3 ratio corr/para: block {int(cv.loc[cv.s3_ratio_corr_over_para.idxmax(), 'block'])} ({cv.s3_ratio_corr_over_para.max():.3f})",
              "- a flat or rising curve is reported without a mechanism claim (PLAN)", ""]
    (L.OVERNIGHT / "n4_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, block20={"c3_d_entity": float(b20.c3_d_entity), "c3_d_phrasing": float(b20.c3_d_phrasing), "s3_d_corr": float(b20.s3_d_corr), "s3_d_para": float(b20.s3_d_para)})
    L.log("N4 done")


if __name__ == "__main__":
    main()

"""R0 — artifact check + cache regeneration (PLAN.md round 2).

  uv run python overnight/r0_check.py

1. Assert every reused round-1 file exists with the round-1 row counts (200 stimuli, 200
   explanations, 671 claims, 538 S3 edit rows with 490 edit_ok).
2. Regenerate out/acts_L20.npz exactly as S0 did: same wikitext docs (doc_idx), truncate 512,
   pos / pos2 from stimuli.csv, TARGET hidden_states[LAYER+1] (and LAYER, LAYER+2) at pos,
   hidden_states[LAYER+1] at pos2; batch 1, raw text, add_special_tokens=False.
3. Regenerate out/recon_L20.npz: AR prediction for every explanations.jsonl text (same text
   selection as S1) plus the empty-explanation prediction.
4. Acceptance: mean cos_own on the evaluation set (stimuli 40-199) recomputed from the
   regenerated caches equals the round-1 value 0.8820 to +-0.002. Both numbers -> r0_check.md.
Nothing from round 1 is overwritten (stimuli.csv, explanations.jsonl, s1_recon.csv are read only).
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

ROUND1_MEAN_COS_OWN = 0.8820
TOL = 0.002
MAX_LEN = 512
EXPECTED = {"stimuli": 200, "explanations": 200, "claims": 671, "s3_edits": 538, "s3_edit_ok": 490}


def check_artifacts() -> dict:
    ov = L.OVERNIGHT
    for name in ["stimuli.csv", "explanations.jsonl", "s2_claims.csv", "s3_edits.jsonl", "s3_scores.csv", "nla_lib.py", "s1_recon.csv"]:
        assert (ov / name).exists(), f"missing round-1 artifact {name}"
    stim = pd.read_csv(ov / "stimuli.csv", keep_default_na=False)
    expl = [json.loads(l) for l in (ov / "explanations.jsonl").read_text().splitlines() if l.strip()]
    claims = pd.read_csv(ov / "s2_claims.csv", keep_default_na=False)
    edits = [json.loads(l) for l in (ov / "s3_edits.jsonl").read_text().splitlines() if l.strip()]
    counts = {"stimuli": len(stim), "explanations": len(expl), "claims": len(claims),
              "s3_edits": len(edits), "s3_edit_ok": int(sum(bool(e["edit_ok"]) for e in edits))}
    for k, v in EXPECTED.items():
        assert counts[k] == v, f"{k}: expected {v}, found {counts[k]}"
    assert sorted(stim.stim_idx) == list(range(200))
    assert sorted(e["stim_idx"] for e in expl) == list(range(200))
    return counts


def regen_acts(stim: pd.DataFrame, timings: dict) -> dict:
    from datasets import load_dataset
    t0 = time.time()
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    tok = tgt.tok
    n = len(stim)
    d = tgt.model.config.hidden_size
    h19 = np.zeros((n, d), np.float32); h20 = np.zeros_like(h19); h21 = np.zeros_like(h19); h20_pos2 = np.zeros_like(h19)
    mismatches = []
    t0 = time.time()
    for r in stim.itertuples():
        i = int(r.stim_idx)
        ids = tok(ds[int(r.doc_idx)]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
        if len(ids) != int(r.seq_len) or tok.decode([ids[int(r.pos)]]) != r.token_str:
            mismatches.append({"stim_idx": i, "seq_len_csv": int(r.seq_len), "seq_len_now": len(ids),
                               "token_csv": r.token_str, "token_now": tok.decode([ids[int(r.pos)]]) if int(r.pos) < len(ids) else None})
        hs = tgt.hidden_states(torch.tensor([ids]))
        h19[i] = L.to_cpu_f32(hs[L.LAYER][0, int(r.pos)]).numpy()
        h20[i] = L.to_cpu_f32(hs[L.LAYER + 1][0, int(r.pos)]).numpy()
        h21[i] = L.to_cpu_f32(hs[L.LAYER + 2][0, int(r.pos)]).numpy()
        h20_pos2[i] = L.to_cpu_f32(hs[L.LAYER + 1][0, int(r.pos2)]).numpy()
        if i % 50 == 0:
            L.log(f"acts {i}/{n} seq_len={len(ids)} pos={r.pos} norm20={np.linalg.norm(h20[i]):.1f}")
    timings["acts_regen_s"] = time.time() - t0
    assert not mismatches, f"stimulus tokenisation drift: {mismatches[:5]}"
    arrs = {"h20": h20, "h19": h19, "h21": h21, "h20_pos2": h20_pos2,
            "stim_idx": stim["stim_idx"].values, "doc_idx": stim["doc_idx"].values,
            "pos": stim["pos"].values, "pos2": stim["pos2"].values}
    L.OUT.mkdir(exist_ok=True)
    np.savez(L.OUT / "acts_L20.npz", **arrs)
    L.log(f"acts_L20.npz regenerated in {timings['acts_regen_s']:.0f}s; {len(mismatches)} tokenisation mismatches")
    tgt.free()
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    return arrs


def regen_recon(expl: dict[int, dict], n: int, d: int, timings: dict) -> tuple[np.ndarray, np.ndarray, list]:
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    pred = np.full((n, d), np.nan, np.float32)
    errors = []
    t0 = time.time()
    for i in range(n):
        r = expl[i]
        text = r["explanation"] if r.get("explanation") is not None else (r.get("raw_generation") or "")
        try:
            pred[i] = ar.predict(text).numpy()
        except Exception as e:
            errors.append({"stim_idx": i, "error": traceback.format_exc()})
            L.log(f"AR FAILED on {i}: {e}")
        if i % 50 == 0:
            L.log(f"AR {i}/{n}")
    pred_empty = ar.predict("").numpy()
    timings["ar_sec_per_score"] = (time.time() - t0) / n
    ar.free()
    np.savez(L.OUT / "recon_L20.npz", pred=pred, pred_empty=pred_empty, stim_idx=np.arange(n))
    L.log("recon_L20.npz regenerated")
    return pred, pred_empty, errors


def main():
    S = L.Settings("r0", round1_mean_cos_own=ROUND1_MEAN_COS_OWN, tolerance=TOL, max_len=MAX_LEN,
                   expected_counts=EXPECTED, evaluation_set="stimuli 40-199",
                   dataset={"repo": "EleutherAI/wikitext_document_level", "config": "wikitext-2-raw-v1", "split": "train"})
    timings = {}
    counts = check_artifacts()
    S.update(artifact_counts=counts)
    L.log(f"artifact counts OK: {counts}")
    stim = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    expl = {}
    for line in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); expl[r["stim_idx"]] = r
    s1 = pd.read_csv(L.OVERNIGHT / "s1_recon.csv")

    acts = regen_acts(stim, timings)
    h20 = acts["h20"]
    pred, pred_empty, errors = regen_recon(expl, len(stim), h20.shape[1], timings)

    rows = []
    for i in range(len(stim)):
        ok = not np.isnan(pred[i]).any()
        rows.append({"stim_idx": i, "split": L.split_of(i),
                     "cos_own": L.cos(pred[i], h20[i]) if ok else np.nan,
                     "cos_empty": L.cos(pred_empty, h20[i]),
                     "cos_own_round1": float(s1.cos_own.iloc[i]), "cos_empty_round1": float(s1.cos_empty.iloc[i]),
                     "act_norm": float(np.linalg.norm(h20[i])), "act_norm_round1": float(s1.act_norm.iloc[i])})
    rc = pd.DataFrame(rows)
    rc.to_csv(L.OVERNIGHT / "r0_recon.csv", index=False)
    ev = rc[rc.split == "eval"].dropna(subset=["cos_own"])
    ci = L.cluster_bootstrap_mean(ev.cos_own, ev.stim_idx)
    mean_now = float(ev.cos_own.mean())
    diff = mean_now - ROUND1_MEAN_COS_OWN
    accepted = bool(abs(diff) <= TOL and len(ev) == 160)
    row_diff = (rc.cos_own - rc.cos_own_round1).abs()
    norm_diff = (rc.act_norm - rc.act_norm_round1).abs()
    empty_diff = (rc.cos_empty - rc.cos_empty_round1).abs()
    lines = ["# R0 check — artifact counts + cache regeneration", "",
             f"git {L.git_hash()[:8]}; settings in r0_settings.json", "",
             "## Artifact counts (expected / found)", ""]
    for k, v in EXPECTED.items():
        lines.append(f"- {k}: expected {v}, found {counts[k]}")
    lines += ["", "## Acceptance: mean cos_own on evaluation set (stimuli 40-199)", "",
              f"- round-1 value (S1, s1_recon.csv): {ROUND1_MEAN_COS_OWN:.4f}",
              f"- regenerated value: {mean_now:.4f} CI95 [{ci['lo']:.4f}, {ci['hi']:.4f}] n={ci['n']}",
              f"- difference: {diff:+.5f}; tolerance +-{TOL}; within tolerance: {accepted}",
              f"- round-1 eval mean recomputed from s1_recon.csv: {s1[s1.split == 'eval'].cos_own.mean():.4f}", "",
              "## Per-row agreement with round 1 (all 200 stimuli)", "",
              f"- |cos_own − cos_own_round1|: max {row_diff.max():.5f}, mean {row_diff.mean():.5f}, n>0.001: {int((row_diff > 0.001).sum())}",
              f"- |act_norm − act_norm_round1|: max {norm_diff.max():.4f}, mean {norm_diff.mean():.4f}",
              f"- |cos_empty − cos_empty_round1|: max {empty_diff.max():.5f}",
              f"- AR errors: {len(errors)}", "", "## Timings", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.2f}" if isinstance(v, float) else f"- {k}: {v}")
    lines += ["", f"R0 ACCEPTED: {accepted}", ""]
    (L.OVERNIGHT / "r0_check.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, mean_cos_own_eval=mean_now, ci=ci, diff_vs_round1=diff, accepted=accepted,
             per_row_max_abs_diff=float(row_diff.max()), ar_errors=errors)
    L.log(f"R0 done: mean cos_own eval={mean_now:.4f} (round 1 {ROUND1_MEAN_COS_OWN}); accepted={accepted}")


if __name__ == "__main__":
    main()

"""U0c — round-3c artifact check + micro-benchmark of every model-call type + re-budget (PLAN.md round 3c; no kill test).

  uv run python overnight/u0c_check.py

Asserts the reuse files exist with the expected row counts, then times 5 calls of each call type used by the round-3c
stages (TARGET short forward; TARGET forward on a 512-token document with all hidden states; TARGET forward with a
residual hook at block 20; AV forward with prefill; AV generation 200 tokens; AR score), one model at a time
(TARGET -> free -> AV -> free -> AR), writes measured s/item to u0c_check.md and u0c_settings.json and projects every
stage's time from the PLAN's call counts against its cap.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix, PREFILL_CC  # noqa: E402  (import-safe: Settings inside main)
from overnight.t2a_audit import P3  # noqa: E402
from src.model_utils import get_blocks, _block_output  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

MAX_LEN = 512
N_CALLS = 5
CAPS_MIN = {"U1": 60, "X3": 60, "X1": 60, "N3": 60, "N4": 60, "X1b": 60, "RT": 90, "M": 90}


def timeit(fn, n=N_CALLS):
    ts = []
    for _ in range(n):
        t = time.time(); fn(); torch.mps.synchronize(); ts.append(time.time() - t)
    return {"n": n, "mean_s": float(np.mean(ts)), "min_s": float(np.min(ts)), "max_s": float(np.max(ts)), "all_s": [float(x) for x in ts]}


def main():
    S = L.Settings("u0c", n_calls=N_CALLS, caps_min=CAPS_MIN, max_len=MAX_LEN)
    checks = []

    def chk(name, got, want):
        checks.append((name, got, want, got == want)); assert got == want, (name, got, want)

    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False); chk("stimuli rows", len(st), 200)
    t2a = pd.read_csv(L.OVERNIGHT / "t2a_scores.csv", keep_default_na=False); chk("t2a_scores rows", len(t2a), 200); chk("t2a_scores errors", int((t2a.error != "").sum()), 0)
    t2c = pd.read_csv(L.OVERNIGHT / "t2c_pairs.csv"); chk("t2c_pairs rows", len(t2c), 40); chk("t2c_pairs errors", int(t2c.error.notna().sum()), 0)
    c2 = pd.read_csv(L.OVERNIGHT / "c2_pairs.csv"); chk("c2_pairs rows", len(c2), 40)
    c3 = pd.read_csv(L.OVERNIGHT / "c3_cells.csv"); chk("c3_cells rows", len(c3), 40)
    s3 = pd.read_csv(L.OVERNIGHT / "s3_scores.csv", keep_default_na=False)
    n_ok = int((s3.edit_ok.astype(str) == "True").sum()); checks.append(("s3_scores rows with edit_ok (all edit types)", n_ok, ">0", n_ok > 0)); assert n_ok > 0
    acc = s3[(s3.edit_type == "corrupt") & (s3.edit_ok.astype(str) == "True")]; chk("s3 accepted LLM-corrupt rows", len(acc), 490)
    det = s3[(s3.edit_type == "corrupt_det") & (s3.edit_ok.astype(str) == "True")]; checks.append(("s3 corrupt_det edit_ok rows", len(det), "≈445 (402 also LLM-accepted)", True))
    t0t = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False); chk("t0_topics rows", len(t0t), 200)
    t0e = pd.read_csv(L.OVERNIGHT / "t0_entropy.csv", keep_default_na=False); chk("t0_entropy rows", len(t0e), 200)
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False); chk("s2_claims rows", len(s2), 671)
    ne = sum(1 for ln in (L.OVERNIGHT / "s3_edits.jsonl").read_text().splitlines() if ln.strip()); chk("s3_edits rows", ne, 538)
    nx = sum(1 for ln in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines() if ln.strip()); chk("explanations rows", nx, 200)
    a = np.load(L.OUT / "acts_L20.npz"); chk("acts_L20 h20 shape", tuple(a["h20"].shape), (200, 3584)); chk("acts_L20 h20_pos2 shape", tuple(a["h20_pos2"].shape), (200, 3584))
    ca = np.load(L.OUT / "c2_acts.npz"); chk("c2_acts H shape", tuple(ca["H"].shape), (40, 2, 3584)); chk("c2_acts rows", 40 * 2, 80)
    c3a = np.load(L.OUT / "c3_acts.npz"); chk("c3_acts H shape", tuple(c3a["H"].shape), (40, 4, 3584))
    rec = np.array([L.cos(ca["H"][i, 0], ca["H"][i, 1]) for i in range(40)]); dev = float(np.max(np.abs(rec - c2.cos_ha_hb.values)))
    checks.append(("c2_acts vs c2_pairs cos(h_a,h_b) max |dev|", dev, "<1e-4", dev < 1e-4)); assert dev < 1e-4
    for f in ["t2_prefix.py", "t2a_audit.py", "t2c_entity.py", "c2_matched.py", "c3_phrasing.py", "t1_arprobe.py"]:
        src = (L.OVERNIGHT / f).read_text(); safe = "L.Settings(" not in src.split("def main():")[0]
        checks.append((f"{f} import-safe (Settings inside main)", safe, True, safe)); assert safe
    L.log(f"artifact checks: {sum(c[3] for c in checks)}/{len(checks)} OK")
    S.update(checks=[{"check": n, "got": str(g), "want": str(w), "ok": bool(o)} for n, g, w, o in checks])

    from datasets import load_dataset
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]
    bench = {}
    h20 = a["h20"]

    # ---------------- TARGET
    t0 = time.time(); tgt = L.Target(); bench["target_load_s"] = time.time() - t0
    tok = tgt.tok
    short_ids = tok(c2.context_a[0], return_tensors="pt", add_special_tokens=False)["input_ids"]
    bench["target_short_forward"] = timeit(lambda: tgt.hidden_states(short_ids)); bench["target_short_forward"]["tokens"] = int(short_ids.shape[1])
    docs = []
    for i in range(N_CALLS):
        ids = tok(ds[int(st.doc_idx[i])]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
        assert len(ids) == int(st.seq_len[i]); docs.append(torch.tensor([ids]))
    it = iter(list(range(N_CALLS)) * 2)
    dev20 = []

    def doc_fwd():
        i = next(it); hs = tgt.hidden_states(docs[i])
        dev20.append(1 - L.cos(L.to_cpu_f32(hs[L.LAYER + 1][0, int(st.pos[i])]).numpy(), h20[i]))
    bench["target_doc512_forward_all_hidden"] = timeit(doc_fwd); bench["target_doc512_forward_all_hidden"]["tokens"] = [int(d.shape[1]) for d in docs]
    bench["target_doc512_forward_all_hidden"]["max_1_minus_cos_vs_acts_L20"] = float(max(dev20))
    # residual hook at block 20 (self-patch of the final row; pattern from src/patching.py)
    blocks = get_blocks(tgt.model)
    with torch.inference_mode():
        base_logits = tgt.model(short_ids.to(L.DEVICE), use_cache=False, logits_to_keep=1).logits[0, -1].float().cpu()
    box = {}

    def hook(_m, _i, output):
        h = _block_output(output).clone(); box["h"] = h[0, -1].detach().clone(); h[0, -1] = box["h"]
        return (h, *output[1:]) if isinstance(output, tuple) else h

    def hooked():
        hd = blocks[L.LAYER].register_forward_hook(hook)
        try:
            with torch.inference_mode():
                box["logits"] = tgt.model(short_ids.to(L.DEVICE), use_cache=False, logits_to_keep=1).logits[0, -1].float().cpu()
        finally:
            hd.remove()
    bench["target_forward_hook_block20"] = timeit(hooked)
    bench["target_forward_hook_block20"]["self_patch_max_abs_logit_diff"] = float((box["logits"] - base_logits).abs().max())
    tgt.free(); bench["rss_after_target_free_G"] = L.rss_mb() / 1024

    # ---------------- AV
    t0 = time.time(); av = L.AV(); bench["av_load_s"] = time.time() - t0
    P = Prefix(av); top = t0t.topic_true[0]
    bench["av_forward_prefill"] = timeit(lambda: P.cont_logprob(torch.from_numpy(h20[0]), P3, " " + top))
    gens = []
    it2 = iter(range(N_CALLS))
    bench["av_generation_200"] = timeit(lambda: gens.append(av.verbalize(torch.from_numpy(h20[next(it2)]), max_new_tokens=200)))
    bench["av_generation_200"]["n_tokens"] = [g["n_tokens"] for g in gens]; bench["av_generation_200"]["parse_ok"] = [g["parse_ok"] for g in gens]
    av.free(); bench["rss_after_av_free_G"] = L.rss_mb() / 1024

    # ---------------- AR
    t0 = time.time(); ar = L.AR(); bench["ar_load_s"] = time.time() - t0
    it3 = iter(gens)
    bench["ar_score"] = timeit(lambda: ar.predict(next(it3)["explanation"]))
    ar.free()

    # ---------------- re-budget (call counts from the PLAN stage texts)
    c = {k: bench[k]["mean_s"] for k in ["target_short_forward", "target_doc512_forward_all_hidden", "target_forward_hook_block20", "av_forward_prefill", "av_generation_200", "ar_score"]}
    loads = {"T": bench["target_load_s"], "A": bench["av_load_s"], "R": bench["ar_load_s"]}
    n_x3 = None
    budget = {
        "U1": {"calls": {"av_forward_prefill": 200 * 8 + 400 + 480, "target_doc512_forward_all_hidden": 400 + 200}, "loads": ["T"],
               "note": "topic 200 docs x 2 prefixes x 2 cands x (own, swap) + no-inj cache 400; entity 40 x 2 x 2 x 2 + 160 no-inj; text-only 200 x 2 titles (prefix) + prior cached by topic ~200 (counted as doc forwards)"},
        "X3": {"calls": {"ar_score": 3000, "target_short_forward": 700}, "loads": ["T", "R"], "note": "≈330 rows x 9 AR scores (T/F/P x 3 conditions); judge ≈660 short TARGET generations (≤8 tokens) counted as short forwards x4"},
        "X1": {"calls": {"target_doc512_forward_all_hidden": 200, "target_short_forward": 80, "av_forward_prefill": 4 * (160 * 4 + 40 * 4) + 280}, "loads": ["T", "A"], "note": "4 layers x (topic 160 x 4 + entity 40 x 4) + no-inj cache"},
        "N3": {"calls": {"ar_score": 1650}, "loads": ["R"], "note": "402 rows x 4 versions (original cached per explanation)"},
        "N4": {"calls": {"target_short_forward": 160 + 1900}, "loads": ["T"], "note": "40 cells x 4 contexts + ≈1,900 claim texts, all hidden states"},
        "X1b": {"calls": {"av_generation_200": 80, "ar_score": 80}, "loads": ["A", "R"], "note": "40 pilot x 2 layers"},
        "RT": {"calls": {"target_forward_hook_block20": 16 * 6 + 32, "av_generation_200": 16, "av_forward_prefill": 16 * 6, "ar_score": 16}, "loads": ["T", "A", "R", "T"], "note": "16 contexts; gates + 4 patches x 16 + text QA"},
        "M": {"calls": {"av_generation_200": 200 * 1.0 + 80, "target_short_forward": 80 * 4, "ar_score": 80}, "loads": ["T", "A", "R"], "note": "200 TARGET generations ≤200 tokens counted at the AV generation rate; 80 items AV + AR"},
    }
    rows = []
    for stg, b in budget.items():
        secs = sum(n * c[k] for k, n in b["calls"].items()) + sum(loads[x] for x in b["loads"])
        b["projected_min"] = secs / 60; b["cap_min"] = CAPS_MIN[stg]; b["over_cap"] = b["projected_min"] > CAPS_MIN[stg]
        rows.append((stg, b["projected_min"], CAPS_MIN[stg], b["over_cap"], b["note"]))
    total = sum(b["projected_min"] for b in budget.values())
    lines = ["# U0c check — artifacts, measured per-call costs, re-budget (round 3c)", "", f"git {L.git_hash()[:8]}; settings in u0c_settings.json", "",
             "## Artifact checks", "", "| check | got | want | ok |", "|---|---|---|---|"]
    lines += [f"| {n} | {g} | {w} | {'OK' if o else 'FAIL'} |" for n, g, w, o in checks]
    lines += ["", f"## Measured costs ({N_CALLS} calls each; mean / min / max seconds; MPS synchronised)", "", "| call type | mean s | min s | max s | note |", "|---|---|---|---|---|"]
    for k in ["target_short_forward", "target_doc512_forward_all_hidden", "target_forward_hook_block20", "av_forward_prefill", "av_generation_200", "ar_score"]:
        b = bench[k]; extra = {kk: vv for kk, vv in b.items() if kk not in ("n", "mean_s", "min_s", "max_s", "all_s")}
        lines.append(f"| {k} | {b['mean_s']:.3f} | {b['min_s']:.3f} | {b['max_s']:.3f} | {json.dumps(extra)} |")
    lines += ["", f"- model loads: TARGET {bench['target_load_s']:.0f} s, AV {bench['av_load_s']:.0f} s, AR {bench['ar_load_s']:.0f} s; RSS after TARGET free {bench['rss_after_target_free_G']:.1f} G, after AV free {bench['rss_after_av_free_G']:.1f} G",
              f"- self-patch at block 20 (own row written back): max |Δlogit| {bench['target_forward_hook_block20']['self_patch_max_abs_logit_diff']:.2e} (bf16)",
              f"- 512-token document forward: block-20 activation at pos vs acts_L20 max(1−cos) {bench['target_doc512_forward_all_hidden']['max_1_minus_cos_vs_acts_L20']:.2e}",
              "", "## Re-budget (call counts from the PLAN stage texts x measured means + loads)", "", "| stage | projected min | cap min | over cap | counts |", "|---|---|---|---|---|"]
    lines += [f"| {s} | {p:.1f} | {cap} | {'YES' if o else 'no'} | {n} |" for s, p, cap, o, n in rows]
    lines += ["", f"- total projected {total:.0f} min for U1..M (hard stop 9 h = 540 min from the first round-3c RUNLOG line)", ""]
    (L.OVERNIGHT / "u0c_check.md").write_text("\n".join(lines))
    S.finish(bench=bench, budget=budget, total_projected_min=total)
    L.log(f"U0c done: costs {json.dumps({k: round(v, 3) for k, v in c.items()})}; total projected {total:.0f} min")


if __name__ == "__main__":
    main()

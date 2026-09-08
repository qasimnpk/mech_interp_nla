"""RT — does task-relevant information survive the NLA round trip? (PLAN.md round 3c; GATED 8-pair pilot; TARGET → AV+AR → TARGET).

  uv run python overnight/rt_roundtrip.py

Contexts (frozen; raw text, no chat template): '{N1} received the {O1}. {N2} received the {O2}.\nQuestion: Who received the
{O1}?\nAnswer:' and its twin '{N2} received the {O1}. {N1} received the {O2}.' + the same question. Name pairs (Anna, Tom),
(Sara, Ben); object pairs (key, book), (coin, letter), (cup, hat), (map, pen) → 8 pairs = 16 contexts; correct answer for
A is N1, for the twin N2; candidates ' ' + name are asserted single tokens. Position = the final prompt token (':' after
'Answer'); activation = hidden_states[21] there. m = lp(' correct') − lp(' other') at the next token.
Gates (pilot counts): G0 native m > 0 in ≥ 14/16; G1 self-patch (block-20 output row at the position replaced by itself)
reproduces every next-token logit within 1e-2 in 16/16; G2 twin donor patch moves m toward the twin's answer (Δm < 0) in
≥ 12/16. If any gate fails: numbers written, RT stops (no layer/position search).
Routes (after the gates): (1) native m; (2) default AV description of h (greedy, 200 tokens) → text-only QA: the TARGET
reads 'Description of the model's state:\n<desc>\n' + 'Question: Who received the {O1}?\nAnswer:' with no injection →
m_text; (3) forced-prefix AV scoring '<explanation>\nThe person who received the {O1} is' under h, h_twin, h_0 → D as in
T2c; (4) round trip ĥ = AR(desc) · ‖h‖ / ‖AR(desc)‖ patched at the position → m_rt; control h + ε with ‖ε‖ = ‖ĥ − h‖ in a
random direction (3 seeds; m_pert = mean over seeds, per-seed values kept); cos(ĥ, h) reported. The patch hook replaces
exactly one row of the block-20 output (asserted) and leaves every other position untouched (the forward is recomputed
from the prompt; no KV cache).
Kill RT (pre-registered, only if the gates pass): CI (paired bootstrap over the 16 contexts, 1000 draws, seed 0) of
[m_rt − m_pert] ≤ 0 → MET.
Models: TARGET alone (native, gates, cache h) → free → AV (descriptions, forced prefix) + AR (reconstructions) → free → TARGET
alone (text-only QA, round-trip and perturbation patches). Never three co-resident.
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight.t2_prefix import Prefix  # noqa: E402
from src.model_utils import get_blocks, _block_output  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

TEMPLATE = "{N1} received the {O1}. {N2} received the {O2}.\nQuestion: Who received the {O1}?\nAnswer:"
QUESTION = "Question: Who received the {O1}?\nAnswer:"
TEXT_QA = "Description of the model's state:\n{desc}\n" + QUESTION
PREFIX_RT = "<explanation>\nThe person who received the {O1} is"
NAMES = [("Anna", "Tom"), ("Sara", "Ben")]
OBJECTS = [("key", "book"), ("coin", "letter"), ("cup", "hat"), ("map", "pen")]
G0_MIN, G1_TOL, G2_MIN = 14, 1e-2, 12
N_SEEDS = 3
N_BOOT, SEED = 1000, 0


def build_contexts() -> list[dict]:
    ctx = []
    for pi, (n1, n2) in enumerate(NAMES):
        for oi, (o1, o2) in enumerate(OBJECTS):
            pair = pi * len(OBJECTS) + oi
            a = TEMPLATE.format(N1=n1, N2=n2, O1=o1, O2=o2); b = TEMPLATE.format(N1=n2, N2=n1, O1=o1, O2=o2)
            ctx.append({"ctx_id": 2 * pair, "pair_id": pair, "side": "A", "text": a, "correct": n1, "other": n2, "O1": o1, "O2": o2, "twin_ctx_id": 2 * pair + 1})
            ctx.append({"ctx_id": 2 * pair + 1, "pair_id": pair, "side": "B", "text": b, "correct": n2, "other": n1, "O1": o1, "O2": o2, "twin_ctx_id": 2 * pair})
    assert len(ctx) == 16
    return ctx


class Patcher:
    """Replace one row of block-20's output at `pos` with `vec` (bf16) for a single forward; asserts exactly one row changed."""

    def __init__(self, model):
        self.blocks = get_blocks(model); self.model = model

    def logits(self, ids: torch.Tensor, pos: int | None = None, vec: torch.Tensor | None = None) -> torch.Tensor:
        box = {}

        def hook(_m, _i, output):
            h = _block_output(output)
            box["orig_row"] = h[0, pos].detach().clone(); h2 = h.clone(); h2[0, pos] = vec.to(h.dtype)
            diff = (h2 != h).any(-1)[0]; assert int(diff.sum()) <= 1 and (int(diff.sum()) == 0 or bool(diff[pos])), "patch touched more than one row"
            return (h2, *output[1:]) if isinstance(output, tuple) else h2
        hd = self.blocks[L.LAYER].register_forward_hook(hook) if vec is not None else None
        try:
            with torch.inference_mode():
                lg = self.model(ids.to(L.DEVICE), use_cache=False).logits[0, -1].float().cpu()
        finally:
            if hd is not None:
                hd.remove()
        return lg


def main():
    S = L.Settings("rt", template=TEMPLATE, question=QUESTION, text_qa=TEXT_QA, prefix=PREFIX_RT, names=NAMES, objects=OBJECTS, gates={"G0": f"native m>0 in ≥{G0_MIN}/16", "G1": f"self-patch max|Δlogit| ≤ {G1_TOL} in 16/16", "G2": f"twin patch Δm<0 in ≥{G2_MIN}/16"},
                   n_seeds=N_SEEDS, n_boot=N_BOOT, seed=SEED, kill="CI (paired bootstrap over 16 contexts) of [m_rt − m_pert(mean of 3 seeds)] ≤ 0 → MET (only after the gates)", tokenisation="raw text, add_special_tokens=False, no chat template")
    timings = {}; ctx = build_contexts()
    # ---------------- TARGET phase 1: native, gates, cache h
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0
    tok = tgt.tok; Pt = Patcher(tgt.model)
    for c in ctx:
        ids = tok(c["text"], return_tensors="pt", add_special_tokens=False)["input_ids"]; c["ids"] = ids; c["pos"] = int(ids.shape[1] - 1); c["n_tokens"] = int(ids.shape[1])
        assert tok.decode([int(ids[0, -1])]) == ":", tok.decode([int(ids[0, -1])])
        for k in ["correct", "other"]:
            t = tok.encode(" " + c[k], add_special_tokens=False); assert len(t) == 1, (c[k], t); c[f"id_{k}"] = t[0]
    S.update(candidate_ids={c["correct"]: c["id_correct"] for c in ctx}, n_tokens=[c["n_tokens"] for c in ctx])
    for c in ctx:
        lg = Pt.logits(c["ids"]); lp = torch.log_softmax(lg, -1); c["native_logits"] = lg
        c["m_native"] = float(lp[c["id_correct"]] - lp[c["id_other"]]); c["lp_correct_native"] = float(lp[c["id_correct"]]); c["top1_native"] = tok.decode([int(lg.argmax())])
        with torch.inference_mode():
            hs = tgt.model(c["ids"].to(L.DEVICE), output_hidden_states=True, use_cache=False).hidden_states
        c["h"] = L.to_cpu_f32(hs[L.LAYER + 1][0, c["pos"]]); c["norm_h"] = float(c["h"].norm())
    for c in ctx:  # G1 self-patch, G2 twin patch
        lg_self = Pt.logits(c["ids"], c["pos"], c["h"]); c["self_patch_max_abs_dlogit"] = float((lg_self - c["native_logits"]).abs().max())
        twin = ctx[c["twin_ctx_id"]]; lg_tw = Pt.logits(c["ids"], c["pos"], twin["h"]); lp = torch.log_softmax(lg_tw, -1)
        c["m_twin_patch"] = float(lp[c["id_correct"]] - lp[c["id_other"]]); c["dm_twin"] = c["m_twin_patch"] - c["m_native"]; c["cos_h_twin"] = L.cos(c["h"], twin["h"])
    g0 = sum(c["m_native"] > 0 for c in ctx); g1 = sum(c["self_patch_max_abs_dlogit"] <= G1_TOL for c in ctx); g2 = sum(c["dm_twin"] < 0 for c in ctx)
    gates = {"G0": (g0, g0 >= G0_MIN), "G1": (g1, g1 == 16), "G2": (g2, g2 >= G2_MIN)}
    gates_pass = all(v[1] for v in gates.values())
    L.append_disconfirmation("RT", "RT-gates", f"G0 native m>0 ≥{G0_MIN}/16; G1 self-patch max|Δlogit|≤{G1_TOL} 16/16; G2 twin patch Δm<0 ≥{G2_MIN}/16",
                             f"G0 {g0}/16 (mean m_native {np.mean([c['m_native'] for c in ctx]):.3f}); G1 {g1}/16 (max |Δlogit| {max(c['self_patch_max_abs_dlogit'] for c in ctx):.2e}); G2 {g2}/16 (mean Δm {np.mean([c['dm_twin'] for c in ctx]):.3f}; mean cos(h, h_twin) {np.mean([c['cos_h_twin'] for c in ctx]):.4f})",
                             "PASS" if gates_pass else "FAIL", "if FAIL, RT stops here: no layer or position search")
    tgt.free(); timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    pd.DataFrame([{k: v for k, v in c.items() if k not in ("ids", "h", "native_logits")} for c in ctx]).to_csv(L.OVERNIGHT / "rt_gates.csv", index=False)
    if not gates_pass:
        lines = ["# RT summary — gates FAILED; routes not run", "", f"git {L.git_hash()[:8]}; settings in rt_settings.json; rows in rt_gates.csv", "",
                 f"- G0 {g0}/16 (need ≥{G0_MIN}); G1 {g1}/16 (need 16); G2 {g2}/16 (need ≥{G2_MIN})", "", "| ctx | text | correct | m_native | top1 | self-patch max|Δlogit| | m_twin_patch | Δm | cos(h,h_twin) |", "|---|---|---|---|---|---|---|---|---|"]
        lines += [f"| {c['ctx_id']} | {c['text']!r} | {c['correct']} | {c['m_native']:+.3f} | {c['top1_native']!r} | {c['self_patch_max_abs_dlogit']:.2e} | {c['m_twin_patch']:+.3f} | {c['dm_twin']:+.3f} | {c['cos_h_twin']:.4f} |" for c in ctx]
        (L.OVERNIGHT / "rt_summary.md").write_text("\n".join(lines) + "\n"); S.finish(timings=timings, gates=gates, gates_pass=False); L.log("RT stopped at the gates"); return

    # ---------------- AV + AR
    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0; P = Prefix(av)
    with open(L.OVERNIGHT / "rt_outputs.jsonl", "w") as f:
        for c in ctx:
            try:
                r = av.verbalize(c["h"], max_new_tokens=200); c.update({"desc": r["explanation"], "raw_generation": r["raw_generation"], "parse_ok": r["parse_ok"], "cjk": r["cjk"]})
                pre = PREFIX_RT.format(O1=c["O1"]); ca, cb = " " + c["correct"], " " + c["other"]
                twin = ctx[c["twin_ctx_id"]]
                c["D_h"] = P.cont_logprob(c["h"], pre, ca)[0] - P.cont_logprob(c["h"], pre, cb)[0]
                c["D_twin"] = P.cont_logprob(twin["h"], pre, ca)[0] - P.cont_logprob(twin["h"], pre, cb)[0]
                c["D_0"] = P.cont_logprob(None, pre, ca)[0] - P.cont_logprob(None, pre, cb)[0]
                c["mentions_correct"] = c["correct"].lower() in (c["desc"] or "").lower(); c["mentions_other"] = c["other"].lower() in (c["desc"] or "").lower()
                c["error"] = ""
            except Exception:
                c["error"] = traceback.format_exc(); L.log(f"RT AV FAILED ctx {c['ctx_id']}")
            f.write(json.dumps({k: v for k, v in c.items() if k not in ("ids", "h", "native_logits")}, ensure_ascii=False, default=str) + "\n"); f.flush()
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0; timings["rss_av_ar_G"] = L.rss_mb() / 1024
    for c in ctx:
        pred = ar.predict(c["desc"] or ""); c["cos_hhat_h"] = L.cos(pred, c["h"]); c["hhat"] = pred / pred.norm() * c["h"].norm(); c["norm_hhat_minus_h"] = float((c["hhat"] - c["h"]).norm())
    ar.free(); av.free(); timings["rss_after_av_ar_free_G"] = L.rss_mb() / 1024

    # ---------------- TARGET phase 2: text-only QA, round-trip and perturbation patches
    t0 = time.time(); tgt = L.Target(); timings["target_reload_s"] = time.time() - t0; tok = tgt.tok; Pt = Patcher(tgt.model)
    for c in ctx:
        ids_t = tok(TEXT_QA.format(desc=c["desc"] or "", O1=c["O1"]), return_tensors="pt", add_special_tokens=False)["input_ids"]
        lp = torch.log_softmax(Pt.logits(ids_t), -1); c["m_text"] = float(lp[c["id_correct"]] - lp[c["id_other"]])
        lp = torch.log_softmax(Pt.logits(c["ids"], c["pos"], c["hhat"]), -1); c["m_rt"] = float(lp[c["id_correct"]] - lp[c["id_other"]])
        eps_norm = c["norm_hhat_minus_h"]; ms = []
        for s in range(N_SEEDS):
            g = torch.Generator().manual_seed(SEED + 100 * s + c["ctx_id"]); e = torch.randn(c["h"].shape, generator=g); e = e / e.norm() * eps_norm
            hp = c["h"] + e; c[f"cos_pert_{s}"] = L.cos(hp, c["h"])
            lp = torch.log_softmax(Pt.logits(c["ids"], c["pos"], hp), -1); ms.append(float(lp[c["id_correct"]] - lp[c["id_other"]])); c[f"m_pert_{s}"] = ms[-1]
        c["m_pert"] = float(np.mean(ms)); c["rt_minus_pert"] = c["m_rt"] - c["m_pert"]
    tgt.free()
    df = pd.DataFrame([{k: v for k, v in c.items() if k not in ("ids", "h", "native_logits", "hhat")} for c in ctx]); df.to_csv(L.OVERNIGHT / "rt_routes.csv", index=False)
    ok = df[df.error == ""]
    cl = ok.ctx_id.values
    ci = lambda v: L.cluster_bootstrap_mean(np.asarray(v, float), cl, n_boot=N_BOOT, seed=SEED)  # noqa: E731
    fm = lambda c, d=3: f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"  # noqa: E731
    k = ci(ok.rt_minus_pert); out = L.outcome_ci_at_or_below(k, 0.0, min_n=16)
    pres = {r: float((ok[f"m_{r}"] > 0).mean()) for r in ["native", "rt", "pert", "text", "twin_patch"]}
    donor = ci(ok.D_h - ok.D_twin); acc_fp = float(np.mean(np.concatenate([(ok.D_h > 0), (ok.D_twin < 0)])))
    L.append_disconfirmation("RT", "RT", "CI (paired bootstrap over 16 contexts) of [m_rt − m_pert] (round-trip patch vs displacement-matched random perturbation, mean of 3 seeds) ≤ 0",
                             f"mean m_rt−m_pert={fm(k)} n={k['n']}; m_native {ok.m_native.mean():.3f} m_rt {ok.m_rt.mean():.3f} m_pert {ok.m_pert.mean():.3f} m_text {ok.m_text.mean():.3f}; preservation rate (m>0) native {pres['native']:.3f} rt {pres['rt']:.3f} pert {pres['pert']:.3f} text {pres['text']:.3f}; "
                             f"cos(ĥ,h) mean {ok.cos_hhat_h.mean():.4f}; ‖ĥ−h‖ mean {ok.norm_hhat_minus_h.mean():.1f} (‖h‖ {ok.norm_h.mean():.1f}); forced-prefix donor sensitivity {fm(donor)} accuracy {acc_fp:.3f}; desc mentions correct name {int(ok.mentions_correct.sum())}/16 other {int(ok.mentions_other.sum())}/16",
                             out, "MET would mean reconstruction preserves the answer no better than a displacement-matched perturbation")
    lines = ["# RT summary — does task-relevant information survive the NLA round trip? (8-pair pilot; gates passed)", "",
             f"git {L.git_hash()[:8]}; settings in rt_settings.json; rt_gates.csv, rt_routes.csv, rt_outputs.jsonl", "",
             f"- gates: G0 {g0}/16, G1 {g1}/16 (max |Δlogit| {max(c['self_patch_max_abs_dlogit'] for c in ctx):.2e}), G2 {g2}/16 → PASS; errors {int((df.error != '').sum())}",
             "", "## Kill RT", "", f"- mean [m_rt − m_pert]: {fm(k)} n={k['n']} → **{out}**", "",
             "## Routes (16 contexts; m = lp(correct) − lp(other); paired CI over contexts)", "", "| route | mean m [CI] | preservation rate (m>0) |", "|---|---|---|"]
    for r, nm in [("native", "(1) native"), ("twin_patch", "twin donor patch (gate G2)"), ("text", "(2) AV description → text-only QA"), ("rt", "(4) round trip ĥ = AR(desc) patched"), ("pert", "(4c) displacement-matched random perturbation (mean of 3 seeds)")]:
        lines.append(f"| {nm} | {fm(ci(ok[f'm_{r}']))} | {pres[r]:.3f} |")
    lines += [f"| (3) forced prefix `{PREFIX_RT}`: donor sensitivity D(h) − D(h_twin) | {fm(donor)} | accuracy (32 activations) {acc_fp:.3f}; D(h_0) mean {ok.D_0.mean():+.3f} |",
              "", f"- cos(ĥ, h) mean {ok.cos_hhat_h.mean():.4f} (min {ok.cos_hhat_h.min():.4f}, max {ok.cos_hhat_h.max():.4f}); ‖ĥ − h‖ mean {ok.norm_hhat_minus_h.mean():.1f}; cos(h + ε, h) mean {ok[[f'cos_pert_{s}' for s in range(N_SEEDS)]].values.mean():.4f}; cos(h, h_twin) mean {ok.cos_h_twin.mean():.4f}",
              f"- per-seed m_pert means: " + ", ".join(f"{ok[f'm_pert_{s}'].mean():.3f}" for s in range(N_SEEDS)),
              "", "## Pre-committed reading key (from PLAN; the numbers decide)", "", "high cos(ĥ,h), gates pass, m_rt impaired vs m_pert → concrete loss of task-relevant information in reconstruction; m_rt preserved → a boundary on 'the AR discards specifics'; all NLA routes fail while native succeeds → interface limitation, not proof the activation lacks it; m_rt ≈ m_pert both failing → insufficient evidence of specifically semantic damage.",
              "", "## All 16 contexts verbatim", "", "| ctx | text | correct | m_native | m_twin_patch | m_text | m_rt | m_pert | cos(ĥ,h) | D(h) | D(h_twin) | desc mentions correct/other | description |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in df.itertuples():
        lines.append(f"| {r.ctx_id} | {r.text!r} | {r.correct} | {r.m_native:+.3f} | {r.m_twin_patch:+.3f} | {r.m_text:+.3f} | {r.m_rt:+.3f} | {r.m_pert:+.3f} | {r.cos_hhat_h:.4f} | {r.D_h:+.2f} | {r.D_twin:+.2f} | {r.mentions_correct}/{r.mentions_other} | {(r.desc or '').replace(chr(10), ' ')} |")
    lines.append("")
    (L.OVERNIGHT / "rt_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, gates=gates, gates_pass=True, kill_RT={"ci": k, "outcome": out}, preservation=pres, donor=donor, forced_prefix_acc=acc_fp, mean={r: float(ok[f"m_{r}"].mean()) for r in ["native", "rt", "pert", "text", "twin_patch"]})
    L.log(f"RT done: m_rt−m_pert {fm(k)} -> {out}")


if __name__ == "__main__":
    main()

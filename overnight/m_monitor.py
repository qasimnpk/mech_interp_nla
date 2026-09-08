"""M — does reconstruction error warn of an incorrect answer beyond the target's own uncertainty? (PLAN.md round 3c; GATED pilot).

  uv run python overnight/m_monitor.py

Problems (frozen generator, seed 0): 200 items 'Compute {a} × {b}. Work step by step, then write "Answer:" followed by the
number.' with a ∈ [100, 999], b ∈ [11, 99]; greedy TARGET generation ≤ 200 tokens on the raw-text prompt (no chat template,
as every activation in this project is taken on raw text). Correct iff the integer after the first 'Answer:' in the
generation equals a·b (no 'Answer:' → incorrect and flagged has_answer=False).
Gate GM: ≥ 20 incorrect and ≥ 20 correct; else stop.
Position: the ':' of the model's own first 'Answer:' = the first generated token whose cumulative decode contains
'Answer:'; the prefix (prompt + generated tokens up to and including it) is re-run; activation = hidden_states[21] at its
last token; comparators at the same position: next-token entropy (nats), top-1 margin (log-prob top1 − top2);
text-only: the TARGET reads the visible prefix + '\nWill the final answer be correct? Yes/No\nAnswer:' → logit(' Yes') −
logit(' No'). Items without 'Answer:' have no position and are excluded from the sample (count reported).
Sample: all incorrect items with a position (cap 40) and 40 correct items (rng seed 0). AV explanation (greedy, 200 tokens)
from the prefix activation; AR cosine = the primary NLA signal (frozen).
Kill M (pre-registered): AUROC(−cos, incorrect vs correct), bootstrap by problem, CI ≤ 0.60 → MET. Reported: AUROC of
entropy and of −margin; in-sample logistic model (entropy, margin) vs (entropy, margin, cos) — exploratory.
Models: TARGET alone → free → AV + AR co-resident → free.
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
from overnight.t1_arprobe import auroc  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

PROMPT = 'Compute {a} × {b}. Work step by step, then write "Answer:" followed by the number.'
YN_SUFFIX = "\nWill the final answer be correct? Yes/No\nAnswer:"
N_PROBLEMS, MAX_NEW, GM_MIN, CAP_INC, N_COR = 200, 200, 20, 40, 40
N_BOOT, SEED, THRESH = 1000, 0, 0.60
ANS_RE = re.compile(r"Answer:\s*\$?\s*(-?[\d,]+)")


def boot_auroc_by_problem(score, label, seed=SEED):
    score = np.asarray(score, float); label = np.asarray(label, bool); n = len(score)
    rng = np.random.default_rng(seed); vals = []
    for idx in rng.integers(0, n, size=(N_BOOT, n)):
        s, y = score[idx], label[idx]
        vals.append(auroc(s[y], s[~y]) if y.any() and (~y).any() else np.nan)
    vals = np.array(vals); vals = vals[~np.isnan(vals)]
    return {"auroc": auroc(score[label], score[~label]), "lo": float(np.percentile(vals, 2.5)), "hi": float(np.percentile(vals, 97.5)), "n": int(n), "n_pos": int(label.sum()), "n_neg": int((~label).sum())}


def main():
    S = L.Settings("m", prompt=PROMPT, yn_suffix=YN_SUFFIX, n_problems=N_PROBLEMS, max_new_tokens=MAX_NEW, gate={"min_incorrect": GM_MIN, "min_correct": GM_MIN}, sample={"incorrect_cap": CAP_INC, "correct": N_COR, "seed": SEED},
                   tokenisation="raw text, add_special_tokens=False, no chat template; greedy", n_boot=N_BOOT, seed=SEED, threshold=THRESH, kill="AUROC(−cos, incorrect vs correct) CI by problem ≤ 0.60 → MET")
    timings = {}
    rng = np.random.default_rng(SEED)
    probs = [{"pid": k, "a": int(rng.integers(100, 1000)), "b": int(rng.integers(11, 100))} for k in range(N_PROBLEMS)]
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0; tok = tgt.tok
    t0 = time.time()
    for p in probs:
        p["prompt"] = PROMPT.format(a=p["a"], b=p["b"]); p["truth"] = p["a"] * p["b"]
        try:
            ids = tok(p["prompt"], return_tensors="pt", add_special_tokens=False)["input_ids"].to(L.DEVICE)
            with torch.inference_mode():
                out = tgt.model.generate(ids, max_new_tokens=MAX_NEW, do_sample=False, pad_token_id=tok.pad_token_id or tok.eos_token_id)
            gen = out[0, ids.shape[1]:].tolist(); p["gen_ids"] = gen; p["generation"] = tok.decode(gen, skip_special_tokens=True); p["n_gen_tokens"] = len(gen)
            m = ANS_RE.search(p["generation"]); p["has_answer"] = "Answer:" in p["generation"]
            p["answer"] = int(m.group(1).replace(",", "")) if m else None; p["correct"] = p["answer"] == p["truth"]
            # position: first generated token whose cumulative decode contains 'Answer:'
            p["ans_tok"] = None
            if p["has_answer"]:
                for t in range(len(gen)):
                    if "Answer:" in tok.decode(gen[: t + 1], skip_special_tokens=True):
                        p["ans_tok"] = t; break
            p["error"] = ""
        except Exception:
            p["error"] = traceback.format_exc(); p["has_answer"] = False; p["correct"] = False; p["ans_tok"] = None; L.log(f"M gen FAILED {p['pid']}")
        if p["pid"] % 25 == 24:
            L.log(f"gen {p['pid'] + 1}/{N_PROBLEMS} ({(time.time() - t0) / (p['pid'] + 1):.1f} s each); correct so far {sum(q['correct'] for q in probs[: p['pid'] + 1])}")
    timings["target_s_per_gen"] = (time.time() - t0) / N_PROBLEMS
    n_cor = sum(p["correct"] for p in probs); n_inc = N_PROBLEMS - n_cor; n_noans = sum(not p["has_answer"] for p in probs); n_inc_pos = sum((not p["correct"]) and p["ans_tok"] is not None for p in probs)
    gate_ok = n_inc >= GM_MIN and n_cor >= GM_MIN
    L.append_disconfirmation("M", "M-gate", f"GM: ≥ {GM_MIN} incorrect and ≥ {GM_MIN} correct of {N_PROBLEMS} synthetic multiplications",
                             f"correct {n_cor}, incorrect {n_inc} (no 'Answer:' {n_noans}; incorrect with a position {n_inc_pos}); mean generation length {np.mean([p.get('n_gen_tokens', 0) for p in probs]):.0f} tokens",
                             "PASS" if gate_ok else "FAIL", "if FAIL, M stops here")
    pd.DataFrame([{k: v for k, v in p.items() if k != "gen_ids"} for p in probs]).to_csv(L.OVERNIGHT / "m_problems.csv", index=False)
    if not gate_ok:
        tgt.free(); (L.OVERNIGHT / "m_summary.md").write_text(f"# M summary — gate GM FAILED (correct {n_cor}, incorrect {n_inc}); stopped\n\ngit {L.git_hash()[:8]}; problems in m_problems.csv\n"); S.finish(timings=timings, gate_ok=False, n_correct=n_cor, n_incorrect=n_inc); L.log("M stopped at the gate"); return
    # ---------------- sample and positions
    inc = [p for p in probs if (not p["correct"]) and p["ans_tok"] is not None]; cor = [p for p in probs if p["correct"] and p["ans_tok"] is not None]
    rs = np.random.default_rng(SEED); inc_s = [inc[i] for i in rs.choice(len(inc), size=min(CAP_INC, len(inc)), replace=False)]; cor_s = [cor[i] for i in rs.choice(len(cor), size=min(N_COR, len(cor)), replace=False)]
    sample = sorted(inc_s + cor_s, key=lambda p: p["pid"]); yes = tok.encode(" Yes", add_special_tokens=False); no = tok.encode(" No", add_special_tokens=False); assert len(yes) == 1 and len(no) == 1
    d = tgt.model.config.hidden_size; H = np.zeros((len(sample), d), np.float32)
    for n, p in enumerate(sample):
        pids = tok(p["prompt"], add_special_tokens=False)["input_ids"] + p["gen_ids"][: p["ans_tok"] + 1]
        p["prefix_text"] = tok.decode(pids, skip_special_tokens=True); assert p["prefix_text"].rstrip().endswith("Answer:"), p["prefix_text"][-40:]
        with torch.inference_mode():
            o = tgt.model(torch.tensor([pids]).to(L.DEVICE), output_hidden_states=True, use_cache=False)
        H[n] = L.to_cpu_f32(o.hidden_states[L.LAYER + 1][0, -1]).numpy(); lp = torch.log_softmax(o.logits[0, -1].float(), -1).cpu(); pr = lp.exp()
        p["entropy"] = float(-(pr * lp).sum()); top = torch.topk(lp, 2); p["margin"] = float(top.values[0] - top.values[1]); p["top1_str"] = tok.decode([int(top.indices[0])]); p["prefix_tokens"] = len(pids)
        yids = tok(p["prefix_text"] + YN_SUFFIX, return_tensors="pt", add_special_tokens=False)["input_ids"].to(L.DEVICE)
        with torch.inference_mode():
            lg = tgt.model(yids, use_cache=False).logits[0, -1].float().cpu()
        p["yes_minus_no"] = float(lg[yes[0]] - lg[no[0]])
    tgt.free(); np.savez(L.OUT / "m_acts.npz", H=H, pid=np.array([p["pid"] for p in sample]))
    # ---------------- AV + AR
    t0 = time.time(); av = L.AV(); ar = L.AR(); timings["av_ar_load_s"] = time.time() - t0
    t0 = time.time()
    for n, p in enumerate(sample):
        try:
            r = av.verbalize(torch.from_numpy(H[n]), max_new_tokens=200); p.update({"explanation": r["explanation"], "parse_ok": r["parse_ok"], "cjk": r["cjk"]})
            p["cos"] = L.cos(ar.predict(r["explanation"]).numpy(), H[n]); p["nla_error"] = ""
        except Exception:
            p["nla_error"] = traceback.format_exc(); p["cos"] = np.nan; L.log(f"M NLA FAILED {p['pid']}")
        if n % 20 == 19:
            L.log(f"NLA {n + 1}/{len(sample)} ({(time.time() - t0) / (n + 1):.1f} s each)")
    timings["nla_s_per_item"] = (time.time() - t0) / len(sample)
    ar.free(); av.free()
    df = pd.DataFrame([{k: v for k, v in p.items() if k != "gen_ids"} for p in sample]); df.to_csv(L.OVERNIGHT / "m_scores.csv", index=False)
    ok = df[df.nla_error == ""].reset_index(drop=True); y = ~ok.correct.astype(bool).values
    A = {"neg_cos": boot_auroc_by_problem(-ok.cos.values, y), "entropy": boot_auroc_by_problem(ok.entropy.values, y), "neg_margin": boot_auroc_by_problem(-ok.margin.values, y), "neg_yes_minus_no": boot_auroc_by_problem(-ok.yes_minus_no.values, y)}
    k = A["neg_cos"]; out = "INCONCLUSIVE" if (k["n_pos"] < GM_MIN or k["n_neg"] < GM_MIN) else ("MET" if k["hi"] <= THRESH else ("NOT MET" if k["lo"] > THRESH else "INCONCLUSIVE"))
    # exploratory in-sample logistic model
    from sklearn.linear_model import LogisticRegression
    Z = ok[["entropy", "margin", "cos"]].values; Z = (Z - Z.mean(0)) / (Z.std(0) + 1e-9)
    m2 = LogisticRegression(C=1e6, max_iter=1000).fit(Z[:, :2], y); m3 = LogisticRegression(C=1e6, max_iter=1000).fit(Z, y)
    au2 = auroc(m2.decision_function(Z[:, :2])[y], m2.decision_function(Z[:, :2])[~y]); au3 = auroc(m3.decision_function(Z)[y], m3.decision_function(Z)[~y])
    fa = lambda b: f"{b['auroc']:.4f} [{b['lo']:.4f},{b['hi']:.4f}]"  # noqa: E731
    L.append_disconfirmation("M", "M", "AUROC(−cos(AR(desc), h), incorrect vs correct) at the model's own 'Answer:' token, CI by problem ≤ 0.60",
                             f"AUROC={fa(k)} n={k['n']} (incorrect {k['n_pos']}, correct {k['n_neg']}); entropy {fa(A['entropy'])}; −margin {fa(A['neg_margin'])}; text-only −(yes−no) {fa(A['neg_yes_minus_no'])}; "
                             f"in-sample logistic AUROC entropy+margin {au2:.4f} vs +cos {au3:.4f} (cos coef {m3.coef_[0][2]:+.3f}, standardised; exploratory); mean cos correct {ok.cos[~y].mean():.4f} incorrect {ok.cos[y].mean():.4f}; problems correct {n_cor}/{N_PROBLEMS}",
                             out, "MET would mean reconstruction error does not separate incorrect from correct answers beyond chance-level 0.60")
    lines = ["# M summary — does reconstruction error warn of an incorrect answer? (synthetic multiplication pilot)", "",
             f"git {L.git_hash()[:8]}; settings in m_settings.json; m_problems.csv (200), m_scores.csv (sample); activations out/m_acts.npz", "",
             f"- problems: correct {n_cor}, incorrect {n_inc} (no 'Answer:' {n_noans}); gate GM PASS; generation {timings['target_s_per_gen']:.1f} s each, mean {np.mean([p.get('n_gen_tokens', 0) for p in probs]):.0f} tokens; sample incorrect {len(inc_s)} correct {len(cor_s)}; NLA {timings['nla_s_per_item']:.1f} s/item; parse_ok {int(df.parse_ok.fillna(False).astype(bool).sum())}/{len(df)}",
             "", "## Kill M", "", f"- AUROC(−cos) incorrect vs correct: {fa(k)} → **{out}**", "",
             "| signal (higher = predicts incorrect) | AUROC [CI by problem] |", "|---|---|", f"| −cos(AR(desc), h) (NLA) | {fa(A['neg_cos'])} |", f"| next-token entropy at 'Answer:' | {fa(A['entropy'])} |", f"| −(top-1 margin) | {fa(A['neg_margin'])} |", f"| −(yes − no) text-only self-check | {fa(A['neg_yes_minus_no'])} |",
             "", f"- in-sample logistic (exploratory): entropy + margin AUROC {au2:.4f}; + cos {au3:.4f}; standardised coefficients with cos: entropy {m3.coef_[0][0]:+.3f}, margin {m3.coef_[0][1]:+.3f}, cos {m3.coef_[0][2]:+.3f}",
             f"- mean cos: correct {ok.cos[~y].mean():.4f}, incorrect {ok.cos[y].mean():.4f}; mean entropy correct {ok.entropy[~y].mean():.3f} incorrect {ok.entropy[y].mean():.3f}",
             "", "## Five verbatim cases (first 3 incorrect, first 2 correct in the sample)", ""]
    for p in [q for q in sample if not q["correct"]][:3] + [q for q in sample if q["correct"]][:2]:
        lines += [f"### problem {p['pid']}: {p['a']} × {p['b']} = {p['truth']}; model answer {p['answer']} ({'correct' if p['correct'] else 'incorrect'}); cos {p.get('cos', float('nan')):.4f}; entropy {p['entropy']:.3f}; margin {p['margin']:.3f}; yes−no {p['yes_minus_no']:+.2f}",
                  f"- generation: {p['generation'].replace(chr(10), ' ⏎ ')}", f"- explanation: {p.get('explanation')}", ""]
    (L.OVERNIGHT / "m_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, gate_ok=True, n_correct=n_cor, n_incorrect=n_inc, kill_M={"stats": k, "outcome": out}, aurocs=A, logistic={"au2": au2, "au3": au3, "coef3": m3.coef_[0].tolist()})
    L.log(f"M done: AUROC(−cos) {fa(k)} -> {out}")


if __name__ == "__main__":
    main()

"""X1b — OPTIONAL: cross-layer full generations with the fixed layer-20 AV (PLAN.md round 3c; AV + AR; descriptive, no kill).

  uv run python overnight/x1b_gen.py

40 pilot stimuli (0–39), greedy 200-token explanations from the block-16 and block-27 activations (out/x1_acts.npz from X1;
injection unchanged, norm 150). Reported per layer (block-20 = the round-1 explanations.jsonl on the same stimuli, scored
with the same mechanical rules here): parse_ok, CJK rate, quoted-final-token accuracy, 'expecting'-candidate hit rate on the
target's top-1 next token, word overlap (Jaccard over lower-cased word sets) with the block-20 explanation, cos(AR(desc), h_l)
and cos(AR(desc), h_20).
Mechanical rules (this stage's own; the desk's figures 0.444 own / 0.029 shuffled at block 20 were computed with an
unverified rule and are quoted as such): quoted-final-token = some double-quoted span in the explanation, stripped of
whitespace, equals token_str.strip(); expecting-candidates = double-quoted spans in the text after the first occurrence of
'expecting'; hit = the first whitespace token of some candidate, stripped of punctuation, equals the target's top-1 next
token string (t0_entropy.csv top1_str) stripped of whitespace and punctuation; shuffled-pairing floor = the same hit rule
against the top-1 of stimulus (i + 20) mod 40.
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

LAYERS_GEN = [16, 27]
PILOT = list(range(40))
FIXED = [0, 7, 19, 33]
QUOTE_RE = re.compile(r"[\"“”]([^\"“”]{1,80})[\"“”]")
PUNCT = ".,;:!?\"'()[]{}“”‘’"
N_BOOT, SEED = 1000, 0


def quoted_spans(text: str) -> list[str]:
    return [m.group(1) for m in QUOTE_RE.finditer(text or "")]


def quoted_token_ok(text: str, token_str: str) -> bool:
    return any(q.strip() == token_str.strip() for q in quoted_spans(text))


def expecting_candidates(text: str) -> list[str]:
    t = text or ""; i = t.find("expecting")
    return quoted_spans(t[i:]) if i >= 0 else []


def hit(cands: list[str], top1: str) -> bool:
    tgt = top1.strip().strip(PUNCT)
    if not tgt:
        return False
    firsts = [c.strip().split()[0].strip(PUNCT) for c in cands if c.strip()]
    return any(f == tgt for f in firsts)


def jaccard(a: str, b: str) -> float:
    A = set(w.strip(PUNCT).lower() for w in (a or "").split()); B = set(w.strip(PUNCT).lower() for w in (b or "").split()); A.discard(""); B.discard("")
    return len(A & B) / max(1, len(A | B))


def main():
    S = L.Settings("x1b", layers=LAYERS_GEN, pilot=PILOT, fixed=FIXED, rules="see module docstring", desk_figures={"block20_own_hit": 0.444, "block20_shuffled_floor": [0.029, 0.012, 0.056], "note": "desk-computed, rule unverified"}, n_boot=N_BOOT, seed=SEED, no_kill=True)
    timings = {}
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False); ent = pd.read_csv(L.OVERNIGHT / "t0_entropy.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    X = np.load(L.OUT / "x1_acts.npz"); layers = list(X["layers"]); Hst = X["H_stim"]; h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    ex20 = {}
    for ln in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if ln.strip():
            r = json.loads(ln); ex20[r["stim_idx"]] = r
    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    recs = []; t0 = time.time()
    with open(L.OVERNIGHT / "x1b_outputs.jsonl", "w") as f:
        for i in PILOT:
            for l in LAYERS_GEN:
                rec = {"stim_idx": i, "layer": l, "token_str": st.token_str[i], "top1_str": ent.top1_str[i], "error": ""}
                try:
                    rec.update(av.verbalize(torch.from_numpy(Hst[i, layers.index(l)]), max_new_tokens=200))
                except Exception:
                    rec["error"] = traceback.format_exc(); rec["explanation"] = ""; rec["parse_ok"] = False; rec["cjk"] = False; L.log(f"X1b AV FAILED {i} L{l}")
                recs.append(rec); f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            if i % 10 == 9:
                L.log(f"{i + 1}/40 stimuli, {(time.time() - t0) / (2 * (i + 1)):.1f} s/gen")
    timings["av_s_per_gen"] = (time.time() - t0) / (2 * len(PILOT))
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0
    rows = []
    for i in PILOT:
        e20 = ex20[i]["explanation"] or ""
        for l in LAYERS_GEN + [20]:
            if l == 20:
                txt = e20; rec = {"parse_ok": ex20[i].get("parse_ok"), "cjk": ex20[i].get("cjk"), "error": ""}
            else:
                rec = next(r for r in recs if r["stim_idx"] == i and r["layer"] == l); txt = rec["explanation"] or ""
            pred = ar.predict(txt).numpy() if txt else None
            hl = Hst[i, layers.index(l)]
            j = (i + 20) % 40
            rows.append({"stim_idx": i, "layer": l, "parse_ok": bool(rec.get("parse_ok")), "cjk": bool(rec.get("cjk")), "error": rec.get("error", ""), "n_words": len(txt.split()),
                         "quoted_token_ok": quoted_token_ok(txt, st.token_str[i]), "n_expecting_cands": len(expecting_candidates(txt)), "expect_hit": hit(expecting_candidates(txt), ent.top1_str[i]),
                         "expect_hit_shuffled": hit(expecting_candidates(txt), ent.top1_str[j]), "jaccard_vs_L20": jaccard(txt, e20) if l != 20 else 1.0,
                         "cos_AR_h_l": L.cos(pred, hl) if pred is not None else np.nan, "cos_AR_h20": L.cos(pred, h20[i]) if pred is not None else np.nan, "cos_h_l_h20": L.cos(hl, h20[i])})
    ar.free(); av.free()
    df = pd.DataFrame(rows); df.to_csv(L.OVERNIGHT / "x1b_scores.csv", index=False)
    ci = lambda v: L.cluster_bootstrap_mean(np.asarray(v, float), np.arange(len(v)), n_boot=N_BOOT, seed=SEED)  # noqa: E731
    fm = lambda c, d=3: f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"  # noqa: E731
    lines = ["# X1b summary — cross-layer full generations with the layer-20 AV (40 pilot stimuli; descriptive, no kill)", "",
             f"git {L.git_hash()[:8]}; settings in x1b_settings.json; generations in x1b_outputs.jsonl; per-item scores in x1b_scores.csv", "",
             f"- 80 generations ({timings['av_s_per_gen']:.1f} s each); block-20 row = the round-1 explanations on the same stimuli scored with the same rules; errors {int((df.error != '').sum())}",
             "- rules: quoted-final-token = a double-quoted span equals token_str; expecting-hit = first word of a quoted span after 'expecting' equals the target's top-1 next token (punctuation stripped); shuffled floor pairs stimulus i with the top-1 of (i+20) mod 40. The desk's block-20 figures (own 0.444, shuffled 0.029 [0.012, 0.056]) used an unverified rule and are not reproduced here by construction.",
             "", "| block | parse_ok | CJK | quoted-final-token acc | expecting cands/expl | expecting hit (own top-1) | expecting hit (shuffled) | Jaccard vs L20 expl | cos(AR(desc), h_l) | cos(AR(desc), h_20) | cos(h_l, h_20) | words |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for l in LAYERS_GEN + [20]:
        g = df[df.layer == l]
        lines.append(f"| {l}{' (training)' if l == 20 else ''} | {g.parse_ok.mean():.3f} | {g.cjk.mean():.3f} | {fm(ci(g.quoted_token_ok))} | {g.n_expecting_cands.mean():.2f} | {fm(ci(g.expect_hit))} | {fm(ci(g.expect_hit_shuffled))} | {g.jaccard_vs_L20.mean():.3f} | {fm(ci(g.cos_AR_h_l.fillna(0)))} | {fm(ci(g.cos_AR_h20.fillna(0)))} | {g.cos_h_l_h20.mean():.3f} | {g.n_words.mean():.0f} |")
    lines += ["", "## Four fixed examples (stimuli 0, 7, 19, 33)", ""]
    for i in FIXED:
        lines.append(f"### stimulus {i} (token {st.token_str[i]!r}; target top-1 {ent.top1_str[i]!r})")
        lines.append(f"- block 20 (round 1): {ex20[i]['explanation']}")
        for l in LAYERS_GEN:
            rec = next(r for r in recs if r["stim_idx"] == i and r["layer"] == l)
            lines.append(f"- block {l} (parse_ok={rec.get('parse_ok')}, cjk={rec.get('cjk')}): {rec.get('explanation')}")
        lines.append("")
    (L.OVERNIGHT / "x1b_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, per_layer={int(l): {c: float(df[df.layer == l][c].mean()) for c in ["parse_ok", "cjk", "quoted_token_ok", "expect_hit", "expect_hit_shuffled", "jaccard_vs_L20", "cos_AR_h_l", "cos_AR_h20"]} for l in LAYERS_GEN + [20]})
    L.log("X1b done")


if __name__ == "__main__":
    main()

"""T4 — perturbing the injected vector with a target-model concept direction (PLAN.md round 3; pilot set 0-39).

  uv run python overnight/t4_inject.py

Directions (difference of means in the TARGET at block 20, last token; sentences in t34_sentences.py):
  sports = mean(32 sports sentences) - mean(32 length-matched neutral sentences)
  french = mean(32 French sentences) - mean(their 32 English translations)
Norm-preserving mix: h' = ||h|| * normalize((1-beta) h_hat + beta d_hat), beta in {-0.5, -0.25, +0.25, +0.5},
plus a norm-matched random unit direction (np.random.default_rng(1000 + stim_idx)) at beta = +0.5.
Per item the ACTUAL geometry is recorded: cos(h, h') and the angle in degrees (the AV renormalises to 150).
Each h' is verbalised with the default AV prompt (greedy, 200 tokens) and scored by the AR against h and h'.
Measures: sports keyword mention (SPORTS_KEYWORDS, whole-word, case-insensitive), French fraction and the
S5 mechanical pass (>= 0.15), parse_ok, cjk, topic preservation (detok(topic_true) in the explanation,
case-insensitive), word-sequence similarity (difflib ratio over words) and word Jaccard to the unperturbed
round-1 explanation (explanations.jsonl).  Baseline rates on the unperturbed explanations are reported.
Kill T4 (pre-registered): sports mention rate < 0.25 at both positive beta -> MET.  Per beta, bootstrap CI
by stimulus: below (hi < 0.25) / above (lo >= 0.25) / straddles.  MET if both below; NOT MET if either
above; else INCONCLUSIVE.
Prior art (fetched 2026-09-06): LessWrong 'Models are blind outside the J-space. NLAs aren't.' —
Llama-3.3-70B + Anthropic's L53 NLA; difference-of-means concept vectors ('Tell me about {word}' minus
100 baseline words) injected norm-matched; NLA named the concept 100% (n=16 concepts), zero false positives,
with confabulated context noted.  T4 is therefore a replication/control on the 7B pair, not a finding.
TARGET first (freed), then AV + AR co-resident.  Stimulus-outer loop; stops generating at the stage cap.
"""
from __future__ import annotations

import difflib
import json
import math
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)
from overnight import t34_sentences as T  # noqa: E402
from overnight.t1_arprobe import detok  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

THRESH = 0.25
BETAS = [-0.5, -0.25, 0.25, 0.5]
N_PILOT = 40
CAP_S = 85 * 60
FIXED = [0, 7, 19, 33]
CELLS = [("sports", b) for b in BETAS] + [("french", b) for b in BETAS] + [("random", 0.5)]


def unit(v):
    v = np.asarray(v, np.float64); return v / (np.linalg.norm(v) + 1e-30)


def mix(h, d, beta):
    hn = np.linalg.norm(h)
    return (hn * unit((1 - beta) * unit(h) + beta * unit(d))).astype(np.float32)


def words(s):
    return (s or "").lower().split()


def target_phase(timings):
    t0 = time.time(); tgt = L.Target(); timings["target_load_s"] = time.time() - t0

    def acts(sents):
        out = []
        for s in sents:
            ids = tgt.tok(s, return_tensors="pt", add_special_tokens=False)["input_ids"]
            out.append(L.to_cpu_f32(tgt.hidden_states(ids)[L.LAYER + 1][0, -1]).numpy())
        return np.stack(out)
    t0 = time.time()
    A = {"sports": acts(T.SPORTS), "neutral": acts(T.NEUTRAL), "french": acts([f for _, f in T.FRENCH_EN_PAIRS]), "english": acts([e for e, _ in T.FRENCH_EN_PAIRS])}
    timings["target_s_per_short"] = (time.time() - t0) / 128
    tgt.free(); timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    D = {"sports": A["sports"].mean(0) - A["neutral"].mean(0), "french": A["french"].mean(0) - A["english"].mean(0)}
    np.savez(L.OUT / "t4_dirs.npz", **{f"acts_{k}": v for k, v in A.items()}, **{f"dir_{k}": v for k, v in D.items()})
    return D, A


def main():
    S = L.Settings("t4", threshold=THRESH, betas=BETAS, n_pilot=N_PILOT, cap_s=CAP_S, cells=CELLS, fixed_examples=FIXED,
                   directions="difference of means, TARGET hidden_states[21] last token; sports-neutral, french-english (t34_sentences.py)",
                   mix="h' = ||h|| * normalize((1-beta)*h/||h|| + beta*d/||d||); random: d = rng(1000+stim_idx).standard_normal(d)",
                   av_max_new_tokens=200, decoding="greedy", sports_keywords=T.SPORTS_KEYWORDS, french_rule="S5 V4: stoplist fraction >= 0.15",
                   similarity="difflib.SequenceMatcher(None, words(V0), words(desc')).ratio(); Jaccard over lowercase word sets",
                   outcome_rule="per positive beta: CI hi < 0.25 -> below; lo >= 0.25 -> above; MET if both below, NOT MET if either above, else INCONCLUSIVE",
                   prior_art="lesswrong.com/posts/LhDJdccLszLEAqgZ9 (fetched 2026-09-06): Llama-3.3-70B, L53 NLA, diff-of-means concept vectors, 100% naming n=16, 0 false positives")
    timings = {}
    acts = np.load(L.OUT / "acts_L20.npz"); h20 = acts["h20"]
    top = pd.read_csv(L.OVERNIGHT / "t0_topics.csv", keep_default_na=False).sort_values("stim_idx").reset_index(drop=True)
    s1 = pd.read_csv(L.OVERNIGHT / "s1_recon.csv")
    expl = {}
    for line in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); expl[r["stim_idx"]] = r["explanation"] or ""
    D, A = target_phase(timings)
    geo = {k: {"norm": float(np.linalg.norm(D[k])), "mean_norm_class_a": float(np.linalg.norm(A[k if k == 'sports' else 'french'], axis=1).mean()),
               "cos_with_mean_h20": float(L.cos(D[k], h20.mean(0)))} for k in D}
    geo["cos_sports_french"] = float(L.cos(D["sports"], D["french"]))
    S.update(direction_geometry=geo)
    L.log(f"directions: {geo}")

    t0 = time.time(); av = L.AV(); timings["av_load_s"] = time.time() - t0
    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0
    rows = []; t_start = time.time(); stopped = None
    with open(L.OVERNIGHT / "t4_outputs.jsonl", "w") as f:
        for i in range(N_PILOT):
            if time.time() - t_start > CAP_S:
                stopped = i; L.log(f"stage cap reached before stimulus {i}; stopping generation"); break
            h = h20[i]; topic = detok(top.topic_true[i]); v0 = expl[i]
            rng = np.random.default_rng(1000 + i); drand = rng.standard_normal(h.shape[0])
            for direction, beta in CELLS:
                d = drand if direction == "random" else D[direction]
                hp = mix(h, d, beta)
                rec = {"stim_idx": i, "direction": direction, "beta": beta, "cos_h_hprime": L.cos(h, hp),
                       "angle_deg": math.degrees(math.acos(max(-1.0, min(1.0, L.cos(h, hp))))), "norm_h": float(np.linalg.norm(h)),
                       "cos_hprime_dir": L.cos(hp, d), "cos_h_dir": L.cos(h, d), "topic_true": topic, "error": None}
                try:
                    r = av.verbalize(torch.from_numpy(hp)); rec.update(r)
                    e = r["explanation"]
                    m, hits = T.sports_mention(e)
                    rec.update({"sports_mention": m, "sports_hits": hits, "french_frac": T.french_frac(e), "french_pass": T.french_frac(e) >= T.FRENCH_PASS_THRESHOLD,
                                "topic_preserved": topic.lower() in e.lower(), "n_words": len(e.split()),
                                "seq_sim_v0": difflib.SequenceMatcher(None, words(v0), words(e)).ratio(),
                                "jaccard_v0": len(set(words(v0)) & set(words(e))) / max(1, len(set(words(v0)) | set(words(e))))})
                    p = ar.predict(e).numpy()
                    rec["cos_ar_h"] = L.cos(p, h); rec["cos_ar_hprime"] = L.cos(p, hp); rec["cos_v0_s1"] = float(s1.cos_own.iloc[i])
                except Exception:
                    rec["error"] = traceback.format_exc(); L.log(f"FAILED stim {i} {direction} {beta}")
                rows.append(rec); f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            L.log(f"stim {i + 1}/{N_PILOT} done, {len(rows)} items, {(time.time() - t_start) / len(rows):.1f} s/item")
    timings["s_per_item"] = (time.time() - t_start) / max(1, len(rows)); timings["n_items"] = len(rows); timings["stopped_at_stimulus"] = stopped
    av.free(); ar.free()

    df = pd.DataFrame(rows); ok = df[df.error.isna()]
    # baseline rates on the unperturbed explanations (pilot)
    base = pd.DataFrame([{"stim_idx": i, "sports_mention": T.sports_mention(expl[i])[0], "french_frac": T.french_frac(expl[i]),
                          "french_pass": T.french_frac(expl[i]) >= T.FRENCH_PASS_THRESHOLD, "topic_preserved": detok(top.topic_true[i]).lower() in expl[i].lower(),
                          "n_words": len(expl[i].split())} for i in range(N_PILOT)])

    def ci(vals, cl):
        return L.cluster_bootstrap_mean(np.asarray(vals, float), cl)

    def cell(direction, beta):
        return ok[(ok.direction == direction) & (ok.beta == beta)]

    verdicts = {}
    for b in [0.25, 0.5]:
        c = cell("sports", b); r = ci(c.sports_mention, c.stim_idx)
        verdicts[b] = {"ci": r, "class": "below" if r["hi"] < THRESH else ("above" if r["lo"] >= THRESH else "straddles")}
    cls = [verdicts[b]["class"] for b in [0.25, 0.5]]
    out = "MET" if all(c == "below" for c in cls) else ("NOT MET" if any(c == "above" for c in cls) else "INCONCLUSIVE")
    if any(verdicts[b]["ci"]["n"] < 20 for b in verdicts):
        out = "INCONCLUSIVE"
    rb = ci(base.sports_mention, base.stim_idx)
    L.append_disconfirmation("T4", "T4", "sports mention rate < 0.25 at both positive β (pilot, CI by stimulus)",
                             "; ".join(f"β={b}: {verdicts[b]['ci']['mean']:.3f} [{verdicts[b]['ci']['lo']:.3f},{verdicts[b]['ci']['hi']:.3f}] n={verdicts[b]['ci']['n']} ({verdicts[b]['class']})" for b in [0.25, 0.5])
                             + f"; baseline unperturbed {rb['mean']:.3f}; random β=0.5 {cell('random', 0.5).sports_mention.mean():.3f}",
                             out, "MET would mean a large injected concept direction does not surface in the description (readout not direction-additive)")

    lines = ["# T4 summary — perturbing the injected vector with TARGET concept directions (pilot 0–39)", "",
             f"git {L.git_hash()[:8]}; settings in t4_settings.json; items in t4_outputs.jsonl; directions in out/t4_dirs.npz", "",
             f"- items {len(df)} (errors {int(df.error.notna().sum())}); {timings['s_per_item']:.1f} s/item; stopped at stimulus {stopped} (None = all {N_PILOT} done)",
             f"- direction geometry: ||d_sports|| {geo['sports']['norm']:.1f}, ||d_french|| {geo['french']['norm']:.1f}, cos(d_sports, d_french) {geo['cos_sports_french']:.3f}; "
             f"cos(d, mean h20): sports {geo['sports']['cos_with_mean_h20']:.3f}, french {geo['french']['cos_with_mean_h20']:.3f}",
             f"- prior art: LessWrong 'Models are blind outside the J-space. NLAs aren't.' (Llama-3.3-70B, L53 NLA, diff-of-means concept vectors injected norm-matched; NLA named the concept 100 %, n=16, 0 false positives). T4 is a replication/control on this 7B pair.",
             "", "## Kill T4", "",
             "; ".join(f"β={b}: sports mention {verdicts[b]['ci']['mean']:.3f} [{verdicts[b]['ci']['lo']:.3f},{verdicts[b]['ci']['hi']:.3f}] ({verdicts[b]['class']})" for b in [0.25, 0.5]) + f" → **{out}**",
             f"- baseline (unperturbed round-1 explanations, pilot): sports mention {rb['mean']:.3f}, french pass {base.french_pass.mean():.3f}, topic preserved {base.topic_preserved.mean():.3f}, mean words {base.n_words.mean():.1f}",
             "", "## Grid (mean over pilot stimuli; CI by stimulus where shown)", "",
             "| direction | β | n | cos(h,h') | angle° | sports mention [CI] | french pass | french frac | topic preserved | parse_ok | cjk | words | seq-sim V0 | Jaccard V0 | cos(AR,h) | cos(AR,h') | cos(AR,h) − cos V0 |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for direction, beta in CELLS:
        c = cell(direction, beta)
        if not len(c):
            lines.append(f"| {direction} | {beta:+} | 0 | | | | | | | | | | | | | | |"); continue
        sm = ci(c.sports_mention, c.stim_idx)
        lines.append(f"| {direction} | {beta:+} | {len(c)} | {c.cos_h_hprime.mean():.3f} | {c.angle_deg.mean():.1f} | {sm['mean']:.3f} [{sm['lo']:.3f},{sm['hi']:.3f}] | {c.french_pass.mean():.3f} | {c.french_frac.mean():.3f} | "
                     f"{c.topic_preserved.mean():.3f} | {c.parse_ok.mean():.3f} | {c.cjk.mean():.3f} | {c.n_words.mean():.1f} | {c.seq_sim_v0.mean():.3f} | {c.jaccard_v0.mean():.3f} | "
                     f"{c.cos_ar_h.mean():.4f} | {c.cos_ar_hprime.mean():.4f} | {(c.cos_ar_h - c.cos_v0_s1).mean():+.4f} |")
    lines += ["", "## Sports keywords hit (positive β), counts over items", ""]
    for b in [0.25, 0.5]:
        c = cell("sports", b); cnt = pd.Series([k for hs in c.sports_hits for k in hs]).value_counts()
        lines.append(f"- β={b}: " + (", ".join(f"{k}:{v}" for k, v in cnt.items()) if len(cnt) else "(none)"))
    c = cell("random", 0.5); cnt = pd.Series([k for hs in c.sports_hits for k in hs]).value_counts()
    lines.append("- random β=0.5: " + (", ".join(f"{k}:{v}" for k, v in cnt.items()) if len(cnt) else "(none)"))
    lines += ["", "## Four fixed examples (stimuli 0, 7, 19, 33; sports β=+0.5 and french β=+0.5 vs unperturbed)", ""]
    for i in FIXED:
        lines += [f"### stim {i} — topic {detok(top.topic_true[i])}", "", "**unperturbed (round 1):**", "```", expl[i], "```"]
        for direction in ["sports", "french"]:
            r = df[(df.stim_idx == i) & (df.direction == direction) & (df.beta == 0.5)]
            if len(r):
                r = r.iloc[0]
                lines += [f"**{direction} β=+0.5** (cos(h,h')={r.cos_h_hprime:.3f}, sports={r.get('sports_mention')}, french_frac={r.get('french_frac', float('nan')):.2f}, cos(AR,h)={r.get('cos_ar_h', float('nan')):.3f}, seq-sim={r.get('seq_sim_v0', float('nan')):.2f}):",
                          "```", str(r.get("explanation") if r.get("parse_ok") else r.get("raw_generation")), "```"]
        lines.append("")
    (L.OVERNIGHT / "t4_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_T4={"verdicts": verdicts, "outcome": out}, baseline={"sports": rb, "french_pass": float(base.french_pass.mean()), "topic": float(base.topic_preserved.mean())},
             n_items=len(df), n_errors=int(df.error.notna().sum()), stopped_at_stimulus=stopped)
    L.log(f"T4 done: {out}; " + "; ".join(f"β={b} {verdicts[b]['ci']['mean']:.3f}" for b in verdicts))


if __name__ == "__main__":
    main()

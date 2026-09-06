"""T0 — artifact check + topic and entropy sidecar (PLAN.md round 3).

  uv run python overnight/t0_check.py

1. Assert every reused round-1/2 file exists with the round-1 row counts (200 / 200 / 671 / 538 / 490)
   and that out/acts_L20.npz and out/recon_L20.npz exist with the expected shapes. (If a cache were
   missing, the plan says regenerate as round-2 R0 did; this script asserts and stops instead so the
   orchestrator can run r0_check.py explicitly — nothing is regenerated silently.)
2. Topics: topic_true = first ` = X = ` heading of each stimulus's wikitext document;
   topic_foreign = topic_true of stimulus (stim_idx + 100) mod 200. -> t0_topics.csv
3. Entropy: one TARGET pass per document (batch 1, raw text, add_special_tokens=False, truncate 512
   exactly as S0/R0), next-token entropy (nats) and top-1 probability of the logits at `pos`, the
   top-1 next-token string, the actual next token (pos+1) and its probability. -> t0_entropy.csv
4. Measured per-item costs: TARGET forward per 512-token doc, AV greedy generation per explanation
   (3 pilot stimuli, max_new_tokens=200), AR score per text (10 texts). -> t0_check.md re-budget table.
No kill test. Round-1/2 files are read only.
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

MAX_LEN = 512
EXPECTED = {"stimuli": 200, "explanations": 200, "claims": 671, "s3_edits": 538, "s3_edit_ok": 490}
HEAD_RE = re.compile(r"^\s*=\s*([^=\n]+?)\s*=\s*$", re.M)
AV_TIMING_STIMS = [0, 1, 2]        # pilot set
AR_TIMING_STIMS = list(range(10))  # pilot set

# Stage plan (from PLAN.md) expressed in per-item counts, for the re-budget table.
STAGE_ITEMS = {
    "C1": {"ar": 160 * 4},
    "C2": {"target_short": 80, "av_gen": 80, "ar": 80 * 4 + 40},
    "T1": {"ar": 200 * 2 + 6 + 490 * 3, "target_short": 200 * 32},
    "T2": {"av_fwd": 200 * (4 * 2 + 2 * 2) + 490 * 2},
    "T4": {"target_short": 128, "av_gen": 40 * (2 * 4 + 1), "ar": 40 * 9 * 2},
    "T3": {"av_gen": 40 * 2 * 3 * 2 + 128, "ar": 40 * 12},
}


def token_type(tok_str: str) -> str:
    s = tok_str
    if not re.search(r"[A-Za-z0-9]", s):
        return "punctuation"
    if s.startswith(" ") or s.startswith("\n"):
        return "word_initial"
    return "word_piece"


def check_artifacts() -> dict:
    ov = L.OVERNIGHT
    for name in ["stimuli.csv", "explanations.jsonl", "s2_claims.csv", "s3_edits.jsonl", "s3_scores.csv",
                 "nla_lib.py", "s1_recon.csv", "s5_steer.py"]:
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
    for name, keys in [("acts_L20.npz", {"h20": (200, 3584), "h20_pos2": (200, 3584)}),
                       ("recon_L20.npz", {"pred": (200, 3584), "pred_empty": (3584,)})]:
        p = L.OUT / name
        assert p.exists(), f"missing cache {p}; run overnight/r0_check.py to regenerate"
        z = np.load(p)
        for k, shape in keys.items():
            assert z[k].shape == shape, (name, k, z[k].shape)
        counts[name] = {k: list(z[k].shape) for k in z.files}
    return counts


def topics(stim: pd.DataFrame, ds) -> pd.DataFrame:
    rows = []
    for r in stim.itertuples():
        i = int(r.stim_idx)
        page = ds[int(r.doc_idx)]["page"]
        m = HEAD_RE.search(page)
        rows.append({"stim_idx": i, "doc_idx": int(r.doc_idx), "split": L.split_of(i),
                     "topic_true": m.group(1).strip() if m else "", "heading_found": bool(m),
                     "foreign_stim_idx": (i + 100) % 200})
    df = pd.DataFrame(rows).sort_values("stim_idx").reset_index(drop=True)
    t = dict(zip(df.stim_idx, df.topic_true))
    d = dict(zip(df.stim_idx, df.doc_idx))
    df["topic_foreign"] = [t[j] for j in df.foreign_stim_idx]
    df["foreign_doc_idx"] = [d[j] for j in df.foreign_stim_idx]
    assert (df.doc_idx != df.foreign_doc_idx).all(), "foreign pairing shares a document"
    assert df.heading_found.all(), "heading missing for some stimulus"
    assert (df.topic_true.str.lower() != df.topic_foreign.str.lower()).all(), "identical topic strings in a pair"
    return df


def entropy_pass(stim: pd.DataFrame, ds, timings: dict) -> tuple[pd.DataFrame, list]:
    t0 = time.time()
    tgt = L.Target()
    timings["target_load_s"] = time.time() - t0
    tok = tgt.tok
    rows, errors, per_doc = [], [], []
    for r in stim.itertuples():
        i = int(r.stim_idx); pos = int(r.pos)
        ids = tok(ds[int(r.doc_idx)]["page"], add_special_tokens=False)["input_ids"][:MAX_LEN]
        assert len(ids) == int(r.seq_len) and tok.decode([ids[pos]]) == r.token_str, (i, len(ids), r.seq_len)
        row = {"stim_idx": i, "doc_idx": int(r.doc_idx), "pos": pos, "split": L.split_of(i),
               "token_str": r.token_str, "token_type": token_type(r.token_str), "seq_len": len(ids)}
        try:
            t1 = time.time()
            with torch.inference_mode():
                logits = tgt.model(torch.tensor([ids]).to(L.DEVICE), use_cache=False).logits[0, pos]
            per_doc.append(time.time() - t1)
            lp = torch.log_softmax(logits.float(), dim=-1).cpu()
            p = lp.exp()
            ent = float(-(p * lp).sum())
            top = torch.topk(lp, 5)
            top1 = int(top.indices[0])
            nxt = ids[pos + 1] if pos + 1 < len(ids) else None
            row.update({"entropy_nats": ent, "top1_prob": float(p[top1]), "top1_id": top1,
                        "top1_str": tok.decode([top1]),
                        "top5_str": json.dumps([tok.decode([int(j)]) for j in top.indices], ensure_ascii=False),
                        "top5_prob": json.dumps([round(float(p[int(j)]), 5) for j in top.indices]),
                        "next_actual_id": nxt, "next_actual_str": tok.decode([nxt]) if nxt is not None else "",
                        "next_actual_prob": float(p[nxt]) if nxt is not None else np.nan,
                        "next_actual_rank": int((lp > lp[nxt]).sum()) + 1 if nxt is not None else -1,
                        "top1_matches_actual": bool(nxt is not None and top1 == nxt), "error": ""})
        except Exception:
            row.update({"error": traceback.format_exc()})
            errors.append(row)
            L.log(f"TARGET entropy FAILED on {i}")
        rows.append(row)
        if i % 50 == 0:
            L.log(f"entropy {i}/200 pos={pos} ent={row.get('entropy_nats', float('nan')):.3f} top1={row.get('top1_str')!r}")
    timings["target_fwd_s_per_doc"] = float(np.mean(per_doc)) if per_doc else float("nan")
    timings["target_fwd_s_per_doc_median"] = float(np.median(per_doc)) if per_doc else float("nan")
    # short-context forward cost (for RepE / C2 budgeting): 32 short sentences
    short = ["The weather is cold today and the streets are quiet."] * 32
    t1 = time.time()
    with torch.inference_mode():
        for s in short:
            tgt.model(tok(s, return_tensors="pt", add_special_tokens=False)["input_ids"].to(L.DEVICE), use_cache=False)
    timings["target_fwd_s_per_short"] = (time.time() - t1) / len(short)
    tgt.free()
    timings["rss_after_target_free_G"] = L.rss_mb() / 1024
    return pd.DataFrame(rows), errors


def av_timing(expl: dict, acts, timings: dict) -> list:
    t0 = time.time()
    av = L.AV()
    timings["av_load_s"] = time.time() - t0
    out = []
    for i in AV_TIMING_STIMS:
        r = av.verbalize(torch.from_numpy(acts["h20"][i]))
        out.append({"stim_idx": i, "gen_s": r["gen_s"], "n_tokens": r["n_tokens"], "parse_ok": r["parse_ok"],
                    "cjk": r["cjk"], "explanation": r["explanation"],
                    "same_as_round1": r["explanation"] == expl[i]["explanation"]})
        L.log(f"AV timing stim {i}: {r['gen_s']:.1f}s {r['n_tokens']} tok parse_ok={r['parse_ok']} same_as_round1={out[-1]['same_as_round1']}")
    timings["av_gen_s_per_expl"] = float(np.mean([o["gen_s"] for o in out]))
    timings["av_gen_s_per_token"] = float(sum(o["gen_s"] for o in out) / max(1, sum(o["n_tokens"] for o in out)))
    # forward-only cost (T2 budgeting): one forward of the default prompt + 20-token prefill
    ids, p, base = av.prompt(None)
    t1 = time.time()
    with torch.inference_mode():
        for _ in range(10):
            av.model(inputs_embeds=base, use_cache=False)
    timings["av_fwd_s_per_prompt"] = (time.time() - t1) / 10
    av.free()
    timings["rss_after_av_free_G"] = L.rss_mb() / 1024
    return out


def ar_timing(expl: dict, acts, timings: dict) -> list:
    t0 = time.time()
    ar = L.AR()
    timings["ar_load_s"] = time.time() - t0
    out = []
    t1 = time.time()
    for i in AR_TIMING_STIMS:
        pred = ar.predict(expl[i]["explanation"])
        out.append({"stim_idx": i, "cos_own": L.cos(pred, acts["h20"][i])})
    timings["ar_s_per_score"] = (time.time() - t1) / len(AR_TIMING_STIMS)
    t1 = time.time()
    for _ in range(10):
        ar.predict("This text is about Hoover Dam.")
    timings["ar_s_per_short_score"] = (time.time() - t1) / 10
    ar.free()
    return out


def rebudget(timings: dict) -> list[str]:
    unit = {"ar": timings.get("ar_s_per_score", np.nan), "av_gen": timings.get("av_gen_s_per_expl", np.nan),
            "av_fwd": timings.get("av_fwd_s_per_prompt", np.nan), "target_short": timings.get("target_fwd_s_per_short", np.nan)}
    load = {"ar": timings.get("ar_load_s", 0), "av_gen": timings.get("av_load_s", 0), "av_fwd": timings.get("av_load_s", 0),
            "target_short": timings.get("target_load_s", 0)}
    lines = ["| stage | items | est. compute (min) | + model loads (min) | PLAN estimate |", "|---|---|---|---|---|"]
    plan_est = {"C1": 10, "C2": 40, "T1": 10, "T2": 15, "T4": 30, "T3": 45}
    total = 0.0
    for st, items in STAGE_ITEMS.items():
        secs = sum(n * unit[k] for k, n in items.items())
        loads = sum(load[k] for k in items) + 30 * len(items)
        total += secs + loads
        desc = ", ".join(f"{n} {k}" for k, n in items.items())
        lines.append(f"| {st} | {desc} | {secs / 60:.1f} | {(secs + loads) / 60:.1f} | ~{plan_est[st]} |")
    lines.append(f"| total | | | {total / 60:.0f} | |")
    return lines


def main():
    S = L.Settings("t0", max_len=MAX_LEN, expected_counts=EXPECTED, evaluation_set="stimuli 40-199",
                   heading_regex=HEAD_RE.pattern, foreign_rule="(stim_idx + 100) mod 200",
                   av_timing_stims=AV_TIMING_STIMS, ar_timing_stims=AR_TIMING_STIMS, av_max_new_tokens=200,
                   dataset={"repo": "EleutherAI/wikitext_document_level", "config": "wikitext-2-raw-v1", "split": "train"})
    timings = {}
    counts = check_artifacts()
    S.update(artifact_counts=counts)
    L.log(f"artifact counts OK: {counts}")
    from datasets import load_dataset
    ds = load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]
    stim = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    expl = {}
    for line in (L.OVERNIGHT / "explanations.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line); expl[r["stim_idx"]] = r
    acts = np.load(L.OUT / "acts_L20.npz")

    top = topics(stim, ds)
    top.to_csv(L.OVERNIGHT / "t0_topics.csv", index=False)
    L.log(f"t0_topics.csv written: {len(top)} rows; {top.topic_true.nunique()} unique topics")

    ent, errors = entropy_pass(stim, ds, timings)
    ent.to_csv(L.OVERNIGHT / "t0_entropy.csv", index=False)
    av_rows = av_timing(expl, acts, timings)
    ar_rows = ar_timing(expl, acts, timings)

    ok = ent[ent.error == ""]
    ev = ok[ok.split == "eval"]
    # topic-in-explanation split (used by T2): case-insensitive substring of the default explanation
    topic_in = [(t.lower() in (expl[i]["explanation"] or "").lower()) for i, t in zip(top.stim_idx, top.topic_true)]
    top["topic_in_default_explanation"] = topic_in
    top.to_csv(L.OVERNIGHT / "t0_topics.csv", index=False)

    lines = ["# T0 check — artifacts, topics, entropy sidecar, measured costs", "",
             f"git {L.git_hash()[:8]}; settings in t0_settings.json", "",
             "## Artifact counts (expected / found)", ""]
    for k, v in EXPECTED.items():
        lines.append(f"- {k}: expected {v}, found {counts[k]}")
    lines += [f"- out/acts_L20.npz: {counts['acts_L20.npz']}", f"- out/recon_L20.npz: {counts['recon_L20.npz']}", "",
              "## Topics (t0_topics.csv)", "",
              f"- headings found: {int(top.heading_found.sum())}/200; unique topic_true: {top.topic_true.nunique()}",
              f"- foreign pairing (i+100) mod 200: document collisions 0 (asserted)",
              f"- topic_true appears (case-insensitive) in the default explanation: all {int(sum(topic_in))}/200; "
              f"eval {int(sum(t for t, s in zip(topic_in, top.split) if s == 'eval'))}/160",
              f"- topic_true word count: mean {top.topic_true.str.split().str.len().mean():.2f}, max {top.topic_true.str.split().str.len().max()}",
              "", "## Entropy at pos (t0_entropy.csv; TARGET logits at pos, nats)", "",
              f"- rows OK: {len(ok)}/200; errors: {len(errors)}",
              f"- entropy all: mean {ok.entropy_nats.mean():.3f} median {ok.entropy_nats.median():.3f} "
              f"min {ok.entropy_nats.min():.3f} max {ok.entropy_nats.max():.3f}",
              f"- entropy eval: mean {ev.entropy_nats.mean():.3f} median {ev.entropy_nats.median():.3f}",
              f"- top1_prob eval: mean {ev.top1_prob.mean():.3f} median {ev.top1_prob.median():.3f}",
              f"- top-1 matches actual next token: all {int(ok.top1_matches_actual.sum())}/{len(ok)}; eval {int(ev.top1_matches_actual.sum())}/{len(ev)}",
              "", "| token_type | n (eval) | mean entropy | median entropy | mean top1_prob |", "|---|---|---|---|---|"]
    for tt, g in ev.groupby("token_type"):
        lines.append(f"| {tt} | {len(g)} | {g.entropy_nats.mean():.3f} | {g.entropy_nats.median():.3f} | {g.top1_prob.mean():.3f} |")
    lines += ["", "## Measured per-item costs", ""]
    for k, v in timings.items():
        lines.append(f"- {k}: {v:.3f}" if isinstance(v, float) else f"- {k}: {v}")
    lines += ["", "AV timing generations (pilot stimuli; same_as_round1 = greedy text identical to explanations.jsonl):", ""]
    for o in av_rows:
        lines.append(f"- stim {o['stim_idx']}: {o['gen_s']:.1f} s, {o['n_tokens']} tokens, parse_ok={o['parse_ok']}, same_as_round1={o['same_as_round1']}")
    lines += ["", f"AR timing: mean cos_own on pilot 0-9 = {np.mean([o['cos_own'] for o in ar_rows]):.4f} "
              f"(round-1 s1_recon: {pd.read_csv(L.OVERNIGHT / 's1_recon.csv').cos_own.iloc[:10].mean():.4f})", "",
              "## Re-budget from measured costs (item counts from PLAN.md stage specs)", ""]
    lines += rebudget(timings)
    lines += ["", "Ten fixed rows (eval 0,16,...,144 = stim 40,56,...,184):", "",
              "| stim | token | type | entropy | top1_prob | top1 | actual next | topic_true | topic_foreign |", "|---|---|---|---|---|---|---|---|---|"]
    for i in range(40, 200, 16):
        e = ent[ent.stim_idx == i].iloc[0]; t = top[top.stim_idx == i].iloc[0]
        lines.append(f"| {i} | {e.token_str!r} | {e.token_type} | {e.get('entropy_nats', float('nan')):.3f} | {e.get('top1_prob', float('nan')):.3f} | "
                     f"{e.get('top1_str', '')!r} | {e.get('next_actual_str', '')!r} | {t.topic_true} | {t.topic_foreign} |")
    lines.append("")
    (L.OVERNIGHT / "t0_check.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, entropy_errors=errors, av_timing=av_rows, ar_timing=ar_rows,
             n_topic_in_default_explanation=int(sum(topic_in)))
    L.log("T0 done")


if __name__ == "__main__":
    main()

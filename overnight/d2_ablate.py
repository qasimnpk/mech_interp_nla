"""D2 — claim-direction ablation on the 8 annotated round-5 7B explanations (PLAN.md "Round 5b stage D2"; AR → AV+AR; greedy; γ = 0.3).

  uv run python overnight/d2_ablate.py       # re-entrant; saved generations (d2_av.jsonl) are never regenerated

Direction / ablation / persistence code copied from d1_ablate.py (which is not edited). Sentences come from r4_lib.split_claims_quote_aware.
Arms: own (d̂ of the row's own sentence), random (d̂ of a sentence from a different explanation in the same stratum; fixed derangement,
seed 8101), same (d̂ of a different sentence of the same explanation). Atomic claims (p2_claims_annotated.csv, with truth labels) are mapped
to sentences by token overlap so that persistence can be tabulated by arm × truth × type. Numbers only.
Outputs d2_claim_map.csv, d2_rows.csv, d2_av.jsonl, d2_summary.md, d2_settings.json, d2_progress.json, out/d2_vectors.npz.
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import r4_lib as R  # noqa: E402
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

STAGE, PFX = "D2", "d2"
ARMS = ("own", "random", "same")
ALPHA = 0.3
MIN_ROWS = 60
CAP_MIN = 60
DERANGEMENT_SEED = 8101
VEC = L.OUT / "d2_vectors.npz"
F = {k: L.OVERNIGHT / f"{PFX}_{k}" for k in ["rows.csv", "av.jsonl", "summary.md", "claim_map.csv", "atomic.csv"]}
PUNCT = ".,;:!?\"'()[]"  # k1_kway.PUNCT (copied; k1_kway is not imported to avoid its load-time side effects)
QUOTE_RE = re.compile(r"[\"“”]([^\"“”]{1,80})[\"“”]")
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
STOP = set("""with that this from into than then they them their there these those what when where which while will would could should have been
being were also such some more most very each about after before over under only other same both does just like much many onto upon here
because although through between during without within among again against whose whom itself your ours yours himself herself themselves
cannot shall might must having doing done until unless whether either neither since still even ever every it's don't isn't aren't wasn't
weren't hasn't haven't didn't doesn't won't can't than""".split())
TRUTHS = ("true", "false", "unsupported")
TYPES = ("entity", "detail", "theme", "forecast")


# ----------------------------------------------------------------------------- copied from d1_ablate.py
def toks(s: str) -> set[str]:
    return {w.strip(PUNCT).lower() for w in (s or "").split() if w.strip(PUNCT)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


def quoted_token_ok(text: str, token_str: str) -> bool:
    return any(m.group(1).strip() == token_str.strip() for m in QUOTE_RE.finditer(text or ""))


# ----------------------------------------------------------------------------- D2-specific measures
def content_words(claim_text: str) -> list[str]:
    """Lower-cased word tokens of claim_text (quoted words included), non-stopword, ≥ 4 chars; order preserved, de-duplicated."""
    out = []
    for w in WORD_RE.findall((claim_text or "").lower()):
        w = w.strip("'-")
        if len(w) >= 4 and w not in STOP and w not in out:
            out.append(w)
    return out


def word_in(word: str, text: str) -> bool:
    return bool(re.search(r"(?<![\w])" + re.escape(word) + r"(?![\w])", text or "", re.I))


def persist_atomic(claim_text: str, new_expl: str) -> float:
    cw = content_words(claim_text)
    if not cw:
        return float("nan")
    return float(all(word_in(w, new_expl) for w in cw))


def build_rows(expl: dict[int, str]) -> pd.DataFrame:
    """One row per sentence of every explanation; stratum last / non-last; same-explanation partner; random derangement partner."""
    recs = []
    for i in sorted(expl):
        sents = R.split_claims_quote_aware(expl[i]); k = len(sents)
        for j, s in enumerate(sents, 1):
            a, b, dup = R.sentence_span(expl[i], s)
            recs.append({"row": 10 * i + j, "idx": i, "sentence_no": j, "k": k, "is_last": j == k, "stratum": "positive_control_last" if j == k else "non-last",
                         "sentence": s, "span_a": a, "span_b": b, "span_dup": dup, "n_words": len(s.split())})
    df = pd.DataFrame(recs)
    # same-explanation partner: for non-last rows the next non-last sentence cyclically (== the other non-last sentence when k = 3);
    # for the last row the preceding sentence (k − 1); k = 2 explanations have no other non-last sentence for non-last rows → skipped
    df["same_row"] = -1
    for i in sorted(expl):
        sub = df[df.idx == i]; nl = sub[~sub.is_last].sentence_no.tolist(); k = int(sub.k.iloc[0])
        for r in sub.itertuples():
            if r.is_last:
                df.loc[r.Index, "same_row"] = 10 * i + (k - 1) if k >= 2 else -1
            elif len(nl) >= 2:
                df.loc[r.Index, "same_row"] = 10 * i + nl[(nl.index(r.sentence_no) + 1) % len(nl)]
    # random partner: fixed derangement within stratum, different explanation (seed 8101)
    rng = np.random.default_rng(DERANGEMENT_SEED)
    df["random_row"] = -1
    for name in ("non-last", "positive_control_last"):
        idx = df.index[df.stratum == name].tolist(); stims = df.loc[idx, "idx"].values
        for _ in range(100000):
            perm = rng.permutation(len(idx))
            if all(perm[q] != q and stims[perm[q]] != stims[q] for q in range(len(idx))):
                break
        else:
            raise RuntimeError(f"no derangement for {name}")
        for q in range(len(idx)):
            df.loc[idx[q], "random_row"] = int(df.loc[idx[perm[q]], "row"])
    # processing order: round-robin non-last / last so a cap leaves both strata partially covered
    order, lists = [], {n: df.index[df.stratum == n].tolist() for n in ("non-last", "positive_control_last")}
    while any(lists.values()):
        for n in lists:
            if lists[n]:
                order.append(lists[n].pop(0))
    df = df.loc[order].reset_index(drop=True); df["process_order"] = range(len(df))
    return df


def claim_map(df: pd.DataFrame, claims: pd.DataFrame) -> pd.DataFrame:
    """Each P2 claim → the sentence of its explanation with the largest token overlap (ties → lowest sentence_no); overlap 0 → unmapped."""
    out = []
    for c in claims.itertuples():
        i = int(c.idx); ct = toks(str(c.claim_text)) | set().union(*[toks(m.group(1)) for m in QUOTE_RE.finditer(str(c.claim_text))]) if QUOTE_RE.search(str(c.claim_text)) else toks(str(c.claim_text))
        sub = df[df.idx == i].sort_values("sentence_no")
        ov = [(len(ct & toks(r.sentence)), int(r.sentence_no), int(r.row)) for r in sub.itertuples()]
        best = max(o[0] for o in ov); cands = [o for o in ov if o[0] == best]
        tie = len(cands) > 1 and best > 0
        sn, row = (cands[0][1], cands[0][2]) if best > 0 else (-1, -1)
        out.append({"idx": i, "claim_no": int(c.claim_no), "sentence_no": sn, "row": row, "overlap": best, "tie": tie, "mapped": best > 0, "type": c.type, "truth": c.truth,
                    "claim_text": c.claim_text, "content_words": " ".join(content_words(str(c.claim_text))), "n_content_words": len(content_words(str(c.claim_text)))})
    return pd.DataFrame(out)


def cell(values, clusters, d=3) -> str:
    v = np.asarray(list(values), dtype=float); m = ~np.isnan(v)
    if m.sum() == 0:
        return "n=0"
    c = R.ci(v[m], np.asarray(list(clusters))[m])
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}] n={c['n']} k={c['n_clusters']}"


def main():
    prog = R.Progress(PFX)
    S = L.Settings(PFX, arms=list(ARMS), alpha=ALPHA, min_rows=MIN_ROWS, cap_min=CAP_MIN, derangement_seed=DERANGEMENT_SEED, decoding="greedy 200 tokens",
                   sentences="r4_lib.split_claims_quote_aware(explanation_7b); last sentence = positive_control_last, others non-last",
                   direction="d_s = AR(z) − AR(z\\s) raw fp32, z\\s = ' '.join(sentences without s) (D1 span logic); h' = h − 0.3‖h‖ d̂",
                   arms_detail="own: d̂ of the row's sentence; random: d̂ of the derangement partner (same stratum, different explanation, seed 8101); same: d̂ of a different sentence of the same explanation (non-last rows: next non-last sentence cyclically = the other non-last sentence when k = 3; last rows: sentence k − 1; k = 2 explanations: skipped for non-last rows)",
                   claim_map="each P2 claim → sentence with the largest overlap of distinct lower-cased tokens (PUNCT-stripped; quoted phrases' tokens included); ties → lowest sentence_no (tie flagged); overlap 0 → unmapped (excluded from by-truth tables)",
                   measures="persist_claim (max token-Jaccard between the sentence and any quote-aware-split sentence of the new explanation; D1 definition); persist_atomic (1 if every content word of claim_text — lower-cased, non-stopword, ≥ 4 chars, quoted words included — occurs whole-word case-insensitively in the new explanation; NaN if the claim has no content word); format_break = parse fail or CJK; cos_new = cos(AR(new explanation), h); jaccard_expl (token Jaccard original vs new explanation); quoted_token_ok (positive control: the original last token quoted verbatim); reference = the P1 explanation of the unablated h",
                   stopwords=sorted(STOP), bootstrap="cluster by explanation (idx), 1000 draws, seed 0",
                   kill="mean[persist_claim(random) − persist_claim(own)] on non-last rows; MET if CI ≤ 0, NOT MET if CI > 0, INCONCLUSIVE if straddles or rows < 60")
    hits = R.assert_no_av_model_calls([L.OVERNIGHT / "d2_ablate.py", L.OVERNIGHT / "r4_lib.py"]); assert not hits, hits
    p1 = {int(r["idx"]): r for r in R.read_jsonl(L.OVERNIGHT / "p1_av.jsonl")}
    expl = {i: p1[i]["explanation_7b"] for i in p1}
    tokens = {int(t["idx"]): t["last_token_str"] for t in json.loads((L.OVERNIGHT / "p0_tokens.json").read_text())}
    z0 = np.load(L.OUT / "p0_acts.npz"); h20 = z0["h20"]; assert z0["idx"].tolist() == sorted(expl), z0["idx"]
    claims = pd.read_csv(L.OVERNIGHT / "p2_claims_annotated.csv", keep_default_na=False)
    df = build_rows(expl)
    assert all(a >= 0 and not dup for a, dup in zip(df.span_a, df.span_dup)), "sentence span not found or duplicated"
    cm = claim_map(df, claims); cm.to_csv(F["claim_map.csv"], index=False)
    L.log(f"D2: {len(df)} sentence rows ({int((~df.is_last).sum())} non-last, {int(df.is_last.sum())} last); claims mapped {int(cm.mapped.sum())}/{len(cm)} (ties {int(cm.tie.sum())}); same-arm skipped rows {int((df.same_row < 0).sum())}")
    # ---------------- AR phase: directions
    if VEC.exists():
        z = np.load(VEC); D = {int(r): z["d_hat"][q] for q, r in enumerate(z["rows"])}; meta = json.loads(str(z["meta"]))
    else:
        prog.set_phase("ar_directions")
        ar = L.AR(); pz = {}; D = {}; meta = {}
        for r in df.sort_values("row").itertuples():
            i = int(r.idx); E = expl[i]; sents = R.split_claims_quote_aware(E); ci = int(r.sentence_no) - 1
            assert ci < len(sents) and sents[ci] == str(r.sentence), (r.row, ci, len(sents))
            if i not in pz:
                pz[i] = ar.predict(E).numpy()
            zc = " ".join(sents[:ci] + sents[ci + 1:])
            pzc = ar.predict(zc).numpy()
            d = (pz[i] - pzc).astype(np.float32); nd = float(np.linalg.norm(d)); dh = d / max(nd, 1e-12)
            h = h20[i]; nh = float(np.linalg.norm(h))
            D[int(r.row)] = dh
            meta[str(int(r.row))] = {"d_norm": nd, "cos_dhat_hhat": float(dh @ h / nh), "proj": float(h @ dh / nh), "h_norm": nh, "cos_z": L.cos(pz[i], h), "cos_zc": L.cos(pzc, h), "z_minus_s": zc}
        ar.free()
        rows = np.array(sorted(D)); np.savez(VEC, rows=rows, d_hat=np.stack([D[int(r)] for r in rows]), meta=json.dumps(meta))
        prog.completed("directions", len(D))
        L.log(f"D2 directions: {len(D)} rows")
    # ---------------- AV+AR phase (re-entrant; d2_av.jsonl is the checkpoint)
    def arms_of(r):
        return [a for a in ARMS if not (a == "same" and int(r.same_row) < 0)]

    def partner(r, arm):
        return int(r.row) if arm == "own" else int(r.random_row) if arm == "random" else int(r.same_row)

    done = {}
    for g in R.read_jsonl(F["av.jsonl"]):
        if g.get("explanation") is not None:
            done[(int(g["row"]), g["arm"])] = g
    prog.set_phase("av_ar")
    av = ar = None
    n_gen = 0; t0 = time.time(); capped = False
    for r in df.itertuples():
        row = int(r.row); i = int(r.idx); h = h20[i]; nh = float(np.linalg.norm(h))
        need = [a for a in arms_of(r) if (row, a) not in done]
        if not need:
            continue
        if prog.minutes >= CAP_MIN or prog.over_failures():
            capped = True
            prog.incomplete("rows", [int(x.row) for x in df.itertuples() if any((int(x.row), a) not in done for a in arms_of(x))]); break
        if av is None:
            av = L.AV(); ar = L.AR()
        for arm in need:
            dh = D[partner(r, arm)]
            hp = (h - ALPHA * nh * dh).astype(np.float32)
            rec = {"row": row, "idx": i, "sentence_no": int(r.sentence_no), "stratum": r.stratum, "arm": arm, "partner_row": partner(r, arm), "cos_hprime_h": L.cos(hp, h), "hprime_norm": float(np.linalg.norm(hp))}
            try:
                rec.update(R.verbalize_greedy(av, torch.from_numpy(hp)))
                rec["cos_new"] = L.cos(ar.predict(rec["explanation"]).numpy(), h); n_gen += 1
            except Exception:
                rec.update({"error": traceback.format_exc(), "explanation": None, "parse_ok": False}); prog.fail(f"row {row} {arm}: {rec['error'][-200:]}")
            R.append_jsonl(F["av.jsonl"], rec)
            if rec.get("explanation") is not None:
                done[(row, arm)] = rec
        nrows = sum(1 for x in df.itertuples() if all((int(x.row), a) in done for a in arms_of(x)))
        prog.completed("rows", nrows)
        L.log(f"D2: {nrows}/{len(df)} rows complete, {(time.time()-t0)/max(1, n_gen):.1f} s/generation, {prog.minutes:.1f} min")
    if av is not None:
        av.free(); ar.free()
    # ---------------- measures
    rows = []
    for r in df.itertuples():
        row = int(r.row); i = int(r.idx); E = expl[i]; sent = str(r.sentence); m = meta[str(row)]
        rec = {"row": row, "idx": i, "sentence_no": int(r.sentence_no), "k": int(r.k), "stratum": r.stratum, "is_last": bool(r.is_last), "sentence": sent, "random_row": int(r.random_row), "same_row": int(r.same_row),
               "d_norm": m["d_norm"], "cos_dhat_hhat": m["cos_dhat_hhat"], "proj": m["proj"], "cos_z": m["cos_z"], "cos_zc": m["cos_zc"],
               "n_atomic_mapped": int(((cm.row == row) & cm.mapped).sum()), "ref_quoted_token_ok": quoted_token_ok(E, tokens[i]), "complete": all((row, a) in done for a in arms_of(r))}
        for arm in ARMS:
            g = done.get((row, arm))
            if g is None:
                for k in ["persist_claim", "jaccard_expl", "parse_ok", "cjk", "format_break", "cos_new", "cos_hprime_h", "quoted_token_ok", "n_tokens", "n_atomic_true_persist", "n_atomic_false_persist", "n_atomic_unsupported_persist"]:
                    rec[f"{arm}_{k}"] = np.nan
                rec[f"{arm}_skipped"] = arm == "same" and int(r.same_row) < 0
                continue
            new = g["explanation"] or ""
            sents = R.split_claims_quote_aware(new); ct = toks(sent)
            rec[f"{arm}_persist_claim"] = max([jaccard(ct, toks(s)) for s in sents], default=0.0)
            rec[f"{arm}_jaccard_expl"] = jaccard(toks(E), toks(new))
            rec[f"{arm}_parse_ok"] = float(bool(g.get("parse_ok"))); rec[f"{arm}_cjk"] = float(bool(g.get("cjk"))); rec[f"{arm}_format_break"] = float((not g.get("parse_ok")) or bool(g.get("cjk")))
            rec[f"{arm}_cos_new"] = g.get("cos_new", np.nan); rec[f"{arm}_cos_hprime_h"] = g["cos_hprime_h"]; rec[f"{arm}_quoted_token_ok"] = float(quoted_token_ok(new, tokens[i])); rec[f"{arm}_n_tokens"] = g.get("n_tokens")
            rec[f"{arm}_skipped"] = False
            for t in TRUTHS:
                sub = cm[(cm.row == row) & cm.mapped & (cm.truth == t)]
                vals = [persist_atomic(str(c.claim_text), new) for c in sub.itertuples()]
                rec[f"{arm}_n_atomic_{t}_persist"] = int(np.nansum(vals)) if vals else 0
                rec[f"{arm}_n_atomic_{t}"] = int(sum(1 for v in vals if not np.isnan(v)))
        rows.append(rec)
    df2 = pd.DataFrame(rows); df2.to_csv(F["rows.csv"], index=False)
    # atomic-claim-level table (unit = mapped P2 claim × arm)
    at = []
    for c in cm[cm.mapped].itertuples():
        row = int(c.row); r = df2[df2.row == row].iloc[0]
        ref = persist_atomic(str(c.claim_text), expl[int(c.idx)])
        for arm in ARMS:
            g = done.get((row, arm))
            at.append({"idx": int(c.idx), "claim_no": int(c.claim_no), "row": row, "sentence_no": int(c.sentence_no), "stratum": r.stratum, "is_last": bool(r.is_last), "type": c.type, "truth": c.truth, "arm": arm,
                       "n_content_words": int(c.n_content_words), "ref_persist_atomic": ref, "persist_atomic": persist_atomic(str(c.claim_text), g["explanation"] or "") if g is not None else np.nan, "generated": g is not None})
    at = pd.DataFrame(at); at.to_csv(F["atomic.csv"], index=False)
    # ---------------- kill statistic (first)
    ok = df2[df2.complete == True].copy()
    ok_or = df2[df2.own_persist_claim.notna() & df2.random_persist_claim.notna()].copy()  # own + random present (same may be skipped)
    for k in ["persist_claim", "jaccard_expl", "format_break", "quoted_token_ok", "cos_new"]:
        ok_or[f"diff_rand_{k}"] = ok_or[f"random_{k}"] - ok_or[f"own_{k}"]
        ok_or[f"diff_same_{k}"] = ok_or[f"same_{k}"] - ok_or[f"own_{k}"]
    nl = ok_or[~ok_or.is_last]; last = ok_or[ok_or.is_last]
    ci = L.cluster_bootstrap_mean(nl.diff_rand_persist_claim, nl.idx) if len(nl) else {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
    out = L.outcome_ci_at_or_below(ci, 0.0, min_n=MIN_ROWS)

    def strat(s, name):
        if not len(s):
            return f"{name}: n=0"
        return (f"{name}: n={len(s)} persist_claim own {s.own_persist_claim.mean():.3f} random {s.random_persist_claim.mean():.3f} same {s.same_persist_claim.mean():.3f} (same n={int(s.same_persist_claim.notna().sum())}); "
                f"random − own {R.fmt_ci(R.ci(s.diff_rand_persist_claim, s.idx), 4)}; same − own {cell(s.diff_same_persist_claim, s.idx, 4)}; "
                f"format-break own {s.own_format_break.mean():.3f} random {s.random_format_break.mean():.3f} same {s.same_format_break.mean():.3f}; cos_new own {s.own_cos_new.mean():.4f} random {s.random_cos_new.mean():.4f} same {s.same_cos_new.mean():.4f}")
    atn = at[(~at.is_last) & at.generated & at.persist_atomic.notna()]
    atomic_txt = "; ".join(f"persist_atomic {arm} true {atn[(atn.arm == arm) & (atn.truth == 'true')].persist_atomic.mean():.3f} (n={int(((atn.arm == arm) & (atn.truth == 'true')).sum())}) false {atn[(atn.arm == arm) & (atn.truth == 'false')].persist_atomic.mean():.3f} (n={int(((atn.arm == arm) & (atn.truth == 'false')).sum())}) unsupported {atn[(atn.arm == arm) & (atn.truth == 'unsupported')].persist_atomic.mean():.3f} (n={int(((atn.arm == arm) & (atn.truth == 'unsupported')).sum())})" for arm in ARMS)
    obs = (strat(nl, "non-last pooled") + "; " + strat(last, "positive_control_last") + f"; positive control quoted_token_ok own {last.own_quoted_token_ok.mean() if len(last) else float('nan'):.3f} random {last.random_quoted_token_ok.mean() if len(last) else float('nan'):.3f} same {last.same_quoted_token_ok.mean() if len(last) else float('nan'):.3f} reference {df2[df2.is_last].ref_quoted_token_ok.mean():.3f}; "
           + atomic_txt + f"; claims mapped {int(cm.mapped.sum())}/{len(cm)}; rows completed {len(ok)}/{len(df)} (own+random {len(ok_or)}); same-arm skipped rows {int((df.same_row < 0).sum())}")
    kill = L.append_disconfirmation("D2", "D2", "CI95 (cluster by explanation) of [persist_claim(random) − persist_claim(own)] on non-last rows ≤ 0 → MET; > 0 → NOT MET; straddles or < 60 rows → INCONCLUSIVE (n ≈ 17 by design → INCONCLUSIVE by n expected)", obs, out,
                                    "descriptive; concerns the AV's output under a vector edit only; n = 8 explanations by design")
    # ---------------- summary
    lines = ["# D2 summary — claim-direction ablation on the 8 annotated 7B explanations (greedy, γ = 0.3; arms own / random / same-explanation)", "",
             f"git {L.git_hash()[:8]}; settings in d2_settings.json; progress in d2_progress.json; rows in d2_rows.csv; atomic-claim rows in d2_atomic.csv; claim map in d2_claim_map.csv; generations in d2_av.jsonl", "",
             "## Kill test (logged to DISCONFIRMATION.md first)", "", f"- {kill}", "",
             "## Counts", "",
             f"- sentence rows {len(df)} (non-last {int((~df.is_last).sum())}, last {int(df.is_last.sum())}); k per explanation {json.dumps({int(i): int(df[df.idx == i].k.iloc[0]) for i in sorted(expl)})}; rows completed (all arms) {len(ok)}; own+random present {len(ok_or)}; same-arm skipped rows {int((df.same_row < 0).sum())}; generations {sum(1 for _ in done)}; failures {prog.d['failures']}; capped {capped}",
             f"- P2 claims {len(cm)}; mapped {int(cm.mapped.sum())}; unmapped (overlap 0) {int((~cm.mapped).sum())}; ties (resolved to lowest sentence_no) {int(cm.tie.sum())}; mapped to non-last {int((cm.mapped & (cm.sentence_no < cm.idx.map(lambda i: int(df[df.idx == i].k.iloc[0])))).sum())}; claims with no content word {int((cm.n_content_words == 0).sum())}",
             f"- mapped claims per sentence_no: {json.dumps({int(k): int(v) for k, v in cm[cm.mapped].sentence_no.value_counts().sort_index().items()})}",
             f"- reference persist_atomic (claim content words all present in the ORIGINAL explanation): {at[at.arm == 'own'].ref_persist_atomic.mean():.3f} (n={int(at[at.arm == 'own'].ref_persist_atomic.notna().sum())}); reference quoted_token_ok on last rows {df2[df2.is_last].ref_quoted_token_ok.mean():.3f}",
             "", "## Table 1 — persist_claim by arm × stratum (mean [cluster-bootstrap CI95] n=rows k=explanations)", "",
             "| stratum | own | random | same | random − own | same − own |", "|---|---|---|---|---|---|"]
    for name, s in [("non-last", nl), ("positive_control_last", last), ("all", ok_or)]:
        lines.append(f"| {name} | {cell(s.own_persist_claim, s.idx)} | {cell(s.random_persist_claim, s.idx)} | {cell(s.same_persist_claim, s.idx)} | {cell(s.diff_rand_persist_claim, s.idx)} | {cell(s.diff_same_persist_claim, s.idx)} |")
    lines += ["", "## Table 2 — persist_atomic by arm × truth × type, pooled over non-last rows (unit = mapped P2 claim; cluster by explanation)", ""]
    for arm in ARMS:
        a = atn[atn.arm == arm]
        lines += [f"### arm = {arm} (n claims = {len(a)})", "", "| truth \\ type | entity | detail | theme | forecast | all types |", "|---|---|---|---|---|---|"]
        for t in TRUTHS + ("all",):
            s_t = a if t == "all" else a[a.truth == t]
            cells = [cell(s_t[s_t.type == ty].persist_atomic, s_t[s_t.type == ty].idx) for ty in TYPES] + [cell(s_t.persist_atomic, s_t.idx)]
            lines.append(f"| {t} | " + " | ".join(cells) + " |")
        lines.append("")
    lines += ["### paired differences per claim (random − own, same − own), non-last, by truth", "", "| truth | n | random − own | same − own |", "|---|---|---|---|"]
    piv = atn.pivot_table(index=["idx", "claim_no", "type", "truth"], columns="arm", values="persist_atomic").reset_index()
    for t in TRUTHS + ("all",):
        s_t = piv if t == "all" else piv[piv.truth == t]
        dr = (s_t["random"] - s_t["own"]) if "random" in s_t else pd.Series(dtype=float); ds = (s_t["same"] - s_t["own"]) if "same" in s_t else pd.Series(dtype=float)
        lines.append(f"| {t} | {len(s_t)} | {cell(dr, s_t.idx)} | {cell(ds, s_t.idx)} |")
    lines += ["", "### persist_atomic by arm × truth, positive-control (last) rows", "", "| truth | own | random | same |", "|---|---|---|---|"]
    atl = at[at.is_last & at.generated & at.persist_atomic.notna()]
    for t in TRUTHS + ("all",):
        s_t = atl if t == "all" else atl[atl.truth == t]
        lines.append(f"| {t} | " + " | ".join(cell(s_t[s_t.arm == arm].persist_atomic, s_t[s_t.arm == arm].idx) for arm in ARMS) + " |")
    lines += ["", "## Table 3 — format-break rate, cos_new, whole-explanation Jaccard, cos(h', h) by arm (all completed rows)", "", "| measure | own | random | same |", "|---|---|---|---|"]
    for k in ["format_break", "parse_ok", "cjk", "cos_new", "jaccard_expl", "cos_hprime_h", "n_tokens"]:
        lines.append(f"| {k} | " + " | ".join(cell(ok_or[f"{arm}_{k}"], ok_or.idx, 4) for arm in ARMS) + " |")
    lines += ["", "## Table 4 — positive-control stratum (last sentence)", "", "| measure | own | random | same |", "|---|---|---|---|"]
    for k in ["persist_claim", "quoted_token_ok", "cos_new", "jaccard_expl", "format_break"]:
        lines.append(f"| {k} | " + " | ".join(cell(last[f"{arm}_{k}"], last.idx, 4) for arm in ARMS) + " |")
    lines += ["", "## Direction diagnostics", ""] + R.DIST_HEADER
    for c in ["d_norm", "proj", "cos_dhat_hhat", "cos_z", "cos_zc", "own_cos_hprime_h", "random_cos_hprime_h", "same_cos_hprime_h"]:
        for name, s in [("non-last", df2[~df2.is_last]), ("last", df2[df2.is_last])]:
            lines.append(R.dist_row(f"{c} / {name}", s[c]))
    lines += ["", "## Table 5 — per-row listing", "", "| row | idx | sent | stratum | arm | partner | persist_claim | atomic true persisted/n | atomic false persisted/n | atomic unsupported persisted/n | cos_new | format_break |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in df2.sort_values("row").itertuples():
        for arm in ARMS:
            if np.isnan(getattr(r, f"{arm}_persist_claim")):
                lines.append(f"| {r.row} | {r.idx} | {r.sentence_no} | {r.stratum} | {arm} | — | (skipped) | | | | | |" if getattr(r, f"{arm}_skipped") else f"| {r.row} | {r.idx} | {r.sentence_no} | {r.stratum} | {arm} | — | (not generated) | | | | | |")
                continue
            p = r.row if arm == "own" else r.random_row if arm == "random" else r.same_row
            lines.append(f"| {r.row} | {r.idx} | {r.sentence_no} | {r.stratum} | {arm} | {p} | {getattr(r, f'{arm}_persist_claim'):.3f} | {getattr(r, f'{arm}_n_atomic_true_persist')}/{getattr(r, f'{arm}_n_atomic_true')} | {getattr(r, f'{arm}_n_atomic_false_persist')}/{getattr(r, f'{arm}_n_atomic_false')} | {getattr(r, f'{arm}_n_atomic_unsupported_persist')}/{getattr(r, f'{arm}_n_atomic_unsupported')} | {getattr(r, f'{arm}_cos_new'):.4f} | {getattr(r, f'{arm}_format_break'):.0f} |")
    lines += ["", "## Re-verbalizations (verbatim; also in d2_av.jsonl)", ""]
    for i in sorted(expl):
        lines += [f"### idx {i}", "", f"- original (P1): {expl[i]!r}"]
        for r in df2[df2.idx == i].sort_values("row").itertuples():
            for arm in ARMS:
                g = done.get((int(r.row), arm))
                if g is not None:
                    lines.append(f"- row {r.row} sentence {r.sentence_no} arm {arm} (partner {g['partner_row']}, cos(h',h) {g['cos_hprime_h']:.4f}, cos_new {g.get('cos_new', float('nan')):.4f}, persist_claim {getattr(r, f'{arm}_persist_claim'):.3f}): {g['explanation']!r}")
        lines.append("")
    F["summary.md"].write_text("\n".join(lines))
    prog.set_phase("done"); S.finish(progress=prog.d, kill=ci, outcome=out, rows_completed=len(ok), n_rows=len(df), claims_mapped=int(cm.mapped.sum()), capped=capped)
    L.log(f"D2 done: {out}; {len(ok)}/{len(df)} rows; {prog.minutes:.1f} min")


if __name__ == "__main__":
    main()

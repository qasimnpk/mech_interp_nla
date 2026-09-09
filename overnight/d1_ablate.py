"""D1 — claim-direction ablation with the reconstructor as encoder (PLAN.md round 4, desk-designed; AR → AV+AR; greedy; one strength).

  uv run python overnight/d1_ablate.py       # re-entrant; saved generations (d1_av.jsonl) are never regenerated

What D1 measures: changes in the AV's output when 0.3‖h‖ of the reconstructor-attributed claim direction (own) or of another row's
direction (random control, fixed derangement seed 8001) is subtracted from the activation. It says nothing about the target model.
Outputs d1_rows.csv, d1_av.jsonl, d1_summary.md, d1_review_blind.csv / d1_review_key.csv (20 rows), out/d1_vectors.npz.
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
from overnight.k1_kway import load_rows, PUNCT  # noqa: E402  (import-safe: Settings inside main)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

STAGE, PFX = "D1", "d1"
N_STRATA = {"nonlast_in_prefix": 60, "nonlast_not_in_prefix": 60, "positive_control_last": 20}
ALPHA = 0.3
MIN_ROWS = 60
VEC = L.OUT / "d1_vectors.npz"
F = {k: L.OVERNIGHT / f"{PFX}_{k}" for k in ["rows.csv", "av.jsonl", "summary.md", "review_blind.csv", "review_key.csv", "sample.csv"]}
SENT_RE = re.compile(r"(?<=[.!?])\s+")
MARKER_RE = re.compile(r"^\s*(\d+[.)]|[-*•])\s*")
QUOTE_RE = re.compile(r"[\"“”]([^\"“”]{1,80})[\"“”]")


def split_claims_s2(text: str) -> list[str]:
    """S2 rule (copied from s2_deletion.split_claims; that module is not importable without side effects)."""
    out = []
    for line in text.split("\n"):
        for piece in SENT_RE.split(line):
            p = MARKER_RE.sub("", piece.strip()).strip()
            if len(p.split()) >= 3:
                out.append(p)
    return out


def toks(s: str) -> set[str]:
    return {w.strip(PUNCT).lower() for w in (s or "").split() if w.strip(PUNCT)}


def jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if (a | b) else 0.0


def quoted_token_ok(text: str, token_str: str) -> bool:
    return any(m.group(1).strip() == token_str.strip() for m in QUOTE_RE.finditer(text or ""))


def sample_rows(det: pd.DataFrame) -> pd.DataFrame:
    if F["sample.csv"].exists():
        return pd.read_csv(F["sample.csv"], keep_default_na=False)
    rng = np.random.default_rng(8000)
    parts = []
    for name, n in N_STRATA.items():
        s = det[det.stratum == name].sort_values("row")
        pick = sorted(rng.choice(s.row.values, size=min(n, len(s)), replace=False))
        parts.append(s[s.row.isin(pick)].copy())
    df = pd.concat(parts).sort_values(["stratum", "row"]).reset_index(drop=True)
    # fixed derangement within stratum (seed 8001): partner = different row from a different explanation
    rng2 = np.random.default_rng(8001)
    df["partner_row"] = -1
    for name in N_STRATA:
        idx = df.index[df.stratum == name].tolist(); stims = df.loc[idx, "stim_idx"].values
        for _ in range(10000):
            perm = rng2.permutation(len(idx))
            if all(perm[k] != k and stims[perm[k]] != stims[k] for k in range(len(idx))):
                break
        else:
            raise RuntimeError(f"no derangement for {name}")
        for k in range(len(idx)):
            df.loc[idx[k], "partner_row"] = int(df.loc[idx[perm[k]], "row"])
    # processing order: round-robin across strata so a cap leaves every stratum partially covered
    order, lists = [], {n: df.index[df.stratum == n].tolist() for n in N_STRATA}
    while any(lists.values()):
        for n in N_STRATA:
            if lists[n]:
                order.append(lists[n].pop(0))
    df = df.loc[order].reset_index(drop=True); df["process_order"] = range(len(df))
    df.to_csv(F["sample.csv"], index=False)
    return df


def main():
    prog = R.Progress(STAGE)
    S = L.Settings(PFX, strata=N_STRATA, alpha=ALPHA, min_rows=MIN_ROWS, sample_seed=8000, derangement_seed=8001, decoding="greedy 200 tokens",
                   direction="d_c = AR(z) − AR(z\\c) raw fp32, z\\c = explanation with the claim removed (S2 split rule); h' = h − 0.3‖h‖ d̂; random control: d̂ of the derangement partner (same stratum, different explanation)",
                   measures="persist_word (whole-word, case-insensitive core of word_orig in the new explanation); persist_claim (max token-Jaccard between the original claim and any S2-split sentence of the new explanation); jaccard_expl (token Jaccard original vs new explanation); quoted_token_ok (X1b rule) for the positive control; reference = the round-1 greedy explanation",
                   bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")
    hits = R.assert_no_av_model_calls([L.OVERNIGHT / "d1_ablate.py", L.OVERNIGHT / "r4_lib.py"]); assert not hits, hits
    det = load_rows(); df = sample_rows(det)
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    expl = {r["stim_idx"]: r for r in R.read_jsonl(L.OVERNIGHT / "explanations.jsonl")}
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    # ---------------- AR phase: directions
    if VEC.exists():
        z = np.load(VEC); D = {int(r): z["d_hat"][k] for k, r in enumerate(z["rows"])}; meta = json.loads(str(z["meta"]))
    else:
        prog.set_phase("ar_directions")
        ar = L.AR(); pz = {}; D = {}; meta = {}
        for r in df.itertuples():
            i = int(r.stim_idx); E = expl[i]["explanation"]; claims = split_claims_s2(E); ci = int(r.claim_idx)
            assert ci < len(claims) and claims[ci] == str(r.claim), (r.row, ci, len(claims))
            if i not in pz:
                pz[i] = ar.predict(E).numpy()
            zc = " ".join(claims[:ci] + claims[ci + 1:])
            pzc = ar.predict(zc).numpy()
            d = (pz[i] - pzc).astype(np.float32); nd = float(np.linalg.norm(d)); dh = d / max(nd, 1e-12)
            h = h20[i]; nh = float(np.linalg.norm(h))
            D[int(r.row)] = dh
            meta[str(int(r.row))] = {"d_norm": nd, "cos_dhat_hhat": float(dh @ h / nh), "proj": float(h @ dh / nh), "h_norm": nh, "cos_z": L.cos(pz[i], h), "cos_zc": L.cos(pzc, h), "z_minus_c": zc}
        ar.free()
        rows = np.array(sorted(D)); np.savez(VEC, rows=rows, d_hat=np.stack([D[int(r)] for r in rows]), meta=json.dumps(meta))
        prog.completed("directions", len(D))
        L.log(f"D1 directions: {len(D)} rows")
    # ---------------- AV+AR phase
    done = {}
    for g in R.read_jsonl(F["av.jsonl"]):
        if g.get("explanation") is not None:
            done[(int(g["row"]), g["arm"])] = g
    prog.set_phase("av_ar")
    av = ar = None
    n_gen = 0; t0 = time.time()
    for r in df.itertuples():
        row = int(r.row); i = int(r.stim_idx); h = h20[i]; nh = float(np.linalg.norm(h))
        need = [arm for arm in ("own", "random") if (row, arm) not in done]
        if not need:
            continue
        if prog.over_cap() or prog.over_failures():
            prog.incomplete("rows", [int(x.row) for x in df.itertuples() if any((int(x.row), a) not in done for a in ("own", "random"))]); break
        if av is None:
            av = L.AV(); ar = L.AR()
        for arm in need:
            dh = D[row] if arm == "own" else D[int(r.partner_row)]
            hp = (h - ALPHA * nh * dh).astype(np.float32)
            rec = {"row": row, "stim_idx": i, "arm": arm, "partner_row": int(r.partner_row) if arm == "random" else row, "cos_hprime_h": L.cos(hp, h), "hprime_norm": float(np.linalg.norm(hp))}
            try:
                rec.update(R.verbalize_greedy(av, torch.from_numpy(hp)))
                rec["cos_h_AR_new"] = L.cos(ar.predict(rec["explanation"]).numpy(), h); n_gen += 1
            except Exception:
                rec.update({"error": traceback.format_exc(), "explanation": None, "parse_ok": False}); prog.fail(f"row {row} {arm}: {rec['error'][-200:]}")
            R.append_jsonl(F["av.jsonl"], rec)
            if rec.get("explanation") is not None:
                done[(row, arm)] = rec
        nrows = sum(1 for x in df.itertuples() if all((int(x.row), a) in done for a in ("own", "random")))
        prog.completed("rows", nrows)
        if nrows % 10 == 0:
            L.log(f"D1: {nrows}/{len(df)} rows, {(time.time()-t0)/max(1, n_gen):.1f} s/generation")
    if av is not None:
        av.free(); ar.free()
    # ---------------- measures + statistics
    rows = []
    for r in df.itertuples():
        row = int(r.row); i = int(r.stim_idx); E = expl[i]["explanation"]; claim = str(r.claim); core = str(r.core_orig)
        m = meta[str(row)]
        rec = {"row": row, "stim_idx": i, "claim_idx": int(r.claim_idx), "stratum": r.stratum, "is_last": bool(r.is_last), "in_full_prefix": bool(r.in_full_prefix), "slot_type": r.slot_type,
               "word_orig": r.word_orig, "core_orig": core, "claim": claim, "partner_row": int(r.partner_row), "d_norm": m["d_norm"], "cos_dhat_hhat": m["cos_dhat_hhat"], "proj": m["proj"], "cos_z": m["cos_z"], "cos_zc": m["cos_zc"],
               "ref_persist_word": bool(re.search(r"(?<![\w])" + re.escape(core) + r"(?![\w])", E, re.I)), "ref_quoted_token_ok": quoted_token_ok(E, st.token_str[i]), "complete": all((row, a) in done for a in ("own", "random"))}
        for arm in ("own", "random"):
            g = done.get((row, arm))
            if g is None:
                for k in ["persist_word", "persist_claim", "jaccard_expl", "parse_ok", "cjk", "format_break", "cos_h_AR_new", "cos_hprime_h", "quoted_token_ok", "n_tokens"]:
                    rec[f"{arm}_{k}"] = np.nan
                continue
            new = g["explanation"] or ""
            rec[f"{arm}_persist_word"] = float(bool(re.search(r"(?<![\w])" + re.escape(core) + r"(?![\w])", new, re.I)))
            sents = split_claims_s2(new); ct = toks(claim)
            rec[f"{arm}_persist_claim"] = max([jaccard(ct, toks(s)) for s in sents], default=0.0)
            rec[f"{arm}_jaccard_expl"] = jaccard(toks(E), toks(new))
            rec[f"{arm}_parse_ok"] = float(bool(g.get("parse_ok"))); rec[f"{arm}_cjk"] = float(bool(g.get("cjk"))); rec[f"{arm}_format_break"] = float((not g.get("parse_ok")) or bool(g.get("cjk")))
            rec[f"{arm}_cos_h_AR_new"] = g.get("cos_h_AR_new", np.nan); rec[f"{arm}_cos_hprime_h"] = g["cos_hprime_h"]; rec[f"{arm}_quoted_token_ok"] = float(quoted_token_ok(new, st.token_str[i])); rec[f"{arm}_n_tokens"] = g.get("n_tokens")
        rows.append(rec)
    df2 = pd.DataFrame(rows); df2.to_csv(F["rows.csv"], index=False)
    ok = df2[df2.complete == True].copy()
    for k in ["persist_word", "persist_claim", "jaccard_expl", "format_break", "quoted_token_ok"]:
        ok[f"diff_{k}"] = ok[f"random_{k}"] - ok[f"own_{k}"]
    nl = ok[~ok.is_last]
    ci = R.ci(nl.diff_persist_word, nl.stim_idx) if len(nl) else {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0, "n_clusters": 0}
    out = R.outcome(ci, min_n=MIN_ROWS)
    def strat(s, name):
        if not len(s):
            return f"{name}: n=0"
        pw = R.ci(s.diff_persist_word, s.stim_idx); pc = R.ci(s.diff_persist_claim, s.stim_idx)
        return f"{name}: n={len(s)} persist_word own {s.own_persist_word.mean():.3f} random {s.random_persist_word.mean():.3f} diff {R.fmt_ci(pw, 4)}; persist_claim own {s.own_persist_claim.mean():.3f} random {s.random_persist_claim.mean():.3f} diff {R.fmt_ci(pc, 4)}; format-break own {s.own_format_break.mean():.3f} random {s.random_format_break.mean():.3f}"
    obs = strat(nl, "non-last pooled") + "; " + "; ".join(strat(ok[ok.stratum == n], n) for n in N_STRATA) + f"; positive control quoted_token_ok own {ok[ok.is_last].own_quoted_token_ok.mean() if len(ok[ok.is_last]) else float('nan'):.3f} random {ok[ok.is_last].random_quoted_token_ok.mean() if len(ok[ok.is_last]) else float('nan'):.3f} reference {ok[ok.is_last].ref_quoted_token_ok.mean() if len(ok[ok.is_last]) else float('nan'):.3f}; rows completed {len(ok)}/{len(df)}"
    kill = L.append_disconfirmation("D1", "D1", "CI95 (cluster by explanation) of [persist_word(random) − persist_word(own)] on non-last rows (n ≤ 120) ≤ 0 → MET; > 0 → NOT MET; straddles or < 60 rows completed → INCONCLUSIVE", obs, out,
                                    "concerns the AV's output under a vector edit only; MET/INCONCLUSIVE with the positive control NOT MET = the AV re-asserts from remaining content or the AR direction is not what the AV reads")
    H = ["| stratum | n | n_expl | measure | own | random | random − own | CI lo | CI hi |", "|---|---|---|---|---|---|---|---|---|"]
    lines = ["# D1 summary — claim-direction ablation with the reconstructor as encoder (greedy, α = 0.3)", "", f"git {L.git_hash()[:8]}; settings in d1_settings.json; progress in d1_progress.json", "",
             "## Kill test", "", f"- {kill}", "", "## Format-break rate first", "",
             f"- own: parse_ok {ok.own_parse_ok.mean() if len(ok) else float('nan'):.3f}, cjk {ok.own_cjk.mean() if len(ok) else float('nan'):.3f}, format-break {ok.own_format_break.mean() if len(ok) else float('nan'):.3f}; random: parse_ok {ok.random_parse_ok.mean() if len(ok) else float('nan'):.3f}, cjk {ok.random_cjk.mean() if len(ok) else float('nan'):.3f}, format-break {ok.random_format_break.mean() if len(ok) else float('nan'):.3f} (n={len(ok)})",
             f"- rows sampled {len(df)} ({json.dumps({n: int((df.stratum == n).sum()) for n in N_STRATA})}); completed {len(ok)}; reference persist_word {df2.ref_persist_word.mean():.3f}; reference quoted_token_ok on last rows {df2[df2.is_last].ref_quoted_token_ok.mean():.3f}",
             "", "## Per stratum (paired random − own, cluster by explanation)", ""] + H
    for name in ["non-last pooled"] + list(N_STRATA):
        s = nl if name == "non-last pooled" else ok[ok.stratum == name]
        for k in ["persist_word", "persist_claim", "jaccard_expl", "format_break", "quoted_token_ok", "cos_h_AR_new"]:
            if len(s):
                d = s[f"random_{k}"] - s[f"own_{k}"]; c = R.ci(d, s.stim_idx)
                lines.append(f"| {name} | {len(s)} | {s.stim_idx.nunique()} | {k} | {s[f'own_{k}'].mean():.4f} | {s[f'random_{k}'].mean():.4f} | {c['mean']:.4f} | {c['lo']:.4f} | {c['hi']:.4f} |")
    lines += ["", "## 2×2 (non-last rows): in_full_prefix × slot type — persist_word own / random / diff", "", "| in_full_prefix \\ slot type | entity | detail |", "|---|---|---|"]
    for ip in [True, False]:
        cells = []
        for stp in ["entity", "detail"]:
            s = nl[(nl.in_full_prefix == ip) & (nl.slot_type == stp)]
            cells.append((lambda c: f"n={len(s)} own {s.own_persist_word.mean():.3f} random {s.random_persist_word.mean():.3f} diff {c['mean']:.3f} [{c['lo']:.3f},{c['hi']:.3f}]")(R.ci(s.diff_persist_word, s.stim_idx)) if len(s) else "n=0")
        lines.append(f"| {ip} | {cells[0]} | {cells[1]} |")
    lines += ["", "Distributions for the four cells (persist_claim, own):", ""] + R.DIST_HEADER
    for ip in [True, False]:
        for stp in ["entity", "detail"]:
            s = nl[(nl.in_full_prefix == ip) & (nl.slot_type == stp)]; lines.append(R.dist_row(f"own_persist_claim / in_full_prefix={ip} × {stp}", s.own_persist_claim))
    lines += ["", "## Distributions", ""] + R.DIST_HEADER
    for c in ["d_norm", "proj", "cos_dhat_hhat", "own_cos_hprime_h", "random_cos_hprime_h", "own_cos_h_AR_new", "random_cos_h_AR_new", "cos_z", "cos_zc", "own_persist_claim", "random_persist_claim", "own_jaccard_expl", "random_jaccard_expl"]:
        for name in ["non-last pooled", "positive_control_last"]:
            s = nl if name == "non-last pooled" else ok[ok.stratum == name]
            if len(s):
                lines.append(R.dist_row(f"{c} / {name}", s[c]))
    lines += ["", "## 5 fixed verbatim examples (seed 0; completed non-last rows)", ""]
    rng = np.random.default_rng(0)
    if len(nl):
        for row in rng.choice(nl.row.values, size=min(5, len(nl)), replace=False):
            r = nl[nl.row == row].iloc[0]; i = int(r.stim_idx)
            lines += [f"### row {row} (stim {i}, {r.stratum}, {r.slot_type}, word_orig {r.word_orig!r})", "", f"- claim: {r.claim!r}", f"- original explanation: {expl[i]['explanation']!r}",
                      f"- own ablation (‖d_c‖ {r.d_norm:.3f}, proj {r.proj:.4f}, cos(h',h) {r.own_cos_hprime_h:.4f}): persist_word {r.own_persist_word}, persist_claim {r.own_persist_claim:.3f}: {done[(int(row), 'own')]['explanation']!r}",
                      f"- random ablation (partner row {r.partner_row}, cos(h',h) {r.random_cos_hprime_h:.4f}): persist_word {r.random_persist_word}, persist_claim {r.random_persist_claim:.3f}: {done[(int(row), 'random')]['explanation']!r}", ""]
    blind, key = [], []
    for row in rng.choice(ok.row.values, size=min(20, len(ok)), replace=False):
        r = ok[ok.row == row].iloc[0]; i = int(r.stim_idx); arms = ["own", "random"]; o = np.random.default_rng(int(row)).permutation(2)
        b = {"item_id": f"d1_row_{row}", "item_type": "d1_row", "context_id": i, "prefix_text": "", "sentence": r.claim, "original_explanation": expl[i]["explanation"],
             "new_explanation_1": done[(int(row), arms[o[0]])]["explanation"], "new_explanation_2": done[(int(row), arms[o[1]])]["explanation"], "transform": "ablation (which new explanation still asserts the claim?)", "human_label": "", "human_note": ""}
        blind.append(b); key.append({**b, "arm_1": arms[o[0]], "arm_2": arms[o[1]], "stratum": r.stratum, "own_persist_word": r.own_persist_word, "random_persist_word": r.random_persist_word, "own_persist_claim": r.own_persist_claim, "random_persist_claim": r.random_persist_claim})
    pd.DataFrame(blind).to_csv(F["review_blind.csv"], index=False); pd.DataFrame(key).to_csv(F["review_key.csv"], index=False)
    lines += ["", "- review sheets: d1_review_blind.csv (20 rows, seed 0; the two new explanations in shuffled order) — open first; d1_review_key.csv after", ""]
    F["summary.md"].write_text("\n".join(lines))
    prog.set_phase("done"); S.finish(progress=prog.d, kill=ci, outcome=out, rows_completed=len(ok))
    L.log(f"D1 done: {out}; {len(ok)} rows; {prog.minutes:.1f} min")


if __name__ == "__main__":
    main()

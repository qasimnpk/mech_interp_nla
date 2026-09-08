"""N3 — what does the frozen AR reward: correct specific / wrong specific / generic / omitted (PLAN.md round 3c; AR only).

  uv run python overnight/n3_generic.py

Rows: the accepted deterministic-swap triples of S3 (edit_ok AND numeric_ok; all evaluation claims; n≈402) whose swap
changes exactly one whitespace token of the claim (the S3 rule: first number n → n+7 (n*3 if n<3), else the first
capitalised non-sentence-initial token swapped for a capitalised token from another explanation). kind = 'number' if the
swapped token contains a digit, else 'name' (a capitalised token; the S3 swap list carries no person/place marker).
Four versions of the claim inside the full explanation (claims joined by one space, S3's z_joined convention):
  original; wrong specific = corrupt_det; generic: number → the matched number span replaced by 'a number'; name → the
  capitalised core of the token replaced by 'a place' (PLAN: 'a person' if the swap list marks a person name, else
  'a place'; the list carries no marker, so the else-branch applies to every name — logged); omitted = the claim deleted.
cost(v) = cos(AR(original), h) − cos(AR(v), h). CIs cluster by explanation (stim_idx), 1000 draws, seed 0.
Kill N3 (pre-registered): CI of [cost(generic) − cost(wrong specific)] ≤ 0 → MET. Reported: cost(omitted) − cost(wrong).
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

NUM_RE = re.compile(r"\d+(?:\.\d+)?")
PUNCT = ".,;:!?\"'()"
N_BOOT, SEED = 1000, 0
MIN_N = 100
GENERIC = {"number": "a number", "name": "a place"}
FIXED_EXAMPLES = 5


def make_generic(claim: str, k: int, kind: str) -> str:
    toks = claim.split()
    if kind == "number":
        m = NUM_RE.search(toks[k]); assert m, toks[k]
        toks[k] = toks[k][: m.start()] + GENERIC["number"] + toks[k][m.end():]
    else:
        core = toks[k].strip(PUNCT); toks[k] = toks[k].replace(core, GENERIC["name"], 1)
    return " ".join(toks)


def main():
    S = L.Settings("n3", generic_rule=GENERIC, kind_rule="'number' if the swapped whitespace token contains a digit, else 'name'", join="claims joined by one space (S3 z_joined)",
                   person_marker="the S3 swap list carries no person/place marker → PLAN's else-branch ('a place') applies to every capitalised-name swap", n_boot=N_BOOT, seed=SEED, min_n=MIN_N,
                   kill="CI (by explanation) of mean [cost(generic) − cost(wrong specific)] ≤ 0 → MET")
    timings = {}
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    claims_by_stim = {i: list(g.sort_values("claim_idx").claim) for i, g in s2.groupby("stim_idx")}
    rows = []; n_multi = 0; n_total = 0
    for ln in (L.OVERNIGHT / "s3_edits.jsonl").read_text().splitlines():
        if not ln.strip():
            continue
        r = json.loads(ln)
        if not (r["edit_ok"] and r["numeric_ok"]):
            continue
        n_total += 1
        a, b = r["claim"].split(), r["corrupt_det"].split()
        diff = [k for k in range(min(len(a), len(b))) if a[k] != b[k]]
        if len(a) != len(b) or len(diff) != 1:
            n_multi += 1; continue
        k = diff[0]; kind = "number" if NUM_RE.search(a[k]) else "name"
        claims = claims_by_stim[int(r["stim_idx"])]; ci_ = int(r["claim_idx"]); assert claims[ci_] == r["claim"]
        rows.append({"row": int(r["row"]), "stim_idx": int(r["stim_idx"]), "claim_idx": ci_, "n_claims": int(r["n_claims"]), "is_last": ci_ == len(claims) - 1, "kind": kind, "word_pos": k,
                     "tok_orig": a[k], "tok_wrong": b[k], "claim": r["claim"], "wrong": r["corrupt_det"], "generic": make_generic(r["claim"], k, kind), "_claims": claims, "error": ""})
    L.log(f"rows: {n_total} accepted det triples → {len(rows)} single-token swaps (excluded {n_multi}); kinds {pd.Series([r['kind'] for r in rows]).value_counts().to_dict()}")
    S.update(n_accepted_det=n_total, n_rows=len(rows), n_excluded_multi=n_multi)

    t0 = time.time(); ar = L.AR(); timings["ar_load_s"] = time.time() - t0
    cache = {}

    def score(text, i):
        key = (text, i)
        if key not in cache:
            cache[key] = L.cos(ar.predict(text).numpy(), h20[i])
        return cache[key]
    t0 = time.time()
    for n, r in enumerate(rows):
        i, ci_, cl = r["stim_idx"], r["claim_idx"], r["_claims"]
        try:
            r["z_original"] = " ".join(cl); r["z_wrong"] = " ".join(cl[:ci_] + [r["wrong"]] + cl[ci_ + 1:]); r["z_generic"] = " ".join(cl[:ci_] + [r["generic"]] + cl[ci_ + 1:]); r["z_omitted"] = " ".join(cl[:ci_] + cl[ci_ + 1:])
            for v in ["original", "wrong", "generic", "omitted"]:
                r[f"cos_{v}"] = score(r[f"z_{v}"], i)
            for v in ["wrong", "generic", "omitted"]:
                r[f"cost_{v}"] = r["cos_original"] - r[f"cos_{v}"]
            r["generic_minus_wrong"] = r["cost_generic"] - r["cost_wrong"]; r["omitted_minus_wrong"] = r["cost_omitted"] - r["cost_wrong"]; r["omitted_minus_generic"] = r["cost_omitted"] - r["cost_generic"]
        except Exception:
            r["error"] = traceback.format_exc(); L.log(f"N3 FAILED row {r['row']}")
        if n % 100 == 99:
            L.log(f"{n + 1}/{len(rows)} rows, AR forwards {ar.n_forward} ({(time.time() - t0) / max(1, ar.n_forward):.2f} s each)")
    timings["ar_s_per_score"] = (time.time() - t0) / max(1, ar.n_forward); timings["n_ar_forward"] = ar.n_forward
    ar.free()
    df = pd.DataFrame([{k: v for k, v in r.items() if not k.startswith("_")} for r in rows]); df.to_csv(L.OVERNIGHT / "n3_scores.csv", index=False)
    ok = df[df.error == ""].reset_index(drop=True)

    def ci(v, c):
        return L.cluster_bootstrap_mean(np.asarray(v, float), c, n_boot=N_BOOT, seed=SEED)

    def fm(c, d=5):
        return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}]"

    def block(e):
        return {"n": int(len(e)), "n_expl": int(e.stim_idx.nunique()), **{f"cost_{v}": ci(e[f"cost_{v}"], e.stim_idx) for v in ["wrong", "generic", "omitted"]},
                "generic_minus_wrong": ci(e.generic_minus_wrong, e.stim_idx), "omitted_minus_wrong": ci(e.omitted_minus_wrong, e.stim_idx), "omitted_minus_generic": ci(e.omitted_minus_generic, e.stim_idx),
                "frac_generic_gt_wrong": float((e.generic_minus_wrong > 0).mean()), "frac_omitted_gt_wrong": float((e.omitted_minus_wrong > 0).mean()), "mean_cos_original": float(e.cos_original.mean())}
    B = block(ok); Bk = {k: block(ok[ok.kind == k]) for k in ["number", "name"]}; Bl = {k: block(ok[ok.is_last == v]) for k, v in [("last", True), ("not_last", False)]}
    out = L.outcome_ci_at_or_below(B["generic_minus_wrong"], 0.0, min_n=MIN_N)
    L.append_disconfirmation("N3", "N3", "CI (cluster by explanation) of mean [cost(generic) − cost(wrong specific)], cost(v) = cos(AR(z)) − cos(AR(z_v)), deterministic single-token swaps ≤ 0",
                             f"mean generic−wrong={fm(B['generic_minus_wrong'])} n={B['n']} n_expl={B['n_expl']}; cost wrong {fm(B['cost_wrong'])} generic {fm(B['cost_generic'])} omitted {fm(B['cost_omitted'])}; omitted−wrong {fm(B['omitted_minus_wrong'])}; "
                             f"frac generic>wrong {B['frac_generic_gt_wrong']:.3f}; number n={Bk['number']['n']} generic−wrong {fm(Bk['number']['generic_minus_wrong'])}; name n={Bk['name']['n']} {fm(Bk['name']['generic_minus_wrong'])}",
                             out, "MET would mean no evidence the frozen AR prefers a thematically matched wrong specific over a generic; says what the frozen scorer rewards, not what training caused")
    lines = ["# N3 summary — what the frozen AR rewards: correct specific / wrong specific / generic / omitted (AR only)", "",
             f"git {L.git_hash()[:8]}; settings in n3_settings.json; rows in n3_scores.csv", "",
             f"- accepted deterministic-swap triples {n_total} → {len(rows)} single-token swaps ({n_multi} excluded: swap not a single whitespace token); kinds {ok.kind.value_counts().to_dict()}; last-claim rows {int(ok.is_last.sum())}",
             f"- generic rule: number → `a number`; capitalised name → `a place` (the S3 swap list carries no person marker, so PLAN's else-branch applies to all names); no LLM",
             f"- AR forwards {timings['n_ar_forward']} ({timings['ar_s_per_score']:.2f} s each); errors {int((df.error != '').sum())}",
             "", "## Kill N3", "", f"- mean [cost(generic) − cost(wrong specific)]: {fm(B['generic_minus_wrong'])} n={B['n']} → **{out}**", "",
             "## Four-way table (cost = cos drop relative to the original; CI by explanation)", "", "| subset | n | n_expl | mean cos(original) | cost(wrong specific) | cost(generic) | cost(omitted) | generic − wrong | omitted − wrong | omitted − generic | frac generic>wrong | frac omitted>wrong |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, b in [("all", B), ("number swaps", Bk["number"]), ("name swaps", Bk["name"]), ("last claim", Bl["last"]), ("not last claim", Bl["not_last"])]:
        lines.append(f"| {name} | {b['n']} | {b['n_expl']} | {b['mean_cos_original']:.4f} | {fm(b['cost_wrong'])} | {fm(b['cost_generic'])} | {fm(b['cost_omitted'])} | {fm(b['generic_minus_wrong'])} | {fm(b['omitted_minus_wrong'])} | {fm(b['omitted_minus_generic'])} | {b['frac_generic_gt_wrong']:.3f} | {b['frac_omitted_gt_wrong']:.3f} |")
    lines += ["", "## Five verbatim rows (first five rows; number and name)", ""]
    for r in ([x for x in rows if x["kind"] == "number" and not x["error"]][:3] + [x for x in rows if x["kind"] == "name" and not x["error"]][:2]):
        lines += [f"### row {r['row']} (stim {r['stim_idx']}, claim {r['claim_idx']}/{r['n_claims']}, {r['kind']}: {r['tok_orig']!r} → {r['tok_wrong']!r})",
                  f"- original: {r['claim']}", f"- wrong specific: {r['wrong']}", f"- generic: {r['generic']}",
                  f"- cos original {r['cos_original']:.4f}; cost wrong {r['cost_wrong']:+.5f} generic {r['cost_generic']:+.5f} omitted {r['cost_omitted']:+.5f}", ""]
    (L.OVERNIGHT / "n3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(timings=timings, kill_N3={"ci": B["generic_minus_wrong"], "outcome": out}, stats={"all": B, "number": Bk["number"], "name": Bk["name"], "last": Bl["last"], "not_last": Bl["not_last"]})
    L.log(f"N3 done: generic−wrong {fm(B['generic_minus_wrong'])} -> {out}")


if __name__ == "__main__":
    main()

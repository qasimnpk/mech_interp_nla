"""V0 — round-4 artifact check, benchmark, pipeline verification, orchestrator throughput, re-budget (PLAN.md round 4; no kill test).

  uv run python overnight/v0_check.py [--minutes rewrite=M,label=M,equiv=M]

Re-entrant: the model benchmark is saved to overnight/v0_bench.json and never recomputed; the throughput task file
v0_agent_tasks_bench.jsonl (10 rewrite + 5 label + 5 equiv) goes through the agent-judgement protocol (AWAITING exit),
and the re-budget runs once the outputs validate. Writes v0_check.md, v0_settings.json, v0_progress.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import r4_lib as R  # noqa: E402  (imports nla_lib first: MPS env)
from overnight import nla_lib as L  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

N_CALLS = 5
BENCH_JSON = L.OVERNIGHT / "v0_bench.json"
STAGE = "V0"
CAPS = R.ROUND4_CAPS_MIN
# projection assumptions (recorded; not thresholds)
ASSUME = {"b1_slot_verify_per_context": 2.0, "a1_slots_per_context": 2.0, "a1_slot_verify_per_slot": 1.5,
          "a1_contradicted_fraction": 0.3, "a1_entity_slot_fraction": 0.5,
          "judge_task_minutes": "slot_verify and edit_check at the measured label rate; fact_swap / detail_sub / relation_rev / negation / correction at max(label, 0.5 x rewrite)"}


def timeit(fn, n=N_CALLS):
    ts = []
    for _ in range(n):
        t = time.time(); fn(); torch.mps.synchronize(); ts.append(time.time() - t)
    return {"n": n, "mean_s": float(np.mean(ts)), "min_s": float(np.min(ts)), "max_s": float(np.max(ts)), "all_s": [float(x) for x in ts]}


def artifact_checks() -> list[tuple]:
    checks = []

    def chk(name, got, want):
        checks.append((name, got, want, got == want))

    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False); chk("stimuli rows", len(st), 200)
    nx = len(R.read_jsonl(L.OVERNIGHT / "explanations.jsonl")); chk("explanations rows", nx, 200)
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False); chk("s2_claims rows", len(s2), 671)
    ne = len(R.read_jsonl(L.OVERNIGHT / "s3_edits.jsonl")); chk("s3_edits rows", ne, 538)
    s3 = pd.read_csv(L.OVERNIGHT / "s3_scores.csv", keep_default_na=False); checks.append(("s3_scores rows", len(s3), ">0", len(s3) > 0))
    t2b = pd.read_csv(L.OVERNIGHT / "t2b_claims.csv", keep_default_na=False); chk("t2b_claims rows", len(t2b), 691)
    a = np.load(L.OUT / "acts_L20.npz"); chk("acts_L20 h20 shape", tuple(a["h20"].shape), (200, 3584))
    p = pd.read_csv(L.REPO_ROOT / "notes" / "t2b_in_full_prefix.csv"); chk("t2b_in_full_prefix rows", len(p), 691)
    chk("t2b_in_full_prefix True", int(p.in_full_prefix.sum()), 257)
    det = t2b[t2b.edit_type == "corrupt_det"]; chk("t2b corrupt_det rows", len(det), 393)
    pdet = p[p.edit_type == "corrupt_det"][["row", "in_full_prefix"]]
    m = det.merge(pdet, on="row", how="left"); chk("corrupt_det rows with in_full_prefix", int(m.in_full_prefix.notna().sum()), 393)
    nl = m[m.is_last.astype(str) == "False"]; chk("corrupt_det is_last==False", len(nl), 266)
    chk("corrupt_det is_last==False & in_full_prefix", int(nl.in_full_prefix.sum()), 107)
    chk("corrupt_det is_last==True", int((m.is_last.astype(str) == "True").sum()), 127)
    for f in ["nla_lib.py", "s2_deletion.py", "s3_corrupt.py", "c2_matched.py"]:
        chk(f"{f} present", (L.OVERNIGHT / f).exists(), True)
    return checks


def build_tasks(tok, ds) -> list[dict]:
    s2 = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    tasks = []
    for i in range(10):
        g = s2[s2.stim_idx == i].sort_values("claim_idx")
        claim = g.claim.iloc[1] if len(g) > 1 else g.claim.iloc[0]
        tasks.append({"task_id": f"v0_rw_{i}", "type": "rewrite", "inputs": {"candidate": claim, "instruction": R.TASK_INSTRUCTIONS["rewrite"]}})
    for i in range(5):
        g = s2[s2.stim_idx == i].sort_values("claim_idx")
        claim = g.claim.iloc[1] if len(g) > 1 else g.claim.iloc[0]
        prefix, _ = R.stimulus_prefix(tok, ds, int(st.doc_idx[i]), int(st.pos[i]))
        tasks.append({"task_id": f"v0_lb_{i}", "type": "label", "inputs": {"passage": prefix, "sentence": claim, "instruction": R.TASK_INSTRUCTIONS["label"]}})
    ed = [e for e in R.read_jsonl(L.OVERNIGHT / "s3_edits.jsonl") if e.get("edit_ok")][:5]
    for k, e in enumerate(ed):
        tasks.append({"task_id": f"v0_eq_{k}", "type": "equiv", "inputs": {"candidate": e["claim"], "realization": e["paraphrase"], "instruction": R.TASK_INSTRUCTIONS["equiv"],
                                                                          "source": f"s3_edits row {e['row']} (claim, LLM paraphrase); used for nothing else"}})
    return tasks


def run_bench(prog: R.Progress) -> dict:
    B = {"pipeline": {}, "bench": {}}
    st = pd.read_csv(L.OVERNIGHT / "stimuli.csv", keep_default_na=False)
    expl = {r["stim_idx"]: r for r in R.read_jsonl(L.OVERNIGHT / "explanations.jsonl")}
    h20 = np.load(L.OUT / "acts_L20.npz")["h20"]
    ds = R.wikitext_train()
    pairs = R.b1_pairs()

    # ---------------- TARGET
    prog.set_phase("bench_target")
    t0 = time.time(); tgt = L.Target(); B["bench"]["target_load_s"] = time.time() - t0
    tok = tgt.tok
    B["pipeline"]["extractor"] = {"class": "nla_lib.Target", "repo": L.TARGET, "snapshot": L.snapshot(L.TARGET).name,
                                  "num_hidden_layers": int(tgt.model.config.num_hidden_layers), "hidden_states_index": L.LAYER + 1}
    # (7) B1 position check
    def pos_table(filler2):
        rows = []
        for p in pairs:
            ids = {v: tok(R.b1_context(p, v, filler2), add_special_tokens=False)["input_ids"] for v in "AB"}
            rows.append({"pair_id": p["pair_id"], "n_tokens_A": len(ids["A"]), "n_tokens_B": len(ids["B"]), "t_A": len(ids["A"]) - 1, "t_B": len(ids["B"]) - 1,
                         "tok_t_A": ids["A"][-1], "tok_t_B": ids["B"][-1], "tok_str_t": tok.decode([ids["A"][-1]]),
                         "len_mismatch": len(ids["A"]) != len(ids["B"]), "final_ok": tok.decode([ids["A"][-1]]) == "." and tok.decode([ids["B"][-1]]) == "."})
        return rows
    rows = pos_table(False); min_t = min(min(r["t_A"], r["t_B"]) for r in rows)
    filler2 = min_t < 50
    if filler2:
        rows = pos_table(True); min_t = min(min(r["t_A"], r["t_B"]) for r in rows)
    B["pipeline"]["b1_position"] = {"filler2_applied": filler2, "min_t": min_t, "all_t_ge_50": min_t >= 50, "n_contexts": 2 * len(rows),
                                    "n_len_mismatch": sum(r["len_mismatch"] for r in rows), "n_final_token_not_period": sum(not r["final_ok"] for r in rows),
                                    "tok_t_match_within_pair": all(r["tok_t_A"] == r["tok_t_B"] for r in rows), "rows": rows}
    # benchmark forwards
    ctx80 = tok(R.b1_context(pairs[0], "A", filler2), return_tensors="pt", add_special_tokens=False)["input_ids"]
    B["bench"]["target_ctx_forward_hidden"] = timeit(lambda: tgt.hidden_states(ctx80)); B["bench"]["target_ctx_forward_hidden"]["tokens"] = int(ctx80.shape[1])
    ids256 = torch.tensor([tok(ds[int(st.doc_idx[0])]["page"], add_special_tokens=False)["input_ids"][:256]])
    B["bench"]["target_256_forward_hidden"] = timeit(lambda: tgt.hidden_states(ids256)); B["bench"]["target_256_forward_hidden"]["tokens"] = int(ids256.shape[1])
    # sanity: block-20 activation at stimulus 0's position from the 512-token doc matches the cache
    ids512 = torch.tensor([tok(ds[int(st.doc_idx[0])]["page"], add_special_tokens=False)["input_ids"][:512]])
    hs = tgt.hidden_states(ids512); dev = 1 - L.cos(L.to_cpu_f32(hs[L.LAYER + 1][0, int(st.pos[0])]).numpy(), h20[0])
    B["pipeline"]["acts_cache_1_minus_cos"] = float(dev)
    tasks = build_tasks(tok, ds)
    tgt.free(); B["bench"]["rss_after_target_free_G"] = L.rss_mb() / 1024
    prog.tick()

    # ---------------- AV
    prog.set_phase("bench_av")
    t0 = time.time(); av = L.AV(); B["bench"]["av_load_s"] = time.time() - t0
    sampled, greedy = [], []
    it = iter(range(N_CALLS))
    B["bench"]["av_sampled_200"] = timeit(lambda: sampled.append(R.verbalize_sampled(av, torch.from_numpy(h20[(k := next(it))]), seed=1 + k)))
    it2 = iter(range(N_CALLS))
    B["bench"]["av_greedy_200"] = timeit(lambda: greedy.append(R.verbalize_greedy(av, torch.from_numpy(h20[next(it2)]))))
    for name, gens in [("av_sampled_200", sampled), ("av_greedy_200", greedy)]:
        B["bench"][name]["n_tokens"] = [g["n_tokens"] for g in gens]; B["bench"][name]["parse_ok"] = [g["parse_ok"] for g in gens]
        B["bench"][name]["ended_with_close_tag"] = [g["ended_with_close_tag"] for g in gens]; B["bench"][name]["ended_with_eos"] = [g["ended_with_eos"] for g in gens]
    B["generations"] = {"sampled": sampled, "greedy": greedy}
    # (1) stimuli 0 and 1 give different greedy explanations
    B["pipeline"]["check1_greedy_0_ne_1"] = {"different": greedy[0]["explanation"] != greedy[1]["explanation"],
                                             "greedy_equals_round1": [greedy[k]["explanation"] == expl[k]["explanation"] for k in range(N_CALLS)]}
    av.free(); B["bench"]["rss_after_av_free_G"] = L.rss_mb() / 1024
    prog.tick()

    # ---------------- AR
    prog.set_phase("bench_ar")
    t0 = time.time(); ar = L.AR(); B["bench"]["ar_load_s"] = time.time() - t0
    z = {i: expl[i]["explanation"] for i in range(10)}
    preds = {}
    it3 = iter(range(N_CALLS))
    B["bench"]["ar_score"] = timeit(lambda: preds.__setitem__((k := next(it3)), R.ar_score(ar, z[k], h20[k])))
    for i in range(N_CALLS, 10):
        preds[i] = R.ar_score(ar, z[i], h20[i])
    # (2) own vs shifted explanation
    c2 = []
    for i in range(10):
        j = (i + 5) % 10
        own = preds[i]["cos"]; other = L.cos(preds[j]["pred"], h20[i])
        c2.append({"i": i, "j": j, "cos_own": own, "cos_other": other, "own_gt_other": own > other})
    B["pipeline"]["check2_own_vs_shift"] = {"n_own_gt_other": sum(r["own_gt_other"] for r in c2), "rows": c2, "pass": sum(r["own_gt_other"] for r in c2) >= 9}
    # (3) z_0 scored five times
    reps = [R.ar_score(ar, z[0], h20[0])["cos"] for _ in range(5)]
    B["pipeline"]["check3_repeat"] = {"cos": reps, "max_abs_delta": float(max(reps) - min(reps)), "pass": (max(reps) - min(reps)) < 1e-4}
    # (5) longest round-1 explanation inside the AR template; generations not ending with </explanation> or EOS
    longest = max(expl.values(), key=lambda r: len(r["explanation"] or ""))
    n_tok_longest = R.ar_input_tokens(ar, longest["explanation"])
    not_closed = [r["stim_idx"] for r in expl.values() if not ((r.get("raw_generation") or "").rstrip().endswith("</explanation>") or (r.get("n_tokens") or 200) < 200)]
    B["pipeline"]["check5_ar_input"] = {"longest_stim_idx": longest["stim_idx"], "ar_input_tokens": n_tok_longest, "pass": n_tok_longest < 1024,
                                        "round1_not_closed_or_eos": len(not_closed), "round1_not_closed_ids": not_closed,
                                        "eos_rule": "n_tokens < 200 (generation stopped before max_new_tokens) taken as EOS; close tag = raw ends with </explanation>"}
    ar.free()
    prog.tick()

    # (4) dummy edited text passes the prefix/suffix asserts
    E = z[0]; claims = R.split_claims_quote_aware(E); s = claims[1] if len(claims) > 1 else claims[0]
    a, b, dup = R.sentence_span(E, s); E2 = R.substitute(E, a, b, "This is a dummy sentence.")
    B["pipeline"]["check4_dummy_edit"] = {"stim_idx": 0, "sentence": s, "span": [a, b], "dup_sentence": dup, "edited_len": len(E2), "pass": True,
                                          "deletion_text": R.deletion_text(E, a, b)}
    B["tasks"] = tasks
    return B


def project(stage: str, c: dict, j: dict, loads: dict, params: dict) -> dict:
    """Projected minutes from measured per-call costs (s) and per-task judgement minutes."""
    P = dict(params)
    if stage == "B1":
        n = P["n_ctx"]; npar = P["n_par"]; sv = ASSUME["b1_slot_verify_per_context"]
        calls = {"target_ctx_forward_hidden": n, "av_sampled_200": n, "ar_score": n * (2 * (1 + npar) + 1)}
        tasks = {"slot_verify": n * sv + n, "fact_swap": n, "edit_check": n, "rewrite": 2 * n, "equiv": 2 * n * npar}
        ld = ["T", "A", "R"]
    elif stage == "A1":
        n = P["n_ctx"]; npar = P["n_par"]; ns = n * ASSUME["a1_slots_per_context"]; neg = 1 if P["negation"] else 0
        ent = ASSUME["a1_entity_slot_fraction"]; ncand = ent * (3 + neg) + (1 - ent) * (2 + neg); nagent = 2 + neg
        corr = ASSUME["a1_contradicted_fraction"]
        meanings = 1 + ncand + corr
        calls = {"target_256_forward_hidden": n, "av_sampled_200": n, "ar_score": ns * (meanings * (1 + npar) + 1) + n}
        tasks = {"slot_verify": ns * ASSUME["a1_slot_verify_per_slot"], "label": ns + ns * corr + ns * ncand, "correction": ns * corr,
                 "detail_sub": ns, "relation_rev": ns, "negation": ns * neg, "edit_check": ns * corr + ns * ncand,
                 "rewrite": ns * meanings, "equiv": ns * meanings * npar}
        ld = ["T", "A", "R"]
    elif stage == "K1":
        calls = {"ar_score": 393 * 8 + 20}; tasks = {}; ld = ["R"]
    elif stage == "D1":
        n = P["n_rows"]
        calls = {"ar_score": 2 * n + 2 * n, "av_greedy_200": 2 * n}; tasks = {}; ld = ["R", "A", "R"]
    else:
        raise ValueError(stage)
    secs = sum(k * c[name] for name, k in calls.items()) + sum(loads[x] for x in ld)
    jm = sum(k * j[t] for t, k in tasks.items())
    return {"stage": stage, "params": P, "calls": calls, "tasks": tasks, "compute_min": secs / 60, "judgement_min": jm,
            "projected_min": secs / 60 + jm, "cap_min": CAPS[stage], "over_cap": secs / 60 + jm > CAPS[stage]}


def rebudget(c, j, loads) -> dict:
    out = {"cut_rules_applied": [], "stages": {}}
    # A1: (a) paraphrases 2+2 -> 1+1; (b) drop negation; (c) contexts 60 -> 40
    p = {"n_ctx": 60, "n_par": 4, "negation": True}; hist = [project("A1", c, j, loads, p)]
    for rule, upd in [("A1(a) paraphrases 2+2 -> 1+1 (light1, aggr1)", {"n_par": 2}), ("A1(b) drop the negation candidate", {"negation": False}),
                      ("A1(c) contexts 60 -> 40 (dev 10 stays; eval 50 -> 30 by selection order)", {"n_ctx": 40})]:
        if not hist[-1]["over_cap"]:
            break
        p.update(upd); out["cut_rules_applied"].append(rule); hist.append(project("A1", c, j, loads, p))
    out["stages"]["A1"] = {"final": hist[-1], "history": hist}
    # B1: (a) fillings 5 -> 4 (drop f4); (b) paraphrases as A1(a)
    p = {"n_ctx": 80, "n_par": 4}; hist = [project("B1", c, j, loads, p)]
    for rule, upd in [("B1(a) fillings per template 5 -> 4 (drop f4): 64 contexts", {"n_ctx": 64}), ("B1(b) paraphrases 2+2 -> 1+1 (light1, aggr1)", {"n_par": 2})]:
        if not hist[-1]["over_cap"]:
            break
        p.update(upd); out["cut_rules_applied"].append(rule); hist.append(project("B1", c, j, loads, p))
    out["stages"]["B1"] = {"final": hist[-1], "history": hist}
    # K1: none
    out["stages"]["K1"] = {"final": project("K1", c, j, loads, {}), "history": []}
    # D1: strata 60+60 -> 40+40
    p = {"n_rows": 140}; hist = [project("D1", c, j, loads, p)]
    if hist[-1]["over_cap"]:
        p.update({"n_rows": 100}); out["cut_rules_applied"].append("D1 strata 60+60 -> 40+40 (positive control 20 unchanged): 100 rows"); hist.append(project("D1", c, j, loads, p))
    out["stages"]["D1"] = {"final": hist[-1], "history": hist}
    out["total_projected_min"] = sum(v["final"]["projected_min"] for v in out["stages"].values())
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--minutes", default="", help="orchestrator per-type minutes, e.g. rewrite=3.0,label=1.5,equiv=0.7")
    args = ap.parse_args()
    prog = R.Progress(STAGE)
    S = L.Settings("v0", n_calls=N_CALLS, caps_min=CAPS, assumptions=ASSUME, task_instructions=R.TASK_INSTRUCTIONS, agent_model=R.AGENT_MODEL,
                   b1_preamble=R.PREAMBLE, b1_filler2=R.FILLER2)
    checks = artifact_checks()
    n_ok = sum(c[3] for c in checks); L.log(f"artifact checks: {n_ok}/{len(checks)} OK")
    S.update(checks=[{"check": n, "got": str(g), "want": str(w), "ok": bool(o)} for n, g, w, o in checks])
    if BENCH_JSON.exists():
        B = json.loads(BENCH_JSON.read_text()); L.log("bench reused from v0_bench.json")
    else:
        try:
            B = run_bench(prog)
        except Exception:
            prog.fail(traceback.format_exc()); raise
        BENCH_JSON.write_text(json.dumps(B, indent=1, ensure_ascii=False, default=str))
        for g in B["generations"]["sampled"] + B["generations"]["greedy"]:
            R.append_jsonl(L.OVERNIGHT / "v0_av.jsonl", g)
    # (6) no AV.model( call outside verbalize*
    files = [L.OVERNIGHT / f for f in ["r4_lib.py", "v0_check.py", "b1_pairs.py", "a1_natural.py", "k1_kway.py", "d1_ablate.py"]]
    hits = R.assert_no_av_model_calls(files)
    B["pipeline"]["check6_av_model_calls"] = {"files_scanned": [f.name for f in files if f.exists()], "hits": hits, "pass": not hits}
    # orchestrator throughput (agent-judgement protocol)
    prog.set_phase("agent_bench")
    outs = R.require_outputs("v0", "bench", B["tasks"], prog)  # exits 0 with AWAITING / MISSING until complete
    prog.completed("agent_tasks", len(outs))
    minutes = {}
    for kv in args.minutes.split(","):
        if "=" in kv:
            k, v = kv.split("="); minutes[k.strip()] = float(v)
    types = {}
    for t in B["tasks"]:
        types[t["type"]] = types.get(t["type"], 0) + 1
    jl = prog.d["judgement_log"][-1] if prog.d["judgement_log"] else {"minutes": float("nan")}
    per_task = {}
    for ty, n in types.items():
        per_task[ty] = (minutes[ty] / n) if ty in minutes else (jl["minutes"] / len(B["tasks"]))
    per_task_source = "--minutes per type (orchestrator's own block timing)" if minutes else "total awaiting minutes / 20 tasks (no per-type timing given)"
    # re-budget
    prog.set_phase("rebudget")
    c = {k: B["bench"][k]["mean_s"] for k in ["target_ctx_forward_hidden", "target_256_forward_hidden", "av_sampled_200", "av_greedy_200", "ar_score"]}
    loads = {"T": B["bench"]["target_load_s"], "A": B["bench"]["av_load_s"], "R": B["bench"]["ar_load_s"]}
    j = {"rewrite": per_task.get("rewrite", float("nan")), "label": per_task.get("label", float("nan")), "equiv": per_task.get("equiv", float("nan"))}
    j["slot_verify"] = j["label"]; j["edit_check"] = j["label"]
    for t in ["fact_swap", "detail_sub", "relation_rev", "negation", "correction"]:
        j[t] = max(j["label"], 0.5 * j["rewrite"])
    RB = rebudget(c, j, loads)
    for r in RB["cut_rules_applied"]:
        prog.add_cut_rule(r)
    # ---------------- report
    pl = B["pipeline"]
    lines = ["# V0 check — artifacts, benchmark, pipeline verification, orchestrator throughput, re-budget (round 4)", "",
             f"git {L.git_hash()[:8]}; settings in v0_settings.json; bench in v0_bench.json; generations in v0_av.jsonl; tasks v0_agent_tasks_bench.jsonl / outputs v0_agent_outputs_bench.jsonl", "",
             "## Artifact checks", "", "| check | got | want | ok |", "|---|---|---|---|"]
    lines += [f"| {n} | {g} | {w} | {'OK' if o else 'FAIL'} |" for n, g, w, o in checks]
    lines += ["", f"## Measured costs ({N_CALLS} calls each; mean / min / max seconds; MPS synchronised; first call includes warm-up)", "",
              "| call type | mean s | min s | max s | note |", "|---|---|---|---|---|"]
    for k in ["target_ctx_forward_hidden", "target_256_forward_hidden", "av_sampled_200", "av_greedy_200", "ar_score"]:
        b = B["bench"][k]; extra = {kk: vv for kk, vv in b.items() if kk not in ("n", "mean_s", "min_s", "max_s", "all_s")}
        lines.append(f"| {k} | {b['mean_s']:.3f} | {b['min_s']:.3f} | {b['max_s']:.3f} | {json.dumps(extra)} |")
    lines += ["", f"- model loads: TARGET {loads['T']:.0f} s, AV {loads['A']:.0f} s, AR {loads['R']:.0f} s; RSS after TARGET free {B['bench']['rss_after_target_free_G']:.1f} G, after AV free {B['bench']['rss_after_av_free_G']:.1f} G",
              f"- block-20 activation of stimulus 0 recomputed from the 512-token document vs acts_L20: 1−cos = {pl['acts_cache_1_minus_cos']:.2e}", "",
              "## Pipeline verification (dev items only)", "", "| check | result | pass |", "|---|---|---|",
              f"| (1) stimuli 0 and 1 give different greedy explanations | different={pl['check1_greedy_0_ne_1']['different']}; greedy equals round-1 explanation for stimuli 0–4: {pl['check1_greedy_0_ne_1']['greedy_equals_round1']} | {'OK' if pl['check1_greedy_0_ne_1']['different'] else 'FAIL'} |",
              f"| (2) s(h_i, z_i) > s(h_i, z_(i+5) mod 10), stimuli 0–9 | {pl['check2_own_vs_shift']['n_own_gt_other']}/10 | {'OK' if pl['check2_own_vs_shift']['pass'] else 'FAIL'} |",
              f"| (3) z_0 scored five times: max Δcos | {pl['check3_repeat']['max_abs_delta']:.2e} | {'OK' if pl['check3_repeat']['pass'] else 'FAIL'} |",
              f"| (4) dummy edited text passes the prefix/suffix asserts | stim 0 sentence span {pl['check4_dummy_edit']['span']} dup={pl['check4_dummy_edit']['dup_sentence']} | OK |",
              f"| (5) longest round-1 explanation in the AR template | stim {pl['check5_ar_input']['longest_stim_idx']}: ar_input_tokens={pl['check5_ar_input']['ar_input_tokens']} (<1024); round-1 generations ending with neither </explanation> nor EOS: {pl['check5_ar_input']['round1_not_closed_or_eos']} {pl['check5_ar_input']['round1_not_closed_ids']} | {'OK' if pl['check5_ar_input']['pass'] else 'FAIL'} |",
              f"| (6) extractor = nla_lib.Target ({pl['extractor']['repo']}, snapshot {pl['extractor']['snapshot']}); AV.model( calls outside verbalize* | scanned {pl['check6_av_model_calls']['files_scanned']}; hits {pl['check6_av_model_calls']['hits']} | {'OK' if pl['check6_av_model_calls']['pass'] else 'FAIL'} |",
              f"| (7) B1 position check: all 80 contexts t ≥ 50 | min t={pl['b1_position']['min_t']}; filler2 applied={pl['b1_position']['filler2_applied']}; len_mismatch pairs={pl['b1_position']['n_len_mismatch']}; final token '.' everywhere={pl['b1_position']['n_final_token_not_period'] == 0}; token id at t matches within every pair={pl['b1_position']['tok_t_match_within_pair']} | {'OK' if pl['b1_position']['all_t_ge_50'] else 'FAIL'} |",
              "", "## Orchestrator throughput (20-task sample: 10 rewrite, 5 label, 5 equiv; outputs used for nothing else)", "",
              f"- wall-clock between AWAITING and validation: {jl['minutes']:.1f} min for {len(B['tasks'])} tasks",
              f"- per-task minutes used for the re-budget ({per_task_source}): " + ", ".join(f"{k} {v:.2f}" for k, v in per_task.items()),
              f"- assumed rates for unmeasured types: {ASSUME['judge_task_minutes']}",
              "", "## Re-budget (measured costs × PLAN call counts + judgement minutes; cut rules applied in the pre-declared order until the projection fits the cap)", "",
              "| stage | params | compute min | judgement min | projected min | cap | over cap |", "|---|---|---|---|---|---|---|"]
    for stg, v in RB["stages"].items():
        for h in v["history"] or [v["final"]]:
            lines.append(f"| {stg} | {json.dumps(h['params'])} | {h['compute_min']:.1f} | {h['judgement_min']:.1f} | {h['projected_min']:.1f} | {h['cap_min']} | {'YES' if h['over_cap'] else 'no'} |")
    lines += ["", "### Cut rules applied", ""] + ([f"- {r}" for r in RB["cut_rules_applied"]] or ["- none"])
    lines += ["", f"- total projected {RB['total_projected_min']:.0f} min for B1 + A1 + K1 + D1 (hard stop 10 h = 600 min from the first round-4 RUNLOG line; T9 reserve 30 min)",
              f"- projection assumptions: {json.dumps({k: v for k, v in ASSUME.items() if k != 'judge_task_minutes'})}",
              f"- V0 cumulative minutes (script + judgement): {prog.minutes:.1f} (cap {CAPS['V0']})", ""]
    (L.OVERNIGHT / "v0_check.md").write_text("\n".join(lines))
    S.finish(bench=B["bench"], pipeline={k: v for k, v in pl.items() if k != "b1_position"} | {"b1_position": {k: v for k, v in pl["b1_position"].items() if k != "rows"}},
             rebudget=RB, per_task_minutes=per_task, per_task_source=per_task_source, cut_rules_applied=RB["cut_rules_applied"])
    prog.set_phase("done")
    L.log(f"V0 done: costs {json.dumps({k: round(v, 3) for k, v in c.items()})}; judgement per task {json.dumps({k: round(v, 2) for k, v in per_task.items()})}; cuts {RB['cut_rules_applied']}; total projected {RB['total_projected_min']:.0f} min")


if __name__ == "__main__":
    main()

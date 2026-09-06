"""S3 — corrupted vs paraphrased claims (PLAN.md round 1).

  uv run python overnight/s3_corrupt.py

Editor = plain TARGET (Qwen2.5-7B-Instruct), chat template, greedy, 120 new tokens; TARGET + AR
co-resident. For every evaluation claim from S2: LLM corruption c*, LLM paraphrase c~,
deterministic corruption (number/capitalised-token swap) and off-topic swap. Scores each edited
explanation z_edit and the deletion delta of the edited claim. Kill test K3.
"""
from __future__ import annotations

import json
import re
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402
from overnight.s2_deletion import split_claims  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

MAX_NEW = 120
MIN_ACCEPTED = 100
CORRUPT_PROMPT = ("Rewrite the sentence below changing exactly ONE checkable fact (a name, a number, a place, a category, "
                  "or a polarity such as positive/negative) to a clearly contradictory value. Keep every other word, the length, "
                  "and the style identical. Output only the rewritten sentence inside <out></out> tags.\n\nSentence: {claim}")
PARA_PROMPT = ("Rewrite the sentence below so that it says exactly the same thing with different wording. Do not add, remove or "
               "change any fact. Keep the length similar. Output only the rewritten sentence inside <out></out> tags.\n\nSentence: {claim}")
OUT_RE = re.compile(r"<out>\s*(.*?)\s*</out>", re.DOTALL)
NUM_RE = re.compile(r"\d+(?:\.\d+)?")
CAP_RE = re.compile(r"^[A-Z][A-Za-z]+$")
EDIT_TYPES = ["corrupt", "paraphrase", "corrupt_det", "offtopic"]

S = L.Settings("s3", max_new_tokens=MAX_NEW, decoding="greedy", min_accepted=MIN_ACCEPTED,
               corrupt_prompt=CORRUPT_PROMPT, paraphrase_prompt=PARA_PROMPT,
               acceptance="tags parsed; word count within ±30% of original; >=1 word changed; corrupt != paraphrase",
               corrupt_det="first number n -> n+7 (n*3 if n<3); else first capitalised non-sentence-initial token swapped for a capitalised non-initial token from another evaluation explanation's claims (rng 3000+row); else numeric_ok=False",
               offtopic="claim replaced by a claim from another evaluation document (rng 2000+row)",
               claims_source="overnight/s2_claims.csv rows with split==eval",
               bootstrap="cluster by explanation (stim_idx), 1000 draws, seed 0")


def parse_out(raw: str):
    m = OUT_RE.search(raw)
    return (m.group(1).strip(), True) if m else (None, False)


def word_ok(orig: str, new: str | None) -> bool:
    if not new:
        return False
    a, b = len(orig.split()), len(new.split())
    return 0.7 * a <= b <= 1.3 * a and new.split() != orig.split()


def corrupt_det(claim: str, pool: list[str], rng) -> tuple[str | None, bool]:
    m = NUM_RE.search(claim)
    if m:
        s = m.group(0)
        n = float(s)
        new = n + 7 if n >= 3 else n * 3
        new_s = str(int(new)) if "." not in s else f"{new:.{len(s.split('.')[1])}f}"
        return claim[:m.start()] + new_s + claim[m.end():], True
    toks = claim.split()
    for k in range(1, len(toks)):
        core = toks[k].strip(".,;:!?\"'()")
        if CAP_RE.match(core) and pool:
            repl = pool[int(rng.integers(0, len(pool)))]
            toks[k] = toks[k].replace(core, repl, 1)
            return " ".join(toks), True
    return None, False


def auroc(pos, neg) -> float:
    from scipy.stats import rankdata
    pos = np.asarray(pos, float); neg = np.asarray(neg, float)
    pos = pos[~np.isnan(pos)]; neg = neg[~np.isnan(neg)]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    r = rankdata(np.concatenate([pos, neg]))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def main():
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    cl = pd.read_csv(L.OVERNIGHT / "s2_claims.csv", keep_default_na=False)
    cl = cl[cl.split == "eval"].reset_index(drop=True)
    claims_by_stim = {i: list(g.sort_values("claim_idx").claim) for i, g in cl.groupby("stim_idx")}
    # pools for deterministic / off-topic edits
    cap_pool_by_stim = {}
    for i, cs in claims_by_stim.items():
        p = []
        for c in cs:
            toks = c.split()
            p += [t.strip(".,;:!?\"'()") for t in toks[1:] if CAP_RE.match(t.strip(".,;:!?\"'()"))]
        cap_pool_by_stim[i] = p
    all_claims = [(int(r.stim_idx), r.claim) for r in cl.itertuples()]

    edits_path = L.OVERNIGHT / "s3_edits.jsonl"
    done = {}
    if edits_path.exists():
        for line in edits_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line); done[r["row"]] = r

    # ---------------- editor (TARGET)
    tgt = L.Target()
    t0 = time.time(); n_gen = 0
    with open(edits_path, "a") as f:
        for r in cl.itertuples():
            row = int(r.row)
            if row in done:
                continue
            claim = r.claim
            rec = {"row": row, "stim_idx": int(r.stim_idx), "doc_idx": int(r.doc_idx), "pos": int(r.pos), "claim_idx": int(r.claim_idx),
                   "n_claims": int(r.n_claims), "claim": claim}
            try:
                rec["editor_raw_corrupt"] = tgt.chat_generate(CORRUPT_PROMPT.format(claim=claim), MAX_NEW)
                rec["editor_raw_paraphrase"] = tgt.chat_generate(PARA_PROMPT.format(claim=claim), MAX_NEW)
                rec["error"] = None
                n_gen += 2
            except Exception as e:
                rec.update({"editor_raw_corrupt": None, "editor_raw_paraphrase": None, "error": traceback.format_exc()})
                L.log(f"editor FAILED row {row}: {e}")
            c, cok = parse_out(rec["editor_raw_corrupt"] or "")
            p, pok = parse_out(rec["editor_raw_paraphrase"] or "")
            rec.update({"corrupt": c, "paraphrase": p, "corrupt_tags_ok": cok, "paraphrase_tags_ok": pok,
                        "corrupt_words_ok": word_ok(claim, c), "paraphrase_words_ok": word_ok(claim, p)})
            rec["edit_ok"] = bool(cok and pok and rec["corrupt_words_ok"] and rec["paraphrase_words_ok"] and c != p)
            # deterministic corruption: pool from OTHER evaluation explanations
            rng3 = np.random.default_rng(3000 + row)
            pool = [t for i, ps in cap_pool_by_stim.items() if i != r.stim_idx for t in ps]
            cd, numeric_ok = corrupt_det(claim, pool, rng3)
            rec.update({"corrupt_det": cd, "numeric_ok": numeric_ok})
            rng2 = np.random.default_rng(2000 + row)
            others = [c2 for (i2, c2) in all_claims if i2 != r.stim_idx]
            rec["offtopic"] = others[int(rng2.integers(0, len(others)))]
            f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
            done[row] = rec
            if row % 25 == 0:
                L.log(f"editor row {row} ({n_gen} gens, {(time.time()-t0)/max(1,n_gen):.1f}s each) edit_ok={rec['edit_ok']}")
    S.update(editor_wall_s=time.time() - t0, editor_n_gen=n_gen)
    tgt.free()

    # ---------------- AR scoring
    ar = L.AR()
    cache = {}

    def score(text, i):
        if text not in cache:
            cache[text] = ar.predict(text).numpy()
        return L.cos(cache[text], h20[i])

    rows = []
    t0 = time.time()
    for r in cl.itertuples():
        row = int(r.row); rec = done[row]; i = int(r.stim_idx)
        cs = claims_by_stim[i]; ci = int(r.claim_idx)
        rest = " ".join(cs[:ci] + cs[ci + 1:])
        try:
            cos_rest = score(rest, i)
            cos_z_joined = score(" ".join(cs), i)
        except Exception:
            cos_rest = cos_z_joined = float("nan")
        cos_z = float(r.cos_z); d_z = float(cl.loc[cl.row == row, "Δcos"].iloc[0])
        for et in EDIT_TYPES:
            new = rec.get(et)
            ok = {"corrupt": rec["edit_ok"], "paraphrase": rec["edit_ok"], "corrupt_det": rec["numeric_ok"], "offtopic": True}[et]
            out = {"row": row, "stim_idx": i, "claim_idx": ci, "edit_type": et, "edit_ok": bool(ok and new),
                   "cos_z": cos_z, "cos_z_joined": cos_z_joined, "cos_rest": cos_rest, "Δ_z": d_z,
                   "cos_z_edit": np.nan, "Δ_z_edit": np.nan, "error": None}
            if ok and new:
                try:
                    z_edit = " ".join(cs[:ci] + [new] + cs[ci + 1:])
                    out["cos_z_edit"] = score(z_edit, i)
                    out["Δ_z_edit"] = cos_rest - out["cos_z_edit"]
                except Exception:
                    out["error"] = traceback.format_exc()
            rows.append(out)
        if row % 50 == 0:
            L.log(f"AR row {row} forwards {ar.n_forward} ({(time.time()-t0)/max(1,ar.n_forward):.2f}s each)")
    ar.free()
    sc = pd.DataFrame(rows)
    sc.to_csv(L.OVERNIGHT / "s3_scores.csv", index=False)

    # ---------------- statistics
    def wide(et):
        s = sc[(sc.edit_type == et) & sc.edit_ok].set_index("row")
        return s
    C, P, Dd, O = wide("corrupt"), wide("paraphrase"), wide("corrupt_det"), wide("offtopic")
    acc = C.index.intersection(P.index)
    A = (C.loc[acc, "Δ_z_edit"] - C.loc[acc, "Δ_z"]); Pp = (P.loc[acc, "Δ_z_edit"] - P.loc[acc, "Δ_z"])
    clus = C.loc[acc, "stim_idx"].values
    ci_A = L.cluster_bootstrap_mean(A, clus); ci_P = L.cluster_bootstrap_mean(Pp, clus)
    ci_AP = L.cluster_bootstrap_mean(A - Pp, clus)
    k3_out = L.outcome_ci_at_or_below(ci_AP, 0.0, min_n=MIN_ACCEPTED)
    k3 = L.append_disconfirmation("S3", "K3", "CI95 of mean(A−P) ≤ 0; INCONCLUSIVE if straddles or accepted<100",
                                  f"mean A={ci_A['mean']:.5f} [{ci_A['lo']:.5f},{ci_A['hi']:.5f}]; mean P={ci_P['mean']:.5f} [{ci_P['lo']:.5f},{ci_P['hi']:.5f}]; "
                                  f"mean A−P={ci_AP['mean']:.5f} CI95=[{ci_AP['lo']:.5f},{ci_AP['hi']:.5f}] n_accepted={ci_AP['n']} n_expl={ci_AP['n_clusters']}",
                                  k3_out, "MET would mean the score does not respond to an LLM factual contradiction more than to a meaning-preserving rewording")
    accd = Dd.index.intersection(P.index)
    Ad = Dd.loc[accd, "Δ_z_edit"] - Dd.loc[accd, "Δ_z"]; Pd = P.loc[accd, "Δ_z_edit"] - P.loc[accd, "Δ_z"]
    ci_Ad = L.cluster_bootstrap_mean(Ad, Dd.loc[accd, "stim_idx"].values)
    ci_AdP = L.cluster_bootstrap_mean(Ad - Pd, Dd.loc[accd, "stim_idx"].values)
    k3d_out = L.outcome_ci_at_or_below(ci_AdP, 0.0, min_n=MIN_ACCEPTED)
    k3d = L.append_disconfirmation("S3", "K3-det", "same as K3 for deterministic corruption (reported separately, not a pre-registered kill)",
                                   f"mean A_det={ci_Ad['mean']:.5f} [{ci_Ad['lo']:.5f},{ci_Ad['hi']:.5f}]; mean A_det−P={ci_AdP['mean']:.5f} CI95=[{ci_AdP['lo']:.5f},{ci_AdP['hi']:.5f}] n={ci_AdP['n']}",
                                   k3d_out, "deterministic number/name swap instead of LLM corruption")

    # ---------------- report
    n_rows = len(cl)
    lines = ["# S3 summary — corrupted vs paraphrased claims (evaluation claims)", "",
             f"git {L.git_hash()[:8]}; settings in s3_settings.json", "", "## Editor acceptance", "",
             f"- evaluation claims: {n_rows}",
             f"- corrupt: tags parsed {np.mean([d['corrupt_tags_ok'] for d in done.values()]):.3f}, words ok {np.mean([d['corrupt_words_ok'] for d in done.values()]):.3f}",
             f"- paraphrase: tags parsed {np.mean([d['paraphrase_tags_ok'] for d in done.values()]):.3f}, words ok {np.mean([d['paraphrase_words_ok'] for d in done.values()]):.3f}",
             f"- corrupt == paraphrase: {np.mean([(d['corrupt'] == d['paraphrase']) for d in done.values()]):.3f}",
             f"- edit_ok (both accepted): {sum(d['edit_ok'] for d in done.values())} / {n_rows} = {np.mean([d['edit_ok'] for d in done.values()]):.3f}; rejection rate {1-np.mean([d['edit_ok'] for d in done.values()]):.3f}",
             f"- numeric_ok (deterministic corruption possible): {sum(d['numeric_ok'] for d in done.values())} / {n_rows}",
             f"- editor errors: {sum(d['error'] is not None for d in done.values())}", "",
             "## Primary statistics (accepted claims, paired)", "", "| statistic | mean | CI95 lo | CI95 hi | n | n_expl |", "|---|---|---|---|---|---|"]
    for name, ci in [("A = Δ_i(z*) − Δ_i(z)  [LLM corrupt]", ci_A), ("P = Δ_i(z~) − Δ_i(z)  [paraphrase]", ci_P), ("A − P", ci_AP),
                     ("A_det [deterministic corrupt]", ci_Ad), ("A_det − P", ci_AdP)]:
        lines.append(f"| {name} | {ci['mean']:.5f} | {ci['lo']:.5f} | {ci['hi']:.5f} | {ci['n']} | {ci['n_clusters']} |")
    lines += ["", "## Secondary statistics", "", "| statistic | mean | CI95 lo | CI95 hi | n |", "|---|---|---|---|---|"]
    for name, s, cl_ in [("cos(z) − cos(z*)  [corrupt]", C.cos_z - C.cos_z_edit, C.stim_idx), ("cos(z) − cos(z~)  [paraphrase]", P.cos_z - P.cos_z_edit, P.stim_idx),
                         ("cos(z) − cos(z_det)", Dd.cos_z - Dd.cos_z_edit, Dd.stim_idx), ("cos(z) − cos(z_offtopic)", O.cos_z - O.cos_z_edit, O.stim_idx),
                         ("cos(z_joined) − cos(z*)  [joined-claims baseline]", C.cos_z_joined - C.cos_z_edit, C.stim_idx),
                         ("cos(z_joined) − cos(z~)", P.cos_z_joined - P.cos_z_edit, P.stim_idx)]:
        ci = L.cluster_bootstrap_mean(s, cl_.values)
        lines.append(f"| {name} | {ci['mean']:.5f} | {ci['lo']:.5f} | {ci['hi']:.5f} | {ci['n']} |")
    lines += ["", f"- AUROC(Δ_z_edit corrupt vs Δ_z original), accepted claims: {auroc(C.loc[acc,'Δ_z_edit'], C.loc[acc,'Δ_z']):.4f}",
              f"- AUROC(Δ_z_edit paraphrase vs Δ_z original): {auroc(P.loc[acc,'Δ_z_edit'], P.loc[acc,'Δ_z']):.4f}",
              f"- AUROC(Δ_z_edit corrupt vs Δ_z_edit paraphrase): {auroc(C.loc[acc,'Δ_z_edit'], P.loc[acc,'Δ_z_edit']):.4f}",
              f"- AUROC(Δ_z_edit corrupt_det vs Δ_z original): {auroc(Dd['Δ_z_edit'], Dd['Δ_z']):.4f}",
              f"- AUROC(Δ_z_edit offtopic vs Δ_z original): {auroc(O['Δ_z_edit'], O['Δ_z']):.4f}",
              f"- fraction A > 0: {(A > 0).mean():.4f}; fraction P > 0: {(Pp > 0).mean():.4f}; fraction A > P: {(A > Pp).mean():.4f}",
              "", "## Kill test", "", f"- {k3}", f"- {k3d}", "",
              "## 10 fixed examples (accepted evaluation claims at rows 0, 16, …, 144 of the accepted list; verbatim)", ""]
    acc_list = list(acc)
    for k in range(0, 160, 16):
        if k >= len(acc_list):
            lines.append(f"(accepted list has only {len(acc_list)} entries; example {k} absent)"); continue
        row = acc_list[k]; d = done[row]
        lines += [f"### accepted #{k} (row {row}, stim {d['stim_idx']}, claim {d['claim_idx']}/{d['n_claims']}) token={df.token_str[d['stim_idx']]!r}",
                  f"- original:   {d['claim']}", f"- corrupted:  {d['corrupt']}", f"- paraphrase: {d['paraphrase']}",
                  f"- corrupt_det: {d['corrupt_det']}",
                  f"- Δ_z(original)={C.loc[row,'Δ_z']:.5f}  Δ_z*(corrupt)={C.loc[row,'Δ_z_edit']:.5f}  Δ_z~(paraphrase)={P.loc[row,'Δ_z_edit']:.5f}  "
                  f"Δ_det={(Dd.loc[row,'Δ_z_edit'] if row in Dd.index else float('nan')):.5f}  A={A.loc[row]:.5f}  P={Pp.loc[row]:.5f}", ""]
    (L.OVERNIGHT / "s3_summary.md").write_text("\n".join(lines) + "\n")
    S.finish(k3=ci_AP, k3_det=ci_AdP, n_accepted=int(len(acc)), n_forward=ar.n_forward)
    L.log("S3 done")


if __name__ == "__main__":
    main()

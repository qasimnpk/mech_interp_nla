"""S5 — prompt steering of the describer on the 40 pilot stimuli (PLAN.md round 1).

  uv run python overnight/s5_steer.py              # generate + score + summary
  uv run python overnight/s5_steer.py --summary    # rebuild summary only (after s5_judge.csv is filled)

AV + AR co-resident. Six instruction variants (fixed wording); mechanical checks on V3/V4/V5;
kill test K5 = follow_rate over V3+V4. The agent-rubric judge for V1/V2/V5 is filled by the
orchestrator into overnight/s5_judge.csv after reading s5_judge_input.md.
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

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import torch  # noqa: E402

N_PILOT = 40
MAX_NEW = 200
K5_THRESHOLD = 0.25
DEFAULT_INSTR = "The explanation consists of 2-3 text snippets describing that vector."
VARIANTS = {
    "V0": DEFAULT_INSTR,
    "V1": "The explanation consists of 2-3 text snippets describing the OPPOSITE of the semantic content of that vector.",
    "V2": "The explanation consists of 2-3 text snippets describing that vector, written in a furious, exasperated tone.",
    "V3": "The explanation consists of exactly ONE word that best describes that vector. Output nothing else inside the tags.",
    "V4": "The explanation consists of 2-3 text snippets describing that vector, written entirely in French.",
    "V5": "Answer this question about the vector, then give 1-2 text snippets: is the token this vector was taken from most likely a NOUN, VERB, or OTHER? Start the explanation with one of those three words in capitals.",
}
FRENCH = set("""le la les un une des du de et est sont a à au aux en dans sur sous pour par avec sans que qui quoi dont où ne pas plus
moins très trop bien mal ce cet cette ces celui celle ceux celles il elle ils elles nous vous je tu on me te se lui leur mon ma mes ton ta
tes son sa ses notre nos votre vos leurs y ou mais donc car ni comme si quand lorsque alors ainsi aussi encore déjà toujours jamais souvent
parfois ici là avant après pendant depuis jusque vers chez entre contre selon être avoir faire dire aller voir savoir pouvoir vouloir venir
devoir prendre donner mettre parler passer rester porter tenir trouver penser croire aimer sembler laisser montrer décrire concerne
texte mot mots phrase phrases vecteur activation contenu sémantique sens signification exemple exemples extrait extraits terme termes
nom noms verbe verbes langue langage modèle description explication cette ceci cela chose choses quelque quelques tout tous toute toutes
autre autres même mêmes grand grande petit petite nouveau nouvelle premier première dernier dernière bon bonne mauvais mauvaise
homme femme personne personnes gens temps jour jours année années monde vie fois lieu partie nombre point manière façon
peut peuvent peu beaucoup assez surtout notamment particulièrement généralement souvent probablement également
étant été sera serait seront sont était étaient fait faite faits utilisé utilisée utilisés indique indiquent représente représentent
semble suggère suggèrent liés liée lié relatif relative concernant décrit décrivent évoque évoquent référence références""".split())
FUNCTION_WORDS = set("""the a an and or but of to in on at by for with from as is are was were be been being it its this that these those
he she they we you i his her their our your not no do does did have has had will would can could may might shall should than then""".split())
CAP_WORDS = {"NOUN", "VERB", "OTHER"}

S = L.Settings("s5", n_pilot=N_PILOT, max_new_tokens=MAX_NEW, decoding="greedy", k5_threshold=K5_THRESHOLD,
               variants=VARIANTS, french_stoplist_n=len(FRENCH), function_words_n=len(FUNCTION_WORDS),
               checks={"V3": "word count of explanation == 1", "V4": "fraction of ASCII-letter tokens in French stoplist >= 0.15",
                       "V5": "first word in {NOUN,VERB,OTHER}; agreement with content-word rule (alphabetic token_str not in function list)"})


def mech_check(variant: str, expl: str, token_str: str):
    if variant == "V3":
        return {"mech_pass": len(expl.split()) == 1}
    if variant == "V4":
        toks = re.findall(r"[A-Za-zÀ-ÿ]+", expl)
        fr = float(np.mean([t.lower() in FRENCH for t in toks])) if toks else 0.0
        return {"mech_pass": fr >= 0.15, "french_frac": fr}
    if variant == "V5":
        first = expl.strip().split()[0].strip(".,:;!?\"'*") if expl.strip() else ""
        first = first.upper() if first.upper() in CAP_WORDS else first
        tok = token_str.strip()
        content = tok.isalpha() and tok.lower() not in FUNCTION_WORDS
        pred_content = first in {"NOUN", "VERB"}
        return {"mech_pass": first in CAP_WORDS, "v5_word": first, "token_is_content_word": bool(content),
                "v5_agrees_content_rule": bool(first in CAP_WORDS and pred_content == content)}
    return {"mech_pass": None}


def summary(outs: pd.DataFrame, rc: pd.DataFrame, df: pd.DataFrame, k5_line: str):
    judge_path = L.OVERNIGHT / "s5_judge.csv"
    judge = pd.read_csv(judge_path) if judge_path.exists() else None
    lines = ["# S5 summary — prompt steering on the 40 pilot stimuli", "", f"git {L.git_hash()[:8]}; settings in s5_settings.json", "",
             "Judge columns (`followed`, `same_referent`) are an LLM-as-judge score produced by the orchestrating agent under the fixed rubric in PLAN.md S5, read side by side with V0; they are not human labels.", "",
             "| variant | mech pass rate | judge followed | judge same_referent | mean cos_Vk | mean cos_Vk − cos_V0 | median cos_Vk − cos_V0 | parse_ok | cjk | mean n_tokens |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    v0 = rc[rc.variant == "V0"].set_index("stim_idx").cos
    for v in VARIANTS:
        o = outs[outs.variant == v]; r = rc[rc.variant == v].set_index("stim_idx")
        mech = o.mech_pass.dropna()
        mp = f"{mech.astype(float).mean():.3f} (n={len(mech)})" if len(mech) else "—"
        jf = js = "—"
        if judge is not None and v in set(judge.variant):
            jv = judge[judge.variant == v]
            jf = f"{jv.followed.mean():.3f} (n={len(jv)})"; js = f"{jv.same_referent.mean():.3f}"
        d = (r.cos - v0.reindex(r.index))
        lines.append(f"| {v} | {mp} | {jf} | {js} | {r.cos.mean():.4f} | {d.mean():.4f} | {d.median():.4f} | {o.parse_ok.mean():.3f} | {o.cjk.mean():.3f} | {o.n_tokens.mean():.1f} |")
    v4 = outs[outs.variant == "V4"]; v5 = outs[outs.variant == "V5"]
    lines += ["", f"- V4 mean french_frac: {v4.french_frac.mean():.3f}",
              f"- V5 first-word distribution: {v5.v5_word.value_counts().to_dict()}; agreement with content-word rule among mech-pass items: {v5[v5.mech_pass == True].v5_agrees_content_rule.mean():.3f} (n={int((v5.mech_pass == True).sum())}); token_is_content_word rate: {v5.token_is_content_word.mean():.3f}",
              f"- V3 explanations word-count distribution: {outs[outs.variant == 'V3'].explanation.map(lambda s: len(str(s).split())).value_counts().sort_index().to_dict()}",
              "", "## Kill test", "", f"- {k5_line}", "", "## Verbatim examples: positions 0, 7, 19, 33", ""]
    for i in [0, 7, 19, 33]:
        s = df.iloc[i]
        lines += [f"### stim {i} (doc {s.doc_idx}, pos {s.pos}) token={s.token_str!r}", "",
                  "context: " + json.dumps(s.context_left_64) + " [[" + json.dumps(s.token_str) + "]] " + json.dumps(s.context_right_16), ""]
        for v in VARIANTS:
            o = outs[(outs.variant == v) & (outs.stim_idx == i)].iloc[0]
            c = rc[(rc.variant == v) & (rc.stim_idx == i)].cos.iloc[0]
            lines += [f"**{v}** (cos={c:.3f}, parse_ok={o.parse_ok}, mech={o.mech_pass}):", "```", str(o.explanation if o.parse_ok else o.raw_generation), "```"]
        lines.append("")
    (L.OVERNIGHT / "s5_summary.md").write_text("\n".join(lines) + "\n")


def main():
    df, acts = L.load_stimuli()
    h20 = acts["h20"]
    out_path = L.OVERNIGHT / "s5_outputs.jsonl"
    rc_path = L.OVERNIGHT / "s5_recon.csv"
    if "--summary" in sys.argv:
        outs = pd.read_json(out_path, lines=True); rc = pd.read_csv(rc_path)
        k5_line = [l for l in (L.OVERNIGHT / "DISCONFIRMATION.md").read_text().splitlines() if "  K5  " in l][-1]
        summary(outs, rc, df, k5_line); L.log("S5 summary rebuilt"); return

    av = L.AV()
    base = av.default_prompt
    assert DEFAULT_INSTR in base, "default instruction sentence not found in AV template"
    prompts = {v: base.replace(DEFAULT_INSTR, ins) for v, ins in VARIANTS.items()}
    assert prompts["V0"] == base
    S.update(prompts_verbatim=prompts)
    for v in VARIANTS:
        av.prompt(prompts[v])  # runs the injection-position asserts for every variant
    recs = []
    done = set()
    if out_path.exists():
        for line in out_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line); recs.append(r); done.add((r["variant"], r["stim_idx"]))
    t0 = time.time(); n_gen = 0
    with open(out_path, "a") as f:
        for v in VARIANTS:
            for i in range(N_PILOT):
                if (v, i) in done:
                    continue
                rec = {"stim_idx": i, "doc_idx": int(df.doc_idx[i]), "pos": int(df.pos[i]), "token_str": df.token_str[i], "variant": v}
                try:
                    rec.update(av.verbalize(torch.from_numpy(h20[i]), prompts[v], MAX_NEW)); rec["error"] = None; n_gen += 1
                except Exception as e:
                    rec.update({"raw_generation": None, "explanation": "", "parse_ok": False, "cjk": False, "n_tokens": 0, "gen_s": float("nan"), "error": traceback.format_exc()})
                    L.log(f"AV FAILED {v} {i}: {e}")
                rec.update(mech_check(v, rec["explanation"] or "", rec["token_str"]))
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush(); recs.append(rec)
                L.log(f"{v} {i}/{N_PILOT} n_tok={rec['n_tokens']} {rec['gen_s']:.1f}s parse_ok={rec['parse_ok']} mech={rec.get('mech_pass')}")
    S.update(av_wall_s=time.time() - t0, av_n_generated=n_gen)
    outs = pd.DataFrame(recs)
    # K5 first (before AR scoring)
    k = outs[outs.variant.isin(["V3", "V4"])]
    ci = L.cluster_bootstrap_mean(k.mech_pass.astype(float), k.stim_idx)
    if ci["n"] < 2 * N_PILOT:
        out = "INCONCLUSIVE"
    elif ci["hi"] < K5_THRESHOLD:
        out = "MET"
    elif ci["lo"] >= K5_THRESHOLD:
        out = "NOT MET"
    else:
        out = "INCONCLUSIVE"
    k5_line = L.append_disconfirmation("S5", "K5", f"follow_rate(V3+V4 mechanical) < {K5_THRESHOLD}",
                                       f"follow_rate={ci['mean']:.4f} CI95=[{ci['lo']:.4f},{ci['hi']:.4f}] n={ci['n']} (V3 {k[k.variant=='V3'].mech_pass.astype(float).mean():.3f}, V4 {k[k.variant=='V4'].mech_pass.astype(float).mean():.3f})",
                                       out, "MET would mean the describer ignores instruction text at inference time")
    ar = L.AR()
    rows = []
    for r in recs:
        text = r["explanation"] if r["parse_ok"] else (r["raw_generation"] or "")
        try:
            c = L.cos(ar.predict(text).numpy(), h20[r["stim_idx"]])
        except Exception:
            c = float("nan")
        rows.append({"stim_idx": r["stim_idx"], "doc_idx": r["doc_idx"], "pos": r["pos"], "variant": r["variant"], "cos": c})
    ar.free(); av.free()
    rc = pd.DataFrame(rows)
    v0 = rc[rc.variant == "V0"].set_index("stim_idx").cos
    rc["cos_minus_V0"] = rc.cos.values - v0.reindex(rc.stim_idx).values
    rc.to_csv(rc_path, index=False)
    # judge input for the orchestrator
    jl = ["# S5 judge input — V0 next to V1/V2/V5 per pilot position (fill overnight/s5_judge.csv)", ""]
    for i in range(N_PILOT):
        jl.append(f"## stim {i} token={df.token_str[i]!r}")
        for v in ["V0", "V1", "V2", "V5"]:
            o = outs[(outs.variant == v) & (outs.stim_idx == i)].iloc[0]
            jl.append(f"[{v}] {(o.explanation if o.parse_ok else o.raw_generation)!r}")
        jl.append("")
    (L.OVERNIGHT / "s5_judge_input.md").write_text("\n".join(jl) + "\n")
    summary(outs, rc, df, k5_line)
    S.finish(k5=ci)
    L.log("S5 done")


if __name__ == "__main__":
    main()

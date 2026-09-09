"""r4_lib — round-4 helpers (PLAN.md "Round 4 stages"). `nla_lib.py` is imported unchanged (read-only).

Provides: verbalize_sampled / verbalize_greedy (AV generation with the review-pack fields), ar_score,
split_claims_quote_aware, prefix/suffix substitution with the binding asserts, the deletion baseline,
advisory lexical checks, dist_block, cluster-bootstrap wrappers, the per-stage progress file, the
agent-judgement task/output protocol (AWAITING_AGENT_TASKS / MISSING exits), the B1 context builder,
and the wikitext prefix decoder. Import this module before torch (it imports nla_lib first).
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from overnight import nla_lib as L  # noqa: E402  (sets MPS env first)

import numpy as np  # noqa: E402
import torch  # noqa: E402

AGENT_MODEL = "claude-fable-5-1"
OVERNIGHT = L.OVERNIGHT
OUT = L.OUT
ROUND4_CAPS_MIN = {"V0": 30, "B1": 150, "A1": 210, "K1": 45, "D1": 60}
MAX_FAILURES = 5
INJECTION_NORM = 150.0


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def runlog(stage: str, event: str, detail: str) -> None:
    with open(OVERNIGHT / "RUNLOG.md", "a") as f:
        f.write(f"{now()}  {stage}  {event}  {detail}\n")


# ----------------------------------------------------------------------------- jsonl
def read_jsonl(path: Path) -> list[dict]:
    if not Path(path).exists():
        return []
    out = []
    for line in Path(path).read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def append_jsonl(path: Path, obj: dict) -> None:
    with open(path, "a") as f:
        f.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")
        f.flush()


# ----------------------------------------------------------------------------- AV
def _eos_ids(av) -> set[int]:
    e = av.model.generation_config.eos_token_id
    if e is None:
        e = av.tok.eos_token_id
    return set(e if isinstance(e, (list, tuple)) else [e])


def _av_common(av, vec: torch.Tensor):
    ids, inj_pos, base = av.prompt(None)
    v = vec.float()
    v_scaled = (v / v.norm().clamp_min(1e-12) * av.scale).to(L.DEVICE, torch.bfloat16)
    embeds = base.clone()
    embeds[0, inj_pos] = v_scaled
    return ids, inj_pos, embeds


def _av_pack(av, ids, inj_pos, out, t0, decoding, seed, temperature) -> dict:
    raw = av.tok.decode(out[0], skip_special_tokens=True)  # inputs_embeds -> only new tokens
    expl, ok = L.parse_explanation(raw)
    last = int(out[0, -1])
    return {"prompt_ids_len": int(ids.shape[1]), "marker_pos": int(inj_pos), "injection_norm": float(av.scale),
            "decoding": decoding, "temperature": temperature, "seed": seed,
            "raw_generation": raw, "explanation": expl, "parse_ok": ok, "cjk": L.has_cjk(raw),
            "n_tokens": int(out.shape[1]), "gen_s": time.time() - t0,
            "ended_with_close_tag": raw.rstrip().endswith("</explanation>"),
            "ended_with_eos": last in _eos_ids(av), "last_token_id": last}


def verbalize_sampled(av, vec: torch.Tensor, seed: int, temperature: float = 1.0, max_new_tokens: int = 200) -> dict:
    """Body of AV.verbalize with torch.manual_seed(seed) immediately before sampled generation (T=1, top_p=1, top_k=0)."""
    ids, inj_pos, embeds = _av_common(av, vec)
    t0 = time.time()
    torch.manual_seed(int(seed))
    with torch.inference_mode():
        out = av.model.generate(inputs_embeds=embeds, attention_mask=torch.ones_like(ids),
                                max_new_tokens=max_new_tokens, do_sample=True, temperature=float(temperature),
                                top_p=1.0, top_k=0, pad_token_id=av.tok.pad_token_id or av.tok.eos_token_id)
    return _av_pack(av, ids, inj_pos, out, t0, "sampled", int(seed), float(temperature))


def verbalize_greedy(av, vec: torch.Tensor, max_new_tokens: int = 200) -> dict:
    """AV.verbalize (greedy) with the same review-pack fields as verbalize_sampled."""
    ids, inj_pos, embeds = _av_common(av, vec)
    t0 = time.time()
    with torch.inference_mode():
        out = av.model.generate(inputs_embeds=embeds, attention_mask=torch.ones_like(ids),
                                max_new_tokens=max_new_tokens, do_sample=False,
                                pad_token_id=av.tok.pad_token_id or av.tok.eos_token_id)
    return _av_pack(av, ids, inj_pos, out, t0, "greedy", None, 0.0)


# ----------------------------------------------------------------------------- AR
def ar_score(ar, explanation: str, h) -> dict:
    """One AR.predict; returns cos / mse / pred_norm and the raw fp32 prediction for reuse against a second activation."""
    pred = ar.predict(explanation).numpy()
    c = L.cos(pred, h)
    return {"cos": c, "mse": L.mse_from_cos(c), "pred_norm": float(np.linalg.norm(pred)), "pred": pred}


def ar_input_tokens(ar, explanation: str) -> int:
    return int(ar.tok(ar.template.format(explanation=explanation), add_special_tokens=True, return_tensors="pt")["input_ids"].shape[1])


def movement(pred_a, pred_b) -> float:
    """Reconstruction movement V(z, z0) = 1 − cos(AR(z), AR(z0))."""
    return 1.0 - L.cos(pred_a, pred_b)


# ----------------------------------------------------------------------------- claim splitting (S2 rule + quote awareness)
SENT_RE = re.compile(r"(?<=[.!?])\s+")
MARKER_RE = re.compile(r"^\s*(\d+[.)]|[-*•])\s*")
MIN_WORDS = 3
SNIPPET_RE_B1 = re.compile(r"final token|last token|expecting|continu", re.I)
SNIPPET_RE_A1 = re.compile(r"final token|last token|current token|expecting|continu|followed by|next (word|token)", re.I)


def split_claims_quote_aware(text: str) -> list[str]:
    """s2_deletion.split_claims with one extra rule: never split at a sentence end inside an open double quote
    (odd count of '"' before the split point within the line)."""
    out = []
    for line in (text or "").split("\n"):
        cuts = [m.start() for m in SENT_RE.finditer(line) if line[:m.start()].count('"') % 2 == 0]
        pieces, prev = [], 0
        for c in cuts:
            pieces.append(line[prev:c]); prev = c
        pieces.append(line[prev:])
        for piece in pieces:
            p = MARKER_RE.sub("", piece.strip()).strip()
            if len(p.split()) >= MIN_WORDS:
                out.append(p)
    return out


def sentence_span(E: str, sentence: str) -> tuple[int, int, bool]:
    """Character span [a, b) of the first exact occurrence; dup=True if the sentence occurs more than once."""
    a = E.find(sentence)
    if a < 0:
        return -1, -1, False
    dup = E.find(sentence, a + 1) >= 0
    return a, a + len(sentence), dup


def substitute(E: str, a: int, b: int, realization: str) -> str:
    """E' = E[:a] + realization + E[b:] with the binding prefix / suffix asserts."""
    E2 = E[:a] + realization + E[b:]
    assert E2[:a] == E[:a], "prefix assert failed"
    assert E2[len(E2) - (len(E) - b):] == E[b:], "suffix assert failed"
    return E2


def deletion_text(E: str, a: int, b: int) -> str:
    """Deletion baseline E[:a] + E[b:] with collapse of double spaces / space before punctuation (exact bytes are recorded by the caller)."""
    E2 = E[:a] + E[b:]
    E2 = re.sub(r"[ \t]{2,}", " ", E2)
    E2 = re.sub(r" +([.,;:!?])", r"\1", E2)
    E2 = re.sub(r"\n[ \t]+", "\n", E2)
    E2 = re.sub(r"[ \t]+\n", "\n", E2)
    return E2.strip()


# ----------------------------------------------------------------------------- advisory lexical checks
NUM_WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen",
             "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
             "sixty", "seventy", "eighty", "ninety", "hundred"]
NUM_WORD_SET = set(NUM_WORDS)
POLARITY = {"not", "n't", "no", "never", "none", "neither", "nor"}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'\-]*|\d[\d.,]*")


def _words(text: str) -> list[str]:
    return WORD_RE.findall(text or "")


def cap_tokens(text: str, skip_initial: bool) -> set[str]:
    ws = _words(text)
    out = set()
    for i, w in enumerate(ws):
        if i == 0 and skip_initial:
            continue
        if w[0].isupper():
            out.add(w.strip("'-"))
    return out


def numbers_of(text: str) -> list[str]:
    out = []
    for w in _words(text):
        wl = w.lower().replace("'", "")
        if w[0].isdigit():
            out.append(w.rstrip(".,"))
        else:
            for part in wl.split("-"):
                if part in NUM_WORD_SET:
                    out.append(part)
    return sorted(out)


def polarity_count(text: str) -> int:
    t = (text or "").lower()
    return sum(len(re.findall(r"\b" + re.escape(p) + r"\b" if p != "n't" else r"n't\b", t)) for p in POLARITY)


def lexical_checks(candidate: str, realization: str, tok=None) -> dict:
    d = {"names_kept": cap_tokens(candidate, True) <= cap_tokens(realization, False),
         "numbers_kept": numbers_of(candidate) == numbers_of(realization),
         "polarity_kept": polarity_count(candidate) == polarity_count(realization)}
    if tok is not None:
        nc = len(tok(candidate, add_special_tokens=False)["input_ids"]); nr = len(tok(realization, add_special_tokens=False)["input_ids"])
        d["len_ratio"] = nr / max(1, nc)
    else:
        d["len_ratio"] = len(_words(realization)) / max(1, len(_words(candidate)))
    d["len_ok"] = 0.75 <= d["len_ratio"] <= 1.25
    return d


def norm_text(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


# ----------------------------------------------------------------------------- statistics
DIST_KEYS = ["n", "mean", "sd", "var", "min", "p5", "p10", "p25", "p50", "p75", "p90", "p95", "max"]
DIST_HEADER = ["| column | n | mean | sd | var | min | p5 | p10 | p25 | p50 | p75 | p90 | p95 | max |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]


def dist_block(values) -> dict:
    a = np.asarray(list(values), dtype=np.float64)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return {k: (0 if k == "n" else float("nan")) for k in DIST_KEYS}
    sd = float(a.std(ddof=1)) if len(a) > 1 else float("nan")
    q = np.percentile(a, [5, 10, 25, 50, 75, 90, 95])
    return {"n": int(len(a)), "mean": float(a.mean()), "sd": sd, "var": sd * sd if not np.isnan(sd) else float("nan"),
            "min": float(a.min()), "p5": q[0], "p10": q[1], "p25": q[2], "p50": q[3], "p75": q[4], "p90": q[5], "p95": q[6], "max": float(a.max())}


def dist_row(name: str, values, d: int = 5) -> str:
    b = dist_block(values)
    return f"| {name} | {b['n']} | " + " | ".join(f"{b[k]:.{d}f}" for k in DIST_KEYS[1:]) + " |"


def ci(values, clusters) -> dict:
    """Cluster bootstrap by the stage's cluster unit (1000 draws, seed 0)."""
    return L.cluster_bootstrap_mean(values, clusters, n_boot=1000, seed=0)


def fmt_ci(c: dict, d: int = 5) -> str:
    return f"{c['mean']:.{d}f} [{c['lo']:.{d}f},{c['hi']:.{d}f}] n={c['n']} k={c['n_clusters']}"


def outcome(c: dict, min_n: int | None = None) -> str:
    """MET if CI entirely ≤ 0; NOT MET if entirely > 0; INCONCLUSIVE otherwise or if n < min_n."""
    return L.outcome_ci_at_or_below(c, 0.0, min_n=min_n)


# ----------------------------------------------------------------------------- progress file
class Progress:
    """<stage>_progress.json: cumulative minutes (script + judgement), phase, completed / incomplete counts, failures, cut rules."""

    def __init__(self, stage: str):
        self.stage = stage
        self.path = OVERNIGHT / f"{stage}_progress.json"
        self.cap = ROUND4_CAPS_MIN.get(stage)
        if self.path.exists():
            self.d = json.loads(self.path.read_text())
        else:
            self.d = {"stage": stage, "cap_min": self.cap, "cumulative_minutes": 0.0, "script_minutes": 0.0, "judgement_minutes": 0.0,
                      "phase": None, "completed": {}, "incomplete": {}, "failures": 0, "cut_rules_applied": [], "blocked": None,
                      "awaiting": None, "invocations": [], "judgement_log": []}
        self.t0 = time.time()
        self.d["invocations"].append({"start": now(), "argv": sys.argv[1:]})
        self.save()

    def save(self):
        self.d["cumulative_minutes"] = float(self.d["script_minutes"] + self.d["judgement_minutes"])
        self.d["last_saved"] = now()
        self.path.write_text(json.dumps(self.d, indent=2, ensure_ascii=False, default=str))

    def tick(self):
        """Fold this invocation's elapsed wall-clock into script_minutes (called at every checkpoint and exit)."""
        el = (time.time() - self.t0) / 60
        self.d["script_minutes"] += el
        self.t0 = time.time()
        self.d["invocations"][-1]["end"] = now()
        self.save()

    def set_phase(self, phase: str):
        self.d["phase"] = phase; self.tick()

    def completed(self, unit: str, n: int):
        self.d["completed"][unit] = int(n); self.tick()

    def incomplete(self, unit, n):
        self.d["incomplete"][unit] = n; self.tick()

    def fail(self, detail: str):
        self.d["failures"] += 1
        self.d.setdefault("failure_log", []).append({"ts": now(), "detail": detail[-2000:]})
        self.tick()

    def add_cut_rule(self, rule: str):
        if rule not in self.d["cut_rules_applied"]:
            self.d["cut_rules_applied"].append(rule)
        self.tick()

    @property
    def minutes(self) -> float:
        self.tick(); return float(self.d["cumulative_minutes"])

    def over_cap(self) -> bool:
        return self.cap is not None and self.minutes >= self.cap

    def over_failures(self) -> bool:
        return self.d["failures"] >= MAX_FAILURES

    def block(self, reason: str):
        self.d["blocked"] = {"ts": now(), "reason": reason}; self.tick()

    # -- judgement timing: AWAITING exit stamps awaiting_since; the resuming invocation folds (now − since) into judgement_minutes
    def awaiting(self, phase: str, path: str, n: int, kind: str):
        if not self.d.get("awaiting") or self.d["awaiting"].get("phase") != phase:
            self.d["awaiting"] = {"phase": phase, "file": str(path), "n": n, "since": now(), "since_epoch": time.time()}
        self.d["awaiting"]["last_exit"] = kind; self.d["awaiting"]["last_exit_ts"] = now()
        self.tick()

    def resume_judgement(self, phase: str, n: int, types: dict) -> float:
        aw = self.d.get("awaiting")
        mins = 0.0
        if aw and aw.get("phase") == phase:
            mins = (time.time() - float(aw["since_epoch"])) / 60
            self.d["judgement_minutes"] += mins
            self.d["judgement_log"].append({"phase": phase, "n_tasks": n, "types": types, "minutes": mins, "since": aw["since"], "until": now()})
            self.d["awaiting"] = None
        self.tick()
        return mins


# ----------------------------------------------------------------------------- agent-judgement protocol
TASK_INSTRUCTIONS = {
    "label": ("Judge the sentence against the passage alone, not against world knowledge. `entailed` = every checkable proposition in the "
              "sentence is stated by or follows necessarily from the passage. `contradicted` = at least one checkable proposition is denied by "
              "the passage. `undetermined` = the passage neither establishes nor denies it (including claims about format, genre, what comes "
              "next, or the model's cognition). Quote the decisive passage span verbatim as evidence."),
    "equiv": ("Do the two sentences state exactly the same proposition — the same entities, quantities, polarity, modality, time and "
              "attribution — with no fact added, removed or weakened? Answer Yes or No."),
    "rewrite": ("light1, light2: small changes in wording or word order only; keep every name, number, date, place, polarity, modality, tense "
                "and attribution exactly the same; length within about 25% of the original. aggr1, aggr2: substantially different syntax and "
                "vocabulary, exactly the same proposition at the same level of specificity; every name, number, date, place, polarity, "
                "modality, tense and attribution unchanged. Members of a pair must differ after whitespace/case normalisation; if a second "
                "distinct faithful rendering is not possible, repeat the first and set dup_realization=True."),
    "detail_sub": ("Change exactly ONE detail that is not a person's or place's name — a number, a quantity, an event, an attribute, a date or an "
                   "outcome — to a clearly different, same-topic value; keep every other word identical."),
    "relation_rev": ("If the sentence asserts an ordered relation between two parties or events (who did what to whom, which came first, which "
                     "contains which), exchange the roles or the order keeping every other word identical; otherwise output NONE."),
    "negation": "Negate the same proposition without changing any of its arguments (add or remove a single negation such as 'not' or 'no').",
    "correction": ("The sentence makes a claim the passage contradicts. Change only the incorrect fact to the value the passage supports; keep "
                   "every other word identical."),
    "fact_swap": "Rewrite the sentence so that it asserts the other meaning, changing only the words that carry that fact and nothing else.",
    "slot_verify": "Decide whether the sentence itself asserts the target fact, as opposed to merely mentioning the names, numbers or words involved.",
    "edit_check": ("Does the edit change exactly one checkable fact and leave every other proposition, name, number and qualifier unchanged? "
                   "Answer Yes or No and name the changed fact."),
}
OUTPUT_SCHEMA = {  # required output fields and allowed values (None = free text); NONE allowed where the plan says so
    "label": {"label": {"entailed", "contradicted", "undetermined"}, "evidence": None, "reason": None},
    "equiv": {"answer": {"Yes", "No"}, "reason": None},
    "rewrite": {"light1": None, "light2": None, "aggr1": None, "aggr2": None},
    "detail_sub": {"text": None}, "relation_rev": {"text": None}, "negation": {"text": None},
    "correction": {"text": None}, "fact_swap": {"text": None},
    "slot_verify": {"asserts": None, "other_content": None},  # allowed values are task-specific (A/B/neither or yes/no)
    "edit_check": {"one_fact": {"Yes", "No"}, "changed": None},
}


def tasks_path(stage: str, phase: str) -> Path:
    return OVERNIGHT / f"{stage}_agent_tasks_{phase}.jsonl"


def outputs_path(stage: str, phase: str) -> Path:
    return OVERNIGHT / f"{stage}_agent_outputs_{phase}.jsonl"


def validate_output(task: dict, out: dict) -> str | None:
    """Return None if valid, else a reason."""
    if not isinstance(out, dict):
        return "output not an object"
    schema = OUTPUT_SCHEMA[task["type"]]
    if task["type"] == "rewrite" and task["inputs"].get("fields"):
        schema = {k: None for k in task["inputs"]["fields"]}  # V0 cut rule A1(a): only the requested realizations
    for k, allowed in schema.items():
        if k not in out:
            return f"missing field {k}"
        v = out[k]
        if allowed is not None and v not in allowed:
            return f"field {k}={v!r} not in {sorted(allowed)}"
        if allowed is None and not isinstance(v, str):
            return f"field {k} not a string"
    if task["type"] == "slot_verify":
        allowed = set(task["inputs"].get("allowed_values", ["A", "B", "neither"]))
        if out["asserts"] not in allowed:
            return f"asserts={out['asserts']!r} not in {sorted(allowed)}"
    if task["type"] == "rewrite":
        for k in (task["inputs"].get("fields") or ("light1", "light2", "aggr1", "aggr2")):
            if not out[k].strip():
                return f"empty {k}"
    if task["type"] in ("detail_sub", "relation_rev", "negation", "correction", "fact_swap") and not out["text"].strip():
        return "empty text"
    return None


def require_outputs(stage: str, phase: str, tasks: list[dict], progress: Progress) -> dict[str, dict]:
    """Write the task file if absent (never edit an existing one), read the outputs, validate, and either return
    {task_id: output_object} or print AWAITING_AGENT_TASKS / MISSING and exit 0 (normal transitions)."""
    tp, op = tasks_path(stage, phase), outputs_path(stage, phase)
    ids = [t["task_id"] for t in tasks]
    assert len(ids) == len(set(ids)), "duplicate task ids"
    if tp.exists():
        existing = [t["task_id"] for t in read_jsonl(tp)]
        assert existing == ids, f"task file {tp.name} exists with different task ids; never edited — refusing"
    else:
        with open(tp, "w") as f:
            for t in tasks:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        L.log(f"wrote {len(tasks)} tasks to {tp.name}")
    if len(tasks) == 0:
        return {}
    by_id = {t["task_id"]: t for t in tasks}
    outs, dup = {}, []
    for o in read_jsonl(op):
        tid = o.get("task_id")
        if tid in outs:
            dup.append(tid)
        outs[tid] = o  # last occurrence wins; duplicates are recorded
    missing, invalid = [], {}
    for tid in ids:
        if tid not in outs:
            missing.append(tid); continue
        why = validate_output(by_id[tid], outs[tid].get("output"))
        if why:
            invalid[tid] = why
    types = {}
    for t in tasks:
        types[t["type"]] = types.get(t["type"], 0) + 1
    if not outs:
        progress.awaiting(phase, op.name, len(tasks), "AWAITING")
        print(f"AWAITING_AGENT_TASKS {tp} {len(tasks)}", flush=True)
        sys.exit(0)
    if missing or invalid:
        progress.awaiting(phase, op.name, len(tasks), "MISSING")
        bad = missing + list(invalid)
        print(f"MISSING {len(bad)} task_ids: " + ", ".join(bad[:60]) + (" …" if len(bad) > 60 else ""), flush=True)
        for tid, why in list(invalid.items())[:60]:
            print(f"  invalid {tid}: {why}", flush=True)
        sys.exit(0)
    mins = progress.resume_judgement(phase, len(tasks), types)
    if mins > 0:
        runlog(stage, "agent-tasks", f"{phase} {json.dumps(types)} n={len(tasks)} {mins:.1f} min (orchestrator judgement, wall-clock between AWAITING and validation); dup_outputs={len(dup)}")
    return {tid: outs[tid] for tid in ids}


def _code_lines(src: str) -> list[str]:
    """Source lines with comments and string literals blanked (so the check sees code only)."""
    import io
    import tokenize
    lines = src.splitlines()
    masks = [bytearray(len(l)) for l in lines]
    skip = {tokenize.COMMENT, tokenize.STRING} | {getattr(tokenize, n) for n in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END") if hasattr(tokenize, n)}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type not in skip:
                continue
            (sl, sc), (el, ec) = tok.start, tok.end
            for ln in range(sl, el + 1):
                a = sc if ln == sl else 0
                b = ec if ln == el else len(lines[ln - 1])
                for k in range(a, min(b, len(lines[ln - 1]))):
                    masks[ln - 1][k] = 1
    except tokenize.TokenError:
        pass
    return ["".join(" " if masks[i][k] else ch for k, ch in enumerate(l)) for i, l in enumerate(lines)]


def assert_no_av_model_calls(files: list[Path]) -> dict:
    """V0 check (6): no `.model(` / `.model.generate(` call on an AV object outside verbalize* (comments and strings ignored);
    returns per-file line hits (must be empty)."""
    hits = {}
    for f in files:
        f = Path(f)
        if not f.exists():
            continue
        for i, line in enumerate(_code_lines(f.read_text()), 1):
            if re.search(r"\bav\.model\(|\bAV\.model\(|self\.model\.generate\(|av\.model\.generate\(", line):
                if f.name == "r4_lib.py" and "av.model.generate(inputs_embeds" in line:
                    continue
                hits.setdefault(f.name, []).append(i)
    return hits


# ----------------------------------------------------------------------------- wikitext prefixes
def wikitext_train():
    from datasets import load_dataset
    return load_dataset("EleutherAI/wikitext_document_level", "wikitext-2-raw-v1")["train"]


def stimulus_prefix(tok, ds, doc_idx: int, pos: int, max_len: int = 512) -> tuple[str, list[int]]:
    """Visible prefix tokens 0..pos of a round-1 stimulus (page truncated to 512 tokens as in S0)."""
    ids = tok(ds[int(doc_idx)]["page"], add_special_tokens=False)["input_ids"][:max_len]
    return tok.decode(ids[:pos + 1]), ids[:pos + 1]


# ----------------------------------------------------------------------------- B1 contexts (frozen in PLAN.md)
PREAMBLE = ("The following entry was copied from the archive without changes. It was checked once for completeness and once for "
            "accuracy, and nothing in it was altered.")
FILLER2 = "The entry is reproduced in full below."
END_SENTENCE = "The record ends here."
F2_KEYS = ["before", "after", "earlier", "later", "first", "simultaneous", "same time"]
F4_KEYS = ["success", "failure", "approval", "rejection", "granted", "denied"]


def b1_pairs() -> list[dict]:
    P = []

    def add(family, template, filling, slot_type, background, factA, factB, meanA, meanB, keywords, name_overlap=False):
        P.append({"pair_id": f"F{family}T{template}f{filling}", "family": family, "template": template, "filling": filling,
                  "split": "dev" if filling == 0 else "eval", "slot_type": slot_type, "background": background,
                  "fact_A": factA, "fact_B": factB, "meaning_A": meanA, "meaning_B": meanB, "keywords": keywords,
                  "name_overlap": name_overlap})

    # Family 1 (entity / recipient)
    for k, (n1, n2, obj) in enumerate([("Mira", "Jonas", "parcel"), ("Lena", "Omar", "envelope"), ("Priya", "Tomas", "crate"),
                                       ("Farah", "Niko", "ledger"), ("Ines", "Ravi", "sample")]):
        bg = f"The dispatch log lists {n1} and {n2} as the two possible recipients. Exactly one person received the {obj}."
        add(1, 1, k, "entity", bg, f"The {obj} was delivered to {n1}, not {n2}.", f"The {obj} was delivered to {n2}, not {n1}.",
            f"The {obj} was delivered to {n1}.", f"The {obj} was delivered to {n2}.", [n1, n2], name_overlap=(k == 1))
    for k, (n1, n2, verb, dev) in enumerate([("Lena", "Omar", "calibrated", "sensor"), ("Mira", "Jonas", "calibrated", "scale"),
                                             ("Sela", "Dario", "serviced", "pump"), ("Priya", "Tomas", "inspected", "valve"),
                                             ("Farah", "Niko", "calibrated", "meter")]):
        bg = f"The laboratory log lists {n1} and {n2} as the two technicians on duty. Exactly one technician {verb} the {dev}."
        add(1, 2, k, "entity", bg, f"{n1} {verb} the {dev}; {n2} did not.", f"{n2} {verb} the {dev}; {n1} did not.",
            f"{n1} {verb} the {dev}.", f"{n2} {verb} the {dev}.", [n1, n2], name_overlap=(k == 1))
    # Family 2 (relation / order)
    for k, (n1, n2) in enumerate([("Mira", "Jonas"), ("Lena", "Omar"), ("Priya", "Tomas"), ("Farah", "Niko"), ("Ines", "Ravi")]):
        bg = f"The access log records one arrival by {n1} and one by {n2}. Their arrival times were different."
        add(2, 1, k, "detail", bg, f"{n1} arrived before {n2}.", f"{n2} arrived before {n1}.",
            f"{n1} arrived before {n2}.", f"{n2} arrived before {n1}.", F2_KEYS + [n1, n2, "arrival", "arrived"], name_overlap=(k == 1))
    f2t2 = [("warehouse log", "one shipment arrival and one inspection", "The shipment arrived before the inspection began.",
             "The inspection began before the shipment arrived.", ["shipment", "inspection"]),
            ("clinic log", "one sample delivery and one analysis", "The sample was delivered before the analysis began.",
             "The analysis began before the sample was delivered.", ["sample", "analysis"]),
            ("garage log", "one repair and one road test", "The repair was completed before the road test began.",
             "The road test began before the repair was completed.", ["repair", "road test", "test"]),
            ("office log", "one payment and one invoice", "The payment was received before the invoice was issued.",
             "The invoice was issued before the payment was received.", ["payment", "invoice"]),
            ("station log", "one train arrival and one platform inspection", "The train arrived before the platform inspection began.",
             "The platform inspection began before the train arrived.", ["train", "platform inspection", "inspection"])]
    for k, (log, ev, A, B, nouns) in enumerate(f2t2):
        bg = f"The {log} records {ev}. These events occurred at different times."
        add(2, 2, k, "detail", bg, A, B, A, B, F2_KEYS + nouns)
    # Family 3 (numerical detail)
    for k, (nA, nB, items) in enumerate([("six", "nine", "glass vials"), ("four", "seven", "copper coins"), ("five", "eight", "sealed envelopes"),
                                         ("three", "ten", "steel bolts"), ("two", "eleven", "glass slides")]):
        bg = "The inventory entry describes one sealed box. Its contents were counted twice and the counts agreed."
        A, B = f"The box contained exactly {nA} {items}.", f"The box contained exactly {nB} {items}."
        add(3, 1, k, "detail", bg, A, B, A, B, ["<digits>", "<numwords>", items.split()[-1], "minutes"])
    for k, (log, nA, nB) in enumerate([("meeting log", "twenty", "forty"), ("training log", "fifteen", "thirty"), ("rehearsal log", "ten", "fifty"),
                                       ("briefing log", "twenty-five", "fifty-five"), ("hearing log", "thirty-five", "seventy")]):
        bg = f"The {log} records one session. Its duration was measured from the opening statement to the final adjournment."
        A, B = f"The session lasted exactly {nA} minutes.", f"The session lasted exactly {nB} minutes."
        add(3, 2, k, "detail", bg, A, B, A, B, ["<digits>", "<numwords>", "minutes"])
    # Family 4 (outcome / polarity)
    for k, (op, pos, neg) in enumerate([("upload", "succeeded", "failed"), ("backup", "succeeded", "failed"), ("transfer", "succeeded", "failed"),
                                        ("login", "succeeded", "failed"), ("build", "passed", "failed")]):
        bg = f"The tool log records one {op} attempt, with no retries. The result was checked after the attempt ended."
        A, B = f"The {op} {pos}.", f"The {op} {neg}."
        add(4, 1, k, "detail", bg, A, B, A, B, [pos, neg, pos[:4] + "*", neg[:4] + "*"] + F4_KEYS)
    for k, (log, item, pos, neg) in enumerate([("review log", "application", "approved", "rejected"), ("permit log", "permit", "granted", "denied"),
                                               ("claims log", "claim", "accepted", "rejected"), ("committee log", "proposal", "approved", "rejected"),
                                               ("records log", "request", "granted", "denied")]):
        bg = f"The {log} concerns one {item} and one final decision. The decision was issued yesterday."
        A, B = f"The {item} was {pos}.", f"The {item} was {neg}."
        add(4, 2, k, "detail", bg, A, B, A, B, [pos, neg, pos[:4] + "*", neg[:4] + "*"] + F4_KEYS)
    assert len(P) == 40
    for i, p in enumerate(P):
        p["pair_index"] = i
    return P


def b1_context(p: dict, version: str, filler2: bool) -> str:
    fact = p["fact_A"] if version == "A" else p["fact_B"]
    pre = (FILLER2 + " " if filler2 else "") + PREAMBLE
    return f"{pre} {p['background']} {fact} {END_SENTENCE}"


def keyword_hit(sentence: str, keywords: list[str]) -> list[str]:
    """Case-insensitive whole-word hits; '<digits>' matches \\d+, '<numwords>' matches English number words, 'stem*' matches \\bstem\\w*."""
    s = sentence.lower(); hits = []
    for k in keywords:
        if k == "<digits>":
            if re.search(r"\b\d+\b", s):
                hits.append(k)
        elif k == "<numwords>":
            if any(re.search(r"\b" + w + r"\b", s) for w in NUM_WORDS):
                hits.append(k)
        elif k.endswith("*"):
            if re.search(r"\b" + re.escape(k[:-1].lower()) + r"\w*", s):
                hits.append(k)
        elif re.search(r"\b" + re.escape(k.lower()) + r"\b", s):
            hits.append(k)
    return hits

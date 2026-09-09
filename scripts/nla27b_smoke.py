"""Smoke test for ceselder/qwen3.6-27b-nla-rl on one 80 GB GPU.

Phase A: load av_base (bf16) + one RL LoRA adapter, inject each example activation
         (norm-matched additive, output of decoder block 1, raw vector), greedy-decode
         the <explanation>.  Frees the AV.
Phase B: load ar_reconstructor (43-block truncated backbone, final norm -> Identity)
         + value_head (fp32), reconstruct from each explanation at the last token of
         the critic template, report cosine to the original activation, plus a
         shuffled-pair control (cos to a different example's activation).

Injection and AR conventions follow EasyNLA nla/injection.py, nla/utils/hooks.py,
nla/utils/critic.py (commit as cloned into /workspace/tools/EasyNLA).  Numbers only.
"""
import argparse, gc, json, re, time
from pathlib import Path
import torch, yaml
import pyarrow.parquet as pq
from transformers import AutoModelForCausalLM, AutoTokenizer

p = argparse.ArgumentParser()
p.add_argument("--repo", default=None)
p.add_argument("--adapter", default="iter_000600")
p.add_argument("--n", type=int, default=8)
p.add_argument("--max-new-tokens", type=int, default=200)
p.add_argument("--out", default="/workspace/logs/nla27b_smoke_out.json")
args = p.parse_args()

repo = Path(args.repo) if args.repo else next(Path("/workspace/hf/hub/models--ceselder--qwen3.6-27b-nla-rl/snapshots").iterdir())
meta = yaml.safe_load((repo / "nla_meta.yaml").read_text())
INJ = meta["tokens"]["injection_char"]; INJ_ID = meta["tokens"]["injection_token_id"]
LEFT = meta["tokens"]["injection_left_neighbor_id"]; RIGHT = meta["tokens"]["injection_right_neighbor_id"]
ACTOR_T = meta["prompt_templates"]["actor"]; CRITIC_T = meta["prompt_templates"]["critic"]
D = meta["extraction"]["d_model"]; MSE_SCALE = D ** 0.5  # sidecar has no mse_scale; EasyNLA default "sqrt_d_model"
EXPL_RE = re.compile(r"<explanation>(.*?)</explanation>", re.DOTALL)
dev = "cuda"

tab = pq.read_table(repo / "data/example_activations.parquet").slice(0, args.n).to_pylist()
acts = torch.tensor([r["activation_vector"] for r in tab], dtype=torch.float32)
print(f"examples {len(tab)}  act norms {[round(x,1) for x in acts.norm(dim=1).tolist()]}", flush=True)
report = {"repo": str(repo), "adapter": args.adapter, "n": len(tab), "mse_scale": MSE_SCALE, "rows": []}
for r in tab:
    report["rows"].append({"doc_id": r["doc_id"], "n_raw_tokens": r["n_raw_tokens"],
                           "source_tail": r["detokenized_text_truncated"][-300:]})

def gpu_gb(): return round(torch.cuda.memory_allocated() / 2**30, 1)

# ---------------- Phase A: verbalizer ----------------
tok = AutoTokenizer.from_pretrained(repo / "av_base")
t0 = time.time()
base = AutoModelForCausalLM.from_pretrained(repo / "av_base", dtype=torch.bfloat16, device_map=dev, attn_implementation="sdpa")
from peft import PeftModel
av = PeftModel.from_pretrained(base, repo / "av_rl_adapters" / args.adapter).eval()
print(f"AV loaded {time.time()-t0:.0f}s  gpu {gpu_gb()} GB  type {type(base).__name__}", flush=True)

inner = base.model
if hasattr(inner, "language_model"): inner = inner.language_model
layers = inner.layers
print(f"decoder blocks {len(layers)}  hook on block 1 output", flush=True)

vref = {"v": None, "ids": None, "hits": 0}
def embed_hook(m, a, kw, out):
    vref["ids"] = kw.get("input") if kw and kw.get("input") is not None else (a[0] if a else None)
    return out
def layer_hook(m, a, out):
    resid = out[0] if isinstance(out, tuple) else out
    ids = vref["ids"]
    if vref["v"] is None or ids is None or resid.shape[1] < 2: return out
    ids = ids.to(resid.device); new = resid.clone(); hits = 0
    for b, pos in (ids == INJ_ID).nonzero().tolist():
        if pos == 0 or pos == ids.shape[1]-1: continue
        if ids[b, pos-1] != LEFT or ids[b, pos+1] != RIGHT: continue
        h = new[b, pos].clone(); v = vref["v"].to(new.device, new.dtype)
        new[b, pos] = h + h.norm() * (v / (v.norm() + 1e-9)); hits += 1
    vref["hits"] = hits
    return (new, *out[1:]) if isinstance(out, tuple) else new
base.get_input_embeddings().register_forward_hook(embed_hook, with_kwargs=True)
layers[1].register_forward_hook(layer_hook)

msgs = [{"role": "user", "content": ACTOR_T.format(injection_char=INJ)}]
ptxt = tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
ids = tok.encode(ptxt, add_special_tokens=False)
pos = [i for i, t in enumerate(ids) if t == INJ_ID]
print(f"prompt tokens {len(ids)}  marker at {pos}  neighbours {(ids[pos[0]-1], ids[pos[0]+1])}  expect ({LEFT},{RIGHT})", flush=True)
assert len(pos) == 1 and ids[pos[0]-1] == LEFT and ids[pos[0]+1] == RIGHT
pt = torch.tensor([ids], device=dev)

for i, row in enumerate(report["rows"]):
    vref["v"] = acts[i:i+1]; vref["hits"] = 0
    t0 = time.time()
    with torch.no_grad():
        out = av.generate(input_ids=pt, attention_mask=torch.ones_like(pt), max_new_tokens=args.max_new_tokens,
                          do_sample=False, pad_token_id=tok.eos_token_id)
    vref["v"] = None
    resp = tok.decode(out[0, pt.shape[1]:], skip_special_tokens=True)
    m = EXPL_RE.search(resp)
    row.update({"response": resp, "explanation": m.group(1).strip() if m else None,
                "gen_tokens": int(out.shape[1] - pt.shape[1]), "gen_s": round(time.time()-t0, 1),
                "inject_hits_first_forward": vref["hits"]})
    print(f"\n### {i}  gen {row['gen_tokens']} tok in {row['gen_s']}s\nSOURCE TAIL: …{row['source_tail'][-200:]!r}\nRESPONSE: {resp}", flush=True)
Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False))

del av, base, inner, layers; gc.collect(); torch.cuda.empty_cache()
print(f"\nAV freed  gpu {gpu_gb()} GB", flush=True)

# ---------------- Phase B: reconstructor ----------------
from safetensors.torch import load_file
t0 = time.time()
ar = AutoModelForCausalLM.from_pretrained(repo / "ar_reconstructor", dtype=torch.bfloat16, device_map=dev, attn_implementation="sdpa").eval()
inner = ar.model
if hasattr(inner, "language_model"): inner = inner.language_model
print(f"AR loaded {time.time()-t0:.0f}s  blocks {len(inner.layers)}  gpu {gpu_gb()} GB  final norm {type(inner.norm).__name__} -> Identity", flush=True)
inner.norm = torch.nn.Identity()
vh = torch.nn.Linear(D, D, bias=False, dtype=torch.float32).to(dev)
sd = load_file(repo / "ar_reconstructor/value_head.safetensors")
vh.load_state_dict(sd); print(f"value_head keys {list(sd)}  |W-I|_F {(vh.weight.detach().cpu()-torch.eye(D)).norm():.2f}", flush=True)

def reconstruct(expl: str) -> torch.Tensor:
    cids = tok.encode(CRITIC_T.format(explanation=expl), add_special_tokens=False)
    x = torch.tensor([cids], device=dev)
    with torch.no_grad():
        h = inner(input_ids=x, use_cache=False).last_hidden_state[0, -1].float()
        h = h / (h.norm() + 1e-9) * MSE_SCALE
        return vh(h)

preds = []
for i, row in enumerate(report["rows"]):
    if not row["explanation"]:
        preds.append(None); continue
    preds.append(reconstruct(row["explanation"]).cpu())
cos = torch.nn.functional.cosine_similarity
for i, row in enumerate(report["rows"]):
    if preds[i] is None: continue
    g = acts[i]; pr = preds[i]
    c = cos(pr, g, dim=0).item()
    j = (i + 1) % len(preds); ctrl = cos(pr, acts[j], dim=0).item()
    pn = pr / pr.norm() * MSE_SCALE; gn = g / g.norm() * MSE_SCALE
    row.update({"cos_own": round(c, 4), "cos_shuffled": round(ctrl, 4), "mse_norm": round(((pn-gn)**2).mean().item(), 4)})
    print(f"{i}: cos_own {c:.4f}  cos_shuffled({j}) {ctrl:.4f}  mse_norm {row['mse_norm']:.4f}", flush=True)
own = [r["cos_own"] for r in report["rows"] if "cos_own" in r]; sh = [r["cos_shuffled"] for r in report["rows"] if "cos_shuffled" in r]
report["summary"] = {"n_scored": len(own), "cos_own_mean": round(sum(own)/max(len(own),1), 4), "cos_shuffled_mean": round(sum(sh)/max(len(sh),1), 4),
                     "n_no_explanation": sum(r["explanation"] is None for r in report["rows"])}
print("SUMMARY", json.dumps(report["summary"]), flush=True)
Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False))
print("DONE", flush=True)

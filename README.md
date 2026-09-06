# mech-interp

Local mechanistic-interpretability environment. Setup is specified in `SETUP.md`;
the resulting environment is documented in `notes/environment.md`.

```sh
source scripts/env.sh          # shell-side MPS env (model_utils sets the same in-process)
uv run python -m scripts.smoke_test   # correctness gate, sections 4a-4f of SETUP.md
uv run ipython                 # interactive work
```

- `src/model_utils.py` — the only model loader. Import it; do not write a second one.
- `src/patching.py` — causal interventions on a loaded model: residual patch
  sweeps over (layer, position), per-head/per-MLP direct logit attribution.
- `src/viz.py` — notebook display helpers. Never loads a model.
- `scripts/smoke_test.py` — CPU-vs-MPS logits, chat template, padding, hooks,
  logit lens, throughput/RSS.

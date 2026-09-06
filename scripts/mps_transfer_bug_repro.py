"""Standalone reproducer for the torch 2.13.0 MPS device+dtype transfer bug.

A combined `.to("cpu", torch.float32)` off an MPS tensor whose dtype is 2 bytes
wide (bf16/fp16) and whose storage offset is nonzero reads from the wrong offset:
the offset is applied in the DESTINATION element size.  `a[1]` (elements 10..19,
byte offset 20) comes back as elements 5..9 plus zeros.

Run:  uv run python -m scripts.mps_transfer_bug_repro
See src/model_utils.to_cpu_f32() for the workaround used throughout this repo.
"""
from src.model_utils import MPS_ENV
import torch
print("torch", torch.__version__)

def check(dtype, n=10):
    a = torch.arange(2 * n, dtype=dtype, device="mps").reshape(2, n)
    want = list(range(n, 2 * n))
    variants = {
        "x[1].to('cpu', f32)      ": a[1].to("cpu", torch.float32),
        "x[1].contiguous().to(..) ": a[1].contiguous().to("cpu", torch.float32),
        "x[1].clone().to(..)      ": a[1].clone().to("cpu", torch.float32),
        "x[1].float().cpu()       ": a[1].float().cpu(),
        "x[1].cpu().float()       ": a[1].cpu().float(),
        "x[0].to('cpu', f32)  ofs0": a[0].to("cpu", torch.float32),
    }
    for name, t in variants.items():
        exp = want if "x[1]" in name else list(range(n))
        print(f"  {dtype!s:16s} {name} -> {'OK ' if t.tolist() == exp else 'WRONG'} {t.tolist()}")

for dt in (torch.bfloat16, torch.float16, torch.float32):
    check(dt)

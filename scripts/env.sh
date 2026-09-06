#!/bin/sh
# Shell-side env for mech-interp work.  `source scripts/env.sh` before `uv run ipython`.
#
# NOTE: src/model_utils.py sets these same values in-process above `import torch`
# (see load_model / _set_mps_env).  Keep the two in sync.  A subprocess `source`
# would die with the child, so Python never sources this file.

export PYTORCH_ENABLE_MPS_FALLBACK=1

# Cap MPS allocations at 80% of unified memory.  Do NOT set 0.0 ("no limit"):
# on a shared-memory Mac that lets the allocator starve macOS and hang the machine.
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.8

# The low watermark must be <= the high one.  Its default is 1.4, so setting only
# the high ratio makes the allocator raise
#   RuntimeError: invalid low watermark ratio 1.4
# on the first empty_cache()/allocation.  Set both or neither.
export PYTORCH_MPS_LOW_WATERMARK_RATIO=0.7

# Fallback logging: PYTORCH_DEBUG_MPS_FALLBACK is NOT supported by torch 2.13.0.
# Verified by scanning torch/lib/*.dylib for the string -- only
# PYTORCH_ENABLE_MPS_FALLBACK, PYTORCH_MPS_HIGH_WATERMARK_RATIO and
# PYTORCH_MPS_LOW_WATERMARK_RATIO are read by this build.  There is therefore no
# way to log silent CPU fallbacks via env var here; watch for the 100x slowdown
# instead, or set PYTORCH_ENABLE_MPS_FALLBACK=0 temporarily to make an
# unsupported op raise instead of silently falling back.

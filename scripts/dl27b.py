import os
os.environ.setdefault("HF_HOME","/workspace/hf")
os.environ["HF_HUB_ENABLE_HF_TRANSFER"]="1"
from huggingface_hub import snapshot_download
p = snapshot_download(
    "ceselder/qwen3.6-27b-nla-rl",
    allow_patterns=["av_base/*","av_rl_adapters/iter_000600/*","ar_reconstructor/*",
                    "data/example_activations.parquet","nla_meta.yaml","run_config.yaml"],
    max_workers=16,
)
print("SNAPSHOT", p)

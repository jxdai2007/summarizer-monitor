#!/usr/bin/env python3
"""Merge the AutoScientist LoRA checkpoint (../results/best-checkpoint.tgz, extracted to ../results/ckpt) into
Qwen/Qwen3.5-4B and save a full bf16 model to ../results/merged for MLX inference.
  uv run --no-project --with "transformers>=4.57" --with peft --with torch --with accelerate python e14_merge.py"""
import tarfile
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

RES = Path(__file__).resolve().parent.parent / "results"
ck = RES / "ckpt"
if not ck.exists():
    with tarfile.open(RES / "best-checkpoint.tgz") as t:
        t.extractall(ck, filter="data")
ad = sorted(ck.rglob("adapter_config.json"))[0].parent
print("adapter", ad)
m = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3.5-4B", dtype=torch.bfloat16)
m = PeftModel.from_pretrained(m, str(ad)).merge_and_unload()
m.save_pretrained(RES / "merged", safe_serialization=True)
AutoTokenizer.from_pretrained("Qwen/Qwen3.5-4B").save_pretrained(RES / "merged")
print("saved", RES / "merged")

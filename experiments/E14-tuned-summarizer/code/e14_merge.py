#!/usr/bin/env python3
"""Merge the AutoScientist LoRA (../results/ckpt, keys model.language_model.layers.*) into Qwen/Qwen3.5-4B loaded as
Qwen3_5ForConditionalGeneration (the class the adapter was trained on), verify the merge changed the targeted weights,
and save a full bf16 model to ../results/merged for MLX inference. CPU only.
  uv run --no-project --with "transformers>=4.57" --with peft --with torch --with accelerate --with torchvision python e14_merge.py"""
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForImageTextToText, AutoProcessor, AutoTokenizer

import sys
RES = Path(__file__).resolve().parent.parent / "results"
if "--b" in sys.argv:
    RES = RES / "e14b"   # E14b checkpoint extracted to results/e14b/ckpt, merged to results/e14b/merged
m = AutoModelForImageTextToText.from_pretrained("Qwen/Qwen3.5-4B", dtype=torch.bfloat16)
print(type(m).__name__)
name = "model.language_model.layers.0.mlp.down_proj.weight"
before = dict(m.named_parameters())[name].detach().clone().float()
pm = PeftModel.from_pretrained(m, str(RES / "ckpt"))
n_lora = sum(1 for n, _ in pm.named_parameters() if "lora_" in n)
print("lora tensors attached:", n_lora)
assert n_lora > 0, n_lora
merged = pm.merge_and_unload()
after = dict(merged.named_parameters())[name].detach().float()
delta = (after - before).norm().item() / before.norm().item()
print(f"relative change in {name}: {delta:.4f}")
assert delta > 1e-4, "merge did not change the weights"
merged.save_pretrained(RES / "merged", safe_serialization=True)
AutoTokenizer.from_pretrained("Qwen/Qwen3.5-4B").save_pretrained(RES / "merged")
try:
    AutoProcessor.from_pretrained("Qwen/Qwen3.5-4B").save_pretrained(RES / "merged")
except Exception as e:  # noqa: BLE001
    print("processor not saved:", str(e)[:120])
print("saved", RES / "merged")

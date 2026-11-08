# E14 analysis (in progress)

## Deviations (logged before any evaluation output existed)
- **D1, inference engine (18:55 PT).** Evaluation runs on MLX (mlx-lm 0.32.2, `batch_generate`) instead of transformers
  on MPS. Weights (bf16), sampling (temperature 0.7, top_p 0.95), max tokens (700), thinking off and prompts are
  unchanged.
  - Reason: transformers fell back to reference PyTorch kernels for Qwen3.5's linear-attention layers. The projection
    was about 3 h, against about 40 min on MLX.
  - The tuned variant is the base model with the LoRA merged in (`code/e14_merge.py`), not a runtime adapter.
- **D2, run order (18:55 PT).** The base-model arms run first, while AutoScientist training is still in progress. The
  protocol had listed tuned before base. This changes the order only.

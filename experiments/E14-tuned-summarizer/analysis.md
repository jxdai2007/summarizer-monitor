# E14 analysis

## Results (locked predictions; MLX inference; monitors Haiku 5.5 + DeepSeek v4.1 Flash)
**E14** (platform recipe: 1 epoch, 23 steps, learning rate 5e-5, LoRA rank 16): **KILL.**

| Held-out set B | Base | Tuned |
|---|---|---|
| LlamaIndex prompt (unseen) | +70.7 | +67.5 |
| LangChain prompt (seen) | +67.1 | +62.3 |
| Held-out controls flagged | 0/16 | 0/16 |

**E14b** (stronger dose: 3 epochs, 69 steps, learning rate 2e-4, LoRA rank 64; training loss 1.37 → 0.42): **PASS**
(T1–T4 all pass).

| Held-out set B | Base | Tuned |
|---|---|---|
| LlamaIndex prompt (unseen) | +70.7 | **+11.4** [+5, +18] |
| LangChain prompt (seen) | +67.1 | **+1.3** [−9, +9] |
| Held-out controls flagged | 0/16 | 0/16 |

**E14c** (ChatDev transfer kill-test, an environment never seen in training; LlamaIndex prompt): **WEAKEN.**
- Tuned +15.9 [+3, +29] vs base +61.1.
- Tuned flags 1/24 control pairs.
- C2 misses the locked ≤ 15 PASS line by 0.9 points.
- Reading: most of the repair carries over to a new environment, but not all of it.

**Allowed wording.** "Fine-tuning a 4B open model on about 1,200 summaries from audit-passing summarizers (set A only)
cut its held-out loss under shipped prompts from about 70 to 1–11 points. On a new environment, from 61 to 16 (just over
the FAIL line). A lighter platform-default recipe did nothing."


## Deviations (logged before any evaluation output existed)
- **D1, inference engine (18:55 PT).** Evaluation runs on MLX (mlx-lm 0.32.2, `batch_generate`) instead of transformers
  on MPS. Weights (bf16), sampling (temperature 0.7, top_p 0.95), max tokens (700), thinking off and prompts are
  unchanged.
  - Reason: transformers fell back to reference PyTorch kernels for Qwen3.5's linear-attention layers. The projection
    was about 3 h, against about 40 min on MLX.
  - The tuned variant is the base model with the LoRA merged in (`code/e14_merge.py`), not a runtime adapter.
- **D2, run order (18:55 PT).** The base-model arms run first, while AutoScientist training is still in progress. The
  protocol had listed tuned before base. This changes the order only.

## Training outcome (19:10 PT; before any tuned-model evaluation)
- AutoScientist run `e5444697…` succeeded: 1 iteration, 1 epoch, 23 steps, LoRA rank 16 on attention and MLP
  projections. Training loss went from 1.37 to 1.04.
- The platform's own `best_win_rate` was 0.094. That is the platform's head-to-head judge on its own evaluations, not
  our measure.
- **Merge.** The adapter keys refer to `Qwen3_5ForConditionalGeneration`, so it was merged into that class (all 256
  LoRA tensors attached, and the targeted weights changed). Loading it into the text-only class would have silently
  skipped the adapter.
- **Caveat.** The adapter's base is named `togethercomputer/Qwen3.5-4B`, which is Adaption's training backend and not a
  public repo. It is assumed to be the official Qwen/Qwen3.5-4B weights, which is what we merged into and evaluate as
  the base.

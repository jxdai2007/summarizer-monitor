#!/usr/bin/env python3
"""E14: upload ../data/train.csv (raw prompt/completion) and start one AutoScientist SFT run on Qwen/Qwen3.5-4B (LoRA),
max_iterations 1. Writes ../results/train_run.json. `status` polls; `download` fetches the best checkpoint."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
RES = EXP / "results"
RES.mkdir(exist_ok=True)
KEY = [l.split("=", 1)[1].strip() for l in Path("/Users/macstudio/projects/swarm-alignment/.env").read_text().splitlines()
       if l.startswith("ADAPTION_API_KEY=")][0]
from adaption import Adaption  # noqa: E402
c = Adaption(api_key=KEY, timeout=600)
cmd = sys.argv[1]
if cmd == "start":
    ds = c.datasets.upload_file(str(EXP / "data/train.jsonl"), name="e14-oversight-summaries", processing_mode="raw",
                                column_mapping={"prompt": "prompt", "completion": "completion"})
    print("dataset", ds.dataset_id, flush=True)
    c.datasets.wait_for_completion(ds.dataset_id, timeout=1800)
    print("dataset status", c.datasets.get_status(ds.dataset_id), flush=True)
    run = c.autoscientist.create(dataset_id=ds.dataset_id, model="Qwen/Qwen3.5-4B", training_method="instruction",
                                 max_iterations=1, idempotency_key="e14-qwen35-4b-v1")
    out = {"dataset_id": ds.dataset_id, "run_id": run.id, "status": run.status, "model": "Qwen/Qwen3.5-4B"}
    (RES / "train_run.json").write_text(json.dumps(out, indent=1))
    print(out, flush=True)
elif cmd == "start_b":
    ds_id = json.loads((RES / "train_run.json").read_text())["dataset_id"]
    run = c.autoscientist.create(dataset_id=ds_id, model="Qwen/Qwen3.5-4B", training_method="instruction", max_iterations=1,
                                 hyperparams={"n_epochs": 3, "learning_rate": 2e-4, "lora_r": 64, "lora_alpha": 128,
                                              "lora_trainable_modules": "all-linear"}, idempotency_key="e14b-qwen35-4b-v1")
    out = {"dataset_id": ds_id, "run_id": run.id, "status": run.status, "model": "Qwen/Qwen3.5-4B", "variant": "e14b"}
    (RES / "train_run_b.json").write_text(json.dumps(out, indent=1))
    print(out, flush=True)
elif cmd == "status":
    rid = json.loads((RES / ("train_run_b.json" if sys.argv[2:] == ["b"] else "train_run.json")).read_text())["run_id"]
    r = c.autoscientist.get(rid)
    print({k: getattr(r, k, None) for k in ("id", "status", "iterations_completed", "max_iterations", "best_win_rate",
                                             "download_available", "error", "model")})
elif cmd == "download":
    b = sys.argv[2:] == ["b"]
    rid = json.loads((RES / ("train_run_b.json" if b else "train_run.json")).read_text())["run_id"]
    dst = RES / ("e14b/best-checkpoint.tgz" if b else "best-checkpoint.tgz")
    dst.parent.mkdir(exist_ok=True)
    with c.autoscientist.with_streaming_response.download(rid) as resp:
        resp.stream_to_file(str(dst))
    print("downloaded", dst.stat().st_size)

#!/bin/bash
# usage: run.sh LOGNAME args...   (runs e2b_run.py with uv, output to ../results/LOGNAME.log)
cd "$(dirname "$0")"
name=$1; shift
uv run --with openai --with scipy python e2b_run.py "$@" > ../results/$name.log 2>&1

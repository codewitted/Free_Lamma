#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python evaluation/run_experiments.py
python - <<'PY'
from backend.api.main import run_full_pipeline, CommandRequest
cmd = "On Floor 6, Robot 1 must collect the blue box from the office. Robot 2 must collect the coffee mug from the kitchen. Robot 3 must inspect the corridor. All robots must avoid blocking each other and deliver or report to the storage room."
print(run_full_pipeline(CommandRequest(command=cmd)))
PY


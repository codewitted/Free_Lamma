#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PY="${PYTHON:-.venv/bin/python}"
if [ ! -x "$PY" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
    echo "WARNING: Python virtual environment not found. Falling back to system python: $PY"
  else
    echo "ERROR: Python virtual environment not found at $PY"
    echo "Run first: bash scripts/setup_ubuntu.sh"
    exit 1
  fi
fi

echo "==> 1/6 Python compile checks"
"$PY" -m py_compile \
  scripts/demo_ai2thor_video.py \
  scripts/constraint_optimizer.py \
  scripts/run_natural_command.py \
  scripts/check_local_llm.py \
  scripts/pddlrun_llmseparate.py \
  scripts/plantocode.py \
  gazebo_demo/scripts/check_gazebo_assets.py

echo "==> 2/6 Optimiser baseline vs MILP verification"
"$PY" scripts/constraint_optimizer.py \
  --task-file data/final_test/FloorPlan15vague.json \
  --output-dir outputs/optimizer/FloorPlan15vague >/tmp/lammap_optimizer_check.json

"$PY" - <<'PY'
import json
from pathlib import Path

path = Path("outputs/optimizer/FloorPlan15vague/allocation_result.json")
payload = json.loads(path.read_text())
greedy = payload["greedy_metrics"]["total_travel_cost"]
optimised = payload["optimised_metrics"]["total_travel_cost"]
success = payload["optimised_metrics"]["success_proxy"]
if optimised > greedy:
    raise SystemExit(f"Optimiser regression: optimised {optimised} > greedy {greedy}")
if success < 1.0:
    raise SystemExit(f"Unexpected success proxy: {success}")
print(f"Optimiser OK: greedy={greedy}, optimised={optimised}, improvement={(greedy-optimised)/greedy*100:.2f}%")
PY

echo "==> 3/6 Typed natural-language command verification"
"$PY" scripts/run_natural_command.py \
  --command "put the apple and tomato in the fridge and switch off the light" \
  --robots 1,2,3 \
  --output-dir outputs/natural_command_demo >/tmp/lammap_natural_command_check.json

"$PY" - <<'PY'
import json
from pathlib import Path

task = json.loads(Path("outputs/natural_command_demo/parsed_task.json").read_text())
result = json.loads(Path("outputs/natural_command_demo/allocation_result.json").read_text())
assert task["object_states"][0]["name"] == "Fridge"
assert "Apple" in task["object_states"][0]["contains"]
assert "Tomato" in task["object_states"][0]["contains"]
assert any(s["name"] == "LightSwitch" and s["state"] == "OFF" for s in task["object_states"])
assert result["optimised_metrics"]["success_proxy"] == 1.0
print("Natural command OK: parsed command and allocated all subtasks")
PY

echo "==> 4/6 Gazebo asset and script verification"
"$PY" gazebo_demo/scripts/check_gazebo_assets.py
bash -n gazebo_demo/scripts/run_gz_sim_demo.sh

if command -v gz >/dev/null 2>&1; then
  echo "Gazebo command found: $(command -v gz)"
  echo "To launch the GUI demo, run:"
  echo "  cd gazebo_demo && bash scripts/run_gz_sim_demo.sh"
else
  echo "WARNING: 'gz' not found, so Gazebo GUI demo cannot launch on this machine."
  echo "Run 'bash scripts/setup_ubuntu.sh' to install Gazebo, or install it manually."
fi

echo "==> 5/6 AI2-THOR output evidence check"
"$PY" - <<'PY'
from pathlib import Path
import os
import subprocess

videos = sorted(Path("outputs/ai2thor_demo").glob("video_*.mp4"))
if len(videos) < 3:
    raise SystemExit("Missing AI2-THOR MP4 evidence")

try:
    import imageio.v2 as imageio
    import numpy as np

    for video in videos:
        reader = imageio.get_reader(video)
        frame = reader.get_data(0)
        meta = reader.get_meta_data()
        reader.close()
        if float(np.std(frame)) < 1.0:
            raise SystemExit(f"Video appears blank: {video}")
        print(f"Video OK: {video.name}, fps={meta.get('fps')}, size={meta.get('size')}")
except Exception as exc:
    print(f"WARNING: Deep video inspection unavailable ({exc}). Falling back to existence/size checks.")
    for video in videos:
        size = os.path.getsize(video)
        if size < 10000:
            raise SystemExit(f"Video too small to be credible evidence: {video} ({size} bytes)")
        print(f"Video present: {video.name}, size={size} bytes")

contact_sheet = Path("outputs/ai2thor_demo/preview_contact_sheet.jpg")
if not contact_sheet.exists():
    raise SystemExit("Missing AI2-THOR contact sheet evidence")
print(f"Contact sheet OK: {contact_sheet} ({contact_sheet.stat().st_size} bytes)")
PY

echo "==> 6/6 Optional local LLM endpoint check"
if [ -n "${LOCAL_LLM_BASE_URL:-}" ]; then
  "$PY" scripts/check_local_llm.py \
    --base-url "$LOCAL_LLM_BASE_URL" \
    --api-key "${LOCAL_LLM_API_KEY:-local-no-key-required}" \
    --model "${LOCAL_LLM_MODEL:-llama3.1:8b}"
else
  echo "Skipping local LLM check because LOCAL_LLM_BASE_URL is not set."
  echo "Example:"
  echo "  export LOCAL_LLM_BASE_URL=http://localhost:11434/v1"
  echo "  export LOCAL_LLM_MODEL=llama3.1:8b"
fi

echo
echo "ALL NON-GUI CHECKS PASSED."
echo "If Gazebo is installed, launch the visual demo with:"
echo "  cd gazebo_demo && bash scripts/run_gz_sim_demo.sh"

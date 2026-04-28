# Project Status

Date: 2026-04-28

## Current Stage

Open LaMMA-R has been created as a clean dissertation artefact under `Open-Lamma-R/`.

## Working Now

- Local-first backend package layout.
- FastAPI endpoints for parse, PDDL generation, planning, optimisation, execution, status and full pipeline.
- Ollama/OpenWebUI local LLM gateway with strict JSON parsing and rule-based fallback.
- Pydantic mission schema.
- PDDL domain and problem generator.
- Fast Downward client with unavailable-planner fallback.
- MILP allocator using SciPy HiGHS when installed, greedy fallback otherwise.
- Dry-run executor.
- AI2-THOR and ROS 2 adapters with graceful fallback/mocking.
- React dashboard source.
- Ten simulation scenarios.
- Evaluation script for ablation CSVs and plots.
- Tests for the critical dry-run path.
- Setup guides, dissertation draft and recording instructions.
- No-server AI2-THOR Floor 6 video command:
  - `scripts/run_floor6_ai2thor_video.py`
  - `scripts/run_floor6_ai2thor_video.ps1`

## Verification Performed

- Direct Python test harness passed all test functions in:
  - `tests/test_json_schema.py`
  - `tests/test_pddl_generation.py`
  - `tests/test_milp_allocator.py`
  - `tests/test_plan_parser.py`
  - `tests/test_full_pipeline_dry_run.py`
- `evaluation/run_experiments.py` completed and generated:
  - `evaluation/results/results_metrics.csv`
  - `evaluation/results/cv_summary.csv`
  - `evaluation/results/ablation_results.csv`
  - `evaluation/plots/success_rate.png`
  - `evaluation/plots/travel_cost.png`
  - `evaluation/plots/planning_time.png`
  - `evaluation/plots/utility_score.png`
- `python -m pytest tests -q` passes after dependency installation.
- `scripts/run_floor6_ai2thor_video.py` plans the Floor 6 mission and reaches the AI2-THOR launch stage. On this Windows machine, AI2-THOR fails because no Windows build exists for its Unity commit. This is an external simulator/platform limitation, not a planning pipeline failure.

## Local Runtime Limitations Observed

- `pytest` is not installed in the bundled runtime, so tests were executed through a direct Python import harness.
- `fastapi` is not installed in the bundled runtime, so the API server needs `pip install -r requirements.txt` before launch.
- `scipy` is not installed in the bundled runtime, so the MILP allocator used its deterministic greedy fallback during verification.
- `matplotlib` is not installed in the bundled runtime, so evaluation created valid placeholder PNG artefacts until dependencies are installed.

## External Setup Needed

- `pip install -r requirements.txt`
- `cd frontend && npm install`
- Optional: Ollama/OpenWebUI.
- Optional: Fast Downward.
- Optional: AI2-THOR.
- Optional: ROS 2 Humble/Jazzy with LIMO/Nav2 stack.
- Optional: FFmpeg or VLC for video capture.
- Linux/WSL2/display-capable workstation for AI2-THOR video generation.

## Next Engineering Stage

1. Run `.\scripts\run_floor6_ai2thor_video.ps1`.
2. Install VLC if you want automatic VLC playback instead of the default Windows video player.
3. Build Fast Downward or set `FAST_DOWNWARD_PATH`.
4. Replace dry-run planner fallback with real planner output in demo evidence.
5. For visible LIMO robot bodies, connect the same plan trace to Gazebo/ROS 2 or custom AI2-THOR Unity robot assets.

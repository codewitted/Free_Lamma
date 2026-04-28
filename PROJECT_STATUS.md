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

## Next Engineering Stage

1. Install Python dependencies with `pip install -r requirements.txt`.
2. Run `python -m pytest tests -q`.
3. Install frontend dependencies and run the GUI.
4. Build Fast Downward or set `FAST_DOWNWARD_PATH`.
5. Replace dry-run planner fallback with real planner output in demo evidence.
6. Add screenshots/video once the GUI and simulator are running.

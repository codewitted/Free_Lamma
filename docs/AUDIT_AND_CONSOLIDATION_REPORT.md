# Audit and Consolidation Report

## Sources Audited

- `upstream/LaMMA-P`: official LaMMA-P ICRA 2025 baseline with MAT-THOR data, PDDL resources, AI2-THOR scripts and vendored Fast Downward.
- `upstream/Proj-Lamma`: experimental pivot adding ROS 2/Nav2 bridge templates, resource locking, mock showcase and local/Ollama claims.
- `upstream/lamma_project`: cleaner Python benchmark layout with schema validation, Ollama/OpenAI/OpenWebUI client ideas, Floor 6 evaluation scripts and PDDL generator.
- `upstream/MyLamma`: web-facing prototype with TypeScript schema, React visualisation concept, GLPK/MILP-inspired allocation, and headless result outputs.
- `27047194_Robotics_Project_2526.pdf`: literature/project proposal motivating LLM + PDDL + MILP for LIMO robots under ROS 2.

## Inherited Ideas

- From LaMMA-P: natural-language decomposition into symbolic planning, AI2-THOR/MAT-THOR inspiration, PDDL and Fast Downward use, and FloorPlan task datasets.
- From Proj-Lamma: ROS 2/Nav2 dispatch direction, mock mode, and resource reservation for corridor/aisle conflicts.
- From lamma_project: Pydantic schema validation, local provider abstraction, Floor 6 evaluation mindset, and planner client separation.
- From MyLamma: GUI requirement, task/robot schema shape, allocation visualisation, and downloadable run artefacts.

## Problems Found

- The inherited repos mix research code, generated outputs, vendored dependencies and virtual environments.
- The official baseline still depends on paid OpenAI API setup through `api_key.txt`.
- Some planner clients use hard-coded absolute paths.
- PDDL generation and LLM parsing are scattered across scripts.
- ROS 2 and AI2-THOR execution are not cleanly optional.
- GUI work exists separately from Python planning/evaluation logic.
- MILP optimisation is either absent, partial, or implemented in a separate JavaScript prototype.

## What Changed

- Created `Open-Lamma-R/` as a clean examiner-facing repository.
- Replaced paid API dependence with a local-first LLM gateway supporting Ollama and OpenWebUI, with paid OpenAI-compatible fallback disabled by default.
- Added strict Pydantic validation and robust JSON extraction.
- Added rule-based fallback so the flagship demo runs without a model.
- Added a new multi-robot PDDL domain and problem generator.
- Added Fast Downward integration with setup-aware fallback.
- Added a SciPy HiGHS MILP allocator with deterministic greedy fallback.
- Added dry-run, AI2-THOR, and ROS 2/mock execution layers.
- Added a React dashboard with command input, status, JSON, PDDL, plan, allocation, logs, metrics and download controls.
- Added a no-server AI2-THOR Floor 6 MP4 evidence command for dissertation/demo use.
- Added ten scenarios, evaluation CSV generation and plot generation.
- Added tests for schema, PDDL, MILP, plan parsing and full dry-run pipeline.
- Added dissertation-ready documentation and setup guides.

## What Was Removed

Nothing was deleted from the cloned upstream references. The new project deliberately avoids copying vendored virtual environments, generated logs, crash dumps, large media artefacts and API-key files into the clean structure.

## What Was Added

- Original contribution: MILP task allocation layer between LLM parsing and symbolic/execution stages.
- Original contribution: local/free LLM architecture with OpenWebUI/Ollama preference.
- Original contribution: full dry-run path that produces reproducible evidence without paid APIs or robotics hardware.
- Original contribution: GUI for inspecting every pipeline stage.
- Original contribution: evaluation framework for LLM-only, PDDL-only, LLM+PDDL and LLM+PDDL+MILP ablations.
- Original contribution: ROS 2/LIMO-ready dispatcher that degrades to mock mode.

## Setup Still Required

- Install Python dependencies from `requirements.txt`.
- Install Node.js dependencies in `frontend/`.
- Install and run Ollama or OpenWebUI for live local LLM parsing.
- Install/build Fast Downward for true classical planning instead of heuristic dry-run fallback.
- Install AI2-THOR with a working display for FloorPlan6 screenshots.
- Install ROS 2 Humble/Jazzy and LIMO/Nav2 stack for real robot dispatch.
- Install VLC or FFmpeg for recording demo evidence.

## What The Original LaMMA-P Repository Does

`https://github.com/codewitted/LaMMA-P.git` is the original informing repository. It implements Language Model-Driven Multi-Agent PDDL Planning for MAT-THOR/AI2-THOR tasks. In practical terms, it takes household-style natural-language tasks, uses an OpenAI-backed language model to decompose and allocate subtasks, generates PDDL problem files, solves them with the vendored Fast Downward planner, then converts or executes the resulting plans in AI2-THOR-oriented scripts.

The useful inherited ideas are:

- LM-driven task decomposition.
- PDDL as the symbolic planning representation.
- Fast Downward as the classical planner.
- MAT-THOR/AI2-THOR household task benchmark inspiration.
- Multi-agent long-horizon planning structure.

The limitations for this dissertation project are:

- It expects paid OpenAI API use.
- It is script-heavy rather than a clean reusable project.
- It includes generated artefacts and vendored environment material.
- It does not provide the local/free LLM + MILP + ROS 2/LIMO-ready dissertation package required here.

# RBT3001 Examiner Run Guide

Project: Learning-Assisted Multi-Robot Coordination with Local LLMs, PDDL and Constraint-Driven Optimisation

Student ID: 27047194

## What This Artefact Demonstrates

This repository extends LaMMA-P into a dissertation-ready robotics project artefact. It demonstrates:

- a local/no-paid-API LLM pathway for LaMMA-P using OpenAI-compatible endpoints such as Open WebUI or Ollama;
- a deterministic MILP task-allocation optimiser for heterogeneous multi-robot teams;
- AI2-THOR multi-agent video evidence showing robots carrying out pickup/carry/place tasks;
- documented evaluation outputs suitable for the dissertation results chapter.

## Key Files

- `README.md`: project overview and main commands.
- `docs/dissertation_project_blueprint.md`: dissertation-facing aims, methodology, evaluation plan and rubric mapping.
- `docs/dissertation_ai_prompt.md`: a full prompt to generate the dissertation from the completed artefact.
- `scripts/constraint_optimizer.py`: MILP/ILP allocation contribution.
- `scripts/demo_ai2thor_video.py`: AI2-THOR video demonstration.
- `scripts/check_local_llm.py`: local Open WebUI/Ollama smoke test.
- `scripts/run_natural_command.py`: lightweight typed natural-language command runner.
- `gazebo_demo/`: Gazebo Sim world, playback script and asset checker for Ubuntu/Gazebo execution.
- `configs/local_llm.env.example`: local model configuration template.
- `api_key.example.txt`: placeholder only; no paid API key is included or required for local mode.
- `docs/project_status_answers.md`: honest answers on novelty, Gazebo scope, typed commands, ML/training and GPU requirements.
- `outputs/optimizer/FloorPlan15vague/allocation_result.json`: quantitative optimiser result.
- `outputs/ai2thor_demo/*.mp4`: generated robot execution videos.

## Reproducible Setup

Recommended platform: Windows 11 with WSL2 Ubuntu, or native Ubuntu 22.04+ with Python 3.10+.

This package was carried forward from `27047194_RBT3001_LaMMA_P_Artefact_CLEAN.zip` and repackaged as `27047194_RBT3001_LaMMA_P_Artefact_WINDOWS_WSL_VERIFIED.zip`.

The verification pass on `2026-05-02` confirmed:

- `bash scripts/setup_ubuntu.sh` now completes cleanly even if `sudo` or package downloads are blocked, while clearly warning that Gazebo/AI2-THOR dependencies still need a normal Ubuntu machine.
- `bash scripts/verify_ubuntu_pipeline.sh` passed all non-GUI checks.
- `python3 scripts/constraint_optimizer.py --task-file data/final_test/FloorPlan15vague.json --output-dir outputs/optimizer/FloorPlan15vague` passed with `13.54%` travel-cost improvement over greedy.
- `python3 scripts/run_natural_command.py --command "put the apple and tomato in the fridge and switch off the light" --robots 1,2,3 --output-dir outputs/natural_command_demo` passed with success proxy `1.0`.
- `python3 gazebo_demo/scripts/check_gazebo_assets.py` passed.
- On Windows 11 + WSL2 Ubuntu with Gazebo Sim installed, `gz sim --versions` returned `8.11.0` and `bash scripts/run_gz_sim_demo.sh` launched the Gazebo demo successfully.

The same pass also found honest environment limits in the container used here:

- `gz` was not installed, so Gazebo GUI launch could not be verified live.
- `glxinfo -B` failed with `unable to open display :1`.
- `scripts/demo_ai2thor_video.py` could not be rerun here because `ai2thor` was not installable in this restricted environment, but valid bundled evidence remains included under `outputs/ai2thor_demo/`.
- `scripts/check_local_llm.py` could not contact a local endpoint here; local OpenAI-compatible endpoint support remains implemented for Ollama/Open WebUI.

Create a clean Linux-side environment:

```bash
unzip 27047194_RBT3001_LaMMA_P_Artefact_WINDOWS_WSL_VERIFIED.zip -d ~/projects
cd ~/projects/27047194_RBT3001_LaMMA_P_Artefact
bash scripts/setup_ubuntu.sh
```

This installs Python dependencies and Gazebo Sim on Ubuntu when possible. On a normal WSL2 Ubuntu machine with `sudo` and internet access, this should install the missing runtime packages directly. In a restricted environment, the script now degrades cleanly and leaves clear warnings instead of aborting immediately.

Verify the complete non-GUI pipeline:

```bash
bash scripts/verify_ubuntu_pipeline.sh
```

## Run the Optimiser Evidence

```bash
.venv/bin/python scripts/constraint_optimizer.py \
  --task-file data/final_test/FloorPlan15vague.json \
  --output-dir outputs/optimizer/FloorPlan15vague
```

Expected result files:

- `outputs/optimizer/FloorPlan15vague/allocation_result.json`
- `outputs/optimizer/FloorPlan15vague/allocation_result.csv`

Verified sample result:

- Greedy travel-cost proxy: `21.060`
- Optimised travel-cost proxy: `18.209`
- Improvement: `13.54%`
- Optimised success proxy: `1.0`

This directly supports the dissertation claim that a deterministic optimisation layer improves task allocation quality compared with a simple greedy allocation baseline.

## Run the AI2-THOR Video Demo

```bash
.venv/bin/python scripts/demo_ai2thor_video.py \
  --scene FloorPlan1 \
  --output-dir outputs/ai2thor_demo \
  --fps 8
```

Expected result files:

- `outputs/ai2thor_demo/video_agent_1.mp4`
- `outputs/ai2thor_demo/video_agent_2.mp4`
- `outputs/ai2thor_demo/video_top_view.mp4`
- `outputs/ai2thor_demo/index.html`
- `outputs/ai2thor_demo/preview_contact_sheet.jpg`

First run note: AI2-THOR may download a Unity simulator build for the current OS. This can be several hundred MB and requires internet access. The generated MP4 files are included in this submission so the examiner can inspect the successful output even if the local AI2-THOR runtime is unavailable.

## Run the Gazebo Sim Demonstration

The Gazebo demo requires Ubuntu with Gazebo Sim installed. The restricted packaging container could not launch it, but a later Windows 11 + WSL2 Ubuntu verification did launch it successfully with Gazebo Sim `8.11.0`. Evidence notes are included under `outputs/gazebo_demo/`.

On an Ubuntu/Gazebo machine:

```bash
cd LaMMA-P-main/gazebo_demo
bash scripts/run_gz_sim_demo.sh
```

The local asset checks passed on the development machine:

```bash
.venv/bin/python gazebo_demo/scripts/check_gazebo_assets.py
bash -n gazebo_demo/scripts/run_gz_sim_demo.sh
```

Expected behaviour: robot1 carries apple to fridge, robot2 carries tomato to fridge, and robot3 moves to the light switch.

If Gazebo opens but the expected `/world/lammap_demo/set_pose` service name differs, the launcher now attempts to auto-discover the available `/world/.../set_pose` service automatically.

Important package note: if `gz sim --versions` prints `Invalid arguments`, you likely installed Gazebo Classic (`gazebo11`) instead of Gazebo Sim. The working installation for this artefact used `gz-harmonic`.

## Run the Local LLM Smoke Test

Ollama example:

```bash
ollama serve
ollama pull llama3.1:8b
.venv/bin/python scripts/check_local_llm.py \
  --base-url http://localhost:11434/v1 \
  --model llama3.1:8b
```

Open WebUI example:

```bash
.venv/bin/python scripts/check_local_llm.py \
  --base-url http://localhost:3000/api \
  --api-key <open-webui-token-if-required> \
  --model llama3.1:8b
```

Then run LaMMA-P with the local endpoint:

```bash
.venv/bin/python scripts/pddlrun_llmseparate.py \
  --floor-plan 6 \
  --base-url http://localhost:11434/v1 \
  --gpt-version llama3.1:8b
```

## Type a New Natural-Language Command Without Paid APIs

```bash
.venv/bin/python scripts/run_natural_command.py \
  --command "put the apple and tomato in the fridge and switch off the light" \
  --robots 1,2,3 \
  --output-dir outputs/natural_command_demo
```

This writes:

- `outputs/natural_command_demo/parsed_task.json`
- `outputs/natural_command_demo/allocation_result.json`
- `outputs/natural_command_demo/allocation_result.csv`

## Constraints and Honest Limitations

- The full LaMMA-P PDDL pipeline depends on Fast Downward and local model quality.
- Open WebUI and Ollama endpoint formats can vary by version; this artefact uses OpenAI-compatible `/v1` style clients.
- AI2-THOR can fail on unsupported OS/build combinations. Version `ai2thor==4.2.0` was pinned because newer versions pointed to missing macOS simulator builds during testing.
- Full Gazebo GUI evidence still depends on `gz` plus working WSLg or native Ubuntu graphics.
- The verification container used here blocked `sudo` privilege elevation and outbound package downloads, so Gazebo install and AI2-THOR rerun could not be completed inside that container itself.
- Physical LIMO deployment is documented as the next stage; this completed artefact provides the simulation, optimisation, and local-LLM foundation.

## Why This Meets the Project Brief

- LO1: clear aim, problem, SMART objectives, feasible scope and evaluation plan.
- LO2: literature review ideas are directly implemented in the artefact.
- LO3: documented plan, risks, constraints and reproducible commands.
- LO4: non-trivial robotic software solution integrating LLMs, symbolic planning, optimisation and simulation.
- LO5: technical design, methodology, evidence, results and limitations are documented for the dissertation.
- LO7: local/no-paid-API implementation and simulation fallback demonstrate independent resource management.

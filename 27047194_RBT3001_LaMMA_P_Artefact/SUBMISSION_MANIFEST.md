# Submission Manifest

Recommended ZIP name:

`27047194_RBT3001_LaMMA_P_Artefact_WINDOWS_WSL_VERIFIED.zip`

Previous clean package retained for traceability:

`27047194_RBT3001_LaMMA_P_Artefact_CLEAN.zip`

## Included Examiner-Facing Material

- `EXAMINER_README.md`: start here; contains setup, run commands, constraints and marking-outcome mapping.
- `README.md`: project overview and quickstart.
- `requirements.txt`: Python dependencies, including pinned `ai2thor==4.2.0`.
- `configs/local_llm.env.example`: local LLM/Open WebUI/Ollama environment example.
- `docs/dissertation_project_blueprint.md`: formal project blueprint for dissertation chapters.
- `docs/dissertation_ai_prompt.md`: full dissertation-generation prompt for ChatGPT or another AI.
- `docs/literature_review_extracted.txt`: extracted text from the student's reviewed proposal/literature review.
- `scripts/constraint_optimizer.py`: deterministic MILP allocation layer.
- `scripts/demo_ai2thor_video.py`: AI2-THOR multi-agent video demo.
- `scripts/check_local_llm.py`: local LLM smoke test.
- `scripts/run_natural_command.py`: typed natural-language command runner.
- `scripts/setup_ubuntu.sh`: one-command Ubuntu setup for Python dependencies and Gazebo Sim.
- `scripts/verify_ubuntu_pipeline.sh`: end-to-end non-GUI verification script for Ubuntu.
- `docs/project_status_answers.md`: precise answers about novelty, Gazebo scope, command entry, ML/training and GPU.
- `gazebo_demo/`: Gazebo Sim world, playback script and checker for Ubuntu/Gazebo demonstration.
- `scripts/pddlrun_llmseparate.py`: LaMMA-P planner modified for local OpenAI-compatible APIs.
- `scripts/plantocode.py`: plan-to-code script modified for local OpenAI-compatible APIs.
- `outputs/optimizer/FloorPlan15vague/allocation_result.json`: quantitative optimiser evidence.
- `outputs/optimizer/FloorPlan15vague/allocation_result.csv`: tabular optimiser evidence.
- `outputs/ai2thor_demo/*.mp4`: generated robot video evidence.
- `outputs/ai2thor_demo/index.html`: local gallery for videos.
- `outputs/ai2thor_demo/preview_contact_sheet.jpg`: still-frame evidence summary.
- `outputs/natural_command_demo/parsed_task.json`: evidence of a newly typed natural phrase being parsed.
- `outputs/natural_command_demo/allocation_result.json`: optimiser output for the typed phrase.
- `outputs/gazebo_demo/gazebo_launch_log.txt`: Gazebo verification log for the Linux packaging pass.
- `outputs/gazebo_demo/gazebo_demo_notes.md`: Gazebo status, limits and examiner rerun guidance.
- `api_key.example.txt`: placeholder only; no paid API key is included.

## Excluded From ZIP

The following are intentionally excluded because they are generated, bulky or machine-specific:

- `.venv/`
- `venv/`
- `.ai2thor/`
- `__pycache__/`
- `.DS_Store`
- downloaded source archive ZIPs
- `api_key.txt`
- raw AI2-THOR frame folders, because the MP4s and contact sheet are included instead

The examiner can recreate the environment using `requirements.txt`. AI2-THOR may download a platform-specific Unity build on first run.

## Verified Evidence

Optimiser command:

```bash
.venv/bin/python scripts/constraint_optimizer.py \
  --task-file data/final_test/FloorPlan15vague.json \
  --output-dir outputs/optimizer/FloorPlan15vague
```

Verified metrics:

- Greedy travel-cost proxy: `21.060`
- Optimised travel-cost proxy: `18.209`
- Improvement: `13.54%`
- Optimised success proxy: `1.0`

Video evidence:

- `outputs/ai2thor_demo/video_agent_1.mp4`
- `outputs/ai2thor_demo/video_agent_2.mp4`
- `outputs/ai2thor_demo/video_top_view.mp4`

Compile check:

```bash
.venv/bin/python -m py_compile \
  scripts/demo_ai2thor_video.py \
  scripts/constraint_optimizer.py \
  scripts/check_local_llm.py \
  scripts/pddlrun_llmseparate.py \
  scripts/plantocode.py
```

Result: passed, with only pre-existing regex escape warnings in `pddlrun_llmseparate.py`.

Typed command verification:

```bash
.venv/bin/python scripts/run_natural_command.py \
  --command "put the apple and tomato in the fridge and switch off the light" \
  --robots 1,2,3 \
  --output-dir outputs/natural_command_demo
```

Verified typed-command metrics:

- Greedy travel-cost proxy: `24.382`
- Optimised travel-cost proxy: `22.218`
- Success proxy: `1.0`

Gazebo asset verification:

```bash
.venv/bin/python gazebo_demo/scripts/check_gazebo_assets.py
bash -n gazebo_demo/scripts/run_gz_sim_demo.sh
```

Result: asset check passed and launcher syntax passed. A later Windows 11 + WSL2 Ubuntu verification launched Gazebo Sim successfully with `gz sim --versions -> 8.11.0`. See `outputs/gazebo_demo/`.

Ubuntu / WSL2 examiner workflow:

```bash
unzip 27047194_RBT3001_LaMMA_P_Artefact_WINDOWS_WSL_VERIFIED.zip -d ~/projects
cd ~/projects/27047194_RBT3001_LaMMA_P_Artefact
bash scripts/setup_ubuntu.sh
bash scripts/verify_ubuntu_pipeline.sh
cd gazebo_demo
bash scripts/run_gz_sim_demo.sh
```

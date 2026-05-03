# Project Status Answers: Novelty, Gazebo, Commands, ML and GPU

## 1. Does this project do anything novel?

Yes, but the novelty must be stated precisely.

It does not claim to invent LaMMA-P. The original LaMMA-P contribution is the LLM-driven PDDL planner evaluated on MAT-THOR/AI2-THOR tasks.

This project's distinct contribution is an engineering and research extension of LaMMA-P:

- It removes paid API dependence by adapting the LLM scripts to local OpenAI-compatible endpoints such as Open WebUI/Ollama.
- It adds a deterministic constraint-driven allocation layer in `scripts/constraint_optimizer.py`.
- It turns LLM/PDDL task goals into auditable robot-subtask assignments using MILP/ILP.
- It compares optimiser allocation against a greedy baseline.
- It provides repeatable AI2-THOR video evidence and saved result files for dissertation evaluation.
- It adds a typed natural-language command entry point in `scripts/run_natural_command.py`.

The strongest dissertation claim is therefore:

> This project extends LaMMA-P by replacing unstable free-text task allocation with a reproducible MILP allocation layer and by making the LLM interface deployable with local/no-paid-API models.

That is a credible undergraduate project contribution. It is not the same as claiming a new state-of-the-art planner.

## 2. Where is the Gazebo demonstration?

There is now a Gazebo Sim demonstration folder:

- `gazebo_demo/worlds/lammap_gazebo_demo.sdf`
- `gazebo_demo/scripts/run_gz_sim_demo.sh`
- `gazebo_demo/scripts/check_gazebo_assets.py`
- `gazebo_demo/README.md`

This is a real Gazebo Sim world and playback route. It visualises the typed command:

```text
put the apple and tomato in the fridge and switch off the light
```

It moves three LIMO-like robot models and task objects inside Gazebo.

In the final Linux packaging pass on `2026-05-02`, the Gazebo world file and launcher script were rechecked successfully, but the GUI could not be launched in that restricted container because `gz` was not installed there and display probing failed (`glxinfo -B -> unable to open display :1`).

After that, the same Gazebo route was verified successfully on the actual Windows 11 + WSL2 Ubuntu target machine. `gz sim --versions` returned `8.11.0`, Gazebo Sim opened under WSLg, and the scripted mission playback executed.

Supporting evidence is included in:

- `outputs/gazebo_demo/gazebo_launch_log.txt`
- `outputs/gazebo_demo/gazebo_demo_notes.md`

The completed simulation evidence is AI2-THOR, not Gazebo:

- `scripts/demo_ai2thor_video.py`
- `outputs/ai2thor_demo/video_agent_1.mp4`
- `outputs/ai2thor_demo/video_agent_2.mp4`
- `outputs/ai2thor_demo/video_top_view.mp4`

Why not Gazebo in the current artefact:

- This macOS workspace does not have ROS 2, Gazebo, Ignition or `gz` installed.
- `ros2`, `gazebo`, `gz` and `ign` are not available in the current environment.
- Gazebo/LIMO work normally belongs on a Linux/Ubuntu ROS 2 machine, not this macOS AI2-THOR setup.

How to present this:

- Do not pretend that Gazebo was launched on macOS.
- Say that a Gazebo Sim world and playback route were added, structurally validated, and then successfully launched on WSL2 Ubuntu with Gazebo Sim installed.
- Use AI2-THOR as the fully verified simulation demonstration.
- Use the optimiser as the technical contribution that is simulator-independent and transferable to ROS 2/Gazebo.

If Gazebo becomes required later, the next implementation stage should be a ROS 2 package that subscribes to the optimiser output and dispatches Nav2 goals to LIMO robot namespaces.

## 3. Where are commands typed? Are they predetermined or can new natural phrases be typed?

There are now three command paths.

### A. Original LaMMA-P dataset commands

The original repo uses predefined dataset tasks such as:

- `data/final_test/FloorPlan6.json`
- `data/final_test/FloorPlan15vague.json`

These are run by floor-plan number:

```bash
.venv/bin/python scripts/pddlrun_llmseparate.py --floor-plan 6
```

### B. Local LLM natural-language pipeline

New natural phrases can be sent through a local OpenAI-compatible model:

```bash
.venv/bin/python scripts/pddlrun_llmseparate.py \
  --floor-plan 6 \
  --base-url http://localhost:11434/v1 \
  --gpt-version llama3.1:8b
```

This depends on the local model and prompt quality. It is the closest path to the original LaMMA-P natural-language-to-PDDL pipeline.

### C. New lightweight typed-command optimiser path

This project adds a no-paid-API command runner:

```bash
.venv/bin/python scripts/run_natural_command.py \
  --command "put the apple and tomato in the fridge and switch off the light" \
  --robots 1,2,3 \
  --output-dir outputs/natural_command_demo
```

It parses a new phrase into structured task goals, then runs the MILP optimiser. Example output:

- move Apple to Fridge;
- move Tomato to Fridge;
- switch off LightSwitch;
- assign each subtask to a feasible robot.

This path is intentionally smaller than a full LLM parser, but it is robust and reproducible for demonstration.

It was rerun successfully in the final Linux packaging pass:

- parsed `Fridge <- Apple, Tomato`
- parsed `LightSwitch -> OFF`
- optimiser success proxy `1.0`
- greedy travel-cost proxy `24.382`
- optimised travel-cost proxy `22.218`

## 4. Does the project require machine learning? What would be trained?

The completed project uses machine learning through inference, not training.

No model is trained in the completed artefact.

The "learning-assisted" part is:

- use of an LLM for natural-language interpretation when Open WebUI/Ollama is connected;
- use of LaMMA-P-style prompts for semantic decomposition;
- local model inference rather than paid cloud inference.

The optimiser itself is not machine learning. It is mathematical optimisation using MILP.

What could be trained in a larger future version:

- a small intent/entity parser trained on natural-language robot commands;
- a LoRA/fine-tuned local LLM for JSON/PDDL generation;
- a task success predictor estimating execution risk;
- a learned travel-time model from real robot logs;
- a policy model for low-level control, though this is outside the current project.

For this dissertation, the stronger argument is:

> The project does not need to train a model to be successful. It integrates pretrained local LLM inference with symbolic planning and deterministic optimisation.

In the final Linux packaging pass, the local LLM smoke-test script itself was improved so it can talk to OpenAI-compatible endpoints even if the `openai` Python package is missing, using a direct HTTP fallback. A live endpoint was not available in the restricted packaging environment, so that check remains optional for the examiner.

## 5. Why did the professor suggest a good machine with GPU?

A good GPU is useful for local LLM inference and robotics simulation.

Reasons:

- Running Open WebUI/Ollama with 7B, 8B, 14B or larger instruction models is much faster with GPU acceleration.
- Larger local models are more reliable at producing valid JSON/PDDL than small CPU-only models.
- AI2-THOR and Gazebo both use 3D simulation; rendering and physics benefit from GPU resources.
- ROS 2/Gazebo with multiple robots, sensors, cameras and Nav2 can be heavy.
- If future work trains or fine-tunes a parser/LLM adapter, GPU memory becomes important.

In this completed project, GPU is helpful but not strictly required for:

- running the MILP optimiser;
- reading existing outputs;
- using included MP4 evidence;
- running small local models slowly on CPU.

GPU becomes much more important for:

- fast local LLM inference;
- larger models;
- full Gazebo/LIMO simulation;
- any future fine-tuning.

## 6. Best honest top-grade positioning

The strongest position is:

1. The original LaMMA-P is the research foundation.
2. This project extends it for local/no-paid-API operation.
3. The project adds a deterministic MILP allocation module that directly addresses a limitation identified in the literature review.
4. The project provides reproducible simulation evidence in AI2-THOR.
5. Gazebo/LIMO integration is a documented future stage, not a completed result.
6. The project uses pretrained machine learning models through inference; no training is required for the submitted artefact.

This is honest, defensible, and much stronger than pretending the artefact includes ROS 2/Gazebo or physical LIMO work that has not actually been implemented.

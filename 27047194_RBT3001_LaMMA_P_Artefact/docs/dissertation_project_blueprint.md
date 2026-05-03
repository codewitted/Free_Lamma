# Dissertation Project Blueprint

Project title: Learning-Assisted Multi-Robot Coordination: Integrating Local LLMs with PDDL and Constraint-Driven Optimisation for Heterogeneous Robot Teams

## 1. Problem Statement

Multi-robot task planning becomes difficult when a human gives high-level natural language goals, because the system must interpret ambiguous instructions, allocate subtasks to heterogeneous robots, and produce executable behaviour without violating capability, resource, or ordering constraints.

LaMMA-P is a strong starting point because it combines LLM task reasoning with PDDL and Fast Downward planning. The project contribution is to make that pipeline reproducible without paid APIs and to strengthen allocation reliability using a deterministic constraint-driven optimiser.

## 2. Aim

Design, implement, and evaluate a local LLM-assisted PDDL planning framework enhanced with MILP-based task allocation for reliable multi-robot coordination in AI2-THOR, with a migration path to ROS 2/Gazebo/LIMO robots.

## 3. SMART Objectives

O1: Adapt LaMMA-P to run with local OpenAI-compatible LLM services such as Open WebUI or Ollama, avoiding paid API dependency.

O2: Preserve the LaMMA-P natural-language-to-PDDL workflow while documenting the setup, inputs, outputs, and failure modes.

O3: Implement a constraint-driven optimiser that converts task goals into robot-subtask allocations subject to skill feasibility, availability, battery proxy, mass capacity, and workload limits.

O4: Produce repeatable AI2-THOR demonstrations showing multi-agent pickup/carry/place behaviours and saved videos.

O5: Evaluate the hybrid system against baseline allocation using success proxy, feasibility rate, travel-cost proxy, workload balance, execution evidence, and video artefacts.

O6: Package the source code, commands, logs, plots/tables, and dissertation-ready methodology notes as supporting documentation.

## 4. Literature Review Linkage

The literature review argues that PDDL provides correctness and structure, while LLMs provide semantic interpretation. It also identifies a weakness in LLM-only allocation: generated plans can be unstable, wrongly formatted, or insensitive to robot capability/resource constraints.

This artefact directly answers that gap:

- LaMMA-P/SMART-LLM idea: use LLMs for semantic decomposition of natural-language tasks.
- PDDL/Fast Downward idea: preserve symbolic planning for explicit action feasibility.
- Multi-robot coordination literature: add deterministic allocation rather than trusting free-text LLM assignments.
- MILP contribution: make allocation auditable, reproducible, and measurable.
- Local model constraint: remove paid API reliance using Open WebUI/Ollama compatible endpoints.

## 5. Implemented Artefact Components

### 5.1 Local LLM Interface

Modified:

- `scripts/pddlrun_llmseparate.py`
- `scripts/plantocode.py`

The scripts now accept local OpenAI-compatible APIs via `--base-url`, `LOCAL_LLM_BASE_URL`, or `OPENAI_BASE_URL`. When a local endpoint is used, no paid API key file is required; a dummy local key is used unless the service requires a token.

Example with Ollama:

```bash
export LOCAL_LLM_BASE_URL=http://localhost:11434/v1
export LOCAL_LLM_API_KEY=local-no-key-required
.venv/bin/python scripts/pddlrun_llmseparate.py --floor-plan 6 --base-url "$LOCAL_LLM_BASE_URL" --gpt-version llama3.1:8b
```

Example with Open WebUI:

```bash
export LOCAL_LLM_BASE_URL=http://localhost:3000/api
export LOCAL_LLM_API_KEY=<open-webui-token-if-required>
.venv/bin/python scripts/pddlrun_llmseparate.py --floor-plan 6 --base-url "$LOCAL_LLM_BASE_URL" --gpt-version llama3.1:8b
```

### 5.2 Constraint-Driven Optimiser

Added:

- `scripts/constraint_optimizer.py`

The optimiser reads MAT-THOR task JSON, infers subtasks from goal states, loads robot skill definitions from `resources/robots.py`, then solves a binary MILP assignment problem.

Decision variable:

`x[i,r] = 1` if subtask `i` is assigned to robot `r`; otherwise `0`.

Constraints:

- each subtask must be assigned exactly once;
- assignment is forbidden if the robot lacks the required skill;
- assignment is forbidden if task load exceeds robot capacity;
- assignment respects a battery threshold proxy;
- workload per robot is capped to avoid overloading a single agent.

Objective:

Minimise travel proxy cost plus availability/workload penalties minus task utility.

Run:

```bash
.venv/bin/python scripts/constraint_optimizer.py \
  --task-file data/final_test/FloorPlan15vague.json \
  --output-dir outputs/optimizer/FloorPlan15vague
```

Outputs:

- `outputs/optimizer/FloorPlan15vague/allocation_result.json`
- `outputs/optimizer/FloorPlan15vague/allocation_result.csv`

Current sample result:

- Greedy travel-cost proxy: `21.060`
- Optimised travel-cost proxy: `18.209`
- Improvement: approximately `13.5%`
- Feasible tasks: `4/4`

### 5.3 AI2-THOR Video Demonstration

Added:

- `scripts/demo_ai2thor_video.py`

This provides a no-paid-API demonstration of two AI2-THOR agents executing pickup/carry/place behaviours. It saves first-person agent videos, a top-view video, raw frames, and an HTML gallery.

Run:

```bash
.venv/bin/python scripts/demo_ai2thor_video.py \
  --scene FloorPlan1 \
  --output-dir outputs/ai2thor_demo \
  --fps 8
```

Outputs:

- `outputs/ai2thor_demo/video_agent_1.mp4`
- `outputs/ai2thor_demo/video_agent_2.mp4`
- `outputs/ai2thor_demo/video_top_view.mp4`
- `outputs/ai2thor_demo/index.html`
- `outputs/ai2thor_demo/preview_contact_sheet.jpg`

### 5.4 Gazebo Sim Demonstration Route

Added:

- `gazebo_demo/worlds/lammap_gazebo_demo.sdf`
- `gazebo_demo/scripts/run_gz_sim_demo.sh`
- `gazebo_demo/scripts/check_gazebo_assets.py`

This provides a Gazebo Sim visualisation route for the typed natural-language command evidence. It uses LIMO-like robot models and visible task objects in a Gazebo world. Robot poses and carried object poses are played through Gazebo Transport services.

Local validation passed for the SDF structure and shell script syntax. A full Gazebo GUI run requires an Ubuntu machine with Gazebo Sim installed; this macOS host does not include `gz`, `gazebo`, `ros2`, Docker or Homebrew.

## 6. Evaluation Plan

### Research Questions

RQ1: Can a local LLM-assisted LaMMA-P pipeline generate usable symbolic task plans without paid APIs?

RQ2: Does a MILP allocation layer improve allocation quality compared with a greedy baseline?

RQ3: Can the resulting system produce observable multi-agent robot behaviour in AI2-THOR?

### Metrics

- Task feasibility rate: proportion of subtasks assigned to capable robots.
- Success proxy: feasible subtasks divided by total subtasks.
- Travel-cost proxy: deterministic spatial cost for robot-object-target assignment.
- Workload balance: standard deviation of assigned subtasks per robot.
- Execution evidence: generated videos and frame counts.
- Reproducibility: fixed commands, saved JSON/CSV outputs, no paid API dependency.

### Baselines

- Greedy allocation: assign each task to the least-loaded capable robot with lowest local cost.
- Optimised allocation: solve the MILP objective with feasibility and workload constraints.
- AI2-THOR behavioural demo: qualitative evidence of multi-agent execution.

## 7. Dissertation Chapter Mapping

Introduction:
Use the problem statement, aim, SMART objectives, and motivation from the literature review.

Literature Review:
Use the existing review and strengthen the critical link between LaMMA-P, SMART-LLM, PDDL, Fast Downward, market-based allocation, and MILP/constraint optimisation.

Requirements Analysis:
Discuss no-paid-API requirement, local model compatibility, reproducible simulation, heterogeneous robot skills, measurable allocation quality, and safe fallback to simulation.

Design and Methodology:
Present the hybrid architecture: natural-language command, local LLM parser, PDDL generator, symbolic planner, MILP allocator, AI2-THOR/ROS executor, evaluation logger.

Implementation:
Document the modified scripts, the optimiser, the AI2-THOR demo runner, dependency pinning, and generated artefacts.

Results and Discussion:
Report optimiser metrics, generated video evidence, failure cases in malformed dataset files, local model constraints, and comparison with greedy baseline.

Conclusion:
State which objectives were achieved, what remains for ROS 2/Gazebo/LIMO deployment, and what future improvements would increase real-robot robustness.

## 8. Known Constraints and Honest Scope

- The current fully verified executable artefact is AI2-THOR simulation plus an optimisation layer.
- A Gazebo Sim world/playback route is included and structurally validated, but requires Ubuntu/Gazebo for GUI execution.
- Physical LIMO deployment is a future integration stage unless hardware access is available.
- Open WebUI/Ollama quality depends on the chosen local model; larger instruction models should outperform small models for PDDL formatting.
- Some MAT-THOR JSON files are malformed or JSON-lines style, so the optimiser includes tolerant parsing for robustness.
- Fast Downward still needs to be installed separately if full PDDL plan generation is required.

## 9. Rubric Alignment

C1: Clear problem, aim, SMART objectives, and feasible scope are defined.

C2: Literature review ideas directly determine the artefact: LLM semantics, PDDL formality, MILP allocation, and local deployment constraints.

C3: Technical design includes modules, constraints, objective function, commands, and artefact outputs.

C4: Evaluation uses quantitative optimiser metrics and observable AI2-THOR video evidence.

C5: The final dissertation can conclude from evidence rather than description alone.

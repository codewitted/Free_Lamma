# Dissertation Writing Prompt for ChatGPT or Another AI

Use this prompt to generate the final RBT3001 dissertation after the project is complete. Paste it into ChatGPT or another capable writing model together with the key evidence files from this repository.

---

You are an expert UK university robotics dissertation writer and technical editor. Write a polished, distinction-level undergraduate dissertation for RBT3001 Robotics Project Assessment 2.

The dissertation must follow this required structure:

1. Introduction
2. Literature Review
3. Requirements Analysis
4. Design and Methodology
5. Implementation
6. Results and Discussion
7. Conclusion

The writing must target the highest band of the provided rubric:

- academically argued rationale and clear SMART objectives;
- comprehensive and critical literature review that directly informs the method;
- precise technical specification and sophisticated system design;
- robust, evidence-driven evaluation;
- clear discussion of constraints, limitations, and future work;
- professional technical communication.

Project title:

Learning-Assisted Multi-Robot Coordination: Integrating Local Large Language Models with PDDL and Constraint-Driven Optimisation for Heterogeneous Robot Teams

Project context:

This project extends the LaMMA-P architecture by Zhang et al. (2025), which uses language models to decompose natural-language robot tasks into PDDL-style symbolic plans and uses classical planning ideas to improve reliability. The student project adapts the repository for no-paid-API operation using local OpenAI-compatible LLM endpoints such as Open WebUI or Ollama, adds a deterministic MILP/ILP allocation layer, and demonstrates multi-agent execution in AI2-THOR with saved videos.

Use the following source files as the factual basis:

- `docs/literature_review_extracted.txt`
- `docs/dissertation_project_blueprint.md`
- `EXAMINER_README.md`
- `README.md`
- `scripts/constraint_optimizer.py`
- `scripts/demo_ai2thor_video.py`
- `scripts/pddlrun_llmseparate.py`
- `scripts/plantocode.py`
- `outputs/optimizer/FloorPlan15vague/allocation_result.json`
- `outputs/optimizer/FloorPlan15vague/allocation_result.csv`
- `outputs/ai2thor_demo/video_agent_1.mp4`
- `outputs/ai2thor_demo/video_agent_2.mp4`
- `outputs/ai2thor_demo/video_top_view.mp4`
- `outputs/ai2thor_demo/preview_contact_sheet.jpg`
- `gazebo_demo/worlds/lammap_gazebo_demo.sdf`
- `gazebo_demo/scripts/run_gz_sim_demo.sh`
- `docs/project_status_answers.md`

Core project aim:

To design, implement and evaluate a local LLM-assisted PDDL planning framework enhanced by a constraint-driven optimisation layer that improves reliable multi-robot task allocation and demonstrates executable multi-agent behaviour in AI2-THOR, with a documented path toward ROS 2/Gazebo/LIMO deployment.

SMART objectives:

1. Adapt LaMMA-P to support local OpenAI-compatible LLM services, avoiding paid APIs.
2. Preserve the natural-language-to-PDDL planning flow while documenting setup, inputs, outputs and failure modes.
3. Implement a MILP allocation layer that assigns subtasks to robots subject to skill feasibility, availability, battery proxy, mass capacity and workload constraints.
4. Produce AI2-THOR demonstrations showing multi-agent pickup/carry/place behaviour and saved MP4 evidence.
5. Evaluate the hybrid system against a greedy baseline using success proxy, feasibility rate, travel-cost proxy, workload balance and execution evidence.
6. Package code, documentation, outputs and limitations for examiner reproduction.

Technical contribution:

The central contribution is not merely running LaMMA-P, but strengthening it with a deterministic allocation layer. The optimiser converts task goals into subtasks, loads heterogeneous robot skill definitions from `resources/robots.py`, defines binary assignment variables `x[i,r]`, and solves a MILP using SciPy/HiGHS. It enforces one assignment per subtask, skill compatibility, mass capacity, battery proxy and workload caps. It minimises a cost combining travel proxy, availability and workload penalties while rewarding task utility.

Important quantitative result:

For `data/final_test/FloorPlan15vague.json`, the optimiser produced:

- Greedy travel-cost proxy: 21.060
- Optimised travel-cost proxy: 18.209
- Improvement: 13.54%
- Optimised success proxy: 1.0
- Feasible tasks: 4/4

AI2-THOR evidence:

The project generated:

- `video_agent_1.mp4`
- `video_agent_2.mp4`
- `video_top_view.mp4`
- `index.html`
- `preview_contact_sheet.jpg`

These show two AI2-THOR agents executing pickup/carry/place tasks. The demonstration does not require paid APIs or Fast Downward.

Gazebo evidence:

The repository also contains a Gazebo Sim demonstration route under `gazebo_demo/`. It includes a real SDF world and a Gazebo Transport playback script that visualises robot1 carrying apple to fridge, robot2 carrying tomato to fridge, and robot3 moving to the light switch. The Gazebo assets and script syntax were validated locally, but the GUI was not launched because the macOS host did not have `gz`, `gazebo`, `ros2`, Docker or Homebrew installed. Present this honestly as a Gazebo-ready demonstration route requiring Ubuntu/Gazebo, while AI2-THOR remains the fully verified local simulation evidence.

Important development constraints to discuss honestly:

The project moved across Linux, Windows and macOS environments. AI2-THOR was difficult because simulator builds are OS- and version-specific. Newer `ai2thor` versions pointed to missing macOS builds, so `ai2thor==4.2.0` was pinned. Open WebUI/Ollama configuration also required care because local endpoints vary by version. Fast Downward remains needed for the full LaMMA-P symbolic planning workflow, while the included AI2-THOR demo and optimiser are self-contained evidence of the implemented contribution. A Gazebo Sim world/playback route was added but requires an Ubuntu/Gazebo machine for GUI execution. Physical LIMO deployment is future work unless hardware access is available.

Required tone:

Use formal academic British English. Be clear, precise and technical. Avoid exaggeration. Make strong claims only where evidence supports them. Where the project is simulation-only, say so honestly and explain why simulation is a valid evaluation stage. Present constraints as engineering challenges that were overcome or bounded, not excuses.

Expected dissertation length:

Write enough for a substantial undergraduate robotics dissertation. Aim for a full technical report style, not a short essay. Include tables where useful. Include figure captions and placeholders such as `[Insert system architecture diagram here]`, `[Insert optimiser result table here]`, and `[Insert AI2-THOR video contact sheet here]`.

Citation requirements:

Use and cite the following works in Harvard or IEEE style:

- McDermott et al. (1998), PDDL.
- Helmert (2006), Fast Downward.
- Zlot and Stentz (2006), market-based multi-robot coordination.
- Dias et al. or related auction-based multi-robot coordination work where appropriate.
- Torreño et al. (2017), cooperative multi-agent planning.
- Kannan et al. (2023), SMART-LLM.
- Zhang et al. (2024/2025), LaMMA-P.

Write each chapter as follows:

Introduction:

- Introduce multi-robot coordination and the gap between natural language instructions and formal robot execution.
- Explain why LLMs are useful but unreliable alone.
- Explain why PDDL is structured but inflexible alone.
- Present the project aim, SMART objectives and contribution.

Literature Review:

- Critically compare symbolic planning, LLM-assisted planning, and optimisation-based multi-robot allocation.
- Show why LaMMA-P is a suitable base.
- Identify the exact gap: LLM-generated allocation instability and lack of deterministic constraint satisfaction.
- Explain why local LLMs matter for cost, reproducibility and privacy.
- End by deriving the chosen method from the literature.

Requirements Analysis:

- Functional requirements: local LLM interface, PDDL compatibility, optimiser, AI2-THOR execution, outputs/logs.
- Non-functional requirements: reproducibility, no paid APIs, explainability, OS constraints, safety, simulation fallback.
- Evaluation requirements and success criteria.

Design and Methodology:

- Present the architecture: natural language input, local LLM, PDDL generation, symbolic planning, MILP allocation, AI2-THOR execution, logging/evaluation.
- Describe the MILP formulation formally.
- Describe baselines and metrics.
- Include risk analysis and mitigation.

Implementation:

- Explain code modifications in `pddlrun_llmseparate.py` and `plantocode.py`.
- Explain `check_local_llm.py`.
- Explain `constraint_optimizer.py`.
- Explain `demo_ai2thor_video.py`.
- Discuss dependency pinning, especially `ai2thor==4.2.0`.
- Explain how outputs are generated.

Results and Discussion:

- Present the optimiser result table and calculate the 13.54% improvement.
- Discuss success proxy and feasibility.
- Discuss video evidence and qualitative behaviour.
- Discuss limitations: proxy travel model, simulation scope, local model quality, Fast Downward setup, physical LIMO future work.
- Compare back to literature: the optimiser addresses the instability gap in LLM-only allocation.

Conclusion:

- State objectives achieved.
- Explain contribution clearly.
- Reflect on development process across Linux/Windows/macOS and how issues were overcome.
- Give future work: full ROS 2/Gazebo integration, physical LIMO deployment, richer maps, real localisation, larger benchmark study, improved local models, formal PDDL validation.

Output:

Produce the full dissertation draft with headings, subheadings, tables, figure placeholders, equations for MILP, and a reference list. Make it suitable to paste into the university dissertation template and refine manually.

---

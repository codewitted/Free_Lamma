# Open LaMMA-R Dissertation Draft

## 1. Abstract

This project presents Open LaMMA-R, a local-LLM, PDDL and MILP-based multi-robot coordination framework for LIMO robots in AI2-THOR Floor 6 and ROS 2. The system converts natural-language instructions into validated JSON, generates symbolic PDDL problems, plans with Fast Downward, refines task allocation using MILP optimisation, and executes through dry-run, AI2-THOR or ROS 2-compatible layers.

## 2. Introduction

LLM-only robot planning is flexible but unreliable: outputs may be malformed, infeasible or inconsistent across runs. Classical PDDL planning provides symbolic guarantees but is hard for non-expert users to specify. Open LaMMA-R combines both approaches and adds mathematical optimisation for multi-robot allocation.

## 3. Literature Review

The work builds on PDDL, Fast Downward, SMART-LLM, LaMMA-P, market-based coordination and optimisation-based multi-robot task allocation. LaMMA-P demonstrated the value of LM-driven PDDL planning in MAT-THOR, while this project targets a free/local, GUI-driven, ROS 2/LIMO-ready dissertation artefact.

## 4. Requirements

The system must use free/local models where possible, validate LLM output, generate valid PDDL, support Fast Downward, allocate tasks with MILP, provide a GUI, and degrade gracefully when optional robotics tools are unavailable.

## 5. System Design

The design has five layers: LLM parsing, schema validation, symbolic planning, MILP allocation and execution. A FastAPI backend exposes the pipeline to a React dashboard. Dry-run mode is the reproducible baseline; AI2-THOR and ROS 2 extend it toward embodied robotics.

## 6. Implementation

The backend is modular: `llm_gateway`, `parser`, `pddl`, `planner`, `optimiser`, `executor` and `api`. The frontend visualises JSON, PDDL, plans, allocation, logs and metrics. Scenarios and evaluation scripts create repeatable evidence.

## 7. Evaluation Methodology

Experiments compare LLM-only, PDDL-only, LLM+PDDL and LLM+PDDL+MILP across ten scenarios. Metrics include task success rate, malformed JSON rate, PDDL validity, planner success, allocation feasibility, travel cost, makespan, planning time, optimisation time and utility.

## 8. Results

Results are generated into `evaluation/results/` and plots into `evaluation/plots/`. The expected finding is that strict validation reduces malformed output risk, PDDL improves feasibility, and MILP improves allocation consistency and utility.

## 9. Discussion

Local LLMs reduce cost and privacy concerns. PDDL gives explainability and symbolic checks. MILP produces deterministic allocation decisions with clear constraint explanations. The GUI improves inspectability for supervisors and demonstrators.

## 10. Limitations

Full AI2-THOR, Gazebo and physical LIMO execution require local installation and hardware access. The current embodied layers are fallback-safe and ready for progressive replacement with real robot mappings.

## 11. Conclusion

Open LaMMA-R turns the LaMMA-P concept into a practical, free/local, inspectable and dissertation-ready robotics coordination system with a clear original MILP contribution.

## 12. References

- Helmert, M. (2006). The Fast Downward Planning System.
- Kannan, S. S. et al. (2023). SMART-LLM.
- McDermott, D. et al. (1998). PDDL.
- Zhang, X. et al. (2025). LaMMA-P.
- Zlot, R. and Stentz, A. (2006). Market-based Multirobot Coordination.


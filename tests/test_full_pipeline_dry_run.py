from backend.executor.dry_run_executor import execute_plan
from backend.optimiser.milp_allocator import allocate_tasks
from backend.parser.fallback_parser import parse_rule_based
from backend.pddl.problem_generator import generate_problem
from backend.planner.fast_downward_client import heuristic_plan_from_mission


def test_full_pipeline_runs_in_dry_run_mode():
    mission = parse_rule_based("blue box coffee mug inspect corridor").model_dump()
    allocation = allocate_tasks(mission)
    assert allocation["allocation"]
    pddl = generate_problem(mission)
    assert "open_lamma_r" in pddl
    actions = heuristic_plan_from_mission(mission)
    result = execute_plan(actions)
    assert result["status"] == "success"


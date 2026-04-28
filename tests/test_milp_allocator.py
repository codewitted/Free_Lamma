from backend.optimiser.milp_allocator import allocate_tasks
from backend.parser.fallback_parser import parse_rule_based


def test_milp_assigns_each_task_once():
    mission = parse_rule_based("blue box coffee mug inspect corridor").model_dump()
    result = allocate_tasks(mission)
    assigned = [item for item in result["allocation"] if item["assigned_robot"]]
    assert len(assigned) == len(mission["tasks"])


def test_robot_without_capability_is_rejected():
    mission = parse_rule_based("blue box").model_dump()
    mission["robots"][0]["capabilities"] = ["navigate"]
    mission["robots"][1]["capabilities"] = ["navigate", "pickup", "drop"]
    result = allocate_tasks(mission)
    assert result["allocation"][0]["assigned_robot"] != "robot1"


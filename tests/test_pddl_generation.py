from backend.parser.fallback_parser import parse_rule_based
from backend.pddl.problem_generator import generate_problem
from backend.pddl.pddl_validator import validate_pddl_text


def test_valid_json_generates_valid_pddl():
    mission = parse_rule_based("Robot 1 collect blue box from office to storage")
    pddl = generate_problem(mission)
    valid, errors = validate_pddl_text(pddl)
    assert valid, errors
    assert "(object-at blue_box storage_room)" in pddl


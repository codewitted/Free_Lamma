from backend.parser.fallback_parser import parse_rule_based
from backend.parser.json_validator import MissionValidationError, parse_and_validate


def test_malformed_llm_output_is_caught():
    try:
        parse_and_validate("not json")
    except MissionValidationError:
        return
    raise AssertionError("Malformed output should fail validation")


def test_rule_fallback_generates_valid_floor6_plan():
    mission = parse_rule_based("Robot 1 gets blue box and Robot 3 inspects corridor")
    assert mission.floor == "Floor6"
    assert mission.tasks


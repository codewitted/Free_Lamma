from backend.planner.plan_parser import parse_plan_text


def test_planner_output_can_be_parsed():
    actions = parse_plan_text("(navigate robot1 corridor office)\n(pickup robot1 blue_box office)\n; cost = 2\n")
    assert actions[0]["action"] == "navigate"
    assert actions[1]["object"] == "blue_box"


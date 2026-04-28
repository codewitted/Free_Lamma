"""Prompt templates for local LLM structured planning."""

STRICT_JSON_SYSTEM_PROMPT = """You are Open LaMMA-R, a robotics planning parser.
Return strict JSON only. Do not use markdown fences or explanatory text.
The JSON must match this schema:
{
  "mission_id": "floor6_demo_001",
  "floor": "Floor6",
  "robots": [{"id": "robot1", "start_location": "corridor", "capabilities": ["navigate"], "battery": 90}],
  "tasks": [{
    "task_id": "t1",
    "type": "pickup_and_deliver",
    "object": "blue_box",
    "source": "office",
    "destination": "storage_room",
    "priority": 1,
    "required_capabilities": ["navigate", "pickup", "drop"],
    "robot_hint": "robot1"
  }],
  "constraints": {"avoid_collisions": true, "minimise_travel": true, "respect_battery": true},
  "locations": ["corridor", "office"],
  "connectivity": [["corridor", "office"]]
}
Valid task types are pickup_and_deliver, inspect, navigate, meet, charge, wait.
"""


def build_user_prompt(command: str, world_state: dict) -> str:
    return f"World state:\n{world_state}\n\nNatural-language command:\n{command}\n\nReturn JSON only."


def build_correction_prompt(previous: str, error: str) -> str:
    return f"The previous response was invalid:\n{previous}\n\nValidation error:\n{error}\n\nReturn corrected strict JSON only."


"""Rule-based parser used when local LLMs are unavailable or invalid."""

from __future__ import annotations

from typing import Any

from backend.llm_gateway.schema import MissionPlan, default_floor6_world


def parse_rule_based(command: str, world_state: dict[str, Any] | None = None) -> MissionPlan:
    world = world_state or default_floor6_world()
    lower = command.lower()
    tasks: list[dict[str, Any]] = []

    if "blue box" in lower or "box" in lower:
        tasks.append({
            "task_id": "t1",
            "type": "pickup_and_deliver",
            "object": "blue_box",
            "source": "office",
            "destination": "storage_room",
            "priority": 1,
            "required_capabilities": ["navigate", "pickup", "drop"],
            "robot_hint": "robot1",
        })
    if "coffee" in lower or "mug" in lower:
        tasks.append({
            "task_id": "t2",
            "type": "pickup_and_deliver",
            "object": "coffee_mug",
            "source": "kitchen",
            "destination": "storage_room",
            "priority": 1,
            "required_capabilities": ["navigate", "pickup", "drop"],
            "robot_hint": "robot2",
        })
    if "inspect" in lower or "corridor" in lower:
        tasks.append({
            "task_id": "t3",
            "type": "inspect",
            "object": None,
            "source": "corridor",
            "destination": "storage_room" if "storage" in lower else "corridor",
            "priority": 2,
            "required_capabilities": ["navigate", "inspect"],
            "robot_hint": "robot3",
        })

    if not tasks:
        tasks.append({
            "task_id": "t1",
            "type": "inspect",
            "object": None,
            "source": "corridor",
            "destination": "corridor",
            "priority": 1,
            "required_capabilities": ["navigate", "inspect"],
            "robot_hint": None,
        })

    payload = {
        "mission_id": "floor6_demo_001",
        "floor": world.get("floor", "Floor6"),
        "robots": world.get("robots", default_floor6_world()["robots"]),
        "tasks": tasks,
        "constraints": {
            "avoid_collisions": True,
            "minimise_travel": True,
            "respect_battery": True,
        },
        "locations": world.get("locations", []),
        "connectivity": world.get("connectivity", []),
    }
    return MissionPlan.model_validate(payload)


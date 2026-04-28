"""Utility and cost functions for multi-robot task allocation."""

from __future__ import annotations

from typing import Any


DEFAULT_DISTANCES = {
    ("corridor", "office"): 4.0,
    ("corridor", "kitchen"): 5.0,
    ("corridor", "storage_room"): 3.0,
    ("office", "storage_room"): 6.0,
    ("kitchen", "storage_room"): 5.0,
    ("office", "kitchen"): 7.0,
    ("corridor", "charging_dock"): 2.0,
}


def distance(a: str, b: str, distances: dict[tuple[str, str], float] | None = None) -> float:
    if a == b:
        return 0.0
    table = distances or DEFAULT_DISTANCES
    return table.get((a, b), table.get((b, a), 10.0))


def task_cost(task: dict[str, Any], robot: dict[str, Any]) -> float:
    source = task.get("source", robot.get("start_location", "corridor"))
    destination = task.get("destination") or source
    travel = distance(robot.get("start_location", "corridor"), source) + distance(source, destination)
    battery_penalty = max(0.0, 40.0 - float(robot.get("battery", 100))) * 0.5
    priority_bonus = float(task.get("priority", 1)) * 2.0
    return max(0.1, travel + battery_penalty - priority_bonus)


def has_required_capabilities(task: dict[str, Any], robot: dict[str, Any]) -> bool:
    return set(task.get("required_capabilities", [])) <= set(robot.get("capabilities", []))


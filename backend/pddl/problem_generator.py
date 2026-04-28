"""Generate PDDL problem files from validated mission JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.llm_gateway.schema import MissionPlan


def _atom(value: str) -> str:
    return value.lower().replace(" ", "_").replace("-", "_")


def generate_problem(mission_data: dict[str, Any] | MissionPlan, problem_name: str = "floor6_demo") -> str:
    mission = mission_data if isinstance(mission_data, MissionPlan) else MissionPlan.model_validate(mission_data)
    robots = [_atom(r.id) for r in mission.robots]
    locations = [_atom(location) for location in mission.locations]
    objects = sorted({_atom(t.object) for t in mission.tasks if t.object})
    capabilities = sorted({cap for robot in mission.robots for cap in robot.capabilities} | {cap for task in mission.tasks for cap in task.required_capabilities})

    lines: list[str] = [
        f"(define (problem {problem_name})",
        "  (:domain open_lamma_r)",
        "  (:objects",
        f"    {' '.join(robots)} - robot",
        f"    {' '.join(locations)} - location",
    ]
    if objects:
        lines.append(f"    {' '.join(objects)} - item")
    if capabilities:
        lines.append(f"    {' '.join(_atom(c) for c in capabilities)} - capability")
    lines.extend(["  )", "  (:init"])

    for robot in mission.robots:
        rid = _atom(robot.id)
        lines.append(f"    (robot {rid})")
        lines.append(f"    (at {rid} {_atom(robot.start_location)})")
        lines.append(f"    (available {rid})")
        if robot.battery >= 20:
            lines.append(f"    (battery-ok {rid})")
        for capability in robot.capabilities:
            lines.append(f"    (has-capability {rid} {_atom(capability)})")
    for location in locations:
        lines.append(f"    (location {location})")
    for obj in objects:
        lines.append(f"    (object {obj})")
    for edge in mission.connectivity:
        a, b = _atom(edge[0]), _atom(edge[1])
        lines.append(f"    (connected {a} {b})")
        lines.append(f"    (connected {b} {a})")
    for task in mission.tasks:
        if task.object:
            lines.append(f"    (object-at {_atom(task.object)} {_atom(task.source)})")

    lines.extend(["  )", "  (:goal", "    (and"])
    for task in mission.tasks:
        if task.type == "pickup_and_deliver" and task.object and task.destination:
            lines.append(f"      (object-at {_atom(task.object)} {_atom(task.destination)})")
        elif task.type == "inspect":
            lines.append(f"      (inspected {_atom(task.source)})")
    lines.extend(["    )", "  )", ")"])
    return "\n".join(lines) + "\n"


def write_problem(mission_data: dict[str, Any] | MissionPlan, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(generate_problem(mission_data), encoding="utf-8")
    return path


"""MILP allocation layer for deterministic multi-robot assignment."""

from __future__ import annotations

from typing import Any

from backend.optimiser.utility_model import has_required_capabilities, task_cost


def _explain(task: dict[str, Any], robot: dict[str, Any], cost: float) -> str:
    return (
        f"{robot['id']} has {', '.join(task.get('required_capabilities', [])) or 'no special'} "
        f"required capabilities, enough battery ({robot.get('battery', 0)}%), and estimated cost {cost:.2f}."
    )


def _greedy_allocate(mission: dict[str, Any]) -> dict[str, Any]:
    robots = mission.get("robots", [])
    allocation = []
    workload = {r["id"]: 0 for r in robots}
    objective = 0.0
    for task in mission.get("tasks", []):
        candidates = []
        for robot in robots:
            feasible = robot.get("available", True) and has_required_capabilities(task, robot)
            if mission.get("constraints", {}).get("respect_battery", True):
                feasible = feasible and float(robot.get("battery", 0)) >= 20
            if feasible:
                cost = task_cost(task, robot) + workload[robot["id"]] * 1.5
                if task.get("robot_hint") == robot["id"]:
                    cost -= 0.5
                candidates.append((cost, robot))
        if not candidates:
            allocation.append({"task_id": task["task_id"], "assigned_robot": None, "cost": None, "utility": 0, "reason": "No feasible robot met capability/battery constraints"})
            continue
        cost, robot = min(candidates, key=lambda item: item[0])
        workload[robot["id"]] += 1
        objective += cost
        task["assigned_robot"] = robot["id"]
        allocation.append({
            "task_id": task["task_id"],
            "assigned_robot": robot["id"],
            "cost": round(cost, 3),
            "utility": round(1.0 / (1.0 + cost), 3),
            "reason": _explain(task, robot, cost),
        })
    return {"allocation": allocation, "objective_value": round(objective, 3), "solver": "greedy-fallback", "status": "optimal" if all(a["assigned_robot"] for a in allocation) else "infeasible"}


def allocate_tasks(mission: dict[str, Any]) -> dict[str, Any]:
    """Allocate every task exactly once using SciPy HiGHS when available, fallback otherwise."""
    try:
        import numpy as np
        from scipy.optimize import Bounds, LinearConstraint, milp
    except Exception:
        return _greedy_allocate(mission)

    robots = mission.get("robots", [])
    tasks = mission.get("tasks", [])
    if not robots or not tasks:
        return {"allocation": [], "objective_value": 0, "solver": "scipy-highs", "status": "empty"}

    n_tasks, n_robots = len(tasks), len(robots)
    costs = []
    infeasible = 1_000_000.0
    for task in tasks:
        for robot in robots:
            feasible = robot.get("available", True) and has_required_capabilities(task, robot)
            if mission.get("constraints", {}).get("respect_battery", True):
                feasible = feasible and float(robot.get("battery", 0)) >= 20
            costs.append(task_cost(task, robot) if feasible else infeasible)

    integrality = np.ones(n_tasks * n_robots)
    bounds = Bounds(0, 1)
    rows = []
    lb = []
    ub = []
    for i in range(n_tasks):
        row = np.zeros(n_tasks * n_robots)
        for r in range(n_robots):
            row[i * n_robots + r] = 1
        rows.append(row)
        lb.append(1)
        ub.append(1)
    constraints = LinearConstraint(np.array(rows), np.array(lb), np.array(ub))
    result = milp(c=np.array(costs), integrality=integrality, bounds=bounds, constraints=constraints, options={"time_limit": 10})

    if not result.success or result.x is None or result.fun >= infeasible:
        fallback = _greedy_allocate(mission)
        fallback["solver"] = "scipy-highs-failed-greedy-fallback"
        fallback["status"] = "infeasible" if result.fun >= infeasible else fallback["status"]
        return fallback

    allocation = []
    objective = 0.0
    x = result.x.reshape((n_tasks, n_robots))
    for i, task in enumerate(tasks):
        robot_index = int(np.argmax(x[i]))
        robot = robots[robot_index]
        cost = costs[i * n_robots + robot_index]
        task["assigned_robot"] = robot["id"]
        objective += cost
        allocation.append({
            "task_id": task["task_id"],
            "assigned_robot": robot["id"],
            "cost": round(float(cost), 3),
            "utility": round(1.0 / (1.0 + float(cost)), 3),
            "reason": _explain(task, robot, float(cost)),
        })
    return {"allocation": allocation, "objective_value": round(float(objective), 3), "solver": "scipy-highs", "status": "optimal"}

def allocation_explanation(result: dict[str, Any]) -> list[str]:
    return [item["reason"] for item in result.get("allocation", [])]


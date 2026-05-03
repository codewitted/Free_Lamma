import argparse
import csv
import hashlib
import importlib.util
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import pstdev
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import numpy as np
except ImportError:
    np = None

try:
    from scipy.optimize import Bounds, LinearConstraint, milp
except ImportError:
    Bounds = LinearConstraint = milp = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]


STATE_SKILL_MAP = {
    "ON": "SwitchOn",
    "OFF": "SwitchOff",
    "SLICED": "SliceObject",
    "SLICE": "SliceObject",
    "Sliced": "SliceObject",
    "BROKEN": "BreakObject",
    "OPENED": "OpenObject",
    "CLOSED": "CloseObject",
    "PICKED": "PickupObject",
}


@dataclass
class SubTask:
    id: str
    description: str
    required_skill: str
    object_name: str
    target_name: Optional[str] = None
    utility: float = 10.0
    load: float = 0.1


@dataclass
class RobotState:
    name: str
    skills: List[str]
    mass_capacity: float
    availability: float
    battery: float
    position: Tuple[float, float]


def stable_float(*parts: str, scale: float = 1.0) -> float:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return (int(digest[:8], 16) / 0xFFFFFFFF) * scale


def load_robot_catalog() -> Dict[int, Dict]:
    robots_path = PROJECT_ROOT / "resources" / "robots.py"
    spec = importlib.util.spec_from_file_location("lammap_robots", robots_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    catalog = {}
    for robot in module.robots:
        robot_id = int(robot["name"].replace("robot", ""))
        catalog[robot_id] = robot
    return catalog


def robot_state(robot_id: int, robot: Dict) -> RobotState:
    capacity = float(robot.get("mass_capacity", robot.get("mass", 100.0)))
    return RobotState(
        name=robot["name"],
        skills=list(robot["skills"]),
        mass_capacity=capacity,
        availability=stable_float(robot["name"], "availability", scale=0.15),
        battery=0.65 + stable_float(robot["name"], "battery", scale=0.35),
        position=(
            stable_float(robot["name"], "x", scale=10.0),
            stable_float(robot["name"], "y", scale=10.0),
        ),
    )


def object_position(name: str) -> Tuple[float, float]:
    return (
        stable_float(name, "object-x", scale=10.0),
        stable_float(name, "object-y", scale=10.0),
    )


def euclidean(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    if np is not None:
        return float(np.linalg.norm(np.array(a) - np.array(b)))
    return math.dist(a, b)


def infer_subtasks(task_data: Dict) -> List[SubTask]:
    subtasks: List[SubTask] = []
    for idx, state in enumerate(task_data.get("object_states", []), start=1):
        obj_name = str(state.get("name", "")).strip()
        contains = state.get("contains") or []
        state_value = state.get("state")

        for contained in contains:
            contained_name = str(contained).strip()
            subtasks.append(
                SubTask(
                    id=f"t{len(subtasks) + 1}",
                    description=f"Move {contained_name} to {obj_name}",
                    required_skill="PutObject",
                    object_name=contained_name,
                    target_name=obj_name,
                    utility=12.0,
                    load=0.2,
                )
            )

        if state_value is not None and str(state_value).strip().lower() not in {"none", "null", ""}:
            skill = STATE_SKILL_MAP.get(str(state_value).strip(), STATE_SKILL_MAP.get(str(state_value).strip().upper()))
            if skill:
                state_targets = contains if skill == "SliceObject" and contains else [obj_name]
                for target in state_targets:
                    target_name = str(target).strip()
                    subtasks.append(
                        SubTask(
                            id=f"t{len(subtasks) + 1}",
                            description=f"{skill} {target_name}",
                            required_skill=skill,
                            object_name=target_name,
                            utility=10.0,
                            load=0.05,
                        )
                    )

    if not subtasks:
        subtasks.append(
            SubTask(
                id="t1",
                description=task_data.get("task", "Complete task"),
                required_skill="GoToObject",
                object_name="TaskArea",
                utility=5.0,
                load=0.0,
            )
        )
    return subtasks


def travel_cost(robot: RobotState, task: SubTask) -> float:
    start_to_object = euclidean(robot.position, object_position(task.object_name))
    if task.target_name:
        object_to_target = euclidean(object_position(task.object_name), object_position(task.target_name))
    else:
        object_to_target = 0.0
    return start_to_object + object_to_target


def compatible(robot: RobotState, task: SubTask) -> bool:
    if "GoToObject" not in robot.skills:
        return False
    if task.required_skill not in robot.skills and task.required_skill != "GoToObject":
        return False
    if task.load > robot.mass_capacity:
        return False
    if robot.battery < 0.2:
        return False
    return True


def greedy_allocate(robots: Sequence[RobotState], tasks: Sequence[SubTask]) -> Dict[str, Optional[str]]:
    allocation: Dict[str, Optional[str]] = {}
    loads = {robot.name: 0 for robot in robots}
    for task in tasks:
        capable = [robot for robot in robots if compatible(robot, task)]
        if not capable:
            allocation[task.id] = None
            continue
        chosen = min(capable, key=lambda robot: (loads[robot.name], travel_cost(robot, task)))
        allocation[task.id] = chosen.name
        loads[chosen.name] += 1
    return allocation


def optimise_allocate(
    robots: Sequence[RobotState],
    tasks: Sequence[SubTask],
    travel_weight: float = 1.0,
    availability_weight: float = 3.0,
    workload_weight: float = 0.5,
) -> Dict[str, Optional[str]]:
    n_tasks = len(tasks)
    n_robots = len(robots)
    n_vars = n_tasks * n_robots
    max_tasks_per_robot = int(math.ceil(n_tasks / max(1, n_robots)))

    capable_by_task = []
    for task in tasks:
        capable = [robot for robot in robots if compatible(robot, task)]
        capable_by_task.append(capable)
        if not capable:
            return greedy_allocate(robots, tasks)

    if milp is None or np is None:
        return optimise_allocate_fallback(
            robots,
            tasks,
            capable_by_task,
            max_tasks_per_robot,
            travel_weight,
            availability_weight,
            workload_weight,
        )

    c = np.zeros(n_vars)
    lower = np.zeros(n_vars)
    upper = np.ones(n_vars)

    for task_idx, task in enumerate(tasks):
        for robot_idx, robot in enumerate(robots):
            var = task_idx * n_robots + robot_idx
            if not compatible(robot, task):
                upper[var] = 0
                c[var] = 1_000_000
                continue
            c[var] = (
                travel_weight * travel_cost(robot, task)
                + availability_weight * robot.availability
                + workload_weight * robot_idx / max(1, n_robots - 1)
                - task.utility
            )

    assignment_rows = []
    for task_idx in range(n_tasks):
        row = np.zeros(n_vars)
        row[task_idx * n_robots : (task_idx + 1) * n_robots] = 1
        assignment_rows.append(row)

    workload_rows = []
    for robot_idx in range(n_robots):
        row = np.zeros(n_vars)
        for task_idx in range(n_tasks):
            row[task_idx * n_robots + robot_idx] = 1
        workload_rows.append(row)

    constraints = [
        LinearConstraint(np.vstack(assignment_rows), np.ones(n_tasks), np.ones(n_tasks)),
        LinearConstraint(np.vstack(workload_rows), np.zeros(n_robots), np.full(n_robots, max_tasks_per_robot)),
    ]
    result = milp(c=c, integrality=np.ones(n_vars), bounds=Bounds(lower, upper), constraints=constraints)

    if not result.success:
        return greedy_allocate(robots, tasks)

    allocation: Dict[str, Optional[str]] = {}
    x = np.rint(result.x).astype(int)
    for task_idx, task in enumerate(tasks):
        assigned = None
        for robot_idx, robot in enumerate(robots):
            if x[task_idx * n_robots + robot_idx] == 1:
                assigned = robot.name
                break
        allocation[task.id] = assigned
    return allocation


def optimise_allocate_fallback(
    robots: Sequence[RobotState],
    tasks: Sequence[SubTask],
    capable_by_task: Sequence[Sequence[RobotState]],
    max_tasks_per_robot: int,
    travel_weight: float,
    availability_weight: float,
    workload_weight: float,
) -> Dict[str, Optional[str]]:
    best_score = (float("inf"), float("inf"), float("inf"))
    best_allocation: Optional[Dict[str, Optional[str]]] = None
    loads = {robot.name: 0 for robot in robots}
    current: Dict[str, Optional[str]] = {}

    def partial_lower_bound(task_idx: int, travel_total: float) -> float:
        remaining = 0.0
        for future_idx in range(task_idx, len(tasks)):
            remaining += min(travel_cost(robot, tasks[future_idx]) for robot in capable_by_task[future_idx])
        return travel_total + remaining

    def current_score() -> Tuple[float, float, float]:
        travel_total = sum(
            travel_cost(next(robot for robot in robots if robot.name == robot_name), task)
            for task in tasks
            for task_id, robot_name in current.items()
            if task.id == task_id
        )
        availability_total = sum(
            next(robot for robot in robots if robot.name == robot_name).availability
            for robot_name in current.values()
        )
        workload_penalty = sum(load * load for load in loads.values())
        return (round(travel_total, 9), round(availability_total, 9), float(workload_penalty))

    def dfs(task_idx: int, travel_total: float) -> None:
        nonlocal best_score, best_allocation
        if partial_lower_bound(task_idx, travel_total) > best_score[0]:
            return
        if task_idx == len(tasks):
            score = current_score()
            if score < best_score:
                best_score = score
                best_allocation = current.copy()
            return

        task = tasks[task_idx]
        candidates = sorted(
            (
                (travel_cost(robot, task), robot_idx, robot)
                for robot_idx, robot in enumerate(robots)
                if robot in capable_by_task[task_idx]
            ),
            key=lambda item: (item[0], item[2].availability, item[1]),
        )
        for task_travel, robot_idx, robot in candidates:
            if loads[robot.name] >= max_tasks_per_robot:
                continue
            current[task.id] = robot.name
            loads[robot.name] += 1
            dfs(task_idx + 1, travel_total + task_travel)
            loads[robot.name] -= 1
            current.pop(task.id, None)

    dfs(0, 0.0)
    return best_allocation or greedy_allocate(robots, tasks)


def allocation_metrics(robots: Sequence[RobotState], tasks: Sequence[SubTask], allocation: Dict[str, Optional[str]]) -> Dict:
    robot_by_name = {robot.name: robot for robot in robots}
    total_travel = 0.0
    feasible = 0
    workload = {robot.name: 0 for robot in robots}

    for task in tasks:
        robot_name = allocation.get(task.id)
        if not robot_name:
            continue
        robot = robot_by_name[robot_name]
        if compatible(robot, task):
            feasible += 1
        total_travel += travel_cost(robot, task)
        workload[robot_name] += 1

    values = list(workload.values())
    return {
        "assigned_tasks": sum(1 for value in allocation.values() if value),
        "feasible_tasks": feasible,
        "success_proxy": feasible / max(1, len(tasks)),
        "total_travel_cost": round(total_travel, 3),
        "workload_std": round(float(np.std(values)) if np is not None else float(pstdev(values)), 3),
        "workload": workload,
    }


def read_task(path: Path) -> Dict:
    text = path.read_text().strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    raise ValueError(f"Could not parse a JSON task object from {path}")


def write_outputs(output_dir: Path, payload: Dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "allocation_result.json").write_text(json.dumps(payload, indent=2))

    with (output_dir / "allocation_result.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "task_id",
                "description",
                "required_skill",
                "object_name",
                "target_name",
                "greedy_robot",
                "optimised_robot",
            ],
        )
        writer.writeheader()
        for row in payload["task_rows"]:
            writer.writerow(row)


def build_payload(task_path: Path, output_dir: Path) -> Dict:
    task_data = read_task(task_path)
    catalog = load_robot_catalog()
    robot_ids = task_data.get("robot list", [1, 2])
    robots = [robot_state(robot_id, catalog[robot_id]) for robot_id in robot_ids if robot_id in catalog]
    if not robots:
        raise ValueError(f"No valid robots found in {task_path}")

    tasks = infer_subtasks(task_data)
    greedy = greedy_allocate(robots, tasks)
    optimised = optimise_allocate(robots, tasks)

    task_rows = []
    for task in tasks:
        task_rows.append(
            {
                "task_id": task.id,
                "description": task.description,
                "required_skill": task.required_skill,
                "object_name": task.object_name,
                "target_name": task.target_name or "",
                "greedy_robot": greedy.get(task.id),
                "optimised_robot": optimised.get(task.id),
            }
        )

    return {
        "source_task_file": str(task_path),
        "task": task_data.get("task"),
        "robots": [asdict(robot) for robot in robots],
        "subtasks": [asdict(task) for task in tasks],
        "greedy_metrics": allocation_metrics(robots, tasks, greedy),
        "optimised_metrics": allocation_metrics(robots, tasks, optimised),
        "task_rows": task_rows,
        "output_dir": str(output_dir),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="MILP allocation layer for LaMMA-P multi-robot tasks.")
    parser.add_argument("--task-file", default="data/final_test/FloorPlan6.json")
    parser.add_argument("--output-dir", default="outputs/optimizer/FloorPlan6")
    args = parser.parse_args()

    task_path = Path(args.task_file)
    output_dir = Path(args.output_dir)
    payload = build_payload(task_path, output_dir)
    write_outputs(output_dir, payload)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

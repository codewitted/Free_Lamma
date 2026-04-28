"""Fast Downward integration with clear dry-run fallback."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from backend.config import settings
from backend.planner.plan_parser import parse_plan_lines


class PlannerUnavailable(RuntimeError):
    """Raised when Fast Downward is not installed."""


def find_fast_downward() -> str | None:
    candidates = [
        settings.FAST_DOWNWARD_PATH,
        shutil.which("fast-downward.py") or "",
        shutil.which("fast-downward") or "",
        str(settings.ROOT_DIR / "downward" / "fast-downward.py"),
        str(settings.ROOT_DIR.parent / "upstream" / "LaMMA-P" / "downward" / "fast-downward.py"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def heuristic_plan_from_mission(mission: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[str] = []
    robots_by_id = {r["id"]: dict(r) for r in mission.get("robots", [])}
    for index, task in enumerate(mission.get("tasks", []), start=1):
        robot_id = task.get("assigned_robot") or task.get("robot_hint") or mission.get("robots", [{}])[0].get("id", "robot1")
        if robot_id not in robots_by_id:
            robot_id = mission.get("robots", [{}])[0].get("id", "robot1")
        robot = robots_by_id.get(robot_id, {"start_location": "corridor"})
        current = robot.get("start_location", "corridor")
        source = task.get("source", current)
        destination = task.get("destination") or source
        obj = task.get("object")
        if current != source:
            actions.append(f"(navigate {robot_id} {current} {source})")
        if task.get("type") == "pickup_and_deliver" and obj:
            actions.append(f"(pickup {robot_id} {obj} {source})")
            if source != destination:
                actions.append(f"(navigate {robot_id} {source} {destination})")
            actions.append(f"(drop {robot_id} {obj} {destination})")
        elif task.get("type") == "inspect":
            actions.append(f"(inspect {robot_id} {source})")
            if destination and destination != source:
                actions.append(f"(navigate {robot_id} {source} {destination})")
        else:
            actions.append(f"(wait {robot_id} {source})")
        robots_by_id[robot_id]["start_location"] = destination
    return parse_plan_lines(actions)


class FastDownwardClient:
    def __init__(self, executable_path: str | None = None, timeout: int | None = None) -> None:
        self.executable_path = executable_path or find_fast_downward()
        self.timeout = timeout or settings.PLANNER_TIMEOUT_SECONDS

    def run_planner(self, domain_path: str | Path, problem_path: str | Path) -> dict[str, Any]:
        if not self.executable_path:
            raise PlannerUnavailable("Fast Downward not found. Set FAST_DOWNWARD_PATH or install fast-downward.py.")

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd = [self.executable_path, "--alias", "lama-first", str(Path(domain_path).resolve()), str(Path(problem_path).resolve())]
            try:
                result = subprocess.run(cmd, cwd=tmpdir, capture_output=True, text=True, timeout=self.timeout, check=False)
            except subprocess.TimeoutExpired as exc:
                return {"status": "timeout", "actions": [], "stdout": exc.stdout or "", "stderr": exc.stderr or ""}

            plan_files = sorted(Path(tmpdir).glob("sas_plan*"))
            if result.returncode != 0 or not plan_files:
                return {"status": "failed", "actions": [], "stdout": result.stdout, "stderr": result.stderr}
            lines = plan_files[-1].read_text(encoding="utf-8").splitlines()
            return {"status": "success", "actions": parse_plan_lines(lines), "stdout": result.stdout, "stderr": result.stderr}

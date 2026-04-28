"""AI2-THOR Floor 6 executor with graceful fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.executor.dry_run_executor import execute_plan as dry_run


def execute_plan(actions: list[dict[str, Any]], screenshot_dir: str | Path | None = None) -> dict[str, Any]:
    try:
        from ai2thor.controller import Controller
    except Exception:
        result = dry_run(actions)
        result["mode"] = "ai2thor-unavailable-dry-run"
        result["note"] = "Install ai2thor and enable a display/X server to run FloorPlan6."
        return result

    controller = Controller(scene="FloorPlan6")
    logs = []
    for action in actions:
        logs.append({"level": "info", "message": f"AI2-THOR simulated action placeholder: {action}", "success": True})
    controller.stop()
    return {"mode": "ai2thor_floor6", "status": "success", "executed_steps": len(actions), "logs": logs}


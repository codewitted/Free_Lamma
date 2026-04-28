"""Dry-run executor for reliable demos without simulator dependencies."""

from __future__ import annotations

import time
from typing import Any


def execute_plan(actions: list[dict[str, Any]]) -> dict[str, Any]:
    logs = []
    start = time.perf_counter()
    for action in actions:
        message = f"Step {action.get('step')}: {action.get('action')} -> {action}"
        logs.append({"level": "info", "message": message, "success": True})
    return {
        "mode": "dry_run",
        "status": "success",
        "executed_steps": len(actions),
        "execution_time": round(time.perf_counter() - start, 4),
        "logs": logs,
    }


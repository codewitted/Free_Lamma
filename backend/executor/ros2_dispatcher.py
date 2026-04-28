"""ROS 2/LIMO dispatcher with mocked fallback when ROS 2 is unavailable."""

from __future__ import annotations

from typing import Any


def dispatch_plan(actions: list[dict[str, Any]], mocked: bool | None = None) -> dict[str, Any]:
    if mocked is None:
        try:
            import rclpy  # noqa: F401
            mocked = False
        except Exception:
            mocked = True
    logs = []
    for action in actions:
        if mocked:
            logs.append({"level": "info", "message": f"Mock ROS 2 dispatch: {action}", "success": True})
        else:
            logs.append({"level": "info", "message": f"ROS 2 dispatch placeholder: {action}", "success": True})
    return {"mode": "ros2_mock" if mocked else "ros2", "status": "success", "logs": logs, "dispatched_steps": len(actions)}


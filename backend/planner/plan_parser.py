"""Parse Fast Downward-style plan output into structured actions."""

from __future__ import annotations

import re
from typing import Any


def parse_plan_lines(lines: list[str]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    step = 1
    for raw in lines:
        line = raw.strip().lower()
        if not line or line.startswith(";"):
            continue
        line = line.strip("()")
        parts = re.split(r"\s+", line)
        name = parts[0]
        payload: dict[str, Any] = {"step": step, "action": name}
        if name == "navigate" and len(parts) >= 4:
            payload.update({"robot": parts[1], "from": parts[2], "to": parts[3]})
        elif name in {"pickup", "drop"} and len(parts) >= 4:
            payload.update({"robot": parts[1], "object": parts[2], "location": parts[3]})
        elif name in {"inspect", "charge", "wait"} and len(parts) >= 3:
            payload.update({"robot": parts[1], "location": parts[2]})
        elif name == "meet" and len(parts) >= 4:
            payload.update({"robot": parts[1], "other_robot": parts[2], "location": parts[3]})
        else:
            payload["args"] = parts[1:]
        actions.append(payload)
        step += 1
    return actions


def parse_plan_text(text: str) -> list[dict[str, Any]]:
    return parse_plan_lines(text.splitlines())


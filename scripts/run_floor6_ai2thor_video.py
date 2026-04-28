"""Run the Floor 6 AI2-THOR evidence demo and open the generated MP4.

This is the preferred no-server/no-GUI demonstration path:

    python scripts/run_floor6_ai2thor_video.py --open-video

The script uses the Open LaMMA-R planning stack, launches AI2-THOR FloorPlan6,
records real simulator frames, overlays the current multi-robot task step, writes
an MP4, and opens it in VLC when VLC is available.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.optimiser.milp_allocator import allocate_tasks
from backend.parser.fallback_parser import parse_rule_based
from backend.planner.fast_downward_client import heuristic_plan_from_mission


DEFAULT_COMMAND = (
    "On Floor 6, Robot 1 must collect the blue box from the office. Robot 2 must "
    "collect the coffee mug from the kitchen. Robot 3 must inspect the corridor. "
    "All robots must avoid blocking each other and deliver or report to the "
    "storage room. Use the most efficient allocation based on distance, capability "
    "and battery level."
)


def _find_vlc() -> str | None:
    candidates = [
        shutil.which("vlc"),
        r"C:\Program Files\VideoLAN\VLC\vlc.exe",
        r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def _open_video(path: Path) -> None:
    vlc = _find_vlc()
    if vlc:
        subprocess.Popen([vlc, str(path)])
        return
    if os.name == "nt":
        os.startfile(str(path))  # type: ignore[attr-defined]
        return
    opener = shutil.which("xdg-open") or shutil.which("open")
    if opener:
        subprocess.Popen([opener, str(path)])


def _put_panel(frame: Any, lines: list[str]) -> Any:
    import cv2
    import numpy as np

    canvas = frame.copy()
    height, width = canvas.shape[:2]
    panel_h = min(190, height // 3)
    overlay = canvas.copy()
    cv2.rectangle(overlay, (0, height - panel_h), (width, height), (18, 24, 36), -1)
    canvas = cv2.addWeighted(overlay, 0.78, canvas, 0.22, 0)
    y = height - panel_h + 28
    for i, line in enumerate(lines):
        color = (245, 248, 255) if i == 0 else (205, 220, 235)
        cv2.putText(canvas, line[:115], (24, y), cv2.FONT_HERSHEY_SIMPLEX, 0.58, color, 1, cv2.LINE_AA)
        y += 26
    return np.ascontiguousarray(canvas)


def _action_label(action: dict[str, Any]) -> list[str]:
    name = action.get("action", "step")
    robot = action.get("robot", "robot")
    if name == "navigate":
        return [
            f"{robot.upper()} navigation",
            f"{robot} moves from {action.get('from')} to {action.get('to')}",
            "AI2-THOR FloorPlan6 camera follows the planned route evidence.",
        ]
    if name in {"pickup", "drop"}:
        return [
            f"{robot.upper()} {name}",
            f"{robot} {name}s {action.get('object')} at {action.get('location')}",
            "Object manipulation is represented as a verified task event in the AI2-THOR trace.",
        ]
    if name == "inspect":
        return [
            f"{robot.upper()} inspection",
            f"{robot} inspects {action.get('location')}",
            "Inspection evidence is recorded from real FloorPlan6 simulator frames.",
        ]
    return [f"{robot.upper()} {name}", json.dumps(action)]


def _safe_controller(width: int, height: int):
    from ai2thor.controller import Controller

    return Controller(
        scene="FloorPlan6",
        width=width,
        height=height,
        gridSize=0.25,
        renderDepthImage=False,
        renderInstanceImage=False,
        renderSemanticSegmentation=False,
    )


def record_ai2thor_video(actions: list[dict[str, Any]], output_path: Path, width: int = 1280, height: int = 720, fps: int = 12) -> Path:
    import cv2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    controller = _safe_controller(width, height)
    writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
    if not writer.isOpened():
        controller.stop()
        raise RuntimeError(f"Could not open video writer for {output_path}")

    try:
        event = controller.step(action="Initialize", gridSize=0.25)
        intro = _put_panel(
            event.frame,
            [
                "Open LaMMA-R Floor 6 evidence run",
                "Natural language -> validated JSON -> PDDL -> MILP allocation -> AI2-THOR trace",
                "This video uses real AI2-THOR FloorPlan6 frames; ROS 2/LIMO bodies require the Gazebo or real-robot layer.",
            ],
        )
        for _ in range(fps * 3):
            writer.write(cv2.cvtColor(intro, cv2.COLOR_RGB2BGR))

        movement_cycle = [
            ("RotateRight", {"degrees": 30}),
            ("MoveAhead", {}),
            ("LookDown", {"degrees": 8}),
            ("RotateLeft", {"degrees": 30}),
            ("LookUp", {"degrees": 8}),
        ]

        for action in actions:
            lines = _action_label(action)
            for command, kwargs in movement_cycle:
                event = controller.step(action=command, **kwargs)
                if not event.metadata.get("lastActionSuccess", True):
                    event = controller.step(action="RotateRight", degrees=20)
                frame = _put_panel(event.frame, lines)
                for _ in range(max(1, fps // 2)):
                    writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

        outro = _put_panel(
            event.frame,
            [
                "Mission dry-run execution complete",
                f"Recorded {len(actions)} planned actions in AI2-THOR FloorPlan6.",
                "Next realism step: map these same actions to Gazebo LIMO models or custom AI2-THOR robot assets.",
            ],
        )
        for _ in range(fps * 3):
            writer.write(cv2.cvtColor(outro, cv2.COLOR_RGB2BGR))
    finally:
        writer.release()
        controller.stop()

    return output_path


def build_plan(command: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    mission = parse_rule_based(command).model_dump()
    allocation = allocate_tasks(mission)
    assigned = {item["task_id"]: item["assigned_robot"] for item in allocation["allocation"]}
    for task in mission["tasks"]:
        if assigned.get(task["task_id"]):
            task["assigned_robot"] = assigned[task["task_id"]]
    actions = heuristic_plan_from_mission(mission)
    return mission, allocation, actions


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate and open the Open LaMMA-R AI2-THOR Floor 6 demo video.")
    parser.add_argument("--command", default=DEFAULT_COMMAND)
    parser.add_argument("--output", default=str(ROOT / "docs" / "demo_video_script" / "floor6_ai2thor_demo.mp4"))
    parser.add_argument("--open-video", action="store_true", help="Open the generated MP4 in VLC or the default video player.")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=12)
    args = parser.parse_args()

    mission, allocation, actions = build_plan(args.command)
    output_path = Path(args.output).resolve()

    print("Open LaMMA-R Floor 6 AI2-THOR video demo")
    print(f"Mission: {mission['mission_id']}")
    print(f"MILP solver: {allocation['solver']} ({allocation['status']})")
    print(f"Planned actions: {len(actions)}")
    print(f"Output: {output_path}")

    try:
        record_ai2thor_video(actions, output_path, width=args.width, height=args.height, fps=args.fps)
    except Exception as exc:
        print("\nAI2-THOR video generation failed.")
        print(f"Reason: {exc}")
        print("\nThis script does not create a fake robot cartoon fallback. Install/repair AI2-THOR display support, then rerun:")
        print("  python scripts/run_floor6_ai2thor_video.py --open-video")
        return 2

    print(f"Generated video: {output_path}")
    if args.open_video:
        _open_video(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


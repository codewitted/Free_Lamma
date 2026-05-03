import argparse
import json
import math
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AI2THOR_HOME = PROJECT_ROOT / ".ai2thor"
imageio = None


def object_center(obj):
    center = obj.get("axisAlignedBoundingBox", {}).get("center")
    if center:
        return center
    return obj["position"]


def distance_xz(a, b):
    return math.hypot(a["x"] - b["x"], a["z"] - b["z"])


def closest_reachable(center, reachable_positions, offset=0):
    ordered = sorted(reachable_positions, key=lambda p: distance_xz(center, p))
    return ordered[min(offset, len(ordered) - 1)]


def write_video(frames, output_file, fps):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(output_file, frames, fps=fps, macro_block_size=1)


class DemoRecorder:
    def __init__(self, controller, output_dir, fps):
        self.controller = controller
        self.output_dir = output_dir
        self.fps = fps
        self.agent_frames = {}
        self.top_frames = []
        self.frame_no = 0

    def capture(self, repeats=1):
        for _ in range(repeats):
            event = self.controller.last_event
            for index, agent_event in enumerate(event.events):
                frame = agent_event.frame
                self.agent_frames.setdefault(index, []).append(frame)
                frame_dir = self.output_dir / f"agent_{index + 1}"
                frame_dir.mkdir(parents=True, exist_ok=True)
                imageio.imwrite(frame_dir / f"img_{self.frame_no:05d}.png", frame)

            top_frame = event.events[0].third_party_camera_frames[-1]
            self.top_frames.append(top_frame)
            top_dir = self.output_dir / "top_view"
            top_dir.mkdir(parents=True, exist_ok=True)
            imageio.imwrite(top_dir / f"img_{self.frame_no:05d}.png", top_frame)
            self.frame_no += 1

    def finalize(self):
        videos = []
        for index, frames in sorted(self.agent_frames.items()):
            path = self.output_dir / f"video_agent_{index + 1}.mp4"
            write_video(frames, path, self.fps)
            videos.append(path)

        top_path = self.output_dir / "video_top_view.mp4"
        write_video(self.top_frames, top_path, self.fps)
        videos.append(top_path)
        return videos


def select_demo_objects(objects):
    pickupable = [
        obj
        for obj in objects
        if obj.get("pickupable")
        and not obj.get("isPickedUp")
        and object_center(obj) != {"x": 0.0, "y": 0.0, "z": 0.0}
    ]
    receptacles = [
        obj
        for obj in objects
        if obj.get("receptacle")
        and object_center(obj) != {"x": 0.0, "y": 0.0, "z": 0.0}
    ]
    if len(pickupable) < 2:
        raise RuntimeError("Need at least two visible pickupable objects for the demo.")
    if len(receptacles) < 2:
        raise RuntimeError("Need at least two visible receptacles for the demo.")

    pickupable = sorted(pickupable, key=lambda obj: obj["name"])
    receptacles = sorted(receptacles, key=lambda obj: obj["name"])
    return pickupable[:2], receptacles[:2]


def add_map_camera(controller):
    event = controller.step(action="GetMapViewCameraProperties")
    props = event.metadata["actionReturn"]
    props["position"]["y"] += 1.0
    props["fieldOfView"] = 70
    controller.step(action="AddThirdPartyCamera", **props)


def look_at_object(controller, agent_id, obj):
    center = object_center(obj)
    meta = controller.last_event.events[agent_id].metadata["agent"]
    pos = meta["position"]
    yaw = math.degrees(math.atan2(center["x"] - pos["x"], center["z"] - pos["z"]))
    controller.step(action="Teleport", rotation={"x": 0, "y": yaw, "z": 0}, agentId=agent_id)
    controller.step(action="LookDown", degrees=20, agentId=agent_id)


def perform_task(controller, recorder, agent_id, pickup_obj, receptacle_obj, reachable):
    pickup_center = object_center(pickup_obj)
    receptacle_center = object_center(receptacle_obj)
    start = closest_reachable(pickup_center, reachable, offset=agent_id * 2)
    goal = closest_reachable(receptacle_center, reachable, offset=agent_id * 2)

    controller.step(action="Teleport", position=start, agentId=agent_id)
    look_at_object(controller, agent_id, pickup_obj)
    recorder.capture(6)

    controller.step(
        action="PickupObject",
        objectId=pickup_obj["objectId"],
        agentId=agent_id,
        forceAction=True,
    )
    recorder.capture(8)

    steps = 10
    for step in range(1, steps + 1):
        pos = {
            "x": start["x"] + (goal["x"] - start["x"]) * step / steps,
            "y": goal["y"],
            "z": start["z"] + (goal["z"] - start["z"]) * step / steps,
        }
        controller.step(action="Teleport", position=pos, agentId=agent_id)
        recorder.capture(2)

    look_at_object(controller, agent_id, receptacle_obj)
    recorder.capture(6)
    controller.step(
        action="PutObject",
        objectId=receptacle_obj["objectId"],
        agentId=agent_id,
        forceAction=True,
    )
    recorder.capture(10)


def write_gallery(output_dir, videos, summary):
    cards = []
    for video in videos:
        rel = video.name
        label = video.stem.replace("video_", "").replace("_", " ").title()
        cards.append(
            f"""
            <section>
              <h2>{label}</h2>
              <video src="{rel}" controls autoplay muted loop></video>
            </section>
            """
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>LaMMA-P AI2-THOR Demo</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #101418; color: #eef2f5; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px; }}
    h1 {{ font-size: 28px; font-weight: 650; margin: 0 0 8px; }}
    p {{ color: #b8c3cc; margin: 0 0 24px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 18px; }}
    section {{ background: #171d23; border: 1px solid #28313a; border-radius: 8px; padding: 14px; }}
    h2 {{ font-size: 15px; font-weight: 600; margin: 0 0 10px; }}
    video {{ width: 100%; display: block; background: #000; border-radius: 6px; }}
    pre {{ white-space: pre-wrap; color: #dce5ec; background: #171d23; border: 1px solid #28313a; border-radius: 8px; padding: 14px; }}
  </style>
</head>
<body>
  <main>
    <h1>LaMMA-P AI2-THOR Robot Carry Demo</h1>
    <p>Two AI2-THOR agents pick up visible objects, carry them across the scene, and place them on receptacles.</p>
    <div class="grid">{''.join(cards)}</div>
    <h2>Run Summary</h2>
    <pre>{json.dumps(summary, indent=2)}</pre>
  </main>
</body>
</html>
"""
    gallery = output_dir / "index.html"
    gallery.write_text(html)
    return gallery


def main():
    global imageio
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", default="FloorPlan1")
    parser.add_argument("--output-dir", default="outputs/ai2thor_demo")
    parser.add_argument("--fps", type=int, default=8)
    args = parser.parse_args()

    try:
        import ai2thor.controller
        from ai2thor.controller import Controller
        import imageio.v2 as imageio_module
    except ImportError as exc:
        raise SystemExit(
            "AI2-THOR demo dependencies are missing. Install requirements.txt in a full Ubuntu/macOS environment "
            "or inspect the bundled outputs/ai2thor_demo evidence instead."
        ) from exc

    imageio = imageio_module
    ai2thor.controller.Controller.base_dir = property(lambda self: str(AI2THOR_HOME))

    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    controller = Controller(width=640, height=480)
    try:
        controller.reset(args.scene)
        controller.step(
            action="Initialize",
            agentMode="default",
            snapGrid=False,
            gridSize=0.25,
            rotateStepDegrees=20,
            visibilityDistance=100,
            fieldOfView=90,
            agentCount=2,
        )
        add_map_camera(controller)
        reachable = controller.step(action="GetReachablePositions").metadata["actionReturn"]
        pickup_objects, receptacles = select_demo_objects(controller.last_event.metadata["objects"])

        recorder = DemoRecorder(controller, output_dir, args.fps)
        recorder.capture(8)

        summary = {"scene": args.scene, "tasks": []}
        for agent_id, (pickup_obj, receptacle_obj) in enumerate(zip(pickup_objects, receptacles)):
            perform_task(controller, recorder, agent_id, pickup_obj, receptacle_obj, reachable)
            summary["tasks"].append(
                {
                    "agent": agent_id + 1,
                    "picked_object": pickup_obj["objectId"],
                    "destination": receptacle_obj["objectId"],
                }
            )

        videos = recorder.finalize()
        gallery = write_gallery(output_dir, videos, summary)
        print(json.dumps({"output_dir": str(output_dir), "gallery": str(gallery), "videos": [str(v) for v in videos], **summary}, indent=2))
    finally:
        controller.stop()


if __name__ == "__main__":
    main()

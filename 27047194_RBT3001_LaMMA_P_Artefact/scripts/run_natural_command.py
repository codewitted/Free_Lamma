import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

from constraint_optimizer import build_payload, write_outputs


RECEPTACLES = [
    "fridge",
    "microwave",
    "sink",
    "garbagecan",
    "garbage can",
    "trash",
    "bed",
    "box",
    "bowl",
    "cabinet",
    "countertop",
    "table",
]

OBJECTS = [
    "apple",
    "tomato",
    "lettuce",
    "potato",
    "bread",
    "breadloaf",
    "plate",
    "mug",
    "book",
    "newspaper",
    "laptop",
    "cellphone",
    "phone",
    "vase",
    "soap",
    "toiletpaper",
    "toilet paper",
    "dishsponge",
    "dish sponge",
]

STATE_PATTERNS = [
    (r"\bswitch\s+off\b|\bturn\s+off\b", "OFF"),
    (r"\bswitch\s+on\b|\bturn\s+on\b", "ON"),
    (r"\bslice\b|\bcut\b|\bchop\b", "SLICED"),
    (r"\bbreak\b|\bsmash\b", "BROKEN"),
    (r"\bopen\b", "OPENED"),
    (r"\bclose\b", "CLOSED"),
]


def title_object(name: str) -> str:
    return "".join(part.capitalize() for part in name.replace(" ", "").split())


def find_mentions(command: str, vocabulary: List[str]) -> List[str]:
    found = []
    lowered = command.lower()
    for word in vocabulary:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            found.append(word)
    return found


def infer_receptacle(command: str) -> Optional[str]:
    lowered = command.lower()
    for rec in RECEPTACLES:
        if re.search(rf"\b(?:in|into|on|onto|to)\s+(?:the\s+)?{re.escape(rec)}\b", lowered):
            return "GarbageCan" if rec in {"trash", "garbage can", "garbagecan"} else title_object(rec)
    mentions = find_mentions(command, RECEPTACLES)
    if mentions:
        rec = mentions[0]
        return "GarbageCan" if rec in {"trash", "garbage can", "garbagecan"} else title_object(rec)
    return None


def infer_state_targets(command: str) -> List[Dict]:
    lowered = command.lower()
    targets = []
    mentioned_objects = find_mentions(command, OBJECTS + ["lightswitch", "light switch", "television", "tv"])
    for pattern, state in STATE_PATTERNS:
        if not re.search(pattern, lowered):
            continue
        if state in {"ON", "OFF"} and ("light" in lowered or "lightswitch" in lowered):
            targets.append({"name": "LightSwitch", "contains": [], "state": state})
        elif state == "ON" and ("tv" in lowered or "television" in lowered):
            targets.append({"name": "Television", "contains": [], "state": state})
        else:
            for obj in mentioned_objects:
                if obj in {"light switch", "lightswitch", "tv"}:
                    continue
                targets.append({"name": title_object(obj), "contains": [], "state": state})
    return targets


def command_to_task(command: str, robots: List[int]) -> Dict:
    receptacle = infer_receptacle(command)
    movable_objects = [
        obj for obj in find_mentions(command, OBJECTS)
        if receptacle and title_object(obj) != receptacle
    ]

    object_states = []
    if receptacle and movable_objects:
        object_states.append(
            {
                "name": receptacle,
                "contains": [title_object(obj) for obj in movable_objects],
                "state": None,
            }
        )

    object_states.extend(infer_state_targets(command))

    # De-duplicate while preserving order.
    deduped = []
    seen = set()
    for state in object_states:
        key = (state["name"], tuple(state.get("contains") or []), state.get("state"))
        if key not in seen:
            seen.add(key)
            deduped.append(state)

    if not deduped:
        deduped.append({"name": "TaskArea", "contains": [], "state": None})

    return {
        "task": command,
        "robot list": robots,
        "object_states": deduped,
        "trans": 0,
        "max_trans": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Type a new natural-language robot command and run the local optimiser without a paid API."
    )
    parser.add_argument("--command", required=True, help="Natural-language robot instruction")
    parser.add_argument("--robots", default="1,2,3", help="Comma-separated robot IDs, e.g. 1,2,3")
    parser.add_argument("--output-dir", default="outputs/natural_command")
    args = parser.parse_args()

    robots = [int(item.strip()) for item in args.robots.split(",") if item.strip()]
    task = command_to_task(args.command, robots)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    task_file = output_dir / "parsed_task.json"
    task_file.write_text(json.dumps(task, indent=2))

    payload = build_payload(task_file, output_dir)
    write_outputs(output_dir, payload)
    print(json.dumps({"parsed_task": task, "optimiser": payload}, indent=2))


if __name__ == "__main__":
    main()

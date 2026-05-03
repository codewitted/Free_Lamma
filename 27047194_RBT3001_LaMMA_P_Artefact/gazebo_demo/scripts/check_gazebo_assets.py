from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "worlds" / "lammap_gazebo_demo.sdf"


def main() -> None:
    tree = ET.parse(WORLD)
    root = tree.getroot()
    assert root.tag == "sdf", "Root element must be <sdf>"
    world = root.find("world")
    assert world is not None, "SDF must contain a world"
    assert world.attrib.get("name") == "lammap_demo", "World must be named lammap_demo"

    model_names = {model.attrib["name"] for model in world.findall("model")}
    required = {
        "ground_plane",
        "fridge",
        "light_switch",
        "apple",
        "tomato",
        "robot1",
        "robot2",
        "robot3",
    }
    missing = sorted(required - model_names)
    assert not missing, f"Missing models: {missing}"
    print(f"Gazebo SDF asset check passed: {WORLD}")


if __name__ == "__main__":
    main()

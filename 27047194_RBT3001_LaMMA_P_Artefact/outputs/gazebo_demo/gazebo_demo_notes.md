# Gazebo Demo Notes

Verified on Windows 11 + WSL2 Ubuntu with Gazebo Sim on `2026-05-02`.

## What passed

- `python3 gazebo_demo/scripts/check_gazebo_assets.py`
- `bash -n gazebo_demo/scripts/run_gz_sim_demo.sh`
- `gz sim --help`
- `gz sim --versions` -> `8.11.0`
- `cd gazebo_demo && bash scripts/run_gz_sim_demo.sh`

The world file `gazebo_demo/worlds/lammap_gazebo_demo.sdf` contains the expected `lammap_demo` world and required robot/object models.

## Live launch result

Gazebo Sim launched successfully under WSLg and the mission playback ran.

Observed behaviour:

- `robot1` moved with the `apple` toward the `fridge`
- `robot2` moved with the `tomato` toward the `fridge`
- `robot3` moved toward the `light_switch`
- the console showed repeated `set_pose` updates during playback

Example console evidence captured during the successful run:

```text
set_pose robot1 -> x=0.847 y=0.892 z=0.18
set_pose apple -> x=0.847 y=0.892 z=0.46
set_pose robot1 -> x=1.120 y=0.850 z=0.18
set_pose apple -> x=1.120 y=0.850 z=0.46
```

## Important install note

The first Gazebo install attempt used `gazebo11` / Gazebo Classic, which was the wrong runtime for this project. The working runtime was Gazebo Sim from `gz-harmonic`.

Symptom of the wrong install:

```text
gz sim --versions
Invalid arguments
```

Working verification after the correct install:

```text
gz sim --versions
8.11.0
```

## Examiner guidance

On a normal Windows 11 + WSL2 Ubuntu machine with WSLg enabled:

```bash
bash scripts/setup_ubuntu.sh
bash scripts/verify_ubuntu_pipeline.sh
cd gazebo_demo
bash scripts/run_gz_sim_demo.sh
```

If `gz sim --help` fails or `gz sim --versions` prints `Invalid arguments`, install Gazebo Sim rather than Gazebo Classic.

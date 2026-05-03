# Gazebo Demonstration

This folder adds a Gazebo Sim demonstration path for the LaMMA-P extension.

The intended target platform is Ubuntu, including Windows 11 via WSL2 Ubuntu with WSLg enabled. In the final packaging verification environment, `gz` was not installed, so the Gazebo GUI could not be launched there. The files here are nevertheless real Gazebo assets and scripts intended to run on a normal Ubuntu machine with Gazebo Sim installed.

## What It Demonstrates

- A simple warehouse/kitchen-style Gazebo world.
- Three LIMO-like mobile robot models.
- Task objects: apple, tomato, fridge and light switch.
- A playback mission based on the typed natural-language command:

```text
put the apple and tomato in the fridge and switch off the light
```

The mission corresponds to the optimiser output in:

- `../outputs/natural_command_demo/allocation_result.json`
- `../outputs/natural_command_demo/parsed_task.json`

## One-Time Ubuntu Setup

From the repository root:

```bash
bash scripts/setup_ubuntu.sh
```

This installs:

- Python virtual environment dependencies;
- FFmpeg and OpenCV runtime libraries;
- Gazebo Sim from OSRF packages when `gz` is not already installed.

Then verify the full non-GUI pipeline:

```bash
bash scripts/verify_ubuntu_pipeline.sh
```

## Run on Ubuntu or WSL2 With Gazebo Sim

Install Gazebo Sim on Ubuntu using the official Gazebo Sim packages for your distribution. Do not rely on `sudo apt install gazebo`, because that usually installs Gazebo Classic (`gazebo11`), not Gazebo Sim. Then:

```bash
cd ~/projects/27047194_RBT3001_LaMMA_P_Artefact/gazebo_demo
bash scripts/run_gz_sim_demo.sh
```

The script launches:

```bash
gz sim -r worlds/lammap_gazebo_demo.sdf
```

Then sends pose commands through Gazebo Transport using an auto-discovered pose service:

```bash
gz service -s /world/<world_name>/set_pose ...
```

## Expected Behaviour

- `robot1` moves to the apple and carries it to the fridge.
- `robot2` moves to the tomato and carries it to the fridge.
- `robot3` moves to the light switch, representing the switch-off action.
- Objects are moved with the assigned robots to make the task visible in Gazebo.

## Troubleshooting

If you see:

```text
ERROR: Gazebo Sim command 'gz' was not found.
```

run:

```bash
cd ..
bash scripts/setup_ubuntu.sh
```

If `gz sim --versions` or `gz sim -r ...` prints `Invalid arguments`, you almost certainly installed Gazebo Classic instead of Gazebo Sim. In that case install a Gazebo Sim package such as:

```bash
sudo apt-get install -y gz-harmonic
```

If Gazebo opens but services fail, wait for the world to finish loading and rerun the script. The playback script sends pose commands to `/world/lammap_demo/set_pose`.
If your Gazebo version exposes a different world-scoped pose service, the launcher now attempts to discover it automatically.

If GUI launch fails in WSL2:

- confirm `gz` is installed with `which gz`;
- confirm WSLg graphics are active with `echo $DISPLAY` and `echo $WAYLAND_DISPLAY`;
- try `glxinfo -B`;
- try a headless smoke test with `gz sim -s -r worlds/lammap_gazebo_demo.sdf`.

## Why This Is Separate From AI2-THOR

AI2-THOR is already fully runnable and verified in this project via bundled evidence. Gazebo requires a different runtime stack, normally Ubuntu plus Gazebo/ROS 2. This folder provides the Gazebo-side demonstration assets so the project has a clear route from the completed optimiser to a Gazebo visualisation.

## ROS 2/LIMO Next Step

The next stage for real LIMO robots would be:

1. Wrap the optimiser output as a ROS 2 node.
2. Publish assigned goals to robot namespaces such as `/robot1/navigate_to_pose`.
3. Use Nav2 for motion execution.
4. Replace the pose-playback script with real robot controllers.
5. Use AprilTag/localisation feedback for physical LIMO deployment.

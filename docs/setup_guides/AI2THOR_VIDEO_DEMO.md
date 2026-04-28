# AI2-THOR Floor 6 Video Demo

The primary no-server demo command is:

```powershell
.\scripts\run_floor6_ai2thor_video.ps1
```

or:

```bash
python scripts/run_floor6_ai2thor_video.py --open-video
```

The command:

1. Parses the default Floor 6 mission.
2. Validates the structured mission.
3. Runs MILP task allocation.
4. Generates a plan trace.
5. Launches AI2-THOR `FloorPlan6`.
6. Records real AI2-THOR frames to `docs/demo_video_script/floor6_ai2thor_demo.mp4`.
7. Opens the video in VLC if VLC is installed, otherwise the default video player.

## Important Realism Note

AI2-THOR provides realistic indoor simulator frames, but it does not include visible LIMO robot bodies by default. This demo records real FloorPlan6 scene evidence and overlays the task execution trace. For visible LIMO robot bodies moving through a world, use the Gazebo/ROS 2 LIMO layer or add custom robot assets to an AI2-THOR/Unity build.

The script deliberately does not generate a fake cartoon fallback. If AI2-THOR cannot launch, it exits with setup guidance.

## Windows Limitation

AI2-THOR builds are not reliably available for every Windows/Python/Unity commit combination. If you see an error similar to:

```text
Invalid commit_id ... no build exists for arch=Windows
```

run this demo on Linux, WSL2 with WSLg/display support, or a robotics workstation where AI2-THOR can launch Unity scenes. The rest of the Open LaMMA-R stack still runs on Windows: JSON validation, PDDL generation, MILP allocation, planning fallback, tests and evaluation.

## Visible LIMO Robots

AI2-THOR is a household embodied-agent simulator; it does not provide LIMO robot meshes or multi-robot bodies out of the box. For a video where physical-looking LIMO robots visibly drive around, use the ROS 2/Gazebo path and map the same Open LaMMA-R plan actions to Gazebo LIMO models. AI2-THOR is best used here for realistic Floor 6-style indoor task context and evidence frames.

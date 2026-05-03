#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORLD_FILE="$ROOT_DIR/worlds/lammap_gazebo_demo.sdf"
WORLD_NAME="lammap_demo"
GZ_SIM_ARGS="${GZ_SIM_ARGS:-}"

if [ ! -f "$WORLD_FILE" ]; then
  echo "ERROR: World file not found: $WORLD_FILE"
  exit 1
fi

if ! command -v gz >/dev/null 2>&1; then
  echo "ERROR: Gazebo Sim command 'gz' was not found."
  echo "Install Gazebo Sim on Ubuntu, then rerun:"
  echo "  cd .. && bash scripts/setup_ubuntu.sh"
  echo "or install Gazebo manually from:"
  echo "  https://gazebosim.org/docs/latest/install_ubuntu/"
  echo "Then:"
  echo "  bash gazebo_demo/scripts/run_gz_sim_demo.sh"
  exit 1
fi

if ! gz sim --help >/dev/null 2>&1; then
  echo "ERROR: 'gz' exists, but 'gz sim' is not available."
  echo "This usually means Gazebo Classic was installed instead of Gazebo Sim."
  echo "The current demo requires Gazebo Sim (for example gz-harmonic or gz-garden)."
  echo "Remove or ignore Gazebo Classic and install Gazebo Sim, then rerun:"
  echo "  sudo apt-get install -y gz-harmonic"
  exit 1
fi

if [ -z "${DISPLAY:-}" ] && [ -z "${WAYLAND_DISPLAY:-}" ]; then
  echo "WARNING: DISPLAY and WAYLAND_DISPLAY are both unset."
  echo "WARNING: Gazebo GUI may not open. If you only want a headless smoke test, run:"
  echo "  gz sim -s -r \"$WORLD_FILE\""
fi

find_set_pose_service() {
  local service_list
  service_list="$(gz service -l 2>/dev/null || true)"
  if printf '%s\n' "$service_list" | grep -q "^/world/$WORLD_NAME/set_pose$"; then
    printf '/world/%s/set_pose\n' "$WORLD_NAME"
    return 0
  fi
  local discovered
  discovered="$(printf '%s\n' "$service_list" | grep '/world/.*/set_pose' | head -n 1 || true)"
  if [ -n "$discovered" ]; then
    printf '%s\n' "$discovered"
    return 0
  fi
  return 1
}

echo "Launching Gazebo Sim world: $WORLD_FILE"
echo "If the Gazebo GUI is already open, close it before rerunning this script."
gz sim -r "$WORLD_FILE" $GZ_SIM_ARGS &
GZ_PID=$!

cleanup() {
  if kill -0 "$GZ_PID" >/dev/null 2>&1; then
    kill "$GZ_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

sleep 5
SET_POSE_SERVICE="$(find_set_pose_service || true)"
if [ -z "$SET_POSE_SERVICE" ]; then
  echo "WARNING: Could not auto-discover a /world/.../set_pose service."
  echo "WARNING: The world may still be loading, or Gazebo may be running headless only."
  echo "Available services:"
  gz service -l 2>/dev/null || true
  echo "Leaving Gazebo running for manual inspection."
  wait "$GZ_PID"
  exit 1
fi

echo "Using Gazebo service: $SET_POSE_SERVICE"

set_pose() {
  local name="$1"
  local x="$2"
  local y="$3"
  local z="$4"
  echo "set_pose $name -> x=$x y=$y z=$z"
  gz service \
    -s "$SET_POSE_SERVICE" \
    --reqtype gz.msgs.Pose \
    --reptype gz.msgs.Boolean \
    --timeout 2000 \
    --req "name: '$name' position: {x: $x y: $y z: $z}" >/dev/null || true
}

move_line() {
  local name="$1"
  local x1="$2"
  local y1="$3"
  local z="$4"
  local x2="$5"
  local y2="$6"
  local steps="${7:-18}"
  local carry="${8:-}"
  for i in $(seq 0 "$steps"); do
    local x
    local y
    x=$(awk -v a="$x1" -v b="$x2" -v i="$i" -v n="$steps" 'BEGIN { printf "%.3f", a + (b-a)*i/n }')
    y=$(awk -v a="$y1" -v b="$y2" -v i="$i" -v n="$steps" 'BEGIN { printf "%.3f", a + (b-a)*i/n }')
    set_pose "$name" "$x" "$y" "$z"
    if [ -n "$carry" ]; then
      set_pose "$carry" "$x" "$y" "0.46"
    fi
    sleep 0.15
  done
}

echo "Playing optimiser-derived mission:"
echo "  robot1: Move Apple to Fridge"
echo "  robot2: Move Tomato to Fridge"
echo "  robot3: SwitchOff LightSwitch"

move_line robot1 -5.2 1.6 0.18 -3.8 1.6 10
move_line robot1 -3.8 1.6 0.18 4.4 0.35 30 apple
set_pose apple 4.75 0.25 0.7

move_line robot2 -5.2 -1.6 0.18 -3.6 -1.6 10
move_line robot2 -3.6 -1.6 0.18 4.4 -0.35 30 tomato
set_pose tomato 4.75 -0.25 0.72

move_line robot3 -5.2 -3.0 0.18 4.35 -2.8 34
echo "robot3 reached light switch: SwitchOff complete"

echo "Gazebo mission complete. Close Gazebo or press Ctrl+C."
wait "$GZ_PID"

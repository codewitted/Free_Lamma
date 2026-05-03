#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ "$(uname -s)" != "Linux" ]; then
  echo "ERROR: This setup script is for Ubuntu/Linux. Current OS: $(uname -s)"
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo "ERROR: apt-get not found. This script targets Ubuntu/Debian."
  exit 1
fi

if ! command -v sudo >/dev/null 2>&1; then
  echo "WARNING: sudo not found. System package installation will be skipped."
fi

have_working_sudo() {
  command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1
}

if have_working_sudo; then
  echo "==> Updating apt metadata"
  sudo apt-get update

  echo "==> Installing base system dependencies"
  sudo apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    mesa-utils
else
  echo "WARNING: sudo is unavailable or blocked in this environment."
  echo "WARNING: Skipping apt installs. On a normal Ubuntu/WSL machine, rerun this script with sudo enabled."
fi

echo "==> Creating Python virtual environment"
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip setuptools wheel || true
if ! .venv/bin/python -m pip install -r requirements.txt; then
  echo "WARNING: Python dependency installation failed."
  echo "WARNING: Continuing with built-in modules only. Optimiser and parser checks can still run."
fi

if command -v gz >/dev/null 2>&1 && gz sim --help >/dev/null 2>&1; then
  echo "==> Gazebo Sim already installed: $(gz sim --versions 2>/dev/null || gz --versions 2>/dev/null || true)"
else
  if command -v gz >/dev/null 2>&1; then
    echo "WARNING: Found a 'gz' command, but 'gz sim' is unavailable."
    echo "WARNING: This usually means Gazebo Classic is installed instead of Gazebo Sim."
    echo "WARNING: The demo requires Gazebo Sim (gz-harmonic/gz-garden), not classic gazebo11."
  fi
  if have_working_sudo; then
    echo "==> Installing Gazebo Sim via official OSRF packages"
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://packages.osrfoundation.org/gazebo.gpg \
      | sudo gpg --dearmor -o /etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
      | sudo tee /etc/apt/sources.list.d/gazebo-stable.list >/dev/null
    sudo apt-get update

    if apt-cache show gz-harmonic >/dev/null 2>&1; then
      sudo apt-get install -y gz-harmonic
    elif apt-cache show gz-garden >/dev/null 2>&1; then
      sudo apt-get install -y gz-garden
    elif apt-cache show ignition-fortress >/dev/null 2>&1; then
      sudo apt-get install -y ignition-fortress
    else
      echo "ERROR: No supported Gazebo Sim package found for this Ubuntu release."
      echo "Install Gazebo manually from https://gazebosim.org/docs/latest/install_ubuntu/"
      exit 1
    fi
  else
    echo "WARNING: Gazebo Sim not installed and cannot be auto-installed without working sudo."
  fi
fi

echo "==> Running local project checks"
.venv/bin/python -m py_compile \
  scripts/demo_ai2thor_video.py \
  scripts/constraint_optimizer.py \
  scripts/run_natural_command.py \
  scripts/check_local_llm.py \
  gazebo_demo/scripts/check_gazebo_assets.py
.venv/bin/python gazebo_demo/scripts/check_gazebo_assets.py
bash -n gazebo_demo/scripts/run_gz_sim_demo.sh
bash -n scripts/verify_ubuntu_pipeline.sh

echo
echo "Ubuntu setup complete."
echo "Next:"
echo "  bash scripts/verify_ubuntu_pipeline.sh"
echo
echo "For Gazebo GUI demo only:"
echo "  cd gazebo_demo && bash scripts/run_gz_sim_demo.sh"

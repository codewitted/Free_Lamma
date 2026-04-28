"""Central configuration for Open LaMMA-R."""

from __future__ import annotations

import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
RESULTS_DIR = ROOT_DIR / "evaluation" / "results"
PLOTS_DIR = ROOT_DIR / "evaluation" / "plots"
SCENARIOS_DIR = ROOT_DIR / "simulation" / "scenarios"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OPENWEBUI_BASE_URL = os.getenv("OPENWEBUI_BASE_URL", "http://localhost:3000")
OPENWEBUI_API_KEY = os.getenv("OPENWEBUI_API_KEY", "")
USE_PAID_API = os.getenv("USE_PAID_API", "false").lower() == "true"
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

FAST_DOWNWARD_PATH = os.getenv("FAST_DOWNWARD_PATH", "")
PLANNER_TIMEOUT_SECONDS = int(os.getenv("PLANNER_TIMEOUT_SECONDS", "30"))
EXECUTION_MODE = os.getenv("EXECUTION_MODE", "dry_run")


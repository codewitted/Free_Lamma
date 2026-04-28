"""FastAPI backend for Open LaMMA-R."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from backend.executor import ai2thor_executor, dry_run_executor, ros2_dispatcher
from backend.llm_gateway.local_llm import generate_structured_plan
from backend.llm_gateway.schema import default_floor6_world
from backend.optimiser.milp_allocator import allocate_tasks
from backend.pddl.problem_generator import generate_problem
from backend.pddl.pddl_validator import validate_pddl_text
from backend.planner.fast_downward_client import FastDownwardClient, PlannerUnavailable, heuristic_plan_from_mission


app = FastAPI(title="Open LaMMA-R API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class CommandRequest(BaseModel):
    command: str
    world_state: dict[str, Any] | None = None


class MissionRequest(BaseModel):
    mission: dict[str, Any]


class ExecuteRequest(BaseModel):
    actions: list[dict[str, Any]]
    mode: str = "dry_run"


@app.get("/api/status")
def status() -> dict[str, Any]:
    return {
        "status": "ok",
        "llm_provider": settings.LLM_PROVIDER,
        "ollama_base_url": settings.OLLAMA_BASE_URL,
        "fast_downward_found": FastDownwardClient().executable_path is not None,
        "execution_mode": settings.EXECUTION_MODE,
    }


@app.post("/api/parse")
def parse(req: CommandRequest) -> dict[str, Any]:
    return generate_structured_plan(req.command, req.world_state or default_floor6_world())


@app.post("/api/generate-pddl")
def generate_pddl(req: MissionRequest) -> dict[str, Any]:
    text = generate_problem(req.mission)
    valid, errors = validate_pddl_text(text)
    return {"pddl": text, "valid": valid, "errors": errors}


@app.post("/api/optimise")
def optimise(req: MissionRequest) -> dict[str, Any]:
    return allocate_tasks(req.mission)


@app.post("/api/plan")
def plan(req: MissionRequest) -> dict[str, Any]:
    mission = req.mission
    pddl = generate_problem(mission)
    tmp_problem = settings.RESULTS_DIR / "latest_problem.pddl"
    tmp_problem.parent.mkdir(parents=True, exist_ok=True)
    tmp_problem.write_text(pddl, encoding="utf-8")
    try:
        return FastDownwardClient().run_planner(settings.BACKEND_DIR / "pddl" / "domain.pddl", tmp_problem)
    except PlannerUnavailable as exc:
        return {"status": "fallback", "reason": str(exc), "actions": heuristic_plan_from_mission(mission)}


@app.post("/api/execute")
def execute(req: ExecuteRequest) -> dict[str, Any]:
    if req.mode == "ai2thor":
        return ai2thor_executor.execute_plan(req.actions)
    if req.mode == "ros2":
        return ros2_dispatcher.dispatch_plan(req.actions)
    return dry_run_executor.execute_plan(req.actions)


@app.post("/api/run-full-pipeline")
def run_full_pipeline(req: CommandRequest) -> dict[str, Any]:
    mission = parse(req)
    allocation = allocate_tasks(mission)
    assigned = {item["task_id"]: item["assigned_robot"] for item in allocation["allocation"]}
    for task in mission["tasks"]:
        if assigned.get(task["task_id"]):
            task["assigned_robot"] = assigned[task["task_id"]]
    pddl = generate_problem(mission)
    plan_result = plan(MissionRequest(mission=mission))
    execution = dry_run_executor.execute_plan(plan_result.get("actions", []))
    return {"mission": mission, "pddl": pddl, "allocation": allocation, "plan": plan_result, "execution": execution}


@app.get("/api/results")
def results() -> dict[str, Any]:
    settings.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return {"files": [str(path.relative_to(settings.ROOT_DIR)) for path in settings.RESULTS_DIR.glob("*") if path.is_file()]}


"""Pydantic schema for strict LLM output validation."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Robot(BaseModel):
    id: str
    start_location: str
    capabilities: list[str] = Field(default_factory=list)
    battery: float = Field(ge=0, le=100, default=100)
    available: bool = True


class Task(BaseModel):
    task_id: str
    type: Literal["pickup_and_deliver", "inspect", "navigate", "meet", "charge", "wait"]
    object: str | None = None
    source: str
    destination: str | None = None
    priority: int = Field(default=1, ge=1, le=10)
    required_capabilities: list[str] = Field(default_factory=list)
    robot_hint: str | None = None
    estimated_duration: float = Field(default=1.0, ge=0)

    @model_validator(mode="after")
    def delivery_has_destination(self) -> "Task":
        if self.type == "pickup_and_deliver" and not self.destination:
            raise ValueError("pickup_and_deliver tasks require destination")
        return self


class Constraints(BaseModel):
    avoid_collisions: bool = True
    minimise_travel: bool = True
    respect_battery: bool = True
    max_workload_per_robot: int | None = None


class MissionPlan(BaseModel):
    mission_id: str = "floor6_demo_001"
    floor: str = "Floor6"
    robots: list[Robot]
    tasks: list[Task]
    constraints: Constraints = Field(default_factory=Constraints)
    locations: list[str] = Field(default_factory=list)
    connectivity: list[tuple[str, str]] = Field(default_factory=list)

    @field_validator("robots", "tasks")
    @classmethod
    def must_not_be_empty(cls, value: list[Any]) -> list[Any]:
        if not value:
            raise ValueError("field must not be empty")
        return value

    @model_validator(mode="after")
    def infer_locations_and_connectivity(self) -> "MissionPlan":
        locations = set(self.locations)
        for robot in self.robots:
            locations.add(robot.start_location)
        for task in self.tasks:
            locations.add(task.source)
            if task.destination:
                locations.add(task.destination)
        self.locations = sorted(locations)
        if not self.connectivity:
            ordered = list(self.locations)
            self.connectivity = [(a, b) for a in ordered for b in ordered if a != b]
        return self


def default_floor6_world() -> dict[str, Any]:
    return {
        "floor": "Floor6",
        "locations": ["corridor", "office", "kitchen", "storage_room", "charging_dock"],
        "connectivity": [
            ["corridor", "office"],
            ["corridor", "kitchen"],
            ["corridor", "storage_room"],
            ["corridor", "charging_dock"],
        ],
        "robots": [
            {"id": "robot1", "start_location": "corridor", "capabilities": ["navigate", "pickup", "drop"], "battery": 90},
            {"id": "robot2", "start_location": "corridor", "capabilities": ["navigate", "pickup", "drop"], "battery": 85},
            {"id": "robot3", "start_location": "corridor", "capabilities": ["navigate", "inspect"], "battery": 80},
        ],
    }


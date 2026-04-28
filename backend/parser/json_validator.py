"""Robust JSON extraction and validation for LLM responses."""

from __future__ import annotations

import json
import re
from typing import Any

from pydantic import ValidationError

from backend.llm_gateway.schema import MissionPlan


class MissionValidationError(ValueError):
    """Raised when LLM output cannot be converted into a valid mission."""


def strip_markdown_fences(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?", "", cleaned.strip(), flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned.strip()).strip()
    return cleaned


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = strip_markdown_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise MissionValidationError("No JSON object found in LLM response")
    snippet = cleaned[start : end + 1]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise MissionValidationError(f"Invalid JSON: {exc}") from exc


def validate_mission(data: dict[str, Any]) -> MissionPlan:
    try:
        return MissionPlan.model_validate(data)
    except ValidationError as exc:
        raise MissionValidationError(str(exc)) from exc


def parse_and_validate(text: str) -> MissionPlan:
    return validate_mission(extract_json_object(text))


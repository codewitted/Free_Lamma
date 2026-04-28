"""Local/free LLM gateway with robust fallback behavior."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib import request

from backend.config import settings
from backend.llm_gateway.prompt_templates import (
    STRICT_JSON_SYSTEM_PROMPT,
    build_correction_prompt,
    build_user_prompt,
)
from backend.parser.fallback_parser import parse_rule_based
from backend.parser.json_validator import MissionValidationError, parse_and_validate


def _post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class LocalLLMGateway:
    """Gateway for Ollama, OpenWebUI and disabled-by-default paid API fallback."""

    def __init__(self, provider: str | None = None) -> None:
        self.provider = (provider or settings.LLM_PROVIDER).lower()

    def _ollama_generate(self, command: str, world_state: dict[str, Any], correction: str | None = None) -> str:
        prompt = correction or build_user_prompt(command, world_state)
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": STRICT_JSON_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }
        result = _post_json(f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat", payload)
        return result.get("message", {}).get("content", "")

    def _openai_compatible_generate(self, base_url: str, api_key: str, model: str, command: str, world_state: dict[str, Any], correction: str | None = None) -> str:
        prompt = correction or build_user_prompt(command, world_state)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": STRICT_JSON_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{base_url.rstrip('/')}/chat/completions",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key or 'local'}"},
            method="POST",
        )
        with request.urlopen(req, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"]

    def _generate_once(self, command: str, world_state: dict[str, Any], correction: str | None = None) -> str:
        if self.provider == "ollama":
            return self._ollama_generate(command, world_state, correction)
        if self.provider == "openwebui":
            return self._openai_compatible_generate(settings.OPENWEBUI_BASE_URL, settings.OPENWEBUI_API_KEY, settings.OLLAMA_MODEL, command, world_state, correction)
        if self.provider == "openai" and settings.USE_PAID_API:
            return self._openai_compatible_generate(settings.OPENAI_BASE_URL, settings.OPENAI_API_KEY, settings.OPENAI_MODEL, command, world_state, correction)
        raise RuntimeError(f"LLM provider '{self.provider}' unavailable or disabled")

    def generate_structured_plan(self, command: str, world_state: dict[str, Any]) -> dict[str, Any]:
        start = time.perf_counter()
        previous = ""
        try:
            previous = self._generate_once(command, world_state)
            mission = parse_and_validate(previous)
            source = self.provider
            retries = 0
        except Exception as first_error:
            try:
                correction = build_correction_prompt(previous, str(first_error))
                previous = self._generate_once(command, world_state, correction)
                mission = parse_and_validate(previous)
                source = f"{self.provider}-corrected"
                retries = 1
            except Exception:
                mission = parse_rule_based(command, world_state)
                source = "rule_based_fallback"
                retries = 1

        payload = mission.model_dump()
        payload["_metadata"] = {
            "source": source,
            "provider": self.provider,
            "latency_seconds": round(time.perf_counter() - start, 4),
            "retries": retries,
        }
        return payload


def generate_structured_plan(command: str, world_state: dict[str, Any]) -> dict[str, Any]:
    return LocalLLMGateway().generate_structured_plan(command, world_state)


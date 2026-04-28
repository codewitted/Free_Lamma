"""Lightweight PDDL sanity checks."""

from __future__ import annotations

from pathlib import Path


def validate_pddl_text(text: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if text.count("(") != text.count(")"):
        errors.append("Unbalanced parentheses")
    for required in ["(define", "(:objects", "(:init", "(:goal"]:
        if required not in text:
            errors.append(f"Missing {required}")
    return not errors, errors


def validate_pddl_file(path: str | Path) -> tuple[bool, list[str]]:
    return validate_pddl_text(Path(path).read_text(encoding="utf-8"))


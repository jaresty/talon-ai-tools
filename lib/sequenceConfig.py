# ADR-0225: Named Workflow Sequences — Python SSOT.
#
# Each sequence is a named, directed multi-step workflow pattern. Sequences encode
# the claim that step N's output makes step N+1 more effective than running N+1 cold.
# This is distinct from cross_axis_composition natural pairings, which encode
# compatibility without direction.
#
# Discovery protocol: see ADR-0225 §"Sequence discovery via shuffle".
# Promotion requires: chain test across ≥2 subjects, ordering rationale documented.

from typing import Any

SEQUENCES: dict[str, dict[str, Any]] = {
    "experiment-cycle": {
        "description": "Frame a hypothesis before running an experiment, then review evidence afterward.",
        "steps": [
            {
                "token": "form:prep",
                "role": "pre-experiment framing",
                "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment.",
            },
            {
                "token": "form:vet",
                "role": "post-experiment review",
                "prompt_hint": "Use this step to evaluate the evidence against the original hypothesis.",
            },
        ],
    },
    "debug-cycle": {
        "description": "Surface root causes, fix them, then verify the fix holds.",
        "steps": [
            {
                "token": "task:probe",
                "role": "root cause investigation",
                "prompt_hint": "Use this step to surface hidden assumptions and possible causes before writing any fix.",
            },
            {
                "token": "task:fix",
                "role": "repair",
                "prompt_hint": "Use this step to implement the targeted fix once the root cause is confirmed.",
            },
            {
                "token": "task:check",
                "role": "verification",
                "prompt_hint": "Use this step to verify the fix holds and no regressions were introduced.",
            },
        ],
    },
    "scenario-to-plan": {
        "description": "Simulate a scenario, then derive the action plan it implies.",
        "steps": [
            {
                "token": "method:sim",
                "role": "scenario simulation",
                "prompt_hint": "Use this step to simulate the scenario and observe what it implies.",
            },
            {
                "token": "method:plan",
                "role": "action planning",
                "prompt_hint": "Use this step to convert the simulation's implications into a concrete action plan.",
            },
        ],
    },
    "extract-and-package": {
        "description": "Extract a relevant subset, then package it for downstream use.",
        "steps": [
            {
                "token": "method:pull",
                "role": "extraction",
                "prompt_hint": "Use this step to identify and extract only the relevant material from the subject.",
            },
            {
                "token": "method:contextualise",
                "role": "packaging",
                "prompt_hint": "Use this step to wrap the extracted material with enough context for a downstream reader or LLM.",
            },
        ],
    },
}


def validate_sequences(sequences: dict[str, Any], known_tokens: set[str]) -> list[str]:
    """Return a list of validation errors. Empty list means valid.

    Checks:
    - Each sequence has description (str) and steps (list of ≥2).
    - Each step has token (str) and role (str).
    - Each step token references a known axis:slug.
    """
    errors: list[str] = []
    for name, seq in sequences.items():
        if not isinstance(seq.get("description"), str) or not seq["description"]:
            errors.append(f"{name}: missing or empty description")
        steps = seq.get("steps", [])
        if not isinstance(steps, list) or len(steps) < 2:
            errors.append(f"{name}: steps must be a list of ≥2 entries")
            continue
        for i, step in enumerate(steps):
            if not isinstance(step.get("token"), str) or not step["token"]:
                errors.append(f"{name} step {i}: missing token")
            elif known_tokens and step["token"] not in known_tokens:
                errors.append(f"{name} step {i}: unknown token {step['token']!r}")
            if not isinstance(step.get("role"), str) or not step["role"]:
                errors.append(f"{name} step {i}: missing role")
    return errors


__all__ = ["SEQUENCES", "validate_sequences"]

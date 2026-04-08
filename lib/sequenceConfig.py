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
    "debug-cycle": {
        "description": "Surface root causes, fix them, then verify the fix holds.",
        "example": "A production service is returning 500s intermittently and the cause is unknown.",
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "root cause investigation",
                "prompt_hint": "Use this step to surface hidden assumptions and possible causes before writing any fix.",
                "requires_user_input": True,  # user must attempt fix before verification
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
    "experiment-cycle": {
        "description": "Frame a hypothesis before running an experiment, then review evidence afterward.",
        "example": "Testing whether adding a cache layer reduces p95 latency below 200ms.",
        "mode": "cycle",
        "steps": [
            {
                "token": "form:prep",
                "role": "pre-experiment framing",
                "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment.",
                "requires_user_input": True,  # user must run the experiment before vet
            },
            {
                "token": "form:vet",
                "role": "post-experiment review",
                "prompt_hint": "Use this step to evaluate the evidence against the original hypothesis.",
            },
        ],
    },
    "extract-and-package": {
        "description": "Extract a relevant subset, then package it for downstream use.",
        "example": "Pull the authentication flow from a large codebase and package it as context for a new engineer.",
        "mode": "autonomous",
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
    "gather-and-synthesize": {
        "description": "Frame what to gather, collect it in the real world, then synthesize findings into conclusions.",
        "example": "Understanding why engineers on a team are reluctant to write tests.",
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "gathering frame",
                "prompt_hint": "Use this step to produce interview questions, a research plan, or observation vectors the user can go execute.",
                "requires_user_input": True,  # user must gather before synthesis
            },
            {
                "token": "task:show",
                "role": "synthesis",
                "prompt_hint": "Use this step to extract patterns and generalize conclusions from the gathered findings.",
            },
        ],
    },
    "plan-and-retrospect": {
        "description": "Derive an action plan, implement it in the real world, then retrospectively review what worked.",
        "example": "Improving a team's code review process over two iterations.",
        "mode": "cycle",
        "steps": [
            {
                "token": "task:plan",
                "role": "action planning",
                "prompt_hint": "Use this step to produce concrete steps the user can go implement.",
                "requires_user_input": True,  # user must implement before retrospective
            },
            {
                "token": "form:vet",
                "role": "retrospective review",
                "prompt_hint": "Use this step to evaluate what worked, what didn't, and what to adjust in the next cycle.",
            },
        ],
    },
    "scenario-to-plan": {
        "description": "Simulate a scenario, then derive the action plan it implies.",
        "example": "Planning a migration from a monolith to microservices.",
        "mode": "autonomous",
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
    "simulate-and-review": {
        "description": "Simulate a scenario before executing it, then review actual outcomes against the simulation.",
        "example": "Migrating the auth service as a pilot for a broader microservices migration.",
        "mode": "linear",
        "steps": [
            {
                "token": "method:sim",
                "role": "pre-execution simulation",
                "prompt_hint": "Use this step to anticipate risks and surface hidden dependencies before the user executes.",
                "requires_user_input": True,  # user must execute before review
            },
            {
                "token": "task:check",
                "role": "outcome review",
                "prompt_hint": "Use this step to compare what actually happened against the simulation's predictions.",
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

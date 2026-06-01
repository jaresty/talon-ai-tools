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
        "heuristics": ["investigate then fix", "debug and verify", "find and fix", "root cause then repair", "diagnose fix verify", "something is broken fix it", "find the bug fix it check it"],
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
        "heuristics": ["run an experiment", "test a hypothesis", "scientific method", "hypothesis and evidence", "frame then test", "design an experiment", "validate with data"],
        "mode": "cycle",
        "stop_when": "The hypothesis has been confirmed or falsified — further iterations would not change the conclusion.",
        "steps": [
            {
                "token": "form:prep",
                "role": "pre-experiment framing",
                "prompt_hint": "Use this step to state the hypothesis and success criteria before running the experiment.",
            },
            {
                "type": "action",
                "role": "experiment execution",
                "prompt_hint": "Run the experiment defined in the prior step. Collect results before proceeding to vet.",
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
        "heuristics": ["extract and package", "pull out and wrap", "extract relevant parts", "package for downstream", "extract context", "isolate and document"],
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
        "heuristics": ["gather and synthesize", "collect and summarize", "research and conclude", "gather evidence then synthesize", "interview then analyze", "collect findings"],
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
    "check-and-rewrite": {
        "description": "Evaluate an artifact against criteria, then rewrite it so the gaps are closed.",
        "example": "Reviewing a technical design doc and rewriting the sections that don't hold up.",
        "heuristics": ["check then rewrite", "evaluate and revise", "review then fix", "find gaps and close them", "critique then improve", "audit and rewrite"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "task:check",
                "role": "gap evaluation",
                "prompt_hint": "Use this step to evaluate the subject against criteria and surface specific gaps.",
            },
            {
                "token": "task:fix",
                "role": "form revision",
                "prompt_hint": "Use this step to rewrite the artifact so that the gaps identified in the evaluation are closed — change presentation or structure, not meaning.",
            },
        ],
    },
    "make-and-review": {
        "description": "Produce an artifact, then review it critically before treating it as done.",
        "example": "Drafting an ADR and reviewing it for gaps before publishing.",
        "heuristics": ["make then review", "draft and critique", "produce then evaluate", "write then check", "create and review", "build and vet"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "task:make",
                "role": "artifact production",
                "prompt_hint": "Use this step to produce the artifact — document, plan, design, or code.",
            },
            {
                "token": "form:vet",
                "role": "critical review",
                "prompt_hint": "Use this step to review the artifact: what was produced, how it compares to intent, what is missing or weak.",
            },
        ],
    },
    "probe-and-plan": {
        "description": "Diagnose the structure and hidden assumptions of a situation, then derive a targeted action plan.",
        "example": "Figuring out why a team is slow to ship, then planning what to change.",
        "heuristics": ["diagnose then plan", "understand then act", "investigate then plan", "surface assumptions then plan", "why then what", "root cause then roadmap"],
        "mode": "linear",
        "steps": [
            {
                "token": "task:probe",
                "role": "structural diagnosis",
                "prompt_hint": "Use this step to surface hidden assumptions, root causes, and structural factors before planning.",
                "requires_user_input": True,
            },
            {
                "token": "task:plan",
                "role": "targeted action plan",
                "prompt_hint": "Use this step to produce a plan that directly addresses the findings from diagnosis.",
            },
        ],
    },
    "plan-and-retrospect": {
        "description": "Derive an action plan, implement it in the real world, then retrospectively review what worked.",
        "example": "Improving a team's code review process over two iterations.",
        "heuristics": ["plan then retrospect", "act and reflect", "implement and review", "try then learn", "plan execute review", "iterative improvement"],
        "mode": "cycle",
        "stop_when": "The process has stabilized — the retrospective finds no new gaps worth addressing in another cycle.",
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
        "heuristics": ["simulate then plan", "what if then what now", "scenario planning", "model the future then plan", "anticipate then act"],
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
    "simulate-and-make": {
        "description": "Simulate the consequences of a scenario, then produce the artifact the simulation implies is needed.",
        "example": "Simulating a security breach to determine what runbook needs to be written.",
        "heuristics": ["simulate then build", "what happens then what to make", "anticipate then produce", "simulate consequences then act"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "method:sim",
                "role": "consequence simulation",
                "prompt_hint": "Use this step to simulate the scenario and surface what it implies is missing or needed.",
            },
            {
                "token": "task:make",
                "role": "artifact production",
                "prompt_hint": "Use this step to produce the artifact the simulation revealed is needed.",
            },
        ],
    },
    "parallel-eval": {
        "description": "Enumerate independent evaluation frames, execute each in isolation, then converge on a recommendation.",
        "example": "Evaluating a proposed API design from the perspectives of a security engineer, a frontend consumer, and a platform operator — each independently, with no shared priors.",
        "heuristics": ["evaluate independently", "multiple independent perspectives", "parallel evaluation", "isolated ideation", "spin up subagents", "evaluate from each angle separately", "no shared context between evaluators", "independent assessments then merge"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Use this step to enumerate the named evaluation frames as a governing artifact. Each frame must differ structurally. Do not apply any frame yet — enumeration is the only output of this step.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame evaluation",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "prompt_hint": "Each agent receives only the subject and its assigned frame description as full context — no shared history, no cross-frame information. Return findings in a labeled block.",
            },
            {
                "token": "task:show",
                "role": "independent results collection",
                "prompt_hint": "Use this step to present the results returned from each isolated subagent evaluation — one labeled block per frame, preserving the original framing without interpretation. Do not synthesize yet.",
            },
            {
                "token": "pick method:converge",
                "role": "synthesis",
                "prompt_hint": "Use this step to narrow from the independent frame results to a recommendation, naming what each frame contributed and what was excluded.",
            },
        ],
    },
    "frame-explore": {
        "description": "Enumerate independent frames for a problem, run an experiment cycle within each frame until a goal is reached, then converge on findings across frames.",
        "example": "Exploring whether a proposed API simplification holds up — framed from security, usability, and performance angles — each angle running hypothesis/evidence cycles until the goal condition is satisfied.",
        "heuristics": ["explore from multiple angles", "parallel frame exploration", "hypothesis cycles per frame", "experiment across frames", "multi-frame investigation", "test each angle independently", "explore then converge"],
        "mode": "autonomous",
        "stop_when": "Each frame's experiment cycle has reached the goal condition stated in the original subject.",
        "steps": [
            {
                "token": "make method:prism",
                "role": "frame enumeration",
                "prompt_hint": "Use this step to enumerate the named exploration frames as a governing artifact. Each frame must differ structurally. Also extract and state the goal condition from the subject — this becomes the stop_when for each frame's experiment cycle. Only enumerate frames whose experiments are fully agent-executable (code analysis, API calls, test runs, document review) — frames that require human data-gathering do not belong in this sequence. Do not apply any frame yet.",
            },
            {
                "type": "dispatch",
                "role": "parallel frame experiment cycles",
                "fan_out": "enumerate",
                "join": "all",
                "isolation": True,
                "prompt_hint": "Each agent receives only the subject, its assigned frame description, and the goal condition. Execute the inner sequence until stop_when is met. Return findings in a labeled block with the number of cycles run.",
                "inner": {
                    "mode": "cycle",
                    "stop_when": "The goal condition stated in the subject is satisfied from this frame's perspective — evidence is sufficient for a confident verdict.",
                    "steps": [
                        {
                            "token": "form:prep",
                            "role": "experiment framing",
                            "prompt_hint": "Frame the hypothesis for this cycle: what would be true if the goal condition is met from this frame's angle, and what evidence would confirm or refute it.",
                        },
                        {
                            "type": "action",
                            "role": "experiment execution",
                            "prompt_hint": "Execute the investigation defined in the prior step using available tools (code reads, API calls, test runs, document review). Record findings before proceeding to vet.",
                        },
                        {
                            "token": "form:vet",
                            "role": "evidence evaluation",
                            "prompt_hint": "Evaluate the evidence gathered against the hypothesis. State whether the goal condition is met, partially met, or unmet, and what further cycles would add.",
                        },
                    ],
                },
            },
            {
                "token": "task:show",
                "role": "per-frame findings collection",
                "prompt_hint": "Use this step to present the findings returned from each frame agent — one labeled block per frame, preserving the original framing and cycle count. Do not synthesize yet.",
            },
            {
                "token": "pick method:converge",
                "role": "cross-frame synthesis",
                "prompt_hint": "Use this step to synthesize across frames: what each frame's experiment cycles revealed, where frames agree or diverge, and what the combined evidence supports as a conclusion.",
            },
        ],
    },
    "frame-debug": {
        "description": "Enumerate independent fix hypotheses, race isolated agents to resolve each one, take the first that succeeds, then explain why it worked.",
        "example": "A service is returning intermittent 500s — enumerate candidate root causes (connection pool exhaustion, bad query plan, race condition, config drift), race fix attempts in parallel, take the first that resolves it.",
        "heuristics": ["race fix attempts", "parallel debugging", "first fix wins", "competing hypotheses", "parallel root cause attempts", "race to resolution", "try fixes in parallel"],
        "mode": "autonomous",
        "steps": [
            {
                "token": "make method:prism",
                "role": "fix hypothesis enumeration",
                "prompt_hint": "Use this step to enumerate independent fix hypotheses as a governing artifact. Each hypothesis must be a distinct candidate root cause with a concrete fix approach. Only enumerate hypotheses that are fully agent-verifiable (code inspection, test runs, tool calls). Do not apply any hypothesis yet.",
            },
            {
                "type": "dispatch",
                "role": "parallel fix attempts",
                "fan_out": "enumerate",
                "join": "first",
                "isolation": True,
                "prompt_hint": "Each agent receives only the subject and its assigned hypothesis. Execute the inner sequence until stop_when is met. Return a labeled block stating: hypothesis confirmed or rejected, evidence from the experiment cycles, and the fix applied (if confirmed). The first agent to resolve the problem wins.",
                "inner": {
                    "mode": "cycle",
                    "stop_when": "The problem stated in the subject is understood — the root cause is identified with sufficient evidence to act on.",
                    "steps": [
                        {
                            "token": "form:prep",
                            "role": "hypothesis framing",
                            "prompt_hint": "Frame the hypothesis as a testable claim: what would be true if this hypothesis is correct, and what evidence would confirm or reject it.",
                        },
                        {
                            "type": "action",
                            "role": "hypothesis investigation",
                            "prompt_hint": "Execute the investigation defined in the prior step using available tools (code reads, test runs, log inspection). Record findings before proceeding to vet.",
                        },
                        {
                            "token": "form:vet",
                            "role": "evidence evaluation",
                            "prompt_hint": "Evaluate the evidence gathered against the hypothesis. If confirmed, apply and verify the fix. If rejected, state why and stop.",
                        },
                    ],
                },
            },
            {
                "token": "pick method:converge",
                "role": "resolution explanation",
                "prompt_hint": "Use this step to explain the winning fix: what hypothesis was confirmed, what the fix was, what evidence verified it, and why the other hypotheses were not the cause (if known).",
            },
        ],
    },
    "simulate-and-review": {
        "description": "Simulate a scenario before executing it, then review actual outcomes against the simulation.",
        "example": "Migrating the auth service as a pilot for a broader microservices migration.",
        "heuristics": ["simulate then execute", "predict then review", "anticipate then evaluate", "pre-mortem then retrospective", "model then compare"],
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
            if not isinstance(step.get("role"), str) or not step["role"]:
                errors.append(f"{name} step {i}: missing role")
            step_type = step.get("type", "prompt")
            if step_type == "dispatch":
                if "token" in step:
                    errors.append(f"{name} step {i}: dispatch step must not have a token field")
                if not step.get("fan_out"):
                    errors.append(f"{name} step {i}: dispatch step missing fan_out")
                if not step.get("join"):
                    errors.append(f"{name} step {i}: dispatch step missing join")
            elif step_type == "action":
                if "token" in step:
                    errors.append(f"{name} step {i}: action step must not have a token field")
            else:
                if not isinstance(step.get("token"), str) or not step["token"]:
                    errors.append(f"{name} step {i}: missing token")
                elif known_tokens and step["token"] not in known_tokens:
                    errors.append(f"{name} step {i}: unknown token {step['token']!r}")
    return errors


__all__ = ["SEQUENCES", "validate_sequences"]

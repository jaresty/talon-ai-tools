"""Starter packs for ADR-0144 Phase 2.

Each StarterPack maps a task framing to a suggested `bar build` command.
Pack names must be:
  - A single pronounceable word (no spaces or hyphens)
  - Not conflicting with any registered bar token or axis name (bi-directional
    per ADR-0144: names checked here AND token registration must check this list)

Authoritative source for STARTER_PACKS; consumed by:
  - promptGrammar.py  → grammar JSON `starter_packs` key
  - cmd/bar/main.go   → `bar starter` subcommand (Loop 5)
  - SPA PatternsLibrary.svelte → starter packs section (Loop 6)
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class StarterPack:
    name: str                        # single word, no spaces/hyphens; unique; no token/axis conflicts
    framing: str                     # natural-language task description shown to users
    command: str                     # suggested `bar build ...` command (bare, pipeable)
    heuristics: tuple[str, ...] = () # trigger phrases for tier-matched lookup discovery


STARTER_PACKS: list[StarterPack] = [
    StarterPack(
        name="debug",
        framing="Diagnosing a bug or system failure",
        command="bar build probe diagnose adversarial unknowns",
        heuristics=("debug this", "something is broken", "bug investigation", "root cause analysis", "system failure", "diagnose the issue", "find the bug", "why is this failing"),
    ),
    StarterPack(
        name="design",
        framing="Architectural or interface design decision",
        command="bar build show spur compare balance",
        heuristics=("architecture decision", "design the system", "interface design", "how should we structure", "design review", "system design", "API design", "schema design"),
    ),
    StarterPack(
        name="review",
        framing="Code or document review",
        command="bar build check adversarial fail verify",
        heuristics=("review this", "code review", "review my PR", "check this code", "critique this", "find problems with", "review the document", "peer review"),
    ),
    StarterPack(
        name="dissect",
        framing="Deep structural understanding of a system",
        command="bar build probe analysis mapping depends",
        heuristics=("understand this codebase", "how does this work", "explain the architecture", "map the dependencies", "deep dive", "understand the system", "analyze the structure", "how is this organized"),
    ),
    StarterPack(
        name="pitch",
        framing="Making a case to stakeholders",
        command="bar build make argue compare analog",
        heuristics=("make the case for", "convince stakeholders", "justify this decision", "persuade", "pitch this idea", "argue for", "build the argument", "sell this to"),
    ),
    StarterPack(
        name="compliance",
        framing="Verifiable multi-step argument or compliance check",
        command="bar build check verify chain",
        heuristics=("compliance check", "verify requirements", "audit against", "does this meet", "check conformance", "verify the argument", "step by step verification", "traceability"),
    ),
    StarterPack(
        name="model",
        framing="Scenario simulation or what-if analysis",
        command="bar build sim simulation systemic effects",
        heuristics=("what if", "simulate this", "scenario analysis", "what would happen if", "model the system", "predict the outcome", "run the scenario", "what are the effects"),
    ),
    StarterPack(
        name="charter",
        framing="Planning a project or feature",
        command="bar build plan sweep prioritize fail",
        heuristics=("plan this project", "feature planning", "project charter", "what should we build", "roadmap", "scope this out", "plan the work", "prioritize features"),
    ),
    StarterPack(
        name="explain",
        framing="Explaining a concept or system to an audience",
        command="bar build show analog actors jobs",
        heuristics=("explain this", "help me understand", "teach me", "how do I explain", "make this clear", "explain to a", "describe how", "walk me through"),
    ),
    StarterPack(
        name="versus",
        framing="Structured comparison between alternatives",
        command="bar build diff compare converge polar",
        heuristics=("compare these", "which is better", "tradeoffs between", "pros and cons", "A vs B", "choose between", "evaluate options", "compare alternatives"),
    ),
    StarterPack(
        name="craft",
        framing="Disciplined iterative making — TDD and strict artifact cycles",
        command="bar build make witness ground gate falsify atomic",
        heuristics=("test driven development", "TDD", "red green refactor", "write tests first", "strict artifact", "falsify before implement", "disciplined iteration", "test-driven"),
    ),
    StarterPack(
        name="scout",
        framing="Research with a defined question — find what was asked, cite everything",
        command="bar build make gate verify",
        heuristics=("research this", "find information about", "look this up", "gather evidence", "cite sources", "investigate the topic", "find what exists", "literature review"),
    ),
    StarterPack(
        name="chisel",
        framing="Traceable incremental revision — one change per pass",
        command="bar build make chain atomic",
        heuristics=("one change at a time", "incremental revision", "atomic changes", "small focused edits", "step by step changes", "traceable edits", "refactor incrementally", "one thing at a time"),
    ),
    StarterPack(
        name="assay",
        framing="Behavioral eval suite from a prompt or instruction",
        command="bar build make method:hollow method:prism form:test completeness:triage",
        heuristics=("write evals for this", "generate eval cases", "evaluate this prompt", "behavioral coverage", "what evals should I write", "test this prompt", "prompt audit", "generate test cases for this instruction", "eval suite", "how do I know this prompt works"),
    ),
]

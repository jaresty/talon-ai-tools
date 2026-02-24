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

from dataclasses import dataclass


@dataclass(frozen=True)
class StarterPack:
    name: str      # single word, no spaces/hyphens; unique; no token/axis conflicts
    framing: str   # natural-language task description shown to users
    command: str   # suggested `bar build ...` command (bare, pipeable)


STARTER_PACKS: list[StarterPack] = [
    StarterPack(
        name="debug",
        framing="Diagnosing a bug or system failure",
        command="bar build probe diagnose adversarial unknowns",
    ),
    StarterPack(
        name="design",
        framing="Architectural or interface design decision",
        command="bar build show branch trade balance",
    ),
    StarterPack(
        name="review",
        framing="Code or document review",
        command="bar build check adversarial risks verify",
    ),
    StarterPack(
        name="dissect",
        framing="Deep structural understanding of a system",
        command="bar build probe analysis mapping depends",
    ),
    StarterPack(
        name="pitch",
        framing="Making a case to stakeholders",
        command="bar build make argue trade analog",
    ),
    StarterPack(
        name="audit",
        framing="Compliance, quality, or consistency check",
        command="bar build check verify canon rigor",
    ),
    StarterPack(
        name="model",
        framing="Scenario simulation or what-if analysis",
        command="bar build sim simulation systemic effects",
    ),
    StarterPack(
        name="charter",
        framing="Planning a project or feature",
        command="bar build plan branch prioritize risks",
    ),
    StarterPack(
        name="explain",
        framing="Explaining a concept or system to an audience",
        command="bar build show analog actors jobs",
    ),
    StarterPack(
        name="versus",
        framing="Structured comparison between alternatives",
        command="bar build diff branch trade polar",
    ),
]

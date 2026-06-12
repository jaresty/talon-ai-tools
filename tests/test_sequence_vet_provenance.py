"""
Tests for vet step positional provenance gate in frame-explore and frame-debug.

Each test asserts a literal string that must be present in the new prompt_hint
and absent from the old prompt_hint. Tests FAIL against the old definition,
PASS after the edit.
"""

import pytest
from lib.sequenceConfig import SEQUENCES


def _get_vet_step(sequence_name: str) -> dict:
    seq = SEQUENCES[sequence_name]
    for step in seq["steps"]:
        if step.get("role") == "evidence evaluation":
            return step
        inner = step.get("inner", {})
        for inner_step in inner.get("steps", []):
            if inner_step.get("role") == "evidence evaluation":
                return inner_step
    raise KeyError(f"No evidence evaluation step in {sequence_name}")


# ---------- frame-explore vet step ----------

class TestFrameExploreVetPositionalGate:
    def setup_method(self):
        self.hint = _get_vet_step("frame-explore")["prompt_hint"]

    def test_last_bash_tool_call_literal(self):
        assert "last Bash tool call before this vet step" in self.hint

    def test_command_text_literal(self):
        assert "command text of that call" in self.hint

    def test_enumerate_every_path(self):
        assert "Enumerate every path" in self.hint

    def test_closed_by_gate_1(self):
        assert "closed by gate (1)" in self.hint

    def test_path_1_label(self):
        assert "(path 1)" in self.hint

    def test_does_not_use_old_causal_framing(self):
        assert "the probe step used to produce it" not in self.hint

    def test_terminal_verdict_met(self):
        assert "Goal condition: met" in self.hint


# ---------- frame-debug vet step ----------

class TestFrameDebugVetPositionalGate:
    def setup_method(self):
        self.hint = _get_vet_step("frame-debug")["prompt_hint"]

    def test_last_bash_tool_call_literal(self):
        assert "last Bash tool call before this vet step" in self.hint

    def test_command_text_literal(self):
        assert "command text of that call" in self.hint

    def test_enumerate_every_path(self):
        assert "Enumerate every path" in self.hint

    def test_closed_by_gate_1(self):
        assert "closed by gate (1)" in self.hint

    def test_path_1_label(self):
        assert "(path 1)" in self.hint

    def test_does_not_use_old_causal_framing(self):
        assert "the probe step used to produce it" not in self.hint

    def test_terminal_verdict_confirmed(self):
        assert "Root cause: confirmed" in self.hint

"""Tests for ADR-0228: impl_intent sentinel — every implementation file write must be preceded by
🔵 Intent logged citing the target test assertion and red evidence.

This ADR replaces write_authorized with impl_intent + impl_intent_achieved which sandwich
implementation file writes and provide stronger guarantees (test assertion evidence).

T1 impl-intent-sentinel: sentinel template and gate exist and propagate to prompt.
"""

import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import SENTINEL_TEMPLATES, _SENTINEL_GATES, build_ground_prompt


class TestThread1_ImplIntentSentinel(GroundADRTestBase):
    """impl_intent sentinel template, gate, and propagation to prompt."""

    def setUp(self):
        self.prompt = build_ground_prompt()
        self.gate = _SENTINEL_GATES.get("impl_intent", "")

    def test_sentinel_template_exists(self):
        self.assertIn("impl_intent", SENTINEL_TEMPLATES)

    def test_sentinel_format_contains_target(self):
        self.assertIn("target:", SENTINEL_TEMPLATES["impl_intent"])

    def test_sentinel_format_contains_evidence(self):
        self.assertIn("evidence:", SENTINEL_TEMPLATES["impl_intent"])

    def test_gate_exists(self):
        self.assertNotEqual(
            self.gate, "", "impl_intent must have a gate in _SENTINEL_GATES"
        )

    def test_gate_requires_file_write(self):
        self.assertIn("file-write", self.gate.lower())

    def test_gate_requires_test_assertion(self):
        self.assertIn("test assertion", self.gate.lower())

    def test_gate_voids_without_evidence(self):
        self.assertIn("voids", self.gate.lower())

    def test_gate_includes_perturb_guidance(self):
        self.assertIn("perturb", self.gate.lower())

    def test_impl_intent_propagated_to_prompt(self):
        self.assertIn("impl_intent", self.prompt.lower())

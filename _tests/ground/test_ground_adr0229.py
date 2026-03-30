"""Tests for ADR-0229: impl_intent_achieved gate requires matching target from impl_intent.

T1 impl-intent-achieved-target-match: gate text requires the target test assertion name
to match the target from impl_intent.
"""

import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import SENTINEL_TEMPLATES, _SENTINEL_GATES, build_ground_prompt


class TestThread1_ImplIntentAchievedTargetMatch(GroundADRTestBase):
    """impl_intent_achieved gate requires target to match impl_intent."""

    def setUp(self):
        self.gate = _SENTINEL_GATES["impl_intent_achieved"]
        self.prompt = build_ground_prompt()

    def test_sentinel_template_exists(self):
        self.assertIn("impl_intent_achieved", SENTINEL_TEMPLATES)

    def test_gate_requires_matching_target(self):
        self.assertIn("match", self.gate.lower())
        self.assertIn("impl_intent", self.gate.lower())

    def test_gate_requires_test_assertion_passing(self):
        self.assertIn("test assertion", self.gate.lower())
        self.assertIn("passing", self.gate.lower())

    def test_gate_voids_without_matching_intent(self):
        self.assertIn("voids", self.gate.lower())

    def test_gate_propagated_to_prompt(self):
        self.assertIn("intent achieved", self.prompt.lower())


if __name__ == "__main__":
    unittest.main()

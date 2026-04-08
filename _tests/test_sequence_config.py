"""Python-layer tests for sequenceConfig.py (gate layer boundary requirement).

These tests assert structural entities owned by the Python layer — SEQUENCES dict,
validate_sequences(), example field, new sequence names — independently of the Go
grammar pipeline. A bug in sequenceConfig.py must fail here before reaching Go.
"""
import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if TYPE_CHECKING:
    from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences


class TestSequenceConfigStructure(unittest.TestCase):

    def setUp(self):
        from talon_user.lib.sequenceConfig import SEQUENCES, validate_sequences
        self.sequences = SEQUENCES
        self.validate = validate_sequences

    # Behavior: SEQUENCES is non-empty
    def test_sequences_non_empty(self):
        self.assertGreater(len(self.sequences), 0, "SEQUENCES must be non-empty")

    # Behavior: each sequence has a non-empty description
    def test_all_sequences_have_description(self):
        for name, seq in self.sequences.items():
            self.assertIsInstance(seq.get("description"), str, f"{name}: description must be a string")
            self.assertTrue(seq["description"], f"{name}: description must be non-empty")

    # Behavior: each sequence has a non-empty example
    def test_all_sequences_have_example(self):
        for name, seq in self.sequences.items():
            self.assertIsInstance(seq.get("example"), str, f"{name}: example must be a string")
            self.assertTrue(seq["example"], f"{name}: example must be non-empty")

    # Behavior: each sequence has a valid mode
    def test_all_sequences_have_valid_mode(self):
        valid_modes = {"autonomous", "linear", "cycle"}
        for name, seq in self.sequences.items():
            self.assertIn(seq.get("mode"), valid_modes, f"{name}: mode must be one of {valid_modes}")

    # Behavior: each sequence has ≥2 steps
    def test_all_sequences_have_at_least_two_steps(self):
        for name, seq in self.sequences.items():
            steps = seq.get("steps", [])
            self.assertGreaterEqual(len(steps), 2, f"{name}: must have ≥2 steps")

    # Behavior: each step has token and role
    def test_all_steps_have_token_and_role(self):
        for name, seq in self.sequences.items():
            for i, step in enumerate(seq.get("steps", [])):
                self.assertIsInstance(step.get("token"), str, f"{name} step {i}: token must be a string")
                self.assertTrue(step["token"], f"{name} step {i}: token must be non-empty")
                self.assertIsInstance(step.get("role"), str, f"{name} step {i}: role must be a string")
                self.assertTrue(step["role"], f"{name} step {i}: role must be non-empty")

    # Behavior: three new sequences exist
    def test_gather_and_synthesize_exists(self):
        self.assertIn("gather-and-synthesize", self.sequences)

    def test_plan_and_retrospect_exists(self):
        self.assertIn("plan-and-retrospect", self.sequences)

    def test_simulate_and_review_exists(self):
        self.assertIn("simulate-and-review", self.sequences)

    # Behavior: validate_sequences returns no errors for current SEQUENCES
    def test_validate_sequences_passes(self):
        errors = self.validate(self.sequences, known_tokens=set())
        self.assertEqual(errors, [], f"validate_sequences reported errors: {errors}")

    # Behavior: linear/cycle sequences have at least one step with requires_user_input
    def test_interactive_sequences_have_pause_step(self):
        for name, seq in self.sequences.items():
            if seq.get("mode") in ("linear", "cycle"):
                has_pause = any(step.get("requires_user_input") for step in seq.get("steps", []))
                self.assertTrue(has_pause, f"{name} (mode={seq['mode']}): must have at least one step with requires_user_input=True")


if __name__ == "__main__":
    unittest.main()

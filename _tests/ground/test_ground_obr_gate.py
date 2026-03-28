"""OBR forward gate: Thread N complete blocked when OBR has only test-suite output."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRLiveProcessForwardGate(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_gate_blocks_thread_complete_if_only_test_runner(self):
        """Thread N complete must be explicitly blocked when OBR has only test-runner output."""
        # Requires a specific forward gate sentence — OR-fallback via P4 once prose is deleted
        has_gate = (
            "if the most recent tool call at this rung is a test runner" in self.prompt
            or "if the most recent OBR tool call is a test runner" in self.prompt
            or (
                "P4 (Rung action discipline)" in self.prompt
                and "live-process invocation" in self.prompt
                and "OBR" in self.prompt
                and "blocked" in self.prompt
            )
        )
        self.assertTrue(
            has_gate,
            "OBR must have an explicit forward gate: if most recent OBR tool call is a test runner, "
            "Thread N complete is blocked",
        )

    def test_obr_forward_gate_names_only_valid_next_action(self):
        """The OBR forward gate must name 'only valid next action' as live-process invocation."""
        # Check that 'only valid next action' appears near the OBR test-runner block
        idx = self.prompt.find("if the most recent tool call at this rung is a test runner")
        if idx == -1:
            idx = self.prompt.find("if the most recent OBR tool call is a test runner")
        self.assertGreater(
            idx, -1,
            "OBR explicit forward gate sentence must be present",
        )
        segment = self.prompt[idx:idx+250]
        self.assertTrue(
            "only valid next action" in segment or "only valid next token" in segment,
            "OBR forward gate must name 'only valid next action' within 250 chars of gate trigger",
        )

    def test_condition5_cannot_be_satisfied_before_live_process(self):
        """Condition (5) test suite requirement must be ordered after live-process invocation."""
        # The gate sentence must appear BEFORE condition (5) in the prompt
        gate_idx = self.prompt.find("if the most recent tool call at this rung is a test runner")
        if gate_idx == -1:
            gate_idx = self.prompt.find("if the most recent OBR tool call is a test runner")
        cond5_idx = self.prompt.find(
            "a full test suite run result exists after the most recent OBR tool call"
        )
        self.assertGreater(gate_idx, -1, "OBR forward gate must be present")
        self.assertGreater(cond5_idx, -1, "Condition (5) test suite requirement must be present")
        self.assertLess(
            gate_idx, cond5_idx,
            "OBR forward gate must appear before condition (5) test suite requirement",
        )


if __name__ == "__main__":
    unittest.main()

"""OBR forward gate: Thread N complete blocked when OBR has only test-suite output."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRLiveProcessForwardGate(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_gate_blocks_thread_complete_if_only_test_runner(self):
        # ADR-0187: "if the most recent tool call at this rung is a test runner" deleted.
        # Guarantee carried by: rung table void condition (test-runner output voids OBR rung) +
        # P4 Clause B (live-process invocation is step 3; test suite is step 5 — wrong type at step 3).
        self.assertNotIn(
            "if the most recent tool call at this rung is a test runner",
            self.prompt,
            "ADR-0187: OBR explicit forward gate phrase must be absent — subsumed by rung table + P4 Clause B",
        )
        self.assertIn(
            "test runner output — a test-suite pass is validation-run-observation-type output",
            self.prompt,
            "OBR rung table void condition must carry the test-runner blocking guarantee",
        )

    def test_obr_forward_gate_names_only_valid_next_action(self):
        # ADR-0187: explicit gate deleted; P4 Clause A carries "no content other than the next step".
        self.assertNotIn(
            "if the most recent OBR tool call is a test runner",
            self.prompt,
            "ADR-0187: OBR forward gate phrase must be absent",
        )
        self.assertIn(
            "no content other than the next step in the sequence may appear between steps",
            self.prompt,
            "P4 Clause A must carry the sequencing constraint between OBR steps",
        )

    def test_condition5_cannot_be_satisfied_before_live_process(self):
        # ADR-0187: explicit "most recent tool call" gate deleted.
        # P4 Clause B ordering: live-process is step (3), test suite is step (5) — ordering enforced.
        live_idx = self.prompt.find("live-process invocation of the implementation artifact")
        suite_idx = self.prompt.find("(5) test suite run")
        self.assertGreater(live_idx, -1, "P4 Clause B live-process invocation must be present")
        self.assertGreater(suite_idx, -1, "P4 Clause B test suite step must be present")
        self.assertLess(
            live_idx, suite_idx,
            "P4 Clause B must order live-process invocation (step 3) before test suite run (step 5)",
        )


if __name__ == "__main__":
    unittest.main()

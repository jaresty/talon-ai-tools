"""ADR-0205: Align three conflicting rule pairs into mutually reinforcing gates.

Thread 1: hard-stop-positive-gate — HARD STOP valid in exactly one case (P5 underspecification)
Thread 2: prose-rung-cycle-scope — prose re-emission scoped to new cycles only, not post-HARD-STOP
Thread 3: obr-devserver-gate — live-process invocation is a blocking gate before step-5 test suite
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestHardStopPositiveGate(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_hard_stop_valid_in_exactly_one_case(self):
        self.assertIn(
            "valid in exactly one case",
            self.prompt,
            "Protocol must state HARD STOP is valid in exactly one case",
        )

    def test_hard_stop_positive_gate_references_p5(self):
        self.assertIn(
            "all other failure classes have defined routes",
            self.prompt,
            "HARD STOP positive gate must state all other failure classes have defined routes",
        )


class TestProseRungCycleScope(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prose_reemission_scoped_to_new_cycle(self):
        self.assertIn(
            "does not require prose re-emission",
            self.prompt,
            "Protocol must state HARD STOP upward return does not require prose re-emission",
        )

    def test_hard_stop_not_new_cycle(self):
        self.assertIn(
            "HARD STOP upward return is not a new cycle",
            self.prompt,
            "Protocol must explicitly state HARD STOP is not a new cycle",
        )


class TestOBRDevServerBlockingGate(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_thread_complete_blocked_until_live_process(self):
        self.assertIn(
            "blocked until a live-process tool call result",
            self.prompt,
            "Protocol must block Thread N complete until a live-process tool call result exists",
        )

    def test_test_runner_does_not_satisfy_live_process_gate(self):
        self.assertIn(
            "test suite run at step 5 presupposes the live-process invocation",
            self.prompt,
            "Protocol must state step-5 test suite presupposes step-3 live-process invocation",
        )


if __name__ == "__main__":
    unittest.main()

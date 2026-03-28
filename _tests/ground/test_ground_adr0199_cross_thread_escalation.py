"""P6 cross-thread convergence blocks progress when same gap class recurs (ADR-0199 Thread 4)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestCrossThreadEscalation(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_p6_cross_thread_convergence_rule_present(self):
        self.assertIn(
            "P6 (Cross-thread convergence)",
            self.prompt,
            "Protocol must define P6 cross-thread convergence principle",
        )

    def test_p6_blocks_subsequent_threads_on_same_gap_class(self):
        self.assertIn(
            "subsequent threads may not proceed past",
            self.prompt,
            "P6 must block subsequent threads from proceeding past VRO for a recurring gap class",
        )

    def test_p6_routing_around_does_not_satisfy(self):
        self.assertIn(
            "routing around a recurring gap by changing the test does not satisfy",
            self.prompt,
            "P6 must explicitly state that test workarounds do not satisfy the root-cause gate",
        )


if __name__ == "__main__":
    unittest.main()

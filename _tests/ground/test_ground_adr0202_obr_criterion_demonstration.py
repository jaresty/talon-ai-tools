"""OBR exec_observed must demonstrate the specific criterion behavior, not just server liveness (ADR-0202)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestOBRCriterionDemonstration(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_obr_requires_criterion_specific_demonstration(self):
        self.assertIn(
            "specific behavior asserted in the criterion",
            self.prompt,
            "Protocol must require OBR output to demonstrate the specific behavior in the criterion",
        )

    def test_server_liveness_does_not_satisfy(self):
        self.assertIn(
            "server liveness",
            self.prompt,
            "Protocol must name server liveness as an example that does not satisfy the OBR gate",
        )


if __name__ == "__main__":
    unittest.main()

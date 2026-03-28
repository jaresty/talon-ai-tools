"""Test for L27: OBR rung pre-invocation gate — test runner does not satisfy live-process gate.

The escape route: at the OBR rung the model invokes a test runner instead of
the implementation artifact as a live process. The voids_if names test runner
output as voiding, but there is no gate before the invocation that names a
test runner as an invalid invocation target.

L27 closes this: a test runner invocation does not satisfy the OBR live-process
gate; the invocation target must be the implementation artifact itself.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL27OBRTestRunnerGate(unittest.TestCase):
    """L27: test runner invocation does not satisfy OBR live-process gate."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l27_test_runner_does_not_satisfy_gate(self):
        """OBR section must state test runner invocation does not satisfy the gate."""
        self.assertIn(
            "test runner invocation does not satisfy this gate",
            self.core,
            "L27: must explicitly state test runner does not satisfy OBR live-process gate",
        )

    def test_l27_invocation_target_must_be_implementation(self):
        """Gate must name the implementation artifact as the required invocation target."""
        idx = self.core.find("test runner invocation does not satisfy this gate")
        self.assertGreater(idx, -1, "L27 gate sentence must be present")
        segment = self.core[idx:idx+300]
        self.assertIn(
            "implementation artifact",
            segment,
            "L27: gate must state the invocation target must be the implementation artifact",
        )

    def test_l27_positioned_in_obr_section(self):
        """L27 gate must appear in the OBR section."""
        obr_start = self.core.find("Upon writing the observed running behavior label")
        obr_end = self.core.find("Thread N complete may not be emitted unless")
        gate_idx = self.core.find("test runner invocation does not satisfy this gate")
        self.assertGreater(gate_idx, -1, "L27 gate sentence must be present")
        self.assertGreater(gate_idx, obr_start, "L27 gate must be after OBR section start")
        self.assertLess(gate_idx, obr_end + 200, "L27 gate must be near OBR section")


if __name__ == "__main__":
    unittest.main()

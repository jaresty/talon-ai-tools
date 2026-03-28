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
        # ADR-0187: "test runner invocation does not satisfy this gate" deleted from OBR prose block.
        # Guarantee carried by OBR rung table void condition + P4 Clause B naming live-process invocation.
        self.assertNotIn(
            "test runner invocation does not satisfy this gate",
            self.core,
            "ADR-0187: L27 gate phrase must be absent — subsumed by rung table void condition and P4 Clause B",
        )
        self.assertIn(
            "test runner output — a test-suite pass is validation-run-observation-type output",
            self.core,
            "OBR rung table void condition must name test-runner output as voiding the rung",
        )

    def test_l27_invocation_target_must_be_implementation(self):
        # ADR-0187: explicit gate sentence deleted; P4 Clause B names "live-process invocation of the implementation artifact".
        self.assertIn(
            "live-process invocation of the implementation artifact",
            self.core,
            "P4 Clause B must name the implementation artifact as the required invocation target",
        )

    def test_l27_positioned_in_obr_section(self):
        # ADR-0187: "Upon writing the observed running behavior label" and "Thread N complete may not be emitted unless"
        # both deleted; L27 guarantee is now global via P4 Clause B.
        self.assertIn(
            "live-process invocation of the implementation artifact",
            self.core,
            "P4 Clause B must carry the L27 invocation-target constraint globally",
        )


if __name__ == "__main__":
    unittest.main()

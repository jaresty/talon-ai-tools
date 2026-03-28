"""Test for L21: stopping mid-ladder at any rung other than VRO-after-Gap is a violation.

The escape route: after writing a criteria artifact, the model stops and waits
for user confirmation before continuing to formal notation. The 'advance
continuously' rule exists but is not stated as a hard gate on any specific rung.

L21 closes this by making explicit: after the criteria artifact is written,
formal notation must follow in the same response; stopping between any two
rungs other than VRO-after-Gap is a protocol violation.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestL21NoMidLadderStop(unittest.TestCase):
    """L21: stopping mid-ladder at any rung other than VRO-after-Gap is a violation."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_l21_stopping_between_rungs_is_violation(self):
        """Stopping between any two rungs other than VRO-after-Gap is a protocol violation."""
        self.assertIn(
            "stopping between rungs",
            self.core,
            "L21: must explicitly name stopping between rungs as a protocol violation",
        )

    def test_l21_only_stop_is_vro_after_gap(self):
        """The only permitted stop is at VRO after emitting Gap — this must be stated as exclusive."""
        idx = self.core.find("stopping between rungs")
        self.assertGreater(idx, -1, "L21 gate sentence must be present")
        segment = self.core[idx:idx+400]
        self.assertIn(
            "protocol violation",
            segment,
            "L21: stopping between rungs must be named a protocol violation",
        )

    def test_l21_no_user_confirmation_between_rungs(self):
        """The model must not pause for user confirmation between rungs."""
        self.assertIn(
            "waiting for user confirmation between rungs",
            self.core,
            "L21: must explicitly prohibit waiting for user confirmation between rungs",
        )


if __name__ == "__main__":
    unittest.main()

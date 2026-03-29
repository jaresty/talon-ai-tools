"""VRO section compactness guard needs updating for ADR-0199 test-interaction harness class."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestVROSectionCompactBaseline(unittest.TestCase):
    def test_vro_section_below_adr0199_guard(self):
        # ADR-0215: compact routing table reduces VRO section below ADR-0199 guard of 1120
        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find("Before writing the validation run observation rung label")
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        ADR0199_GUARD = 1120
        self.assertLess(
            len(vro_section),
            ADR0199_GUARD,
            "ADR-0215: compact routing table must reduce VRO section below ADR-0199 guard of 1120",
        )


if __name__ == "__main__":
    unittest.main()

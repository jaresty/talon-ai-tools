"""VRO section compactness guard needs updating for ADR-0199 test-interaction harness class."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestVROSectionCompactBaseline(unittest.TestCase):
    def test_vro_section_exceeds_old_guard(self):
        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find("Before writing the validation run observation rung label")
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        OLD_GUARD = 1120
        self.assertGreater(
            len(vro_section),
            OLD_GUARD,
            "ADR-0199 test-interaction harness rule must push VRO section past old guard",
        )


if __name__ == "__main__":
    unittest.main()

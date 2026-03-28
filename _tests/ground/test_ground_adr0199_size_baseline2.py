"""Size guard: P6 addition pushes core past 27500 baseline (ADR-0199 Thread 4 support)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestADR0199SizeBaseline2(unittest.TestCase):
    def test_size_baseline_update_needed_after_p6(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        OLD_BASELINE = 27500
        self.assertGreater(
            current,
            OLD_BASELINE,
            "P6 addition must push core past the 27500 baseline confirming update is needed",
        )


if __name__ == "__main__":
    unittest.main()

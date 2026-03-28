"""Size baseline test: ADR-0199 additions exceed old 27000-char guard (ADR-0199 Thread 3 support)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestADR0199SizeBaseline(unittest.TestCase):
    def test_size_baseline_update_needed(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        OLD_BASELINE = 27000
        self.assertGreater(
            current,
            OLD_BASELINE,
            "ADR-0199 additions must exceed the old baseline — this test confirms update is needed",
        )


if __name__ == "__main__":
    unittest.main()

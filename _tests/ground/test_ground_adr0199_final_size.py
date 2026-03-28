"""Final size guard after all ADR-0199 additions (Thread 7 support)."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestADR0199FinalSize(unittest.TestCase):
    def test_final_size_exceeds_28700_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        self.assertGreater(
            current,
            28700,
            "ADR-0199 final additions must exceed the 28700 baseline",
        )


if __name__ == "__main__":
    unittest.main()

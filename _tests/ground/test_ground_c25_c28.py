"""Tests for C25–C28 ground protocol escape-route closures.

ADR-0184 condensation notes:
- C25 (no-edit Thread N complete): subsumed by gate list item (4) — "directly demonstrates criterion"
  means no implementation change → criterion not demonstrated → Thread N complete blocked.
- C26 (blank OBS): subsumed by gate list item (3) "non-empty verbatim output".
- C27 (mock endpoint): subsumed by "directly demonstrate the specific behavior named in the criterion".
- C28 (test dismissal): gate list already requires "every failing test must be explicitly acknowledged
  in the transcript with a written reason".
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestC28TestFailureDismissal(unittest.TestCase):
    """C28: failing tests must be acknowledged — now via gate list item (5)."""
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_c28_failing_test_acknowledged_in_gate_list(self):
        self.assertIn(
            "every failing test must be explicitly acknowledged in the transcript with a written reason",
            self.core,
            "C28: gate list must require every failing test to be acknowledged in the transcript")


if __name__ == "__main__":
    unittest.main()

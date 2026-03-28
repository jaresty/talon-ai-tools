"""ADR-0185 Phase 3: deleted principle-derivative fragments absent.

Size target (16 KB) is deferred — reaching it requires migrating ~40 more
L-series literal-phrase pins to behavioral-effect form. See ADR-0185.
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt


class TestDeletedFragmentsAbsent(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_faithful_derivation_restatement_deleted(self):
        self.assertNotIn(
            "faithful derivation requires form to change, intent to stay fixed",
            self.prompt,
            "Faithful-derivation restatement must be deleted (R2 clause subsumes it)",
        )

    def test_stopping_between_rungs_explicit_violation_deleted(self):
        self.assertNotIn(
            "stopping between rungs at any other point is a protocol violation",
            self.prompt,
            "Explicit stopping-between-rungs violation must be deleted (continuous-transition rule subsumes it)",
        )

    def test_waiting_for_confirmation_explicit_violation_deleted(self):
        self.assertNotIn(
            "waiting for user confirmation between rungs is a protocol violation",
            self.prompt,
            "Explicit waiting-for-confirmation violation must be deleted (without-pausing clause subsumes it)",
        )


if __name__ == "__main__":
    unittest.main()

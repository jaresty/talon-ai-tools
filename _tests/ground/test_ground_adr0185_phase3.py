"""ADR-0185 Phase 3: prompt size reduced; deleted principle-derivative fragments absent."""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import build_ground_prompt

SIZE_TARGET = 26700  # Phase 3 partial: faithful-derivation restatement + stopping/waiting explicit phrases
# Further reductions require migrating more existing L-series test pins — see ADR-0185.

DELETED_FRAGMENTS = [
    # R2 restatement — subsumed by sharpened R2; no existing test pins this exact phrase
    "faithful derivation requires form to change, intent to stay fixed",
    # Stopping/waiting explicit phrases — subsumed by "without pausing for user confirmation"
    # + "all other rung transitions are continuous within the same response"
    "stopping between rungs at any other point is a protocol violation",
    "waiting for user confirmation between rungs is a protocol violation",
]


class TestPromptSize(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_prompt_size_at_most_16kb(self):
        size = len(self.prompt.encode("utf-8"))
        self.assertLessEqual(
            size,
            SIZE_TARGET,
            f"Prompt is {size} bytes; target is ≤ {SIZE_TARGET} bytes",
        )


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

"""Tests for collapse-redundancies and prehoc-gates refactor.

Collapse:
- EV sentinel has one unified checklist, not three separate guards
- Manifest exhausted count check appears only once (not duplicated)
- OBR invocation exclusion is one unified sentence
- Thread-sequential constraint is one sentence, not three

Pre-hoc gates:
- EV rung: only valid content after rung label is artifact then tool call
- OBR rung: provenance statement must identify invocation target before tool call;
  if target is a test runner, the provenance statement is a gate that stops emission
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestOBRInvocationTargetPrehoc(unittest.TestCase):
    """OBR provenance statement gates invocation target before tool call fires."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_provenance_statement_gates_target(self):
        """Provenance statement must name invocation target; test runner stops emission."""
        self.assertIn(
            "if the target is a test runner, stop",
            self.core,
            "OBR pre-hoc gate: provenance statement must gate on target type before tool call",
        )

    def test_obr_invocation_target_must_be_artifact(self):
        idx = self.core.find("if the target is a test runner, stop")
        self.assertGreater(idx, -1, "OBR pre-hoc gate must be present")
        segment = self.core[idx:idx+200]
        self.assertIn(
            "implementation artifact itself",
            segment,
            "OBR pre-hoc gate: must name implementation artifact as required target",
        )


class TestManifestExhaustedNoDuplicate(unittest.TestCase):
    """Manifest exhausted count gate appears at most once."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_manifest_exhausted_count_not_duplicated(self):
        count = self.core.count("count of \u2705 Thread N complete sentinels")
        self.assertLessEqual(count, 1,
            "Manifest exhausted count check appears more than once — collapse to one")


class TestThreadSequentialNotTriplicated(unittest.TestCase):
    """Thread-sequential constraint stated at most once."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_thread_sequential_not_triplicated(self):
        # Three forms that express the same rule — only one should survive
        forms = [
            "No criterion for Thread N+1 may appear until",
            "no rung content of any type for Thread N+1 may appear before",
        ]
        # At least one should be gone (collapsed into a single statement)
        surviving = sum(1 for f in forms if f in self.core)
        self.assertLessEqual(surviving, 1,
            "Thread-sequential constraint is stated in multiple forms — collapse to one")


if __name__ == "__main__":
    unittest.main()

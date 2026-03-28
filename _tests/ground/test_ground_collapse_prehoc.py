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
        # ADR-0187: "if the target is a test runner, stop" deleted — derivable from P4 Clause B: step (3)
        # is live-process invocation; a test runner is the wrong type (P4 closed action set).
        self.assertNotIn(
            "if the target is a test runner, stop",
            self.core,
            "ADR-0187: this phrase must be absent — derivable from P4 OBR sequence type constraints",
        )
        # Guarantee carried by P4: live-process invocation as step (3) — test runner is wrong type.
        self.assertIn(
            "live-process invocation of the implementation artifact",
            self.core,
            "P4 Clause B must name live-process invocation of the implementation artifact as step (3)",
        )

    def test_obr_invocation_target_must_be_artifact(self):
        # ADR-0187: "if the target is a test runner, stop" phrase deleted.
        # P4 Clause B explicitly names "live-process invocation of the implementation artifact" as step (3).
        self.assertIn(
            "live-process invocation of the implementation artifact",
            self.core,
            "P4 Clause B must name implementation artifact as the required invocation target",
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

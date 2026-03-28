"""Meta-test for ADR-0185 Phase 2: validates that the migration test file
(test_ground_adr0185_phase2.py) exists and does not contain assertIn calls
pinning the deletion-target prose fragments."""
import unittest
import os
import ast

MIGRATION_FILE = "_tests/ground/test_ground_adr0185_phase2.py"

# Prose fragments scheduled for deletion in Thread 3 (principle-derivative blocks).
# These must not appear as assertIn literals in the migration file.
DELETION_TARGETS = [
    "all seven rungs must complete for Thread N before any rung content for Thread N+1 may appear",
    "stopping between rungs",
    "waiting for user confirmation between rungs",
    "observation cannot be produced is a prose-description failure",
    "no additional invariants",
    "nothing beyond it",
    "one criterion per thread per cycle",
    "one edit means exactly one tool call that creates or modifies a file",
    "one edit per re-run",
    "VRO rung label must appear in the transcript",
    "from the current cycle",
    "prior cycle does not satisfy this gate",
    "any cycle following an upward return",
    "prose rung must be re-emitted at the start of every cycle",
    "the criterion must be immediately derivable from the re-emitted prose",
]


class TestMigrationFileExists(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(
            os.path.exists(MIGRATION_FILE),
            f"Migration file {MIGRATION_FILE} must exist",
        )


class TestMigrationFileNoProsePins(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(MIGRATION_FILE):
            self.skipTest(f"{MIGRATION_FILE} does not exist yet")
        with open(MIGRATION_FILE) as f:
            self.tree = ast.parse(f.read())

    def _get_assertin_literals(self):
        literals = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call):
                fn = getattr(node.func, "attr", "")
                if fn == "assertIn" and node.args:
                    a = node.args[0]
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        literals.append(a.value)
        return literals

    def test_no_deletion_target_literal_pins(self):
        literals = self._get_assertin_literals()
        violations = [
            (target, lit)
            for target in DELETION_TARGETS
            for lit in literals
            if target[:40] in lit
        ]
        self.assertEqual(
            violations,
            [],
            f"Migration file pins deletion-target fragments: {violations}",
        )


if __name__ == "__main__":
    unittest.main()

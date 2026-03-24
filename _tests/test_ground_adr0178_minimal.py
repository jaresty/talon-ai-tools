"""ADR-0178 Phase 2: D1–D7 applied to GROUND_PARTS_MINIMAL["core"] + structural cleanup."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt


def _minimal():
    return build_ground_prompt()


class TestD1ElisionMinimal(unittest.TestCase):
    def test_elision_prohibition_in_minimal(self):
        self.assertIn(
            "elision",
            _minimal(),
            "D1: minimal must prohibit elision markers inside the triple-backtick block",
        )


class TestD2NextActionGateMinimal(unittest.TestCase):
    def test_next_action_gate_in_minimal(self):
        self.assertIn(
            "only valid next action",
            _minimal(),
            "D2: minimal must state the only valid next action after the sentinel is the tool call",
        )


class TestD3FalsifyingConditionMinimal(unittest.TestCase):
    def test_falsifying_condition_in_minimal(self):
        self.assertIn(
            "falsifying condition",
            _minimal(),
            "D3: minimal must require explicit falsifying condition on each criterion",
        )


class TestD4OpenConstraintMinimal(unittest.TestCase):
    def test_open_constraint_in_minimal(self):
        self.assertIn(
            "open constraint",
            _minimal(),
            "D4: minimal must require open-constraint declaration for partial downward-sufficiency",
        )


class TestD5ThreadMarkersMinimal(unittest.TestCase):
    def test_thread_marker_in_minimal(self):
        self.assertIn(
            "thread marker",
            _minimal(),
            "D5: minimal must require inline [T: gap-name] thread markers on behavioral predicate sentences",
        )


class TestD6VerbatimTestNameMinimal(unittest.TestCase):
    def test_verbatim_test_name_in_minimal(self):
        self.assertIn(
            "verbatim test name",
            _minimal(),
            "D6: minimal must require verbatim test-name quotation in carry-forward",
        )


class TestD7ProvenanceMinimal(unittest.TestCase):
    def test_provenance_statement_in_minimal(self):
        self.assertIn(
            "provenance statement",
            _minimal(),
            "D7: minimal must require provenance citation before filesystem tool calls at OBR",
        )


class TestStructuralCleanup(unittest.TestCase):
    def test_build_ground_prompt_no_minimal_param(self):
        """build_ground_prompt() with no args returns the minimal version."""
        import inspect
        from lib.groundPrompt import build_ground_prompt
        sig = inspect.signature(build_ground_prompt)
        self.assertNotIn(
            "minimal",
            sig.parameters,
            "build_ground_prompt() must not have a minimal parameter after GROUND_PARTS removal",
        )

    def test_ground_parts_removed(self):
        """GROUND_PARTS dict must not exist after migration."""
        import lib.groundPrompt as gp
        self.assertFalse(
            hasattr(gp, "GROUND_PARTS"),
            "GROUND_PARTS must be removed from groundPrompt module after migration",
        )

    def test_section_labels_removed(self):
        """_SECTION_LABELS must not exist after migration."""
        import lib.groundPrompt as gp
        self.assertFalse(
            hasattr(gp, "_SECTION_LABELS"),
            "_SECTION_LABELS must be removed from groundPrompt module after migration",
        )


if __name__ == "__main__":
    unittest.main()

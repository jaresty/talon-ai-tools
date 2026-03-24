"""ADR-0178: Ground prompt drift closure — 7 behavioral-marker tests."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt


class TestADR0178D1ElisionProhibition(unittest.TestCase):
    def test_elision_marker_prohibition_present(self):
        self.assertIn(
            "elision",
            build_ground_prompt(),
            "D1: sentinel_rules must prohibit elision markers inside the triple-backtick block",
        )


class TestADR0178D2NextActionGate(unittest.TestCase):
    def test_next_action_gate_present(self):
        self.assertIn(
            "only valid next action",
            build_ground_prompt(),
            "D2: sentinel_rules must state the only valid next action after 🔴 Execution observed is the tool call",
        )

    def test_immediately_before_retired(self):
        self.assertNotIn(
            "immediately before",
            build_ground_prompt(),
            "D2: 'immediately before' proximity language must be replaced with next-action gate rule",
        )


class TestADR0178D3FalsifyingCondition(unittest.TestCase):
    def test_falsifying_condition_present(self):
        self.assertIn(
            "falsifying condition",
            build_ground_prompt(),
            "D3: criteria rung must require an explicit falsifying condition for each criterion",
        )


class TestADR0178D4OpenConstraint(unittest.TestCase):
    def test_open_constraint_declaration_present(self):
        self.assertIn(
            "open constraint",
            build_ground_prompt(),
            "D4: epistemological_protocol must require stating open constraints when downward-sufficiency is incomplete",
        )


class TestADR0178D5ThreadMarkers(unittest.TestCase):
    def test_thread_marker_format_present(self):
        self.assertIn(
            "thread marker",
            build_ground_prompt(),
            "D5: prose rung must require inline thread markers [T: gap-name] on behavioral predicate sentences",
        )


class TestADR0178D6VerbatimTestName(unittest.TestCase):
    def test_verbatim_test_name_required(self):
        self.assertIn(
            "verbatim test name",
            build_ground_prompt(),
            "D6: carry-forward format must require verbatim test-name quotation from prior 🔴 Execution observed output",
        )


class TestADR0178D7ProvenanceCitation(unittest.TestCase):
    def test_provenance_statement_required(self):
        self.assertIn(
            "provenance statement",
            build_ground_prompt(),
            "D7: OBR rung must require provenance citation before filesystem tool calls",
        )


if __name__ == "__main__":
    unittest.main()

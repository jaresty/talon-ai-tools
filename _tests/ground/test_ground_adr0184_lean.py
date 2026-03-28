"""Tests for ADR-0184: lean rewrite — collapse A1/P1, remove A2, trim rung-entry gate, collapse P2.

After the rewrite:
- A1 and P1 are merged into one canonical statement
- A2 is removed (its example is in OBR voids_if)
- Rung-entry gate keeps only item (d) — exec_observed type check
- P2 is removed — rung table gate column + rung-entry gate (d) cover it
"""
import unittest
import sys
sys.path.insert(0, '.')
from lib.groundPrompt import GROUND_PARTS_MINIMAL


class TestA1P1Collapsed(unittest.TestCase):
    """A1 and P1 merged into one canonical statement."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_a1_restatement_removed(self):
        """A1 as a separate axiom header should not exist — merged into P1."""
        self.assertNotIn(
            "A1: only tool-executed events have evidential standing",
            self.core,
            "A1 restatement must be removed — merged into single canonical statement",
        )

    def test_canonical_evidential_rule_present(self):
        """Single canonical evidential rule must be present."""
        self.assertIn(
            "if and only if a tool-executed event",
            self.core,
            "Canonical evidential rule (P1 form) must remain after A1 removal",
        )

    def test_inference_prediction_exclusion_present(self):
        """Inference/prediction exclusion must survive the collapse."""
        self.assertIn(
            "inference, prediction",
            self.core,
            "Inference/prediction exclusion must remain in the canonical rule",
        )


class TestA2Removed(unittest.TestCase):
    """A2 cross-type corollary removed — covered by OBR voids_if."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_a2_header_removed(self):
        """A2 as a separate axiom header should not exist."""
        self.assertNotIn(
            "A2: each rung defines an artifact type; a tool-executed event satisfies",
            self.core,
            "A2 must be removed — it is a corollary of P1 and the rung table",
        )

    def test_cross_type_example_survives_in_obr(self):
        """ADR-0188 Fix 1: OBR void condition scoped — test runner used as live-process evidence voids;
        step-5 test runner output does not void. Cross-type distinction is preserved in scoped form."""
        self.assertIn(
            "test runner output used as OBR live-process evidence voids this rung",
            self.core,
            "Cross-type example must survive in OBR voids_if (scoped form per ADR-0188 Fix 1)",
        )


class TestRungEntryGateTrimmed(unittest.TestCase):
    """Rung-entry gate trimmed to exec_observed type check only."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_rung_entry_gate_items_abc_removed(self):
        """Items (a)-(c) of rung-entry gate restate P1/P2 — removed."""
        self.assertNotIn(
            "state (a) the rung name, (b) the current gap",
            self.core,
            "Rung-entry gate items (a)-(c) must be removed — they restate P1/P2/rung table",
        )

    def test_exec_observed_type_check_survives(self):
        """ADR-0187: rung-entry gate deleted entirely (P1 procedural restatement). Item (d) phrase absent; P1 carries the guarantee."""
        # ADR-0187: entire rung-entry gate block deleted. "no valid exec_observed exists in the current cycle" is absent.
        # The behavioral guarantee (exec_observed type check gates rung content) is carried by P1 evidential boundary.
        self.assertNotIn(
            "no valid exec_observed exists in the current cycle",
            self.core,
            "ADR-0187: rung-entry gate item (d) must be absent — entire gate block deleted as P1 restatement",
        )
        self.assertIn(
            "P1 (Evidential boundary)",
            self.core,
            "P1 must be present to carry the rung-entry gate guarantee",
        )


class TestP2Collapsed(unittest.TestCase):
    """P2 forward-only discipline removed — rung table gate column covers it."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_p2_header_removed(self):
        """P2 as a named principle should not exist."""
        self.assertNotIn(
            "P2 (Forward-only discipline)",
            self.core,
            "P2 must be removed — rung table gate column and rung-entry gate (d) cover it",
        )

    def test_rung_label_precondition_rule_survives(self):
        """The operative rule — no label before gate conditions — must survive somewhere."""
        # This is covered by the rung table gate column and P2's core rule
        # After removal, P3 or the rung table must still make this operative
        has_rule = (
            "no content at a rung is valid before the label" in self.core
            or "precondition list for each rung is the rung table" in self.core
            or "gate column" in self.core
        )
        self.assertTrue(
            has_rule,
            "Forward-only rule must survive in some form after P2 removal",
        )


if __name__ == "__main__":
    unittest.main()

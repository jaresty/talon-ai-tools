"""Tests for ADR-0196: Why-framing additions to ground prompt.

Asserts that each of the five why-sentences is present in the prompt
at its specified location.
"""

import unittest

from lib.groundPrompt import build_ground_prompt


class TestADR0196ProtocolPurpose(unittest.TestCase):
    """Addition 1: protocol-level purpose sentence before all existing text."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_protocol_purpose_present(self):
        self.assertIn(
            "This protocol exists because a model\u2019s description of completed work "
            "is indistinguishable from actually completing it",
            self.prompt,
        )

    def test_protocol_purpose_precedes_gate_mechanism(self):
        purpose_pos = self.prompt.find(
            "This protocol exists because a model\u2019s description of completed work"
        )
        gate_pos = self.prompt.find(
            "Every rung gate exists to prevent one class of error"
        )
        self.assertGreater(purpose_pos, -1, "Protocol purpose sentence absent")
        self.assertGreater(gate_pos, -1, "Gate mechanism sentence absent")
        self.assertLess(
            purpose_pos,
            gate_pos,
            "Protocol purpose sentence must precede gate mechanism sentence",
        )


class TestADR0196DescentStructure(unittest.TestCase):
    """Addition 3: descent structure purpose sentence before seven-rung list."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_descent_structure_purpose_present(self):
        self.assertIn(
            "Each rung forces a kind of specificity the prior rung cannot enforce",
            self.prompt,
        )

    def test_descent_structure_precedes_rung_names(self):
        descent_pos = self.prompt.find(
            "Each rung forces a kind of specificity the prior rung cannot enforce"
        )
        rung_names_pos = self.prompt.find("Seven rungs in order:")
        self.assertGreater(descent_pos, -1, "Descent structure sentence absent")
        self.assertGreater(rung_names_pos, -1, "Seven rungs sentence absent")
        self.assertLess(
            descent_pos,
            rung_names_pos,
            "Descent structure sentence must precede seven-rung list",
        )


class TestADR0196ProgressiveRefinement(unittest.TestCase):
    """Addition 4: progressive refinement purpose sentence near R2."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_progressive_refinement_purpose_present(self):
        self.assertIn(
            "Each artifact must be derived from the prior rung\u2019s actual content",
            self.prompt,
        )

    def test_progressive_refinement_near_r2(self):
        r2_pos = self.prompt.find("R2 (Minimal derivation)")
        pr_pos = self.prompt.find(
            "Each artifact must be derived from the prior rung\u2019s actual content"
        )
        self.assertGreater(r2_pos, -1, "R2 sentence absent")
        self.assertGreater(pr_pos, -1, "Progressive refinement sentence absent")
        # must appear within 2000 chars of R2
        self.assertLess(
            abs(pr_pos - r2_pos),
            2000,
            "Progressive refinement sentence must be near R2",
        )


class TestADR0196LocalWhySentences(unittest.TestCase):
    """Addition 5: three local why-sentences."""

    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_criteria_batch_collect_why_absent(self):
        # ADR-0215: batch-collect paragraph removed (thread sequencing already in axiom block)
        self.assertNotIn(
            "each thread\u2019s criterion is only valid in the context of that thread\u2019s descent",
            self.prompt,
        )

    def test_criteria_batch_collect_rule_absent(self):
        # ADR-0215: batch-collect rule removed (derivable from axiom block thread sequencing)
        self.assertNotIn(
            "batch-collecting criteria for multiple threads under one criteria label",
            self.prompt,
        )

    def test_r2_audit_sentinel_why_present(self):
        self.assertIn(
            "emitting it before the audit section inverts causality",
            self.prompt,
        )

    def test_r2_audit_sentinel_why_near_audit_sentinel(self):
        why_pos = self.prompt.find("emitting it before the audit section inverts causality")
        sentinel_pos = self.prompt.find(
            "the sentinel closes the audit section; it does not constitute it"
        )
        self.assertGreater(why_pos, -1, "R2 audit sentinel why-sentence absent")
        self.assertGreater(sentinel_pos, -1, "Audit sentinel rule absent")
        self.assertLess(
            abs(why_pos - sentinel_pos),
            500,
            "R2 audit sentinel why-sentence must be near audit sentinel rule",
        )

    def test_gap_before_criterion_why_present(self):
        self.assertIn(
            "the Gap names the currently-false assertion that the criterion will make true",
            self.prompt,
        )

    def test_gap_before_criterion_why_near_gap_rule(self):
        why_pos = self.prompt.find(
            "the Gap names the currently-false assertion that the criterion will make true"
        )
        gap_rule_pos = self.prompt.find(
            "writing the criterion before \U0001f534 Gap: is a protocol violation"
        )
        self.assertGreater(why_pos, -1, "Gap-before-criterion why-sentence absent")
        self.assertGreater(gap_rule_pos, -1, "Gap-before-criterion rule absent")
        self.assertLess(
            abs(why_pos - gap_rule_pos),
            500,
            "Gap-before-criterion why-sentence must be near gap rule",
        )


if __name__ == "__main__":
    unittest.main()

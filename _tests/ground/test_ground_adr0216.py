"""Tests for ADR-0216: Ground prompt derivable restatements pass.

Three removals from GROUND_PARTS_MINIMAL["core"]:
1. Formal notation natural-language restatement (post-audit, ~170 chars)
2. VRO shortcut conclusion restatement (~90 chars)
3. HARD STOP routing table restatements: two harness routes + position gate clause (~200 chars)
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0216FormalNotationRestatementAbsent(unittest.TestCase):
    """Thread 1: post-audit natural-language restatement removed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_post_audit_nl_restatement_absent(self):
        self.assertNotIn(
            "Natural language may appear as section labels but may not substitute for encoding a constraint in notation",
            self.core,
            "ADR-0216: post-audit natural-language restatement must be absent",
        )

    def test_original_nl_prohibition_still_present(self):
        self.assertIn(
            "may not substitute for notation",
            self.core,
            "ADR-0216: original natural-language prohibition (lines 315-317) must remain",
        )


class TestADR0216VROShortcutConclusionAbsent(unittest.TestCase):
    """Thread 2: VRO shortcut conclusion restatement removed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_shortcut_conclusion_absent(self):
        self.assertNotIn(
            "skipping EV and VRO for a new criterion introduced by HARD STOP is a protocol violation",
            self.core,
            "ADR-0216: VRO shortcut conclusion restatement must be absent",
        )

    def test_shortcut_conditional_still_present(self):
        self.assertIn(
            "EV and VRO must fire before impl_gate",
            self.core,
            "ADR-0216: VRO shortcut conditional (non-derivable) must remain",
        )


class TestADR0216HardStopRoutingRestatementAbsent(unittest.TestCase):
    """Thread 3: HARD STOP routing table restatements removed."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_hard_stop_missing_impl_route_absent(self):
        # This route is covered by the compact routing table (ADR-0215)
        idx = self.core.find("all other failure classes have defined routes")
        self.assertGreater(idx, -1, "HARD STOP failure-class block must be present")
        segment = self.core[idx:idx+300]
        self.assertNotIn(
            "missing implementation file routes to EI directly",
            segment,
            "ADR-0216: missing-impl route must be absent from HARD STOP block (covered by routing table)",
        )

    def test_hard_stop_test_interaction_route_absent(self):
        idx = self.core.find("all other failure classes have defined routes")
        segment = self.core[idx:idx+300]
        self.assertNotIn(
            "test-interaction failure routes to EV repair",
            segment,
            "ADR-0216: test-interaction route must be absent from HARD STOP block (covered by routing table)",
        )

    def test_hard_stop_non_derivable_routes_present(self):
        self.assertIn(
            "implementation gap that changes between cycles loops within EI",
            self.core,
            "ADR-0216: non-derivable EI loop route must remain",
        )
        self.assertIn(
            "spec gap returns to formal notation",
            self.core,
            "ADR-0216: non-derivable spec-gap route must remain",
        )

    def test_position_gate_redundant_clause_absent(self):
        self.assertNotIn(
            "the only valid next action when EV shows a harness error is a tool call that fixes the harness",
            self.core,
            "ADR-0216: redundant 'only valid next action' clause must be absent from position gate",
        )

    def test_position_gate_base_prohibition_present(self):
        self.assertIn(
            "harness error at EV requires fixing the harness, not an upward return",
            self.core,
            "ADR-0216: base harness-fix prohibition must remain in position gate",
        )


class TestADR0216CharCountReduced(unittest.TestCase):
    """Thread 4: char-count — changes reduce core string length."""

    def test_char_count_below_adr0215_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        ADR0215_BASELINE = 30447  # measured after ADR-0215
        self.assertLess(
            current,
            ADR0215_BASELINE,
            f"ADR-0216: core string ({current} chars) must be shorter than ADR-0215 baseline ({ADR0215_BASELINE})",
        )


if __name__ == "__main__":
    unittest.main()

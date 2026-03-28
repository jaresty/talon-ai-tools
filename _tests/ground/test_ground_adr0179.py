"""ADR-0179: Ground prompt collapse + drift-fix closure — 11 behavioral-marker tests."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt


class TestC1InferenceRestatementRemoved(unittest.TestCase):
    def test_vro_prediction_restatement_absent(self):
        self.assertNotIn(
            "predicting what the run would show does not satisfy this gate regardless of accuracy",
            build_ground_prompt(),
            "C1: VRO per-rung inference restatement must be removed; opening axiom covers it",
        )


class TestC1VROInferenceRestatementRemoved(unittest.TestCase):
    """C1 collapse: only VRO prediction restatement was legitimately redundant."""
    def test_vro_prediction_restatement_absent(self):
        self.assertNotIn(
            "predicting what the run would show does not satisfy this gate regardless of accuracy",
            build_ground_prompt(),
            "C1: VRO per-rung inference restatement must be removed; opening axiom covers it",
        )


class TestE1CarryForwardReadGate(unittest.TestCase):
    def test_carry_forward_read_gate_present(self):
        # ADR-0188: explicit "read the current test file" rule deleted — derivable from A4 (Provenance).
        # A4 requires provenance establishment for carry-forward; the specific read mechanism
        # is a consequence of A4 + P4 EV step 1, not a standalone rule.
        self.assertIn(
            "A4 (Provenance)",
            build_ground_prompt(),
            "E1: carry-forward provenance requirement is now owned by A4 (Provenance axiom)",
        )




class TestE4FalsifyingConditionContentGate(unittest.TestCase):
    def test_falsifying_condition_content_gate_present(self):
        self.assertIn(
            "content gate",
            build_ground_prompt(),
            "E4: falsifying condition must be a content gate (no implementation internals), not a self-check",
        )

    def test_falsifying_condition_self_check_replaced(self):
        self.assertNotIn(
            "before advancing, verify both parts are present",
            build_ground_prompt(),
            "E4: self-check phrasing must be replaced with the content gate",
        )


class TestE5CriteriaManifestQuoteGate(unittest.TestCase):
    def test_criteria_manifest_quote_gate_present(self):
        self.assertIn(
            "quote the gap text for this thread verbatim",
            build_ground_prompt(),
            "E5: criteria rung must require quoting manifest gap text verbatim before writing criterion",
        )


class TestE6ThreadNCompleteSuiteGate(unittest.TestCase):
    def test_suite_next_action_gate_present(self):
        self.assertIn(
            "only valid next action if no such result exists is the tool call that runs the suite",
            build_ground_prompt(),
            "E6: Thread N complete must gate on tool-executed suite result, naming the tool call as only valid next action",
        )

    def test_suite_self_check_replaced(self):
        self.assertNotIn(
            "before emitting ✅ Thread N complete or ✅ Manifest exhausted, run the full test suite",
            build_ground_prompt(),
            "E6: self-check phrasing must be replaced with the next-action gate",
        )


if __name__ == "__main__":
    unittest.main()

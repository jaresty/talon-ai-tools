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


class TestADR0180Closures(unittest.TestCase):
    """ADR-0180: Five SWE drift closures — C5, C2, C1, C4, C3."""

    def test_c5_obr_reinvoke_gate(self):
        """C5: OBR test-runner output blocking gate must say re-invoke the implemented artifact directly."""
        self.assertIn(
            "re-invoke the implemented artifact directly",
            _minimal(),
            "C5: ground prompt must include explicit OBR blocking gate requiring re-invoke when test runner output observed",
        )

    def test_c2_manifest_exhaustion_count_anchor(self):
        """C2: Manifest exhaustion must anchor count to declared N in Manifest declared sentinel."""
        self.assertIn(
            "locate the N in",
            _minimal(),
            "C2: ground prompt must instruct locating the N in Manifest declared before emitting Manifest exhausted",
        )

    def test_c1_hard_stop_ev_prohibition(self):
        """C1: HARD STOP must be explicitly prohibited at the executable validation rung."""
        self.assertIn(
            "HARD STOP may not be emitted at the executable validation rung",
            _minimal(),
            "C1: ground prompt must explicitly prohibit HARD STOP at the EV rung",
        )

    def test_c4_vro_label_required_for_impl_gate(self):
        """C4: VRO rung label must appear in transcript before Implementation gate cleared."""
        self.assertIn(
            "VRO rung label must appear in the transcript",
            _minimal(),
            "C4: ground prompt must require VRO rung label in transcript before impl gate",
        )

    def test_c3_formal_notation_const_prohibition(self):
        """C3: Formal notation must explicitly prohibit const/let/var assignments."""
        self.assertIn(
            "constant declarations (const, let, var",
            _minimal(),
            "C3: ground prompt must explicitly prohibit constant declarations in formal notation",
        )


class TestADR0181Closures(unittest.TestCase):
    """ADR-0181: Four OBR escape-route closures — N1, N2, N3, N4."""

    def test_n1_obr_exec_observed_mandatory(self):
        """N1: provenance statement does not replace 🔴 Execution observed at OBR."""
        self.assertIn(
            "provenance statement does not replace",
            _minimal(),
            "N1: ground prompt must state provenance statement does not replace the tool call / exec-observed",
        )

    def test_n2_ui_component_obr_mechanism(self):
        """N2: OBR invocation for UI components must specify renderToStaticMarkup or container.innerHTML."""
        self.assertIn(
            "renderToStaticMarkup",
            _minimal(),
            "N2: ground prompt must name renderToStaticMarkup or container.innerHTML as valid UI OBR invocation",
        )

    def test_n3_criterion_reemission_gate(self):
        """N3: criterion re-emission at OBR must be a blocking gate before Thread N complete."""
        self.assertIn(
            "criterion re-emission",
            _minimal(),
            "N3: ground prompt must name criterion re-emission as a gate before Thread N complete",
        )

    def test_n4_initial_criteria_one_criterion(self):
        """N4: first criteria rung after manifest must emit exactly one criterion."""
        self.assertIn(
            "first criteria rung after",
            _minimal(),
            "N4: ground prompt must prohibit multi-criterion planning block at the first criteria rung",
        )


if __name__ == "__main__":
    unittest.main()

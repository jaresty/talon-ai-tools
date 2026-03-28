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
        """C5: OBR test-runner output blocking gate — ADR-0181: attractor 6 subsumed by rung-entry gate."""
        # "re-invoke the implemented artifact directly" removed; gate part (c)/(d) enforces OBR type check.
        self.assertIn(
            "Rung-entry gate",
            _minimal(),
            "C5: rung-entry gate (ADR-0181) subsumes OBR test-runner blocking — gate must be present",
        )

    def test_c2_manifest_exhaustion_count_anchor(self):
        """C2: Manifest exhaustion must anchor count to declared N in Manifest declared sentinel."""
        self.assertIn(
            "Manifest exhausted may not be emitted unless the count of",
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
        """N4: one-criterion-per-thread-per-cycle discipline is encoded (ADR-0182: now via P3)."""
        self.assertIn(
            "one criterion per thread per cycle",
            _minimal(),
            "N4: ground prompt must state one criterion per thread per cycle — now encoded in P3 (Scope discipline)",
        )


class TestADR0182Closures(unittest.TestCase):
    """ADR-0182: Three transcript drift closures — N5, N6, N7."""

    def test_n5_exec_observed_prose_voids_sentinel(self):
        """N5: exec-observed with no delimited block is void (ADR-0184: condensed form)."""
        self.assertIn(
            "deviation voids the sentinel",
            _minimal(),
            "N5: ground prompt must void exec-observed sentinel on any deviation (ADR-0184: condensed form)",
        )

    def test_n6_v_complete_required_before_obr(self):
        """N6: OBR gate requires EV artifact to have run — encoded via rung table + P2 (ADR-0182)."""
        self.assertIn(
            "executable validation artifact runs",
            _minimal(),
            "N6: VRO gate 'executable validation artifact runs' must appear in rung table — P2 + rung table subsume V-complete-before-OBR",
        )

    def test_n7_manifest_covers_all_t_tags(self):
        """N7: manifest must contain one entry per [T:] tag in prose."""
        self.assertIn(
            "[T: gap-name] marker",
            _minimal(),
            "N7: ground prompt must require manifest to cover every [T:] tag in prose",
        )


if __name__ == "__main__":
    unittest.main()

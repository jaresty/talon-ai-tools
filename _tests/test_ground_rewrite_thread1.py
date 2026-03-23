"""Thread 1: GROUND_PARTS_MINIMAL core is rewritten — shorter, two new rules added."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import build_ground_prompt

ORIGINAL_CHARS = 14036
# The two new rules (rung-type constraint + ORB all-criteria) add ~710 chars.
# Redundancy removal should prevent unbounded growth — cap at original + 800.
MAX_CHARS = ORIGINAL_CHARS + 800


class TestGroundRewrite(unittest.TestCase):

    def setUp(self):
        self.prompt = build_ground_prompt(minimal=True)

    def test_prompt_does_not_grow_beyond_additions(self):
        self.assertLess(
            len(self.prompt),
            MAX_CHARS,
            f"Rewritten prompt ({len(self.prompt)} chars) must be < original + 800 ({MAX_CHARS}); "
            f"additions added ~710 chars, so net redundancy removal is required",
        )

    def test_rung_type_constraint_present(self):
        self.assertIn(
            "artifact type",
            self.prompt,
            "Rung-type constraint must state tool output must match the rung's artifact type",
        )

    def test_orb_all_criteria_present(self):
        self.assertTrue(
            "each criterion" in self.prompt or "every criterion" in self.prompt,
            "ORB gate must require demonstrating each/every criterion before Thread N complete",
        )

    def test_rung_type_restatement_removed_1(self):
        self.assertNotIn(
            "tests are never a valid consumer at this rung",
            self.prompt,
            "Restatement of rung-type constraint must be removed; axiom-level statement covers this",
        )

    def test_rung_type_restatement_removed_2(self):
        self.assertNotIn(
            "test pass/fail report is not valid OBS output",
            self.prompt,
            "Restatement of rung-type constraint must be removed; axiom-level statement covers this",
        )


    def test_ev_section_is_compact_gate_list(self):
        """EV section must be ≤ 1450 chars (raised from 1250 after C20 red-run-before-edit gate ~+170)."""
        import sys
        sys.path.insert(0, '.')
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        ev_start = core.find("Only validation artifacts may be produced")
        ev_end = core.find("✅ Validation artifact V complete must be emitted at the executable validation rung")
        ev_section = core[ev_start:ev_end]
        self.assertLessEqual(
            len(ev_section), 1450,
            f"EV rung section is {len(ev_section)} chars; must be ≤ 1450 after C20 red-run-before-edit addition",
        )


    def test_obs_section_is_compact(self):
        """OBS rung section must be ≤ 950 chars (raised from 850 after F4 UI artifact-type addition ~+90)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        obs_start = core.find("Upon writing the observed running behavior label")
        obs_end = core.find("✅ Thread N complete may not be emitted unless")
        obs_section = core[obs_start:obs_end]
        self.assertLessEqual(
            len(obs_section), 950,
            f"OBS rung section is {len(obs_section)} chars; must be ≤ 950 after F4 UI artifact-type addition",
        )


    def test_vro_section_is_compact(self):
        """VRO section must be ≤ 810 chars (raised from 650 after C11 harness-error gate addition ~+155)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find("Before writing the validation run observation rung label")
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        self.assertLessEqual(
            len(vro_section), 810,
            f"VRO section is {len(vro_section)} chars; must be ≤ 810 after C11 harness-error gate addition",
        )


    def test_criteria_section_is_compact(self):
        """Criteria rung section must be ≤ 1450 chars (raised from 1050 after C14+C17 additions ~+380)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        crit_start = core.find("From the criteria rung onward")
        crit_end = core.find("Formal notation encodes only")
        crit_section = core[crit_start:crit_end]
        self.assertLessEqual(
            len(crit_section), 1450,
            f"Criteria section is {len(crit_section)} chars; must be ≤ 1450 after C14+C17 gate additions",
        )


    def test_reconciliation_gate_is_compact(self):
        """Reconciliation gate section must be ≤ 400 chars (ADR-0177 target ~350)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        rec_start = core.find("Reconciliation gate:")
        rec_end = core.find("Each completion sentinel is valid")
        rec_section = core[rec_start:rec_end]
        self.assertLessEqual(
            len(rec_section), 400,
            f"Reconciliation gate is {len(rec_section)} chars; must be ≤ 400 after compact rewrite",
        )


    # F1: Thread N complete cycle anchor
    def test_f1_thread_complete_has_cycle_anchor(self):
        """Thread N complete gate must anchor OBS to 'after the most recent 🟢 Implementation gate cleared'."""
        self.assertIn(
            "after the most recent",
            build_ground_prompt(minimal=True),
            "F1: Thread N complete gate must anchor OBS cycle to 'after the most recent 🟢 Implementation gate cleared in this thread'",
        )


    # F2: Red-witness cycle anchor
    def test_f2_red_witness_has_cycle_anchor(self):
        """Red-witness gate must anchor prior red to 'after the most recent 🟢 Implementation gate cleared'."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find("Before writing the validation run observation rung label")
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        self.assertIn(
            "after the most recent",
            vro_section,
            "F2: red-witness gate must anchor prior red run to 'after the most recent 🟢 Implementation gate cleared for this thread'",
        )


    # F3: Behavioral-vs-structural criterion gate
    def test_f3_structural_criterion_gate_present(self):
        """Criteria rung must distinguish structural-presence assertions from behavioral assertions."""
        prompt = build_ground_prompt(minimal=True)
        self.assertIn(
            "structural",
            prompt,
            "F3: criteria rung must name structural-presence assertions and require a behavioral assertion about content or effect",
        )

    def test_f3_structural_criterion_names_counterexample(self):
        """Structural-vs-behavioral gate must name a concrete counterexample (column header)."""
        prompt = build_ground_prompt(minimal=True)
        self.assertIn(
            "column header",
            prompt,
            "F3: structural-vs-behavioral gate must name 'column header' as the disallowed structural-only form",
        )


    # F4: OBS artifact type clarification for UI
    def test_f4_obs_ui_artifact_type_named(self):
        """OBS rung must name browser-visible text as the required form for UI components."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        obs_start = core.find("Upon writing the observed running behavior label")
        obs_end = core.find("✅ Thread N complete may not be emitted unless")
        obs_section = core[obs_start:obs_end]
        self.assertIn(
            "browser",
            obs_section,
            "F4: OBS rung must name browser-visible output as the required form for UI components, excluding test-runner DOM queries",
        )


    # F5: Per-criterion OBS demonstration — test pass excluded
    def test_f5_thread_complete_demonstration_excludes_test_pass(self):
        """Thread N complete gate must state that a test pass does not constitute demonstration."""
        prompt = build_ground_prompt(minimal=True)
        self.assertIn(
            "test pass is not a demonstration",
            prompt,
            "F5: Thread N complete gate must state that a test pass does not constitute OBS demonstration of a criterion",
        )


    # Axiom collapse: artifact type is operative gate, "matching its definition" removed
    def test_axiom_uses_artifact_type_not_matching_definition(self):
        """Opening axiom must gate on artifact type, not the vague 'matching its definition'."""
        prompt = build_ground_prompt(minimal=True)
        self.assertNotIn(
            "matching its definition",
            prompt,
            "Axiom must not use 'matching its definition' — artifact type is the operative gate test",
        )

    def test_axiom_artifact_type_present_in_opening(self):
        """Opening axiom must make artifact type the operative gate condition."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        axiom_end = core.index("inference, prediction")
        axiom = core[:axiom_end]
        self.assertIn(
            "artifact type",
            axiom,
            "Axiom must state artifact type as the gate condition before the inference exclusion",
        )


if __name__ == "__main__":
    unittest.main()

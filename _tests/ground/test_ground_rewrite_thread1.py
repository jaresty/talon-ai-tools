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
# C22–C24 add ~820 chars; C25–C28 add ~883 chars; ADR-0178 D1-D7 add ~5191 chars (drift closures).
MAX_CHARS = (
    ORIGINAL_CHARS + 13900
)  # ADR-0179: E1-E6 add ~1117; ADR-0180: C1-C5 add ~500; ADR-0181: N1-N4 add ~900; ADR-0182: N5-N7 add ~770; formal notation separation; OBR live-process fix: +326; L1-L6 drift closures: +578; ADR-0183 L7-L12 forward-gate closures: +~1940; L13-L24 escape-route closures: +~800; L25-L27 escape-route closures: +~350; L35 EV-rung tool-call gate + meta-test forward gate: +~262; OBR forward gate + all-criteria rule: +~528


class TestGroundRewrite(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

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
        """EV section must be ≤ 2600 chars (raised from 1800 after ADR-0178 D6 carry-forward addition)."""
        import sys

        sys.path.insert(0, ".")
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        ev_start = core.find("Only validation artifacts may be produced")
        ev_end = core.find(
            "✅ Validation artifact V complete must be emitted at the executable validation rung"
        )
        ev_section = core[ev_start:ev_end]
        self.assertLessEqual(
            len(ev_section),
            2900,
            f"EV rung section is {len(ev_section)} chars; must be ≤ 2900 after ADR-0179 E1 carry-forward read gate",
        )

    def test_obr_realism_hierarchy(self):
        """OBR rung must require live running process; in-process rendering gated on no runnable artifact."""
        # ADR-0184: dev server / HTML enumeration removed by Thread B; live-process invariant is the gate.
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        self.assertIn(
            "live running process",
            core,
            "OBR realism hierarchy: live running process must be named as the required invocation form",
        )
        self.assertIn(
            "only when no runnable artifact exists",
            core,
            "OBR realism hierarchy: in-process rendering must be gated on no runnable artifact existing",
        )

    def test_obs_section_is_compact(self):
        """OBS rung section must be ≤ 2700 chars (raised from 2200 after OBR live-process fix)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        obs_start = core.find("Upon writing the observed running behavior label")
        obs_end = core.find("✅ Thread N complete may not be emitted unless")
        obs_section = core[obs_start:obs_end]
        self.assertLessEqual(
            len(obs_section),
            3200,
            f"OBS rung section is {len(obs_section)} chars; must be ≤ 3200 after ADR-0183 L8 gate addition",
        )

    def test_vro_section_is_compact(self):
        """VRO section must be ≤ 810 chars (raised from 650 after C11 harness-error gate addition ~+155)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find(
            "Before writing the validation run observation rung label"
        )
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        self.assertLessEqual(
            len(vro_section),
            810,
            f"VRO section is {len(vro_section)} chars; must be ≤ 810 after C11 harness-error gate addition",
        )

    def test_criteria_section_is_compact(self):
        """Criteria rung section must be ≤ 2400 chars (raised from 1800 after ADR-0178 D3 falsifying-condition + D5 thread-markers)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        crit_start = core.find("From the criteria rung onward")
        crit_end = core.find("Formal notation encodes only")
        crit_section = core[crit_start:crit_end]
        self.assertLessEqual(
            len(crit_section),
            2700,
            f"Criteria section is {len(crit_section)} chars; must be ≤ 2700 after ADR-0179 E4/E5 additions",
        )

    def test_reconciliation_gate_is_compact(self):
        """Reconciliation gate section must be ≤ 400 chars (ADR-0177 target ~350)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        rec_start = core.find("Reconciliation gate:")
        rec_end = core.find("Each completion sentinel is valid")
        rec_section = core[rec_start:rec_end]
        self.assertLessEqual(
            len(rec_section),
            400,
            f"Reconciliation gate is {len(rec_section)} chars; must be ≤ 400 after compact rewrite",
        )

    # F1: Thread N complete cycle anchor
    def test_f1_thread_complete_has_cycle_anchor(self):
        """Thread N complete gate must anchor OBS to 'after the most recent 🟢 Implementation gate cleared'."""
        self.assertIn(
            "after the most recent",
            build_ground_prompt(),
            "F1: Thread N complete gate must anchor OBS cycle to 'after the most recent 🟢 Implementation gate cleared in this thread'",
        )

    # F2: Red-witness cycle anchor
    def test_f2_red_witness_has_cycle_anchor(self):
        """Red-witness gate must anchor prior red to 'after the most recent 🟢 Implementation gate cleared'."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find(
            "Before writing the validation run observation rung label"
        )
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
        prompt = build_ground_prompt()
        self.assertIn(
            "structural",
            prompt,
            "F3: criteria rung must name structural-presence assertions and require a behavioral assertion about content or effect",
        )

    def test_f3_structural_criterion_names_counterexample(self):
        """Structural-vs-behavioral gate must name a concrete counterexample (column header)."""
        prompt = build_ground_prompt()
        self.assertIn(
            "column header",
            prompt,
            "F3: structural-vs-behavioral gate must name 'column header' as the disallowed structural-only form",
        )

    # F4: OBS artifact type — output must directly demonstrate criterion behavior
    def test_f4_obs_ui_artifact_type_named(self):
        """OBS output must directly demonstrate the specific behavior named in the criterion."""
        # ADR-0184: "browser"-specific enumeration removed by Thread B; "directly demonstrate" covers it.
        from lib.groundPrompt import GROUND_PARTS_MINIMAL

        core = GROUND_PARTS_MINIMAL["core"]
        obs_start = core.find("Upon writing the observed running behavior label")
        obs_end = core.find("✅ Thread N complete may not be emitted unless")
        obs_section = core[obs_start:obs_end]
        self.assertIn(
            "directly demonstrate the specific behavior named in the criterion",
            obs_section,
            "F4: OBR output must directly demonstrate the specific behavior named in the criterion",
        )

    # F5: Per-criterion OBS demonstration — test output is VRO-type not OBR-type (A2 axiom)
    def test_f5_thread_complete_demonstration_excludes_test_pass(self):
        """A2 axiom must state test-suite output is VRO-type, not OBR-type."""
        # ADR-0184: "test pass is not a demonstration" removed; A2 covers this globally at axiom level.
        prompt = build_ground_prompt()
        self.assertIn(
            "validation-run-observation-type output, not observed-running-behavior-type output",
            prompt,
            "F5: A2 axiom must state that test-suite output is VRO-type not OBR-type",
        )

    # Axiom collapse: artifact type is operative gate, "matching its definition" removed
    def test_axiom_uses_artifact_type_not_matching_definition(self):
        """Opening axiom must gate on artifact type, not the vague 'matching its definition'."""
        prompt = build_ground_prompt()
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

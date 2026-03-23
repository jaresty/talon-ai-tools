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
        """EV section must be rewritten as a compact gate list (≤ 1250 chars, ADR-0177 target ~1200)."""
        import sys
        sys.path.insert(0, '.')
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        ev_start = core.find("Only validation artifacts may be produced")
        ev_end = core.find("✅ Validation artifact V complete must be emitted at the executable validation rung")
        ev_section = core[ev_start:ev_end]
        self.assertLessEqual(
            len(ev_section), 1250,
            f"EV rung section is {len(ev_section)} chars; must be ≤ 1250 after compact gate list rewrite",
        )


    def test_obs_section_is_compact(self):
        """OBS rung section must be ≤ 850 chars (ADR-0177 target ~800)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        obs_start = core.find("Upon writing the observed running behavior label")
        obs_end = core.find("✅ Thread N complete may not be emitted unless")
        obs_section = core[obs_start:obs_end]
        self.assertLessEqual(
            len(obs_section), 850,
            f"OBS rung section is {len(obs_section)} chars; must be ≤ 850 after compact rewrite",
        )


    def test_vro_section_is_compact(self):
        """VRO section must be ≤ 650 chars (ADR-0177 target ~600)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        vro_start = core.find("Before writing the validation run observation rung label")
        vro_end = core.find("At the validation run observation rung, run")
        vro_section = core[vro_start:vro_end]
        self.assertLessEqual(
            len(vro_section), 650,
            f"VRO section is {len(vro_section)} chars; must be ≤ 650 after compact rewrite",
        )


    def test_criteria_section_is_compact(self):
        """Criteria rung section must be ≤ 750 chars (ADR-0177 target ~700)."""
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        core = GROUND_PARTS_MINIMAL["core"]
        crit_start = core.find("From the criteria rung onward")
        crit_end = core.find("Formal notation encodes only")
        crit_section = core[crit_start:crit_end]
        self.assertLessEqual(
            len(crit_section), 750,
            f"Criteria section is {len(crit_section)} chars; must be ≤ 750 after compact rewrite",
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


if __name__ == "__main__":
    unittest.main()

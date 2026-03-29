"""Tests for ADR-0214: Ground prompt generative kernel rewrite.

Asserts that GROUND_PARTS_MINIMAL["core"] is structured as a five-section
generative kernel and that P4 prose enumerations and the type taxonomy block
prose have been replaced.
"""

import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0214GateFormulaPresent(unittest.TestCase):
    """Thread 1: gate-formula — gate formula (A1/A2/A4/R2 as single conditional) is present."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_gate_formula_conditional_present(self):
        """Gate formula states a single if-and-only-if conditional for all rung gates."""
        self.assertIn(
            "if and only if",
            self.core,
            "ADR-0214: gate formula must state the gate condition as a single if-and-only-if conditional",
        )

    def test_type_determined_by_production_method_present(self):
        """A2 must be stated: type is determined by production method, not content."""
        self.assertIn(
            "production method, not content",
            self.core,
            "ADR-0214: A2 (type = production method) must be present in gate formula",
        )


class TestADR0214P4ProseAbsent(unittest.TestCase):
    """Thread 2: p4-prose-absent — P4 verbose rung-action prose is replaced by sequence table."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_ev_rung_prose_enumeration_absent(self):
        """P4 EV rung prose enumeration replaced by sequence table entry."""
        self.assertNotIn(
            "writing implementation files at the EV rung is a protocol violation",
            self.core,
            "ADR-0214: P4 EV prose 'writing implementation files at EV rung' must be absent",
        )

    def test_p4_prose_header_absent(self):
        """P4 rung action discipline prose header removed."""
        self.assertNotIn(
            "P4 (Rung action discipline): each rung has a closed action set",
            self.core,
            "ADR-0214: P4 named principle header must be absent",
        )

    def test_type_taxonomy_block_header_absent(self):
        """_type_taxonomy_block() header prose replaced by type definitions in rung table."""
        self.assertNotIn(
            "Artifact type classification",
            self.core,
            "ADR-0214: _type_taxonomy_block 'Artifact type classification' header must be absent",
        )

    def test_type_taxonomy_vro_prose_absent(self):
        """VRO-type verbose explanation from _type_taxonomy_block replaced by rung table type definition."""
        self.assertNotIn(
            "VRO-type is produced by running a test suite",
            self.core,
            "ADR-0214: _type_taxonomy_block VRO-type prose must be absent; type definition belongs in rung table",
        )


class TestADR0214NonDerivableRulesPresent(unittest.TestCase):
    """Thread 3: non-derivable-rules — Section 5 non-derivable rules are present."""

    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_harness_error_not_red_run_present(self):
        """Harness-error routing rule must remain (non-derivable: defines what red run means)."""
        self.assertIn(
            "harness error",
            self.core.lower(),
            "ADR-0214: harness-error routing rule must be present in non-derivable section",
        )

    def test_green_without_red_vacuity_present(self):
        """Green-without-red vacuity rule must remain (non-derivable: closes rationalization)."""
        self.assertIn(
            "vacuous",
            self.core,
            "ADR-0214: green-without-red vacuity rule must be present in non-derivable section",
        )

    def test_hard_stop_scope_present(self):
        """HARD STOP scope rule must remain (non-derivable: names the one valid upward return)."""
        self.assertIn(
            "HARD STOP",
            self.core,
            "ADR-0214: HARD STOP scope rule must be present in non-derivable section",
        )

    def test_session_persistence_present(self):
        """Session persistence policy must remain (non-derivable: design decision)."""
        self.assertIn(
            "Ground entered",
            self.core,
            "ADR-0214: session persistence rule must be present",
        )


class TestADR0214CharCountReduced(unittest.TestCase):
    """Thread 4: char-count — rewrite reduces core string length."""

    def test_char_count_below_pre_adr0214_baseline(self):
        """Generative kernel rewrite must significantly reduce core string length."""
        current = len(GROUND_PARTS_MINIMAL["core"])
        PRE_ADR0214_BASELINE = 33473  # measured before rewrite
        self.assertLess(
            current,
            PRE_ADR0214_BASELINE,
            f"ADR-0214: core string ({current} chars) must be shorter than pre-rewrite baseline ({PRE_ADR0214_BASELINE})",
        )

    def test_protocol_invariant_opens_core(self):
        """Core must open with the protocol invariant sentence."""
        core = GROUND_PARTS_MINIMAL["core"]
        self.assertTrue(
            core.startswith("This protocol exists"),
            "ADR-0214: core must open with the protocol invariant why-sentence",
        )


class TestADR0214HelperFunctionRemoved(unittest.TestCase):
    """Thread 2: helper-functions — _type_taxonomy_block() is removed."""

    def test_type_taxonomy_block_not_importable(self):
        """_type_taxonomy_block helper must not exist after ADR-0214 rewrite."""
        import lib.groundPrompt as gp
        self.assertFalse(
            hasattr(gp, "_type_taxonomy_block"),
            "ADR-0214: _type_taxonomy_block must be removed; its content is absorbed or superseded",
        )


if __name__ == "__main__":
    unittest.main()

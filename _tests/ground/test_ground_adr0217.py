"""Tests for ADR-0217: Ground prompt — generative ladder (19 principles).

Asserts:
- Each of the 19 principle labels (P1 through P19) is present
- The ladder derivation rung instruction is present
- The standard rung names example line is present
- The sentinel block is present
- Key removed phrases are absent
- Core char count is below the ADR-0216 baseline (29,990)
"""
import unittest

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0217PrinciplesPresent(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_p1_present(self):
        self.assertIn("P1 (Intent primacy)", self.core)

    def test_p2_present(self):
        self.assertIn("P2 (Behavioral change isolation)", self.core)

    def test_p3_present(self):
        self.assertIn("P3 (Observable evidence required)", self.core)

    def test_p4_present(self):
        self.assertIn("P4 (Enforced and persistent)", self.core)

    def test_p5_present(self):
        self.assertIn("P5 (Automation quality verified)", self.core)

    def test_p6_present(self):
        self.assertIn("P6 (Artifact type discipline)", self.core)

    def test_p7_present(self):
        self.assertIn("P7 (Upward faithfulness)", self.core)

    def test_p8_present(self):
        self.assertIn("P8 (Rung validity test)", self.core)

    def test_p9_present(self):
        self.assertIn("P9 (Information density preservation)", self.core)

    def test_p10_present(self):
        self.assertIn("P10 (Three-part completeness)", self.core)

    def test_p11_present(self):
        self.assertIn("P11 (Immediate lowest-rung observation)", self.core)

    def test_p12_present(self):
        self.assertIn("P12 (Completeness slice)", self.core)

    def test_p13_present(self):
        self.assertIn("P13 (Observation-first, observation-last)", self.core)

    def test_p14_present(self):
        self.assertIn("P14 (Evidential authority)", self.core)

    def test_p15_present(self):
        self.assertIn("P15 (Cycle identity)", self.core)

    def test_p16_present(self):
        self.assertIn("P16 (Provenance)", self.core)

    def test_p17_present(self):
        self.assertIn("P17 (Derivation chain)", self.core)

    def test_p18_present(self):
        self.assertIn("P18 (Continuous descent)", self.core)

    def test_p19_present(self):
        self.assertIn("P19 (Thread sequencing)", self.core)


class TestADR0217LadderDerivationPresent(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_ladder_derivation_rung_instruction_present(self):
        self.assertIn("Ladder derivation rung:", self.core)

    def test_standard_rung_names_example_present(self):
        self.assertIn(
            "prose \u2192 criteria \u2192 formal notation \u2192 executable validation \u2192 "
            "validation run observation \u2192 executable implementation \u2192 observed running behavior",
            self.core,
        )


class TestADR0217SentinelBlockPresent(unittest.TestCase):
    def setUp(self):
        self.prompt = build_ground_prompt()

    def test_sentinel_block_present(self):
        self.assertIn("Sentinel formats \u2014", self.prompt)

    def test_exec_observed_sentinel_present(self):
        self.assertIn("Execution observed:", self.prompt)

    def test_impl_gate_sentinel_present(self):
        self.assertIn("Implementation gate cleared", self.prompt)

    def test_thread_complete_sentinel_present(self):
        self.assertIn("Thread N complete", self.prompt)


class TestADR0217RemovedPhrasesAbsent(unittest.TestCase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]

    def test_closed_action_set_absent(self):
        self.assertNotIn(
            "closed action set",
            self.core,
            "ADR-0217: closed action set language must be absent",
        )

    def test_ev_rung_sequence_absent(self):
        self.assertNotIn(
            "EV rung: (1)",
            self.core,
            "ADR-0217: EV rung action sequence must be absent",
        )

    def test_obr_rung_sequence_absent(self):
        self.assertNotIn(
            "OBR rung: (1)",
            self.core,
            "ADR-0217: OBR rung action sequence must be absent",
        )

    def test_before_writing_vro_label_absent(self):
        self.assertNotIn(
            "Before writing the validation run observation rung label",
            self.core,
            "ADR-0217: VRO pre-run gate prose must be absent",
        )

    def test_implementation_gate_first_token_absent(self):
        self.assertNotIn(
            "Implementation gate cleared is the first token",
            self.core,
            "ADR-0217: EI first-token gate prose must be absent",
        )


class TestADR0217CharCount(unittest.TestCase):
    def test_char_count_below_adr0216_baseline(self):
        current = len(GROUND_PARTS_MINIMAL["core"])
        ADR0216_BASELINE = 29_990
        self.assertLess(
            current,
            ADR0216_BASELINE,
            f"ADR-0217: core string ({current} chars) must be shorter than ADR-0216 baseline ({ADR0216_BASELINE})",
        )


if __name__ == "__main__":
    unittest.main()

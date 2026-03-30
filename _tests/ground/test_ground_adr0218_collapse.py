"""Tests for ADR-0218 collapse: 19 collapsed principles replace P1-P21.

Verifies that all escape-route closures from ADR-0227–0237 survive the collapse,
the prompt is shorter than the pre-collapse ceiling, and all key invariants are present.
"""

import unittest

from _tests.ground.ground_test_base import GroundADRTestBase

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt


class TestADR0218Collapse(GroundADRTestBase):
    def setUp(self):
        self.core = GROUND_PARTS_MINIMAL["core"]
        self.prompt = build_ground_prompt()

    # --- size ---

    def test_char_count_below_pre_collapse(self):
        current = len(self.core)
        self.assertLess(
            current,
            21_000,
            f"collapsed core ({current}) should be shorter than pre-collapse 21,427",
        )

    # --- P1-P12 invariants survive ---

    def test_intent_primacy(self):
        self.assertDetects("intent exists", self.core)

    def test_behavioral_change_isolation(self):
        self.assertDetects("One rung per artifact type", self.core)

    def test_observable_evidence_required(self):
        self.assertDetects(
            "Pre/post change states visible through actual tool output", self.core
        )

    def test_automation_quality_verified(self):
        self.assertDetects("Automation must fail before passing", self.core)

    def test_upward_faithfulness(self):
        self.assertDetects("Lower rungs narrow what upper rungs permit", self.core)

    def test_rung_validity_test(self):
        self.assertDetects("Human reviewer with only this rung", self.core)

    def test_completeness_slice(self):
        self.assertDetects(
            "One independently testable behavior per thread per cycle", self.core
        )

    # --- ADR-0235: artifact type definitions ---

    def test_validation_defined(self):
        self.assertDetects(
            "executable validation artifact is a file whose sole purpose is to assert behavioral properties",
            self.core,
        )

    def test_validation_no_behavior(self):
        self.assertDetects("contains no behavior of its own", self.core)

    def test_validation_not_imported(self):
        self.assertDetects(
            "validation files may not be imported by implementation files", self.core
        )

    def test_implementation_defined(self):
        self.assertDetects(
            "executable implementation artifact is a file that produces behavior directly",
            self.core,
        )

    def test_implementation_no_assertions(self):
        self.assertDetects("implementation files may not contain assertions", self.core)

    def test_overlap_voids_rung(self):
        self.assertDetects("file that both asserts and implements", self.core)

    def test_classification_by_content(self):
        self.assertDetects(
            "classification is determined by file content, not file path or naming convention",
            self.core,
        )

    # --- ADR-0236/0237: live-code observation ---

    def test_observation_means_direct_invocation(self):
        self.assertDetects(
            "Observing running behavior means invoking the system directly", self.core
        )

    def test_output_produced_by_behavior_itself(self):
        self.assertDetects("output must be produced by the behavior itself", self.core)

    def test_live_code_required(self):
        self.assertDetects("the tool call must execute live running code", self.core)

    def test_reads_excluded(self):
        self.assertDetects("reading files", self.core)

    def test_test_suite_excluded(self):
        self.assertDetects(
            "a test suite run does not satisfy this requirement", self.core
        )

    # --- ADR-0232/0233/0234: closing observation and loop termination ---

    def test_closing_observation_sentinel(self):
        self.assertDetects("Closing observation", self.core)

    def test_ground_complete_only_from_loop(self):
        self.assertDetects(
            "\u2705 Ground complete may only be emitted as the outcome of the observation loop",
            self.core,
        )

    def test_emitting_outside_loop_is_violation(self):
        self.assertDetects(
            "emitting it outside the loop is a protocol violation", self.core
        )

    # --- ADR-0227: impl_gate assertion-level failure ---

    def test_impl_gate_assertion_level(self):
        self.assertDetects("assertion-level failure", self.core)

    def test_impl_gate_infrastructure_excluded(self):
        self.assertDetects("infrastructure failure", self.core)

    # --- ADR-0229: impl_intent type cross-check ---

    def test_impl_intent_type_crosscheck(self):
        # Now uses impl_intent instead of write_authorized
        self.assertDetects("artifact type permitted at the current rung", self.core)

    # --- ADR-0230/0231: upward return ---

    def test_upward_return_trigger_from_above(self):
        self.assertDetects(
            "trigger for an upward return must originate at the rung being revised or above",
            self.core,
        )

    def test_lower_rung_pressure_prohibited(self):
        self.assertDetects(
            "difficulty, failure, or constraint pressure from any lower rung is not a valid trigger",
            self.core,
        )

    def test_observation_loop_return(self):
        self.assertDetects(
            "Returning to the session observation loop is valid", self.core
        )

    def test_ladder_voided_on_loop_return(self):
        self.assertDetects("entire current ladder is void", self.core)

    # --- propagation ---

    def test_propagated_to_prompt(self):
        self.assertDetects("intent exists", self.prompt)


if __name__ == "__main__":
    unittest.main()

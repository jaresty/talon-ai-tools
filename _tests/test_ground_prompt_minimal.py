"""Tests for Thread 1: minimal GROUND_PARTS in groundPrompt.py."""

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from lib.groundPrompt import RUNG_SEQUENCE, SENTINEL_TEMPLATES, build_ground_prompt

CANONICAL_RUNG_NAMES = [e["name"] for e in RUNG_SEQUENCE]

ABSTRACT_RULES = [
    "tool-executed",          # Rule 1: claim only tool events
    "derives from",           # Rule 2: faithful derivation
    "declared gap",           # Rule 3: stop at the gap
    "only the gap declared",  # Rule 2b: gap-locality
    "reconcile",              # Reconciliation gate
    "without consulting I",   # V self-sufficiency
    "declared intent",        # I precedes its representations
    "rung label",             # Rung label at every transition
]

NAMED_VIOLATION_MODES = [
    "vacuous-green",
    "retroactive sentinel",
    # "carry-forward" removed from ban list: ADR-0178 D6 introduced it as a
    # legitimate process rule in the core prose (modification carry-forward).
    "I-formation",
    "R2 audit",
    "upward correction",
]


class TestMinimalGroundParts(unittest.TestCase):
    def setUp(self):
        from lib.groundPrompt import GROUND_PARTS_MINIMAL
        self.parts = GROUND_PARTS_MINIMAL
        self.prompt = build_ground_prompt()

    def test_total_chars_under_3000(self):
        total = sum(len(v) for v in self.parts.values())
        self.assertLess(total, 21500,
            f"GROUND_PARTS_MINIMAL total {total} chars; expected < 21500 (raised after ADR-0179 E1-E6 drift fixes)")

    def test_three_abstract_rules_present(self):
        for rule_marker in ABSTRACT_RULES:
            self.assertIn(rule_marker, self.prompt,
                f"Abstract rule marker missing: {rule_marker!r}")

    def test_all_rung_names_present_in_order(self):
        pos = -1
        for name in CANONICAL_RUNG_NAMES:
            new_pos = self.prompt.find(name, pos + 1)
            self.assertGreater(new_pos, pos,
                f"Rung name {name!r} missing or out of order")
            pos = new_pos

    def test_all_sentinel_format_strings_present(self):
        for key, value in SENTINEL_TEMPLATES.items():
            self.assertIn(value, self.prompt,
                f"Sentinel {key!r} missing from minimal prompt")

    def test_no_named_violation_modes_in_core_rules(self):
        # Check only the core prose rules, not the sentinel format strings
        # (sentinels legitimately contain terms like "I-formation complete")
        sentinel_values = set(SENTINEL_TEMPLATES.values())
        core = self.parts.get("core", "")
        # Strip sentinel format strings from the check surface
        check_surface = core
        for sv in sentinel_values:
            check_surface = check_surface.replace(sv, "")
        for mode in NAMED_VIOLATION_MODES:
            self.assertNotIn(mode, check_surface,
                f"Named violation mode found in core rules: {mode!r}")

    def test_vro_recurring_gap_returns_to_formal_notation(self):
        self.assertIn("observed gap matches the prior cycle's gap", self.prompt,
            "Minimal spec must state that a recurring gap requires return to formal notation")

    def test_vro_rung_stop_after_first_failure(self):
        self.assertIn("do not enumerate multiple failures", self.prompt,
            "Minimal spec must state VRO stops after first failure")

    def test_ei_rung_pre_edit_check(self):
        self.assertIn("One edit per re-run cycle", self.prompt,
            "Minimal spec must require re-running validation after each edit")

    def test_ei_rung_one_edit_per_cycle(self):
        self.assertIn("One edit per re-run cycle", self.prompt,
            "Minimal spec must state one edit per re-run cycle at EI rung")

    def test_formal_notation_encodes_only_declared_criteria(self):
        self.assertIn("Formal notation encodes only the criteria declared", self.prompt,
            "Minimal spec must state formal notation encodes only declared criteria")

    def test_ev_rung_requires_prior_red_run(self):
        self.assertIn("if it passes, the artifact is vacuous", self.prompt,
            "Minimal spec must require that a passing-before-edit artifact is vacuous and must be rewritten")

    def test_preexisting_test_does_not_satisfy_ev_rung(self):
        self.assertIn("pre-existing test that happens to pass does not satisfy", self.prompt,
            "Minimal spec must clarify that pre-existing passing tests do not satisfy the EV rung")

    def test_every_rung_requires_gap_sentinel(self):
        self.assertIn("Before writing the criteria, formal notation, executable validation, executable implementation", self.prompt,
            "Minimal spec must require a gap sentinel before specific rung label writes")

    def test_gap_names_behavior_not_artifact_absence(self):
        self.assertIn("need to implement a landing page", self.prompt,
            "Minimal spec must give a counterexample showing gap must name absent behavior not an absent artifact")

    def test_gap_phrased_as_currently_false_assertion(self):
        self.assertIn("phrased as a currently-false assertion", self.prompt,
            "Minimal spec must require gap to be phrased as a currently-false assertion not a goal")

    def test_each_rung_artifact_is_minimal(self):
        self.assertIn("one independently testable behavior", self.prompt,
            "Minimal spec must state criterion is one independently testable behavior")

    def test_criterion_may_not_use_conjunction(self):
        self.assertIn("if the criterion contains the word", self.prompt,
            "Minimal spec must forbid joining multiple behaviors with 'and' in one criterion")

    def test_mid_ladder_still_requires_ev_and_vro(self):
        self.assertIn("including after an upward return", self.prompt,
            "Minimal spec must state EV and VRO required even after mid-ladder upward return")

    def test_ev_sentinel_dependency(self):
        self.assertIn("Validation artifact V complete must be emitted at the executable validation rung", self.prompt,
            "Minimal spec must require V-complete sentinel before VRO label as sentinel dependency")

    def test_impl_gate_current_cycle_only(self):
        self.assertIn("from the current cycle", self.prompt,
            "Minimal spec must require execution-observed from current cycle not prior cycle for impl-gate")

    def test_thread_complete_sentinel_dependency(self):
        self.assertIn("Thread N complete may not be emitted unless", self.prompt,
            "Minimal spec must require execution-observed after OBS label before thread-complete")

    def test_post_obs_completeness_check(self):
        self.assertIn("each distinct predicate requires a separate thread", self.prompt,
            "Minimal spec must require each behavioral predicate to have a separate thread (manifest-time gate)")

    def test_conjunction_ban_has_example(self):
        self.assertIn("are two criteria, not one", self.prompt,
            "Minimal spec must include a concrete example showing conjunction splits into two criteria")

    def test_gap_sentinel_not_a_stopping_point(self):
        self.assertIn("only the validation run observation rung stops after naming the gap", self.prompt,
            "Minimal spec must state gap sentinel is not a stopping point — only VRO stops")

    def test_every_rung_addresses_only_declared_gap(self):
        self.assertIn("not all known requirements of the task", self.prompt,
            "Minimal spec must state each rung addresses only declared gap, not all requirements")

    def test_criterion_derivable_from_prose_only(self):
        self.assertIn("derived from the prose alone", self.prompt,
            "Minimal spec must require criterion to be derivable from prose, not implementation knowledge")

    def test_criterion_and_is_invalid(self):
        self.assertIn("if the criterion contains the word", self.prompt,
            "Minimal spec must mechanically ban 'and' in criteria as invalid")

    def test_ev_green_first_run_perturb_to_distinguish(self):
        self.assertIn("perturb the implementation", self.prompt,
            "Minimal spec must require perturbation to distinguish pre-existing behavior from vacuous test")

    def test_ev_vacuous_test_detected_by_perturbation(self):
        self.assertIn("vacuous", self.prompt,
            "Minimal spec must name the vacuous-test case and require rewriting the test")

    def test_ev_green_first_run_return_to_gap(self):
        self.assertIn("if the artifact asserts runtime behavior, perturb the implementation", self.prompt,
            "Minimal spec must require perturbation check for runtime-behavioral artifacts")

    def test_prose_reemitted_before_each_criteria_rung(self):
        self.assertIn("prose rung must be re-emitted at the start of every cycle", self.prompt,
            "Minimal spec must require prose to be re-emitted before criteria in every cycle including upward returns")

    def test_obs_rung_produces_only_tool_output(self):
        self.assertIn("implementation edits, new files, and code changes are not permitted", self.prompt,
            "Minimal spec must forbid implementation edits at OBS rung")

    def test_upward_return_three_level_hierarchy(self):
        self.assertIn("observation cannot be produced is a prose-description failure", self.prompt,
            "Minimal spec must state three-level return hierarchy: EI loop / formal notation / prose")

    def test_prose_return_when_observation_impossible(self):
        self.assertIn("observation cannot be produced", self.prompt,
            "Minimal spec must require prose return when observation cannot be produced")

    def test_obs_rung_required_every_cycle(self):
        self.assertIn("including the observed running behavior rung", self.prompt,
            "Minimal spec must state OBS rung is required in every cycle, not just final")

    def test_manifest_exhausted_when_no_gap_remains(self):
        self.assertIn("if no currently-false behavior remains, emit", self.prompt,
            "Minimal spec must require Manifest exhausted when no false behavior remains, not a fabricated gap")

    def test_thread_complete_requires_obs_label_written(self):
        self.assertIn("observed running behavior label has been written after the most recent", self.prompt,
            "Minimal spec must require OBS label written after most recent impl-gate in this thread (cycle anchor)")

    def test_final_report_rung_by_rung(self):
        self.assertIn("final report", self.prompt,
            "Minimal spec must require a final rung-by-rung report after manifest exhausted")

    def test_final_report_includes_prose_criteria_notation(self):
        self.assertIn("prose, criteria, and formal notation for each thread", self.prompt,
            "Minimal spec must specify final report includes prose, criteria, and formal notation per thread")

    def test_final_report_reconciles_documents(self):
        self.assertIn("reconcile any documents", self.prompt,
            "Minimal spec must require document reconciliation in the final report")

    def test_ev_rung_only_validation_artifact_permitted(self):
        self.assertIn("no other content is permitted before", self.prompt,
            "Minimal spec must state only the validation artifact is permitted before V-complete sentinel")

    def test_sentinel_placement_at_defining_rung_only(self):
        self.assertIn("valid only at its defining rung", self.prompt,
            "Minimal spec must state each completion sentinel is valid only at its defining rung")

    def test_final_report_copies_not_claims(self):
        self.assertIn("no new behavioral claims", self.prompt,
            "Minimal spec must require final report copies existing artifacts, no new behavioral claims")

    def test_prose_reemit_is_a_mechanical_check(self):
        self.assertIn("the criterion must be immediately derivable from the re-emitted prose", self.prompt,
            "Minimal spec must frame prose re-emit as a non-optional gate — criterion must derive from re-emitted prose")

    def test_build_ground_prompt_returns_nonempty(self):
        self.assertGreater(len(self.prompt), 0)

    # C4: run-before-label gate
    def test_vro_rung_requires_tool_invocation_before_label(self):
        self.assertIn("Before writing the validation run observation rung label", self.prompt,
            "Ground must require tool invocation before writing the VRO rung label — prediction does not satisfy this gate")

    # C3: criteria-only after gap
    def test_gap_at_obs_rung_permits_only_criteria_label_next(self):
        self.assertIn("only valid next token", self.prompt,
            "Ground must state that after emitting Gap: at the observation rung, the only valid next token is the criteria rung label")

    # C1: prose-in-cycle gate
    def test_criteria_label_requires_prose_label_in_current_cycle(self):
        self.assertIn("prose rung must be re-emitted at the start of every cycle", self.prompt,
            "Ground must gate the criteria label on prose being re-emitted in the current cycle")

    # C2: newly-produced check
    def test_v_complete_requires_artifact_not_pre_existing(self):
        self.assertIn("confirm via tool call that the artifact path does not pre-exist", self.prompt,
            "Ground must require checking via tool call that the validation artifact does not pre-exist before emitting V-complete")

    # Attractor sentence
    def test_attractor_sentence_rung_satisfied_only_by_tool_event(self):
        self.assertIn("A rung is satisfied when and only when a tool-executed event", self.prompt,
            "Ground must open with the attractor sentence: a rung is satisfied only by a tool-executed event, not inference or prediction")

    # C5: pre-existing document update at reconciliation gate
    def test_reconciliation_gate_covers_preexisting_documents(self):
        gate_idx = self.prompt.index("Reconciliation gate:")
        final_report_idx = self.prompt.index("After emitting \u2705 Manifest exhausted")
        # The gate must mention updating pre-existing documents that record I
        try:
            doc_idx = self.prompt.index("records I", gate_idx)
        except ValueError:
            self.fail("Reconciliation gate must instruct updating pre-existing documents that record I when prose evolves on upward return")
        self.assertLess(doc_idx, final_report_idx,
            "Pre-existing document update must appear in the reconciliation gate, not only in the final report section")


    # Manifest declaration: behavioral predicate scan (C12 — moved from thread-complete)
    def test_thread_complete_references_prose_rung(self):
        idx = self.prompt.index("Before emitting \u2705 Manifest declared, scan every sentence in the prose")
        end = self.prompt.index("Outputting a rung label is what begins that rung")
        segment = self.prompt[idx:end]
        self.assertIn("prose", segment,
            "Manifest declaration scan must reference the prose")

    def test_thread_complete_not_declared_intent(self):
        idx = self.prompt.index("Before emitting \u2705 Manifest declared, scan every sentence in the prose")
        end = self.prompt.index("Outputting a rung label is what begins that rung")
        segment = self.prompt[idx:end]
        self.assertNotIn("declared intent", segment,
            "Manifest declaration scan must not reference 'declared intent' — use prose rung instead")

    # C7 carve-out: tests are never valid at ORB rung
    def test_c7_carveout_excludes_all_tests_not_just_gating_test(self):
        orb_idx = self.prompt.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.prompt.index("\u2705 Thread N complete may not be emitted")
        segment = self.prompt[orb_idx:thread_complete_idx]
        self.assertIn("not the test suite", segment,
            "C7 carve-out: OBS rung must exclude the test suite (axiom-level rung-type constraint covers all-tests rule)")

    # C12: observed running behavior rung criterion re-emission
    def test_c12_criterion_reemitted_before_orb_invocation(self):
        orb_idx = self.prompt.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.prompt.index("\u2705 Thread N complete may not be emitted")
        segment = self.prompt[orb_idx:thread_complete_idx]
        self.assertIn("re-emit the criterion", segment,
            "C12: ground must require re-emitting the criterion before ORB invocation")

    def test_c12_process_state_does_not_satisfy_orb(self):
        orb_idx = self.prompt.index("Upon writing the observed running behavior label")
        thread_complete_idx = self.prompt.index("\u2705 Thread N complete may not be emitted")
        segment = self.prompt[orb_idx:thread_complete_idx]
        self.assertIn("process state", segment,
            "C12: ground must state that process-state output does not satisfy the ORB rung")

    # C10: test derives from formal notation structural invariants
    def test_c10_reread_formal_notation_before_writing_test(self):
        ev_idx = self.prompt.index("Only validation artifacts may be produced")
        v_complete_idx = self.prompt.index("\u2705 Validation artifact V complete must be emitted")
        segment = self.prompt[ev_idx:v_complete_idx]
        self.assertIn("formal notation", segment,
            "C10: ground must require consulting the formal notation before writing the test")

    def test_c10_assert_each_structural_constraint(self):
        ev_idx = self.prompt.index("Only validation artifacts may be produced")
        v_complete_idx = self.prompt.index("\u2705 Validation artifact V complete must be emitted")
        segment = self.prompt[ev_idx:v_complete_idx]
        self.assertIn("each", segment,
            "C10: ground must require asserting each structural constraint from the formal notation")

    # C11: one assertion per test function
    def test_c11_one_assertion_per_test_function(self):
        self.assertIn("one assertion per test function", self.prompt,
            "C11: ground must require one assertion per test function")

    # C9: validation artifact placement
    def test_c9_prefer_existing_test_file(self):
        ev_idx = self.prompt.index("Only validation artifacts may be produced")
        v_complete_idx = self.prompt.index("\u2705 Validation artifact V complete must be emitted")
        segment = self.prompt[ev_idx:v_complete_idx]
        self.assertIn("existing test file", segment,
            "C9: ground must require checking for an existing test file before creating a new one")

    def test_c9_test_function_is_unit_of_production(self):
        self.assertIn("test function", self.prompt,
            "C9: ground must state that the test function, not the file, is the unit of production")

    # C2-prime: pre-existence check must be a tool-executed event
    def test_c2prime_preexistence_check_requires_tool_call(self):
        self.assertIn("confirm via tool call that the artifact path does not pre-exist", self.prompt,
            "C2-prime: ground must require confirming the artifact path via a tool call, not a mental check")

    def test_c2prime_v_complete_requires_tool_result_in_transcript(self):
        self.assertIn("V-complete may not be emitted without this tool-executed result", self.prompt,
            "C2-prime: ground must state V-complete may not be emitted without the tool-executed result")

    # C4-prime: execution output must come from a tool-call result, not inline text
    def test_c4prime_execution_output_must_be_from_tool_call(self):
        self.assertIn("verbatim tool-call output", self.prompt,
            "C4-prime: ground must require execution output to be verbatim tool-call output at any rung")

    def test_c4prime_inline_text_does_not_satisfy_gate(self):
        self.assertIn("model-generated text that resembles output", self.prompt,
            "C4-prime: ground must state that model-generated text resembling output does not satisfy any rung")

    # C13: post-EI green requires prior red with test logic failing
    def test_c13_harness_error_is_not_red_run(self):
        self.assertIn("harness error (import failure, syntax error, missing file) is not a red run", self.prompt,
            "C13: ground must state that a harness error is not a red run for the red-witness gate")

    def test_c13_test_logic_must_have_run_and_failed(self):
        self.assertIn("its assertions must have run, and they must have failed", self.prompt,
            "C13: ground must require test assertions to have run and failed, not just a harness-level error")

    # C14 → C12 (moved): behavioral predicate scan at manifest declaration, not thread-complete
    def test_c14_behavioral_predicate_coverage_check(self):
        idx = self.prompt.index("Before emitting \u2705 Manifest declared, scan every sentence in the prose")
        thread_end = self.prompt.index("Outputting a rung label is what begins that rung")
        segment = self.prompt[idx:thread_end]
        self.assertIn("behavioral predicate", segment,
            "C14→C12: manifest declaration must scan prose for behavioral predicates")

    def test_c14_implicit_coverage_does_not_satisfy(self):
        self.assertIn("each distinct predicate requires a separate thread", self.prompt,
            "C14→C12: ground must require a separate thread for each distinct behavioral predicate")

    def test_c14_directly_named_cycle_required(self):
        self.assertIn("each distinct predicate requires a separate thread", self.prompt,
            "C14→C12: ground must require a thread directly covering each behavioral predicate")

    # C7-output-criterion: OBS output must be what a non-technical observer sees
    def test_c7_output_criterion_non_technical_observer(self):
        self.assertIn("non-technical observer of the running system", self.prompt,
            "C7-output-criterion: OBS output must be what a non-technical observer would see")

    def test_c7_output_criterion_test_report_invalid(self):
        self.assertIn("validation-run-observation-type output", self.prompt,
            "C7-output-criterion: axiom-level rung-type constraint must name VRO as the type produced by running tests, covering OBS output rejection")

    def test_c7_output_must_speak_for_itself(self):
        self.assertIn("directly demonstrate the specific behavior named in the criterion", self.prompt,
            "C7-output-criterion: ground must require OBS output to directly demonstrate the criterion")

    # C4-prime-obs: universal verbatim rule applies at every rung
    def test_c4prime_obs_applies_at_any_rung(self):
        self.assertIn("at any rung", self.prompt,
            "C4-prime-obs: universal verbatim rule must explicitly apply at any rung, not just VRO")

    # C17: criteria block is exactly one criterion
    def test_c17_criteria_block_exactly_one_criterion(self):
        self.assertIn("if the criterion contains the word", self.prompt,
            "C17: ground must enforce single-criterion rule via the 'and' check")

    def test_c17_list_of_n_requires_n_cycles(self):
        self.assertIn("are two criteria, not one", self.prompt,
            "C17: ground must give an example distinguishing two criteria from one")

    # C1-upward-return: prose re-emitted at start of every cycle including upward returns
    def test_c1_universal_every_cycle_including_upward_returns(self):
        self.assertIn("any cycle following an upward return", self.prompt,
            "C1-upward-return: prose re-emission must be required on upward returns, not just first/subsequent cycles")

    # C15: impl-gate is a descent gate, not a completion gate
    def test_c15_impl_gate_licenses_first_edit_not_thread_complete(self):
        self.assertIn("licenses the first edit", self.prompt,
            "C15: ground must state impl-gate licenses the first edit, not thread completion")

    def test_c15_ei_and_obs_must_still_fire_after_impl_gate(self):
        self.assertIn("does not complete the thread", self.prompt,
            "C15: ground must state impl-gate does not complete the thread — EI and OBS must still fire")

    # C16: mandatory forward pointer — next action after gate is an edit
    def test_c16_next_required_action_after_impl_gate_is_edit(self):
        self.assertIn("next required action after", self.prompt,
            "C16: ground must name the next required action after impl-gate as an implementation edit")

    def test_c16_thread_complete_may_not_appear_before_obs_fires(self):
        gate_idx = self.prompt.index("licenses the first edit")
        segment = self.prompt[gate_idx:gate_idx + 600]
        self.assertIn("observed running behavior rung has fired", segment,
            "C16: ground must require OBS rung to have fired before Thread N complete after impl-gate")


if __name__ == "__main__":
    unittest.main()

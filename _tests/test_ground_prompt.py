"""Thread 1 validation: lib/groundPrompt.py structure and content."""
import pytest
from lib.groundPrompt import GROUND_PARTS, build_ground_prompt

EXPECTED_KEYS = ["derivation_structure", "gate_validity", "derivation_discipline", "reconciliation_and_completion"]


def test_ground_parts_has_expected_keys():
    assert list(GROUND_PARTS.keys()) == EXPECTED_KEYS


def test_ground_parts_all_nonempty():
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key].strip(), f"GROUND_PARTS['{key}'] is empty"


def test_build_ground_prompt_joins_all_parts():
    result = build_ground_prompt()
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key] in result


def test_build_ground_prompt_is_space_joined():
    result = build_ground_prompt()
    assert result == " ".join(GROUND_PARTS[k] for k in EXPECTED_KEYS)


def test_derivation_structure_content():
    assert "I is the declared intent" in GROUND_PARTS["derivation_structure"]


def test_observed_running_behavior_excludes_preview():
    ds = GROUND_PARTS["derivation_structure"]
    assert "screenshot" in ds or "preview" in ds or "preview panel" in ds, (
        "derivation_structure must name screenshot/preview as insufficient for observed running behavior"
    )
    assert "specific behavior" in ds or "declared gap" in ds, (
        "derivation_structure must require observation to reference the specific behavior declared in the gap"
    )


def test_observed_running_behavior_requires_traceability():
    ds = GROUND_PARTS["derivation_structure"]
    assert "traceable" in ds or "traceability" in ds or "behavioral gap" in ds, (
        "derivation_structure must require observed running behavior to be traceable to the declared gap"
    )
    assert "server response" in ds or "HTTP" in ds or "URL" in ds or "rendering" in ds, (
        "derivation_structure must name domain-specific anti-patterns for observed running behavior"
    )


def test_rung_label_mandatory_at_every_transition():
    ds = GROUND_PARTS["derivation_structure"]
    assert "must be emitted" in ds or "must appear" in ds or "required at every" in ds, (
        "derivation_structure must mandate a rung label at every rung transition"
    )
    assert "absence" in ds and ("violation" in ds or "invalid" in ds), (
        "derivation_structure must state that absence of a rung label is a violation"
    )


def test_r2_audit_gate():
    ds = GROUND_PARTS["derivation_structure"]
    assert "audit" in ds or "enumerate" in ds, (
        "derivation_structure must require an explicit R2 audit before advancing from formal notation"
    )
    assert "incomplete" in ds or "unencoded" in ds, (
        "derivation_structure must state the rung is incomplete until all criteria are encoded"
    )


def test_formal_notation_r2_requirement():
    ds = GROUND_PARTS["derivation_structure"]
    assert "Formal notation must satisfy R2" in ds, (
        "derivation_structure must state that formal notation must satisfy R2"
    )
    assert "behavioral constraint" in ds, (
        "derivation_structure must mention behavioral constraints for formal notation"
    )
    assert "interface shape" in ds or "structure without encoding invariants" in ds, (
        "derivation_structure must distinguish shape-only notation from complete notation"
    )


def test_i_formation_sentinel():
    ds = GROUND_PARTS["derivation_structure"]
    assert "I-formation complete" in ds, (
        "derivation_structure must define a sentinel for I-formation completion"
    )
    assert "manifest may not appear" in ds or "before the" in ds, (
        "derivation_structure must state the manifest may not appear before the I-formation sentinel"
    )


def test_i_formation_causal_chain():
    ds = GROUND_PARTS["derivation_structure"]
    assert "assumed" in ds or "actual constraints" in ds, (
        "derivation_structure must explain that skipping I-formation derives from assumed rather than actual constraints"
    )
    assert "discarded" in ds or "must be discarded" in ds, (
        "derivation_structure must state that artifacts derived from skipped I-formation must be discarded"
    )


def test_i_formation_is_required_not_permitted():
    ds = GROUND_PARTS["derivation_structure"]
    assert "required" in ds and "I cannot be declared from context alone" in ds, (
        "derivation_structure must state that I-formation is required when context is insufficient"
    )
    assert "error" in ds or "skipping" in ds.lower(), (
        "derivation_structure must name skipping I-formation when context is insufficient as an error"
    )
    assert "permitted" not in ds or ds.index("required") < ds.index("permitted") + 100, (
        "I-formation must be framed as required, not merely permitted"
    )


def test_self_check_before_advancing_executable_rung():
    gv = GROUND_PARTS["gate_validity"]
    assert "before advancing" in gv, (
        "gate_validity must require explicit self-verification before advancing past an executable rung"
    )
    assert "incomplete" in gv, (
        "gate_validity must state the rung is incomplete if self-check conditions are unmet"
    )


def test_build_error_excluded_from_gate():
    gv = GROUND_PARTS["gate_validity"]
    assert "build" in gv or "compile" in gv or "import error" in gv, (
        "gate_validity must explicitly exclude build/compile errors from satisfying the validation gate"
    )
    assert "incomplete" in gv, (
        "gate_validity must state that a build failure means the validation artifact is incomplete"
    )


def test_sentinel_causal_chain():
    gv = GROUND_PARTS["gate_validity"]
    assert "anticipated" in gv, (
        "gate_validity must explain that a composed sentinel records anticipated rather than observed state"
    )
    assert "regardless" in gv and ("correct" in gv or "accuracy" in gv), (
        "gate_validity must state that artifacts from a composed sentinel are invalid regardless of correctness"
    )


def test_gate_validity_content():
    assert "conversation-state condition" in GROUND_PARTS["gate_validity"]


def test_v_complete_requires_green_gate_before_implementation():
    gv = GROUND_PARTS["gate_validity"]
    assert "both" in gv or "then" in gv.lower() and "Implementation gate cleared" in gv, (
        "gate_validity must state both V-complete and 🟢 are required in order before implementation"
    )
    assert "does not open" in gv or "insufficient" in gv or ("alone" in gv and "gate" in gv), (
        "gate_validity must state V-complete alone does not open the implementation gate"
    )


def test_v_complete_sentinel_position():
    gv = GROUND_PARTS["gate_validity"]
    assert "before" in gv and "implementation" in gv, (
        "gate_validity must state V-complete appears before implementation begins"
    )
    assert "after tests pass" in gv or "not after" in gv or "may not appear after" in gv, (
        "gate_validity must explicitly state V-complete may not appear after tests pass"
    )


def test_gate_validity_passing_run_is_gap_signal():
    gv = GROUND_PARTS["gate_validity"]
    assert "vacuous" in gv, (
        "gate_validity must state that a passing run without observed failure may be vacuous"
    )
    assert "gap signal" in gv, (
        "gate_validity must name a passing run without prior failure as a gap signal"
    )


def test_derivation_discipline_content():
    assert "Gap-locality" in GROUND_PARTS["derivation_discipline"]


def test_test_reduction_is_scope_violation():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "reducing" in dd or "reduction" in dd or "deleting" in dd or "fewer tests" in dd, (
        "derivation_discipline must name test reduction as a scope violation"
    )
    assert "gap signal" in dd or "gap signal" in GROUND_PARTS["gate_validity"], (
        "prompt must state a passing suite with fewer tests than the gap requires is a gap signal"
    )


def test_minimal_scope_extends_to_post_ladder():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "entire invocation" in dd or "post-ladder" in dd or "after the ladder" in dd, (
        "derivation_discipline must extend minimal scope to the entire invocation, including post-ladder additions"
    )
    assert "new" in dd and ("manifest" in dd or "descent" in dd), (
        "derivation_discipline must require post-completion additions not in I to have their own manifest"
    )


def test_upward_correction_causal_chain():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "resurface" in dd or "deficiency" in dd, (
        "derivation_discipline must explain that an uncorrected deficiency resurfaces at every rung below"
    )


def test_upward_correction_requires_observation_before_loop():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "before correcting" in dd, (
        "derivation_discipline must require emitting the observation before correcting any higher rung"
    )
    assert "observation record is invalid" in dd, (
        "derivation_discipline must state that corrections without an observation record are invalid"
    )


def test_r3_requires_red_sentinels():
    ds = GROUND_PARTS["derivation_structure"]
    gv = GROUND_PARTS["gate_validity"]
    # R3 sentinel requirement: derivation_structure must state observed running behavior
    # requires 🔴 sentinels, and gap must name behavior from I
    assert "observed running behavior" in ds and (
        "Execution observed" in ds or "\U0001F534" in ds
    ), (
        "derivation_structure must require 🔴 Execution observed at the observed running behavior rung"
    )
    assert "behavior from I" in ds or ("behavior" in ds and "from I" in ds), (
        "derivation_structure must require R3 gap to name the specific behavior from I"
    )


def test_prior_failure_scoped_to_test():
    gv = GROUND_PARTS["gate_validity"]
    assert ("individual test" in gv or "specific test" in gv) and "produced it" in gv, (
        "gate_validity must state prior recorded failure applies to the specific test that produced it"
    )
    assert "carry-forward" in gv or "carry forward" in gv, (
        "gate_validity must require a carry-forward statement after validation artifact modification"
    )
    assert "uncovered" in gv or "no covering" in gv, (
        "gate_validity must state uncovered tests trigger the vacuous-green check"
    )


def test_r2_audit_separate_section():
    ds = GROUND_PARTS["derivation_structure"]
    assert "separate" in ds and "section" in ds, (
        "derivation_structure must state the R2 audit is a separate named section"
    )
    assert "numbered" in ds, (
        "derivation_structure must require each criterion on a numbered row"
    )
    assert "prose" in ds and ("not satisfy" in ds or "does not satisfy" in ds), (
        "derivation_structure must state a prose list does not satisfy the R2 audit"
    )


def test_execution_observed_block_delimiter():
    gv = GROUND_PARTS["gate_validity"]
    assert "complete" in gv and ("block" in gv or "```" in gv or "triple" in gv or "delimit" in gv), (
        "gate_validity must require 🔴 Execution observed to contain a complete delimited block"
    )
    assert "nothing omitted" in gv or "complete output" in gv or "complete tool output" in gv, (
        "gate_validity must state the block contains the complete tool output — nothing omitted"
    )


def test_vacuous_green_unconditional():
    gv = GROUND_PARTS["gate_validity"]
    assert "recorded" in gv and ("failure" in gv or "failed" in gv), (
        "gate_validity must require prior recorded failure in this conversation before a green run is accepted"
    )


def test_self_check_requires_citation():
    gv = GROUND_PARTS["gate_validity"]
    self_check_idx = gv.find("Self-check")
    assert self_check_idx >= 0, "gate_validity must contain a Self-check section"
    # Isolate text from Self-check to end of its sentence block (up to next sentinel or end)
    self_check_text = gv[self_check_idx:self_check_idx + 500]
    assert "quot" in self_check_text or "cannot be located" in self_check_text or "from this conversation" in self_check_text, (
        "gate_validity self-check must require citing sentinels from this conversation, not asserting from memory"
    )


def test_r3_behavioral_specificity():
    ds = GROUND_PARTS["derivation_structure"]
    assert "build" in ds or "system-state" in ds or "system state" in ds, (
        "derivation_structure must exclude build success and system-state events from R3 observation"
    )


def test_validation_artifact_freeze():
    dd = GROUND_PARTS["derivation_discipline"]
    assert "modif" in dd or "frozen" in dd, (
        "derivation_discipline must state that post-declaration modification of the validation artifact requires upward correction"
    )
    assert "mock" in dd or "simplif" in dd or "weaken" in dd, (
        "derivation_discipline must name mock weakening or simplification as a prohibited modification form"
    )


def test_execution_observed_raw_only():
    gv = GROUND_PARTS["gate_validity"]
    assert "no prose" in gv or "only the raw" in gv or "contains only" in gv, (
        "gate_validity must state that 🔴 Execution observed contains only raw tool output"
    )
    assert "interpretation" in gv and "Gap" in gv, (
        "gate_validity must locate interpretation exclusively in the 🔴 Gap line"
    )


def test_r2_audit_checklist_format():
    ds = GROUND_PARTS["derivation_structure"]
    assert "✅ Formal notation R2 audit complete" in ds, (
        "derivation_structure must define the R2 audit completion sentinel"
    )
    assert "UNENCODED" in ds, (
        "derivation_structure must name UNENCODED as the marker for unencodeable criteria"
    )


def test_reconciliation_content():
    assert "Intent precedes its representations" in GROUND_PARTS["reconciliation_and_completion"]


def test_r3_requires_declared_behavior_in_output():
    ds = GROUND_PARTS["derivation_structure"]
    assert "named in the gap" in ds or "by name" in ds or "output content" in ds or "verifiable" in ds, (
        "derivation_structure must state R3 validity depends on output content naming declared behavior — "
        "the specific behavior named in the gap must appear as a verifiable event in the output"
    )
    assert "route loads" in ds or "infrastructure state" in ds, (
        "derivation_structure must name infrastructure-state outputs (e.g., 'route loads') as insufficient for R3"
    )


def test_carry_forward_scope_behavioral_only():
    gv = GROUND_PARTS["gate_validity"]
    assert "import" in gv or "structural" in gv or "assertion" in gv, (
        "gate_validity must clarify carry-forward scope — behavioral changes vs. import/structural corrections"
    )
    cf_idx = gv.find("carry-forward") if "carry-forward" in gv else gv.find("carry forward")
    cf_context = gv[max(0, cf_idx - 100):cf_idx + 500]
    assert "import" in cf_context or "assertion" in cf_context or "behavioral" in cf_context, (
        "gate_validity must name the carry-forward scope near the carry-forward requirement"
    )


def test_r2_audit_must_begin_with_1():
    ds = GROUND_PARTS["derivation_structure"]
    assert "begin with" in ds or "begins with" in ds or "start with" in ds or "starts with '1.'" in ds, (
        "derivation_structure must state the R2 audit must begin with '1.' on the first row"
    )
    assert "1." in ds and ("begin with" in ds or "starts with" in ds), (
        "derivation_structure must explicitly name '1.' as the required start of the audit"
    )


def test_retroactive_sentinel_does_not_open_gate():
    gv = GROUND_PARTS["gate_validity"]
    assert "retroact" in gv or "re-run" in gv or "rerun" in gv, (
        "gate_validity must state that a retroactive sentinel leaves the gate closed and the tool must be re-run"
    )
    # Verify the re-run / gate-closed consequence is linked to retroactive labeling
    retro_idx = gv.find("retroact") if "retroact" in gv else gv.find("re-run")
    context = gv[max(0, retro_idx - 50):retro_idx + 350]
    assert "gate" in context or "re-run" in context or "closed" in context, (
        "gate_validity must state the gate consequence of retroactive sentinel — gate does not open"
    )


def test_manifest_must_include_vro():
    ds = GROUND_PARTS["derivation_structure"]
    assert "must name every" in ds or "must include every" in ds or "must list every" in ds, (
        "derivation_structure must state the manifest must name every R4 rung"
    )
    assert "malformed" in ds or "omitting" in ds, (
        "derivation_structure must state that omitting a required rung from the manifest is malformed"
    )


def test_r3_positive_definition_for_code_contexts():
    ds = GROUND_PARTS["derivation_structure"]
    assert "rendered" in ds or "DOM" in ds or "api response" in ds.lower() or "response body" in ds, (
        "derivation_structure must give a positive definition of what satisfies R3 in code contexts "
        "(e.g., rendered DOM content, API response body)"
    )
    assert "direct" in ds or "directly" in ds or "demonstrates" in ds, (
        "derivation_structure must require the R3 output to directly demonstrate the declared feature"
    )


def test_carry_forward_is_a_gate():
    gv = GROUND_PARTS["gate_validity"]
    assert "no implementation" in gv and ("carry-forward" in gv or "carry forward" in gv), (
        "gate_validity must state that no implementation artifact may appear until carry-forward is emitted "
        "after validation artifact modification"
    )
    cf_idx = gv.find("carry-forward") if "carry-forward" in gv else gv.find("carry forward")
    # Find the gate language near the carry-forward requirement
    cf_context = gv[max(0, cf_idx - 200):cf_idx + 600]
    assert "gate" in cf_context or "violation" in cf_context or "blocked" in cf_context or "no implementation" in cf_context, (
        "gate_validity must frame carry-forward as a gate/violation, not merely an emission requirement"
    )


def test_r2_audit_only_two_valid_outcomes():
    ds = GROUND_PARTS["derivation_structure"]
    assert "no other resolution" in ds or "only two valid" in ds or "only valid row" in ds, (
        "derivation_structure must state the R2 audit has exactly two valid row outcomes — no other resolution"
    )
    assert "architectural constraint" in ds or "constraint type" in ds or "names constraint" in ds, (
        "derivation_structure must name that a constraint-type label is UNENCODED, not a behavioral invariant"
    )


def test_obr_is_observation_not_production():
    ds = GROUND_PARTS["derivation_structure"]
    # OBR is an observation rung — no new files may be created there
    assert "observation" in ds or "observe" in ds, (
        "derivation_structure must state OBR is an observation rung"
    )
    obr_idx = ds.rfind("observed running behavior")
    assert obr_idx >= 0, "derivation_structure must mention observed running behavior"
    # Find the OBR description near the end (last occurrence is in the R4 sequence)
    context = ds[max(0, obr_idx - 100):obr_idx + 500]
    assert "no new" in context or "not a production" in context or "new file" in context or "new artifact" in context, (
        "derivation_structure must state no new files may be created at the OBR rung"
    )


def test_manifest_thread_count_bounds_emissions():
    rc = GROUND_PARTS["reconciliation_and_completion"]
    # The manifest thread count must bound ✅ Thread N complete emissions
    assert "declared" in rc or "count" in rc or "exact" in rc or "bound" in rc, (
        "reconciliation_and_completion must state the declared thread count bounds emissions"
    )
    assert "Thread" in rc and ("complete" in rc or "sentinels" in rc), (
        "reconciliation_and_completion must reference Thread N complete sentinels"
    )
    thread_idx = rc.find("Thread")
    context = rc[max(0, thread_idx - 100):thread_idx + 400]
    assert "declared" in context or "count" in context or "exact" in context or "bound" in context, (
        "reconciliation_and_completion must bind thread emissions to declared count near Thread sentinel text"
    )


def test_compile_error_records_zero_prior_failures():
    gv = GROUND_PARTS["gate_validity"]
    # A compile/import error must not be treated as prior failure coverage for any test
    assert "compile" in gv or "import error" in gv, (
        "gate_validity must address compile/import errors in the context of prior failure coverage"
    )
    compile_idx = gv.find("compile") if "compile" in gv else gv.find("import error")
    context = gv[max(0, compile_idx - 100):compile_idx + 400]
    assert "zero" in context or "no test" in context or "no prior" in context or "uncovered" in context, (
        "gate_validity must state that a compile error records zero prior failures — "
        "no test executed, so no test has a prior failure"
    )


def test_compile_then_pass_triggers_vacuous_green():
    gv = GROUND_PARTS["gate_validity"]
    # After a compile error is corrected and tests pass, every test is uncovered
    assert "compile" in gv, "gate_validity must address compile errors"
    compile_idx = gv.find("compile")
    context = gv[max(0, compile_idx - 100):compile_idx + 600]
    assert "uncovered" in context or "vacuous" in context or "all tests" in context, (
        "gate_validity must state that a compile-then-pass sequence leaves all tests uncovered, "
        "requiring the vacuous-green check for each"
    )


def test_sentinel_must_precede_tool_invocation():
    gv = GROUND_PARTS["gate_validity"]
    assert "retroactively" in gv or "before its sentinel" in gv or "immediately before the tool" in gv, (
        "gate_validity must state the sentinel appears immediately before the tool is invoked "
        "and tool output appearing before its sentinel is uncovered — retroactive labeling is invalid"
    )


def test_assertion_modification_direction_independent():
    dd = GROUND_PARTS["derivation_discipline"]
    # The frozen-artifact rule must cover direction-independent modifications —
    # changing assertions to match implementation must be named as a scope violation
    assert "conform" in dd or "match" in dd or "redefine" in dd or "direction" in dd, (
        "derivation_discipline must state that modifying assertions to match implementation "
        "redefines the gap contract — direction of change is irrelevant"
    )
    assert "gap contract" in dd or "contract" in dd or "epistemological" in dd, (
        "derivation_discipline must name the epistemological error: using model knowledge "
        "of implementation to define the gap"
    )


def test_composed_prose_body_always_invalid():
    gv = GROUND_PARTS["gate_validity"]
    # A prose description of tool output — even accurate — is always composed content
    assert "characterization" in gv or "description of tool output" in gv or "prose description" in gv, (
        "gate_validity must state that a prose description of tool output is always composed content"
    )
    assert "even if accurate" in gv or "regardless of whether" in gv or "even accurate" in gv, (
        "gate_validity must state the rule is not conditioned on accuracy of the description"
    )


def test_sentinel_is_prospective_commitment_not_label():
    gv = GROUND_PARTS["gate_validity"]
    # The sentinel's function is prospective capture before interpretation, not retrospective labeling.
    # Placing a sentinel after tool output has appeared redefines a conversation event as composed content —
    # the same epistemological error as a prose description of output.
    assert "prospective" in gv or "before interpretation" in gv or "commitment" in gv, (
        "gate_validity must state the sentinel is a prospective commitment — its function is to capture "
        "output before interpretation occurs, not to label output already seen"
    )
    retro_idx = gv.find("retroact") if "retroact" in gv else -1
    assert retro_idx >= 0, "gate_validity must contain retroactive sentinel language"
    context = gv[max(0, retro_idx - 200):retro_idx + 600]
    assert "interpret" in context or "composed" in context or "epistemological" in context, (
        "gate_validity must name placing a sentinel after output as the same epistemological error "
        "as composing a prose description — already interpreted, not captured"
    )


def test_self_check_requires_temporal_precedence():
    gv = GROUND_PARTS["gate_validity"]
    self_check_idx = gv.find("Self-check")
    assert self_check_idx >= 0, "gate_validity must contain a Self-check section"
    self_check_text = gv[self_check_idx:self_check_idx + 700]
    # The self-check must require confirming the sentinel appears BEFORE the tool output,
    # not merely that it can be "located" anywhere in the conversation.
    assert (
        "before the tool" in self_check_text
        or "precedes" in self_check_text
        or "appears before" in self_check_text
        or "before tool output" in self_check_text
        or "appears after" in self_check_text
    ), (
        "gate_validity self-check must require confirming the sentinel precedes the tool invocation — "
        "locating it anywhere in the conversation is insufficient; a sentinel after tool output is not located"
    )


def test_structural_correction_has_concrete_predicate_test():
    dd = GROUND_PARTS["derivation_discipline"]
    structural_idx = dd.find("structural correction")
    assert structural_idx >= 0, "derivation_discipline must mention structural correction"
    context = dd[max(0, structural_idx - 100):structural_idx + 800]
    # Must give an operational test for predicate identity —
    # not just "predicate identical" but what makes predicates the same.
    assert "behaviors" in context or "same observable" in context or "which behaviors" in context, (
        "derivation_discipline must state the operational test for structural correction: "
        "whether the set of component behaviors that would cause the assertion to fail is unchanged"
    )


def test_manifest_enumerates_seven_canonical_rung_names():
    ds = GROUND_PARTS["derivation_structure"]
    # The manifest rule must enumerate the seven canonical rung names
    # and state that collapsing VRO into an adjacent rung is malformed
    assert "seven" in ds or "collapses" in ds or "collapse" in ds, (
        "derivation_structure must enumerate the seven canonical rung names in the manifest rule "
        "and state that collapsing VRO into an adjacent rung is malformed"
    )

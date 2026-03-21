"""Thread 1 validation: lib/groundPrompt.py structure and content (ADR-0172)."""
import pytest
from lib.groundPrompt import GROUND_PARTS, build_ground_prompt

EXPECTED_KEYS = ["epistemological_protocol", "sentinel_rules", "rung_sequence_code", "reconciliation_and_completion"]

# Domain aliases — update here if keys change; behavioral assertions below are stable.
EP  = lambda: GROUND_PARTS["epistemological_protocol"]   # Rule 0, primitives, scope discipline
SR  = lambda: GROUND_PARTS["sentinel_rules"]              # Gate mechanics, sentinels, carry-forward
RSC = lambda: GROUND_PARTS["rung_sequence_code"]          # R4 sequence, rung-level rules
RC  = lambda: GROUND_PARTS["reconciliation_and_completion"]


def test_ground_parts_has_expected_keys():
    assert list(GROUND_PARTS.keys()) == EXPECTED_KEYS


def test_ground_parts_all_nonempty():
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key].strip(), f"GROUND_PARTS['{key}'] is empty"


def test_build_ground_prompt_joins_all_parts():
    result = build_ground_prompt()
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key] in result


def test_build_ground_prompt_contains_all_parts():
    result = build_ground_prompt()
    for key in EXPECTED_KEYS:
        assert GROUND_PARTS[key] in result


def test_section_headers_present_in_prompt():
    result = build_ground_prompt()
    assert "\u2500\u2500 PROTOCOL \u2500\u2500" in result
    assert "\u2500\u2500 GATES \u2500\u2500" in result
    assert "\u2500\u2500 STRUCTURE \u2500\u2500" in result
    assert "\u2500\u2500 COMPLETION \u2500\u2500" in result


def test_section_headers_precede_parts():
    result = build_ground_prompt()
    label_map = {
        "epistemological_protocol": "\u2500\u2500 PROTOCOL \u2500\u2500",
        "sentinel_rules": "\u2500\u2500 GATES \u2500\u2500",
        "rung_sequence_code": "\u2500\u2500 STRUCTURE \u2500\u2500",
        "reconciliation_and_completion": "\u2500\u2500 COMPLETION \u2500\u2500",
    }
    for key, label in label_map.items():
        label_pos = result.index(label)
        part_pos = result.index(GROUND_PARTS[key])
        assert label_pos < part_pos, f"Header '{label}' must precede GROUND_PARTS['{key}']"


def test_section_headers_canonical_order():
    result = build_ground_prompt()
    pos_protocol   = result.index("\u2500\u2500 PROTOCOL \u2500\u2500")
    pos_gates      = result.index("\u2500\u2500 GATES \u2500\u2500")
    pos_structure  = result.index("\u2500\u2500 STRUCTURE \u2500\u2500")
    pos_completion = result.index("\u2500\u2500 COMPLETION \u2500\u2500")
    assert pos_protocol < pos_gates < pos_structure < pos_completion


def test_derivation_structure_content():
    assert "I is the declared intent" in EP()


def test_observed_running_behavior_excludes_preview():
    rsc = RSC()
    assert "screenshot" in rsc or "preview" in rsc or "preview panel" in rsc, (
        "rung_sequence_code must name screenshot/preview as insufficient for observed running behavior"
    )
    assert "specific behavior" in rsc or "declared gap" in rsc, (
        "rung_sequence_code must require observation to reference the specific behavior declared in the gap"
    )


def test_observed_running_behavior_requires_traceability():
    rsc = RSC()
    assert "traceable" in rsc or "traceability" in rsc or "behavioral gap" in rsc, (
        "rung_sequence_code must require observed running behavior to be traceable to the declared gap"
    )
    assert "server response" in rsc or "HTTP" in rsc or "URL" in rsc or "rendering" in rsc, (
        "rung_sequence_code must name domain-specific anti-patterns for observed running behavior"
    )


def test_rung_label_mandatory_at_every_transition():
    ep = EP()
    assert "must be emitted" in ep or "must appear" in ep or "required at every" in ep, (
        "epistemological_protocol must mandate a rung label at every rung transition"
    )
    assert "absence" in ep and ("violation" in ep or "invalid" in ep), (
        "epistemological_protocol must state that absence of a rung label is a violation"
    )


def test_r2_audit_gate():
    rsc = RSC()
    assert "audit" in rsc or "enumerate" in rsc, (
        "rung_sequence_code must require an explicit R2 audit before advancing from formal notation"
    )
    assert "incomplete" in rsc or "unencoded" in rsc.lower(), (
        "rung_sequence_code must state the rung is incomplete until all criteria are encoded"
    )


def test_formal_notation_r2_requirement():
    rsc = RSC()
    assert "Formal notation must satisfy R2" in rsc, (
        "rung_sequence_code must state that formal notation must satisfy R2"
    )
    assert "behavioral constraint" in rsc or "behavioral invariant" in rsc, (
        "rung_sequence_code must mention behavioral constraints for formal notation"
    )
    assert "interface shape" in rsc or "structure without encoding invariants" in rsc, (
        "rung_sequence_code must distinguish shape-only notation from complete notation"
    )


def test_i_formation_sentinel():
    rsc = RSC()
    assert "I-formation complete" in rsc, (
        "rung_sequence_code must define a sentinel for I-formation completion"
    )
    assert "manifest may not appear" in rsc or "before the" in rsc, (
        "rung_sequence_code must state the manifest may not appear before the I-formation sentinel"
    )


def test_i_formation_causal_chain():
    rsc = RSC()
    assert "assumed" in rsc or "actual constraints" in rsc, (
        "rung_sequence_code must explain that skipping I-formation derives from assumed rather than actual constraints"
    )
    assert "discarded" in rsc or "must be discarded" in rsc, (
        "rung_sequence_code must state that artifacts derived from skipped I-formation must be discarded"
    )


def test_i_formation_is_required_not_permitted():
    rsc = RSC()
    assert "required" in rsc and "I cannot be declared from context alone" in rsc, (
        "rung_sequence_code must state that I-formation is required when context is insufficient"
    )
    assert "error" in rsc or "skipping" in rsc.lower(), (
        "rung_sequence_code must name skipping I-formation when context is insufficient as an error"
    )


def test_self_check_before_advancing_executable_rung():
    sr = SR()
    assert "before advancing" in sr, (
        "sentinel_rules must require explicit self-verification before advancing past an executable rung"
    )
    assert "incomplete" in sr, (
        "sentinel_rules must state the rung is incomplete if self-check conditions are unmet"
    )


def test_build_error_excluded_from_gate():
    sr = SR()
    assert "build" in sr or "compile" in sr or "import error" in sr, (
        "sentinel_rules must explicitly exclude build/compile errors from satisfying the validation gate"
    )
    assert "incomplete" in sr, (
        "sentinel_rules must state that a build failure means the validation artifact is incomplete"
    )


def test_sentinel_causal_chain():
    sr = SR()
    assert "anticipated" in sr, (
        "sentinel_rules must explain that a composed sentinel records anticipated rather than observed state"
    )
    assert "regardless" in sr and ("correct" in sr or "accuracy" in sr), (
        "sentinel_rules must state that artifacts from a composed sentinel are invalid regardless of correctness"
    )


def test_gate_validity_content():
    assert "conversation-state condition" in SR()


def test_v_complete_requires_green_gate_before_implementation():
    sr = SR()
    assert "both" in sr or ("then" in sr.lower() and "Implementation gate cleared" in sr), (
        "sentinel_rules must state both V-complete and 🟢 are required in order before implementation"
    )
    assert "does not open" in sr or "insufficient" in sr or ("alone" in sr and "gate" in sr), (
        "sentinel_rules must state V-complete alone does not open the implementation gate"
    )


def test_v_complete_sentinel_position():
    sr = SR()
    assert "before" in sr and "implementation" in sr, (
        "sentinel_rules must state V-complete appears before implementation begins"
    )
    assert "after tests pass" in sr or "not after" in sr or "may not appear after" in sr, (
        "sentinel_rules must explicitly state V-complete may not appear after tests pass"
    )


def test_gate_validity_passing_run_is_gap_signal():
    sr = SR()
    assert "vacuous" in sr, (
        "sentinel_rules must state that a passing run without observed failure may be vacuous"
    )
    assert "gap signal" in sr, (
        "sentinel_rules must name a passing run without prior failure as a gap signal"
    )


def test_derivation_discipline_content():
    assert "Gap-locality" in EP()


def test_test_reduction_is_scope_violation():
    ep = EP()
    assert "reducing" in ep or "reduction" in ep or "deleting" in ep or "fewer tests" in ep, (
        "epistemological_protocol must name test reduction as a scope violation"
    )
    assert "gap signal" in ep or "gap signal" in SR(), (
        "prompt must state a passing suite with fewer tests than the gap requires is a gap signal"
    )


def test_minimal_scope_extends_to_post_ladder():
    ep = EP()
    assert "entire invocation" in ep or "post-ladder" in ep or "after the ladder" in ep, (
        "epistemological_protocol must extend minimal scope to the entire invocation, including post-ladder additions"
    )
    assert "new" in ep and ("manifest" in ep or "descent" in ep), (
        "epistemological_protocol must require post-completion additions not in I to have their own manifest"
    )


def test_upward_correction_causal_chain():
    ep = EP()
    assert "resurface" in ep or "deficiency" in ep, (
        "epistemological_protocol must explain that an uncorrected deficiency resurfaces at every rung below"
    )


def test_upward_correction_requires_observation_before_loop():
    ep = EP()
    assert "before correcting" in ep, (
        "epistemological_protocol must require emitting the observation before correcting any higher rung"
    )
    assert "observation record is invalid" in ep, (
        "epistemological_protocol must state that corrections without an observation record are invalid"
    )


def test_r2_audit_separate_section():
    rsc = RSC()
    assert "separate" in rsc and "section" in rsc, (
        "rung_sequence_code must state the R2 audit is a separate named section"
    )
    assert "numbered" in rsc, (
        "rung_sequence_code must require each criterion on a numbered row"
    )
    assert "prose" in rsc and ("not satisfy" in rsc or "does not satisfy" in rsc), (
        "rung_sequence_code must state a prose list does not satisfy the R2 audit"
    )


def test_execution_observed_block_delimiter():
    sr = SR()
    assert "complete" in sr and ("block" in sr or "```" in sr or "triple" in sr or "delimit" in sr), (
        "sentinel_rules must require 🔴 Execution observed to contain a complete delimited block"
    )
    assert "nothing omitted" in sr or "complete output" in sr or "complete tool output" in sr, (
        "sentinel_rules must state the block contains the complete tool output — nothing omitted"
    )


def test_vacuous_green_unconditional():
    sr = SR()
    assert "recorded" in sr and ("failure" in sr or "failed" in sr), (
        "sentinel_rules must require prior recorded failure in this conversation before a green run is accepted"
    )


def test_self_check_requires_citation():
    sr = SR()
    self_check_idx = sr.find("Self-check")
    assert self_check_idx >= 0, "sentinel_rules must contain a Self-check section"
    self_check_text = sr[self_check_idx:self_check_idx + 500]
    assert "quot" in self_check_text or "cannot be located" in self_check_text or "from this conversation" in self_check_text, (
        "sentinel_rules self-check must require citing sentinels from this conversation, not asserting from memory"
    )


def test_r3_behavioral_specificity():
    ep = EP()
    assert "build" in ep or "system-state" in ep or "system state" in ep, (
        "epistemological_protocol must exclude build success and system-state events from R3 observation"
    )


def test_validation_artifact_freeze():
    ep = EP()
    assert "modif" in ep or "frozen" in ep, (
        "epistemological_protocol must state that post-declaration modification of the validation artifact requires upward correction"
    )
    assert "mock" in ep or "simplif" in ep or "weaken" in ep, (
        "epistemological_protocol must name mock weakening or simplification as a prohibited modification form"
    )


def test_execution_observed_raw_only():
    sr = SR()
    assert "no prose" in sr or "only the raw" in sr or "contains only" in sr or "characterization" in sr, (
        "sentinel_rules must state that 🔴 Execution observed contains only raw tool output"
    )
    assert "interpretation" in sr and "Gap" in sr, (
        "sentinel_rules must locate interpretation exclusively in the 🔴 Gap line"
    )


def test_r2_audit_checklist_format():
    rsc = RSC()
    assert "\u2705 Formal notation R2 audit complete" in rsc, (
        "rung_sequence_code must define the R2 audit completion sentinel"
    )
    assert "UNENCODED" in rsc, (
        "rung_sequence_code must name UNENCODED as the marker for unencodeable criteria"
    )


def test_reconciliation_content():
    assert "Intent precedes its representations" in RC()


def test_r3_requires_declared_behavior_in_output():
    rsc = RSC()
    assert "named in the gap" in rsc or "by name" in rsc or "output content" in rsc or "verifiable" in rsc, (
        "rung_sequence_code must state R3 validity depends on output content naming declared behavior"
    )
    assert "route loads" in rsc or "infrastructure state" in rsc, (
        "rung_sequence_code must name infrastructure-state outputs as insufficient for R3"
    )


def test_carry_forward_scope_behavioral_only():
    sr = SR()
    assert "import" in sr or "structural" in sr or "assertion" in sr, (
        "sentinel_rules must clarify carry-forward scope — behavioral changes vs. import/structural corrections"
    )
    cf_idx = sr.find("carry-forward") if "carry-forward" in sr else sr.find("carry forward")
    cf_context = sr[max(0, cf_idx - 100):cf_idx + 500]
    assert "import" in cf_context or "assertion" in cf_context or "behavioral" in cf_context, (
        "sentinel_rules must name the carry-forward scope near the carry-forward requirement"
    )


def test_r2_audit_must_begin_with_1():
    rsc = RSC()
    assert "begin with" in rsc or "begins with" in rsc or "start with" in rsc or "starts with '1.'" in rsc, (
        "rung_sequence_code must state the R2 audit must begin with '1.' on the first row"
    )
    assert "1." in rsc and ("begin with" in rsc or "starts with" in rsc), (
        "rung_sequence_code must explicitly name '1.' as the required start of the audit"
    )


def test_retroactive_sentinel_does_not_open_gate():
    sr = SR()
    assert "retroact" in sr or "re-run" in sr or "rerun" in sr, (
        "sentinel_rules must state that a retroactive sentinel leaves the gate closed and the tool must be re-run"
    )
    retro_idx = sr.find("retroact") if "retroact" in sr else sr.find("re-run")
    context = sr[max(0, retro_idx - 50):retro_idx + 350]
    assert "gate" in context or "re-run" in context or "closed" in context, (
        "sentinel_rules must state the gate consequence of retroactive sentinel — gate does not open"
    )


def test_manifest_must_include_vro():
    ep = EP()
    assert "must name every" in ep or "must include every" in ep or "must list every" in ep, (
        "epistemological_protocol must state the manifest must name every R4 rung"
    )
    assert "malformed" in ep or "omitting" in ep, (
        "epistemological_protocol must state that omitting a required rung from the manifest is malformed"
    )


def test_r3_positive_definition_for_code_contexts():
    rsc = RSC()
    assert "rendered" in rsc or "DOM" in rsc or "api response" in rsc.lower() or "response body" in rsc, (
        "rung_sequence_code must give a positive definition of what satisfies R3 in code contexts"
    )
    assert "direct" in rsc or "directly" in rsc or "demonstrates" in rsc, (
        "rung_sequence_code must require the R3 output to directly demonstrate the declared feature"
    )


def test_carry_forward_is_a_gate():
    sr = SR()
    assert "no implementation" in sr and ("carry-forward" in sr or "carry forward" in sr), (
        "sentinel_rules must state that no implementation artifact may appear until carry-forward is emitted"
    )
    cf_idx = sr.find("carry-forward") if "carry-forward" in sr else sr.find("carry forward")
    cf_context = sr[max(0, cf_idx - 200):cf_idx + 600]
    assert "gate" in cf_context or "violation" in cf_context or "blocked" in cf_context or "no implementation" in cf_context, (
        "sentinel_rules must frame carry-forward as a gate/violation"
    )


def test_r2_audit_only_two_valid_outcomes():
    rsc = RSC()
    assert "no other resolution" in rsc or "only two valid" in rsc or "only valid row" in rsc, (
        "rung_sequence_code must state the R2 audit has exactly two valid row outcomes"
    )
    assert "architectural constraint" in rsc or "constraint type" in rsc or "names constraint" in rsc, (
        "rung_sequence_code must name that a constraint-type label is UNENCODED"
    )


def test_obr_is_observation_not_production():
    rsc = RSC()
    assert "observation" in rsc or "observe" in rsc, (
        "rung_sequence_code must state OBR is an observation rung"
    )
    obr_idx = rsc.rfind("observed running behavior")
    assert obr_idx >= 0, "rung_sequence_code must mention observed running behavior"
    context = rsc[max(0, obr_idx - 100):obr_idx + 500]
    assert "no new" in context or "not a production" in context or "new file" in context or "new artifact" in context, (
        "rung_sequence_code must state no new files may be created at the OBR rung"
    )


def test_manifest_thread_count_bounds_emissions():
    rc = RC()
    assert "declared" in rc or "count" in rc or "exact" in rc or "bound" in rc, (
        "reconciliation_and_completion must state the declared thread count bounds emissions"
    )
    assert "Thread" in rc and ("complete" in rc or "sentinels" in rc), (
        "reconciliation_and_completion must reference Thread N complete sentinels"
    )
    thread_idx = rc.find("Thread")
    context = rc[max(0, thread_idx - 100):thread_idx + 400]
    assert "declared" in context or "count" in context or "exact" in context or "bound" in context, (
        "reconciliation_and_completion must bind thread emissions to declared count"
    )


def test_compile_error_records_zero_prior_failures():
    sr = SR()
    assert "compile" in sr or "import error" in sr, (
        "sentinel_rules must address compile/import errors in the context of prior failure coverage"
    )
    compile_idx = sr.find("compile") if "compile" in sr else sr.find("import error")
    context = sr[max(0, compile_idx - 100):compile_idx + 400]
    assert "zero" in context or "no test" in context or "no prior" in context or "uncovered" in context, (
        "sentinel_rules must state that a compile error records zero prior failures"
    )


def test_compile_then_pass_triggers_vacuous_green():
    sr = SR()
    assert "compile" in sr, "sentinel_rules must address compile errors"
    compile_idx = sr.find("compile")
    context = sr[max(0, compile_idx - 100):compile_idx + 600]
    assert "uncovered" in context or "vacuous" in context or "all tests" in context, (
        "sentinel_rules must state that a compile-then-pass sequence leaves all tests uncovered"
    )


def test_sentinel_must_precede_tool_invocation():
    sr = SR()
    assert "retroactively" in sr or "before its sentinel" in sr or "immediately before the tool" in sr, (
        "sentinel_rules must state the sentinel appears immediately before the tool is invoked"
    )


def test_assertion_modification_direction_independent():
    ep = EP()
    assert "conform" in ep or "match" in ep or "redefine" in ep or "direction" in ep, (
        "epistemological_protocol must state that modifying assertions to match implementation "
        "redefines the gap contract — direction of change is irrelevant"
    )
    assert "gap contract" in ep or "contract" in ep or "epistemological" in ep, (
        "epistemological_protocol must name the epistemological error: using model knowledge "
        "of implementation to define the gap"
    )


def test_composed_prose_body_always_invalid():
    sr = SR()
    assert "characterization" in sr or "description of tool output" in sr or "prose description" in sr, (
        "sentinel_rules must state that a prose description of tool output is always composed content"
    )
    assert "even if accurate" in sr or "regardless of whether" in sr or "even accurate" in sr, (
        "sentinel_rules must state the rule is not conditioned on accuracy of the description"
    )


def test_sentinel_is_prospective_commitment_not_label():
    sr = SR()
    assert "prospective" in sr or "before interpretation" in sr or "commitment" in sr, (
        "sentinel_rules must state the sentinel is a prospective commitment"
    )
    retro_idx = sr.find("retroact") if "retroact" in sr else -1
    assert retro_idx >= 0, "sentinel_rules must contain retroactive sentinel language"
    context = sr[max(0, retro_idx - 200):retro_idx + 600]
    assert "interpret" in context or "composed" in context or "epistemological" in context, (
        "sentinel_rules must name placing a sentinel after output as the same epistemological error"
    )


def test_self_check_requires_temporal_precedence():
    sr = SR()
    self_check_idx = sr.find("Self-check")
    assert self_check_idx >= 0, "sentinel_rules must contain a Self-check section"
    self_check_text = sr[self_check_idx:self_check_idx + 700]
    assert (
        "before the tool" in self_check_text
        or "precedes" in self_check_text
        or "appears before" in self_check_text
        or "before tool output" in self_check_text
        or "appears after" in self_check_text
    ), (
        "sentinel_rules self-check must require confirming the sentinel precedes the tool invocation"
    )


def test_structural_correction_has_concrete_predicate_test():
    ep = EP()
    structural_idx = ep.find("structural correction")
    assert structural_idx >= 0, "epistemological_protocol must mention structural correction"
    context = ep[max(0, structural_idx - 100):structural_idx + 800]
    assert "behaviors" in context or "same observable" in context or "which behaviors" in context, (
        "epistemological_protocol must state the operational test for structural correction"
    )


def test_ei_entry_imperative_blocking_check():
    rsc = RSC()
    ei_idx = rsc.rfind("executable implementation")
    assert ei_idx >= 0, "rung_sequence_code must contain 'executable implementation' in R4 sequence"
    context = rsc[ei_idx:ei_idx + 400]
    assert (
        "stop" in context
        or "verify" in context
        or "must be able to quote" in context
        or "you must" in context
        or "cannot quote" in context
    ), (
        "rung_sequence_code must have an imperative blocking check at the EI entry"
    )
    assert "quote" in context or "Execution observed" in context, (
        "rung_sequence_code EI blocking check must require quoting the 🔴 Execution observed sentinel"
    )


def test_explicit_discard_required_on_skip_ahead_recovery():
    sr = SR()
    assert "discard" in sr or "discarding" in sr.lower() or "explicitly" in sr, (
        "sentinel_rules must require an explicit discard statement when a skip-ahead violation is discovered"
    )
    discard_idx = sr.lower().find("discard")
    assert discard_idx >= 0
    context = sr[max(0, discard_idx - 100):discard_idx + 500]
    assert "re-enter" in context or "re-entry" in context or "reenter" in context, (
        "sentinel_rules discard language must reference re-entering the ladder"
    )
    assert "silent" in context or "ambiguous" in context or "name" in context or "explicit" in context, (
        "sentinel_rules must state that silent re-entry is insufficient"
    )


def test_complexity_exemption_prohibited():
    ep = EP()
    assert (
        "simple" in ep
        or "complexity" in ep
        or "incremental" in ep
        or "clear requirements" in ep
    ), (
        "epistemological_protocol must prohibit complexity-based exemption from the ladder"
    )
    assert "achievable" in ep or "not achievable" in ep or "standard artifact" in ep, (
        "epistemological_protocol must distinguish complexity exemption (invalid) from "
        "domain-achievability exemption (valid)"
    )


def test_ground_governs_invocation_unconditionally():
    ep = EP()
    assert "invocation" in ep or "unconditional" in ep or "once" in ep, (
        "epistemological_protocol must state ground governs the entire invocation once present"
    )
    assert "optional" in ep or "preference" in ep or "asking" in ep or "whether to apply" in ep, (
        "epistemological_protocol must state ground is not an optional style preference"
    )


def test_pre_action_rung_self_check():
    sr = SR()
    assert "before producing" in sr or "before any artifact" in sr or "before each artifact" in sr, (
        "sentinel_rules must define a pre-action self-check that fires before producing any artifact"
    )
    pre_idx = sr.find("before producing") if "before producing" in sr else sr.find("before any artifact")
    assert pre_idx >= 0
    context = sr[max(0, pre_idx - 50):pre_idx + 500]
    assert "rung" in context, (
        "sentinel_rules pre-action check must require identifying the current rung"
    )
    assert "prose" in context or "criteria" in context or "non-executable" in context or "all artifact" in context or "every artifact" in context, (
        "sentinel_rules pre-action check must explicitly apply to non-executable rungs"
    )


def test_implementation_gate_blocks_file_edits():
    sr = SR()
    gate_idx = sr.find("Implementation gate cleared")
    assert gate_idx >= 0, "sentinel_rules must contain 🟢 Implementation gate cleared"
    context = sr[max(0, gate_idx - 100):gate_idx + 700]
    assert (
        "file edit" in context
        or ("file" in context and "edit" in context)
        or ("modif" in context and "file" in context)
        or "tool call" in context
        or "creates or modifies" in context
    ), (
        "sentinel_rules must explicitly name file edits / tool calls that create or modify "
        "implementation files as gated by 🟢"
    )
    assert (
        "validation" in context
        or "test file" in context
        or "carry-forward" in context
    ), (
        "sentinel_rules must carve out validation artifacts from the 🟢 file-edit gate"
    )
    assert (
        "regardless" in context
        or "characteriz" in context
        or "small fix" in context
        or "config" in context
    ), (
        "sentinel_rules must state that characterization of the edit is irrelevant"
    )


def test_i_formation_is_read_only():
    rsc = RSC()
    i_form_idx = rsc.find("I-formation")
    assert i_form_idx >= 0, "rung_sequence_code must contain I-formation section"
    context = rsc[i_form_idx:i_form_idx + 800]
    assert (
        "read-only" in context
        or "observation-only" in context
        or "reading" in context
        or "state" in context
    ), (
        "rung_sequence_code I-formation must be defined as observation-only / state-invariant"
    )
    assert (
        "modif" in context
        or "creat" in context
        or "writing" in context
        or "write" in context
    ), (
        "rung_sequence_code I-formation must explicitly exclude file creation/modification"
    )
    assert (
        "exploring" in context
        or "exploration" in context
        or "rung work" in context
        or "regardless" in context
    ), (
        "rung_sequence_code must state that file modification before the manifest "
        "is rung work regardless of what phase the model believes it is in"
    )


def test_pre_action_check_is_citation_not_assessment():
    sr = SR()
    pre_idx = sr.find("before producing") if "before producing" in sr else sr.find("before any artifact")
    assert pre_idx >= 0
    context = sr[pre_idx:pre_idx + 600]
    assert "quote" in context or "cite" in context or "locate" in context, (
        "sentinel_rules pre-action check condition (c) must require quoting prior-rung "
        "artifacts from this conversation"
    )
    assert "cannot quote" in context or "cannot locate" in context or "not complete" in context or "if you cannot" in context, (
        "sentinel_rules pre-action check must state that inability to quote means "
        "the prior rung is not complete"
    )


def test_obr_infrastructure_creation_is_production():
    rsc = RSC()
    obr_idx = rsc.rfind("observed running behavior")
    assert obr_idx >= 0
    context = rsc[max(0, obr_idx - 100):obr_idx + 1100]
    assert "infrastructure" in context or "enable" in context or "enabling" in context, (
        "rung_sequence_code must state that creating infrastructure to enable OBR observation "
        "is production, not observation"
    )
    assert "existing" in context or "fall back" in context or "ladder artifacts" in context or "test suite" in context, (
        "rung_sequence_code must state the correct alternative: use existing ladder artifacts"
    )


def test_r2_audit_outside_scope_is_unencoded():
    rsc = RSC()
    assert "delegat" in rsc or "outside" in rsc or "handled by" in rsc or "scope" in rsc, (
        "rung_sequence_code must address the 'outside scope / handled by X' rationalization "
        "in the R2 audit section"
    )
    r2_idx = rsc.find("R2 audit")
    assert r2_idx >= 0
    context = rsc[r2_idx:r2_idx + 800]
    assert "delegat" in context or "outside" in context or "handled" in context, (
        "rung_sequence_code R2 audit section must explicitly address delegation/scope justifications "
        "as UNENCODED"
    )


def test_checkmark_sentinel_backward_binding():
    sr = SR()
    assert (
        "attest" in sr
        or "prior completion" in sr
        or "backward" in sr
        or "does not close" in sr
        or "not constitute" in sr
    ), (
        "sentinel_rules must state ✅ sentinels attest prior completion — they do not constitute it"
    )
    assert (
        "retroactively" in sr
        or "invalidates" in sr
        or "reopens" in sr
    ), (
        "sentinel_rules must state that work continuing after a ✅ sentinel retroactively invalidates it"
    )
    assert (
        "inert" in sr
        or "manifest entries" in sr
        or "status annotation" in sr
        or "planning text" in sr
    ), (
        "sentinel_rules must state ✅ tokens in manifest entries or planning text are inert"
    )


def test_sentinel_body_consistency_criterion():
    sr = SR()
    assert (
        "consistent" in sr
        or "traceable" in sr
        or "consistent with" in sr
    ), (
        "sentinel_rules must state the sentinel body must be consistent with "
        "what the validation artifact as written could produce"
    )
    assert (
        "symbol" in sr
        or "absent" in sr
        or "not present" in sr
    ), (
        "sentinel_rules must state that output naming symbols absent from the "
        "validation artifact is fabricated"
    )
    assert (
        "fabricated" in sr
        or "fabrication" in sr
    ), (
        "sentinel_rules must name output inconsistent with the artifact as fabricated"
    )


def test_manifest_enumerates_seven_canonical_rung_names():
    ep = EP()
    assert "seven" in ep or "collapses" in ep or "collapse" in ep, (
        "epistemological_protocol must enumerate the seven canonical rung names in the manifest rule "
        "and state that collapsing VRO into an adjacent rung is malformed"
    )


def test_red_token_validity_is_operational():
    sr = SR()
    assert (
        "inert" in sr
        or "no gate function" in sr
        or "not a sentinel" in sr
        or "carries no gate" in sr
    ), (
        "sentinel_rules must state that a 🔴 token not followed by verbatim tool output "
        "is not a sentinel — it is inert text and carries no gate function"
    )
    assert (
        "cited" in sr
        or "point to" in sr
        or "pointed to" in sr
        or "treated as satisfying" in sr
        or "cannot be cited" in sr
    ), (
        "sentinel_rules must state the inert token cannot be cited or pointed to "
        "as satisfying any gate requirement"
    )


def test_r3_requires_red_sentinels():
    rsc = RSC()
    assert "observed running behavior" in rsc and (
        "Execution observed" in rsc or "\U0001F534" in rsc
    ), (
        "rung_sequence_code must require 🔴 Execution observed at the observed running behavior rung"
    )
    assert "behavior from I" in rsc or ("behavior" in rsc and "from I" in rsc), (
        "rung_sequence_code must require R3 gap to name the specific behavior from I"
    )


def test_prior_failure_scoped_to_test():
    sr = SR()
    assert ("individual test" in sr or "specific test" in sr) and "produced it" in sr, (
        "sentinel_rules must state prior recorded failure applies to the specific test that produced it"
    )
    assert "carry-forward" in sr or "carry forward" in sr, (
        "sentinel_rules must require a carry-forward statement after validation artifact modification"
    )
    assert "uncovered" in sr or "no covering" in sr, (
        "sentinel_rules must state uncovered tests trigger the vacuous-green check"
    )


def test_criteria_rung_falsifiability_is_a_gate():
    rsc = RSC()
    criteria_idx = rsc.find("criteria (")
    assert criteria_idx >= 0, "rung_sequence_code must contain a criteria rung"
    context = rsc[criteria_idx:criteria_idx + 400]
    assert "falsif" in context.lower(), (
        "criteria rung must state a falsifiability requirement"
    )
    assert "before advancing" in context or "verify" in context, (
        "falsifiability must be framed as a gate before advancing, not descriptive guidance"
    )
    assert "structural" in context or "implementation detail" in context or "behavioral" in context, (
        "criteria rung must name the anti-pattern: structural shape or implementation detail "
        "rather than behavioral condition"
    )


def test_carry_forward_names_a1_exception_with_causal_chain():
    sr = SR()
    cf_idx = sr.find("carry-forward is the one")
    if cf_idx < 0:
        cf_idx = sr.find("carry-forward")
    assert cf_idx >= 0, "sentinel_rules must contain carry-forward language"
    context = sr[cf_idx:cf_idx + 400]
    assert "exception" in context.lower(), (
        "carry-forward must be named as an exception to the event-gate requirement "
        "in proximity to the carry-forward instruction"
    )
    assert "composed" in context.lower(), (
        "carry-forward must be named as a composed claim rather than a captured event"
    )
    assert "strict" in context.lower() or "derives" in context.lower(), (
        "must state that the strictness of the format requirement derives from "
        "its exception status (causal chain)"
    )


def test_locality_directional_asymmetry_with_nonconflict():
    ep = EP()
    motion_idx = ep.find("downward motion")
    assert motion_idx >= 0, (
        "epistemological_protocol must state locality constrains downward motion "
        "(not just 'downward-sufficient' in Primitive 2)"
    )
    context = ep[max(0, motion_idx - 50):motion_idx + 300]
    assert "upward" in context, (
        "downward-motion statement must reference upward correction in the same context "
        "to establish the directional asymmetry"
    )
    assert "not conflict" in context or "opposite" in context or "do not conflict" in context, (
        "must explicitly state the two constraints do not conflict because they apply "
        "in opposite directions"
    )


def test_manifest_entries_name_behavioral_gaps_not_implementation_decisions():
    ep = EP()
    manifest_idx = ep.find("The manifest must name every rung")
    assert manifest_idx >= 0, \
        "epistemological_protocol must contain manifest rung-naming requirement"
    context = ep[manifest_idx:manifest_idx + 600]
    assert "implementation decision" in context, (
        "manifest rules must name implementation decisions as a prohibited content type"
    )
    assert "behavioral gap" in context, (
        "manifest rules must name behavioral gaps as the required content type"
    )


def test_ev_artifact_must_be_in_project_tree():
    rsc = RSC()
    ev_idx = rsc.find("executable validation (")
    assert ev_idx >= 0, "rung_sequence_code must contain executable validation rung"
    context = rsc[ev_idx:ev_idx + 600]
    assert "project directory" in context or "project tree" in context, (
        "EV rung must require the artifact to reside within the project directory"
    )
    assert "/tmp" in context or "outside the project" in context, (
        "EV rung must name out-of-project paths (e.g. /tmp) as not satisfying the rung"
    )


def test_i_formation_prohibits_implementation_intent():
    rsc = RSC()
    assert "I-formation ends" in rsc or "gate prohibiting" in rsc, (
        "rung_sequence_code I-formation must end at a gate prohibiting implementation intent"
    )
    i_form_end_idx = rsc.find("I-formation ends")
    if i_form_end_idx < 0:
        i_form_end_idx = rsc.find("gate prohibiting")
    context = rsc[i_form_end_idx:i_form_end_idx + 400]
    assert "implementation decisions" in context or "implementation decision" in context, (
        "I-formation gate must name implementation decisions as prohibited"
    )
    assert "behavioral gap" in context.lower(), (
        "I-formation gate must name behavioral gaps as the only permitted manifest content"
    )

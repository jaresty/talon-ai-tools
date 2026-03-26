"""Ground prompt behavioral tests (ADR-0178: GROUND_PARTS removed; minimal is the only version)."""

import pytest
from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt

# All section aliases now return the full prompt — behavioral tests below are stable.
EP = lambda: build_ground_prompt()  # Rule 0, primitives, scope discipline
SR = lambda: build_ground_prompt()  # Gate mechanics, sentinels, carry-forward
RSC = lambda: build_ground_prompt()  # R4 sequence, rung-level rules
RC = lambda: build_ground_prompt()  # Reconciliation and completion


def test_build_ground_prompt_is_nonempty():
    result = build_ground_prompt()
    assert result.strip(), "build_ground_prompt() must return a non-empty string"


def test_build_ground_prompt_starts_with_response():
    result = build_ground_prompt()
    assert result.startswith("The response "), (
        "build_ground_prompt() must start with 'The response '"
    )


def test_derivation_structure_content():
    assert "I is the declared intent" in EP()


def test_observed_running_behavior_requires_traceability():
    rsc = RSC()
    assert "traceable" in rsc or "traceability" in rsc or "behavioral gap" in rsc, (
        "rung_sequence_code must require observed running behavior to be traceable to the declared gap"
    )
    assert (
        "server response" in rsc or "HTTP" in rsc or "URL" in rsc or "rendering" in rsc
    ), (
        "rung_sequence_code must name domain-specific anti-patterns for observed running behavior"
    )


def test_r2_audit_gate():
    rsc = RSC()
    assert "audit" in rsc or "enumerate" in rsc, (
        "rung_sequence_code must require an explicit R2 audit before advancing from formal notation"
    )
    assert "incomplete" in rsc or "unencoded" in rsc.lower(), (
        "rung_sequence_code must state the rung is incomplete until all criteria are encoded"
    )


def test_i_formation_sentinel():
    rsc = RSC()
    assert "I-formation complete" in rsc, (
        "rung_sequence_code must define a sentinel for I-formation completion"
    )
    assert "manifest may not appear" in rsc or "before the" in rsc, (
        "rung_sequence_code must state the manifest may not appear before the I-formation sentinel"
    )


def test_self_check_before_advancing_executable_rung():
    # ADR-0179 E4: "before advancing, verify both parts" replaced with content gate
    sr = SR()
    assert "content gate" in sr, (
        "ADR-0179 E4: falsifying condition must be a content gate (no implementation internals), not a self-check"
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


def test_v_complete_requires_green_gate_before_implementation():
    sr = SR()
    assert "both" in sr or (
        "then" in sr.lower() and "Implementation gate cleared" in sr
    ), (
        "sentinel_rules must state both V-complete and 🟢 are required in order before implementation"
    )
    assert (
        "does not open" in sr
        or "insufficient" in sr
        or ("alone" in sr and "gate" in sr)
    ), (
        "sentinel_rules must state V-complete alone does not open the implementation gate"
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
    assert "complete" in sr and (
        "block" in sr or "```" in sr or "triple" in sr or "delimit" in sr
    ), (
        "sentinel_rules must require 🔴 Execution observed to contain a complete delimited block"
    )
    assert (
        "nothing omitted" in sr
        or "complete output" in sr
        or "complete tool output" in sr
    ), (
        "sentinel_rules must state the block contains the complete tool output — nothing omitted"
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


def test_retroactive_sentinel_does_not_open_gate():
    sr = SR()
    assert "retroact" in sr or "re-run" in sr or "rerun" in sr, (
        "sentinel_rules must state that a retroactive sentinel leaves the gate closed and the tool must be re-run"
    )
    retro_idx = sr.find("retroact") if "retroact" in sr else sr.find("re-run")
    context = sr[max(0, retro_idx - 50) : retro_idx + 350]
    assert "gate" in context or "re-run" in context or "closed" in context, (
        "sentinel_rules must state the gate consequence of retroactive sentinel — gate does not open"
    )


def test_r3_positive_definition_for_code_contexts():
    rsc = RSC()
    assert (
        "rendered" in rsc
        or "DOM" in rsc
        or "api response" in rsc.lower()
        or "response body" in rsc
        or "HTML fragment" in rsc
        or "render utility" in rsc
    ), (
        "rung_sequence_code must give a positive definition of what satisfies R3 in code contexts"
    )
    assert "direct" in rsc or "directly" in rsc or "demonstrates" in rsc, (
        "rung_sequence_code must require the R3 output to directly demonstrate the declared feature"
    )


def test_carry_forward_is_a_gate():
    sr = SR()
    assert "no implementation" in sr and (
        "carry-forward" in sr or "carry forward" in sr
    ), (
        "sentinel_rules must state that no implementation artifact may appear until carry-forward is emitted"
    )
    # Use the "modification without carry-forward" occurrence (gate rule), not the E1 read-gate occurrence
    cf_idx = sr.find("modification without carry-forward")
    if cf_idx < 0:
        cf_idx = (
            sr.find("carry-forward")
            if "carry-forward" in sr
            else sr.find("carry forward")
        )
    cf_context = sr[max(0, cf_idx - 200) : cf_idx + 600]
    assert (
        "gate" in cf_context
        or "violation" in cf_context
        or "blocked" in cf_context
        or "no implementation" in cf_context
    ), "sentinel_rules must frame carry-forward as a gate/violation"


def test_composed_prose_body_always_invalid():
    sr = SR()
    assert (
        "characterization" in sr
        or "description of tool output" in sr
        or "prose description" in sr
    ), (
        "sentinel_rules must state that a prose description of tool output is always composed content"
    )
    assert (
        "even if accurate" in sr
        or "regardless of whether" in sr
        or "even accurate" in sr
    ), (
        "sentinel_rules must state the rule is not conditioned on accuracy of the description"
    )


def test_pre_action_rung_self_check():
    # ADR-0181: rung-entry gate is the pre-action check. It says "before producing content at any rung"
    # and requires stating rung name, gap, artifact type, and exec_observed check.
    sr = SR()
    assert (
        "before producing" in sr
        or "before any artifact" in sr
        or "before each artifact" in sr
    ), (
        "sentinel_rules must define a pre-action self-check that fires before producing any artifact"
    )
    pre_idx = (
        sr.find("before producing")
        if "before producing" in sr
        else sr.find("before any artifact")
    )
    assert pre_idx >= 0
    context = sr[max(0, pre_idx - 50) : pre_idx + 500]
    assert "rung" in context, (
        "sentinel_rules pre-action check must require identifying the current rung"
    )
    # "any rung" covers all rungs including prose, criteria, and non-executable rungs
    assert (
        "any rung" in context
        or "prose" in context
        or "criteria" in context
        or "non-executable" in context
        or "all artifact" in context
        or "every artifact" in context
    ), "sentinel_rules pre-action check must explicitly apply to non-executable rungs"


def test_ei_rung_vacuous_green_rearms_during_cycle():
    # ADR-0178 migration: GROUND_PARTS["rung_sequence_code"] removed; check full minimal prompt.
    # "vacuous" is present in the EV rung section which covers this check.
    rsc = RSC()
    assert "vacuous" in rsc or "uncovered" in rsc, (
        "Ground prompt must contain vacuous-green check: a test that passes without a prior "
        "recorded failure is vacuous"
    )


def test_test_modification_requires_meta_test_rule():
    sr = SR()
    assert (
        "meta-test" in sr
        or "meta_test" in sr
        or "test-under-modification" in sr
        or "test under modification" in sr
    ), (
        "Ground prompt must provide a rule for when the declared intent is to modify a test artifact, "
        "naming the test-under-modification as the implementation artifact and requiring a meta-test "
        "as the validation artifact"
    )


def test_formal_notation_verbatim_restatement_permitted():
    sr = SR()
    assert "verbatim" in sr and (
        "no elaboration" in sr or "restate" in sr or "restatement" in sr
    ), (
        "Ground prompt must permit verbatim restatement of the criterion as the formal notation artifact "
        "when the criterion is already a complete behavioral specification"
    )


def test_continuous_rung_traversal_required():
    sr = SR()
    assert (
        "without pausing" in sr
        or "continuously" in sr
        or "do not pause" in sr
        or "without stopping" in sr
    ), (
        "Ground prompt must state that rung traversal is continuous and the model must not pause "
        "for user confirmation between rungs"
    )


def test_formal_notation_prohibits_implementation_shaped_content():
    sr = SR()
    assert (
        "function bod" in sr or "function body" in sr or "function bodies" in sr
    ) and ("pseudocode" in sr), (
        "Ground prompt must explicitly prohibit complete function bodies at the formal notation rung "
        "and must clarify that labeling content as pseudocode does not exempt it from the prohibition"
    )


def test_sequential_thread_execution_required():
    # ADR-0181: "at most one thread" removed (attractor 4 subsumed by rung-entry gate).
    # Gate part (b) — singular current gap — enforces serialization: a model producing thread N+1
    # content cannot state a singular current gap without contradiction.
    sr = SR()
    assert (
        "before beginning the next thread" in sr
        or "before starting the next thread" in sr
        or "before thread" in sr
        or "at most one thread" in sr
        or "one thread at a time" in sr
        or "Rung-entry gate" in sr
    ), (
        "Ground prompt must enforce sequential thread execution — via explicit gate or rung-entry gate"
    )


def test_sequential_thread_gate_covers_all_rungs():
    # ADR-0181: "at most one thread" clause removed; rung-entry gate covers all rungs by design.
    sr = SR()
    # Gate says "before producing content at any rung" — covers all rungs, not just prose.
    assert "Rung-entry gate" in sr, (
        "rung-entry gate must be present to enforce all-rung thread serialization"
    )
    gate_idx = sr.find("Rung-entry gate")
    context = sr[gate_idx : gate_idx + 300]
    assert "any rung" in context, (
        "Rung-entry gate must apply to 'any rung' — not limited to the prose rung"
    )


def test_immediate_descent_after_criteria():
    sr = SR()
    assert (
        "enumerating remaining criteria" in sr or "planning future gap cycles" in sr
    ), (
        "Ground prompt must state that after emitting the criteria artifact the model must immediately "
        "proceed to formal notation without enumerating remaining criteria or planning future cycles"
    )


def test_manifest_entries_are_gap_labels_only():
    sr = SR()
    manifest_idx = sr.find("Manifest declared may be emitted")
    assert manifest_idx >= 0, "manifest rule must be present"
    # Search in a window around the manifest rule
    window = sr[max(0, manifest_idx - 500) : manifest_idx + 500]
    assert ("label" in window or "noun phrase" in window or "short" in window) and (
        "assertion" in window or "verb" in window or "first time" in window
    ), (
        "Ground prompt must state near the manifest rule that entries are gap labels only "
        "(not behavioral assertions) and that the behavioral assertion is produced at the criteria rung"
    )


def test_criterion_emergence_gated_on_thread_complete():
    sr = SR()
    assert (
        (
            "next criterion" in sr
            and "thread"
            in sr[
                sr.find("next criterion") - 200 : sr.find("next criterion") + 200
            ].lower()
        )
        or ("criterion may not be named" in sr)
        or (
            "subsequent criteria emerge only after" in sr
            and "complete"
            in sr[
                sr.find("subsequent criteria emerge only after") : sr.find(
                    "subsequent criteria emerge only after"
                )
                + 100
            ]
        )
    ), (
        "Ground prompt must state that the next criterion may not be named until "
        "Thread N complete has been emitted for the prior criterion's cycle"
    )


def test_formal_notation_must_encode_all_constraints():
    # ADR-0181: "Only validation artifacts may be produced" removed (attractor 1 subsumed by gate).
    # EV rung now opens with "each test function asserts exactly one behavioral property".
    sr = SR()
    fn_idx = sr.find("Formal notation encodes only the criteria")
    ev_idx = sr.find("each test function asserts exactly one behavioral property")
    assert fn_idx >= 0 and ev_idx > fn_idx, (
        "formal notation section must be present before EV rung"
    )
    fn_section = sr[fn_idx:ev_idx]
    assert (
        "every structural constraint" in fn_section
        or "all structural constraints" in fn_section
        or "each constraint" in fn_section
        or "all constraints" in fn_section
    ), (
        "Formal notation section must state that the artifact must encode all structural constraints "
        "the criterion implies, not just a subset of permitted forms"
    )


def test_thread_scanner_scoped_to_practitioner_prose():
    sr = SR()
    # The manifest-scanning sentence must explicitly reference the prose rung artifact,
    # not just "the prose" (which is ambiguous and could include the ground prompt itself).
    scan_idx = sr.find("scan every sentence in the prose")
    assert scan_idx >= 0, "manifest scanning sentence must be present"
    context = sr[scan_idx : scan_idx + 300]
    assert (
        "prose rung" in context
        or "prose rung artifact" in context
        or "practitioner" in context
    ), (
        "The manifest-scanning sentence must scope 'the prose' to the practitioner's prose rung artifact, "
        "not to the ground prompt's rule text or other transcript content"
    )


def test_formal_notation_rung_permits_prose_labels():
    prompt = build_ground_prompt()
    assert (
        "Natural language may appear as section labels or introductions" in prompt
        or "natural language" in prompt.lower()
        and "label" in prompt.lower()
    ), (
        "Formal notation rung must explicitly permit natural language as section labels or introductions"
    )


def test_formal_notation_separates_behavioral_from_explanation():
    prompt = build_ground_prompt()
    assert (
        "separates behavioral specification from explanation" in prompt.lower()
        or "separate" in prompt.lower()
        and "behavioral" in prompt.lower()
        and "explanation" in prompt.lower()
    ), (
        "Formal notation rung must explicitly state it separates behavioral specification from explanation"
    )
    assert "encodes what must be true" in prompt.lower(), (
        "Formal notation rung must state that formal notation encodes what must be true"
    )
    assert "executable or testable" in prompt.lower(), (
        "Formal notation rung must describe the encoded content as executable/testable"
    )
    assert (
        "explains the specification" in prompt.lower()
        or "prose adds context" in prompt.lower()
    ), (
        "Formal notation rung must describe prose as explaining/adding context, not as the deliverable"
    )
    assert (
        "explains" in prompt.lower()
        or "context" in prompt.lower()
        or "introduces" in prompt.lower()
    ) and ("prose" in prompt.lower() or "natural language" in prompt.lower()), (
        "Formal notation rung must state that prose explains or provides context, not the deliverable itself"
    )


def test_formal_notation_prose_does_not_substitute_for_notation():
    prompt = build_ground_prompt()
    assert (
        "may not substitute for encoding a constraint in notation" in prompt
        or "must not substitute" in prompt
    ), (
        "Formal notation rung must state that prose may not substitute for encoding a constraint in notation"
    )

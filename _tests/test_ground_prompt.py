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


def test_reconciliation_content():
    assert "Intent precedes its representations" in GROUND_PARTS["reconciliation_and_completion"]

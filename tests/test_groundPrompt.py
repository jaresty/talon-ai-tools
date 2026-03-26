"""Tests for groundPrompt — sentinel gates and ADR-0179 axiom-first formulation."""
from lib.groundPrompt import SENTINEL_TEMPLATES, build_ground_prompt


def test_manifest_declared_sentinel_present():
    """SENTINEL_TEMPLATES contains a 'manifest_declared' sentinel."""
    assert "manifest_declared" in SENTINEL_TEMPLATES


def test_ground_entered_sentinel_present():
    """SENTINEL_TEMPLATES contains a 'ground_entered' sentinel."""
    assert "ground_entered" in SENTINEL_TEMPLATES


def test_hard_stop_sentinel_present():
    """Rendered ground prompt contains HARD STOP text."""
    assert "HARD STOP" in build_ground_prompt()


def test_hard_stop_signals_upward_return_not_termination():
    """HARD STOP description specifies upward return to criteria, not termination."""
    text = build_ground_prompt()
    hard_stop_idx = text.index("HARD STOP")
    nearby = text[hard_stop_idx:hard_stop_idx + 300]
    assert "no further content" not in nearby


def test_axiom_a1_present():
    """ADR-0179: rendered prompt states A1 (epistemic authority — tool-executed events only)."""
    text = build_ground_prompt()
    assert "A1" in text, (
        "expected 'A1' in rendered ground prompt — "
        "axiom-first formulation must name A1 explicitly"
    )


def test_rung_entry_gate_present():
    """ADR-0181: rendered prompt contains rung-entry gate text."""
    text = build_ground_prompt()
    assert "Rung-entry gate" in text, (
        "expected 'Rung-entry gate' in rendered ground prompt — "
        "ADR-0181 requires a rung-entry gate before any rung-specific enforcement text"
    )


def test_rung_entry_gate_precedes_exec_observed_rule():
    """ADR-0181: rung-entry gate appears before the exec_observed verbatim rule."""
    text = build_ground_prompt()
    gate_idx = text.index("Rung-entry gate")
    exec_rule_idx = text.index("Every \U0001F534 Execution observed: sentinel")
    assert gate_idx < exec_rule_idx, (
        "rung-entry gate must appear before the exec_observed verbatim rule — "
        "gate fires at rung entry, before any rung-specific content rule"
    )


def test_rung_entry_gate_follows_r2_block():
    """ADR-0181: rung-entry gate appears after the R2 axiom block."""
    text = build_ground_prompt()
    r2_anchor = "each artifact addresses only the gap declared by the prior rung"
    r2_idx = text.index(r2_anchor)
    gate_idx = text.index("Rung-entry gate")
    assert r2_idx < gate_idx, (
        "rung-entry gate must follow the R2 axiom block — "
        "ADR-0181 specifies placement immediately after A1-A3-R2"
    )


def test_attractor1_vro_stop_removed():
    """ADR-0181: attractor 1 (VRO-only stop) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "Only validation artifacts may be produced at the executable validation rung" not in text, (
        "attractor 1 enforcement clause must be removed — rung-entry gate subsumes it"
    )


def test_attractor4_thread_serialization_removed():
    """ADR-0181: attractor 4 (thread serialization gate) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "at most one thread is in progress at a time" not in text, (
        "attractor 4 enforcement clause must be removed — rung-entry gate subsumes it"
    )


def test_attractor6_obr_testrunner_removed():
    """ADR-0181: attractor 6 (OBR test-runner prohibition) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "it does not satisfy the OBR gate \u2014 re-invoke the implemented artifact directly" not in text, (
        "attractor 6 enforcement clause must be removed — rung-entry gate subsumes it"
    )


def test_attractor7_final_report_transcript_gate_removed():
    """ADR-0181: attractor 7 (final report transcript gate) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "before writing each section, locate the artifact in the prior transcript" not in text, (
        "attractor 7 enforcement clause must be removed — rung-entry gate subsumes it"
    )


def test_attractor8_reconciliation_gate_removed():
    """ADR-0181: attractor 8 (reconciliation loop) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "Reconciliation gate:" not in text, (
        "attractor 8 enforcement clause must be removed — rung-entry gate subsumes it"
    )


def test_attractor5_enforcement_wrapper_removed():
    """ADR-0181: attractor 5 enforcement wrapper removed — definitional content retained."""
    text = build_ground_prompt()
    assert "it is invalid \u2014 split it before continuing" not in text, (
        "attractor 5 enforcement wrapper must be removed — only definitional content is kept"
    )


def test_attractor5_conjunction_definition_retained():
    """ADR-0181: attractor 5 conjunction definition retained after enforcement wrapper removed."""
    text = build_ground_prompt()
    assert "conjunction" in text, (
        "conjunction definitional content must be retained — "
        "the model needs it to execute the rung-entry gate correctly"
    )


def test_axiom_r2_present():
    """ADR-0179: rendered prompt states R2 as a named axiom (not only in sentinel text)."""
    text = build_ground_prompt()
    # "R2" already appears in sentinel text; require it to appear before the sentinel block
    sentinel_block_marker = "Sentinel formats"
    sentinel_idx = text.index(sentinel_block_marker) if sentinel_block_marker in text else len(text)
    pre_sentinel = text[:sentinel_idx]
    assert "R2" in pre_sentinel, (
        "expected 'R2' in the axiom/rule section of the rendered prompt (before sentinel block) — "
        "axiom-first formulation must name R2 as a derivation rule"
    )

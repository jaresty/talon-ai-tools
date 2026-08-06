"""Tests for groundPrompt — spike/craft-token-refactor form (Ground properties: block)."""
from lib.groundPrompt import build_ground_prompt


# --- Attractor removal tests (keep: these verify old text is absent) ---

def test_attractor1_vro_stop_removed():
    """ADR-0181: attractor 1 (VRO-only stop) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "Only validation artifacts may be produced at the executable validation rung" not in text


def test_attractor4_thread_serialization_removed():
    """ADR-0181: attractor 4 (thread serialization gate) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "at most one thread is in progress at a time" not in text


def test_attractor6_obr_testrunner_removed():
    """ADR-0181: attractor 6 (OBR test-runner prohibition) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "it does not satisfy the OBR gate — re-invoke the implemented artifact directly" not in text


def test_attractor7_final_report_transcript_gate_removed():
    """ADR-0181: attractor 7 (final report transcript gate) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "before writing each section, locate the artifact in the prior transcript" not in text


def test_attractor8_reconciliation_gate_removed():
    """ADR-0181: attractor 8 (reconciliation loop) removed — subsumed by rung-entry gate."""
    text = build_ground_prompt()
    assert "Reconciliation gate:" not in text


def test_attractor5_enforcement_wrapper_removed():
    """ADR-0181: attractor 5 enforcement wrapper removed — definitional content retained."""
    text = build_ground_prompt()
    assert "it is invalid — split it before continuing" not in text


# --- Current structure tests (spike/craft-token-refactor ground definition) ---

def test_ground_properties_block_required():
    """Ground properties: block must be required before any action."""
    text = build_ground_prompt()
    assert "Ground properties:" in text


def test_interpretation_line_required():
    """Interpretation: line must be required for ambiguous requests."""
    text = build_ground_prompt()
    assert "Interpretation:" in text


def test_property_line_format():
    """Properties are written as 'property [N]:' lines."""
    text = build_ground_prompt()
    assert "property [N]:" in text


def test_split_test_sentinel():
    """§ split test: sentinel must appear in the definition."""
    text = build_ground_prompt()
    assert "§ split test:" in text


def test_split_test_atomic_form():
    """Atomic conclusion form must be present."""
    text = build_ground_prompt()
    assert "atomic, no valid split" in text


def test_completeness_check_sentinel():
    """§ completeness check: sentinel must appear."""
    text = build_ground_prompt()
    assert "§ completeness check:" in text


def test_properties_complete_yes():
    """§ properties complete? yes sentinel must appear."""
    text = build_ground_prompt()
    assert "§ properties complete? yes" in text


def test_observational_independence():
    """Observational independence check must be required."""
    text = build_ground_prompt()
    assert "observationally independent" in text


def test_ground_complete_sentinel():
    """§ ground complete must be the final sentinel of the block."""
    text = build_ground_prompt()
    assert "§ ground complete" in text


def test_formality_check_sentinel():
    """§ formality check: sentinel must appear before split test."""
    text = build_ground_prompt()
    assert "§ formality check:" in text
    assert text.index("§ formality check:") < text.index("§ split test:")


def test_formality_check_iterates():
    """Rewrite loop: rewritten definition must be re-checked until confirmed formal."""
    text = build_ground_prompt()
    assert "§ rewritten:" in text
    assert "confirmed formal" in text

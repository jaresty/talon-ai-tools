"""Tests for groundPrompt — current slim form (ADR-0224: ground slimmed to A0+M only)."""
from lib.groundPrompt import build_ground_prompt


def test_opening_bookend_inside_criteria():
    """Opening bookend is criterion (0) inside the derivation sequence, not an external pre-condition."""
    text = build_ground_prompt()
    assert "invoke the subject as a tool call" in text, (
        "opening bookend must appear as first criterion inside derivation sequence"
    )
    assert "Before writing the governing goal heading, run the system under test" not in text, (
        "old external pre-condition form must be removed"
    )


def test_closing_bookend_names_subject_directly():
    """Closing bookend requires tool-result substring via §4 coverage verified sentinel (CL2 gate)."""
    text = build_ground_prompt()
    assert "when every covered dimension cites such a substring, write '§4 coverage verified'" in text, (
        "closing bookend must require tool-result substring — §4 coverage verified sentinel must be present"
    )
    assert "every covered dimension must cite a verbatim string from a tool-executed result that contains output the system produced directly" not in text, (
        "old semantic-source form must be removed"
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

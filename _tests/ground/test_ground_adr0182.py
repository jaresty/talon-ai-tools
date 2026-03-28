"""Tests for ADR-0182: Attractor-first restructure of groundPrompt.py.

Four threads:
  1. principles-named  — P1/P2/P3 labels appear after axioms, before protocol mechanics
  2. rung-table-present — rung table generated from RUNG_SEQUENCE is present in output
  3. corollaries-removed — paragraphs listed in ADR-0182 as P1/P2/P3 corollaries are absent
  4. gate-repositioned  — rung-entry gate appears after P3 principle text
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lib.groundPrompt import build_ground_prompt


def _result() -> str:
    return build_ground_prompt()


# ── Thread 1: principles-named ────────────────────────────────────────────────

def test_p1_label_present():
    assert "P1 (Evidential boundary)" in _result()


def test_p2_label_present():
    # P2 removed (ADR-0184 lean rewrite) — forward-only rule folded into P1 gate column sentence
    assert "gate condition for each rung is the rung table" in _result()


def test_p3_label_present():
    assert "P3 (Scope discipline)" in _result()


def test_principles_appear_after_axioms():
    result = _result()
    ax_end = result.index("R2:") + len("R2:")
    p1_pos = result.index("P1 (Evidential boundary)")
    assert ax_end < p1_pos, "P1 must appear after the R2 axiom text"


def test_principles_appear_before_exec_observed_block():
    result = _result()
    p3_pos = result.index("P3 (Scope discipline)")
    mech_start = result.index("\U0001f534 Execution observed: requires")
    assert p3_pos < mech_start, "P3 must appear before the exec_observed verbatim rule"


# ── Thread 2: rung-table-present ─────────────────────────────────────────────

def test_rung_table_header_present():
    assert "Rung table" in _result()


def test_rung_table_contains_all_rung_names():
    result = _result()
    rung_names = [
        "prose",
        "criteria",
        "formal notation",
        "executable validation",
        "validation run observation",
        "executable implementation",
        "observed running behavior",
    ]
    table_start = result.index("Rung table")
    # All rung names must appear in the table section (before protocol mechanics)
    mech_start = result.index("\U0001f534 Execution observed: requires")
    table_section = result[table_start:mech_start]
    for name in rung_names:
        assert name in table_section, f"Rung '{name}' missing from rung table section"


# ── Thread 3: corollaries-removed ────────────────────────────────────────────

def test_corollary_one_edit_per_rerun_removed():
    # "One edit per re-run cycle" is a P3 corollary listed in ADR-0182 for removal
    assert "One edit per re-run cycle" not in _result()


def test_corollary_no_additional_invariants_removed():
    # "no additional invariants, no anticipated cases" is a P3 corollary
    assert "no additional invariants, no anticipated cases" not in _result()


def test_corollary_file_reads_ev_removed():
    # "file reads, grep output, and manual inspection do not constitute executable validation"
    # is a P1 corollary
    assert "file reads, grep output, and manual inspection do not constitute executable validation" not in _result()


def test_corollary_v_complete_before_red_run_removed():
    # "implementation edits may not begin until a red run exists in the transcript"
    # is a P2 corollary
    assert "implementation edits may not begin until a red run exists in the transcript" not in _result()


# ── Thread 4: gate-repositioned ──────────────────────────────────────────────

def test_rung_entry_gate_appears_after_p3():
    result = _result()
    p3_pos = result.index("P3 (Scope discipline)")
    gate_pos = result.index("Rung-entry gate:")
    assert p3_pos < gate_pos, "Rung-entry gate must appear after P3 principle"


def test_rung_entry_gate_appears_after_rung_table():
    result = _result()
    table_pos = result.index("Rung table")
    gate_pos = result.index("Rung-entry gate:")
    assert table_pos < gate_pos, "Rung-entry gate must appear after rung table"

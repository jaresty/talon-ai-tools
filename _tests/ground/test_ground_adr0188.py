"""Tests for ADR-0188: Axiom Completeness — A4, A5, P5, Fix 1, Fix 2."""

import pytest
from lib.groundPrompt import build_ground_prompt, GROUND_PARTS_MINIMAL


def _prompt() -> str:
    return build_ground_prompt()


# ── Thread 1: A4/A5/P5 present and ordered before P1 ──────────────────────────

def test_a4_provenance_present():
    assert "A4 (Provenance)" in _prompt()


def test_a5_cycle_identity_present():
    assert "A5 (Cycle identity)" in _prompt()


def test_p5_convergence_present():
    assert "P5 (Convergence)" in _prompt()


def test_a4_a5_p5_appear_before_p1():
    p = _prompt()
    p1_idx = p.index("P1 (Evidential boundary)")
    assert p.index("A4 (Provenance)") < p1_idx
    assert p.index("A5 (Cycle identity)") < p1_idx
    assert p.index("P5 (Convergence)") < p1_idx


# ── Thread 2: manifest revision semantics (Fix 2) ────────────────────────────

def test_manifest_once_per_invocation_removed():
    assert "exactly once per invocation" not in _prompt()


def test_manifest_revision_semantics_present():
    p = _prompt()
    assert "revised manifest" in p
    assert "Completed threads are closed" in p


# ── Thread 3: OBR void condition scoped (Fix 1) ──────────────────────────────

def test_obr_void_step5_exception_present():
    p = _prompt()
    assert "OBR step 5 does not void this rung" in p


def test_obr_void_live_process_evidence_scoped():
    p = _prompt()
    assert "used as OBR live-process evidence" in p


# ── Thread 4: derivable rules deleted ────────────────────────────────────────

def test_impl_gate_prior_cycle_clause_removed():
    # A4 derives this; should not appear as a standalone rule
    assert "not from a prior cycle" not in _prompt()


def test_hard_stop_identical_criterion_block_removed():
    # P5 subsumes this block
    assert "textually identical to the current criterion" not in _prompt()


def test_carry_forward_read_explicit_rule_removed():
    # A4 derives carry-forward read requirement; explicit rule deleted
    assert "invoke a tool call to read the current test file before emitting carry-forward" not in _prompt()

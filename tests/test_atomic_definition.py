"""Tests for the atomic token definition in axisConfig.py.

These tests assert the presence of specific key phrases in the new atomic definition
and the absence of the hollow enumeration-completeness clause.

Each test FAILs against the old definition and PASSes after the new definition is applied.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def test_atomic_scope_commitment_from_run_result():
    """Dim 1: scope commitment is a literal string quoted from the most recently produced run result."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "A scope commitment is a literal string quoted from the most recently produced run result" in defn


def test_atomic_nonrun_recency():
    """Dim 2: run result recency defined structurally — no other run result appears between."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "no other run result appears between that result and the tool call" in defn


def test_atomic_symbol_commitment_line_format():
    """Dim 3: symbol commitment must appear as 'symbol: <identifier>' line."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "symbol: <identifier>" in defn


def test_atomic_four_escape_categories():
    """Dim 4: four named escape categories must be present — closes Drift 1."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "(i) scope inflation" in defn
    assert "(ii) stale quote" in defn
    assert "(iii) symbol cardinality" in defn
    assert "(iv) post-call line mismatch" in defn


def test_atomic_hollow_enumeration_absent():
    """Dim 5: old hollow enumeration-completeness clause must be gone."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "The enumeration is complete when no remaining open path exists" not in defn


def test_atomic_last_line_immediately_before():
    """Dim 6: scope line must appear immediately above (i) escape category line — closes D1+G1."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "line immediately above the `(i)` escape category line must be the quoted scope commitment" in defn


def test_atomic_run_result_no_falsify_coupling():
    """Dim 7: atomic description must not reference FAIL signal, Bash tool call, or test runner — those belong in falsify."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "FAIL signal" not in defn
    assert "Bash tool call" not in defn
    assert "test runner" not in defn


def test_atomic_per_call_independence():
    """Dim 8: scope line requirement must apply independently per call — closes D3+G2."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "independently" in defn


def test_atomic_escape_categories_per_call_positional():
    """Dim 9: five-line block (§ permitted + (i)-(iv)) must appear as last five lines immediately before each call — closes once-discharge gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "last five content lines begin with" in defn


def test_atomic_scope_line_above_escape_categories():
    """Dim 10: quoted scope line must appear immediately above (i) — closes mutual-exclusion conflict with escape categories."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "line immediately above the `(i)` escape category line must be the quoted scope commitment" in defn


def test_atomic_stub_new_symbol():
    """Dim 11: new-symbol calls must introduce only a stub — closes implementation-depth gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "immediately preceding run result, the symbol is new" in defn


def test_atomic_four_escape_categories_only():
    """Dim 12: exactly four escape categories (i)-(iv); (v) implementation depth moved to falsify+atomic composition."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "(iv) post-call line mismatch" in defn
    assert "(v) implementation depth" not in defn


def test_atomic_stub_kind_dispatch():
    """Dim 13: stub requirement dispatches on symbol kind — closes non-callable stub gap."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "stub requirement for its kind" in defn


def test_atomic_stub_noncallable_path():
    """Dim 14: non-callable path explicitly named — variables/constants/exported values covered."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "non-callable (variable, constant, exported value, or class field)" in defn


def test_atomic_new_symbol_scoped_to_preceding_run_result():
    """Dim 15: new-symbol classification must use immediately preceding run result — closes session-history escape."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "immediately preceding run result, the symbol is new" in defn


def test_atomic_stub_callable_no_throw_panic():
    """Dim 16: callable stub must not permit throw/panic — closes stub-to-full escape via throw-produced FAIL."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "panic" not in defn or "throw" not in defn


# Rank repair tests (assay-cycle 2026-07-15, redesigned after falsify/atomic separation)

def test_atomic_rank4_symbol_identifier_line():
    """Rank 4: symbol commitment must appear as 'symbol: <identifier>' line."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "symbol: <identifier>" in defn


def test_atomic_rank5_stub_enumerated_values():
    """Rank 5: stub requirement lists specific zero-values syntactically."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "body/initializer contains only one of nil, null, undefined, 0, 0.0, false" in defn


def test_atomic_rank7_four_lines_contiguous():
    """Rank 7: five-line block must be consecutive with no intervening lines."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "The five lines must appear consecutively with no intervening lines" in defn


def test_atomic_rank9_scope_commitment_substring():
    """Rank 9 (C5): scope commitment text must be a literal substring of the preceding run result."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "literal substring of the immediately preceding run result" in defn


def test_atomic_same_turn_continuity():
    """Same-turn anchor: the (i)-(v) block and the tool call must appear in the same response turn."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "same response turn" in defn


def test_atomic_readiness_same_turn():
    """Readiness sentence must require continuation in the same turn — not cross-turn."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "The tool call must follow in the same response turn" in defn


def test_atomic_derivation_same_turn():
    """Derivation phase and first file-modifying tool call must appear in the same response turn."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "derivation phase and the first file-modifying tool call must appear in the same response turn" in defn


def test_atomic_no_implementation_depth_in_standalone():
    """(v) implementation depth belongs in falsify+atomic composition config, not atomic standalone."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "(v) implementation depth" not in defn


def test_atomic_impl_permitted_immediately_before_i():
    """§ implementation permitted [N] must appear immediately before the (i) line."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "immediately before the `(i)` line" in defn


def test_atomic_tool_call_same_turn_as_iv():
    """Tool call must follow in the same response turn as (iv) line."""
    defn = AXIS_KEY_TO_VALUE["method"]["atomic"]
    assert "tool call must follow in the same response turn" in defn

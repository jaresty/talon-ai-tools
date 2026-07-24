"""Tests asserting key literal strings for Clauses A and B (allow-list source + predicate constraint)
and the imported-contract reference exception.

Each test must FAIL before the edit and PASS after.

Gap: one composite-matcher failure could authorize many implementation identifiers by
seeding them into expected-value diffs. The allow-list must be sourced only from lines
that also contain (a); the exception permits imported-contract identifiers already
visible in prior Read results.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.axisConfig import AXIS_KEY_TO_VALUE


def defn():
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


# Clause A — allow-list source
def test_allowlist_requires_a_on_same_line():
    assert "Only identifiers that appear on a line in (g) that also contains (a) are valid allow-list entries" in defn()

def test_allowlist_excludes_non_a_lines():
    assert "an identifier that appears in (g) only on lines that do not contain (a) is not a valid allow-list entry" in defn()

# Clause B — one (a) line → one entry
def test_predicate_one_a_line_one_entry():
    assert "Each line in (g) that contains (a) authorizes at most one new allow-list entry" in defn()

def test_predicate_no_entry_without_d_identifier():
    assert "if no such identifier appears on that line beyond (a) itself, that line authorizes no new allow-list entry" in defn()

# Imported-contract reference exception
def test_imported_contract_exception_label():
    assert "Imported-contract reference exception" in defn()

def test_imported_contract_read_result_source():
    assert "appears as a declared member name in the content of a Read tool-result block appearing before the current Pre-edit block" in defn()

def test_imported_contract_allowlist_only():
    assert "this exception applies to the allow-list constraint only" in defn()

def test_imported_contract_branch_not_exempt():
    assert "does not exempt a branch construct whose condition or guard contains only imported-contract identifiers from the branch constraint" in defn()

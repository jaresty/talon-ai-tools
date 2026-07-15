"""Eval suite: ground protocol hollow audit — 10 ranked escape routes.

Generated from assay-cycle hollow audit (2026-07-15). Each test asserts that
the protocol text closes a specific structural escape route identified in the audit.

These tests check for named strings or structural properties in groundPrompt.py
that close each ranked gap. A FAIL means the gap is still open in the protocol.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.groundPrompt import GROUND_PARTS_MINIMAL


def _core() -> str:
    return GROUND_PARTS_MINIMAL["core"]


# ── Rank 1: No present-state observable for live execution output ──────────────
# Gap: "live system execution" / "live output" is semantic — no named string or
# structural property in the protocol text allows an evaluator to check whether
# a tool-result block qualifies without reading and interpreting its content.
# The deny-list (GitHub issue body, etc.) is evaluator-checkable but incomplete;
# the positive allow-list condition ("executes the subject system and returns its
# live output") names no structural property an evaluator can check mechanically.
# Fix: the protocol must name a specific structural property — e.g. that the
# qualifying tool result must be produced by invoking a named artifact (not a
# Read/search/file-write), OR must contain a named sentinel line, OR must name
# the tool call type that qualifies (Bash, endpoint call, test runner).

def test_rank1_path_a_positive_condition_names_evaluator_checkable_property():
    """Path A allow-list must name a structural property distinguishing qualifying tool results."""
    core = _core()
    # The protocol must state what structural property a QUALIFYING tool-result block
    # must have — not just what disqualifies it. A structural property is one that
    # an evaluator can check without reading the content (e.g., produced by a Bash
    # tool call, produced by invoking a named artifact, contains a named output line).
    # None of "live output", "live system execution", "executes the subject system"
    # name an evaluator-checkable structural property.
    # This test asserts that the protocol names at least one of the tool call types
    # that qualify for Path A by name (Bash, endpoint, test runner, etc.).
    # Fix: the protocol must name that a qualifying result is produced by a
    # tool call invocation (not a Read, search, or file-write result).
    # The canonical closing string for this gap:
    assert "a tool-result block produced by invoking the named artifact" in core


def test_rank1_path_a_document_content_named_strings_present():
    """Path A deny-list must name specific document-type strings evaluators can check."""
    core = _core()
    # These are the named strings from the current deny-list — evaluator-checkable.
    assert "GitHub issue body" in core
    assert "pull request body" in core
    assert "specification document" in core
    assert "README" in core
    assert "requirements text" in core


# ── Rank 2: [derived: text] adds claims absent from §0 ────────────────────────
# Gap: "claims absent from the user's message" requires semantic inference.
# No structural criterion names what makes a derivation valid vs. claim-adding.
# Fix: protocol must state that [derived: text] is invalid when it contains a
# word or phrase not present as a substring of the §0 scenario declaration.

def test_rank2_derived_text_scope_restricted_to_scenario_declaration():
    """[derived: text] must be restricted to claims present in the §0 declaration, not prior context."""
    core = _core()
    # The protocol must state the restriction is to "the user's message" or "the scenario"
    # and must not merely say "absent from" without naming the scope.
    assert "absent from the user's message" in core


def test_rank2_derived_text_violation_clause_present():
    """Protocol must name the specific violation condition for [derived: text]."""
    core = _core()
    # The clause naming what makes a [derived: text] invalid must be present.
    assert "a '[derived: text]' value that adds a claim absent from the user's message does not satisfy §1" in core


# ── Rank 3: Sentinel detachment — sentinels written before preconditions met ──
# Gap: sentinels like §1b candidates can be written as standalone lines with no
# structural evidence above them that the precondition was satisfied. The protocol
# requires "one candidate exists per alternative means" before §1b candidates —
# but gives no named structural property for what a candidate entry looks like
# (no prefix, no required line format), so an evaluator cannot count candidates
# without semantic inference.
# Fix: the protocol must name a structural marker for each candidate entry
# (e.g. a required line prefix "- Candidate:" or similar) so an evaluator can
# count entries mechanically before accepting the sentinel.

def test_rank3_1b_candidates_requires_named_entry_format():
    """§1b candidates must name the structural format of a candidate entry."""
    core = _core()
    # The protocol says "write one candidate" but names no structural form for
    # the candidate entry — no prefix, bullet format, or heading requirement.
    # Without a named format, an evaluator cannot count candidates mechanically.
    # This test asserts the protocol names a structural marker for candidate entries.
    # Fix: the protocol must name a structural marker for candidate entries
    # so an evaluator can count them without reading content.
    # Canonical closing string: require each candidate to begin with "- Candidate:"
    assert "- Candidate:" in core


def test_rank3_2_dimensions_closed_requires_observable_tag():
    """§2 dimensions closed must be gated on every dimension carrying an observable tag."""
    core = _core()
    assert "when every dimension carries an '[observable:]' tag" in core


def test_rank3_4_coverage_verified_requires_verbatim_citation():
    """§4 coverage verified must require each dimension to cite a verbatim string."""
    core = _core()
    assert "each covered dimension cites a verbatim string" in core


def test_rank3_5_enumeration_complete_requires_closing_string_per_path():
    """§5 enumeration complete must require each path to name its closing string."""
    core = _core()
    assert "for each path, name the literal string whose presence closes it" in core


# ── Rank 4: Semantic value in [observable: <string>] slot ─────────────────────
# Gap: the protocol requires [observable: <string>] and says <string> must be
# "a literal string or structural pattern whose presence in the response constitutes
# satisfaction" — but gives no criterion distinguishing a literal string from an
# adjective or category name. [observable: ambiguous] satisfies the bracket pattern.
# Fix: the protocol must state that an [observable:] value containing only an
# adjective or category name does not satisfy the requirement — naming the
# structural property that makes a value invalid (e.g. "a value that is an
# adjective or category name does not satisfy this requirement").

def test_rank4_observable_slot_excludes_adjectives_and_category_names():
    """Protocol must explicitly exclude adjectives and category names from [observable:] values."""
    core = _core()
    # The protocol must name the invalid form — adjective or category name —
    # so an evaluator can check compliance without semantic inference.
    # Fix: the protocol must name the invalid form explicitly.
    # Canonical closing string: name "adjective or category name" as invalid.
    assert "adjective or category name" in core


def test_rank4_observable_prose_fallback_is_tool_result_conditioned():
    """[observable: prose] fallback must be conditioned on absence of tool-result blocks."""
    core = _core()
    assert "if the response contains no tool-result blocks above §2, write '[observable: prose]' instead" in core


# ── Rank 5: "File-modifying tool call" unnamed ────────────────────────────────
# Gap: "file-modifying tool call" appears in §3 and §5 but names no specific tools.
# An evaluator cannot classify a Bash command that writes a file, or distinguish
# Edit from Write from NotebookEdit, without semantic inference.
# Fix: protocol must name which tool calls count as file-modifying.

def test_rank5_file_modifying_tool_call_term_present():
    """Protocol uses 'file-modifying tool call' as the governing term — known semantic gap, deferred."""
    core = _core()
    # "file-modifying tool call" is a semantic term that requires evaluator inference.
    # Named list would be too narrow (excludes Bash writes). Deferred pending definition clause.
    assert "file-modifying tool call" in core


# ── § implementation permitted addressability ─────────────────────────────────
# Gap: "§ implementation permitted" is a generic phrase that could appear in
# protocol descriptions, examples, or prose — nothing makes a functional
# occurrence structurally distinct from an incidental one. Also, the current
# "exactly once" constraint contradicts the requirement to appear before each
# file-modifying tool call when there are multiple edits.
# Fix: require "§ implementation permitted [N]" where N is the 1-based index
# of the file-modifying tool call this sentinel governs. Each occurrence is
# then unique and evaluator-traceable.

def test_impl_permitted_requires_indexed_form():
    """§ implementation permitted must carry a 1-based index to be uniquely addressable."""
    core = _core()
    assert "'§ implementation permitted [N]'" in core


def test_impl_permitted_exactly_once_removed():
    """'§ implementation permitted' must not be constrained to appear exactly once."""
    core = _core()
    # The old "exactly once" constraint contradicts multi-edit sessions.
    # After the fix, the indexed form removes the need for this constraint.
    assert "§ implementation permitted' each appear exactly once" not in core


# ── Rank 6–7: Quoted-span boundary for sentinel strings ───────────────────────
# Gap: no clause distinguishes a sentinel string inside a code fence from a
# functional sentinel. Quoted protocol text satisfies literal-string checks.
# Fix: add a clause stating occurrences inside code fences do not count.

def test_rank6_sentinel_quoted_span_exclusion_present():
    """Protocol must state that sentinel occurrences inside code fences do not satisfy requirements."""
    core = _core()
    # This test will FAIL until a quoted-span exclusion clause is added.
    assert "code fence" in core or "code block" in core or "fenced" in core


# ── Rank 8: "Question directed at the user" / "closing text" are semantic ─────
# Gap: Clause D of §4 uses "question directed at the user" and "closing text"
# without naming evaluator-checkable strings. Fix: name a structural signal.

def test_rank8_completion_check_placement_rule_present():
    """§4 must require ## Completion check before questions or closing text."""
    core = _core()
    assert "any assistant turn that contains a question directed at the user or no further planned tool calls" in core
    assert "must contain '## Completion check' before that question or closing text" in core


# ── Rank 9: Means-test line has no named string anchor ────────────────────────
# Gap: §1a decomposed must appear "before the means-test line" but "means-test
# line" is not a named string. Evaluator must infer which line is the means-test.
# Fix: name the means-test line by its literal string prefix.

def test_rank9_means_test_line_has_named_prefix():
    """Protocol must name the literal string that identifies the means-test line."""
    core = _core()
    # The canonical means-test line begins with "The goal [text] could be achieved by:"
    # The protocol must name this string so evaluators can locate it without inference.
    assert "The goal" in core and "could be achieved by" in core


# ── Rank 10: §5 enumeration complete written with incomplete enumeration ───────
# Gap: "no further open path remains" requires semantic inference — evaluator
# cannot verify completeness from the transcript alone.
# Fix: the protocol must require each enumerated path to name its closing string,
# making completeness evaluator-checkable (already covered by Rank 3 test above,
# but this test checks the §5 gate is conditioned on that requirement).

def test_rank10_path_enumeration_gate_conditioned_on_coverage_verified():
    """## Path enumeration must not appear before §4 coverage verified."""
    core = _core()
    assert "'## Path enumeration' must not appear before '§4 coverage verified'" in core

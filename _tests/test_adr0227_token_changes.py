"""Tests for ADR-0227 non-deferred token changes.

Behaviors under test:
1. ground: evidence quality — criterion that has only ever passed is not evidence
2. ground: termination trigger — completion check fires when governing artifact cycle exhausted
3. atomic: canonical term "governing output" used instead of "failure message"
4. chain: canonical term "governing output" used for implementation step predecessor
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.groundPrompt import GROUND_PARTS_MINIMAL, build_ground_prompt
from lib.axisConfig import AXIS_KEY_TO_VALUE


def _falsify() -> str:
    return AXIS_KEY_TO_VALUE["method"]["falsify"]


def _ground() -> str:
    return build_ground_prompt()


def _atomic() -> str:
    return AXIS_KEY_TO_VALUE["method"]["atomic"]


def _chain() -> str:
    return AXIS_KEY_TO_VALUE["method"]["chain"]


# --- ground: evidence quality (Decision 3) ---

def test_falsify_evidence_quality_requires_criterion_to_have_failed():
    """falsify must require a tool-executed result block showing the runner's assertion-failure marker.

    ADR-0227 Decision 3 (updated for derivation-based definition): falsify encodes the coverage
    guarantee by requiring the runner's failure-marker to precede each assertion identifier —
    a result block where assertions only pass does not satisfy the criterion.
    """
    text = _falsify()
    assert "assertion-failure marker" in text or "failure-marker" in text, (
        "falsify must require a runner failure-marker before each assertion identifier "
        "(derivation-based coverage guarantee — ADR-0227 Decision 3)"
    )


# --- ground: termination trigger (Decision 4) ---

def test_ground_states_completion_check_trigger_condition():
    """ground must name when the response is not permitted to end (completion check trigger).

    ADR-0227 Decision 4 (updated for derivation-based definition): ground states that
    the response cannot end until the '## Completion check' heading appears and at least one
    dimension is covered by a verbatim tool-executed result.

    The phrase 'completion-check heading' was removed in e558ddb9 when the definition was
    rewritten to use the literal heading string '## Completion check' as the gate.
    """
    text = _ground()
    assert (
        "'## Completion check'" in text and
        "dimension" in text and
        "verbatim" in text
    ), (
        "ground must state the completion-check trigger using the literal heading "
        "'## Completion check' — and at least one dimension covered by verbatim "
        "tool-executed result (ADR-0227 Decision 4, updated e558ddb9)"
    )


# --- atomic: governing output vocabulary (Decision 5) ---

def test_atomic_uses_governing_output_term():
    """atomic must anchor each edit to a literal string from the most recently produced run result.

    ADR-0227 Decision 5 (updated for derivation-based definition): atomic uses
    'most recently produced run result' as the scope commitment anchor, replacing
    the old 'governing output' / 'failure message' / 'failing-item line' vocabulary.
    """
    text = _atomic()
    assert "most recently produced run result" in text, (
        "atomic must anchor scope commitment to the most recently produced run result "
        "(ADR-0227 Decision 5, derivation-based form)"
    )


def test_atomic_defines_governing_output_on_first_use():
    """atomic must define the scope anchor as a literal string from the most recently produced run result.

    ADR-0227 Decision 5 (updated): scope commitment is defined as a literal string quoted
    from the most recently produced run result above each call.
    """
    text = _atomic()
    assert "scope commitment" in text and "most recently produced run result" in text, (
        "atomic must define scope commitment as a literal string from the most recently "
        "produced run result (ADR-0227 Decision 5, derivation-based form)"
    )


# --- falsify: governing-artifact exception (hollow audit fix) ---

def test_falsify_governing_artifact_creation_not_gated():
    """falsify must not gate governing artifact creation (test/spec file writing).

    hollow audit finding: the falsify definition used 'before implementation proceeds'
    without defining 'implementation', allowing agents to treat test-writing as gated.
    Fix: the definition must explicitly state that governing artifact creation is not
    subject to the FAIL gate — only non-governing file edits are gated.
    The structural definition of governing artifact must also be present.
    """
    text = _falsify()
    assert (
        "creation step" in text
    ) and (
        "absent before the action and present after it" in text
    ), (
        "falsify must explicitly exempt governing artifact creation from the result-block requirement, "
        "defined structurally: the governed action is the creation step only if (c) is absent before "
        "the action and present after it"
    )


# --- atomic: hollow audit fixes ---

def test_atomic_manifest_entry_requires_disappearance_criterion():
    """atomic scope commitment must require the quoted scope text to be absent after the edit.

    hollow audit finding 1 (updated for derivation-based definition): the old manifest entry
    clause required intent-assessment. The derivation-based atomic closes this by requiring
    the scope text (first failing-item line) to be absent from the post-edit run result —
    structurally verifiable without intent assessment.
    """
    text = _atomic()
    assert "quoted scope text is absent" in text or (
        "scope text" in text and "absent" in text
    ) or "quoted scope" in text, (
        "atomic must require the quoted scope text to be absent from the post-edit run result "
        "(derivation-based form of hollow audit fix 1)"
    )


def test_atomic_minimal_stub_defined_by_zero_extra_statements():
    """atomic symbol commitment must require naming every symbol before the call.

    hollow audit finding 2 (updated for derivation-based definition): the old 'minimal stub'
    clause required intent-assessment. The derivation-based atomic closes the isolation gap
    by requiring symbol commitment — every symbol the call will add or modify must be
    named above the call before it executes — structurally verifiable without intent assessment.
    """
    text = _atomic()
    assert "symbol commitment" in text, (
        "atomic must require symbol commitment — every symbol to be added or modified must "
        "be named above the call before it executes (derivation-based form of hollow audit fix 2)"
    )


def test_atomic_summary_line_defined_structurally():
    """atomic post-edit verification must check every other line from the pre-edit run result.

    hollow audit finding D1 (updated for derivation-based definition): the old summary-line
    exclusion required domain knowledge of test runner output. The derivation-based atomic
    closes this by requiring that every other line from the immediately preceding pre-edit
    run result is present in the post-edit run result — structurally verifiable by string match.
    """
    text = _atomic()
    assert "every other line" in text or (
        "immediately preceding pre-edit run result" in text and "present" in text
    ), (
        "atomic must require every other line from the pre-edit run result to be present "
        "in the post-edit run result (derivation-based form of hollow audit fix D1)"
    )


def test_atomic_multiple_scope_lines_quote_distinct_signals():
    """atomic scope commitment must be derived from the root criterion via enumeration.

    hollow audit finding D3 (updated for derivation-based definition): the old multiple-Scope
    cardinality clause required verifying intent. The derivation-based atomic closes this by
    requiring the model to enumerate every path by which the commitments could be satisfied
    without the call having changed exactly one independently observable behavior.
    """
    text = _atomic()
    assert "symbol commitment" in text and "(i) scope inflation" in text, (
        "atomic must require exactly one symbol commitment per call and enumerate escape "
        "categories — derivation-based form of hollow audit fix D3 (symbol cardinality + scope inflation)"
    )


def test_atomic_symbol_is_member_not_container():
    """atomic symbol commitment must reject a container reference as a valid symbol.

    kind constraint gap: a file name, module path, or import path satisfies the current
    provenance clause ('must appear as a literal substring of the quoted scope text') because
    import-error lines contain the file/module name verbatim. The fix adds a kind constraint:
    a symbol is a named member within a container, not the container itself.
    """
    text = _atomic()
    assert "named member within a container" in text or "names an entity whose existence is established within" in text, (
        "atomic symbol commitment must reject container references (file names, module paths) — "
        "a symbol is a named member within a container, not the container itself"
    )


def test_ground_unnamed_paths_require_structural_elimination():
    """ground must require that paths which cannot be closed by naming a string be eliminated structurally.

    hollow audit finding D4: a path enumeration escape route exists when a model encounters a
    path it cannot close by naming a literal string, and asserts closure rather than restructuring.
    ground closes this by requiring structural elimination — the required property must be present
    before the heading is written, not asserted after.
    This invariant moved from atomic to ground during the atomic rewrite (ADR-0227).
    """
    text = _ground()
    assert "'§5 enumeration complete'" in text, (
        "ground must require path enumeration to close with '§5 enumeration complete' — "
        "the 'cannot be closed by naming a string must be eliminated' phrasing was replaced "
        "in e558ddb9 with the literal sentinel '§5 enumeration complete'"
    )


def test_atomic_post_edit_verification_defines_assertion_text():
    """atomic post-edit verification must be structurally evaluable by string match.

    hollow audit finding (updated for derivation-based definition): the old 'assertion text' class
    was semantic. The derivation-based atomic closes this by requiring the quoted scope text to
    be absent and every other line from the pre-edit run result to be present — evaluable by
    string match without semantic assessment.
    """
    text = _atomic()
    assert "quoted scope text is absent" in text or (
        "scope text" in text and "absent" in text and "pre-edit run result" in text
    ), (
        "atomic post-edit verification must require the quoted scope text absent and pre-edit "
        "lines present — evaluable by string match (derivation-based hollow audit fix)"
    )


# --- atomic: allow-list closures for enablers 1/2/3 ---

def test_atomic_scope_commitment_is_backward_reference_only():
    """atomic scope commitment must be constrained to tool-executed results already present.

    hollow audit finding (enabler 3 — forward-reference ban): the scope commitment clause
    permits a model to write statements predicting whether a planned edit will satisfy the
    post-call check, using those predictions to justify larger-than-minimal implementations.
    Fix: the definition must state that each commitment is valid only if its truth value can
    be determined from tool-executed results already present above it in the transcript.
    """
    text = _atomic()
    assert (
        "already present" in text or "results already present above it" in text
    ), (
        "atomic must constrain scope commitment to tool-executed results already present "
        "above it in the transcript — forward-referencing statements are not valid commitments "
        "(hollow audit fix: enabler 3 forward-reference ban)"
    )


def test_atomic_scope_text_derives_from_most_recent_run_result():
    """atomic scope text must be a substring of the most recently produced run result before each call.

    hollow audit finding (enabler 1 — freshness gate): the scope commitment clause permits
    a quote whose source result has an intervening tool-executed run result between it and
    the call — the quote is stale but formally satisfies 'above that call'.
    Fix: the definition must state the quoted scope text must be a substring of the run result
    most recently produced before that specific call.
    """
    text = _atomic()
    assert (
        "most recently produced before that" in text or
        "intervening tool-executed run result" in text or
        ("most recent" in text and "before that specific call" in text) or
        "immediately preceding" in text
    ), (
        "atomic must require quoted scope text to derive from the run result most recently "
        "produced before that specific call — a stale quote with an intervening run result "
        "does not satisfy the scope commitment (hollow audit fix: enabler 1 freshness gate)"
    )


def test_atomic_symbol_commitment_bounded_by_scope_text():
    """atomic symbol commitment must bound named symbols to those derivable from the scope text.

    hollow audit finding (enabler 2 — symbol scope gate): the symbol commitment clause permits
    naming an unboundedly large set of symbols ('all behavior required by test 2, including
    A, B, C...'), satisfying the letter while implementing a full behavior.
    Fix: each named symbol must appear as a literal substring of the quoted scope text, or
    must be named in the failing-item line from the most recent tool-executed run result.
    """
    text = _atomic()
    assert (
        "literal substring of the quoted scope text" in text or
        "named in the failing-item line" in text or
        (
            "symbol" in text and
            "substring" in text and
            "scope text" in text
        )
    ), (
        "atomic must bound symbol commitment to symbols appearing in the quoted scope text "
        "or failing-item line — an unbounded symbol list does not satisfy the requirement "
        "(hollow audit fix: enabler 2 symbol scope gate)"
    )


def test_atomic_symbol_commitment_requires_exactly_one_symbol():
    """atomic symbol commitment must require exactly one symbol per file-modifying call.

    Gap D1/G2: the old definition said 'every symbol...must be named' — a completeness
    requirement, not a cardinality requirement. A model could name two symbols
    (createRadarAccountPortfolioRoutes, parseWholeCount) and implement both in one call.
    Fix: 'exactly one symbol' enforces cardinality=1.
    """
    text = _atomic()
    assert "exactly one symbol" in text, (
        "atomic must require exactly one symbol per file-modifying call — "
        "'every symbol' is a completeness requirement, not a cardinality requirement"
    )


def test_atomic_deny_list_sentence_present():
    """atomic must include a deny-list sentence making multi-symbol commitments non-compliant.

    The deny-list sentence closes the escape route where a model names two symbols
    and claims both are 'exactly one' by redefining 'symbol'. The sentence
    'a symbol commitment naming more than one symbol does not satisfy this requirement'
    makes multi-symbol commitments explicitly non-compliant.
    """
    text = _atomic()
    assert "a symbol commitment naming more than one symbol does not satisfy this requirement" in text, (
        "atomic must include deny-list sentence: "
        "'a symbol commitment naming more than one symbol does not satisfy this requirement'"
    )


def test_atomic_escape_category_iii_is_symbol_cardinality():
    """atomic escape category (iii) must be renamed from 'symbol under-declaration' to 'symbol cardinality'.

    The old label 'symbol under-declaration' targeted completeness (no undeclared symbols).
    After the cardinality fix, category (iii) now enforces count=1, not just completeness.
    The new label 'symbol cardinality' reflects this.
    """
    text = _atomic()
    assert "symbol cardinality" in text, (
        "atomic escape category (iii) must be labeled 'symbol cardinality' — "
        "'symbol under-declaration' only enforced completeness, not count=1"
    )


# --- chain: governing output vocabulary (Decision 5) ---

def test_chain_uses_governing_output_for_implementation_step_predecessor():
    """chain must use 'governing output' for the implementation step predecessor.

    ADR-0227 Decision 5: chain uses 'governing output' for the artifact output
    that serves as the predecessor for implementation steps (when gate is present).
    """
    text = _chain()
    assert "governing output" in text, (
        "chain must use 'governing output' for the implementation step predecessor "
        "artifact (ADR-0227 Decision 5)"
    )


# --- falsify: hollow audit fixes (2026-07-21) ---

def test_falsify_opening_clause_requires_assert_call_expression():
    """falsify opening clause must constrain the tool-result block to contain assert call expression substring.

    hollow audit finding 1: 'tool-result block containing the FAIL' does not forward-reference
    (a) or (c); surface FAIL match suffices. Fix: the opening clause must require the failure
    line to contain a substring from the governed assertion call expression.
    """
    text = _falsify()
    assert (
        "governed assertion" in text and
        "call expression" in text
    ), (
        "falsify opening clause must require the failure line to contain a substring from "
        "the governed assertion call expression — surface FAIL match is insufficient "
        "(hollow audit fix 1, 2026-07-21)"
    )


def test_falsify_named_artifact_identifier_is_file_path():
    """falsify must define named governing artifact identifier as file path, not any substring.

    hollow audit finding 2: 'identifier' boundary undefined; any substring of the executor
    invocation qualifies. Fix: must specify that the file path appears as an argument to
    the executor invocation, not a package name or directory.
    """
    text = _falsify()
    assert (
        "file path" in text and
        "argument" in text
    ), (
        "falsify must define named governing artifact as one whose file path appears as an "
        "argument to the executor invocation — not any substring (hollow audit fix 2, 2026-07-21)"
    )


def test_falsify_clause_e_direct_call_defined_by_nesting():
    """falsify clause (e) must define 'direct call' as structural nesting property.

    hollow audit finding 3: 'direct call' requires semantic inference on call depth. Fix: must
    state the call expression is not nested inside another call expression naming a different symbol.
    """
    text = _falsify()
    assert (
        "nested" in text and
        "call expression" in text
    ), (
        "falsify clause (e) must define unit layer via structural call-expression nesting, "
        "not semantic inference on call depth (hollow audit fix 3, 2026-07-21)"
    )


def test_falsify_clause_f_disposable_defined_by_c_absence():
    """falsify clause (f) must define disposable artifact as one where (c) does not appear after removal.

    hollow audit finding 4: 'executor result unchanged' baseline undefined. Fix: must state
    'produces an executor result in which (c) does not appear'.
    """
    text = _falsify()
    assert "(c) does not appear" in text, (
        "falsify clause (f) must define disposable artifact as one where removing the governed "
        "symbol produces an executor result in which (c) does not appear "
        "(hollow audit fix 4, 2026-07-21)"
    )


def test_falsify_clause_g_assert_substring_names_callee():
    """falsify clause (g) must define assert substring via callee name containing governed symbol.

    hollow audit finding 5: 'assert statement' allows any test body line by semantic inference.
    Fix: must name the callee of the governed assertion call expression as the structural marker.
    """
    text = _falsify()
    assert (
        "callee" in text and
        "call expression" in text
    ), (
        "falsify clause (g) must define the assert substring as from the governed assertion "
        "call expression whose callee contains the governed symbol name — not any test body line "
        "(hollow audit fix 5, 2026-07-21)"
    )


def test_falsify_per_behavior_scoping_fixed_at_derivation_time():
    """falsify per-behavior scoping must lock the behavior name at derivation time.

    hollow audit finding 6: 'named behavior' grain unconstrained; model can reframe post-hoc.
    Fix: behavior name must be fixed at derivation time via the (d) entry.
    """
    text = _falsify()
    assert "derivation time" in text, (
        "falsify per-behavior scoping must fix the behavior name at derivation time via the (d) "
        "entry — post-hoc reframing to match an existing FAIL is not permitted "
        "(hollow audit fix 6, 2026-07-21)"
    )

"""Tests for groundPrompt — current slim form (ADR-0224: ground slimmed to A0+M only)."""
from lib.groundPrompt import build_ground_prompt


def test_opening_bookend_inside_criteria():
    """Opening bookend is criterion (0) inside the derivation sequence, not an external pre-condition."""
    text = build_ground_prompt()
    assert "invoke the named artifact as a tool call" in text, (
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


def test_path_a_behavioral_criterion():
    """Path A artifact criterion requires live system execution, not syntactic form."""
    text = build_ground_prompt()
    assert "executes the subject system and returns its live output" in text, (
        "Path A must require artifact to execute subject system and return live output"
    )
    assert "file path, repo URL, endpoint, or shell command" not in text, (
        "old syntactic artifact-type list must be removed from Path A classification"
    )


def test_path_a_disqualifying_forms():
    """Path A §0 satisfaction condition must name specific disqualifying content types."""
    text = build_ground_prompt()
    assert "a tool result consisting of a GitHub issue body" in text, (
        "§0 satisfaction condition must name GitHub issue body as disqualifying form"
    )


def test_path_a_invocation_form_escape():
    """Path A must close the 'regardless of invocation form' escape."""
    text = build_ground_prompt()
    assert "regardless of invocation form" in text, (
        "§0 must state disqualification applies regardless of invocation form"
    )


def test_goal_source_status_only_sentinel():
    """Fix 1: §0 status-only sentinel must be named for execution-status-only §0 results."""
    text = build_ground_prompt()
    assert "§0 status-only" in text, (
        "ground must name §0 status-only as the sentinel when §0 result contains no user-message substring"
    )


def test_goal_source_requires_external_fetch():
    """Fix 1: ## Governing goal: must not appear before a qualifying tool-result block when §0 status-only."""
    text = build_ground_prompt()
    assert "§0 status-only" in text and "## Governing goal:" in text, (
        "ground must gate ## Governing goal: on an external-fetch tool-result block when §0 status-only"
    )


def test_goal_source_substring_gate():
    """Fix 1: qualifying tool-result must contain a line that appears as substring of a user message."""
    text = build_ground_prompt()
    assert "appears as a substring of a user message" in text, (
        "ground must require fetched content to contain a line appearing as substring of a user message"
    )


def test_continuation_invariant_blocked_sentinel():
    """Continuation invariant: § blocked: must be named as a valid turn-end exit string."""
    text = build_ground_prompt()
    assert "§ blocked:" in text, (
        "ground must name § blocked: as a valid exit string when a rung-completion string is the final content"
    )


def test_continuation_invariant_awaiting_sentinel():
    """Continuation invariant: § awaiting: must be named as a valid turn-end exit string."""
    text = build_ground_prompt()
    assert "§ awaiting:" in text, (
        "ground must name § awaiting: as a valid exit string when a rung-completion string is the final content"
    )


def test_continuation_invariant_no_next_action_sentinel():
    """Continuation invariant: § no-next-action: must be named as a valid turn-end exit string."""
    text = build_ground_prompt()
    assert "§ no-next-action:" in text, (
        "ground must name § no-next-action: as a valid exit string when a rung-completion string is the final content"
    )


def test_1a_decomposed_precedes_1_goal_derived():
    """§1 goal derived must not appear before §1a decomposed — ordering gate must be explicit."""
    text = build_ground_prompt()
    assert "'§1 goal derived' must not appear before '§1a decomposed'" in text, (
        "ground must gate §1 goal derived on §1a decomposed having appeared first in the transcript"
    )


def test_deep_ladder_ambiguity_test_clause_present():
    """ADR-XXXX: ground must require deepest possible ladder via ambiguity test, not prescribe example rungs."""
    text = build_ground_prompt()
    assert "ambiguity test" in text, (
        "ground must contain the ambiguity test derivation clause — "
        "the 'One example ladder' hint is not sufficient"
    )
    assert "that phrase names the subject of the next rung" in text, (
        "ground must name the mechanical derivation rule: the ambiguous phrase names the next rung's subject"
    )
    assert "One example ladder" not in text, (
        "example ladder hint must be replaced by the derivation principle"
    )


def test_formalization_sentinel_present():
    """Ground must contain § formalization complete sentinel gating enforcement sequence."""
    text = build_ground_prompt()
    assert "§ formalization complete" in text, (
        "ground must require the § formalization complete sentinel before ## Enforcement sequence"
    )
    assert "## Formalization" in text, (
        "ground must name ## Formalization as a required heading — detectable without semantic inference"
    )


def test_rung_rejects_isolation_present():
    """Ground must require § rung rejects: prefix on each rung to enforce predecessor isolation."""
    text = build_ground_prompt()
    assert "§ rung rejects:" in text, (
        "ground must require § rung rejects: prefix quoting a verbatim phrase from the preceding rung"
    )


def test_quoted_span_exclusion_covers_block_quotes():
    """E-07: quoted-span exclusion must cover block-quote lines ('>'), not just code fences.
    Eval G v3 confirmed: '> §1 goal derived' was accepted as satisfying the ordering gate."""
    text = build_ground_prompt()
    assert "does not begin with '>'" in text, (
        "quoted-span exclusion must name block-quote lines (beginning with '>') explicitly — "
        "eval G v3 showed a model writing '> §1 goal derived' accepted as satisfying ordering gate"
    )


def test_implementation_permitted_no_intervening_content():
    """E-08: no blank line or content may appear between § implementation permitted and (i) line."""
    text = build_ground_prompt()
    assert "no intervening blank lines" in text, (
        "ground must state that no blank line or intervening content may appear between "
        "'§ implementation permitted [N]' and the '(i)' line — "
        "eval H showed a model inserting '---' between them and satisfying the current clause"
    )


def test_implementation_permitted_requires_decimal_integer():
    """E-01: § implementation permitted sentinel must require a decimal integer, not literal [N].
    Eval J confirmed: model emitted bare '§ implementation permitted' with no integer."""
    text = build_ground_prompt()
    assert "decimal integer" in text, (
        "ground must require a decimal integer after '§ implementation permitted' — "
        "eval J showed a model emitting the bare sentinel with no index at all"
    )
    assert "literal bracket characters" in text or "does not satisfy this requirement — only a decimal integer" in text, (
        "ground must explicitly state that the literal '[N]' form does not satisfy the index requirement"
    )


def test_rung_completion_sentinel_finality():
    """E-06: rung-completion sentinels must be the final non-blank line of their turn.
    Eval L confirmed: model emitted §5 enumeration complete then continued writing prose."""
    text = build_ground_prompt()
    assert "Rung-completion sentinel finality" in text, (
        "ground must contain a sentinel finality clause preventing prose from following "
        "a rung-completion sentinel in the same turn — "
        "eval L showed §5 enumeration complete followed by non-sentinel prose"
    )
    assert "no prose, heading, or non-sentinel content may follow" in text, (
        "ground must explicitly state that no content may follow a rung-completion sentinel in the same turn"
    )

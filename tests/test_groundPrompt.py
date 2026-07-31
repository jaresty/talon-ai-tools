"""Tests for groundPrompt — current slim form (ADR-0224: ground slimmed to A0+M only)."""
from lib.groundPrompt import build_ground_prompt


def test_opening_bookend_inside_criteria():
    """Opening bookend is §0: [scenario] — opens ladder unconditionally, artifact invocation is conditional."""
    text = build_ground_prompt()
    assert "§0: [scenario]" in text, (
        "§0: [scenario] must appear as the unified §0 opening sentinel"
    )
    assert "Before writing the governing goal heading, run the system under test" not in text, (
        "old external pre-condition form must be removed"
    )


def test_closing_bookend_names_subject_directly():
    """Closing bookend requires tool-result substring via §4 coverage verified sentinel (CL2 gate)."""
    text = build_ground_prompt()
    assert "every covered dimension cites a property number and such a substring" in text, (
        "closing bookend must require property number citation and tool-result substring"
    )
    assert "'§4 coverage verified' is valid only after '§ test suite complete'" in text, (
        "§4 coverage verified must be gated on § test suite complete"
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


def test_goal_source_conditional_on_observed():
    """§1: governing goal source is conditional — verbatim from tool-result if §0 observed, else from scenario."""
    text = build_ground_prompt()
    assert "if '§0 observed' is present" in text or "§0 observed' is absent" in text, (
        "ground must make governing goal source conditional on §0 observed presence"
    )
    assert "§0 tool-result block above" in text, (
        "ground must require [text] verbatim from §0 tool-result when §0 observed is present"
    )
    assert "derived from the scenario description" in text, (
        "ground must allow goal derivation from scenario when §0 observed is absent"
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
    """§1 goal derived triggered by §1 check — allow-list enforces ordering after §1a decomposed."""
    text = build_ground_prompt()
    assert "after a valid '§1 check:' line has appeared, immediately write '§1 goal derived'" in text, (
        "ground must gate §1 goal derived on §1 check via allow-list trigger"
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


def test_notation_derived_sentinel_required():
    """Ground must require § notation derived: before Formalized properties:."""
    text = build_ground_prompt()
    assert "§ notation derived:" in text, (
        "ground must require the § notation derived: sentinel before Formalized properties:"
    )
    assert "immediately after '§ notation derived:', write the label line 'Formalized properties:'" in text, (
        "ground must require Formalized properties: immediately after § notation derived: (positive predecessor)"
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


def test_formalization_complete_gated_on_ambiguity_test_and_alternative_satisfier():
    """E-03: § formalization complete must not appear before § ambiguity test: and alternative satisfier:.
    Eval K confirmed: model skipped § ambiguity test: entirely and jumped to § formalization complete.
    Hollow audit: bracket as first char = unfilled template = does not satisfy."""
    text = build_ground_prompt()
    assert "'§ formalization complete' must not appear before '§ ambiguity test:'" in text, (
        "ground must gate § formalization complete on § ambiguity test: having appeared first"
    )
    assert "valid 'alternative satisfier:' line" in text, (
        "ground must gate § formalization complete on a valid alternative satisfier: line"
    )
    assert "unfilled template" in text, (
        "ground must disqualify bracket-prefixed alternative satisfier: lines as unfilled templates"
    )


def test_implementation_permitted_requires_decimal_integer():
    """E-01: § implementation permitted sentinel must require a decimal integer, not literal [N].
    Eval J confirmed: model emitted bare '§ implementation permitted' with no integer.
    Hollow audit: 'governs' was semantic — replaced with positional ordinal count."""
    text = build_ground_prompt()
    assert "decimal integer" in text, (
        "ground must require a decimal integer after '§ implementation permitted'"
    )
    assert "ordinal count" in text or "ordinal position" in text, (
        "ground must use positional ordinal count, not semantic 'governs' relationship"
    )
    assert "bracket character" in text, (
        "ground must explicitly disqualify bracket characters as unfilled template markers"
    )


def test_closing_sentinel_addressability_checks():
    """Closing-sentinel addressability: each sentinel must be preceded by a check line
    quoting verbatim from the current rung's output — forces content to exist before sentinel."""
    text = build_ground_prompt()
    assert "'§1a check:'" in text or "§1a check:" in text, (
        "ground must require §1a check: quoting verbatim from labeled fields before §1a decomposed"
    )
    assert "'§1 check:'" in text or "§1 check:" in text, (
        "ground must require §1 check: quoting verbatim from means-test before §1 goal derived"
    )
    assert "'§1b check:'" in text or "§1b check:" in text, (
        "ground must require §1b check: quoting verbatim from candidate lines before §1b candidates"
    )
    assert "'§2 check:'" in text or "§2 check:" in text, (
        "ground must require §2 check: quoting verbatim from [observable:] tags before §2 dimensions closed"
    )
    assert "'§5 check:'" in text or "§5 check:" in text, (
        "ground must require §5 check: quoting verbatim from path enumeration before §5 enumeration complete"
    )


def test_sentinel_formatting_requirement():
    """Sentinel lines must begin with literal § or # character — markdown formatting does not satisfy."""
    text = build_ground_prompt()
    assert "sentinel line beginning with '**' or any other markdown formatting character does not satisfy" in text, (
        "ground must require sentinel lines to begin with literal § or # character"
    )

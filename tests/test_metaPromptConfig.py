"""Tests for metaPromptConfig helpers (ADR-0176)."""
import importlib


def test_prompt_reference_key_as_text_contains_kanji():
    """Thread 1: prompt_reference_key_as_text() returns a string containing 任務 (TASK kanji)."""
    from lib.metaPromptConfig import prompt_reference_key_as_text

    text = prompt_reference_key_as_text()
    assert isinstance(text, str), "expected a string"
    assert "任務" in text, "expected kanji 任務 in reference key text"


def test_task_contract_is_short_inline_not_heading():
    """Thread 3: PROMPT_REFERENCE_KEY['task'] is a short inline contract, not a section heading."""
    from lib.metaPromptConfig import PROMPT_REFERENCE_KEY

    task_contract = PROMPT_REFERENCE_KEY["task"]
    assert not task_contract.startswith("TASK"), (
        f"expected short inline contract without heading prefix, got: {task_contract[:60]!r}"
    )


def test_channel_axis_text_contains_exec_persona_resolution():
    """Cycle-31 R-31-01: _AXIS_FULL_TEXT['channel'] must describe how to resolve exec/executive_brief
    persona co-presence with executable channels (shellscript, code, gherkin, codetour)."""
    from lib.metaPromptConfig import _AXIS_FULL_TEXT

    channel_text = _AXIS_FULL_TEXT["channel"]
    assert "exec" in channel_text or "executive_brief" in channel_text, (
        "expected exec persona resolution rule in _AXIS_FULL_TEXT['channel']"
    )
    assert any(tok in channel_text for tok in ("shellscript", "gherkin", "codetour")), (
        "expected executable channel tokens (shellscript, gherkin, codetour) in _AXIS_FULL_TEXT['channel']"
    )


def test_form_axis_text_contains_prep_vet_resolution():
    """Cycle-31 R-31-03: _AXIS_FULL_TEXT['form'] must describe the prep+vet hollow-cycle resolution
    (an action step must appear between prep and vet)."""
    from lib.metaPromptConfig import _AXIS_FULL_TEXT

    form_text = _AXIS_FULL_TEXT["form"]
    assert "prep" in form_text and "vet" in form_text, (
        "expected prep and vet mentioned in _AXIS_FULL_TEXT['form'] hollow-cycle resolution"
    )
    assert "action" in form_text or "execution" in form_text, (
        "expected action/execution step guidance in _AXIS_FULL_TEXT['form'] for prep+vet"
    )


def test_task_reference_key_root_criterion():
    """token-rewrite BD1: PROMPT_REFERENCE_KEY['task'] uses root-criterion form with 'TASK is the sole authoritative task source'."""
    from lib.metaPromptConfig import PROMPT_REFERENCE_KEY

    task_text = PROMPT_REFERENCE_KEY["task"]
    assert "TASK is the sole authoritative task source" in task_text, (
        f"expected root-criterion phrase 'TASK is the sole authoritative task source' in task definition, got: {task_text[:120]!r}"
    )
    assert "Takes precedence over all other sections." not in task_text, (
        "old procedural phrase 'Takes precedence over all other sections.' must be removed in favour of root-criterion form"
    )


def test_execution_reminder_structural_delimiter():
    """token-rewrite BD2: EXECUTION_REMINDER names 'tool call result block' as structural delimiter for content gate."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "tool call result block" in EXECUTION_REMINDER, (
        "expected structural delimiter 'tool call result block' in EXECUTION_REMINDER"
    )


def test_planning_directive_outer_imperative():
    """token-rewrite BD3a: PLANNING_DIRECTIVE opens with unconditional existence mandate closing zero-instance escape."""
    from lib.metaPromptConfig import PLANNING_DIRECTIVE

    assert "The response must contain a planning block" in PLANNING_DIRECTIVE, (
        "expected outer imperative 'The response must contain a planning block' in PLANNING_DIRECTIVE; "
        "old 'begins with SECTION 1 —' form has zero-instance escape"
    )


def test_planning_directive_no_begins_with_escape():
    """token-rewrite BD3b: PLANNING_DIRECTIVE must not open with description-first 'begins with' clause (zero-instance escape)."""
    from lib.metaPromptConfig import PLANNING_DIRECTIVE

    assert not PLANNING_DIRECTIVE.startswith("The response planning block begins with"), (
        "PLANNING_DIRECTIVE must not begin with descriptive 'begins with' clause — "
        "absence of planning block is not a violation of a 'begins with' claim"
    )


def test_planning_directive_allow_list_form():
    """token-rewrite BD3c: PLANNING_DIRECTIVE uses allow-list form ('is text output') not deny-list ('no tool call result block')."""
    from lib.metaPromptConfig import PLANNING_DIRECTIVE

    assert "all content between 'SECTION 1 —' and 'SECTION 4 —' is text output" in PLANNING_DIRECTIVE, (
        "expected allow-list clause 'all content between ... is text output' in PLANNING_DIRECTIVE; "
        "deny-list 'no tool call result block appears' must be converted"
    )


def test_meta_interpretation_context_position():
    """token-rewrite BD4: META_INTERPRETATION_GUIDANCE names 'tool call result block or user message' as structural position for Suggestion gate."""
    from lib.metaPromptConfig import META_INTERPRETATION_GUIDANCE

    assert "tool call result block or user message" in META_INTERPRETATION_GUIDANCE, (
        "expected structural position 'tool call result block or user message' in META_INTERPRETATION_GUIDANCE Suggestion gate"
    )


def test_execution_reminder_root_criterion_phrase():
    """token-rewrite BD1: EXECUTION_REMINDER opens with permit-condition form naming the transcript as evaluated artifact."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "A transcript satisfies this requirement when" in EXECUTION_REMINDER, (
        "expected root criterion phrase 'A transcript satisfies this requirement when' in EXECUTION_REMINDER; "
        "old gate phrasing 'The response produces content only after' must be replaced"
    )


def test_execution_reminder_evaluator_framing():
    """token-rewrite BD2: EXECUTION_REMINDER names an evaluator scanning the complete transcript as the compliance check agent."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "an evaluator scanning the complete transcript determines compliance" in EXECUTION_REMINDER, (
        "expected evaluator framing 'an evaluator scanning the complete transcript determines compliance' in EXECUTION_REMINDER"
    )


def test_execution_reminder_web_context_permit():
    """token-rewrite BD3: EXECUTION_REMINDER permits trigger string in TASK section of prompt for web/no-tool-call contexts."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "or in the TASK section of this prompt" in EXECUTION_REMINDER, (
        "expected web context permit 'or in the TASK section of this prompt' in EXECUTION_REMINDER; "
        "satisfiability requires covering non-tool-call contexts"
    )


def test_execution_reminder_no_deny_list_clause():
    """token-rewrite BD4: EXECUTION_REMINDER must not contain deny-list clause implying real-time model checking."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "content produced before that string appears does not satisfy" not in EXECUTION_REMINDER, (
        "deny-list clause 'content produced before that string appears does not satisfy' must be removed from EXECUTION_REMINDER; "
        "it implies real-time model checking rather than post-hoc evaluator compliance"
    )


def test_execution_reminder_no_gate_phrasing():
    """token-rewrite BD5: EXECUTION_REMINDER must not contain pre-execution gate phrasing that blocks model output."""
    from lib.metaPromptConfig import EXECUTION_REMINDER

    assert "The response produces content only after" not in EXECUTION_REMINDER, (
        "gate phrasing 'The response produces content only after' must be removed from EXECUTION_REMINDER; "
        "it reads as a pre-execution wait condition rather than an evaluator compliance criterion"
    )


def test_model_types_uses_helper_not_raw_dict():
    """Thread 2: modelTypes.py calls prompt_reference_key_as_text(), not PROMPT_REFERENCE_KEY.strip()."""
    import ast
    import pathlib

    source = pathlib.Path("lib/modelTypes.py").read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Detect .strip() called on PROMPT_REFERENCE_KEY attribute access
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "strip"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "PROMPT_REFERENCE_KEY"
            ):
                raise AssertionError(
                    f"modelTypes.py calls PROMPT_REFERENCE_KEY.strip() at line {node.lineno}; "
                    "should call prompt_reference_key_as_text() instead"
                )

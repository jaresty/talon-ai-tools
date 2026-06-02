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

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

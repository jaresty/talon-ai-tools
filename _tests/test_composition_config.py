"""Tests for ADR-0227 Decision 1: compositionConfig.py and grammar JSON export.

Python layer governing artifact.
"""

import sys
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_compositions_non_empty():
    from lib.compositionConfig import COMPOSITIONS
    assert len(COMPOSITIONS) > 0, "COMPOSITIONS must be non-empty"


def test_each_composition_has_required_fields():
    from lib.compositionConfig import COMPOSITIONS
    for comp in COMPOSITIONS:
        assert "name" in comp and comp["name"], f"composition missing name: {comp}"
        assert "tokens" in comp and len(comp["tokens"]) >= 2, f"{comp.get('name')}: tokens must have ≥2 entries"
        assert "prose" in comp and comp["prose"], f"{comp.get('name')}: prose must be non-empty"


def test_four_named_compositions_exist():
    from lib.compositionConfig import COMPOSITIONS
    names = {c["name"] for c in COMPOSITIONS}
    assert "ground+gate" in names, "ground+gate composition missing"
    assert "gate+atomic" in names, "gate+atomic composition missing"
    assert "gate+chain" in names, "gate+chain composition missing"
    assert "atomic+ground" in names, "atomic+ground composition missing"


def test_composition_tokens_are_valid_method_tokens():
    from lib.compositionConfig import COMPOSITIONS
    from lib.axisConfig import AXIS_KEY_TO_VALUE
    method_tokens = set(AXIS_KEY_TO_VALUE.get("method", {}).keys())
    for comp in COMPOSITIONS:
        for token in comp["tokens"]:
            assert token in method_tokens, (
                f"{comp['name']}: token {token!r} not found in method axis"
            )


def test_grammar_json_contains_compositions():
    grammar_path = ROOT / "build" / "prompt-grammar.json"
    assert grammar_path.exists(), "build/prompt-grammar.json must exist"
    data = json.loads(grammar_path.read_text())
    assert "compositions" in data, "prompt-grammar.json must contain 'compositions' key"
    assert isinstance(data["compositions"], list), "'compositions' must be a list"
    assert len(data["compositions"]) >= 4, "must have at least 4 compositions"


def test_grammar_json_composition_entries_have_required_fields():
    grammar_path = ROOT / "build" / "prompt-grammar.json"
    data = json.loads(grammar_path.read_text())
    for comp in data.get("compositions", []):
        assert "name" in comp, f"composition entry missing name: {comp}"
        assert "tokens" in comp, f"{comp.get('name')}: missing tokens"
        assert "prose" in comp, f"{comp.get('name')}: missing prose"

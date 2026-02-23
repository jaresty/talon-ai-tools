"""Kanji validation tests - ensures kanji meet constraints (ADR-0143)."""

import pytest
import json
from pathlib import Path


def load_grammar():
    """Load the prompt grammar JSON."""
    grammar_path = Path("web/static/prompt-grammar.json")
    if not grammar_path.exists():
        grammar_path = Path("build/prompt-grammar.json")
    with open(grammar_path) as f:
        return json.load(f)


class TestKanjiConstraints:
    """Validate kanji character constraints across all tokens."""

    def test_kanji_character_length(self):
        """All kanji values must be 1-3 characters max."""
        grammar = load_grammar()

        # Check axis kanji
        for axis_name, kanji_map in grammar.get("axes", {}).get("kanji", {}).items():
            for token, kanji in kanji_map.items():
                assert 1 <= len(kanji) <= 3, (
                    f"Kanji for {axis_name}:{token} is {len(kanji)} chars "
                    f"(expected 1-3): '{kanji}'"
                )

        # Check task kanji
        for token, kanji in grammar.get("tasks", {}).get("kanji", {}).items():
            assert 1 <= len(kanji) <= 3, (
                f"Kanji for task:{token} is {len(kanji)} chars "
                f"(expected 1-3): '{kanji}'"
            )

        # Check persona kanji
        persona_kanji = grammar.get("persona", {}).get("kanji", {})
        for axis_name, kanji_map in persona_kanji.items():
            if isinstance(kanji_map, dict):
                for token, kanji in kanji_map.items():
                    assert 1 <= len(kanji) <= 3, (
                        f"Kanji for persona.{axis_name}:{token} is {len(kanji)} chars "
                        f"(expected 1-3): '{kanji}'"
                    )

    def test_kanji_valid_unicode(self):
        """All kanji must be valid Unicode characters."""
        grammar = load_grammar()

        def check_unicode(kanji, location):
            try:
                kanji.encode('utf-8')
                # Ensure it's in a reasonable Unicode range (CJK blocks)
                for char in kanji:
                    code = ord(char)
                    # Basic CJK ranges - not exhaustive but catches most issues
                    valid = (
                        (0x3000 <= code <= 0x303F) or  # CJK Symbols
                        (0x3040 <= code <= 0x309F) or  # Hiragana
                        (0x30A0 <= code <= 0x30FF) or  # Katakana
                        (0x4E00 <= code <= 0x9FFF) or  # CJK Unified Ideographs
                        (0xF900 <= code <= 0xFAFF) or  # CJK Compatibility
                        (0x3400 <= code <= 0x4DBF)     # CJK Extension A
                    )
                    assert valid, f"Character '{char}' at {location} is not in CJK Unicode range"
            except UnicodeError:
                pytest.fail(f"Invalid Unicode in kanji at {location}: {repr(kanji)}")

        # Check all kanji
        for axis_name, kanji_map in grammar.get("axes", {}).get("kanji", {}).items():
            for token, kanji in kanji_map.items():
                check_unicode(kanji, f"{axis_name}:{token}")

        for token, kanji in grammar.get("tasks", {}).get("kanji", {}).items():
            check_unicode(kanji, f"task:{token}")

        persona_kanji = grammar.get("persona", {}).get("kanji", {})
        for axis_name, kanji_map in persona_kanji.items():
            if isinstance(kanji_map, dict):
                for token, kanji in kanji_map.items():
                    check_unicode(kanji, f"persona.{axis_name}:{token}")

    def test_kanji_no_duplicates_within_axis(self):
        """No duplicate kanji assignments within the same axis."""
        grammar = load_grammar()

        # Check each axis for duplicates
        for axis_name, kanji_map in grammar.get("axes", {}).get("kanji", {}).items():
            seen = {}
            for token, kanji in kanji_map.items():
                if kanji in seen:
                    pytest.fail(
                        f"Duplicate kanji '{kanji}' in {axis_name}: "
                        f"used by both '{seen[kanji]}' and '{token}'"
                    )
                seen[kanji] = token

        # Check tasks for duplicates
        task_kanji = grammar.get("tasks", {}).get("kanji", {})
        seen_tasks = {}
        for token, kanji in task_kanji.items():
            if kanji in seen_tasks:
                pytest.fail(
                    f"Duplicate kanji '{kanji}' in tasks: "
                    f"used by both '{seen_tasks[kanji]}' and '{token}'"
                )
            seen_tasks[kanji] = token

        # Check persona axes for duplicates
        persona_kanji = grammar.get("persona", {}).get("kanji", {})
        for axis_name, kanji_map in persona_kanji.items():
            if isinstance(kanji_map, dict):
                seen_persona = {}
                for token, kanji in kanji_map.items():
                    if kanji in seen_persona:
                        pytest.fail(
                            f"Duplicate kanji '{kanji}' in persona.{axis_name}: "
                            f"used by both '{seen_persona[kanji]}' and '{token}'"
                        )
                    seen_persona[kanji] = token

    def test_kanji_persistence_roundtrip(self):
        """Kanji must survive serialization round-trip."""
        grammar = load_grammar()

        # Re-serialize and parse
        serialized = json.dumps(grammar, ensure_ascii=False)
        roundtrip = json.loads(serialized)

        # Verify kanji are preserved
        original_kanji = grammar.get("axes", {}).get("kanji", {})
        roundtrip_kanji = roundtrip.get("axes", {}).get("kanji", {})

        assert original_kanji == roundtrip_kanji, (
            "Kanji lost during JSON round-trip serialization"
        )

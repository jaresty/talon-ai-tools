import pytest
from lib.axisConfig import AXIS_KEY_TO_KANJI
from lib.personaConfig import PERSONA_KEY_TO_KANJI


def _check_kanji(violations: list, prefix: str, kanji_map: dict):
    """Recursively check kanji values are single character."""
    for key, value in kanji_map.items():
        if isinstance(value, dict):
            _check_kanji(violations, f"{prefix}:{key}", value)
        else:
            char_count = len(value)
            if char_count != 1:
                violations.append(f"{prefix}:{key} = '{value}' ({char_count} chars)")


def test_all_kanji_are_single_character():
    """Verify all kanji mappings are exactly 1 character for TUI2 alignment (ADR-0143)."""
    violations = []
    _check_kanji(violations, "axis", AXIS_KEY_TO_KANJI)
    _check_kanji(violations, "persona", PERSONA_KEY_TO_KANJI)

    if violations:
        pytest.fail("Found multi-character kanji:\n" + "\n".join(violations))

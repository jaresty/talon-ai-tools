"""Governing tests for ADR-0236: topology axis in metaPromptConfig.py.

These tests must FAIL before implementation and PASS after.
"""
import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.metaPromptConfig import (
        PROMPT_REFERENCE_KEY,
        PLANNING_DIRECTIVE,
        _AXIS_KANJI,
        _AXIS_FULL_TEXT,
        prompt_reference_key_as_text,
    )

    class TopologyMetaPromptTests(unittest.TestCase):
        def test_M1_prompt_reference_key_has_topology_axis(self) -> None:
            """PROMPT_REFERENCE_KEY['constraints_axes'] must include 'topology'."""
            axes = PROMPT_REFERENCE_KEY.get("constraints_axes", {})
            self.assertIn(
                "topology", axes,
                "topology missing from PROMPT_REFERENCE_KEY['constraints_axes']",
            )
            self.assertTrue(
                axes["topology"].strip(),
                "topology entry in constraints_axes must be non-empty",
            )

        def test_M2_axis_kanji_has_topology(self) -> None:
            """_AXIS_KANJI must include a kanji entry for topology."""
            self.assertIn(
                "topology", _AXIS_KANJI,
                "topology missing from _AXIS_KANJI in metaPromptConfig.py",
            )
            self.assertTrue(
                _AXIS_KANJI["topology"].strip(),
                "_AXIS_KANJI['topology'] must be non-empty",
            )

        def test_M3_axis_full_text_has_topology(self) -> None:
            """_AXIS_FULL_TEXT must include a full description for topology."""
            self.assertIn(
                "topology", _AXIS_FULL_TEXT,
                "topology missing from _AXIS_FULL_TEXT in metaPromptConfig.py",
            )
            self.assertTrue(
                _AXIS_FULL_TEXT["topology"].strip(),
                "_AXIS_FULL_TEXT['topology'] must be non-empty",
            )

        def test_M4_prompt_reference_key_as_text_includes_topology(self) -> None:
            """prompt_reference_key_as_text() output must mention topology."""
            text = prompt_reference_key_as_text()
            self.assertIn(
                "topology", text.lower(),
                "topology axis missing from prompt_reference_key_as_text() output",
            )

        def test_M5_planning_directive_contains_token_derivations_marker(self) -> None:
            """PLANNING_DIRECTIVE must open the derivation block with 'Token derivations:'."""
            self.assertIn(
                "Token derivations:",
                PLANNING_DIRECTIVE,
                "PLANNING_DIRECTIVE must begin derivation block with 'Token derivations:'",
            )

        def test_M6_planning_directive_contains_derived_stance_complete_marker(self) -> None:
            """PLANNING_DIRECTIVE must close the derivation block with 'Derived stance complete.'."""
            self.assertIn(
                "Derived stance complete.",
                PLANNING_DIRECTIVE,
                "PLANNING_DIRECTIVE must close derivation block with 'Derived stance complete.'",
            )

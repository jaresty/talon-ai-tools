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

        def test_M5_planning_directive_scopes_four_section_constraint_to_planning_block(self) -> None:
            """PLANNING_DIRECTIVE must contain four section headings scoped to the planning block."""
            self.assertTrue(
                "SECTION 1 —" in PLANNING_DIRECTIVE and "SECTION 4 —" in PLANNING_DIRECTIVE,
                "PLANNING_DIRECTIVE must define four named sections (SECTION 1 — through SECTION 4 —)",
            )

        def test_M6_planning_directive_states_task_execution_continues_after_planning_block(self) -> None:
            """PLANNING_DIRECTIVE must explicitly state that task execution continues after the four-section block."""
            self.assertTrue(
                "proceed immediately" in PLANNING_DIRECTIVE or "Task execution begins" in PLANNING_DIRECTIVE,
                "PLANNING_DIRECTIVE must state task execution continues after planning block",
            )

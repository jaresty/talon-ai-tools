"""Tests for axis-level empty-state descriptions (Variant B).

Gherkin scenario: Grammar JSON exposes axis_descriptions for all axes.
"""
import json
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.axisConfig import AXIS_KEY_TO_AXIS_DESC, axis_key_to_axis_desc
    from talon_user.lib.axisCatalog import axis_catalog

    EXPECTED_AXES = {"channel", "completeness", "directional", "form", "method", "scope"}

    class AxisLevelDescriptionDataTests(unittest.TestCase):
        def test_all_grammar_axes_have_axis_desc(self) -> None:
            """Every grammar axis must have a non-empty axis-level description."""
            for axis in EXPECTED_AXES:
                with self.subTest(axis=axis):
                    desc = AXIS_KEY_TO_AXIS_DESC.get(axis, "")
                    self.assertTrue(
                        desc,
                        f"AXIS_KEY_TO_AXIS_DESC is missing entry for axis {axis!r}",
                    )

        def test_axis_desc_accessor_returns_correct_value(self) -> None:
            """axis_key_to_axis_desc() returns the dict value for each axis."""
            for axis in EXPECTED_AXES:
                with self.subTest(axis=axis):
                    self.assertEqual(
                        axis_key_to_axis_desc(axis),
                        AXIS_KEY_TO_AXIS_DESC[axis],
                    )

        def test_axis_desc_accessor_returns_empty_for_unknown_axis(self) -> None:
            self.assertEqual(axis_key_to_axis_desc("nonexistent"), "")

        def test_axis_descriptions_propagate_into_catalog(self) -> None:
            """axis_catalog() must include axis_descriptions keyed by axis name."""
            catalog = axis_catalog()
            self.assertIn("axis_descriptions", catalog)
            for axis in EXPECTED_AXES:
                with self.subTest(axis=axis):
                    self.assertIn(axis, catalog["axis_descriptions"])
                    self.assertTrue(catalog["axis_descriptions"][axis])

    class AxisLevelDescriptionGrammarJsonTests(unittest.TestCase):
        """Verify the exported grammar JSON contains axis_descriptions."""

        def _load_grammar(self) -> dict:
            path = Path(__file__).parent.parent / "build" / "prompt-grammar.json"
            if not path.exists():
                self.skipTest("build/prompt-grammar.json not present — run prompts.export first")
            with open(path) as f:
                return json.load(f)

        def test_grammar_json_has_axis_descriptions_field(self) -> None:
            grammar = self._load_grammar()
            self.assertIn("axis_descriptions", grammar["axes"])

        def test_grammar_json_axis_descriptions_covers_all_axes(self) -> None:
            grammar = self._load_grammar()
            descs = grammar["axes"]["axis_descriptions"]
            for axis in EXPECTED_AXES:
                with self.subTest(axis=axis):
                    self.assertIn(axis, descs)
                    self.assertTrue(descs[axis])

else:
    if not TYPE_CHECKING:

        class AxisLevelDescriptionDataTests(unittest.TestCase):  # type: ignore[no-redef]
            def test_skip(self) -> None:
                self.skipTest("bootstrap not available")

        class AxisLevelDescriptionGrammarJsonTests(unittest.TestCase):  # type: ignore[no-redef]
            def test_skip(self) -> None:
                self.skipTest("bootstrap not available")

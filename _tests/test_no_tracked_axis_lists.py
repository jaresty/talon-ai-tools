import unittest
from pathlib import Path
from typing import TYPE_CHECKING

AXIS_LIST_FILES = {
    "completenessModifier.talon-list",
    "scopeModifier.talon-list",
    "methodModifier.talon-list",
    "formModifier.talon-list",
    "channelModifier.talon-list",
    "directionalModifier.talon-list",
    "staticPrompt.talon-list",
}

if not TYPE_CHECKING:

    class NoTrackedAxisListsTests(unittest.TestCase):
        def test_axis_static_prompt_lists_not_tracked(self) -> None:
            """Guardrail: axis/static prompt Talon list files should not be tracked on disk."""

            lists_dir = Path(__file__).resolve().parents[1] / "GPT" / "lists"
            for name in AXIS_LIST_FILES:
                with self.subTest(list=name):
                    self.assertFalse(
                        (lists_dir / name).exists(),
                        f"{name} should not be tracked on disk (catalog-only lists)",
                    )

else:

    class NoTrackedAxisListsTests(unittest.TestCase):  # pragma: no cover
        @unittest.skip("Test harness unavailable in TYPE_CHECKING mode")
        def test_placeholder(self) -> None:
            pass

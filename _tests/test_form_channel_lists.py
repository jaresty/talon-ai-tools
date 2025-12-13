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
    from talon_user.lib.axisCatalog import axis_catalog

    class FormChannelListTests(unittest.TestCase):
        def test_form_and_channel_axes_exist(self) -> None:
            catalog = axis_catalog()
            axes = catalog.get("axes", {}) or {}
            self.assertIn("form", axes)
            self.assertIn("channel", axes)
            self.assertTrue(axes["form"])
            self.assertTrue(axes["channel"])

        def test_form_channel_list_files_exist(self) -> None:
            root = Path(__file__).resolve().parents[1] / "GPT" / "lists"
            self.assertTrue((root / "formModifier.talon-list").is_file())
            self.assertTrue((root / "channelModifier.talon-list").is_file())

else:
    if not TYPE_CHECKING:
        class FormChannelListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

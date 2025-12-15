import unittest
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

        def test_form_channel_lists_seeded_from_catalog(self) -> None:
            catalog = axis_catalog()
            axis_lists = catalog.get("axis_list_tokens", {}) or {}
            self.assertTrue(axis_lists.get("form"))
            self.assertTrue(axis_lists.get("channel"))

else:
    if not TYPE_CHECKING:
        class FormChannelListTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

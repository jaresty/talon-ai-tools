import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()


if bootstrap is not None:
    from talon_user.lib.historyQuery import (
        history_axes_for,
        history_summary_lines,
        history_drawer_entries_from,
    )
    from talon_user.lib.requestHistoryActions import (
        history_axes_for as actions_axes_for,
    )
    from talon_user.lib.requestHistoryActions import (
        history_summary_lines as actions_summary_lines,
    )
    from talon_user.lib.requestHistoryDrawer import (
        history_drawer_entries_from as drawer_entries_from,
    )

    class HistoryQueryTests(unittest.TestCase):
        def test_history_axes_for_delegates_to_actions_helper(self) -> None:
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["bound", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["plain", "Hydrated style"],
                "channel": ["slack", "Hydrated channel"],
            }

            direct = actions_axes_for(axes)
            via_facade = history_axes_for(axes)
            self.assertEqual(via_facade, direct)

        def test_history_summary_lines_delegates_to_actions_helper(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-1"
                    self.prompt = "prompt one"
                    self.duration_ms = 7
                    self.recipe = "infer · full · rigor"
                    self.provider_id = "gemini"
                    self.axes = {"directional": ["fog"]}

            entries = [DummyEntry()]
            direct = actions_summary_lines(entries)
            via_facade = history_summary_lines(entries)
            self.assertEqual(via_facade, direct)
            self.assertTrue(any("provider=gemini" in line for line in via_facade))

        def test_history_drawer_entries_from_delegates_to_drawer_helper(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-1"
                    self.prompt = "prompt one\nsecond line"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 42
                    self.recipe = "infer · full · rigor"
                    self.provider_id = "gemini"

            entries = [DummyEntry()]
            direct = drawer_entries_from(entries)
            via_facade = history_drawer_entries_from(entries)
            self.assertEqual(via_facade, direct)
            self.assertIn("[gemini]", via_facade[0][0])

        def test_history_drawer_prefers_axes_tokens(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-axes"
                    self.prompt = "prompt one\nsecond line"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 42
                    self.recipe = "legacy · recipe"
                    self.provider_id = ""
                    self.axes = {
                        "completeness": ["full"],
                        "scope": ["actions"],
                        "method": ["rigor"],
                        "form": ["adr"],
                        "channel": ["slack"],
                        "directional": ["fog"],
                    }

            entries = [DummyEntry()]
            rendered = history_drawer_entries_from(entries)
            label, body = rendered[0]
            self.assertIn("rid-axes", label)
            self.assertIn("adr", body)
            self.assertIn("slack", body)
            self.assertIn("fog", body)
            self.assertNotIn("recipe", body)

        def test_history_drawer_skips_entries_without_directional(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-no-dir"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = "infer · gist"
                    self.axes = {"completeness": ["gist"], "directional": []}

            entries = [DummyEntry()]
            rendered = history_drawer_entries_from(entries)
            self.assertEqual(rendered, [])


else:
    if not TYPE_CHECKING:

        class HistoryQueryTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

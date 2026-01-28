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
        def test_axis_snapshot_helper_matches_history_axes_for(self) -> None:
            axes = {
                "completeness": ["full", "Important: Hydrated completeness"],
                "scope": ["struct", "Invalid scope"],
                "method": ["rigor", "Unknown method"],
                "form": ["bullets", "Hydrated style"],
                "channel": ["slack", "Hydrated channel"],
                "directional": ["fog", "rog"],
            }

            from talon_user.lib.historyLifecycle import axes_snapshot_from_axes

            direct = actions_axes_for(axes)
            snapshot = axes_snapshot_from_axes(axes)
            self.assertEqual(snapshot.known_axes(), direct)

        def test_history_axes_for_reuses_lifecycle_helper(self) -> None:
            import talon_user.lib.historyLifecycle as history_lifecycle
            import talon_user.lib.historyQuery as history_query_module

            self.assertIs(
                history_query_module._history_axes_for_impl,
                history_lifecycle.history_axes_for,
            )
            self.assertIs(
                history_query_module._axis_snapshot_from_axes_impl,
                history_lifecycle.axes_snapshot_from_axes,
            )

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

        def test_history_summary_lines_reject_unknown_axis_keys(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-bad"
                    self.prompt = "prompt one"
                    self.duration_ms = 7
                    self.recipe = "infer · full · rigor"
                    self.provider_id = "gemini"
                    self.axes = {"directional": ["fog"], "unknown": ["value"]}

            entries = [DummyEntry()]
            with self.assertRaisesRegex(ValueError, "unknown axis keys"):
                history_summary_lines(entries)

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
                    self.axes = {"directional": ["fog"]}

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
                        "scope": ["act"],
                        "method": ["rigor"],
                        "form": ["bullets"],
                        "channel": ["adr"],
                        "directional": ["fog"],
                    }

            entries = [DummyEntry()]
            rendered = history_drawer_entries_from(entries)
            label, body = rendered[0]
            self.assertIn("rid-axes", label)
            self.assertIn("adr", body)
            self.assertIn("bullets", body)
            self.assertIn("fog", body)
            self.assertNotIn("recipe", body)

        def test_history_drawer_rejects_unknown_axis_keys(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-unknown"
                    self.prompt = "prompt"
                    self.response = "resp"
                    self.meta = "meta"
                    self.duration_ms = 5
                    self.recipe = "infer · gist"
                    self.provider_id = "openai"
                    self.axes = {
                        "directional": ["fog"],
                        "completeness": ["gist"],
                        "mystery": ["value"],
                    }

            entries = [DummyEntry()]
            with self.assertRaisesRegex(ValueError, "unknown axis keys"):
                history_drawer_entries_from(entries)

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

        def test_history_drawer_uses_directional_from_recipe_when_axes_missing(
            self,
        ) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-recipe"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = "infer · gist · focus · fog"
                    self.axes = {}

            entries = [DummyEntry()]
            rendered = history_drawer_entries_from(entries)
            self.assertEqual(len(rendered), 1)
            label, body = rendered[0]
            self.assertIn("rid-recipe", label)
            self.assertIn("fog", body)

        def test_history_summary_skips_entries_without_directional(self) -> None:
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
            summary = history_summary_lines(entries)
            self.assertEqual(summary, [])

        def test_history_summary_includes_directional_token(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-dir"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = ""
                    self.axes = {
                        "completeness": ["gist"],
                        "scope": ["struct"],
                        "method": ["flow"],
                        "form": ["bullets"],
                        "channel": ["adr"],
                        "directional": ["fog"],
                    }

            summary = history_summary_lines([DummyEntry()])
            self.assertEqual(len(summary), 1)
            rendered = summary[0]
            self.assertIn("fog", rendered)
            self.assertIn("adr", rendered)
            self.assertIn("bullets", rendered)

        def test_history_summary_normalizes_directional_from_axes(self) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-case"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = ""
                    self.axes = {"directional": ["Fog"]}

            summary = history_summary_lines([DummyEntry()])
            self.assertEqual(len(summary), 1)
            self.assertIn("fog", summary[0])

        def test_history_summary_uses_directional_from_recipe_when_axes_missing(
            self,
        ) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-recipe"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = "infer · gist · focus · fog"
                    self.axes = {}

            summary = history_summary_lines([DummyEntry()])
            self.assertEqual(len(summary), 1)
            rendered = summary[0]
            self.assertIn("fog", rendered)
            self.assertIn("rid-recipe", rendered)

        def test_history_summary_detects_directional_case_insensitive_recipe(
            self,
        ) -> None:
            class DummyEntry:
                def __init__(self) -> None:
                    self.request_id = "rid-recipe-case"
                    self.prompt = "prompt one"
                    self.response = "resp1"
                    self.meta = "meta1"
                    self.duration_ms = 10
                    self.recipe = "infer · gist · focus · Fog"
                    self.axes = {}

            summary = history_summary_lines([DummyEntry()])
            self.assertEqual(len(summary), 1)
            self.assertIn("fog", summary[0])

        def test_history_summary_orders_newest_first_and_includes_ids(self) -> None:
            class DummyEntry:
                def __init__(self, request_id: str, dur: int) -> None:
                    self.request_id = request_id
                    self.prompt = f"prompt for {request_id}"
                    self.response = "resp"
                    self.meta = "meta"
                    self.duration_ms = dur
                    self.recipe = ""
                    self.provider_id = "openai"
                    self.axes = {"directional": ["fog"]}

            old = DummyEntry("rid-old", 10)
            new = DummyEntry("rid-new", 50)
            summary = history_summary_lines([old, new])
            self.assertEqual(len(summary), 2)
            # Newest (last element) should appear first.
            self.assertIn("rid-new", summary[0])
            self.assertIn("50ms", summary[0])
            self.assertIn("fog", summary[0])
            self.assertIn("openai", summary[0])
            self.assertIn("rid-old", summary[1])


else:
    if not TYPE_CHECKING:

        class HistoryQueryTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

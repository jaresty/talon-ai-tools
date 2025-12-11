import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.suggestionCoordinator import (
        last_suggestions,
        record_suggestions,
        suggestion_entries,
        suggestion_source,
        set_last_recipe_from_selection,
        suggestion_grammar_phrase,
        last_recipe_snapshot,
        last_recap_snapshot,
        suggestion_entries_with_metadata,
    )
    from talon_user.lib.modelState import GPTState

    class SuggestionCoordinatorTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()

        def test_record_and_fetch_suggestions(self) -> None:
            suggestions = [
                {
                    "name": "Fix bugs",
                    "recipe": "fix · full · narrow · steps · plain · fog",
                }
            ]
            record_suggestions(suggestions, "clipboard")

            stored, source = last_suggestions()
            self.assertEqual(source, "clipboard")
            self.assertEqual(stored, suggestions)

        def test_record_sanitises_none_source(self) -> None:
            record_suggestions([], None)
            stored, source = last_suggestions()
            self.assertEqual(stored, [])
            self.assertEqual(source, "")

        def test_suggestion_entries_filters_invalid(self) -> None:
            record_suggestions(
                [
                    {"name": "Valid", "recipe": "fix · full · fog"},
                    {"name": "", "recipe": "bad"},
                ],
                "clipboard",
            )
            entries = suggestion_entries()
            self.assertEqual(entries, [{"name": "Valid", "recipe": "fix · full · fog"}])

        def test_suggestion_entries_with_metadata_preserves_extra_fields(self) -> None:
            record_suggestions(
                [
                    {
                        "name": "With stance",
                        "recipe": "fix · full · fog",
                        "stance_command": "model write as teacher …",
                        "why": "Kind stance for junior devs",
                    },
                ],
                "clipboard",
            )
            entries = suggestion_entries_with_metadata()
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry["name"], "With stance")
            self.assertEqual(entry["recipe"], "fix · full · fog")
            self.assertEqual(entry.get("stance_command"), "model write as teacher …")
            self.assertEqual(entry.get("why"), "Kind stance for junior devs")

        def test_suggestion_source_falls_back(self) -> None:
            record_suggestions([], None)
            self.assertEqual(suggestion_source("default"), "default")
            record_suggestions([], "clipboard")
            self.assertEqual(suggestion_source("default"), "clipboard")

        def test_set_last_recipe_from_selection_updates_state(self) -> None:
            set_last_recipe_from_selection(
                static_prompt="fix",
                completeness="full",
                scope="narrow focus",
                method=["steps", "rigor"],
                style="plain",
                directional="fog",
            )
            self.assertEqual(GPTState.last_static_prompt, "fix")
            self.assertEqual(GPTState.last_completeness, "full")
            self.assertEqual(GPTState.last_scope, "narrow focus")
            self.assertEqual(GPTState.last_method, "steps rigor")
            self.assertEqual(GPTState.last_style, "plain")
            self.assertEqual(GPTState.last_directional, "fog")
            self.assertEqual(
                GPTState.last_axes,
                {
                    "completeness": ["full"],
                    "scope": ["narrow", "focus"],
                    "method": ["steps", "rigor"],
                    "style": ["plain"],
                },
            )
            self.assertIn("fix", GPTState.last_recipe)

        def test_suggestion_grammar_phrase_uses_spoken_source(self) -> None:
            phrase = suggestion_grammar_phrase(
                "fix · full · fog", "clipboard", {"clipboard": "clip"}
            )
            self.assertEqual(phrase, "model run clip fix full fog")
            no_source_phrase = suggestion_grammar_phrase("fix · full · fog", None, {})
            self.assertEqual(no_source_phrase, "model run fix full fog")

        def test_last_recipe_snapshot_uses_axes_when_present(self) -> None:
            GPTState.last_static_prompt = "fix"
            GPTState.last_axes = {
                "completeness": ["full"],
                "scope": ["narrow", "focus"],
                "method": ["steps"],
                "style": ["plain"],
            }
            GPTState.last_directional = "fog"
            snapshot = last_recipe_snapshot()
            self.assertEqual(snapshot["static_prompt"], "fix")
            self.assertEqual(snapshot["completeness"], "full")
            self.assertEqual(snapshot["scope_tokens"], ["narrow", "focus"])
            self.assertEqual(snapshot["method_tokens"], ["steps"])
            self.assertEqual(snapshot["style_tokens"], ["plain"])
            self.assertEqual(snapshot["directional"], "fog")

        def test_last_recap_snapshot_includes_response_and_meta(self) -> None:
            GPTState.last_recipe = "fix · full"
            GPTState.last_response = "result text"
            GPTState.last_meta = "meta text"
            recap = last_recap_snapshot()
            self.assertEqual(recap["recipe"], "fix · full")
            self.assertEqual(recap["response"], "result text")
            self.assertEqual(recap["meta"], "meta text")

else:
    if not TYPE_CHECKING:

        class SuggestionCoordinatorTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

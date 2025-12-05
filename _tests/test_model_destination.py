import unittest
from typing import TYPE_CHECKING
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import actions, clip
    from talon_user.lib.modelDestination import ModelDestination
    from talon_user.lib import modelDestination as model_destination_module
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.lib.modelState import GPTState

    class ModelDestinationTests(unittest.TestCase):
        def setUp(self):
            actions.user.calls.clear()
            clip.set_text(None)
            GPTState.reset_all()

        @patch.object(model_destination_module, "Builder")
        def test_browser_includes_recipe_metadata_from_gpt_state(self, builder_cls):
            # Ensure clean state before configuring recipe fields.
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_static_prompt = "describe"

            result = PromptResult.from_messages([format_message("body line")])

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # The browser destination should prepend a Recipe line, a speakable
            # grammar line, and a tip that references the static prompt.
            paragraph_texts = [call.args[0] for call in builder_instance.p.call_args_list]

            self.assertIn(
                "Recipe: describe · full · focus · plain · fog", paragraph_texts
            )
            self.assertIn(
                "Say: model describe full focus plain fog", paragraph_texts
            )
            self.assertTrue(
                any("model show grammar" in text for text in paragraph_texts),
                "Expected a tip mentioning 'model show grammar'",
            )
            self.assertTrue(
                any("model pattern menu describe" in text for text in paragraph_texts),
                "Expected a tip mentioning 'model pattern menu describe'",
            )

            builder_instance.h2.assert_called_with("Response")

        @patch.object(model_destination_module, "Builder")
        def test_browser_includes_meta_section_when_available(self, builder_cls):
            GPTState.reset_all()
            GPTState.last_recipe = "describe · full · focus · plain"
            GPTState.last_directional = "fog"
            GPTState.last_static_prompt = "describe"

            # Simulate a presentation with meta text already split out.
            result = PromptResult.from_messages(
                [format_message("body line\n\n## Model interpretation\nMeta details")]
            )

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # Collect all paragraph calls after Browser.insert.
            paragraph_texts = [call.args[0] for call in builder_instance.p.call_args_list]

            # We expect a dedicated Model interpretation section header and the
            # meta content rendered separately from the main body.
            self.assertIn("Model interpretation", [call.args[0] for call in builder_instance.h2.call_args_list])
            self.assertTrue(
                any("Meta details" in text for text in paragraph_texts),
                "Expected browser view to include meta interpretation text",
            )
            # The bare heading marker should not appear as its own paragraph.
            self.assertNotIn(
                "Model interpretation",
                paragraph_texts,
                "Model interpretation heading should not be rendered as a body paragraph",
            )

        @patch.object(model_destination_module, "Browser")
        def test_insert_uses_response_presentation(self, browser_cls):
            with patch.object(actions.user, "confirmation_gui_append") as gui_append, patch.object(
                actions.user, "paste"
            ) as paste_action:
                result = PromptResult.from_messages([format_message("answer")])

                ModelDestination().insert(result)

            browser_instance = browser_cls.return_value
            gui_append.assert_called_once()
            self.assertFalse(paste_action.called)
            self.assertFalse(browser_instance.insert.called)
            presentation = gui_append.call_args.args[0]
            self.assertIsInstance(presentation, ResponsePresentation)
            self.assertEqual(presentation.display_text, "answer")

        def test_insert_accepts_prompt_result_like_object(self):
            with patch.object(actions.user, "confirmation_gui_append"):
                inner = PromptResult.from_messages([format_message("legacy")])

                class ForeignPromptResult:
                    def __init__(self, wrapped):
                        self._wrapped = wrapped
                        self.messages = wrapped.messages
                        self.session = wrapped.session

                    def presentation_for(self, destination_kind):
                        return self._wrapped.presentation_for(destination_kind)

                    def append_thread(self):
                        return self._wrapped.append_thread()

                    @property
                    def text(self):
                        return self._wrapped.text

                ModelDestination().insert(ForeignPromptResult(inner))

        @patch.object(model_destination_module, "Builder")
        def test_browser_renders_bulleted_response_as_list(self, builder_cls):
            # Ensure rich answer rendering recognises simple bullets.
            GPTState.reset_all()
            result = PromptResult.from_messages(
                [
                    format_message(
                        "Intro paragraph.\n\n- First item\n- Second item\n\nConclusion."
                    )
                ]
            )

            builder_instance = builder_cls.return_value

            browser = model_destination_module.Browser()
            browser.insert(result)

            # The builder should have been asked to render at least one
            # unordered list for the bullet items.
            self.assertTrue(
                any(call[0] == () for call in builder_instance.ul.call_args_list)
                or builder_instance.ul.call_args_list,
                "Expected Browser to render bullets via Builder.ul",
            )

else:
    if not TYPE_CHECKING:
        class ModelDestinationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass

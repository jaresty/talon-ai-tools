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

    class ModelDestinationTests(unittest.TestCase):
        def setUp(self):
            actions.user.calls.clear()
            clip.set_text(None)

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

else:
    if not TYPE_CHECKING:
        class ModelDestinationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass

import unittest
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelSource import ModelSource
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.modelPresentation import ResponsePresentation
    from talon_user.lib.promptPipeline import PromptPipeline, PromptResult

    class _StaticSource(ModelSource):
        def __init__(self, text: str):
            self._text = text

        def get_text(self):  # type: ignore[override]
            return self._text

    class PromptPipelineTests(unittest.TestCase):
        def setUp(self):
            GPTState.reset_all()
            self.session_cls = MagicMock()
            self.session = self.session_cls.return_value
            self.session.execute.return_value = format_message("done")
            self.pipeline = PromptPipeline(session_cls=self.session_cls)

        def test_run_prepares_executes_and_returns_result(self):
            GPTState.enable_thread()
            source = _StaticSource("input")

            result = self.pipeline.run("prompt", source, "paste")

            self.session_cls.assert_called_once_with("paste")
            self.session.prepare_prompt.assert_called_once_with("prompt", source, None)
            self.session.execute.assert_called_once()
            self.session.append_thread.assert_called_once()
            self.assertIsInstance(result, PromptResult)
            self.assertEqual(result.messages, [self.session.execute.return_value])
            self.assertEqual(result.text, "done")

        def test_prompt_result_builds_presentations(self):
            result = PromptResult.from_messages([format_message("line one")])

            presentation = result.presentation_for("default")

            self.assertIsInstance(presentation, ResponsePresentation)
            self.assertEqual(presentation.display_text, "line one")
            # No meta section by default for a single-part response.
            self.assertEqual(presentation.meta_text, "")
            self.assertFalse(presentation.open_browser)

        def test_complete_async_delegates_to_session(self):
            out_handle = self.pipeline.complete_async(self.session)
            out_handle.wait(timeout=1.0)
            self.session.execute.assert_called_once()
            self.session.append_thread.assert_called_once()
            self.assertTrue(out_handle.done)

        def test_run_async_prepares_and_runs(self):
            source = _StaticSource("input")
            out_handle = self.pipeline.run_async("prompt", source, "dest")
            out_handle.wait(timeout=1.0)
            self.session_cls.assert_called_once_with("dest")
            self.session.prepare_prompt.assert_called_once_with("prompt", source, None)
            self.session.execute.assert_called_once()

else:
    if not TYPE_CHECKING:
        class PromptPipelineTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self):
                pass

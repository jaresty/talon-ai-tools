import json
import unittest
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
    from talon_user.lib.promptPipeline import PromptResult
    from talon_user.lib import recursiveOrchestrator as orchestrator_module

    class _Source(ModelSource):
        def __init__(self, text: str):
            self._text = text

        def get_text(self):  # type: ignore[override]
            return self._text

    class RecursiveOrchestratorTests(unittest.TestCase):
        def setUp(self):
            self.source = _Source("input text")
            self.pipeline = MagicMock()
            self.orchestrator = orchestrator_module.RecursiveOrchestrator(self.pipeline)

        def test_run_returns_controller_result_when_no_directive(self):
            controller_result = PromptResult.from_messages(
                [format_message("plain response")]
            )
            self.pipeline.run.return_value = controller_result

            result = self.orchestrator.run(
                "controller prompt", self.source, destination="paste"
            )

            self.pipeline.run.assert_called_once_with(
                "controller prompt",
                self.source,
                "paste",
                None,
            )
            self.assertIs(result, controller_result)

        def test_run_executes_delegate_and_respects_result_format(self):
            directive = json.dumps(
                {
                    "action": "delegate",
                    "prompt": "delegate prompt",
                    "response_destination": "paste",
                }
            )
            controller_result = PromptResult.from_messages(
                [format_message(directive)]
            )
            delegate_result = PromptResult.from_messages(
                [format_message("delegate output in required format")]
            )

            self.pipeline.run.side_effect = [controller_result, delegate_result]

            result = self.orchestrator.run(
                "controller prompt", self.source, destination="paste"
            )

            self.assertEqual(self.pipeline.run.call_count, 2)
            self.pipeline.run.assert_called_with(
                "delegate prompt",
                self.source,
                "paste",
                None,
            )
            self.assertIs(result, delegate_result)

else:
    class RecursiveOrchestratorTests(unittest.TestCase):
        @unittest.skip("Test harness unavailable outside unittest runs")
        def test_placeholder(self):
            pass


if __name__ == "__main__":
    unittest.main()

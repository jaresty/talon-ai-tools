import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelTypes import GPTSystemPrompt
    from talon_user.lib.axisMappings import axis_hydrate_tokens


if bootstrap is not None:

    class GPTSystemPromptAxesHydrationTests(unittest.TestCase):
        def test_contract_axes_are_hydrated_in_system_prompt(self) -> None:
            # Pick a representative token from each contract axis that is known
            # to exist in axisConfig / axisMappings.
            prompt = GPTSystemPrompt(
                completeness="gist",
                scope="system",
                method="steps",
                style="plain",
            )

            lines = prompt.format_as_array()
            as_text = "\n".join(lines)

            # Compute expected hydrated strings using the same helper used by the
            # contract-axis hydration path.
            expected_completeness = axis_hydrate_tokens("completeness", ["gist"])[0]
            expected_scope = " ".join(axis_hydrate_tokens("scope", ["system"]))
            expected_method = " ".join(axis_hydrate_tokens("method", ["steps"]))
            expected_style = " ".join(axis_hydrate_tokens("style", ["plain"]))

            self.assertIn(f"Completeness: {expected_completeness}", as_text)
            self.assertIn(f"Scope: {expected_scope}", as_text)
            self.assertIn(f"Method: {expected_method}", as_text)
            self.assertIn(f"Style: {expected_style}", as_text)

else:
    if not TYPE_CHECKING:

        class GPTSystemPromptAxesHydrationTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelHelpers import split_answer_and_meta

    class SplitAnswerAndMetaTests(unittest.TestCase):
        def test_returns_all_answer_when_no_interpretation_heading(self) -> None:
            text = "Line one\nLine two"

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer, text)
            self.assertEqual(meta, "")

        def test_splits_on_markdown_interpretation_heading(self) -> None:
            text = (
                "Main answer paragraph.\n\n"
                "## Model interpretation\n"
                "Meta line one\n"
                "Meta line two"
            )

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Main answer paragraph.")
            self.assertIn("Model interpretation", meta)
            self.assertIn("Meta line one", meta)
            self.assertIn("Meta line two", meta)

        def test_interpretation_heading_detection_is_case_insensitive(self) -> None:
            text = (
                "Body\n"
                "## MODEL INTERPRETATION\n"
                "Meta content"
            )

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertTrue(meta.strip().startswith("## MODEL INTERPRETATION"))

        def test_leading_whitespace_before_heading_is_ignored(self) -> None:
            text = (
                "Body\n"
                "   ## Model interpretation\n"
                "Meta content"
            )

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertIn("Model interpretation", meta)

        def test_does_not_split_on_unrelated_interpretation_heading(self) -> None:
            text = (
                "Body\n"
                "## Interpretation of results\n"
                "Still part of the main answer"
            )

            answer, meta = split_answer_and_meta(text)

            # No exact '## Model interpretation' heading, so treat everything
            # as part of the main answer.
            self.assertEqual(answer, text)
            self.assertEqual(meta, "")

else:
    if not TYPE_CHECKING:
        class SplitAnswerAndMetaTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

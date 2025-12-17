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
            text = "Body\n## MODEL INTERPRETATION\nMeta content"

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertTrue(meta.strip().startswith("## MODEL INTERPRETATION"))

        def test_leading_whitespace_before_heading_is_ignored(self) -> None:
            text = "Body\n   ## Model interpretation\nMeta content"

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertIn("Model interpretation", meta)

        def test_does_not_split_on_unrelated_interpretation_heading(self) -> None:
            text = "Body\n## Interpretation of results\nStill part of the main answer"

            answer, meta = split_answer_and_meta(text)

            # No exact '## Model interpretation' heading, so treat everything
            # as part of the main answer.
            self.assertEqual(answer, text)
            self.assertEqual(meta, "")

        def test_splits_when_heading_has_suffix_text(self) -> None:
            text = (
                "Body\n## Model interpretation- Interpretation: details\nMeta content"
            )

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertIn("Model interpretation", meta)
            self.assertIn("Meta content", meta)

        def test_splits_when_heading_has_dash_and_suffix(self) -> None:
            text = (
                "Body\n"
                "  ###   Model interpretation- Intended intent: something\n"
                "Meta content\n"
            )

            answer, meta = split_answer_and_meta(text)

            self.assertEqual(answer.strip(), "Body")
            self.assertTrue(meta.strip().startswith("###   Model interpretation"))

        def test_splits_when_heading_and_body_share_line_with_emoji(self) -> None:
            text = (
                "📷✨🌱\n"
                "📷✨🌱## Model interpretation- Approach: explain emoji poem.\n"
                "Meta body line.\n"
            )

            answer, meta = split_answer_and_meta(text)

            # Answer keeps only the emoji runs from the first and second lines.
            self.assertEqual(answer.strip(), "📷✨🌱\n📷✨🌱")
            # Meta starts at the '## Model interpretation- …' heading.
            self.assertIn("Model interpretation", meta)
            self.assertIn("Meta body line.", meta)


else:
    if not TYPE_CHECKING:

        class SplitAnswerAndMetaTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

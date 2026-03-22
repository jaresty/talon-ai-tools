"""
Tests that the Python path aligns with Go's ADDENDUM (CLARIFICATION) section.

Phase 3 of ADR 0082: the `format_source_messages()` function should render
the prompt parameter under the heading `=== ADDENDUM (CLARIFICATION) ===`
(matching Go's sectionAddendum constant), and PROMPT_REFERENCE_KEY should
document that section so LLMs know how to interpret it.
"""

import unittest
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.modelSource import ModelSource, format_source_messages
    from talon_user.lib.metaPromptConfig import PROMPT_REFERENCE_KEY

    class _SimpleSource(ModelSource):
        """Minimal source that returns a fixed text item."""

        def get_text(self) -> str:
            return "subject content"

    class AddendumAlignmentTests(unittest.TestCase):
        def test_format_source_messages_uses_addendum_heading(self) -> None:
            """format_source_messages should render ADDENDUM heading, not '# Prompt'."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "")
                for item in messages
                if isinstance(item, dict)
            )
            self.assertIn(
                "=== ADDENDUM (CLARIFICATION) ===",
                all_text,
                "format_source_messages must use ADDENDUM heading to match Go CLI",
            )
            self.assertNotIn(
                "# Prompt",
                all_text,
                "format_source_messages must not use legacy '# Prompt' heading",
            )

        def test_execution_reminder_precedes_addendum(self) -> None:
            """EXECUTION REMINDER must appear before ADDENDUM in format_source_messages output,
            so it gates completion-intent before the task prompt anchors the model's response plan."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "")
                for item in messages
                if isinstance(item, dict)
            )
            reminder_idx = all_text.find("=== EXECUTION REMINDER ===")
            addendum_idx = all_text.find("=== ADDENDUM (CLARIFICATION) ===")
            self.assertGreater(reminder_idx, -1, "EXECUTION REMINDER section must be present")
            self.assertGreater(addendum_idx, -1, "ADDENDUM section must be present")
            self.assertLess(
                reminder_idx,
                addendum_idx,
                "EXECUTION REMINDER must appear before ADDENDUM so it intercepts completion-intent",
            )

        def test_execution_reminder_also_follows_subject(self) -> None:
            """A second EXECUTION REMINDER must appear after SUBJECT in format_source_messages
            output, providing recency-based resistance to SUBJECT injection attacks."""
            messages = format_source_messages("do this", _SimpleSource())
            all_text = " ".join(
                item.get("text", "")
                for item in messages
                if isinstance(item, dict)
            )
            subject_idx = all_text.find("=== SUBJECT (CONTEXT) ===")
            last_reminder_idx = all_text.rfind("=== EXECUTION REMINDER ===")
            self.assertGreater(subject_idx, -1, "SUBJECT section must be present")
            self.assertGreater(last_reminder_idx, -1, "EXECUTION REMINDER section must be present")
            self.assertGreater(
                last_reminder_idx,
                subject_idx,
                "A second EXECUTION REMINDER must appear after SUBJECT for injection resistance",
            )

        def test_prompt_reference_key_process_method_imperative_check(self) -> None:
            """PROMPT_REFERENCE_KEY must include imperative check for process methods."""
            self.assertIn(
                "Produce that output now before reading files, searching code, or planning",
                PROMPT_REFERENCE_KEY,
                "PROMPT_REFERENCE_KEY Method bullet must include imperative check for process methods",
            )

        def test_prompt_reference_key_documents_addendum_section(self) -> None:
            """PROMPT_REFERENCE_KEY must describe the ADDENDUM section."""
            self.assertIn(
                "ADDENDUM",
                PROMPT_REFERENCE_KEY,
                "PROMPT_REFERENCE_KEY must document the ADDENDUM section",
            )
            self.assertIn(
                "clarification",
                PROMPT_REFERENCE_KEY.lower(),
                "PROMPT_REFERENCE_KEY ADDENDUM entry should mention 'clarification'",
            )

else:
    if not TYPE_CHECKING:

        class AddendumAlignmentTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass


if __name__ == "__main__":
    unittest.main()

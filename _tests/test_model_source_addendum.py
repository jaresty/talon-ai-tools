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

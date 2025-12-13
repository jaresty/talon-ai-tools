import os
import tempfile
import unittest
from unittest import mock
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from pathlib import Path

    from talon import settings as talon_settings  # type: ignore
    from talon_user.GPT import gpt as gpt_module
    from talon_user.lib.modelHelpers import format_message
    from talon_user.lib.modelState import GPTState
    from talon_user.lib.suggestionCoordinator import (
        recipe_header_lines_from_snapshot,
    )

    class SourceSnapshotTests(unittest.TestCase):
        def setUp(self) -> None:
            GPTState.reset_all()

        def test_save_source_snapshot_writes_markdown_with_header_and_body(
            self,
        ) -> None:
            """Characterise the happy-path source snapshot behaviour.

            This focuses on the Axis & Static Prompt Concordance / Streaming domain
            intersection described in ADR-0045: snapshots should include enough
            axis/static-prompt context to be self-describing.
            """

            tmpdir = tempfile.mkdtemp()
            talon_settings.set("user.model_source_save_directory", tmpdir)

            # Seed cached source messages so the helper uses them instead of
            # falling back to the current default source.
            GPTState.last_source_messages = [
                format_message("first line"),
                format_message("second line"),
            ]

            # Provide a minimal snapshot so slug and header fields are populated
            # without depending on the full suggestionCoordinator pipeline.
            snapshot = {
                "static_prompt": "infer",
                "recipe": "infer · full · steps",
                "completeness": "full",
                "scope_tokens": ["bound"],
                "method_tokens": ["steps"],
                "form_tokens": ["plain"],
                "channel_tokens": ["slack"],
                "directional": "fog",
            }

            with (
                mock.patch.object(
                    gpt_module,
                    "last_recipe_snapshot",
                    return_value=snapshot,
                ),
                mock.patch.object(
                    gpt_module,
                    "recipe_header_lines_from_snapshot",
                    recipe_header_lines_from_snapshot,
                    create=True,
                ),
            ):
                path = gpt_module._save_source_snapshot_to_file()

            # A concrete markdown file should be written into the configured dir.
            self.assertIsInstance(path, str)
            self.assertTrue(path)
            self.assertTrue(path.startswith(tmpdir), path)

            content = Path(path).read_text(encoding="utf-8")

            # Header block should include saved_at and the axis/static prompt
            # context we provided in the snapshot.
            self.assertIn("saved_at:", content)
            self.assertIn("recipe: infer · full · steps", content)
            self.assertIn("completeness: full", content)
            self.assertIn("scope_tokens: bound", content)
            self.assertIn("method_tokens: steps", content)
            self.assertIn("form_tokens: plain", content)
            self.assertIn("channel_tokens: slack", content)
            self.assertIn("directional: fog", content)

            # Body should contain the rendered source text under a heading.
            self.assertIn("# Source", content)
            self.assertIn("first line", content)
            self.assertIn("second line", content)

        def test_save_source_snapshot_slug_includes_source_type_and_static_prompt(
            self,
        ) -> None:
            """Slug and header should reflect source type and static prompt.

            This guards the filename/header contract so downstream tools can
            infer source and axes context from saved source files.
            """

            tmpdir = tempfile.mkdtemp()
            talon_settings.set("user.model_source_save_directory", tmpdir)

            # Seed cached source messages and source key so the helper uses the
            # snapshot path and records source_type in headers.
            GPTState.last_source_messages = [format_message("only line")]
            GPTState.last_source_key = "clipboard"

            snapshot = {
                "static_prompt": "infer",
                "recipe": "infer · full · steps",
                "completeness": "full",
                "scope_tokens": ["bound"],
                "method_tokens": ["steps"],
                "form_tokens": ["plain"],
                "channel_tokens": ["slack"],
                "directional": "fog",
            }

            with (
                mock.patch.object(
                    gpt_module,
                    "last_recipe_snapshot",
                    return_value=snapshot,
                ),
                mock.patch.object(
                    gpt_module,
                    "recipe_header_lines_from_snapshot",
                    recipe_header_lines_from_snapshot,
                    create=True,
                ),
            ):
                path = gpt_module._save_source_snapshot_to_file()

            self.assertIsInstance(path, str)
            self.assertTrue(path)

            p = Path(path)
            filename = p.name
            # Filename slug should include both source type and static prompt
            # tokens so files are self-describing at a glance.
            self.assertIn("clipboard", filename)
            self.assertIn("infer", filename)

            content = p.read_text(encoding="utf-8")
            # Header should record the source_type alongside axis context.
            self.assertIn("source_type: clipboard", content)
            self.assertIn("recipe: infer · full · steps", content)
            self.assertIn("completeness: full", content)
            self.assertIn("scope_tokens: bound", content)
            self.assertIn("method_tokens: steps", content)
            self.assertIn("form_tokens: plain", content)
            self.assertIn("channel_tokens: slack", content)
            self.assertIn("directional: fog", content)

else:
    if not TYPE_CHECKING:

        class SourceSnapshotTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

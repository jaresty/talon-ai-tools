import os
import tempfile
import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings, actions
    from talon_user.lib.requestHistoryActions import (
        history_axes_for,
        _save_history_prompt_to_file,
    )

    class _Entry:
        def __init__(self, prompt, axes):
            self.prompt = prompt
            self.axes = axes
            self.request_id = "rid-test"
            self.recipe = ""
            self.meta = ""
            self.response = prompt
            self.duration_ms = None

    class RequestHistoryAxesCatalogTests(unittest.TestCase):
        def test_history_axes_for_keeps_directional_tokens(self) -> None:
            """Guardrail: history_axes_for retains catalog directional tokens."""

            axes = {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["steps"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog", "unknown-dir"],
            }
            filtered = history_axes_for(axes)
            self.assertEqual(filtered["directional"], ["fog"])
            self.assertNotIn("style", filtered)

        def test_history_axes_for_drops_unknown_axes_and_tokens(self) -> None:
            """Guardrail: history_axes_for drops unknown axes/tokens."""

            axes = {
                "completeness": ["full", "unknown"],
                "scope": ["focus", "unknown"],
                "method": ["steps", "unknown"],
                "form": ["bullets", "unknown"],
                "channel": ["slack", "unknown"],
                "directional": ["fog", "unknown-dir"],
                "style": ["plain"],
                "custom": ["value", "other"],
            }

            filtered = history_axes_for(axes)

            # Known axes are retained and cleaned; unknown axes/tokens are dropped.
            for key in (
                "completeness",
                "scope",
                "method",
                "form",
                "channel",
                "directional",
            ):
                self.assertIn(key, filtered)

            self.assertEqual(filtered["completeness"], ["full"])
            self.assertEqual(filtered["scope"], ["focus"])
            self.assertEqual(filtered["method"], ["steps"])
            self.assertEqual(filtered["form"], ["bullets"])
            self.assertEqual(filtered["channel"], ["slack"])
            self.assertEqual(filtered["directional"], ["fog"])
            self.assertNotIn("style", filtered)
            self.assertNotIn("custom", filtered)

        def test_save_history_includes_directional_header(self) -> None:
            """Guardrail: saved history files include directional tokens."""

            axes = {
                "completeness": ["full"],
                "scope": ["focus"],
                "method": ["steps"],
                "form": ["bullets"],
                "channel": ["slack"],
                "directional": ["fog"],
            }
            entry = _Entry(prompt="prompt text", axes=axes)

            with tempfile.TemporaryDirectory() as tmpdir:
                original_get = settings.get

                def fake_get(key, default=None):
                    if key == "user.model_source_save_directory":
                        return tmpdir
                    return original_get(key, default)

                settings.get = fake_get  # type: ignore[assignment]
                try:
                    _save_history_prompt_to_file(entry)
                finally:
                    settings.get = original_get  # type: ignore[assignment]

                saved_files = list(os.scandir(tmpdir))
                self.assertTrue(saved_files, "Expected a saved history file")
                content = Path(saved_files[0].path).read_text(encoding="utf-8")
                self.assertIn("directional_tokens: fog", content)
                self.assertIn("form_tokens: bullets", content)
                self.assertIn("channel_tokens: slack", content)
                self.assertIn("fog", saved_files[0].name)


else:
    if not TYPE_CHECKING:

        class RequestHistoryAxesCatalogTests(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

"""Specifying validation for ADR-0151 T-2: persona resolution chain observability.

_canonical_persona_value must emit a debug log whenever the docs-map fallback
level is reached (orchestrator absent, personaConfig returning empty).  Without
this log the fallback path is silent and alias conflicts are undetectable at
runtime.
"""
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
    import importlib

    gpt = importlib.import_module("talon_user.GPT.gpt")

    class PersonaResolutionFallbackLogTests(unittest.TestCase):
        def test_docs_fallback_emits_debug_log(self):
            """Reaching the docs-map fallback must emit a DEBUG log.

            Contract:
            - orchestrator absent (patched to None) — skips levels 2-4
            - canonical_persona_token returns "" — level 1 misses
            - persona_docs_map returns a controlled dict with "formal" key
            - calling with raw="formal" should match the docs-map key
            - a debug log containing "docs_map" must be emitted
            """
            mock_docs = {"formal": "Formal voice"}
            with (
                patch.object(gpt, "_persona_orchestrator", return_value=None),
                patch(
                    "talon_user.lib.personaConfig.canonical_persona_token",
                    return_value="",
                ),
                patch.object(gpt, "persona_docs_map", return_value=mock_docs),
            ):
                with self.assertLogs("talon_user.GPT.gpt", level="DEBUG") as log_ctx:
                    result = gpt._canonical_persona_value("voice", "formal")

            self.assertEqual(result, "formal")
            self.assertTrue(
                any("docs_map" in msg for msg in log_ctx.output),
                f"Expected a docs_map fallback log record; got: {log_ctx.output}",
            )

else:
    if not TYPE_CHECKING:

        class PersonaResolutionFallbackLogTests(unittest.TestCase):  # type: ignore[no-redef]
            @unittest.skip("Test harness unavailable outside bootstrap context")
            def test_placeholder(self):
                pass

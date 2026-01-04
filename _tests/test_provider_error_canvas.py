import os
import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.modelHelpers import MissingAPIKeyError, get_token
    from talon_user.lib.providerRegistry import reset_provider_registry
    from talon_user.lib.providerStatusLog import (
        ProviderStatusLog,
        clear_provider_status,
    )

    class ProviderErrorCanvasTests(unittest.TestCase):
        def setUp(self) -> None:
            self._orig_key = os.environ.get("OPENAI_API_KEY")
            if "OPENAI_API_KEY" in os.environ:
                del os.environ["OPENAI_API_KEY"]
            reset_provider_registry()
            settings.set("user.model_provider_current", "openai")
            ProviderStatusLog.lines = []
            ProviderStatusLog.showing = False

        def tearDown(self) -> None:
            if self._orig_key is not None:
                os.environ["OPENAI_API_KEY"] = self._orig_key
            else:
                os.environ.pop("OPENAI_API_KEY", None)
            clear_provider_status()
            ProviderStatusLog.lines = []
            ProviderStatusLog.showing = False

        def test_missing_key_triggers_canvas_error(self) -> None:
            with self.assertRaises(MissingAPIKeyError):
                get_token()
            self.assertTrue(ProviderStatusLog.showing)
            joined = " ".join(ProviderStatusLog.lines)
            self.assertIn("OPENAI_API_KEY", joined)

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
    from talon_user.lib.modelHelpers import get_token
    from talon_user.lib.providerRegistry import (
        AmbiguousProviderError,
        ProviderLookupError,
        provider_registry,
        reset_provider_registry,
    )

    class ProviderRegistryTests(unittest.TestCase):
        def setUp(self) -> None:
            reset_provider_registry()
            self._orig_openai_key = os.environ.get("OPENAI_API_KEY")
            self._orig_tokens = settings.get("user.model_provider_tokens", {})
            self._orig_openai_token_setting = settings.get(
                "user.model_provider_token_openai", ""
            )
            settings.set("user.model_provider_current", "openai")
            settings.set("user.model_provider_tokens", {})
            settings.set("user.model_provider_token_openai", "")
            os.environ["OPENAI_API_KEY"] = "test-key"
            os.environ.pop("GEMINI_API_KEY", None)

        def tearDown(self) -> None:
            if self._orig_openai_key is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = self._orig_openai_key
            settings.set("user.model_provider_tokens", self._orig_tokens or {})
            settings.set(
                "user.model_provider_token_openai", self._orig_openai_token_setting
            )

        def test_defaults_include_openai_and_gemini(self) -> None:
            registry = provider_registry()
            ids = registry.provider_ids()
            self.assertIn("openai", ids)
            self.assertIn("gemini", ids)
            # Aliases should match loosely spoken variants.
            self.assertEqual(registry.resolve("gemeni").id, "gemini")

        def test_set_current_updates_settings(self) -> None:
            registry = provider_registry()
            registry.set_current_provider("gemini")
            self.assertEqual(settings.get("user.model_provider_current"), "gemini")
            self.assertEqual(registry.current_provider_id(), "gemini")

        def test_unknown_provider_raises(self) -> None:
            registry = provider_registry()
            with self.assertRaises(ProviderLookupError):
                registry.resolve("nonexistent")

        def test_ambiguous_provider_raises(self) -> None:
            settings.set(
                "user.model_provider_extra",
                {"providers": [{"id": "openai-eu", "aliases": ["openai"]}]},
            )
            registry = provider_registry()
            with self.assertRaises(AmbiguousProviderError):
                registry.resolve("openai")

        def test_settings_tokens_count_as_available(self) -> None:
            settings.set("user.model_provider_token_openai", "from-settings")
            os.environ.pop("OPENAI_API_KEY", None)
            registry = provider_registry()
            entries = registry.status_entries()
            openai_entry = next(entry for entry in entries if entry["id"] == "openai")
            self.assertTrue(openai_entry["available"])
            self.assertEqual(openai_entry.get("token_source"), "settings")
            token = get_token()
            self.assertEqual(token, "from-settings")

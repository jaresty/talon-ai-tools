import unittest
from unittest.mock import patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon import settings
    from talon_user.lib.providerCanvas import ProviderCanvasState
    from talon_user.lib.providerCommands import UserActions as ProviderActions
    from talon_user.lib.providerRegistry import provider_registry, reset_provider_registry

    class ProviderCommandTests(unittest.TestCase):
        def setUp(self) -> None:
            reset_provider_registry()
            ProviderCanvasState.showing = False
            ProviderCanvasState.lines = []
            settings.set("user.model_provider_current", "openai")
            settings.set("user.model_provider_extra", {})
            settings.set("user.model_provider_probe", 0)

        def test_list_opens_canvas(self) -> None:
            ProviderActions.model_provider_list()
            self.assertTrue(ProviderCanvasState.showing)
            joined = " ".join(ProviderCanvasState.lines).lower()
            self.assertIn("openai", joined)
            self.assertIn("stream", joined)

        def test_switch_and_status(self) -> None:
            ProviderActions.model_provider_use("gemini")
            self.assertEqual(settings.get("user.model_provider_current"), "gemini")
            ProviderActions.model_provider_status()
            joined = " ".join(ProviderCanvasState.lines).lower()
            self.assertIn("gemini", joined)
            self.assertIn("streaming (current)", joined)

        def test_cycle_updates_provider(self) -> None:
            registry = provider_registry()
            start = registry.current_provider_id()
            ProviderActions.model_provider_next()
            next_id = settings.get("user.model_provider_current")
            self.assertNotEqual(start, next_id)

        def test_switch_accepts_spoken_alias(self) -> None:
            ProviderActions.model_provider_use("gemeni")
            self.assertEqual(settings.get("user.model_provider_current"), "gemini")

        def test_switch_with_model_sets_preference(self) -> None:
            settings.set("user.openai_model", "gpt-5")
            ProviderActions.model_provider_use("gemini", "gemini-1.5-flash")
            self.assertEqual(settings.get("user.model_provider_current"), "gemini")
            self.assertEqual(
                settings.get("user.model_provider_model_gemini"), "gemini-1.5-flash"
            )

        def test_switch_with_spoken_model_alias(self) -> None:
            ProviderActions.model_provider_use("gemini", "one five pro")
            self.assertEqual(settings.get("user.model_provider_current"), "gemini")
            self.assertEqual(
                settings.get("user.model_provider_model_gemini"), "gemini-1.5-pro"
            )

        def test_openai_spoken_model_alias(self) -> None:
            settings.set("user.openai_model", "gpt-5")
            ProviderActions.model_provider_use("openai", "four o")
            self.assertEqual(settings.get("user.model_provider_current"), "openai")
            self.assertEqual(settings.get("user.openai_model"), "gpt-4o")

        def test_probe_reachability_errors(self) -> None:
            settings.set("user.model_provider_probe", 1)

            def fake_probe(_cfg):
                return False, "boom"

            registry = provider_registry()
            with patch.object(registry, "_probe_endpoint", side_effect=fake_probe):
                ProviderActions.model_provider_list()
            joined = " ".join(ProviderCanvasState.lines).lower()
            self.assertIn("reachability", joined)

        def test_close_hides_canvas(self) -> None:
            ProviderActions.model_provider_list()
            self.assertTrue(ProviderCanvasState.showing)
            ProviderActions.model_provider_close()
            self.assertFalse(ProviderCanvasState.showing)

        def test_ambiguous_provider_shows_error(self) -> None:
            settings.set(
                "user.model_provider_extra",
                {"providers": [{"id": "openai-eu", "aliases": ["open ai"]}]},
            )
            reset_provider_registry()
            ProviderCanvasState.lines = []
            ProviderCanvasState.showing = False
            ProviderActions.model_provider_use("open ai")
            self.assertTrue(ProviderCanvasState.showing)
            joined = " ".join(ProviderCanvasState.lines).lower()
            self.assertIn("ambiguous", joined)

import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None
else:
    bootstrap()


@unittest.skipIf(bootstrap is None, "Tests disabled inside Talon runtime")
class PersonaOrchestratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from talon_user.lib.personaOrchestrator import PersonaIntentOrchestrator
        from talon_user.lib.personaConfig import persona_catalog

        cls._PersonaIntentOrchestrator = PersonaIntentOrchestrator
        cls._persona_catalog = staticmethod(persona_catalog)

    def setUp(self) -> None:
        # Force refresh so tests observe up-to-date catalog data without relying on
        # cached Talon state from other suites.
        self.orchestrator = self._PersonaIntentOrchestrator.build(force_refresh=True)

    def test_persona_presets_align_with_catalog(self) -> None:
        catalog_keys = set(self._persona_catalog().keys())
        orchestrator_keys = set(self.orchestrator.persona_presets.keys())
        self.assertEqual(
            catalog_keys,
            orchestrator_keys,
            "Persona orchestrator must expose the same preset keys as persona_catalog",
        )

    def test_persona_aliases_include_spoken_and_labels(self) -> None:
        preset = self.orchestrator.persona_presets["teach_junior_dev"]
        for alias in filter(None, [preset.spoken, preset.label]):
            canonical = self.orchestrator.canonical_persona_key(alias)
            self.assertEqual(
                canonical,
                preset.key,
                f"Expected alias '{alias}' to resolve to persona preset '{preset.key}'",
            )

    def test_intent_aliases_include_display_labels(self) -> None:
        display_label = self.orchestrator.intent_display_map["teach"]
        self.assertEqual(display_label, "Teach / explain")
        self.assertEqual(
            self.orchestrator.canonical_intent_key("Teach / explain"),
            "teach",
        )
        self.assertEqual(
            self.orchestrator.canonical_intent_key("teach"),
            "teach",
        )

    def test_axis_tokens_are_sorted(self) -> None:
        axis_tokens = self.orchestrator.axis_tokens
        self.assertIn("voice", axis_tokens)
        voice_tokens = axis_tokens["voice"]
        self.assertEqual(tuple(sorted(voice_tokens)), voice_tokens)
        self.assertIn("as programmer", voice_tokens)
        intent_tokens = axis_tokens["intent"]
        self.assertIn("teach", intent_tokens)

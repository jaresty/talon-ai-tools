import unittest

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib.errors import (
        TalonAIError,
        StateError,
        ConfigError,
        ProviderError,
        error_context,
    )

    class ErrorHierarchyTests(unittest.TestCase):
        def test_talon_ai_error_is_exception(self):
            self.assertTrue(issubclass(TalonAIError, Exception))

        def test_state_error_extends_talon_ai_error(self):
            self.assertTrue(issubclass(StateError, TalonAIError))

        def test_config_error_extends_talon_ai_error(self):
            self.assertTrue(issubclass(ConfigError, TalonAIError))

        def test_provider_error_extends_talon_ai_error(self):
            self.assertTrue(issubclass(ProviderError, TalonAIError))

        def test_state_error_is_catchable_as_talon_ai_error(self):
            with self.assertRaises(TalonAIError):
                raise StateError("bad state")

        def test_config_error_is_catchable_as_talon_ai_error(self):
            with self.assertRaises(TalonAIError):
                raise ConfigError("bad config")

        def test_provider_error_is_catchable_as_talon_ai_error(self):
            with self.assertRaises(TalonAIError):
                raise ProviderError("bad provider")

        def test_errors_carry_message(self):
            err = ConfigError("missing key")
            self.assertIn("missing key", str(err))

    class ErrorContextDecoratorTests(unittest.TestCase):
        def test_error_context_passes_through_return_value(self):
            @error_context("doing a thing")
            def fn():
                return 42

            self.assertEqual(fn(), 42)

        def test_error_context_reraises_with_context(self):
            @error_context("loading config")
            def fn():
                raise ValueError("original")

            with self.assertRaises(TalonAIError) as cm:
                fn()
            self.assertIn("loading config", str(cm.exception))
            self.assertIsInstance(cm.exception.__cause__, ValueError)

        def test_error_context_labels_state_errors(self):
            @error_context("reading state", error_class=StateError)
            def fn():
                raise RuntimeError("boom")

            with self.assertRaises(StateError):
                fn()

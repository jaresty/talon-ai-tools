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

    from talon_user.lib.modelHelpers import (
        MissingAPIKeyError,
        GPTRequestError,
        ClipboardImageError,
        ClipboardImageUnsupportedProvider,
        UnsupportedProviderCapability,
    )

    class ExistingExceptionIntegrationTests(unittest.TestCase):
        """Verify that existing scattered exceptions are in the TalonAIError hierarchy."""

        def test_missing_api_key_is_config_error(self):
            self.assertTrue(issubclass(MissingAPIKeyError, ConfigError))

        def test_gpt_request_error_is_provider_error(self):
            self.assertTrue(issubclass(GPTRequestError, ProviderError))

        def test_clipboard_image_error_is_provider_error(self):
            self.assertTrue(issubclass(ClipboardImageError, ProviderError))

        def test_clipboard_image_unsupported_provider_is_provider_error(self):
            self.assertTrue(issubclass(ClipboardImageUnsupportedProvider, ProviderError))

        def test_unsupported_provider_capability_is_provider_error(self):
            self.assertTrue(issubclass(UnsupportedProviderCapability, ProviderError))

        def test_missing_api_key_catchable_as_talon_ai_error(self):
            with self.assertRaises(TalonAIError):
                raise MissingAPIKeyError()

        def test_gpt_request_error_catchable_as_talon_ai_error(self):
            with self.assertRaises(TalonAIError):
                raise GPTRequestError(500, "internal server error")

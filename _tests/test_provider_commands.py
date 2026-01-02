import unittest
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

if bootstrap is not None:
    from talon_user.lib import providerCommands as provider_module
    from talon_user.lib.providerCommands import UserActions as ProviderActions
    from talon import actions


class ProviderCommandGuardTests(unittest.TestCase):
    def test_provider_actions_respect_in_flight_guard(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                provider_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(provider_module, "provider_registry") as registry,
            patch.object(provider_module, "show_provider_canvas") as show_canvas,
        ):
            ProviderActions.model_provider_list()
            ProviderActions.model_provider_status()
            ProviderActions.model_provider_use("openai")
            ProviderActions.model_provider_next()
            ProviderActions.model_provider_previous()
        registry.assert_not_called()
        show_canvas.assert_not_called()

    def test_provider_switch_respects_guard_through_use(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")
        with (
            patch.object(
                provider_module, "_reject_if_request_in_flight", return_value=True
            ),
            patch.object(actions.user, "model_provider_use") as user_use,
        ):
            ProviderActions.model_provider_switch("openai")
        user_use.assert_not_called()

    def test_request_is_in_flight_delegates_to_request_gating(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        with patch.object(
            provider_module, "request_is_in_flight", return_value=True
        ) as helper:
            self.assertTrue(provider_module._request_is_in_flight())
        helper.assert_called_once_with()

        with patch.object(
            provider_module, "request_is_in_flight", return_value=False
        ) as helper:
            self.assertFalse(provider_module._request_is_in_flight())
        helper.assert_called_once_with()

    def test_reject_if_request_in_flight_notifies_with_drop_message(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

        captured_kwargs: dict[str, object] = {}

        def guard_blocks(**kwargs):
            captured_kwargs.update(kwargs)
            on_block = kwargs.get("on_block")
            self.assertTrue(callable(on_block))
            on_block("in_flight", "Request running")
            return True

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_blocks
            ) as guard,
            patch.object(provider_module, "notify") as notify_mock,
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())

        guard.assert_called_once()
        self.assertEqual(captured_kwargs.get("surface"), "provider_commands")
        self.assertEqual(captured_kwargs.get("source"), "providerCommands")
        self.assertTrue(callable(captured_kwargs.get("notify_fn")))
        notify_mock.assert_called_once_with("Request running")
        set_reason.assert_not_called()

        def guard_fallback(**kwargs):
            captured_kwargs.update(kwargs)
            on_block = kwargs.get("on_block")
            on_block("unknown_reason", "")
            return True

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_fallback
            ),
            patch.object(provider_module, "notify") as notify_mock,
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertTrue(provider_module._reject_if_request_in_flight())

        fallback = "GPT: Request blocked; reason=unknown_reason."
        notify_mock.assert_called_once_with(fallback)
        set_reason.assert_called_once_with("unknown_reason", fallback)

        def guard_allows(**kwargs):
            return False

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_allows
            ) as guard,
            patch.object(provider_module, "last_drop_reason", return_value=""),
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(provider_module._reject_if_request_in_flight())

        guard.assert_called_once()
        set_reason.assert_called_once_with("")

        with (
            patch.object(
                provider_module, "guard_surface_request", side_effect=guard_allows
            ),
            patch.object(
                provider_module, "last_drop_reason", return_value="drop_pending"
            ),
            patch.object(provider_module, "set_drop_reason") as set_reason,
        ):
            self.assertFalse(provider_module._reject_if_request_in_flight())
        set_reason.assert_not_called()


class BarCliCommandPathTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

    def test_bar_cli_command_env_override(self):
        with patch.dict(
            provider_module.os.environ, {"BAR_CLI_PATH": "/custom/bar"}, clear=True
        ):
            self.assertEqual(provider_module._bar_cli_command(), Path("/custom/bar"))

    def test_bar_cli_command_default_path(self):
        with patch.dict(provider_module.os.environ, {}, clear=True):
            path_result = provider_module._bar_cli_command()
            self.assertTrue(str(path_result).endswith("cli/bin/bar"))


class BarCliDelegationTests(unittest.TestCase):
    def setUp(self):
        if bootstrap is None:
            self.skipTest("Talon runtime not available")

    def test_delegate_returns_false_when_flag_disabled(self):
        with (
            patch.object(provider_module.settings, "get", return_value=0),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run") as run_mock,
        ):
            self.assertFalse(
                provider_module._delegate_to_bar_cli("model_provider_list")
            )
        run_mock.assert_not_called()

    def test_delegate_handles_missing_binary(self):
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(
                provider_module.subprocess, "run", side_effect=FileNotFoundError
            ),
        ):
            self.assertFalse(
                provider_module._delegate_to_bar_cli("model_provider_list")
            )

    def test_delegate_handles_non_zero_exit_code(self):
        result = SimpleNamespace(returncode=2, stdout="", stderr="error")
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module.subprocess, "run", return_value=result
            ) as run_mock,
        ):
            self.assertFalse(
                provider_module._delegate_to_bar_cli("model_provider_list")
            )
        run_mock.assert_called_once()
        cmd = run_mock.call_args[0][0]
        self.assertIn("model_provider_list", cmd)

    def test_delegate_returns_true_on_success(self):
        result = SimpleNamespace(returncode=0, stdout="ok", stderr="")
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module.subprocess, "run", return_value=result
            ) as run_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli(
                    "model_provider_use", name="openai", model="gpt-4"
                )
            )
        cmd = run_mock.call_args[0][0]
        self.assertIn("model_provider_use", cmd)
        self.assertIn("--name=openai", cmd)
        self.assertIn("--model=gpt-4", cmd)

    def test_delegate_parses_json_payload_and_notifies(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"notify":"bar ok","debug":"status info"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli(
                    "model_provider_status", probe=True
                )
            )
        notify_mock.assert_called_once_with("bar ok")
        printed_args = " ".join(str(arg) for arg in print_mock.call_args[0])
        self.assertIn("status info", printed_args)

    def test_delegate_handles_invalid_json_stdout(self):
        result = SimpleNamespace(returncode=0, stdout="not json", stderr="")
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch("talon_user.lib.providerCommands.print") as print_mock,
            patch.object(provider_module, "notify") as notify_mock,
        ):
            self.assertTrue(provider_module._delegate_to_bar_cli("model_provider_list"))
        notify_mock.assert_not_called()
        printed_calls = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(any("stdout=" in text for text in printed_calls))
        self.assertTrue(any("not json" in text for text in printed_calls))

    def test_delegate_handles_error_payload(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"error":"cli failed","drop_reason":"cli_error"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_called_once_with("cli failed")
        printed_calls = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any(
                "drop_reason='cli_error'" in text and "cli failed" in text
                for text in printed_calls
            )
        )

    def test_delegate_sets_drop_reason_with_message(self):
        base_result = SimpleNamespace(
            returncode=0,
            stdout='{"error":"cli failed","drop_reason":"cli_error"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=base_result),
            patch.object(provider_module, "notify"),
            patch("talon_user.lib.providerCommands.print"),
            patch("talon_user.lib.providerCommands.set_drop_reason") as set_reason,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        self.assertEqual(set_reason.call_args[0][0], "")
        self.assertEqual(set_reason.call_args[0][1], "cli failed")

        severity_result = SimpleNamespace(
            returncode=0,
            stdout='{"error":"cli failed","drop_reason":"history_save_failed","severity":"warning"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(
                provider_module.subprocess, "run", return_value=severity_result
            ),
            patch.object(provider_module, "notify"),
            patch("talon_user.lib.providerCommands.print"),
            patch("talon_user.lib.providerCommands.set_drop_reason") as set_reason,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        self.assertEqual(set_reason.call_args[0][0], "history_save_failed")
        self.assertEqual(set_reason.call_args[0][1], "[WARNING] cli failed")

    def test_delegate_handles_alert_payload(self):
        result = SimpleNamespace(
            returncode=0, stdout='{"alert":"check settings"}', stderr=""
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_called_once_with("check settings")
        printed_calls = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(any("alert='check settings'" in text for text in printed_calls))

    def test_delegate_logs_breadcrumbs(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"breadcrumbs":["step 1","step 2"]}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_not_called()
        printed_calls = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any("breadcrumbs=['step 1', 'step 2']" in text for text in printed_calls)
        )

    def test_delegate_handles_notice_severity(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"notify":"all good","severity":"warning"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_called_once_with("[WARNING] all good")
        printed_calls = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any(
                "severity=" in text and "warning" in text.lower()
                for text in printed_calls
            )
        )

    def test_delegate_parses_multiline_payload(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='info line\n{"notify":"ok","drop_reason":"cli_error"}\n',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
            patch("talon_user.lib.providerCommands.set_drop_reason") as set_reason,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_called_once_with("ok")
        set_reason.assert_called_once_with("", "ok")

    def test_delegate_logs_unknown_drop_reason(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"error":"cli failed","drop_reason":"cli_custom_unknown"}',
            stderr="",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify"),
            patch("talon_user.lib.providerCommands.set_drop_reason") as set_reason,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        self.assertEqual(set_reason.call_args[0][0], "")
        self.assertEqual(set_reason.call_args[0][1], "cli failed")
        logged = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(
            any("normalised unknown drop_reason" in message for message in logged)
        )

    def test_delegate_logs_stderr_on_success(self):
        result = SimpleNamespace(
            returncode=0,
            stdout='{"notify":"ok"}',
            stderr="stderr warning",
        )
        with (
            patch.object(provider_module.settings, "get", return_value=1),
            patch.object(
                provider_module, "_bar_cli_command", return_value=Path("/tmp/bar")
            ),
            patch.object(provider_module.subprocess, "run", return_value=result),
            patch.object(provider_module, "notify") as notify_mock,
            patch("talon_user.lib.providerCommands.print") as print_mock,
        ):
            self.assertTrue(
                provider_module._delegate_to_bar_cli("model_provider_status")
            )
        notify_mock.assert_called_once_with("ok")
        logged = [
            " ".join(str(arg) for arg in call.args)
            for call in print_mock.call_args_list
        ]
        self.assertTrue(any("stderr warning" in entry for entry in logged))

    def test_parse_bar_cli_payload_multiline_stdout(self):
        result = SimpleNamespace(stdout='info line\n{"notify":"ok"}\n')
        payload = provider_module._parse_bar_cli_payload(result)
        self.assertTrue(payload.has_payload)
        self.assertEqual(payload.notice, "ok")
        self.assertFalse(payload.decode_failed)

    def test_parse_bar_cli_payload_invalid_json(self):
        result = SimpleNamespace(stdout="not json")
        payload = provider_module._parse_bar_cli_payload(result)
        self.assertIsInstance(payload, provider_module.BarCliPayload)
        self.assertFalse(payload.has_payload)
        self.assertTrue(payload.decode_failed)
        self.assertIsNone(payload.raw)
        self.assertIsNone(payload.notice)
        self.assertIsNone(payload.error)
        self.assertIsNone(payload.debug)
        self.assertIsNone(payload.drop_reason)
        self.assertIsNone(payload.alert)
        self.assertIsNone(payload.severity)

    def test_format_severity_prefix_helper(self):
        prefix, label = provider_module._format_severity_prefix("warning")
        self.assertEqual(prefix, "[WARNING] ")
        self.assertEqual(label, "WARNING")
        prefix_none, label_none = provider_module._format_severity_prefix(None)
        self.assertEqual(prefix_none, "")
        self.assertEqual(label_none, "")
        prefix_space, label_space = provider_module._format_severity_prefix(
            " critical "
        )
        self.assertEqual(prefix_space, "[CRITICAL] ")
        self.assertEqual(label_space, "CRITICAL")

    def test_parse_breadcrumbs_trims_and_ignores_empty(self):
        result = SimpleNamespace(stdout='{"breadcrumbs": [" step 1 ", "", "step 3"]}')
        payload = provider_module._parse_bar_cli_payload(result)
        self.assertEqual(payload.breadcrumbs, ["step 1", "step 3"])
        self.assertFalse(payload.decode_failed)


if __name__ == "__main__":
    unittest.main()

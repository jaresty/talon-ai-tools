import unittest
from pathlib import Path
import io
import json
import hashlib
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import http.server
import threading
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from unittest import mock
from typing import Any, Dict, List, cast

from talon import actions


REPO_ROOT = Path(__file__).resolve().parents[1]

SIGNATURE_KEY = "adr-0063-cli-release-signature"
os.environ.setdefault("CLI_RELEASE_SIGNING_KEY", SIGNATURE_KEY)
os.environ.setdefault("CLI_RELEASE_SIGNING_KEY_ID", "local-dev")
os.environ.setdefault(
    "CLI_SIGNATURE_METADATA", str(REPO_ROOT / "artifacts" / "cli" / "signatures.json")
)
os.environ.setdefault(
    "CLI_SIGNATURE_TELEMETRY",
    str(REPO_ROOT / "var" / "cli-telemetry" / "signature-metadata.json"),
)
os.environ.setdefault(
    "CLI_SIGNATURE_TELEMETRY_EXPORT",
    str(REPO_ROOT / "artifacts" / "cli" / "signature-telemetry.json"),
)
go_path = shutil.which("go")
if go_path:
    os.environ.setdefault("CLI_GO_COMMAND", go_path)

import lib.cliDelegation as cliDelegation
import lib.cliHealth as cliHealth
import lib.providerCommands as providerCommands
import lib.providerRegistry as providerRegistry
import lib.providerStatusLog as providerStatusLog
import lib.surfaceGuidance as surfaceGuidance
from lib import historyLifecycle, requestBus, requestGating, responseCanvasFallback
from lib.requestState import RequestPhase
import scripts.tools.install_bar_cli as install_bar_cli
import scripts.tools.package_bar_cli as package_bar_cli
from lib.bootstrapTelemetry import (
    clear_bootstrap_warning_events,
    get_bootstrap_warning_messages,
)


bootstrap_module: Any | None = None

try:
    import bootstrap as bootstrap_module
except ModuleNotFoundError:  # Talon runtime
    bootstrap = None

    def get_bootstrap_warnings(*, clear: bool = False):  # type: ignore[override]
        return []
else:
    bootstrap = getattr(bootstrap_module, "bootstrap", None)
    get_bootstrap_warnings = getattr(
        bootstrap_module,
        "get_bootstrap_warnings",
        lambda *, clear=False: [],
    )
    if callable(bootstrap):
        bootstrap()
    else:
        bootstrap = None

CLI_BINARY = REPO_ROOT / "bin" / "bar"
SCHEMA_BUNDLE = REPO_ROOT / "docs" / "schema" / "command-surface.json"
PACKAGED_CLI_DIR = REPO_ROOT / "artifacts" / "cli"

RECORDED_HELLO_META = "## Provider replay\nRecorded on 2025-12-18."
RECORDED_HELLO_CHUNKS = [
    "Recorded provider: hello world summary.",
    "This transcript was captured offline.",
    "Tokens align with provider usage.",
]
RECORDED_HELLO_MESSAGE = "\n".join(RECORDED_HELLO_CHUNKS)
RECORDED_HELLO_SUMMARY = RECORDED_HELLO_CHUNKS[0]
RECORDED_HELLO_HIGHLIGHTS = ["#recorded", "#provider"]
RECORDED_HELLO_USAGE = {
    "prompt_tokens": 2,
    "completion_tokens": 15,
    "total_tokens": 17,
}

RECORDED_UI_META = "## Provider replay\nTalon delegate recorded stream."
RECORDED_UI_CHUNKS = [
    "Recorded CLI: streaming answer for Talon adapters.",
    "History synced from provider transcript.",
    "Canvas refresh triggered from recorded stream.",
]
RECORDED_UI_MESSAGE = "\n".join(RECORDED_UI_CHUNKS)
RECORDED_UI_SUMMARY = RECORDED_UI_CHUNKS[0]
RECORDED_UI_HIGHLIGHTS = ["#delegate", "#talon"]
RECORDED_UI_USAGE = {
    "prompt_tokens": 4,
    "completion_tokens": 18,
    "total_tokens": 22,
}


def _target_suffix() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch = arch_map.get(machine, machine)
    return f"bar-{system}-{arch}"


def _packaged_cli_tarball() -> Path:
    return PACKAGED_CLI_DIR / f"{_target_suffix()}.tar.gz"


def _packaged_cli_manifest(tarball: Path) -> Path:
    return tarball.with_name(f"{tarball.name}.sha256")


def _canonical_snapshot_digest(payload: dict) -> str:
    canonical = dict(payload)
    canonical["updated_at"] = None
    return hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _signature_for(message: str) -> str:
    return hashlib.sha256((SIGNATURE_KEY + "\n" + message).encode("utf-8")).hexdigest()


if bootstrap is None:

    class CLITalonParityPlaceholder(unittest.TestCase):
        @unittest.skip("Talon runtime cannot execute CLI parity harness")
        def test_skip_in_talon_runtime(self) -> None:  # pragma: no cover - Talon skip
            pass

else:

    class CLITalonParityTests(unittest.TestCase):
        def _signature_metadata_path(self) -> Path:
            return PACKAGED_CLI_DIR / "signatures.json"

        def _signature_telemetry_path(self) -> Path:
            return Path(
                os.environ.get(
                    "CLI_SIGNATURE_TELEMETRY",
                    "var/cli-telemetry/signature-metadata.json",
                )
            )

        def _load_signature_metadata(self) -> dict:
            metadata_path = self._signature_metadata_path()
            self.assertTrue(
                metadata_path.exists(),
                "Signature metadata missing; run loop-0039 to rebuild",
            )
            return json.loads(metadata_path.read_text(encoding="utf-8"))

        def _write_signature_telemetry(
            self,
            *,
            signing_key_id: str | None = None,
            status: str = "green",
            issues: list[str] | None = None,
        ) -> dict:
            metadata = self._load_signature_metadata()
            payload = {
                "status": status,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "signing_key_id": signing_key_id
                or metadata.get("signing_key_id")
                or os.environ.get("CLI_RELEASE_SIGNING_KEY_ID", "local-dev"),
                "tarball_manifest": dict(metadata.get("tarball_manifest") or {}),
                "delegation_snapshot": dict(metadata.get("delegation_snapshot") or {}),
            }
            if issues:
                payload["issues"] = list(issues)
            telemetry_path = self._signature_telemetry_path()
            telemetry_path.parent.mkdir(parents=True, exist_ok=True)
            telemetry_path.write_text(
                json.dumps(payload, indent=2) + "\n",
                encoding="utf-8",
            )
            return payload

        def test_cli_health_probe_emits_json_status(self) -> None:
            self.assertTrue(
                CLI_BINARY.exists(),
                "CLI binary missing; run loop-0005 to restore bar stub",
            )

            result = subprocess.run(
                [str(CLI_BINARY), "--health"],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertIn("version", payload)
            self.assertEqual(
                payload.get("runtime"),
                "go",
                "CLI runtime must report Go binary; stubbed implementation detected",
            )
            self.assertEqual(
                payload.get("executor"),
                "compiled",
                "CLI must run compiled binary rather than go run stub",
            )
            self.assertEqual(
                payload.get("binary_path"),
                "bin/bar.bin",
                "CLI must report compiled binary path relative to repo root",
            )

        def test_schema_bundle_contains_version_marker(self) -> None:
            self.assertTrue(
                SCHEMA_BUNDLE.exists(),
                "Schema bundle missing; run loop-0006 to restore",
            )

            payload = json.loads(SCHEMA_BUNDLE.read_text(encoding="utf-8"))
            self.assertIn("version", payload)
            self.assertIn("commands", payload)

        def test_cli_schema_command_outputs_bundle(self) -> None:
            result = subprocess.run(
                [str(CLI_BINARY), "schema"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = SCHEMA_BUNDLE.read_text(encoding="utf-8").strip()
            self.assertEqual(result.stdout.strip(), expected)

        def test_cli_delegate_executes_request(self) -> None:
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            requestBus.emit_reset()
            payload = {
                "request_id": "req-123",
                "prompt": {
                    "text": "hello world",
                },
            }
            meta_text = RECORDED_HELLO_META
            expected_chunks = RECORDED_HELLO_CHUNKS
            try:
                success, response, error_message = cliDelegation.delegate_request(
                    payload
                )
                self.assertTrue(success, error_message)
                self.assertEqual(response.get("status"), "ok")
                self.assertEqual(response.get("request_id"), "req-123")
                message = response.get("message") or ""
                self.assertEqual(message, RECORDED_HELLO_MESSAGE)
                self.assertEqual(response.get("meta"), meta_text)
                result = response.get("result") or {}
                self.assertEqual(result.get("chunk_count"), len(expected_chunks))
                self.assertEqual(result.get("summary"), RECORDED_HELLO_SUMMARY)
                self.assertEqual(
                    result.get("replay_summary"),
                    f"{len(expected_chunks)} chunk(s) replayed",
                )
                self.assertEqual(result.get("highlights"), RECORDED_HELLO_HIGHLIGHTS)
                usage = result.get("usage") or {}
                self.assertEqual(usage, RECORDED_HELLO_USAGE)
                prompt_tokens = usage.get("prompt_tokens")
                completion_tokens = usage.get("completion_tokens")
                self.assertIsInstance(prompt_tokens, int)
                self.assertIsInstance(completion_tokens, int)
                prompt_tokens_int = cast(int, prompt_tokens)
                completion_tokens_int = cast(int, completion_tokens)
                self.assertEqual(
                    prompt_tokens_int, RECORDED_HELLO_USAGE["prompt_tokens"]
                )
                self.assertEqual(
                    completion_tokens_int,
                    RECORDED_HELLO_USAGE["completion_tokens"],
                )
                self.assertEqual(
                    usage.get("total_tokens"),
                    prompt_tokens_int + completion_tokens_int,
                )

                chunks = result.get("chunks") or []
                self.assertEqual(chunks, expected_chunks)
                analysis = result.get("response_analysis") or {}
                self.assertEqual(analysis.get("lines"), len(expected_chunks))
                self.assertEqual(error_message, "")
                events = response.get("events") or []
                event_dicts = [event for event in events if isinstance(event, dict)]
                kinds = [event.get("kind") for event in event_dicts]
                self.assertIn("begin_stream", kinds)
                self.assertIn("complete", kinds)
                self.assertIn("usage", kinds)
                append_texts = []
                for event in event_dicts:
                    if event.get("kind") != "append":
                        continue
                    delta = event.get("delta")
                    if isinstance(delta, dict):
                        append_texts.append(delta.get("text"))
                self.assertEqual(append_texts, expected_chunks)
                usage_events = [
                    event for event in event_dicts if event.get("kind") == "usage"
                ]
                self.assertEqual(len(usage_events), 1)
                self.assertEqual(usage_events[0].get("usage"), usage)
                final_state = requestBus.current_state()
                self.assertEqual(final_state.phase, RequestPhase.DONE)
                entry = historyLifecycle.latest()
                self.assertIsNotNone(entry)
                assert entry is not None
                self.assertEqual(entry.request_id, "req-123")
                self.assertEqual(entry.meta.strip(), meta_text)
                self.assertIn(RECORDED_HELLO_SUMMARY, entry.response)
            finally:
                requestBus.emit_reset()
                responseCanvasFallback.clear_all_fallbacks()
                historyLifecycle.clear_history()

        def test_cli_delegate_failure_disables_delegation(self) -> None:
            cliDelegation.reset_state()
            payload = {"request_id": "req-error"}
            success, response, error_message = cliDelegation.delegate_request(payload)
            self.assertFalse(success)
            self.assertEqual(response, {})
            self.assertIn("prompt.text", error_message)
            self.assertFalse(cliDelegation.delegation_enabled())
            cliDelegation.reset_state()

        def test_cli_delegate_surfaces_history_and_canvas(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-cli-ui",
                "prompt": {"text": "delegate streaming for talon"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            meta_text = RECORDED_UI_META
            try:
                success, response, error_message = cliDelegation.delegate_request(
                    payload
                )
                self.assertTrue(success, error_message)
                self.assertEqual(response.get("message"), RECORDED_UI_MESSAGE)
                result = response.get("result") or {}
                self.assertEqual(result.get("chunks"), RECORDED_UI_CHUNKS)
                self.assertEqual(result.get("highlights"), RECORDED_UI_HIGHLIGHTS)
                self.assertEqual(result.get("usage"), RECORDED_UI_USAGE)
                entry = historyLifecycle.latest()
                self.assertIsNotNone(entry)
                assert entry is not None
                self.assertEqual(entry.request_id, "req-cli-ui")
                self.assertIn("bound", entry.axes.get("scope", []))
                self.assertIn("jog", entry.axes.get("directional", []))
                self.assertEqual(entry.meta.strip(), meta_text)
                self.assertIn(RECORDED_UI_SUMMARY, entry.response)
                fallback_text = responseCanvasFallback.fallback_for("req-cli-ui")
                self.assertIn(RECORDED_UI_SUMMARY, fallback_text)
                action_names = [call[0] for call in actions.user.calls]
                self.assertIn("model_response_canvas_open", action_names)
                self.assertIn("model_response_canvas_refresh", action_names)
            finally:
                responseCanvasFallback.clear_all_fallbacks()
                historyLifecycle.clear_history()
                actions.user.calls.clear()
                cliDelegation.reset_state()

        def test_cli_delegate_uses_external_provider_command(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-cmd",
                "prompt": {"text": "live provider"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / "provider_stub.py"
                script_content = """#!/usr/bin/env python3
import json
import sys

request = json.load(sys.stdin)
prompt = request.get("prompt", {}).get("text", "")
chunks = [
    f"Live provider chunk: {prompt}",
    "Live provider completion chunk.",
]
message = "\\n".join(chunks)
prompt_tokens = len(prompt.split())
completion_tokens = sum(len(chunk.split()) for chunk in chunks)
usage = {
    "prompt_tokens": prompt_tokens,
    "completion_tokens": completion_tokens,
    "total_tokens": prompt_tokens + completion_tokens,
}
response = {
    "status": "ok",
    "message": message,
    "meta": "## Provider replay\\nLive provider command.",
    "result": {
        "answer": message,
        "summary": chunks[0],
        "replay_summary": f"{len(chunks)} chunk(s) replayed",
        "chunks": chunks,
        "chunk_count": len(chunks),
        "highlights": ["#live", "#provider"],
        "response_analysis": {
            "characters": len(message),
            "lines": len(chunks),
        },
        "usage": usage,
        "meta": "## Provider replay\\nLive provider command.",
    },
    "events": [
        {
            "kind": "append",
            "delta": {
                "role": "assistant",
                "type": "text",
                "index": index,
                "text": chunk,
            },
        }
        for index, chunk in enumerate(chunks)
    ]
}
response["events"].append({"kind": "usage", "usage": usage})
json.dump(response, sys.stdout)
"""

                script_path.write_text(script_content, encoding="utf-8")
                script_path.chmod(0o755)

                expected_chunks = [
                    "Live provider chunk: live provider",
                    "Live provider completion chunk.",
                ]
                expected_message = "\n".join(expected_chunks)
                expected_meta = "## Provider replay\nLive provider command."
                expected_usage = {
                    "prompt_tokens": 2,
                    "completion_tokens": 9,
                    "total_tokens": 11,
                }

                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_COMMAND": f"{sys.executable} {script_path}",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertTrue(success, error_message)
                        self.assertEqual(response.get("status"), "ok")
                        self.assertEqual(response.get("request_id"), "req-provider-cmd")
                        self.assertEqual(response.get("message"), expected_message)
                        self.assertEqual(response.get("meta"), expected_meta)

                        result = response.get("result") or {}
                        self.assertEqual(result.get("chunks"), expected_chunks)
                        self.assertEqual(result.get("summary"), expected_chunks[0])
                        self.assertEqual(
                            result.get("highlights"), ["#live", "#provider"]
                        )
                        self.assertEqual(result.get("usage"), expected_usage)
                        self.assertEqual(
                            result.get("replay_summary"),
                            f"{len(expected_chunks)} chunk(s) replayed",
                        )
                        analysis = result.get("response_analysis") or {}
                        self.assertEqual(analysis.get("lines"), len(expected_chunks))

                        events = response.get("events") or []
                        event_kinds = [
                            event.get("kind")
                            for event in events
                            if isinstance(event, dict)
                        ]
                        self.assertIn("usage", event_kinds)
                        append_texts = []
                        for event in events:
                            if not isinstance(event, dict):
                                continue
                            if event.get("kind") != "append":
                                continue
                            delta = event.get("delta")
                            if isinstance(delta, dict):
                                append_texts.append(delta.get("text"))
                        self.assertEqual(append_texts, expected_chunks)

                        entry = historyLifecycle.latest()
                        self.assertIsNotNone(entry)
                        assert entry is not None
                        self.assertEqual(entry.request_id, "req-provider-cmd")
                        self.assertEqual(entry.meta.strip(), expected_meta)
                        self.assertIn(expected_chunks[0], entry.response)
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()

        @staticmethod
        def _http_handler_factory(
            response_payload: Dict[str, Any], sentinel_path: Path
        ):
            class _Handler(http.server.BaseHTTPRequestHandler):
                def do_POST(self) -> None:
                    try:
                        content_length = int(self.headers.get("Content-Length", "0"))
                    except ValueError:
                        content_length = 0
                    if content_length > 0:
                        self.rfile.read(content_length)
                    sentinel_path.write_text("provider-called", encoding="utf-8")
                    body = json.dumps(response_payload).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                    return

            return _Handler

        def test_cli_delegate_uses_http_provider_endpoint(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-http",
                "prompt": {"text": "http provider"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            with tempfile.TemporaryDirectory() as tmpdir:
                sentinel_path = Path(tmpdir) / "http-called.txt"
                expected_chunks = [
                    "HTTP provider chunk: http provider",
                    "HTTP provider completion chunk.",
                ]
                expected_message = "\n".join(expected_chunks)
                expected_meta = "## Provider replay\nHTTP provider command."
                http_response = {
                    "status": "ok",
                    "message": expected_message,
                    "meta": expected_meta,
                    "result": {
                        "answer": expected_message,
                        "summary": expected_chunks[0],
                        "replay_summary": f"{len(expected_chunks)} chunk(s) replayed",
                        "chunks": expected_chunks,
                        "chunk_count": len(expected_chunks),
                        "highlights": ["#http", "#provider"],
                        "response_analysis": {
                            "characters": len(expected_message),
                            "lines": len(expected_chunks),
                        },
                        "usage": {
                            "prompt_tokens": 3,
                            "completion_tokens": 9,
                            "total_tokens": 12,
                        },
                        "meta": expected_meta,
                    },
                    "events": [
                        {
                            "kind": "append",
                            "delta": {
                                "role": "assistant",
                                "type": "text",
                                "index": index,
                                "text": chunk,
                            },
                        }
                        for index, chunk in enumerate(expected_chunks)
                    ]
                    + [
                        {
                            "kind": "usage",
                            "usage": {
                                "prompt_tokens": 3,
                                "completion_tokens": 9,
                                "total_tokens": 12,
                            },
                        }
                    ],
                }
                handler = self._http_handler_factory(http_response, sentinel_path)
                server = http.server.HTTPServer(("127.0.0.1", 0), handler)
                thread = threading.Thread(
                    target=server.serve_forever,
                    name="http-provider-server",
                    daemon=True,
                )
                thread.start()
                endpoint = (
                    f"http://{server.server_address[0]}:{server.server_address[1]}"
                )
                try:
                    with mock.patch.dict(
                        os.environ,
                        {
                            "BAR_PROVIDER_HTTP_ENDPOINT": endpoint,
                            "BAR_PROVIDER_COMMAND_MODE": "http",
                        },
                    ):
                        try:
                            success, response, error_message = (
                                cliDelegation.delegate_request(payload)
                            )
                            self.assertTrue(success, error_message)
                            self.assertTrue(
                                sentinel_path.exists(),
                                "HTTP provider endpoint should be called",
                            )
                            self.assertEqual(response.get("status"), "ok")
                            self.assertEqual(response.get("message"), expected_message)
                            self.assertEqual(response.get("meta"), expected_meta)
                            result = response.get("result") or {}
                            self.assertEqual(result.get("chunks"), expected_chunks)
                            self.assertEqual(result.get("summary"), expected_chunks[0])
                            self.assertEqual(
                                result.get("highlights"), ["#http", "#provider"]
                            )
                            usage = result.get("usage") or {}
                            self.assertEqual(usage.get("prompt_tokens"), 3)
                            self.assertEqual(usage.get("completion_tokens"), 9)
                            self.assertEqual(usage.get("total_tokens"), 12)
                        finally:
                            cliDelegation.reset_state()
                            responseCanvasFallback.clear_all_fallbacks()
                            historyLifecycle.clear_history()
                            actions.user.calls.clear()
                finally:
                    server.shutdown()
                    thread.join()

        def test_cli_delegate_uses_http_bearer_token(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-http-auth",
                "prompt": {"text": "http provider"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }

            class _AuthHandler(http.server.BaseHTTPRequestHandler):
                received_headers: List[str] = []

                def do_POST(self) -> None:
                    _AuthHandler.received_headers.append(
                        self.headers.get("Authorization") or ""
                    )
                    body = json.dumps(
                        {
                            "status": "ok",
                            "message": RECORDED_HELLO_MESSAGE,
                        }
                    ).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                    return

            _AuthHandler.received_headers = []
            server = http.server.HTTPServer(("127.0.0.1", 0), _AuthHandler)
            thread = threading.Thread(
                target=server.serve_forever,
                name="http-provider-auth-server",
                daemon=True,
            )
            thread.start()
            endpoint = f"http://{server.server_address[0]}:{server.server_address[1]}"
            try:
                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_HTTP_ENDPOINT": endpoint,
                        "BAR_PROVIDER_COMMAND_MODE": "http",
                        "BAR_PROVIDER_HTTP_BEARER": "token-123",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertTrue(success, error_message)
                        self.assertEqual(
                            _AuthHandler.received_headers,
                            ["Bearer token-123"],
                        )
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()
            finally:
                server.shutdown()
                thread.join()

        def test_cli_delegate_http_retries_then_falls_back(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-http-retry",
                "prompt": {"text": "hello world"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }

            class _RetryHandler(http.server.BaseHTTPRequestHandler):
                attempts = 0

                def do_POST(self) -> None:
                    _RetryHandler.attempts += 1
                    body = b"server error"
                    self.send_response(500)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)

                def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                    return

            _RetryHandler.attempts = 0
            server = http.server.HTTPServer(("127.0.0.1", 0), _RetryHandler)
            thread = threading.Thread(
                target=server.serve_forever,
                name="http-provider-retry-server",
                daemon=True,
            )
            thread.start()
            endpoint = f"http://{server.server_address[0]}:{server.server_address[1]}"
            try:
                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_HTTP_ENDPOINT": endpoint,
                        "BAR_PROVIDER_COMMAND_MODE": "http",
                        "BAR_PROVIDER_HTTP_RETRIES": "3",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertTrue(success, error_message)
                        self.assertGreaterEqual(_RetryHandler.attempts, 3)
                        meta_text = response.get("meta") or ""
                        self.assertIn("HTTP fallback", meta_text)
                        self.assertIn("after", meta_text)
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()
            finally:
                server.shutdown()
                thread.join()

        def test_cli_delegate_http_falls_back_when_endpoint_missing(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-http-fallback",
                "prompt": {"text": "hello world"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            sentinel_path = Path(tempfile.mkdtemp()) / "http-called.txt"
            with mock.patch.dict(
                os.environ,
                {
                    "BAR_PROVIDER_HTTP_ENDPOINT": "",
                    "BAR_PROVIDER_COMMAND_MODE": "http",
                },
            ):
                try:
                    success, response, error_message = cliDelegation.delegate_request(
                        payload
                    )
                    self.assertTrue(success, error_message)
                    message = response.get("message") or ""
                    self.assertEqual(message, RECORDED_HELLO_MESSAGE)
                    meta_text = response.get("meta") or ""
                    self.assertIn("HTTP fallback", meta_text)
                    self.assertFalse(
                        sentinel_path.exists(),
                        "HTTP endpoint should not be called when missing",
                    )
                finally:
                    cliDelegation.reset_state()
                    responseCanvasFallback.clear_all_fallbacks()
                    historyLifecycle.clear_history()
                    actions.user.calls.clear()

        def test_cli_delegate_skips_provider_command_when_disabled(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-cmd",
                "prompt": {"text": "live provider"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / "provider_stub.py"
                sentinel_path = Path(tmpdir) / "command-ran.txt"
                script_content = f"""#!/usr/bin/env python3
import json
import sys
from pathlib import Path

Path(r"{sentinel_path}").write_text("command executed", encoding="utf-8")
request = json.load(sys.stdin)
json.dump({{"status": "ok", "message": "provider command"}}, sys.stdout)
"""
                script_path.write_text(script_content, encoding="utf-8")
                script_path.chmod(0o755)

                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_COMMAND": f"{sys.executable} {script_path}",
                        "BAR_PROVIDER_COMMAND_MODE": "disabled",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertTrue(success, error_message)
                        message = response.get("message") or ""
                        self.assertIn("Summary: live provider", message)
                        self.assertFalse(
                            sentinel_path.exists(),
                            "provider command should not execute when disabled",
                        )
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()

        def test_cli_delegate_stays_fixture_only_when_mode_set(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-fixture",
                "prompt": {"text": "hello world"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / "provider_stub.py"
                sentinel_path = Path(tmpdir) / "command-ran.txt"
                script_content = f"""#!/usr/bin/env python3
import json
import sys
from pathlib import Path

Path(r"{sentinel_path}").write_text("command executed", encoding="utf-8")
request = json.load(sys.stdin)
json.dump({{"status": "ok", "message": "provider command"}}, sys.stdout)
"""
                script_path.write_text(script_content, encoding="utf-8")
                script_path.chmod(0o755)

                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_COMMAND": f"{sys.executable} {script_path}",
                        "BAR_PROVIDER_COMMAND_MODE": "fixtures-only",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertTrue(success, error_message)
                        message = response.get("message") or ""
                        self.assertEqual(message, RECORDED_HELLO_MESSAGE)
                        self.assertFalse(
                            sentinel_path.exists(),
                            "provider command should not execute when fixtures-only",
                        )
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()

        def test_cli_fixture_only_mode_errors_without_transcript(self) -> None:
            actions.user.calls.clear()
            historyLifecycle.clear_history()
            responseCanvasFallback.clear_all_fallbacks()
            cliDelegation.reset_state()
            payload = {
                "request_id": "req-provider-missing-fixture",
                "prompt": {"text": "missing fixture"},
                "axes": {"scope": ["bound"]},
                "provider_id": "cli",
            }
            with tempfile.TemporaryDirectory() as tmpdir:
                script_path = Path(tmpdir) / "provider_stub.py"
                sentinel_path = Path(tmpdir) / "command-ran.txt"
                script_content = f"""#!/usr/bin/env python3
import json
import sys
from pathlib import Path

Path(r"{sentinel_path}").write_text("command executed", encoding="utf-8")
request = json.load(sys.stdin)
json.dump({{"status": "ok", "message": "provider command"}}, sys.stdout)
"""
                script_path.write_text(script_content, encoding="utf-8")
                script_path.chmod(0o755)

                with mock.patch.dict(
                    os.environ,
                    {
                        "BAR_PROVIDER_COMMAND": f"{sys.executable} {script_path}",
                        "BAR_PROVIDER_COMMAND_MODE": "fixtures-only",
                    },
                ):
                    try:
                        success, response, error_message = (
                            cliDelegation.delegate_request(payload)
                        )
                        self.assertFalse(success)
                        self.assertIn("fixtures-only", error_message)
                        self.assertFalse(
                            sentinel_path.exists(),
                            "provider command should not execute when fixtures-only",
                        )
                    finally:
                        cliDelegation.reset_state()
                        responseCanvasFallback.clear_all_fallbacks()
                        historyLifecycle.clear_history()
                        actions.user.calls.clear()

        def test_install_cli_rebuilds_missing_signature_metadata(self) -> None:
            metadata_path = self._signature_metadata_path()
            manifest = _packaged_cli_manifest(_packaged_cli_tarball())
            manifest_sig_path = manifest.with_suffix(manifest.suffix + ".sig")
            snapshot_manifest_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256"
            snapshot_sig_path = snapshot_manifest_path.with_suffix(
                snapshot_manifest_path.suffix + ".sig"
            )
            snapshot_path = PACKAGED_CLI_DIR / "delegation-state.json"
            telemetry_path = self._signature_telemetry_path()

            metadata_backup = (
                metadata_path.read_bytes() if metadata_path.exists() else None
            )
            telemetry_backup = (
                telemetry_path.read_bytes() if telemetry_path.exists() else None
            )

            metadata_path.unlink(missing_ok=True)
            telemetry_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.clear_drop_reason()
            actions.user.calls.clear()

            def _write_metadata_stub() -> None:
                from scripts.tools import package_bar_cli as pkg

                manifest_recorded = manifest.read_text(encoding="utf-8").strip()
                manifest_signature = manifest_sig_path.read_text(
                    encoding="utf-8"
                ).strip()
                snapshot_recorded = snapshot_manifest_path.read_text(
                    encoding="utf-8"
                ).strip()
                snapshot_signature = snapshot_sig_path.read_text(
                    encoding="utf-8"
                ).strip()
                snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
                pkg._write_signature_metadata(
                    manifest_recorded,
                    manifest_signature,
                    snapshot_recorded,
                    snapshot_signature,
                    snapshot_payload,
                )

            try:
                with mock.patch(
                    "scripts.tools.install_bar_cli._invoke_package_cli",
                    side_effect=_write_metadata_stub,
                ) as package_mock:
                    install_bar_cli.install_cli(quiet=True)
                    package_mock.assert_called()
                self.assertTrue(
                    metadata_path.exists(),
                    "Auto-packaging should recreate signature metadata",
                )
            finally:
                if metadata_backup is None:
                    metadata_path.unlink(missing_ok=True)
                else:
                    metadata_path.write_bytes(metadata_backup)
                if telemetry_backup is None:
                    telemetry_path.unlink(missing_ok=True)
                else:
                    telemetry_path.write_bytes(telemetry_backup)
                cliDelegation.reset_state()
                historyLifecycle.clear_drop_reason()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                get_bootstrap_warning_messages(clear=True)
                actions.user.calls.clear()

        def test_install_cli_missing_go_emits_hint(self) -> None:
            metadata_path = self._signature_metadata_path()
            metadata_backup = (
                metadata_path.read_bytes() if metadata_path.exists() else None
            )
            metadata_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.clear_drop_reason()
            with mock.patch(
                "scripts.tools.install_bar_cli._invoke_package_cli",
                side_effect=FileNotFoundError("go"),
            ):
                with self.assertRaises(install_bar_cli.ReleaseSignatureError) as ctx:
                    install_bar_cli.install_cli(quiet=True)
            self.assertIn("CLI_GO_COMMAND", str(ctx.exception))
            if metadata_backup is None:
                metadata_path.unlink(missing_ok=True)
            else:
                metadata_path.write_bytes(metadata_backup)
            cliDelegation.reset_state()
            historyLifecycle.clear_drop_reason()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)
            get_bootstrap_warning_messages(clear=True)

        def test_install_cli_creates_runtime_state_when_missing(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_backup = state_path.read_bytes() if state_path.exists() else None
            try:
                state_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                historyLifecycle.clear_drop_reason()
                install_bar_cli.install_cli(quiet=True)
                self.assertTrue(
                    state_path.exists(),
                    "Install should recreate delegation state snapshot when missing",
                )
            finally:
                if state_backup is None:
                    state_path.unlink(missing_ok=True)
                else:
                    state_path.write_bytes(state_backup)
                cliDelegation.reset_state()
                historyLifecycle.clear_drop_reason()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                get_bootstrap_warning_messages(clear=True)

        def test_health_failure_auto_repackages_signature_telemetry(self) -> None:
            cliDelegation.reset_state()
            cliDelegation._AUTO_REPACKAGE_ATTEMPTED = False
            with mock.patch("lib.cliDelegation.subprocess.run") as run_mock:
                run_mock.return_value = subprocess.CompletedProcess([], 0)
                cliDelegation.record_health_failure(
                    "signature telemetry mismatch detected during bootstrap"
                )
                run_mock.assert_called_once()
                args, _ = run_mock.call_args
                self.assertIn("check_cli_assets.py", args[0][1])
            cliDelegation._AUTO_REPACKAGE_ATTEMPTED = False
            cliDelegation.reset_state()

        def test_health_failure_auto_installs_missing_cli_binary(self) -> None:
            cliDelegation.reset_state()
            cliDelegation._AUTO_INSTALL_ATTEMPTED = False
            with mock.patch(
                "scripts.tools.install_bar_cli.install_cli"
            ) as install_mock:
                cliDelegation.record_health_failure(
                    "[Errno 2] No such file or directory: 'bin/bar'"
                )
                install_mock.assert_called_once()
            cliDelegation._AUTO_INSTALL_ATTEMPTED = False
            cliDelegation.reset_state()

        def test_package_go_command_prefers_setting(self) -> None:
            with mock.patch.dict(os.environ, {"CLI_GO_COMMAND": ""}, clear=False):
                with mock.patch.object(
                    package_bar_cli, "talon_settings"
                ) as settings_mock:
                    settings_mock.get.return_value = "/custom/go"
                    with mock.patch("shutil.which", return_value=None):
                        with mock.patch.object(
                            package_bar_cli,
                            "PREFERRED_GO_PATHS",
                            [Path("/unlikely/path/go")],
                        ):
                            command = package_bar_cli._go_command()
            self.assertEqual(command, ["/custom/go"])

        def test_package_go_command_prefers_fallback_paths(self) -> None:
            temp_path = Path("var/cli-go-fallback/bin/go")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                temp_path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
                temp_path.chmod(0o755)
                with mock.patch.dict(os.environ, {"CLI_GO_COMMAND": ""}, clear=False):
                    with mock.patch.object(package_bar_cli, "talon_settings", None):
                        with mock.patch("shutil.which", return_value=None):
                            with mock.patch.object(
                                package_bar_cli,
                                "PREFERRED_GO_PATHS",
                                [temp_path],
                            ):
                                command = package_bar_cli._go_command()
                self.assertEqual(command, [str(temp_path)])
            finally:
                try:
                    temp_path.unlink()
                except FileNotFoundError:
                    pass
                try:
                    temp_path.parent.rmdir()
                except OSError:
                    pass

        def test_packaged_cli_assets_present(self) -> None:
            tarball = _packaged_cli_tarball()
            manifest = _packaged_cli_manifest(tarball)

            missing = [str(path) for path in (tarball, manifest) if not path.exists()]
            if missing:
                self.fail(
                    "Packaged CLI artefacts missing; run "
                    "`python3 scripts/tools/package_bar_cli.py --print-paths` to rebuild. "
                    f"Missing: {', '.join(missing)}"
                )

        def test_bootstrap_warning_mentions_rebuild_command(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            tarball = _packaged_cli_tarball()
            manifest = _packaged_cli_manifest(tarball)

            self.assertTrue(
                tarball.exists(),
                "Packaged CLI tarball missing; run `python3 scripts/tools/package_bar_cli.py --print-paths`.",
            )
            self.assertTrue(
                manifest.exists(),
                "Packaged CLI manifest missing; run `python3 scripts/tools/package_bar_cli.py --print-paths`.",
            )

            backup = manifest.read_bytes()
            delegation_state_path = Path("var/cli-telemetry/delegation-state.json")
            disabled_state = None
            restored_state = None
            try:
                manifest.unlink()
            except FileNotFoundError:
                pass
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)
            calls_before = list(actions.user.calls)

            delegation_enabled_after_warning = True
            disable_events = []
            restored_enabled = None
            try:
                buf = io.StringIO()
                with mock.patch(
                    "scripts.tools.install_bar_cli._invoke_package_cli",
                    side_effect=RuntimeError("auto-packaging unavailable"),
                ):
                    with self.assertRaises(install_bar_cli.ReleaseSignatureError):
                        with redirect_stderr(buf):
                            bootstrap()
                warning_output = buf.getvalue()
                telemetry_messages = get_bootstrap_warning_messages(clear=False)
                adapter_messages = actions.user.cli_bootstrap_warning_messages()
                warnings = get_bootstrap_warnings(clear=True)
                disable_events = cliDelegation.disable_events()
                delegation_enabled_after_warning = cliDelegation.delegation_enabled()
                if delegation_state_path.exists():
                    disabled_state = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
            finally:
                manifest.write_bytes(backup)
                bootstrap()
                restored_enabled = cliDelegation.delegation_enabled()
                if delegation_state_path.exists():
                    restored_state = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
                clear_bootstrap_warning_events()
                cliDelegation.reset_state()

            new_calls = actions.user.calls[len(calls_before) :]
            # reset added calls to keep other tests isolated
            del actions.user.calls[len(calls_before) :]
            self.assertIn(
                "`python3 scripts/tools/package_bar_cli.py --print-paths`",
                warning_output,
                "Bootstrap warning must direct operators to rebuild packaged CLI",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in warning
                    for warning in warnings
                ),
                "Bootstrap warnings list should include rebuild instructions",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in message
                    for message in telemetry_messages
                ),
                "Bootstrap telemetry should capture rebuild instructions for adapters",
            )
            self.assertTrue(
                any(
                    "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in message
                    for message in adapter_messages
                ),
                "Talon adapters should read bootstrap telemetry via actions.user",
            )
            self.assertIsNotNone(
                disabled_state,
                "Delegation state file should exist when bootstrap disables CLI",
            )
            if disabled_state is not None:
                self.assertFalse(
                    disabled_state.get("enabled", True),
                    "Delegation state should mark CLI as disabled",
                )
                self.assertIn(
                    "package_bar_cli.py",
                    disabled_state.get("reason", ""),
                    "Delegation state should record rebuild instruction reason",
                )
            self.assertFalse(
                delegation_enabled_after_warning,
                "Bootstrap warnings should disable CLI delegation",
            )
            self.assertTrue(
                any(
                    "package_bar_cli.py" in event.get("reason", "")
                    for event in disable_events
                ),
                "CLI delegation disable events should include rebuild instruction reason",
            )
            self.assertIsNotNone(
                restored_state,
                "Delegation state file should exist after bootstrap reinstalls CLI",
            )
            if restored_state is not None:
                self.assertTrue(
                    restored_state.get("enabled", False),
                    "Delegation state should mark CLI as enabled after reinstall",
                )
            self.assertTrue(
                restored_enabled,
                "Successful bootstrap should re-enable CLI delegation",
            )
            self.assertTrue(
                any(
                    call[0] == "notify"
                    and call[1]
                    and "`python3 scripts/tools/package_bar_cli.py --print-paths`"
                    in call[1][0]
                    for call in new_calls
                ),
                "Bootstrap warning should notify adapters with rebuild instructions",
            )

            delegation_state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

        def test_provider_status_log_records_history(self) -> None:
            providerStatusLog.ProviderStatusLog.showing = False
            providerStatusLog.ProviderStatusLog.title = ""
            providerStatusLog.ProviderStatusLog.lines = []
            providerStatusLog.ProviderStatusLog.last_message = ""
            providerStatusLog.ProviderStatusLog.history = []

            buffer = io.StringIO()
            with redirect_stdout(buffer):
                providerStatusLog.log_provider_status(
                    "Providers",
                    [
                        "GPT: CLI delegation ready; telemetry and health probes are green.",
                        "OpenAI — ready via env",
                    ],
                )

            output = buffer.getvalue().strip()
            self.assertIn("[Providers]", output)
            self.assertIn(
                "• GPT: CLI delegation ready; telemetry and health probes are green.",
                output,
            )
            self.assertEqual(providerStatusLog.ProviderStatusLog.title, "Providers")
            self.assertEqual(
                providerStatusLog.ProviderStatusLog.lines,
                [
                    "GPT: CLI delegation ready; telemetry and health probes are green.",
                    "OpenAI — ready via env",
                ],
            )
            self.assertTrue(providerStatusLog.ProviderStatusLog.showing)
            self.assertEqual(
                providerStatusLog.ProviderStatusLog.last_message.strip(), output
            )
            self.assertIn(output, providerStatusLog.ProviderStatusLog.history)

            providerStatusLog.clear_provider_status()
            self.assertFalse(providerStatusLog.ProviderStatusLog.showing)
            self.assertEqual(providerStatusLog.ProviderStatusLog.title, "")
            self.assertEqual(providerStatusLog.ProviderStatusLog.lines, [])
            self.assertEqual(providerStatusLog.ProviderStatusLog.last_message, "")

        def test_bootstrap_hydrates_release_snapshot_metadata(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            snapshot_path = PACKAGED_CLI_DIR / "delegation-state.json"
            digest_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256"
            signature_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256.sig"
            metadata_path = PACKAGED_CLI_DIR / "signatures.json"
            runtime_path = Path("var/cli-telemetry/delegation-state.json")

            self.assertTrue(
                snapshot_path.exists(),
                "Delegation snapshot missing; run loop-0032 to rebuild",
            )
            self.assertTrue(
                digest_path.exists(),
                "Delegation snapshot digest missing; run loop-0032 to rebuild",
            )

            snapshot_backup = snapshot_path.read_bytes()
            digest_backup = digest_path.read_bytes()
            if signature_path.exists():
                signature_backup = signature_path.read_bytes()
            else:
                recorded_existing = digest_path.read_text(encoding="utf-8").strip()
                signature_path.write_text(
                    f"{_signature_for(recorded_existing)}\n", encoding="utf-8"
                )
                signature_backup = None
            if metadata_path.exists():
                metadata_backup = metadata_path.read_bytes()
            else:
                metadata_backup = None
            runtime_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)

            snapshot_payload = {
                "enabled": True,
                "updated_at": "2026-01-03T00:00:00Z",
                "reason": None,
                "source": "bootstrap",
                "events": [],
                "failure_count": 0,
                "failure_threshold": 3,
                "snapshot_version": "loop-0033-test",
            }
            digest = _canonical_snapshot_digest(snapshot_payload)
            snapshot_path.write_text(
                json.dumps(snapshot_payload, indent=2), encoding="utf-8"
            )
            digest_path.write_text(
                f"{digest}  {snapshot_path.name}\n", encoding="utf-8"
            )
            recorded = f"{digest}  {snapshot_path.name}"
            signature = _signature_for(recorded)
            signature_path.write_text(f"{signature}\n", encoding="utf-8")

            tarball = _packaged_cli_tarball()
            manifest_path = _packaged_cli_manifest(tarball)
            manifest_recorded = manifest_path.read_text(encoding="utf-8").strip()
            manifest_signature_path = manifest_path.with_suffix(
                manifest_path.suffix + ".sig"
            )
            manifest_signature = manifest_signature_path.read_text(
                encoding="utf-8"
            ).strip()
            metadata = {
                "signing_key_id": os.environ.get(
                    "CLI_RELEASE_SIGNING_KEY_ID",
                    "local-dev",
                ),
                "tarball_manifest": {
                    "recorded": manifest_recorded,
                    "signature": manifest_signature,
                },
                "delegation_snapshot": {
                    "recorded": recorded,
                    "signature": signature,
                },
                "cli_recovery_snapshot": {
                    "enabled": snapshot_payload.get("enabled", True),
                    "prompt": historyLifecycle.drop_reason_message("cli_ready"),  # type: ignore[arg-type]
                },
            }
            metadata_path.write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            telemetry_path = self._signature_telemetry_path()
            telemetry_backup = (
                telemetry_path.read_bytes() if telemetry_path.exists() else None
            )
            self._write_signature_telemetry()

            try:
                bootstrap()
                self.assertTrue(
                    runtime_path.exists(),
                    "Bootstrap should hydrate runtime delegation snapshot",
                )
                hydrated = json.loads(runtime_path.read_text(encoding="utf-8"))
                self.assertEqual(
                    hydrated.get("snapshot_version"),
                    snapshot_payload["snapshot_version"],
                    "Hydrated state should preserve release snapshot metadata",
                )
                self.assertEqual(
                    hydrated.get("source"),
                    snapshot_payload["source"],
                    "Hydrated state should preserve snapshot source",
                )
                self.assertTrue(
                    hydrated.get("enabled", False),
                    "Hydrated state should mark delegation enabled",
                )
                self.assertEqual(
                    digest,
                    _canonical_snapshot_digest(hydrated),
                    "Hydrated state digest must match release snapshot digest",
                )
            finally:
                snapshot_path.write_bytes(snapshot_backup)
                digest_path.write_bytes(digest_backup)
                if signature_backup is None:
                    signature_path.unlink(missing_ok=True)
                else:
                    signature_path.write_bytes(signature_backup)
                if metadata_backup is None:
                    metadata_path.unlink(missing_ok=True)
                else:
                    metadata_path.write_bytes(metadata_backup)
                if telemetry_backup is None:
                    telemetry_path.unlink(missing_ok=True)
                else:
                    telemetry_path.write_bytes(telemetry_backup)
                runtime_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)

        def test_bootstrap_disables_delegation_on_signature_telemetry_mismatch(
            self,
        ) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            telemetry_path = self._signature_telemetry_path()
            telemetry_backup = (
                telemetry_path.read_bytes() if telemetry_path.exists() else None
            )

            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)
            get_bootstrap_warning_messages(clear=True)
            cliDelegation.reset_state()
            actions.user.calls.clear()

            self._write_signature_telemetry(signing_key_id="unexpected-key")

            try:
                with mock.patch(
                    "scripts.tools.install_bar_cli._write_signature_telemetry",
                    return_value=None,
                ):
                    bootstrap()
                self.assertFalse(
                    cliDelegation.delegation_enabled(),
                    "Bootstrap should disable delegation when signing telemetry mismatches",
                )

                allowed, reason = requestGating.try_begin_request(
                    source="signature-telemetry-test"
                )
                self.assertFalse(allowed)
                self.assertEqual(reason, "cli_signature_mismatch")
                drop_message = historyLifecycle.last_drop_reason()
                self.assertIn("signature telemetry mismatch", drop_message)
                export_path = os.environ.get(
                    "CLI_SIGNATURE_TELEMETRY_EXPORT",
                    "artifacts/cli/signature-telemetry.json",
                )
                if export_path:
                    self.assertIn(export_path, drop_message)

                registry = providerRegistry.ProviderRegistry()
                entries = registry.status_entries()
                self.assertTrue(
                    any(
                        entry.get("delegation", {}).get("reason")
                        == "cli_signature_mismatch"
                        and "signature telemetry mismatch"
                        in (entry.get("delegation", {}).get("message") or "")
                        for entry in entries
                    ),
                    "Provider registry should surface signature telemetry mismatch",
                )
                if export_path:
                    self.assertTrue(
                        any(
                            export_path
                            in (entry.get("delegation", {}).get("message") or "")
                            for entry in entries
                        ),
                        "Provider registry message should mention telemetry export path",
                    )

                warnings = get_bootstrap_warning_messages(clear=False)
                self.assertTrue(
                    any(
                        "signature telemetry mismatch" in warning
                        for warning in warnings
                    ),
                    "Bootstrap warnings should mention signature telemetry mismatch",
                )
                if export_path:
                    self.assertTrue(
                        any(export_path in warning for warning in warnings),
                        "Bootstrap warnings should mention telemetry export path",
                    )
                delegation_state_path = Path("var/cli-telemetry/delegation-state.json")
                if delegation_state_path.exists():
                    state_payload = json.loads(
                        delegation_state_path.read_text(encoding="utf-8")
                    )
                    self.assertFalse(state_payload.get("enabled", True))
            finally:
                if telemetry_backup is None:
                    telemetry_path.unlink(missing_ok=True)
                else:
                    telemetry_path.write_bytes(telemetry_backup)
                cliDelegation.reset_state()
                historyLifecycle.clear_drop_reason()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                get_bootstrap_warning_messages(clear=True)
                actions.user.calls.clear()

        def test_cli_delegation_ready_surfaces_recovery_prompt(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            actions.user.calls.clear()
            historyLifecycle.set_drop_reason(
                "cli_signature_mismatch",
                historyLifecycle.drop_reason_message("cli_signature_mismatch"),  # type: ignore[arg-type]
            )

            cliDelegation.disable_delegation(
                "signature telemetry mismatch detected during bootstrap",
                source="bootstrap",
                notify=False,
            )

            registry = providerRegistry.ProviderRegistry()
            entries = registry.status_entries()
            self.assertTrue(
                any(
                    entry.get("delegation", {}).get("reason")
                    == "cli_signature_mismatch"
                    for entry in entries
                ),
                "Provider registry should surface signature mismatch before recovery",
            )

            with mock.patch("lib.providerCommands.log_provider_status") as show_canvas:
                cliDelegation.mark_cli_ready(source="parity")
                show_canvas.assert_called_once()
                canvas_args = show_canvas.call_args[0]
                self.assertGreaterEqual(len(canvas_args), 2)
                self.assertIn("Delegation ready", canvas_args[1])

            self.assertTrue(cliDelegation.delegation_enabled())
            reason_code = historyLifecycle.last_drop_reason_code() or "cli_ready"
            self.assertIn(
                reason_code,
                {"cli_ready", "cli_signature_recovered"},
                "Recovered delegation should tag drop reason as cli_ready",
            )

            ready_calls = [
                c for c in actions.user.calls if c[0] == "cli_delegation_ready"
            ]
            self.assertTrue(
                ready_calls,
                "Expected cli_delegation_ready action to be recorded on recovery",
            )
            self.assertEqual(ready_calls[-1][1], ("parity",))

            entries = providerRegistry.ProviderRegistry().status_entries()
            self.assertTrue(
                any(
                    entry.get("delegation", {}).get("reason")
                    == "cli_signature_recovered"
                    for entry in entries
                ),
                "Provider registry should surface signature telemetry recovery",
            )
            recovered_messages = [
                entry.get("delegation", {}).get("message", "")
                for entry in entries
                if entry.get("delegation", {}).get("reason")
                == "cli_signature_recovered"
            ]
            self.assertTrue(
                any(
                    "CLI delegation restored" in message
                    for message in recovered_messages
                ),
                "Recovery message should mention restored delegation",
            )

            actions.user.calls.clear()
            historyLifecycle.set_drop_reason("")
            cliDelegation.reset_state()
            state_path.unlink(missing_ok=True)

        def test_bootstrap_fails_on_snapshot_digest_mismatch(self) -> None:
            self.assertIsNotNone(bootstrap, "bootstrap helper unavailable")
            assert bootstrap is not None

            snapshot_path = PACKAGED_CLI_DIR / "delegation-state.json"
            digest_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256"
            signature_path = PACKAGED_CLI_DIR / "delegation-state.json.sha256.sig"
            runtime_path = Path("var/cli-telemetry/delegation-state.json")

            self.assertTrue(
                snapshot_path.exists(),
                "Delegation snapshot missing; run loop-0032 to rebuild",
            )
            self.assertTrue(
                digest_path.exists(),
                "Delegation snapshot digest missing; run loop-0032 to rebuild",
            )

            snapshot_backup = snapshot_path.read_bytes()
            digest_backup = digest_path.read_bytes()
            runtime_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            clear_bootstrap_warning_events()
            get_bootstrap_warnings(clear=True)

            bad_digest = "0" * 64
            digest_path.write_text(
                f"{bad_digest}  {snapshot_path.name}\n", encoding="utf-8"
            )

            try:
                with self.assertRaises(install_bar_cli.ReleaseSignatureError):
                    bootstrap()
                warnings = get_bootstrap_warnings(clear=True)
                self.assertTrue(
                    any(
                        "release signature validation failed" in warning
                        for warning in warnings
                    ),
                    "Bootstrap warning should surface signature validation failure",
                )
            finally:
                snapshot_path.write_bytes(snapshot_backup)
                digest_path.write_bytes(digest_backup)
                runtime_path.unlink(missing_ok=True)
                cliDelegation.reset_state()
                clear_bootstrap_warning_events()
                get_bootstrap_warnings(clear=True)
                bootstrap()

        def test_cli_health_probe_trips_delegation_after_failures(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

            failure_result = subprocess.CompletedProcess(
                args=[str(CLI_BINARY), "--health"],
                returncode=1,
                stdout="",
                stderr="probe failed",
            )
            success_result = subprocess.CompletedProcess(
                args=[str(CLI_BINARY), "--health"],
                returncode=0,
                stdout=json.dumps({"status": "ok", "version": "test"}),
                stderr="",
            )

            with mock.patch(
                "lib.cliHealth._run_health_command",
                side_effect=[failure_result, failure_result, failure_result],
            ):
                for _ in range(3):
                    cliHealth.probe_cli_health()

            self.assertFalse(
                cliDelegation.delegation_enabled(),
                "Delegation should disable after repeated health failures",
            )
            self.assertTrue(state_path.exists(), "Delegation state file missing")
            disabled_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(disabled_state.get("failure_count"), 3)
            self.assertFalse(disabled_state.get("enabled", True))
            self.assertIn("failure threshold", disabled_state.get("reason", ""))

            cliDelegation.reset_state()
            with mock.patch(
                "lib.cliHealth._run_health_command", return_value=success_result
            ):
                cliHealth.probe_cli_health()

            restored_state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertTrue(restored_state.get("enabled", False))
            self.assertEqual(restored_state.get("failure_count"), 0)

            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()

        def test_request_gating_blocks_when_cli_unhealthy(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            actions.user.calls.clear()

            for _ in range(3):
                cliDelegation.record_health_failure(
                    "probe failed", source="health_probe"
                )

            with mock.patch(
                "lib.cliHealth.probe_cli_health", return_value=False
            ) as probe:
                allowed, reason = requestGating.try_begin_request(source="parity")

            self.assertFalse(allowed)
            self.assertEqual(reason, "cli_unhealthy")
            probe.assert_called_once()

            message = historyLifecycle.last_drop_reason()
            self.assertIn("CLI delegation disabled", message)
            self.assertIn("failed probes", message)

            actions.user.calls.clear()
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            state_path.unlink(missing_ok=True)

        def test_surface_guard_notifies_cli_failure_details(self) -> None:
            state_path = Path("var/cli-telemetry/delegation-state.json")
            state_path.unlink(missing_ok=True)
            cliDelegation.reset_state()
            historyLifecycle.set_drop_reason("")
            actions.user.calls.clear()

            failure_threshold = cliDelegation.failure_threshold()
            for _ in range(failure_threshold):
                cliDelegation.record_health_failure(
                    "probe failed", source="health_probe"
                )

            failure_count = cliDelegation.failure_count()
            expected_probe_fragment = (
                f"failed probes={failure_count}/{failure_threshold}"
                if failure_threshold
                else f"failed probes={failure_count}"
            )

            with mock.patch("lib.cliHealth.probe_cli_health", return_value=False):
                with mock.patch("lib.surfaceGuidance.notify") as notify:
                    blocked = surfaceGuidance.guard_surface_request(
                        surface="provider_commands",
                        source="parity-cli-failure",
                    )

            self.assertTrue(blocked)
            notify.assert_called()
            message = notify.call_args[0][0]
            self.assertIn("CLI delegation disabled", message)
            self.assertIn(expected_probe_fragment, message)
            self.assertIn("probe failed", message)

            historyLifecycle.set_drop_reason("")
            cliDelegation.reset_state()
            state_path.unlink(missing_ok=True)

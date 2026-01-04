"""Manage CLI delegation state for Talon adapters."""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from talon import Module, actions

from . import historyLifecycle
from . import responseCanvasFallback

mod = Module()

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_CLI_BINARY = _REPO_ROOT / "bin" / "bar"
_DELEGATION_ENABLED: bool = True
_DISABLE_EVENTS: List[Dict[str, str]] = []
_TELEMETRY_DIR = _REPO_ROOT / "var" / "cli-telemetry"
_STATE_PATH = _TELEMETRY_DIR / "delegation-state.json"
_CHECK_CLI_ASSETS = _REPO_ROOT / "scripts" / "tools" / "check_cli_assets.py"
_AUTO_REPACKAGE_ATTEMPTED = False
_AUTO_INSTALL_ATTEMPTED = False
_FAILURE_THRESHOLD = 3
_FAILURE_COUNT = 0
_LAST_REASON: str | None = None

_LAST_RECOVERY_CODE: str | None = None
_LAST_RECOVERY_DETAILS: str | None = None

_DEFAULT_DIRECTIONAL_TOKEN = "jog"
_DEFAULT_PROVIDER_ID = "cli"
_RESPONSE_RECIPE = "cli_delegate"


def _auto_refresh_signature_telemetry() -> None:
    global _AUTO_REPACKAGE_ATTEMPTED
    if _AUTO_REPACKAGE_ATTEMPTED:
        return
    if not _CHECK_CLI_ASSETS.exists():
        return
    env = os.environ.copy()
    if "CLI_GO_COMMAND" not in env:
        go_path = shutil.which("go")
        if go_path:
            env["CLI_GO_COMMAND"] = go_path
    try:
        subprocess.run(
            [
                sys.executable or "python3",
                str(_CHECK_CLI_ASSETS),
                "--repackage-on-recovery-drift",
            ],
            check=True,
            cwd=_REPO_ROOT,
            env=env,
        )
    except Exception:
        return
    _AUTO_REPACKAGE_ATTEMPTED = True


def _auto_install_cli() -> None:
    global _AUTO_INSTALL_ATTEMPTED
    if _AUTO_INSTALL_ATTEMPTED:
        return
    try:
        from scripts.tools import install_bar_cli as _install_bar_cli  # type: ignore
    except Exception:
        return
    try:
        _install_bar_cli.install_cli(quiet=True)
    except Exception:
        return
    _AUTO_INSTALL_ATTEMPTED = True


def _recovery_code_for(reason: str | None) -> str | None:
    text = (reason or "").strip().lower()
    if not text:
        return None
    if "signature telemetry mismatch" in text:
        return "cli_signature_recovered"
    return "cli_recovered"


def recovery_prompt() -> str:
    code = _LAST_RECOVERY_CODE or "cli_ready"
    message = ""
    try:
        from .requestLog import drop_reason_message as _drop_reason_message
    except Exception:
        _drop_reason_message = None
    if _drop_reason_message is not None:
        try:
            message = _drop_reason_message(code)  # type: ignore[arg-type]
        except Exception:
            message = ""
    if not isinstance(message, str) or not message.strip():
        message = "CLI delegation ready."
    details = (_LAST_RECOVERY_DETAILS or "").strip()
    if details and code in {"cli_recovered", "cli_signature_recovered"}:
        message = f"{message} (previous: {details})"
    return message


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> None:
    global \
        _DELEGATION_ENABLED, \
        _DISABLE_EVENTS, \
        _FAILURE_COUNT, \
        _LAST_REASON, \
        _LAST_RECOVERY_CODE, \
        _LAST_RECOVERY_DETAILS
    if not _STATE_PATH.exists():
        return
    try:
        payload = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    _DELEGATION_ENABLED = bool(payload.get("enabled", True))
    _DISABLE_EVENTS = list(payload.get("events", []))
    _FAILURE_COUNT = int(payload.get("failure_count", 0))
    reason = payload.get("reason")
    _LAST_REASON = (
        reason.strip() if isinstance(reason, str) and reason.strip() else None
    )
    recovery_code = payload.get("recovery_code")
    _LAST_RECOVERY_CODE = (
        recovery_code.strip()
        if isinstance(recovery_code, str) and recovery_code.strip()
        else None
    )
    recovery_details = payload.get("recovery_details")
    _LAST_RECOVERY_DETAILS = (
        recovery_details.strip()
        if isinstance(recovery_details, str) and recovery_details.strip()
        else None
    )


_load_state()


def _persist_state(
    *,
    enabled: bool,
    reason: str | None,
    source: str | None,
    extra: Dict[str, Any] | None = None,
) -> None:
    try:
        _TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
        existing: Dict[str, Any] = {}
        try:
            current = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
        except Exception:
            current = {}
        if isinstance(current, dict):
            existing = dict(current)
        payload: Dict[str, Any] = dict(existing)
        payload.update(
            {
                "enabled": enabled,
                "updated_at": _timestamp(),
                "reason": reason,
                "source": source,
                "events": list(_DISABLE_EVENTS),
                "failure_count": _FAILURE_COUNT,
                "failure_threshold": _FAILURE_THRESHOLD,
            }
        )
        if _LAST_RECOVERY_CODE is not None:
            payload["recovery_code"] = _LAST_RECOVERY_CODE
        else:
            payload.pop("recovery_code", None)
        if _LAST_RECOVERY_DETAILS is not None:
            payload["recovery_details"] = _LAST_RECOVERY_DETAILS
        else:
            payload.pop("recovery_details", None)
        if extra:
            for key, value in extra.items():
                if key in {
                    "enabled",
                    "updated_at",
                    "reason",
                    "source",
                    "events",
                    "failure_count",
                    "failure_threshold",
                    "recovery_code",
                    "recovery_details",
                }:
                    continue
                payload[key] = value
        _STATE_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    except Exception:
        # Persisting state is best-effort; telemetry continues in memory when this fails.
        pass


def _coerce_axes_payload(raw_axes: Any) -> Dict[str, List[str]]:
    axes: Dict[str, List[str]] = {}
    if not isinstance(raw_axes, dict):
        return axes
    for raw_key, raw_value in raw_axes.items():
        key = str(raw_key).strip()
        if not key:
            continue
        values: list[str] = []
        if isinstance(raw_value, (list, tuple, set)):
            for item in raw_value:
                text = str(item).strip()
                if text:
                    values.append(text)
        elif raw_value is not None:
            text = str(raw_value).strip()
            if text:
                values.append(text)
        if values:
            axes[key] = values
    return axes


def _fallback_request_id() -> str:
    stamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    return f"cli-{stamp}"


def _response_text(response: Dict[str, Any]) -> str:
    message = ""
    raw_message = response.get("message")
    if isinstance(raw_message, str):
        message = raw_message.strip()
    result_text = ""
    result = response.get("result")
    if isinstance(result, dict):
        parts: list[str] = []
        for key, value in result.items():
            text = ""
            if isinstance(value, str):
                text = value.strip()
            elif value is not None:
                try:
                    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
                except Exception:
                    text = str(value)
            if text:
                parts.append(f"{key}: {text}")
        result_text = "\n".join(parts).strip()
    if message and result_text:
        return f"{message}\n\n{result_text}"
    return message or result_text or ""


def _prompt_text(payload: Dict[str, Any]) -> str:
    prompt_payload = payload.get("prompt")
    if isinstance(prompt_payload, dict):
        text = prompt_payload.get("text")
        if isinstance(text, str):
            return text.strip()
        segments = prompt_payload.get("segments")
        if isinstance(segments, (list, tuple)):
            parts = [str(part).strip() for part in segments if str(part).strip()]
            if parts:
                return "\n".join(parts)
    return ""


def _normalise_directional_axis(
    axes: Dict[str, List[str]], payload: Dict[str, Any]
) -> Dict[str, List[str]]:
    directional = [
        token.strip()
        for token in axes.get("directional", [])
        if isinstance(token, str) and token.strip()
    ]
    if directional:
        axes["directional"] = directional
        return axes
    raw_directional = payload.get("directional")
    candidate = ""
    if isinstance(raw_directional, str):
        candidate = raw_directional.strip()
    elif isinstance(raw_directional, (list, tuple)):
        for item in raw_directional:
            if isinstance(item, str) and item.strip():
                candidate = item.strip()
                break
    if candidate:
        axes["directional"] = [candidate]
    else:
        axes["directional"] = [_DEFAULT_DIRECTIONAL_TOKEN]
    return axes


def _record_successful_delegation(
    payload: Dict[str, Any], response: Dict[str, Any]
) -> None:
    try:
        request_id_raw = response.get("request_id") or payload.get("request_id")
        request_id = str(request_id_raw or "").strip()
        if not request_id:
            request_id = _fallback_request_id()
        prompt_text = _prompt_text(payload)
        response_text = _response_text(response)
        axes = _normalise_directional_axis(
            _coerce_axes_payload(payload.get("axes")),
            payload,
        )
        provider_raw = payload.get("provider_id")
        provider_id = (
            str(provider_raw or _DEFAULT_PROVIDER_ID).strip() or _DEFAULT_PROVIDER_ID
        )
        recipe_raw = payload.get("recipe")
        recipe = str(recipe_raw or _RESPONSE_RECIPE).strip() or _RESPONSE_RECIPE

        started_at_ms_val = payload.get("started_at_ms")
        duration_ms_val = payload.get("duration_ms")
        started_at_ms = (
            int(started_at_ms_val)
            if isinstance(started_at_ms_val, (int, float))
            else None
        )
        duration_ms = (
            int(duration_ms_val) if isinstance(duration_ms_val, (int, float)) else None
        )

        historyLifecycle.append_entry(
            request_id,
            prompt_text,
            response_text,
            "",
            recipe=recipe,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
            axes=axes,
            provider_id=provider_id,
        )
        if response_text:
            responseCanvasFallback.set_response_fallback(request_id, response_text)
        else:
            responseCanvasFallback.clear_response_fallback(request_id)
        try:
            actions.user.model_response_canvas_open()
        except Exception:
            pass
        try:
            actions.user.model_response_canvas_refresh()
        except Exception:
            pass
    except Exception:
        pass


def apply_release_snapshot(snapshot: Dict[str, Any]) -> None:
    """Hydrate delegation state from a packaged release snapshot."""

    global \
        _DELEGATION_ENABLED, \
        _DISABLE_EVENTS, \
        _FAILURE_COUNT, \
        _FAILURE_THRESHOLD, \
        _LAST_REASON, \
        _LAST_RECOVERY_CODE, \
        _LAST_RECOVERY_DETAILS

    enabled = bool(snapshot.get("enabled", True))
    failure_count_raw = snapshot.get("failure_count", 0)
    try:
        failure_count = int(failure_count_raw)
    except Exception:
        failure_count = 0
    failure_count = max(0, failure_count)

    failure_threshold_raw = snapshot.get("failure_threshold", _FAILURE_THRESHOLD)
    try:
        failure_threshold = int(failure_threshold_raw)
    except Exception:
        failure_threshold = _FAILURE_THRESHOLD
    if failure_threshold <= 0:
        failure_threshold = _FAILURE_THRESHOLD

    events_raw = snapshot.get("events", [])
    events: List[Dict[str, str]] = []
    if isinstance(events_raw, list):
        for entry in events_raw:
            if isinstance(entry, dict):
                events.append(
                    {
                        "reason": str(entry.get("reason", "")),
                        "source": str(entry.get("source", "")),
                        "timestamp": str(entry.get("timestamp", "")),
                    }
                )

    reason = snapshot.get("reason")
    source = snapshot.get("source") or "snapshot"

    _DELEGATION_ENABLED = enabled
    _FAILURE_COUNT = failure_count
    _FAILURE_THRESHOLD = failure_threshold
    _DISABLE_EVENTS = events
    _LAST_REASON = reason if isinstance(reason, str) and str(reason).strip() else None
    recovery_code = snapshot.get("recovery_code")
    _LAST_RECOVERY_CODE = (
        recovery_code.strip()
        if isinstance(recovery_code, str) and recovery_code.strip()
        else None
    )
    recovery_details = snapshot.get("recovery_details")
    _LAST_RECOVERY_DETAILS = (
        recovery_details.strip()
        if isinstance(recovery_details, str) and recovery_details.strip()
        else None
    )

    extra_fields: Dict[str, Any] = dict(snapshot)
    for key in (
        "enabled",
        "updated_at",
        "reason",
        "source",
        "events",
        "failure_count",
        "failure_threshold",
        "recovery_code",
        "recovery_details",
    ):
        extra_fields.pop(key, None)

    _persist_state(
        enabled=enabled,
        reason=_LAST_REASON,
        source=str(source),
        extra=extra_fields,
    )


def _record_disable_event(reason: str, source: str) -> None:
    if _DISABLE_EVENTS and _DISABLE_EVENTS[-1].get("reason") == reason:
        _DISABLE_EVENTS[-1] = {
            "reason": reason,
            "source": source,
            "timestamp": _timestamp(),
        }
    else:
        _DISABLE_EVENTS.append(
            {
                "reason": reason,
                "source": source,
                "timestamp": _timestamp(),
            }
        )


def disable_delegation(
    reason: str, *, source: str = "bootstrap", notify: bool = True
) -> None:
    """Disable CLI delegation and record the triggering reason."""

    global \
        _DELEGATION_ENABLED, \
        _LAST_REASON, \
        _LAST_RECOVERY_CODE, \
        _LAST_RECOVERY_DETAILS
    _DELEGATION_ENABLED = False
    _LAST_REASON = reason
    _LAST_RECOVERY_CODE = None
    _LAST_RECOVERY_DETAILS = None
    _record_disable_event(reason, source)
    if notify:
        try:
            actions.user.notify(f"CLI delegation disabled: {reason}")
        except Exception:
            pass
        try:
            handler = getattr(actions.user, "cli_delegation_disabled", None)
            if handler is not None:
                handler(reason, source)
        except Exception:
            pass
    _persist_state(enabled=False, reason=reason, source=source)


def mark_cli_ready(*, source: str = "bootstrap") -> None:
    """Mark CLI delegation as healthy and ready after bootstrap succeeds."""

    global \
        _DELEGATION_ENABLED, \
        _FAILURE_COUNT, \
        _LAST_REASON, \
        _LAST_RECOVERY_CODE, \
        _LAST_RECOVERY_DETAILS, \
        _AUTO_REPACKAGE_ATTEMPTED, \
        _AUTO_INSTALL_ATTEMPTED
    previous_reason = _LAST_REASON if isinstance(_LAST_REASON, str) else ""
    _AUTO_REPACKAGE_ATTEMPTED = False
    _AUTO_INSTALL_ATTEMPTED = False
    _DELEGATION_ENABLED = True
    _FAILURE_COUNT = 0
    _LAST_RECOVERY_CODE = _recovery_code_for(previous_reason)
    _LAST_RECOVERY_DETAILS = previous_reason.strip() or None

    prompt = recovery_prompt()

    handler_called = False
    handler_name = ""
    try:
        handler = getattr(actions.user, "cli_delegation_ready", None)
        handler_name = getattr(handler, "__name__", "") if callable(handler) else ""
    except Exception:
        handler = None
    if handler is not None:
        try:
            handler(source)
            handler_called = True
        except Exception:
            handler_called = False
    if handler_called and handler_name == "_noop":
        handler_called = False
    if not handler_called:
        try:
            actions.user.notify(prompt)
        except Exception:
            pass

    try:
        from . import providerCommands as _providerCommands  # type: ignore

        _providerCommands.show_provider_status_message(
            "Delegation ready", prompt=prompt
        )
    except Exception:
        pass

    _LAST_REASON = None

    try:
        from .historyLifecycle import clear_drop_reason as _clear_drop_reason  # type: ignore
    except Exception:
        _clear_drop_reason = None
    if _clear_drop_reason is not None:
        try:
            _clear_drop_reason()
        except Exception:
            pass

    _persist_state(enabled=True, reason=None, source=source)


def delegation_enabled() -> bool:
    """Return True when CLI delegation is currently enabled."""

    return _DELEGATION_ENABLED


def disable_events() -> List[Dict[str, str]]:
    """Return recorded CLI delegation disable events."""

    return list(_DISABLE_EVENTS)


def failure_count() -> int:
    """Return the current consecutive failure count."""

    return _FAILURE_COUNT


def failure_threshold() -> int:
    """Return the failure threshold that disables delegation."""

    return _FAILURE_THRESHOLD


def last_disable_reason() -> str | None:
    """Return the last recorded disablement reason, if any."""

    return _LAST_REASON


def last_recovery_code() -> str | None:
    """Return the last recorded recovery code, if any."""

    return _LAST_RECOVERY_CODE


def last_recovery_details() -> str | None:
    """Return details associated with the last recovery, if any."""

    return _LAST_RECOVERY_DETAILS


def reset_state() -> None:
    """Reset delegation state and forget recorded disable events."""

    global \
        _DELEGATION_ENABLED, \
        _FAILURE_COUNT, \
        _LAST_REASON, \
        _LAST_RECOVERY_CODE, \
        _LAST_RECOVERY_DETAILS, \
        _AUTO_REPACKAGE_ATTEMPTED, \
        _AUTO_INSTALL_ATTEMPTED
    _DELEGATION_ENABLED = True
    _FAILURE_COUNT = 0
    _LAST_REASON = None
    _LAST_RECOVERY_CODE = None
    _LAST_RECOVERY_DETAILS = None
    _AUTO_REPACKAGE_ATTEMPTED = False
    _AUTO_INSTALL_ATTEMPTED = False
    _DISABLE_EVENTS.clear()
    _persist_state(enabled=True, reason=None, source="reset")


def record_health_failure(reason: str, *, source: str = "health_probe") -> None:
    """Record a failed health probe and disable delegation after threshold."""

    global _FAILURE_COUNT, _LAST_REASON

    reason_lower = reason.lower()
    probe_failure = "health probe failed" in reason_lower
    missing_cli = "missing cli" in reason_lower or "missing cli tarball" in reason_lower
    missing_binary = "no such file or directory" in reason_lower and (
        "bin/bar" in reason_lower or "bar.bin" in reason_lower
    )
    telemetry_issue = "signature telemetry" in reason_lower

    needs_repackage = False
    needs_install = False

    if probe_failure:
        needs_repackage = True
        needs_install = True
    else:
        if telemetry_issue:
            needs_repackage = True
        if missing_cli or missing_binary:
            needs_install = True
            needs_repackage = True

    if needs_repackage:
        _auto_refresh_signature_telemetry()
    if needs_install:
        _auto_install_cli()

    if _FAILURE_COUNT < _FAILURE_THRESHOLD:
        _FAILURE_COUNT += 1
    if _FAILURE_COUNT >= _FAILURE_THRESHOLD:
        _FAILURE_COUNT = _FAILURE_THRESHOLD
    _LAST_REASON = reason
    if _FAILURE_COUNT >= _FAILURE_THRESHOLD:
        same_reason = bool(
            _DISABLE_EVENTS and _DISABLE_EVENTS[-1].get("reason") == reason
        )
        already_disabled = not _DELEGATION_ENABLED
        notify = not (already_disabled and same_reason)
        disable_delegation(
            f"{reason}; reached failure threshold {_FAILURE_THRESHOLD}",
            source=source,
            notify=notify,
        )
    else:
        _persist_state(enabled=_DELEGATION_ENABLED, reason=reason, source=source)


def record_health_success(*, source: str = "health_probe") -> None:
    """Record a successful health probe and reset failure counters."""

    global _FAILURE_COUNT
    _FAILURE_COUNT = 0
    mark_cli_ready(source=source)


def invoke_cli_delegate(payload: Dict[str, Any]) -> tuple[bool, Dict[str, Any], str]:
    """Execute the CLI delegate command with the provided payload."""

    command = [str(_CLI_BINARY), "delegate"]
    try:
        result = subprocess.run(  # noqa: S603,S607 - intentional CLI invocation
            command,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        return False, {}, f"failed to execute CLI delegate: {exc}"

    if result.returncode != 0:
        message = result.stderr.strip() or (
            f"CLI delegate exited with status {result.returncode}"
        )
        return False, {}, message

    try:
        response = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        return False, {}, f"invalid CLI response JSON ({exc})"

    return True, response, ""


def delegate_request(payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any], str]:
    """Dispatch a request through the CLI, returning success flag, response, error."""

    success, response, error_message = invoke_cli_delegate(payload)
    if not success:
        disable_delegation(
            f"CLI delegate failure: {error_message}", source="cli_delegate", notify=True
        )
        return False, response, error_message

    mark_cli_ready(source="cli_delegate")
    _record_successful_delegation(payload, response)
    return True, response, ""


@mod.action_class
class CliDelegationActions:
    def cli_delegation_disable(reason: str, source: str = "runtime") -> None:
        """Disable CLI delegation for the provided reason."""

        disable_delegation(reason, source=source)

    def cli_delegation_enable() -> None:
        """Re-enable CLI delegation."""

        mark_cli_ready(source="action")

    def cli_delegation_enabled() -> bool:
        """Return True when CLI delegation is enabled."""

        return delegation_enabled()

    def cli_delegation_disable_reasons() -> List[str]:
        """Return the recorded CLI delegation disable reasons."""

        return [event["reason"] for event in _DISABLE_EVENTS]


__all__ = [
    "disable_delegation",
    "mark_cli_ready",
    "delegation_enabled",
    "disable_events",
    "failure_count",
    "failure_threshold",
    "last_disable_reason",
    "last_recovery_code",
    "last_recovery_details",
    "recovery_prompt",
    "reset_state",
    "record_health_failure",
    "record_health_success",
    "apply_release_snapshot",
    "invoke_cli_delegate",
    "delegate_request",
]

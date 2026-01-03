"""Telemetry helpers for bootstrap warnings.

This module records bootstrap warnings with basic metadata so Talon adapters
and parity harnesses can consume them as structured telemetry rather than
parsing stderr output.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

from .cliDelegation import disable_delegation

DEFAULT_SIGNATURE_METADATA_PATH = Path("artifacts/cli/signatures.json")
SIGNATURE_METADATA_ENV = "CLI_SIGNATURE_METADATA"
DEFAULT_SIGNATURE_TELEMETRY_PATH = Path("var/cli-telemetry/signature-metadata.json")
SIGNATURE_TELEMETRY_ENV = "CLI_SIGNATURE_TELEMETRY"
DEFAULT_SIGNING_KEY_ID = "local-dev"
SIGNING_KEY_ID_ENV = "CLI_RELEASE_SIGNING_KEY_ID"

_TELEMETRY_EVENTS: List[Dict[str, str]] = []


def _append_event(message: str, *, source: str = "bootstrap") -> None:
    """Record a telemetry event for a bootstrap warning."""

    event = {
        "message": message,
        "source": source,
        "severity": "warning",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _TELEMETRY_EVENTS.append(event)


def _metadata_path() -> Path:
    return Path(
        os.environ.get(
            SIGNATURE_METADATA_ENV,
            str(DEFAULT_SIGNATURE_METADATA_PATH),
        )
    )


def _telemetry_path() -> Path:
    return Path(
        os.environ.get(
            SIGNATURE_TELEMETRY_ENV,
            str(DEFAULT_SIGNATURE_TELEMETRY_PATH),
        )
    )


def record_bootstrap_warning(message: str, *, source: str = "bootstrap") -> None:
    """Record a bootstrap warning with optional source metadata."""

    _append_event(message, source=source)
    try:
        disable_delegation(message, source=source)
    except Exception:
        pass


def get_bootstrap_warning_events(*, clear: bool = False) -> List[Dict[str, str]]:
    """Return telemetry events for bootstrap warnings."""

    events = list(_TELEMETRY_EVENTS)
    if clear:
        _TELEMETRY_EVENTS.clear()
    return events


def get_bootstrap_warning_messages(*, clear: bool = False) -> List[str]:
    """Return the warning messages captured via telemetry."""

    return [event["message"] for event in get_bootstrap_warning_events(clear=clear)]


def has_bootstrap_warning_events() -> bool:
    """Return True when structured telemetry has captured any warnings."""

    return bool(_TELEMETRY_EVENTS)


def clear_bootstrap_warning_events() -> None:
    """Clear recorded telemetry events."""

    _TELEMETRY_EVENTS.clear()


def verify_signature_telemetry(*, source: str = "bootstrap") -> bool:
    """Validate release signing telemetry before enabling CLI delegation."""

    telemetry_path = _telemetry_path()
    metadata_path = _metadata_path()
    issues: list[str] = []
    telemetry: Dict[str, Any] | None = None
    metadata: Dict[str, Any] | None = None

    if telemetry_path.exists():
        try:
            loaded = json.loads(telemetry_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            issues.append(f"invalid signature telemetry: {telemetry_path} ({exc})")
        else:
            if isinstance(loaded, dict):
                telemetry = loaded
            else:
                issues.append(
                    f"invalid signature telemetry payload: {telemetry_path} (expected object)"
                )
    else:
        issues.append(f"missing signature telemetry: {telemetry_path}")

    if metadata_path.exists():
        try:
            loaded_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive
            issues.append(f"invalid signature metadata: {metadata_path} ({exc})")
        else:
            if isinstance(loaded_metadata, dict):
                metadata = loaded_metadata
            else:
                issues.append(
                    f"invalid signature metadata payload: {metadata_path} (expected object)"
                )
    else:
        issues.append(f"missing signature metadata: {metadata_path}")

    expected_key = os.environ.get(SIGNING_KEY_ID_ENV, DEFAULT_SIGNING_KEY_ID)

    if telemetry is not None:
        signing_key = telemetry.get("signing_key_id")
        if signing_key != expected_key:
            issues.append("signature telemetry signing_key_id mismatch")
        status = telemetry.get("status")
        if status != "green":
            issues.append(f"signature telemetry status {status!r}")
        telemetry_issues = telemetry.get("issues")
        if telemetry_issues:
            issues.append("signature telemetry reports issues")
    else:
        signing_key = None

    if telemetry is not None and metadata is not None:
        if metadata.get("signing_key_id") != telemetry.get("signing_key_id"):
            issues.append("signature telemetry metadata key mismatch")
        for field in ("tarball_manifest", "delegation_snapshot"):
            metadata_field = metadata.get(field)
            telemetry_field = telemetry.get(field)
            if not isinstance(metadata_field, dict):
                issues.append(f"signature metadata {field} invalid")
                continue
            if not isinstance(telemetry_field, dict):
                issues.append(f"signature telemetry {field} invalid")
                continue
            if metadata_field.get("recorded") != telemetry_field.get("recorded"):
                issues.append(f"signature telemetry {field} recorded mismatch")
            if metadata_field.get("signature") != telemetry_field.get("signature"):
                issues.append(f"signature telemetry {field} signature mismatch")
        recovery_meta = metadata.get("cli_recovery_snapshot")
        recovery_telemetry = telemetry.get("cli_recovery_snapshot")
        if not isinstance(recovery_meta, dict):
            issues.append("signature metadata recovery snapshot invalid")
        elif recovery_telemetry != recovery_meta:
            issues.append("signature telemetry recovery snapshot mismatch")

    if issues:
        unique_issues: List[str] = []
        for item in issues:
            if item not in unique_issues:
                unique_issues.append(item)
        message = (
            "signature telemetry mismatch; run `python3 scripts/tools/check_cli_assets.py` "
            "to refresh release metadata"
        )
        if unique_issues:
            message = f"{message} ({'; '.join(unique_issues)})"
        record_bootstrap_warning(message, source=source)
        return False

    return True


from talon import Module


mod = Module()


@mod.action_class
class BootstrapTelemetryActions:
    def cli_bootstrap_warning_messages() -> List[str]:
        """Return bootstrap warning messages without clearing telemetry."""

        return get_bootstrap_warning_messages(clear=False)

    def cli_bootstrap_warning_messages_clear() -> List[str]:
        """Return bootstrap warning messages and clear telemetry."""

        return get_bootstrap_warning_messages(clear=True)


try:  # Allow tests to access telemetry via stubbed actions.user
    from talon import actions as _bootstrap_actions
except Exception:  # pragma: no cover - Talon runtime without actions module
    _bootstrap_actions = None
else:

    def _record_actions_call(name: str) -> None:
        if _bootstrap_actions is None:
            return
        try:
            actions_user_local = getattr(_bootstrap_actions, "user", None)
            calls = getattr(actions_user_local, "calls", None)
            if isinstance(calls, list):
                calls.append((name, tuple(), {}))
        except Exception:
            pass

    def _actions_cli_bootstrap_warning_messages() -> List[str]:
        _record_actions_call("cli_bootstrap_warning_messages")
        return get_bootstrap_warning_messages(clear=False)

    def _actions_cli_bootstrap_warning_messages_clear() -> List[str]:
        _record_actions_call("cli_bootstrap_warning_messages_clear")
        return get_bootstrap_warning_messages(clear=True)

    actions_user = getattr(_bootstrap_actions, "user", None)
    if actions_user is not None:
        try:
            setattr(
                actions_user,
                "cli_bootstrap_warning_messages",
                _actions_cli_bootstrap_warning_messages,
            )
            setattr(
                actions_user,
                "cli_bootstrap_warning_messages_clear",
                _actions_cli_bootstrap_warning_messages_clear,
            )
        except Exception:
            pass


__all__ = [
    "record_bootstrap_warning",
    "get_bootstrap_warning_events",
    "get_bootstrap_warning_messages",
    "has_bootstrap_warning_events",
    "clear_bootstrap_warning_events",
    "verify_signature_telemetry",
]

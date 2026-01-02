import os
import subprocess
import json
from dataclasses import dataclass
from typing import Optional, cast
from pathlib import Path

from talon import Context, Module, actions, settings

from .providerCanvas import (
    ProviderCanvasState,
    hide_provider_canvas,
    show_provider_canvas,
)
from .providerRegistry import (
    AmbiguousProviderError,
    ProviderLookupError,
    provider_registry,
)
from .requestGating import request_is_in_flight
from .historyLifecycle import last_drop_reason, set_drop_reason
from .requestState import RequestDropReason

from .modelHelpers import notify
from .surfaceGuidance import guard_surface_request

try:
    print(f"[debug] providerCommands loaded from {__file__}")
except Exception:
    pass
mod = Module()
ctx = Context()


def _bar_cli_enabled() -> bool:
    try:
        return bool(settings.get("user.bar_cli_enabled", 0))
    except Exception:
        return False


_DEFAULT_DEBUG_LOG_MAX_LEN = 512


def _resolve_debug_log_limit() -> int:
    try:
        value = settings.get("user.bar_cli_debug_log_limit", _DEFAULT_DEBUG_LOG_MAX_LEN)
    except Exception:
        value = _DEFAULT_DEBUG_LOG_MAX_LEN
    try:
        parsed = int(value)
    except Exception:
        return _DEFAULT_DEBUG_LOG_MAX_LEN
    return max(64, min(parsed, 8192))


try:
    _DEBUG_LOG_MAX_LEN = _resolve_debug_log_limit()
except Exception:
    _DEBUG_LOG_MAX_LEN = _DEFAULT_DEBUG_LOG_MAX_LEN


_KNOWN_DROP_REASONS = {cast(str, value) for value in RequestDropReason.__args__}


def _truncate_debug_value(value: object, limit: int = _DEBUG_LOG_MAX_LEN) -> object:
    if not isinstance(value, str):
        return value
    if len(value) <= limit:
        return value
    suffix = "...(truncated)"
    return value[: max(0, limit - len(suffix))] + suffix


def _truncate_debug_text(
    value: str | None, limit: int = _DEBUG_LOG_MAX_LEN
) -> str | None:
    if value is None:
        return None
    truncated = _truncate_debug_value(value, limit)
    if isinstance(truncated, str):
        return truncated
    return str(truncated)


def _truncate_debug_list(
    values: list[str] | None, limit: int = _DEBUG_LOG_MAX_LEN
) -> list[str] | None:
    if not values:
        return None
    truncated: list[str] = []
    for item in values:
        truncated_item = _truncate_debug_value(item, limit)
        if isinstance(truncated_item, str):
            truncated.append(truncated_item)
        else:
            truncated.append(str(truncated_item))
    return truncated or None


def _truncation_indicator(value: object, limit: int = _DEBUG_LOG_MAX_LEN) -> str:
    if isinstance(value, str):
        if len(value) > limit:
            return f" (original length {len(value)} chars)"
        return ""
    if isinstance(value, list):
        lengths = [
            len(item) for item in value if isinstance(item, str) and len(item) > limit
        ]
        if lengths:
            return f" (truncated {len(lengths)} entries; max original length {max(lengths)} chars)"
    return ""


def _normalise_cli_drop_reason(
    raw_reason: str | None,
) -> tuple[RequestDropReason | None, str | None]:
    if not raw_reason:
        return None, None
    candidate = str(raw_reason).strip()
    if not candidate:
        return None, None
    if candidate in _KNOWN_DROP_REASONS:
        return cast(RequestDropReason, candidate), candidate
    return None, candidate


@dataclass
class BarCliPayload:
    raw: dict | None
    notice: str | None = None
    error: str | None = None
    debug: str | None = None
    drop_reason: str | None = None
    alert: str | None = None
    severity: str | None = None
    breadcrumbs: list[str] | None = None
    decode_failed: bool = False

    @property
    def has_payload(self) -> bool:
        return self.raw is not None


def _format_severity_prefix(raw_severity: str | None) -> tuple[str, str]:
    """Return a tuple of (prefix, normalized severity) for logging/notifications."""

    label = (raw_severity or "").strip()
    if not label:
        return "", ""
    normalized = label.upper()
    return f"[{normalized}] ", normalized


def _bar_cli_command() -> Path:
    """Return the absolute path to the bar CLI binary."""

    override = os.environ.get("BAR_CLI_PATH")
    if override:
        return Path(override)

    root = Path(__file__).resolve().parents[2]
    return root / "cli" / "bin" / "bar"


def _parse_bar_cli_payload(result: object) -> BarCliPayload:
    """Decode CLI stdout into a structured payload helper."""

    stdout_raw = getattr(result, "stdout", "")
    stdout = stdout_raw or ""
    payload: dict | None = None
    decode_failed = False

    if stdout:
        candidates: list[str] = []
        stripped = stdout.strip()
        if stripped:
            candidates.append(stripped)
        if "\n" in stdout:
            lines = [line.strip() for line in stdout.splitlines() if line.strip()]
            if lines:
                joined = "\n".join(lines)
                candidates.append(joined)
                for line in reversed(lines):
                    if line not in candidates:
                        candidates.append(line)
        if stripped:
            first_brace = stripped.find("{")
            if first_brace > 0:
                suffix = stripped[first_brace:]
                candidates.append(suffix)
        seen: set[str] = set()
        for candidate in candidates:
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                payload = parsed
                break
        if payload is None:
            decode_failed = True

    if isinstance(payload, dict):
        breadcrumbs_value = payload.get("breadcrumbs")
        breadcrumbs: list[str] | None = None
        if isinstance(breadcrumbs_value, list):
            filtered = [
                str(item).strip() for item in breadcrumbs_value if str(item).strip()
            ]
            breadcrumbs = filtered or None
        return BarCliPayload(
            raw=payload,
            notice=payload.get("notify") or payload.get("message"),
            error=payload.get("error") or payload.get("error_message"),
            debug=payload.get("debug") or payload.get("status"),
            drop_reason=payload.get("drop_reason"),
            alert=payload.get("alert") or payload.get("warning"),
            severity=payload.get("severity"),
            breadcrumbs=breadcrumbs,
        )
    return BarCliPayload(raw=None, decode_failed=decode_failed and bool(stdout))


def _delegate_to_bar_cli(action: str, *args, **kwargs) -> bool:
    """Temporary bar CLI delegation shim. Returns True once the CLI path handles the request."""

    if not _bar_cli_enabled():
        return False

    command_path = _bar_cli_command()
    cmd = [str(command_path), action]
    if args:
        cmd.extend(str(a) for a in args)
    if kwargs:
        for key, value in kwargs.items():
            cmd.append(f"--{key}={value}")

    try:
        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        try:
            print(
                f"[debug] bar CLI binary not found at {command_path}; fallback to legacy path"
            )
        except Exception:
            pass
        return False

    if result.returncode != 0:
        try:
            print(
                f"[debug] bar CLI returned non-zero exit code {result.returncode}; stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        except Exception:
            pass
        return False

    payload_info = _parse_bar_cli_payload(result)

    severity_prefix, severity_label = _format_severity_prefix(payload_info.severity)
    severity_lower = severity_label.lower() if severity_label else ""

    if payload_info.has_payload:
        normalised_drop_reason, raw_drop_reason = _normalise_cli_drop_reason(
            payload_info.drop_reason
        )
        if raw_drop_reason:
            drop_message_candidate = (
                payload_info.error
                or payload_info.notice
                or payload_info.alert
                or payload_info.debug
                or ""
            )
            drop_message = drop_message_candidate.strip()
            if drop_message and severity_label:
                drop_message = f"{severity_prefix}{drop_message}"
            display_message = drop_message or "none"
            drop_log = (
                _truncate_debug_text(drop_message) if drop_message else display_message
            )
            drop_log = drop_log or display_message
            drop_indicator = _truncation_indicator(drop_message) if drop_message else ""
            if normalised_drop_reason is None:
                try:
                    print(
                        f"[debug] bar CLI normalised unknown drop_reason for {action}; "
                        f"drop_reason={raw_drop_reason!r} message={drop_log!r}{drop_indicator}"
                    )
                except Exception:
                    pass
            try:
                if normalised_drop_reason is not None:
                    if drop_message:
                        set_drop_reason(normalised_drop_reason, drop_message)
                    else:
                        set_drop_reason(normalised_drop_reason)
                elif drop_message:
                    set_drop_reason(cast(RequestDropReason, ""), drop_message)
                else:
                    set_drop_reason(cast(RequestDropReason, ""))
            except Exception:
                pass

        if payload_info.error:
            message = payload_info.error
            if severity_label and severity_lower not in {"error", "critical"}:
                message = f"{severity_prefix}{message}"
            try:
                notify(message)
            except Exception:
                pass
            try:
                error_log = _truncate_debug_text(payload_info.error)
                error_indicator = _truncation_indicator(payload_info.error)
                if raw_drop_reason:
                    print(
                        f"[debug] bar CLI reported error for {action}; "
                        f"drop_reason={raw_drop_reason!r} severity={severity_label or 'none'} message={(error_log if error_log is not None else payload_info.error)!r}{error_indicator}"
                    )
                else:
                    print(
                        f"[debug] bar CLI reported error for {action}; "
                        f"severity={severity_label or 'none'} message={(error_log if error_log is not None else payload_info.error)!r}{error_indicator}"
                    )
            except Exception:
                pass

        if payload_info.notice and (
            not payload_info.error or payload_info.notice != payload_info.error
        ):
            notice_message = payload_info.notice
            if severity_label:
                notice_message = f"{severity_prefix}{notice_message}"
            try:
                notify(notice_message)
            except Exception:
                pass
            if severity_label:
                try:
                    notice_log = _truncate_debug_text(payload_info.notice)
                    notice_indicator = _truncation_indicator(payload_info.notice)
                    print(
                        f"[debug] bar CLI notice severity={severity_label!r} message={(notice_log if notice_log is not None else payload_info.notice)!r}{notice_indicator}"
                    )
                except Exception:
                    pass

        if payload_info.alert and (
            payload_info.alert != payload_info.notice
            and payload_info.alert != payload_info.error
        ):
            alert_message = payload_info.alert
            if severity_label:
                alert_message = f"{severity_prefix}{alert_message}"
            try:
                notify(alert_message)
            except Exception:
                pass
            try:
                alert_log = _truncate_debug_text(payload_info.alert)
                alert_indicator = _truncation_indicator(payload_info.alert)
                print(
                    f"[debug] bar CLI raised alert for {action}; alert={(alert_log if alert_log is not None else payload_info.alert)!r}{alert_indicator} severity={severity_label or 'none'}"
                )
            except Exception:
                pass

        if payload_info.debug:
            try:
                debug_log = _truncate_debug_text(payload_info.debug)
                debug_indicator = _truncation_indicator(payload_info.debug)
                print(
                    f"[debug] bar CLI handled action {action}; status={(debug_log if debug_log is not None else payload_info.debug)!r}{debug_indicator}"
                )
            except Exception:
                pass

        if not any(
            [
                payload_info.notice,
                payload_info.error,
                payload_info.debug,
                payload_info.alert,
            ]
        ):
            try:
                raw_dump = json.dumps(payload_info.raw, default=str)
                payload_log = _truncate_debug_text(raw_dump)
                payload_indicator = _truncation_indicator(raw_dump)
                print(
                    f"[debug] bar CLI handled action {action}; payload={(payload_log if payload_log is not None else raw_dump)!r}{payload_indicator}"
                )
            except Exception:
                pass
        elif severity_label and not payload_info.error:
            try:
                print(
                    f"[debug] bar CLI severity={severity_label!r} applied for {action}"
                )
            except Exception:
                pass

        if payload_info.breadcrumbs:
            try:
                breadcrumbs_log = _truncate_debug_list(payload_info.breadcrumbs)
                breadcrumbs_indicator = _truncation_indicator(payload_info.breadcrumbs)
                print(
                    f"[debug] bar CLI breadcrumbs for {action}; breadcrumbs={(breadcrumbs_log if breadcrumbs_log is not None else payload_info.breadcrumbs)!r}{breadcrumbs_indicator}"
                )
            except Exception:
                pass

        elif severity_label and not payload_info.error:
            try:
                print(
                    f"[debug] bar CLI severity={severity_label!r} applied for {action}"
                )
            except Exception:
                pass

    else:
        if payload_info.decode_failed and result.stdout:
            try:
                stdout_log = _truncate_debug_text(result.stdout)
                stdout_indicator = _truncation_indicator(result.stdout)
                print(
                    f"[debug] bar CLI payload decode failed for {action}; stdout={(stdout_log if stdout_log is not None else result.stdout)!r}{stdout_indicator}"
                )
            except Exception:
                pass
        else:
            try:
                stdout_log = _truncate_debug_text(result.stdout)
                stdout_indicator = _truncation_indicator(result.stdout)
                print(
                    f"[debug] bar CLI handled action {action}; stdout={(stdout_log if stdout_log is not None else result.stdout)!r}{stdout_indicator}"
                )
            except Exception:
                pass

    if result.stderr:
        try:
            stderr_log = _truncate_debug_text(result.stderr)
            stderr_indicator = _truncation_indicator(result.stderr)
            print(
                f"[debug] bar CLI stderr for {action}; stderr={(stderr_log if stderr_log is not None else result.stderr)!r}{stderr_indicator}"
            )
        except Exception:
            pass
    return True


def _render_provider_lines(
    entries: list[dict], message: Optional[str] = None
) -> list[str]:
    lines: list[str] = []
    if message:
        lines.append(message)
    for entry in entries:
        marker = "▶" if entry.get("current") else "•"
        aliases = entry.get("aliases") or []
        alias_text = f" aliases: {', '.join(aliases)}" if aliases else ""
        token_hint = entry.get("token_hint") or entry.get("api_key_env")
        token_source = entry.get("token_source")
        if entry.get("available"):
            source_label = f" via {token_source}" if token_source else ""
            status = f"ready{source_label}"
        else:
            status = f"missing token ({token_hint})"
        lines.append(
            f"{marker} {entry.get('display_name')} ({entry.get('id')}) — {status}"
        )
        model = entry.get("default_model") or ""
        if model:
            lines.append(f"   model: {model}{alias_text}")
        else:
            if alias_text:
                lines.append(f"   {alias_text.lstrip()}")
        endpoint = entry.get("endpoint") or ""
        if endpoint:
            lines.append(f"   endpoint: {endpoint}")
        features = entry.get("features") or {}
        if features:
            streaming = "on" if features.get("streaming", True) else "off"
            vision = "on" if features.get("vision", False) else "off"
            images = "on" if features.get("images", False) else "off"
            lines.append(
                f"   caps: stream {streaming} · vision {vision} · images {images}"
            )
        if "streaming_enabled" in entry:
            streaming_enabled = entry.get("streaming_enabled")
            streaming_label = "on" if streaming_enabled else "off"
            lines.append(f"   streaming (current): {streaming_label}")
        reachable = entry.get("reachable")
        reachability_error = entry.get("reachability_error") or ""
        if reachable is True:
            lines.append("   reachability: ok")
        elif reachable is False:
            suffix = f" ({reachability_error})" if reachability_error else ""
            lines.append(f"   reachability: unreachable{suffix}")
        else:
            lines.append("   reachability: not checked")
    return lines


def _render_error(message: str, suggestions: list[str]) -> list[str]:
    lines = [f"Error: {message}"]
    if suggestions:
        lines.append("Did you mean:")
        for suggestion in suggestions:
            lines.append(f"- {suggestion}")
    return lines


def _normalize_model_key(text: str) -> str:
    """Normalise model alias text for matching."""

    import re

    raw = str(text or "").lower()
    collapsed = re.sub(r"[\s\.\-]+", " ", raw).strip()
    return " ".join(collapsed.split())


def _model_aliases(provider_id: str) -> dict[str, str]:
    """Return known spoken aliases for model ids for a provider."""

    aliases: dict[str, str] = {}
    if provider_id == "gemini":
        defaults = {
            "gemini one five pro": "gemini-1.5-pro",
            "one five pro": "gemini-1.5-pro",
            "1 5 pro": "gemini-1.5-pro",
            "1.5 pro": "gemini-1.5-pro",
            "one point five pro": "gemini-1.5-pro",
            "gemini pro": "gemini-1.5-pro",
            "gemini one five flash": "gemini-1.5-flash",
            "one five flash": "gemini-1.5-flash",
            "1 5 flash": "gemini-1.5-flash",
            "1.5 flash": "gemini-1.5-flash",
            "one point five flash": "gemini-1.5-flash",
            "gemini flash": "gemini-1.5-flash",
            "flash": "gemini-1.5-flash",
            "pro": "gemini-1.5-pro",
        }
        aliases.update({_normalize_model_key(k): v for k, v in defaults.items()})
        try:
            extra = settings.get("user.model_provider_model_aliases_gemini", "") or ""
        except Exception:
            extra = ""
        for part in extra.split(","):
            if not part.strip():
                continue
            if ":" in part:
                spoken, model = part.split(":", 1)
            else:
                spoken, model = part, ""
            spoken_key = _normalize_model_key(spoken)
            model_id = model.strip()
            if spoken_key and model_id:
                aliases[spoken_key] = model_id
    if provider_id == "openai":
        defaults = {
            "four": "gpt-4",
            "g p t four": "gpt-4",
            "four o": "gpt-4o",
            "g p t four o": "gpt-4o",
            "four point one": "gpt-4.1",
            "four one": "gpt-4.1",
            "g p t four one": "gpt-4.1",
            "four point o": "gpt-4o",
            "nano": "gpt-4o-mini",
            "mini": "gpt-4o-mini",
            "four o mini": "gpt-4o-mini",
            "g p t four o mini": "gpt-4o-mini",
            "fifth": "gpt-5",
            "g p t five": "gpt-5",
        }
        aliases.update({_normalize_model_key(k): v for k, v in defaults.items()})
        try:
            extra = settings.get("user.model_provider_model_aliases_openai", "") or ""
        except Exception:
            extra = ""
        for part in extra.split(","):
            if not part.strip():
                continue
            if ":" in part:
                spoken, model = part.split(":", 1)
            else:
                spoken, model = part, ""
            spoken_key = _normalize_model_key(spoken)
            model_id = model.strip()
            if spoken_key and model_id:
                aliases[spoken_key] = model_id
    return aliases


def _resolve_model_alias(provider_id: str, model: str) -> str:
    aliases = _model_aliases(provider_id)
    key = _normalize_model_key(model)
    return aliases.get(key, model.strip())


def _set_provider_model(provider_id: str, model: str) -> None:
    """Persist a provider-specific default model."""

    if not model:
        return
    from .providerRegistry import provider_registry

    if provider_id == "openai":
        settings.set("user.openai_model", model)
        assert settings.get("user.openai_model") == model
        try:
            print(f"[debug] set openai_model -> {model}")
        except Exception:
            pass
        provider_registry().set_default_model(provider_id, model)
    elif provider_id == "gemini":
        settings.set("user.model_provider_model_gemini", model)
        provider_registry().set_default_model(provider_id, model)
    else:
        # For custom providers, apply an in-session override (non-persistent).
        provider_registry().set_default_model(provider_id, model)


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""

    try:
        return request_is_in_flight()
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a provider command should abort due to gating."""

    def _on_block(reason: str, message: str) -> None:
        fallback = message or f"GPT: Request blocked; reason={reason}."
        if not message:
            normalised_reason = reason if reason in _KNOWN_DROP_REASONS else ""
            try:
                set_drop_reason(cast(RequestDropReason, normalised_reason), fallback)
            except Exception:
                pass
        try:
            notify(fallback)
        except Exception:
            pass

    blocked = guard_surface_request(
        surface="provider_commands",
        source="providerCommands",
        suppress_attr="suppress_overlay_inflight_guard",
        on_block=_on_block,
        notify_fn=lambda _message: None,
    )
    if blocked:
        return True

    try:
        if not last_drop_reason():
            set_drop_reason(cast(RequestDropReason, ""))
    except Exception:
        pass
    return False


@mod.action_class
class UserActions:
    def model_provider_list():
        """Show available providers in a canvas."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_list"):
            return

        registry = provider_registry()
        probe = bool(settings.get("user.model_provider_probe", False))
        entries = registry.status_entries(probe=probe)
        lines = _render_provider_lines(entries, "Providers")
        show_provider_canvas("Providers", lines)

    def model_provider_status():
        """Show the current provider status."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_status"):
            return

        registry = provider_registry()
        probe = bool(settings.get("user.model_provider_probe", False))
        current = registry.current_provider_id()
        entries = []
        for entry in registry.status_entries(probe=probe):
            if entry.get("id") != current:
                continue
            entry["streaming_enabled"] = bool(
                settings.get("user.model_streaming", True)
            )
            entries.append(entry)
        if not entries:
            lines = _render_error("No providers configured", [])
        else:
            lines = _render_provider_lines(entries, "Current provider")
        show_provider_canvas("Provider status", lines)

    def model_provider_use(name: str, model: str = ""):
        """Switch to a provider by name or alias, optionally setting its model."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_use", name=name, model=model):
            return

        registry = provider_registry()
        try:
            provider = registry.set_current_provider(name)
            if model:
                resolved_model = _resolve_model_alias(provider.id, model)
                _set_provider_model(provider.id, resolved_model)
            lines = _render_provider_lines(
                registry.status_entries(), f"Switched to {provider.display_name}"
            )
            show_provider_canvas("Provider switched", lines)
        except AmbiguousProviderError as exc:
            lines = _render_error(
                f"Ambiguous provider '{name}'", [f"{match}" for match in exc.matches]
            )
            show_provider_canvas("Provider error", lines)
        except ProviderLookupError:
            entries = registry.status_entries()
            suggestions = [entry["id"] for entry in entries]
            lines = _render_error(f"Unknown provider '{name}'", suggestions)
            show_provider_canvas("Provider error", lines)
            raise

    def model_provider_switch(name: str, model: str = ""):
        """Alias for model_provider_use."""

        if _reject_if_request_in_flight():
            return

        actions.user.model_provider_use(name, model)

    def model_provider_next():
        """Cycle to the next provider."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_next"):
            return

        registry = provider_registry()
        provider = registry.cycle(direction=1)
        lines = _render_provider_lines(
            registry.status_entries(), f"Switched to {provider.display_name}"
        )
        show_provider_canvas("Provider switched", lines)

    def model_provider_previous():
        """Cycle to the previous provider."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_previous"):
            return

        registry = provider_registry()
        provider = registry.cycle(direction=-1)
        lines = _render_provider_lines(
            registry.status_entries(), f"Switched to {provider.display_name}"
        )
        show_provider_canvas("Provider switched", lines)

    def model_provider_close():
        """Hide the provider canvas."""

        if _reject_if_request_in_flight():
            return

        if _delegate_to_bar_cli("model_provider_close"):
            return

        hide_provider_canvas()

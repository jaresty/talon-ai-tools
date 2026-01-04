from typing import Optional

from talon import Context, Module, actions, settings

from .providerStatusLog import log_provider_status, clear_provider_status
from .providerRegistry import (
    AmbiguousProviderError,
    ProviderLookupError,
    provider_registry,
)
from .requestGating import request_is_in_flight
from .historyLifecycle import last_drop_reason, set_drop_reason

from .modelHelpers import notify
from .surfaceGuidance import guard_surface_request

try:
    print(f"[debug] providerCommands loaded from {__file__}")
except Exception:
    pass
mod = Module()
ctx = Context()


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

        delegation = entry.get("delegation") or {}
        if isinstance(delegation, dict) and delegation:
            enabled = bool(delegation.get("enabled", True))
            failure_count = delegation.get("failure_count", 0) or 0
            failure_threshold = delegation.get("failure_threshold", 0) or 0
            last_reason = str(delegation.get("last_reason") or "")
            delegation_status = "enabled" if enabled else "disabled"
            lines.append(f"   delegation: {delegation_status}")
            if failure_count:
                if failure_threshold:
                    lines.append(
                        f"   delegation failures: {failure_count}/{failure_threshold}"
                    )
                else:
                    lines.append(f"   delegation failures: {failure_count}")
            if not enabled and last_reason:
                lines.append(f"   delegation reason: {last_reason}")
            message = str(delegation.get("message") or "").strip()
            if message:
                lines.append(f"   {message}")
    return lines


def _delegation_ready_prompt() -> str:
    try:
        from . import cliDelegation as _cliDelegation
    except Exception:
        _cliDelegation = None
    if _cliDelegation is not None:
        try:
            prompt = _cliDelegation.recovery_prompt()
        except Exception:
            prompt = ""
        if isinstance(prompt, str) and prompt.strip():
            return prompt.strip()
    return "CLI delegation ready."


def show_provider_status_message(message: str, *, prompt: str | None = None) -> None:
    try:
        registry = provider_registry()
        entries = registry.status_entries()
    except Exception:
        entries = []
    if not entries:
        return
    try:
        lines = _render_provider_lines(entries, message)
    except Exception:
        return
    if prompt and isinstance(prompt, str) and prompt.strip():
        lines.insert(1, prompt.strip())
    try:
        log_provider_status("Provider status", lines)
    except Exception:
        pass


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
            try:
                set_drop_reason(reason, fallback)
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
            set_drop_reason("")
    except Exception:
        pass
    return False


@mod.action_class
class UserActions:
    def model_provider_list():
        """Show available providers in a canvas."""

        if _reject_if_request_in_flight():
            return

        registry = provider_registry()
        probe = bool(settings.get("user.model_provider_probe", False))
        entries = registry.status_entries(probe=probe)
        lines = _render_provider_lines(entries, "Providers")
        log_provider_status("Providers", lines)

    def model_provider_status():
        """Show the current provider status."""

        if _reject_if_request_in_flight():
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
        log_provider_status("Provider status", lines)

    def model_provider_use(name: str, model: str = ""):
        """Switch to a provider by name or alias, optionally setting its model."""

        if _reject_if_request_in_flight():
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
            log_provider_status("Provider switched", lines)
        except AmbiguousProviderError as exc:
            lines = _render_error(
                f"Ambiguous provider '{name}'", [f"{match}" for match in exc.matches]
            )
            log_provider_status("Provider error", lines)
        except ProviderLookupError:
            entries = registry.status_entries()
            suggestions = [entry["id"] for entry in entries]
            lines = _render_error(f"Unknown provider '{name}'", suggestions)
            log_provider_status("Provider error", lines)
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

        registry = provider_registry()
        provider = registry.cycle(direction=1)
        lines = _render_provider_lines(
            registry.status_entries(), f"Switched to {provider.display_name}"
        )
        log_provider_status("Provider switched", lines)

    def model_provider_previous():
        """Cycle to the previous provider."""

        if _reject_if_request_in_flight():
            return

        registry = provider_registry()
        provider = registry.cycle(direction=-1)
        lines = _render_provider_lines(
            registry.status_entries(), f"Switched to {provider.display_name}"
        )
        log_provider_status("Provider switched", lines)

    def model_provider_close():
        """Hide the provider canvas."""

        if _reject_if_request_in_flight():
            return

        clear_provider_status()


def _install_cli_ready_handler() -> None:
    try:
        existing = getattr(actions.user, "cli_delegation_ready", None)
    except Exception:
        existing = None

    if (
        callable(existing)
        and getattr(existing, "__name__", "") == "_cli_delegation_ready_action"
    ):
        return

    def _cli_delegation_ready_action(source: str = "runtime") -> None:
        prompt = _delegation_ready_prompt()
        try:
            actions.user.calls.append(("cli_delegation_ready", (source,), {}))
        except Exception:
            pass
        try:
            notify(prompt)
        except Exception:
            pass

    try:
        setattr(actions.user, "cli_delegation_ready", _cli_delegation_ready_action)
    except Exception:
        pass


_install_cli_ready_handler()

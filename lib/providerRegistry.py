from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from talon import settings

# Default endpoints for bundled providers.
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
)


def _normalize(name: str) -> str:
    """Normalise a provider/alias string for matching."""

    return "".join(ch for ch in (name or "").lower() if ch.isalnum())


def provider_tokens_setting() -> Dict[str, str]:
    """Return provider tokens configured via Talon settings."""

    tokens: Dict[str, str] = {}
    try:
        openai_token = settings.get("user.model_provider_token_openai", "") or ""
        gemini_token = settings.get("user.model_provider_token_gemini", "") or ""
        if openai_token.strip():
            tokens["openai"] = openai_token.strip()
        if gemini_token.strip():
            tokens["gemini"] = gemini_token.strip()
    except Exception:
        pass

    try:
        maybe_tokens = settings.get("user.model_provider_tokens", {})  # legacy dict if available
    except Exception:
        maybe_tokens = {}
    if isinstance(maybe_tokens, dict):
        for key, value in maybe_tokens.items():
            if value is None:
                continue
            key_str = str(key).strip()
            val_str = str(value).strip()
            if key_str and val_str:
                tokens[key_str] = val_str
    return tokens


def provider_token_hint(provider_id: str, api_key_env: str) -> str:
    """Return a human-friendly hint for where to configure provider tokens."""

    return f"user.model_provider_tokens['{provider_id}'] or {api_key_env}"


@dataclass
class ProviderConfig:
    id: str
    display_name: str
    aliases: List[str] = field(default_factory=list)
    endpoint: str = ""
    api_key_env: str = "OPENAI_API_KEY"
    default_model: str = ""
    features: Dict[str, bool] = field(default_factory=dict)

    def alias_tokens(self) -> List[str]:
        tokens = [self.id, self.display_name] + list(self.aliases)
        return sorted({_normalize(token) for token in tokens if token})

    def normalized_features(self) -> Dict[str, bool]:
        return {k: bool(v) for k, v in (self.features or {}).items()}


class ProviderLookupError(Exception):
    """Raised when a provider lookup fails."""

    def __init__(self, name: str):
        super().__init__(f"Provider '{name}' not found")
        self.name = name


class AmbiguousProviderError(ProviderLookupError):
    """Raised when a provider lookup is ambiguous."""

    def __init__(self, name: str, matches: Sequence[str]):
        super().__init__(name)
        self.matches = list(matches)


def _default_model_for(provider_id: str) -> str:
    """Return a reasonable default model id for a provider."""

    if provider_id == "gemini":
        try:
            configured = settings.get("user.model_provider_model_gemini", "") or ""
            if configured.strip():
                return configured.strip()
        except Exception:
            pass
        return "gemini-1.5-pro"
    return settings.get("user.openai_model", "gpt-5")  # type: ignore[arg-type]


def _default_endpoint_for(provider_id: str) -> str:
    if provider_id == "gemini":
        return GEMINI_ENDPOINT
    return OPENAI_ENDPOINT


def _parse_aliases(value) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple, set)):
        return [str(v).strip() for v in value if str(v).strip()]
    return []


def default_providers() -> List[ProviderConfig]:
    return [
        ProviderConfig(
            id="openai",
            display_name="OpenAI",
            aliases=["open ai"],
            endpoint=OPENAI_ENDPOINT,
            api_key_env="OPENAI_API_KEY",
            default_model=_default_model_for("openai"),
            features={"streaming": True, "vision": True, "images": True},
        ),
        ProviderConfig(
            id="gemini",
            display_name="Gemini",
            aliases=["gemini", "gemeni"],
            endpoint=GEMINI_ENDPOINT,
            api_key_env="GEMINI_API_KEY",
            default_model=_default_model_for("gemini"),
            features={"streaming": True, "vision": True, "images": False},
        ),
    ]


class ProviderRegistry:
    """SSOT for provider configs and the active selection."""

    def __init__(self):
        self._providers: Dict[str, ProviderConfig] = {}
        self._model_overrides: Dict[str, str] = {}
        self.reload()

    def reload(self) -> None:
        """Reload providers from defaults + user overrides."""

        providers: Dict[str, ProviderConfig] = {
            provider.id: provider for provider in default_providers()
        }
        for cfg in self._parse_extra_providers():
            providers[cfg.id] = cfg
        # Apply in-session model overrides.
        for pid, model in self._model_overrides.items():
            if pid in providers and model:
                providers[pid].default_model = model
        self._providers = providers

    def _parse_extra_providers(self) -> List[ProviderConfig]:
        raw = settings.get("user.model_provider_extra", None)
        if raw is None:
            return []

        if isinstance(raw, str):
            try:
                raw = json.loads(raw)
            except Exception:
                return []

        entries: List[dict] = []
        if isinstance(raw, dict):
            if "providers" in raw and isinstance(raw["providers"], list):
                entries = [entry for entry in raw["providers"] if isinstance(entry, dict)]
            else:
                # Dict keyed by provider id.
                for pid, cfg in raw.items():
                    if not isinstance(cfg, dict):
                        continue
                    entry = dict(cfg)
                    entry.setdefault("id", pid)
                    entries.append(entry)
        elif isinstance(raw, list):
            entries = [entry for entry in raw if isinstance(entry, dict)]

        parsed: List[ProviderConfig] = []
        for entry in entries:
            pid = str(entry.get("id") or entry.get("key") or "").strip()
            if not pid:
                continue
            display = str(entry.get("display_name") or pid).strip() or pid
            aliases = _parse_aliases(entry.get("aliases"))
            endpoint = (
                str(entry.get("endpoint") or "").strip()
                or _default_endpoint_for(pid)
            )
            api_key_env = str(entry.get("api_key_env") or "OPENAI_API_KEY").strip()
            default_model = (
                str(entry.get("default_model") or "").strip()
                or _default_model_for(pid)
            )
            features = entry.get("features")
            parsed.append(
                ProviderConfig(
                    id=pid,
                    display_name=display,
                    aliases=aliases,
                    endpoint=endpoint,
                    api_key_env=api_key_env,
                    default_model=default_model,
                    features=features if isinstance(features, dict) else {},
                )
            )
        return parsed

    def providers(self) -> List[ProviderConfig]:
        self.reload()
        return list(self._providers.values())

    def provider_ids(self) -> List[str]:
        self.reload()
        return list(self._providers.keys())

    def resolve(self, name: str) -> ProviderConfig:
        """Resolve a provider by id/display/alias with prefix fallback."""

        self.reload()
        key = _normalize(name)
        matches: List[ProviderConfig] = []
        for cfg in self._providers.values():
            if key in cfg.alias_tokens():
                matches.append(cfg)
        if not matches:
            for cfg in self._providers.values():
                for token in cfg.alias_tokens():
                    if token.startswith(key):
                        matches.append(cfg)
                        break
        if not matches:
            raise ProviderLookupError(name)
        uniq: Dict[str, ProviderConfig] = {}
        for cfg in matches:
            uniq[cfg.id] = cfg
        matches = list(uniq.values())
        if len(matches) > 1:
            raise AmbiguousProviderError(name, [cfg.id for cfg in matches])
        return matches[0]

    def current_provider_id(self) -> str:
        """Return the current provider id from settings (or default)."""

        current = settings.get("user.model_provider_current", None)
        if isinstance(current, str) and current.strip():
            current = current.strip()
            if current in self._providers:
                return current
        default = settings.get("user.model_provider_default", None)
        if isinstance(default, str) and default.strip():
            if default.strip() in self._providers:
                return default.strip()
        # Fallback to first known provider.
        return next(iter(self._providers.keys()))

    def active_provider(self) -> ProviderConfig:
        """Return the active provider config, falling back to a default."""

        self.reload()
        provider_id = self.current_provider_id()
        provider = self._providers.get(provider_id)
        if provider:
            return provider
        # As a last resort, return the first provider in the registry.
        return next(iter(self._providers.values()))

    def set_current_provider(self, name: str) -> ProviderConfig:
        """Set the active provider by id/display/alias."""

        provider = self.resolve(name)
        settings.set("user.model_provider_current", provider.id)
        try:
            from .modelState import GPTState

            GPTState.current_provider_id = provider.id  # type: ignore[attr-defined]
        except Exception:
            pass
        return provider

    def set_default_model(self, provider_id: str, model: str) -> None:
        """Override the default model for a provider for this session."""

        model = (model or "").strip()
        if not model:
            return
        self._model_overrides[provider_id] = model
        if provider_id in self._providers:
            self._providers[provider_id].default_model = model

    def cycle(self, direction: int = 1) -> ProviderConfig:
        """Cycle to the next/previous provider."""

        self.reload()
        ids = self.provider_ids()
        if not ids:
            raise ProviderLookupError("no providers configured")
        current = self.current_provider_id()
        try:
            idx = ids.index(current)
        except ValueError:
            idx = 0
        next_idx = (idx + direction) % len(ids)
        provider = self._providers[ids[next_idx]]
        settings.set("user.model_provider_current", provider.id)
        try:
            from .modelState import GPTState

            GPTState.current_provider_id = provider.id  # type: ignore[attr-defined]
        except Exception:
            pass
        return provider

    def status_entries(self, *, probe: bool = False) -> List[dict]:
        """Return provider rows with availability details."""

        self.reload()
        tokens = provider_tokens_setting()
        entries: List[dict] = []
        current = self.current_provider_id()
        for cfg in self.providers():
            token_from_settings = tokens.get(cfg.id)
            token_from_env = os.environ.get(cfg.api_key_env)
            has_key = bool(token_from_settings) or bool(token_from_env)
            reachable = None
            reachability_error = ""
            if probe:
                reachable, reachability_error = self._probe_endpoint(cfg)
            token_hint = provider_token_hint(cfg.id, cfg.api_key_env)
            token_source = ""
            if token_from_settings:
                token_source = "settings"
            elif token_from_env:
                token_source = "env"
            entries.append(
                {
                    "id": cfg.id,
                    "display_name": cfg.display_name,
                    "aliases": list(cfg.aliases),
                    "endpoint": cfg.endpoint,
                    "default_model": cfg.default_model,
                    "api_key_env": cfg.api_key_env,
                    "available": has_key,
                    "current": cfg.id == current,
                    "features": cfg.normalized_features(),
                    "reachable": reachable,
                    "reachability_error": reachability_error,
                    "token_hint": token_hint,
                    "token_source": token_source,
                }
            )
        return entries

    def _probe_endpoint(self, provider: ProviderConfig) -> tuple[bool, str]:
        """Best-effort reachability check."""

        try:
            import requests
        except Exception:
            return False, "requests unavailable"

        url = provider.endpoint
        try:
            resp = requests.get(url, timeout=1)
            return bool(resp.status_code < 500), ""
        except Exception as exc:
            return False, str(exc)


_REGISTRY: Optional[ProviderRegistry] = None


def provider_registry() -> ProviderRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = ProviderRegistry()
    return _REGISTRY


def reset_provider_registry() -> None:
    global _REGISTRY
    _REGISTRY = ProviderRegistry()

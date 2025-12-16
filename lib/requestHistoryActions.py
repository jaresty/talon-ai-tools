import datetime
import os
import re
import sys
from typing import Optional

from talon import Module, actions, app, settings

from .modelConfirmationGUI import ConfirmationGUIState
from .modelHelpers import notify
from .modelState import GPTState
from .requestLog import (
    latest,
    nth_from_latest,
    all_entries as requestlog_all_entries,
    last_drop_reason,
)
from .requestBus import current_state, emit_history_saved
from .axisMappings import axis_key_to_value_map_for
from .axisCatalog import axis_catalog
from .requestState import RequestPhase
from .talonSettings import _canonicalise_axis_tokens

mod = Module()

_cursor_offset = 0


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""
    try:
        phase = getattr(current_state(), "phase", RequestPhase.IDLE)
        return phase not in (
            RequestPhase.IDLE,
            RequestPhase.DONE,
            RequestPhase.ERROR,
            RequestPhase.CANCELLED,
        )
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""
    if _request_is_in_flight():
        notify(
            "GPT: A request is already running; wait for it to finish or cancel it first."
        )
        return True
    return False


def _clear_notify_suppression() -> None:
    """Best-effort reset of any lingering notify suppression flags."""

    try:
        from talon_user.GPT import gpt as gpt_module  # type: ignore

        if hasattr(gpt_module, "_suppress_inflight_notify_request_id"):
            gpt_module._suppress_inflight_notify_request_id = None  # type: ignore[attr-defined]
    except Exception:
        pass


def _notify_with_drop_reason(fallback: str, *, use_drop_reason: bool) -> None:
    """Notify with last drop reason when requested, otherwise fall back."""

    if use_drop_reason:
        try:
            reason = last_drop_reason()
        except Exception:
            reason = ""
        if reason:
            notify(reason)
            return
    notify(fallback)

    try:
        if hasattr(GPTState, "suppress_inflight_notify_request_id"):
            GPTState.suppress_inflight_notify_request_id = None  # type: ignore[attr-defined]
    except Exception:
        pass


def _filter_axis_tokens(axis: str, tokens: list[str]) -> list[str]:
    """Filter history axis tokens against the known axis map.

    This helper centralises the token filtering semantics used when hydrating
    GPTState from history entries so tests and future RequestLifecycle/History
    façades can treat it as a single contract.
    """
    valid = axis_key_to_value_map_for(axis)
    return [t for t in tokens if t in valid]


def history_axes_for(axes: dict[str, list[str]]) -> dict[str, list[str]]:
    """Pure helper: normalise stored history axes via the axis map.

    This centralises how history entries' axis tokens are filtered against the
    configured axis keys so RequestLifecycle/HistoryQuery façades and tests
    can reuse it without depending on GPTState.
    """
    axes = axes or {}
    catalog = axis_catalog()
    catalog_tokens = {
        axis: set((tokens or {}).keys())
        for axis, tokens in (catalog.get("axes") or {}).items()
    }
    filtered_completeness = _filter_axis_tokens(
        "completeness", list(axes.get("completeness", []) or [])
    )
    filtered_scope = _filter_axis_tokens("scope", list(axes.get("scope", []) or []))
    filtered_method = _filter_axis_tokens("method", list(axes.get("method", []) or []))
    filtered_form = _filter_axis_tokens("form", list(axes.get("form", []) or []))
    filtered_channel = _filter_axis_tokens(
        "channel", list(axes.get("channel", []) or [])
    )
    filtered_directional = [
        t
        for t in _filter_axis_tokens(
            "directional", list(axes.get("directional", []) or [])
        )
        if t in catalog_tokens.get("directional", set())
    ]

    return {
        # Completeness remains scalar; leave ordering intact.
        "completeness": filtered_completeness,
        # Apply the shared canonicalisation (caps and dedupe) for the remaining axes.
        "scope": _canonicalise_axis_tokens("scope", filtered_scope),
        "method": _canonicalise_axis_tokens("method", filtered_method),
        "form": _canonicalise_axis_tokens("form", filtered_form),
        "channel": _canonicalise_axis_tokens("channel", filtered_channel),
        "directional": _canonicalise_axis_tokens("directional", filtered_directional),
    }


from collections.abc import Sequence


def _slugify_label(value: str) -> str:
    """Create a filesystem-friendly slug from a label."""
    value = (value or "").strip().lower().replace(" ", "-")
    value = re.sub(r"[^a-z0-9._-]+", "", value)
    return value or "history"


def _model_source_save_dir() -> str:
    """Return the base directory for saved history/model sources.

    Shares the same setting key as the GPT helpers so users have a single
    place to configure where source files are written.
    """
    try:
        base = settings.get("user.model_source_save_directory")
        if isinstance(base, str) and base.strip():
            return os.path.expanduser(base)
    except Exception:
        pass

    try:
        current_dir = os.path.dirname(__file__)
        user_root = os.path.dirname(os.path.dirname(current_dir))
        return os.path.join(user_root, "talon-ai-model-sources")
    except Exception:
        return os.path.join(os.path.dirname(__file__), "talon-ai-model-sources")


def history_summary_lines(entries: Sequence[object]) -> list[str]:
    """Pure helper: format recent history entries into summary lines.

    This mirrors the existing `gpt_request_history_list` formatting so drawers
    and future HistoryQuery façades can reuse it without depending on Talon
    notify calls.
    """
    lines: list[str] = []
    for idx, entry in enumerate(reversed(entries)):
        axes = getattr(entry, "axes", {}) or {}
        dir_tokens: list[str] = _directional_tokens_for_entry(entry)
        if not dir_tokens:
            # Skip entries without a directional lens to keep summaries aligned
            # with ADR 048 requirements.
            continue
        # Backfill/normalise directional tokens for downstream rendering.
        if isinstance(axes, dict) and dir_tokens:
            axes = dict(axes)
            axes["directional"] = dir_tokens
        prompt = (
            (getattr(entry, "prompt", "") or "").strip().splitlines()[0]
            if getattr(entry, "prompt", None)
            else ""
        )
        prompt_snippet = prompt[:60] + ("…" if len(prompt) > 60 else "")
        duration_ms = getattr(entry, "duration_ms", None)
        dur = f"{duration_ms}ms" if duration_ms is not None else ""
        request_id = getattr(entry, "request_id", "")
        label = request_id if not dur else f"{request_id} ({dur})"
        recipe = (getattr(entry, "recipe", "") or "").strip()
        if axes:
            axes_tokens = history_axes_for(axes)
            recipe_parts = recipe.split(" · ") if recipe else []
            static_token = recipe_parts[0] if recipe_parts else ""
            comp = " ".join(axes_tokens.get("completeness", [])) or (
                recipe_parts[1] if len(recipe_parts) > 1 else ""
            )
            scope = " ".join(axes_tokens.get("scope", [])) or (
                recipe_parts[2] if len(recipe_parts) > 2 else ""
            )
            method = " ".join(axes_tokens.get("method", [])) or (
                recipe_parts[3] if len(recipe_parts) > 3 else ""
            )
            form = " ".join(axes_tokens.get("form", [])) or (
                recipe_parts[4] if len(recipe_parts) > 4 else ""
            )
            channel = " ".join(axes_tokens.get("channel", [])) or (
                recipe_parts[5] if len(recipe_parts) > 5 else ""
            )
            directional = " ".join(axes_tokens.get("directional", []))
            recipe_tokens = [
                static_token,
                comp,
                scope,
                method,
                form,
                channel,
                directional,
            ]
            recipe = " · ".join([t for t in recipe_tokens if t])
        parts = [p for p in (recipe, prompt_snippet) if p]
        payload = " · ".join(parts) if parts else prompt_snippet
        provider_id = (getattr(entry, "provider_id", "") or "").strip()
        if provider_id:
            payload = f"{payload} · provider={provider_id}" if payload else f"provider={provider_id}"
        lines.append(f"{idx}: {label} | {payload}")
    return lines


def _save_history_prompt_to_file(entry) -> Optional[str]:
    """Save the given history entry's prompt/response to a markdown file and return the path.

    Uses the shared `user.model_source_save_directory` setting and a
    timestamped/slugged filename so history-driven saves align with the
    unified `file` destination (prompt + response + meta).
    """
    _clear_notify_suppression()
    if entry is None:
        notify("GPT: No request history available to save")
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None

    prompt = (getattr(entry, "prompt", "") or "").strip()
    response = (getattr(entry, "response", "") or "").strip()
    meta = (getattr(entry, "meta", "") or "").strip()

    if not prompt:
        notify("GPT: No prompt content available to save for this history entry")
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None

    base_dir = os.path.realpath(os.path.abspath(_model_source_save_dir()))
    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception as exc:
        notify(f"GPT: Could not create source directory: {exc}")
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None

    now = datetime.datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")

    provider_id = (getattr(entry, "provider_id", "") or "").strip()

    slug_parts: list[str] = ["history"]
    request_id = getattr(entry, "request_id", "") or ""
    if request_id:
        slug_parts.append(_slugify_label(str(request_id)))
    if provider_id:
        slug_parts.append(_slugify_label(provider_id))
    recipe = (getattr(entry, "recipe", "") or "").strip()
    if recipe:
        # Use the first token of the recipe as an additional hint.
        slug_parts.append(_slugify_label(recipe.split(" · ", 1)[0]))
    # Include directional axis tokens when present to make the slug more
    # self-describing for catalog-aligned history saves.
    normalized_axes = history_axes_for(getattr(entry, "axes", {}) or {})
    dir_tokens = normalized_axes.get("directional") or []
    if not dir_tokens:
        # Fall back to recipe-derived directional tokens so history saves remain
        # navigable even when axes payloads are missing direction.
        dir_tokens = _directional_tokens_for_entry(entry)
        if dir_tokens:
            normalized_axes = dict(normalized_axes)
            normalized_axes["directional"] = _canonicalise_axis_tokens(
                "directional", dir_tokens
            )
    if not dir_tokens:
        notify(
            "GPT: Cannot save history source; entry is missing a directional lens (fog/fig/dig/ong/rog/bog/jog)."
        )
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None
    for token in dir_tokens:
        slug_parts.append(_slugify_label(str(token)))

    filename = timestamp
    if slug_parts:
        filename += "-" + "-".join(slug_parts)
    filename += ".md"
    path = os.path.realpath(os.path.join(base_dir, filename))
    stem, ext = os.path.splitext(path)
    final_path = path
    counter = 1
    while os.path.exists(final_path):
        final_path = f"{stem}-{counter}{ext}"
        counter += 1
    path = final_path

    header_lines: list[str] = [
        f"saved_at: {now.isoformat()}Z",
        "source_type: history",
    ]
    if request_id:
        header_lines.append(f"request_id: {request_id}")
    if provider_id:
        header_lines.append(f"provider_id: {provider_id}")
    if recipe:
        header_lines.append(f"recipe: {recipe}")
    axes = normalized_axes
    for axis in ("completeness", "scope", "method", "form", "channel", "directional"):
        tokens = axes.get(axis) or []
        if isinstance(tokens, list) and tokens:
            joined = " ".join(str(t) for t in tokens if str(t).strip())
            if joined:
                header_lines.append(f"{axis}_tokens: {joined}")

    sections: list[str] = []
    if prompt:
        sections.append("# Prompt / Context\n" + prompt)
    if response:
        sections.append("# Response\n" + response)
    if meta:
        sections.append("# Meta\n" + meta)

    content = "\n".join(header_lines) + "\n---\n\n" + "\n\n".join(sections)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        notify(f"GPT: Failed to save history source file: {exc}")
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None

    notify(f"GPT: Saved history to {path}")
    try:
        GPTState.last_history_save_path = path  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        emit_history_saved(path, getattr(entry, "request_id", None))
    except Exception:
        pass
    return path


def _directional_tokens_for_entry(entry) -> list[str]:
    """Best-effort directional tokens for filtering/history navigation."""

    axes = getattr(entry, "axes", {}) or {}
    if isinstance(axes, dict) and axes.get("directional"):
        raw = axes.get("directional") or []
        try:
            known = set((axis_catalog().get("axes") or {}).get("directional", {}).keys())
        except Exception:
            known = set()
        canon = []
        for token in raw:
            lower = str(token).strip().lower()
            if not lower:
                continue
            if known and lower in known:
                canon.append(lower)
            elif not known:
                canon.append(lower)
        return canon

    recipe = (getattr(entry, "recipe", "") or "").strip()
    if recipe:
        tokens = [part.strip().lower() for part in recipe.split("·")]
        directional_map = (axis_catalog().get("axes") or {}).get("directional") or {}
        known_directional = set(directional_map.keys())
        for token in tokens:
            if token in known_directional:
                return [token]
    return []


def _directional_history_entries() -> list[object]:
    """Return history entries that include directional axes."""
    try:
        entries = requestlog_all_entries()
    except Exception:
        return []
    directional: list[object] = []
    for entry in entries:
        if _directional_tokens_for_entry(entry):
            directional.append(entry)
    return directional


def _show_entry(entry) -> bool:
    """Populate GPTState with a historic entry and open the response canvas."""
    _clear_notify_suppression()
    if entry is None:
        notify("GPT: No request history available")
        return False
    provider_id = (getattr(entry, "provider_id", "") or "").strip()
    raw_recipe = (getattr(entry, "recipe", "") or "").strip()
    axes_payload = getattr(entry, "axes", None)
    normalized_axes = (
        history_axes_for(axes_payload or {})
        if isinstance(axes_payload, dict) and axes_payload
        else None
    )
    parsed_recipe_fields = None
    if raw_recipe:
        try:
            from .modelPatternGUI import _parse_recipe
        except Exception:
            _parse_recipe = None
        if _parse_recipe is not None:
            try:
                parsed_recipe_fields = _parse_recipe(raw_recipe)
            except Exception:
                parsed_recipe_fields = None
    # History entries must include a directional lens post-ADR 048; bail early
    # before mutating state when missing.
    directional_tokens: list[str] = []
    if normalized_axes is not None:
        directional_tokens = normalized_axes.get("directional", []) or []
    if not directional_tokens and parsed_recipe_fields and len(parsed_recipe_fields) >= 7:
        directional_tokens = (parsed_recipe_fields[6] or "").split()
    if not directional_tokens:
        notify(
            "GPT: History entry has no directional lens; replay requires fog/fig/dig/ong/rog/bog/jog."
        )
        return False
    # Clear any stale presentation so paste uses the history entry text instead
    # of the last live model response.
    ConfirmationGUIState.current_presentation = None
    ConfirmationGUIState.display_thread = False
    ConfirmationGUIState.last_item_text = ""
    ConfirmationGUIState.show_advanced_actions = False
    GPTState.text_to_confirm = entry.response
    GPTState.last_response = entry.response
    GPTState.last_meta = entry.meta
    if provider_id:
        try:
            GPTState.current_provider_id = provider_id  # type: ignore[attr-defined]
        except Exception:
            pass
    else:
        try:
            GPTState.current_provider_id = ""  # type: ignore[attr-defined]
        except Exception:
            pass
    # Keep structured axis fields in sync with the stored axes/recipe so recaps
    # match the history entry instead of whatever the live state held.
    if normalized_axes is not None:
        axes = getattr(entry, "axes", {}) or {}
        if axes.get("style") or getattr(entry, "legacy_style", False):
            notify(
                "GPT: style axis is removed; use form/channel instead (history entry)."
            )
        # Fill missing axis tokens from the parsed recipe when available.
        parsed_static = parsed_recipe_fields[0] if parsed_recipe_fields else ""
        parsed_completeness = parsed_recipe_fields[1] if parsed_recipe_fields else ""
        parsed_scope = parsed_recipe_fields[2] if parsed_recipe_fields else ""
        parsed_method = parsed_recipe_fields[3] if parsed_recipe_fields else ""
        parsed_form = parsed_recipe_fields[4] if parsed_recipe_fields else ""
        parsed_channel = parsed_recipe_fields[5] if parsed_recipe_fields else ""

        merged_axes = {
            "completeness": normalized_axes.get("completeness") or ([parsed_completeness] if parsed_completeness else []),
            "scope": normalized_axes.get("scope") or (parsed_scope.split() if parsed_scope else []),
            "method": normalized_axes.get("method") or (parsed_method.split() if parsed_method else []),
            "form": normalized_axes.get("form") or (parsed_form.split() if parsed_form else []),
            "channel": normalized_axes.get("channel") or (parsed_channel.split() if parsed_channel else []),
            "directional": normalized_axes.get("directional") or (directional_tokens if directional_tokens else []),
        }
        GPTState.last_axes = merged_axes

        GPTState.last_static_prompt = (raw_recipe.split(" · ")[0] if raw_recipe else "") or parsed_static
        GPTState.last_completeness = " ".join(merged_axes.get("completeness", [])).strip()
        GPTState.last_scope = " ".join(merged_axes.get("scope", [])).strip()
        GPTState.last_method = " ".join(merged_axes.get("method", [])).strip()
        GPTState.last_form = " ".join(merged_axes.get("form", [])).strip()
        GPTState.last_channel = " ".join(merged_axes.get("channel", [])).strip()
        GPTState.last_directional = " ".join(merged_axes.get("directional", [])).strip()
        # Derive a concise, token-based recap from axes (token-only storage).
        recipe_parts = []
        for value in (
            GPTState.last_completeness,
            GPTState.last_scope,
            GPTState.last_method,
            GPTState.last_form,
            GPTState.last_channel,
            GPTState.last_directional,
        ):
            if value:
                recipe_parts.append(value)
        GPTState.last_recipe = " · ".join(recipe_parts)

    elif getattr(entry, "recipe", None):
        GPTState.last_recipe = raw_recipe
        static_prompt = completeness = scope = method = form = channel = directional = ""
        if parsed_recipe_fields and len(parsed_recipe_fields) >= 7:
            (
                static_prompt,
                completeness,
                scope,
                method,
                form,
                channel,
                directional,
            ) = parsed_recipe_fields
        GPTState.last_static_prompt = static_prompt or ""
        GPTState.last_completeness = completeness or ""
        GPTState.last_scope = scope or ""
        GPTState.last_method = method or ""
        GPTState.last_form = form or ""
        GPTState.last_channel = channel or ""
        GPTState.last_directional = directional or ""
        GPTState.last_axes = {
            "completeness": [completeness] if completeness else [],
            "scope": scope.split() if scope else [],
            "method": method.split() if method else [],
            "form": form.split() if form else [],
            "channel": channel.split() if channel else [],
            "directional": directional.split() if directional else [],
        }
    else:
        GPTState.last_static_prompt = ""
        GPTState.last_completeness = ""
        GPTState.last_scope = ""
        GPTState.last_method = ""
        GPTState.last_form = ""
        GPTState.last_channel = ""
        GPTState.last_directional = ""
        GPTState.last_axes = {
            "completeness": [],
            "scope": [],
            "method": [],
            "form": [],
            "channel": [],
        }
    # History entries must include a directional lens post-ADR 048.
    if not getattr(GPTState, "last_directional", ""):
        notify(
            "GPT: History entry has no directional lens; replay requires fog/fig/dig/ong/rog/bog/jog."
        )
        return False
    try:
        actions.user.model_response_canvas_open()
    except Exception:
        try:
            app.notify("GPT: Open response canvas to view history entry")
        except Exception:
            pass
    return True


@mod.action_class
class UserActions:
    def gpt_request_history_show_latest():
        """Open the last request/response/meta in the response canvas"""
        _clear_notify_suppression()
        if _reject_if_request_in_flight():
            return
        global _cursor_offset
        entries = _directional_history_entries()
        entry = entries[-1] if entries else None
        _cursor_offset = 0
        if entry is None:
            reason = ""
            try:
                reason = last_drop_reason()
            except Exception:
                reason = ""
            if reason:
                notify(reason)
            else:
                notify("GPT: No request history available")
            return
        _show_entry(entry)

    def gpt_request_history_show_previous(offset: int = 1):
        """Open a previous request/response/meta by offset (1 = previous, 2 = two back)"""
        if _reject_if_request_in_flight():
            return
        if offset < 0:
            notify("GPT: History offset must be non-negative")
            return
        entries = _directional_history_entries()
        index = len(entries) - 1 - offset
        entry = entries[index] if 0 <= index < len(entries) else None
        if entry is None:
            _notify_with_drop_reason(
                "GPT: No older history entry", use_drop_reason=not entries
            )
            return
        _show_entry(entry)

    def gpt_request_history_prev():
        """Step backward in request history and open the entry"""
        if _reject_if_request_in_flight():
            return
        global _cursor_offset
        entries = _directional_history_entries()
        _cursor_offset += 1
        index = len(entries) - 1 - _cursor_offset
        entry = entries[index] if 0 <= index < len(entries) else None
        if entry is None:
            _cursor_offset -= 1
            _notify_with_drop_reason(
                "GPT: No older history entry", use_drop_reason=not entries
            )
            return
        if not _show_entry(entry):
            _cursor_offset -= 1

    def gpt_request_history_next():
        """Step forward in request history and open the entry"""
        if _reject_if_request_in_flight():
            return
        global _cursor_offset
        entries = _directional_history_entries()
        if _cursor_offset <= 0:
            _notify_with_drop_reason(
                "GPT: Already at latest history entry", use_drop_reason=not entries
            )
            return
        _cursor_offset -= 1
        index = len(entries) - 1 - _cursor_offset
        entry = entries[index] if 0 <= index < len(entries) else None
        if entry is None:
            _cursor_offset += 1
            _notify_with_drop_reason(
                "GPT: No newer history entry", use_drop_reason=not entries
            )
            return
        if not _show_entry(entry):
            _cursor_offset += 1

    def gpt_request_history_list(count: int = 5):
        """Show a short summary of recent history entries"""
        _clear_notify_suppression()
        if _reject_if_request_in_flight():
            return
        try:
            entries = _directional_history_entries()[-count:]
        except Exception:
            entries = []
        if not entries:
            drop_reason = ""
            try:
                drop_reason = last_drop_reason()
            except Exception:
                drop_reason = ""
            if drop_reason:
                notify(drop_reason)
            else:
                notify("GPT: No request history available")
            return
        lines = history_summary_lines(entries)
        if not lines:
            drop_reason = ""
            try:
                drop_reason = last_drop_reason()
            except Exception:
                drop_reason = ""
            if drop_reason:
                notify(drop_reason)
            else:
                notify(
                    "GPT: No history entries include a directional lens; replay requires fog/fig/dig/ong/rog/bog/jog."
                )
            return
        message = "Recent model requests:\n" + "\n".join(lines)
        notify(message)

    def gpt_request_history_save_latest_source():
        """Save the latest request's source prompt to a markdown file."""
        _clear_notify_suppression()
        if _reject_if_request_in_flight():
            try:
                GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
            except Exception:
                pass
            return None
        entry = latest()
        return _save_history_prompt_to_file(entry)

    def gpt_request_history_last_save_path():
        """Return the last saved history source path or notify when unavailable."""
        if _reject_if_request_in_flight():
            return None
        return _last_history_save_path()

    def gpt_request_history_copy_last_save_path():
        """Copy the last saved history source path to the clipboard."""
        if _reject_if_request_in_flight():
            return None
        path = _last_history_save_path()
        if not path:
            return None
        try:
            actions.clip.set_text(path)  # type: ignore[attr-defined]
        except Exception:
            try:
                actions.user.paste(path)  # type: ignore[attr-defined]
            except Exception:
                notify(f"GPT: Unable to copy path: {path}")
                try:
                    GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
                except Exception:
                    pass
                return None
        notify(f"GPT: Copied history save path: {path}")
        return path

    def gpt_request_history_open_last_save_path():
        """Open the last saved history source file if available."""
        if _reject_if_request_in_flight():
            return None
        path = _last_history_save_path()
        if not path:
            return None
        if not os.path.exists(path):
            notify(f"GPT: Saved history file not found: {path}")
            try:
                GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
            except Exception:
                pass
            return None
        open_action = getattr(actions.app, "open", None)  # type: ignore[attr-defined]
        if callable(open_action):
            try:
                open_action(path)
            except Exception as exc:
                notify(f"GPT: Unable to open history save: {exc}")
                try:
                    GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
                except Exception:
                    pass
                return None
        else:
            notify("GPT: Unable to open history save; app.open action is unavailable.")
            return path
        notify(f"GPT: Opened history save: {path}")
        return path

    def gpt_request_history_show_last_save_path():
        """Show the last saved history source path."""
        if _reject_if_request_in_flight():
            return None
        path = _last_history_save_path()
        if not path:
            return None
        notify(f"GPT: Last saved history path: {path}")
        return path


def _last_history_save_path() -> Optional[str]:
    """Internal helper for history save path retrieval with notifications."""
    try:
        path = getattr(GPTState, "last_history_save_path", "")  # type: ignore[attr-defined]
    except Exception:
        path = ""
    if not path:
        notify("GPT: No saved history path available; run 'model history save exchange' first")
        return None
    real_path = os.path.realpath(path)
    if not os.path.exists(real_path) or not os.path.isfile(real_path):
        notify(
            f"GPT: Saved history path not found: {real_path}; rerun 'model history save exchange'"
        )
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        return None
    try:
        GPTState.last_history_save_path = real_path  # type: ignore[attr-defined]
    except Exception:
        pass
    return real_path

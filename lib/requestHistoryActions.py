import datetime
import os
from typing import Optional

from talon import Module, actions, app, settings

from .modelDestination import (
    HistorySaveError,
    resolve_model_source_directory,
    save_history_snapshot_to_file,
    slugify_label,
)
from .modelConfirmationGUI import ConfirmationGUIState
from .modelHelpers import notify
from .modelState import GPTState
from .requestLog import (
    latest,
    nth_from_latest,
    all_entries as requestlog_all_entries,
    consume_last_drop_reason_record,
    last_drop_reason,
    set_drop_reason,
    axis_snapshot_from_axes as requestlog_axis_snapshot_from_axes,
    AxisSnapshot,
)
from .dropReasonUtils import render_drop_reason
from .requestBus import emit_history_saved
from .axisCatalog import axis_catalog
from .requestState import RequestPhase
from .requestGating import request_is_in_flight, try_begin_request
from .suggestionCoordinator import recipe_header_lines_from_snapshot
from .talonSettings import _canonicalise_axis_tokens

mod = Module()

_cursor_offset = 0


def axis_snapshot_from_axes(axes: dict[str, list[str]] | None) -> AxisSnapshot:
    """Build a Concordance-aligned axis snapshot for history.

    Delegate to the request log snapshot builder so history and log surfaces use
    a single normalisation contract while trimming legacy style axes.
    """
    payload = dict(axes or {})
    payload.pop("style", None)
    try:
        return requestlog_axis_snapshot_from_axes(payload)
    except ValueError as exc:
        if "style axis is removed" not in str(exc):
            raise
        payload.pop("style", None)
        return requestlog_axis_snapshot_from_axes(payload)


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""

    try:
        return request_is_in_flight()
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""

    allowed, reason = try_begin_request(source="requestHistoryActions")
    if allowed:
        try:
            if not last_drop_reason():
                set_drop_reason("")
        except Exception:
            pass
        return False

    if not reason:
        return False

    message = render_drop_reason(reason)

    try:
        set_drop_reason(reason, message)
    except Exception:
        pass

    try:
        if message:
            notify(message)
    except Exception:
        pass

    return True


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
            record = consume_last_drop_reason_record()
            reason = record.message
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


def _persona_header_lines(entry) -> list[str]:
    snapshot = getattr(entry, "persona", {}) or {}
    if not snapshot:
        return []
    try:
        lines = recipe_header_lines_from_snapshot(snapshot)
    except Exception:
        return []
    return [
        line
        for line in lines
        if line.startswith("persona_preset: ") or line.startswith("intent_preset: ")
    ]


def _parse_summary_line(line: str, prefix: str) -> tuple[str, list[str]]:
    body = line[len(prefix) :].strip()
    if not body:
        return "", []
    if body.endswith(")") and "(" in body:
        descriptor, detail = body.split("(", 1)
        descriptor = descriptor.strip()
        parts = [part.strip() for part in detail[:-1].split(";") if part.strip()]
        return descriptor, parts
    return body, []


def _render_persona_summary(line: str) -> str:
    descriptor, parts = _parse_summary_line(line, "persona_preset: ")
    spoken = ""
    label = ""
    others: list[str] = []
    for part in parts:
        lower = part.lower()
        if lower.startswith("say: persona "):
            spoken = part[len("say: persona ") :].strip()
            continue
        if lower.startswith("label="):
            label = part.split("=", 1)[1].strip()
            continue
        others.append(part)
    display = spoken or label or descriptor or "persona"
    details: list[str] = []
    if descriptor and descriptor != display:
        details.append(f"key={descriptor}")
    if label and label != display:
        details.append(f"label={label}")
    if spoken:
        details.append(f"say: persona {spoken}")
    details.extend(others)
    fragment = f"persona {display}"
    if details:
        fragment += f" ({'; '.join(details)})"
    return fragment


def _render_intent_summary(line: str) -> str:
    descriptor, parts = _parse_summary_line(line, "intent_preset: ")
    spoken = ""
    label = ""
    display = ""
    purpose = ""
    others: list[str] = []
    for part in parts:
        lower = part.lower()
        if lower.startswith("say: intent "):
            spoken = part[len("say: intent ") :].strip()
            continue
        if lower.startswith("label="):
            label = part.split("=", 1)[1].strip()
            continue
        if lower.startswith("display="):
            display = part.split("=", 1)[1].strip()
            continue
        if lower.startswith("purpose="):
            purpose = part.split("=", 1)[1].strip()
            continue
        others.append(part)
    primary = descriptor or display or label or "intent"
    details: list[str] = []
    if descriptor:
        details.append(f"key={descriptor}")
    if label and label not in (primary, display):
        details.append(f"label={label}")
    if display and display != primary:
        details.append(f"display={display}")
    say_value = spoken or descriptor or primary
    if say_value:
        details.append(f"say: intent {say_value}")
    if purpose:
        details.append(f"purpose={purpose}")
    details.extend(others)
    fragment = f"intent {primary}"
    if details:
        fragment += f" ({'; '.join(details)})"
    return fragment


def _persona_summary_fragments(entry) -> list[str]:
    header_lines = _persona_header_lines(entry)
    if not header_lines:
        return []
    fragments: list[str] = []
    for line in header_lines:
        if line.startswith("persona_preset: "):
            fragment = _render_persona_summary(line)
        elif line.startswith("intent_preset: "):
            fragment = _render_intent_summary(line)
        else:
            fragment = ""
        if fragment.strip():
            fragments.append(fragment)
    return fragments


def history_axes_for(axes: dict[str, list[str]]) -> dict[str, list[str]]:
    """Pure helper: return the canonical axis snapshot for history.

    This is a thin wrapper over ``axis_snapshot_from_axes`` that trims the
    snapshot down to the known axis keys used by history drawers/saves.

    Keeping this wrapper (rather than duplicating filtering logic) ensures
    history callers and tests stay aligned with the request-log axis snapshot
    contract.
    """

    snapshot = axis_snapshot_from_axes(axes or {})
    return {
        "completeness": list(snapshot.get("completeness", []) or []),
        "scope": list(snapshot.get("scope", []) or []),
        "method": list(snapshot.get("method", []) or []),
        "form": list(snapshot.get("form", []) or []),
        "channel": list(snapshot.get("channel", []) or []),
        "directional": list(snapshot.get("directional", []) or []),
    }


from collections.abc import Sequence


def _slugify_label(value: str) -> str:
    """Create a filesystem-friendly slug from a label."""

    return slugify_label(value)


def _model_source_save_dir() -> str:
    """Return the base directory for saved history/model sources."""

    return resolve_model_source_directory()


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
            snapshot = axis_snapshot_from_axes(axes)
            axes_tokens = snapshot.known_axes()
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
            payload = (
                f"{payload} · provider={provider_id}"
                if payload
                else f"provider={provider_id}"
            )
        persona_fragments = _persona_summary_fragments(entry)
        if persona_fragments:
            persona_summary = " · ".join(persona_fragments)
            payload = f"{payload} · {persona_summary}" if payload else persona_summary
        lines.append(f"{idx}: {label} | {payload}")
    return lines


def _save_history_prompt_to_file(entry) -> Optional[str]:
    """Save the given history entry's prompt/response to a markdown file and return the path."""

    _clear_notify_suppression()
    if entry is None:
        message = "GPT: No request history available to save"
        notify(message)
        try:
            set_drop_reason("history_save_no_entry", message)
        except Exception:
            pass
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        try:
            session = getattr(GPTState, "last_streaming_session", None)
            if session is not None and hasattr(session, "record_history_saved"):
                session.record_history_saved("", success=False, error=message)
        except Exception:
            pass
        return None

    request_id = getattr(entry, "request_id", "") or ""

    def _record_history_save_event(
        *, success: bool, path: str = "", error: str = ""
    ) -> None:
        try:
            session = getattr(GPTState, "last_streaming_session", None)
            if session is None:
                return
            if getattr(session, "request_id", "") != request_id:
                return
            if not hasattr(session, "record_history_saved"):
                return
            session.record_history_saved(path, success=success, error=error)
        except Exception:
            pass

    prompt = getattr(entry, "prompt", "") or ""
    response = getattr(entry, "response", "") or ""
    meta = getattr(entry, "meta", "") or ""

    snapshot = axis_snapshot_from_axes(getattr(entry, "axes", {}) or {})
    axes_map = {key: list(values) for key, values in snapshot.known_axes().items()}
    dir_tokens = list(axes_map.get("directional", []) or [])
    if not dir_tokens:
        fallback_tokens = _directional_tokens_for_entry(entry)
        if fallback_tokens:
            canonical = _canonicalise_axis_tokens("directional", fallback_tokens)
            axes_map["directional"] = canonical
            dir_tokens = list(canonical)

    persona_lines = _persona_header_lines(entry)
    recipe = (getattr(entry, "recipe", "") or "").strip()
    provider_id = (getattr(entry, "provider_id", "") or "").strip()

    try:
        path = save_history_snapshot_to_file(
            request_id=request_id,
            provider_id=provider_id,
            recipe=recipe,
            prompt=prompt,
            response=response,
            meta=meta,
            axes_map=axes_map,
            directional_tokens=dir_tokens,
            persona_header_lines=persona_lines,
        )
    except HistorySaveError as exc:
        message = exc.message
        notify(message)
        try:
            set_drop_reason(exc.drop_reason, message)
        except Exception:
            pass
        try:
            GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
        except Exception:
            pass
        _record_history_save_event(success=False, error=message)
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

    _record_history_save_event(success=True, path=path)

    return path


def _directional_tokens_for_entry(entry) -> list[str]:
    """Best-effort directional tokens for filtering/history navigation."""

    axes = getattr(entry, "axes", {}) or {}
    if isinstance(axes, dict) and axes.get("directional"):
        raw = axes.get("directional") or []
        try:
            known = set(
                (axis_catalog().get("axes") or {}).get("directional", {}).keys()
            )
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
    if isinstance(axes_payload, dict):
        snapshot = axis_snapshot_from_axes(axes_payload or {})
    else:
        snapshot = axis_snapshot_from_axes({})
    normalized_axes = snapshot.known_axes()

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
    if (
        not directional_tokens
        and parsed_recipe_fields
        and len(parsed_recipe_fields) >= 7
    ):
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
        # Fill missing axis tokens from the parsed recipe when available.
        parsed_static = parsed_recipe_fields[0] if parsed_recipe_fields else ""
        parsed_completeness = parsed_recipe_fields[1] if parsed_recipe_fields else ""
        parsed_scope = parsed_recipe_fields[2] if parsed_recipe_fields else ""
        parsed_method = parsed_recipe_fields[3] if parsed_recipe_fields else ""
        parsed_form = parsed_recipe_fields[4] if parsed_recipe_fields else ""
        parsed_channel = parsed_recipe_fields[5] if parsed_recipe_fields else ""

        merged_axes = {
            "completeness": normalized_axes.get("completeness")
            or ([parsed_completeness] if parsed_completeness else []),
            "scope": normalized_axes.get("scope")
            or (parsed_scope.split() if parsed_scope else []),
            "method": normalized_axes.get("method")
            or (parsed_method.split() if parsed_method else []),
            "form": normalized_axes.get("form")
            or (parsed_form.split() if parsed_form else []),
            "channel": normalized_axes.get("channel")
            or (parsed_channel.split() if parsed_channel else []),
            "directional": normalized_axes.get("directional")
            or (directional_tokens if directional_tokens else []),
        }
        GPTState.last_axes = merged_axes

        GPTState.last_static_prompt = (
            raw_recipe.split(" · ")[0] if raw_recipe else ""
        ) or parsed_static
        GPTState.last_completeness = " ".join(
            merged_axes.get("completeness", [])
        ).strip()
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
        static_prompt = completeness = scope = method = form = channel = directional = (
            ""
        )
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
            _notify_with_drop_reason(
                "GPT: No request history available", use_drop_reason=True
            )
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
            _notify_with_drop_reason(
                "GPT: No request history available", use_drop_reason=True
            )
            return
        lines = history_summary_lines(entries)
        if not lines:
            _notify_with_drop_reason(
                "GPT: No history entries include a directional lens; replay requires fog/fig/dig/ong/rog/bog/jog.",
                use_drop_reason=True,
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
        path = _last_history_save_path()
        if not path:
            return None
        try:
            set_drop_reason("")
        except Exception:
            pass
        return path

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
                message = f"GPT: Unable to copy path: {path}"
                notify(message)
                try:
                    set_drop_reason("history_save_copy_failed", message)
                except Exception:
                    pass
                try:
                    GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
                except Exception:
                    pass
                return None
        try:
            set_drop_reason("")
        except Exception:
            pass
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
            message = f"GPT: Saved history file not found: {path}"
            notify(message)
            try:
                set_drop_reason("history_save_path_not_found", message)
            except Exception:
                pass
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
                message = f"GPT: Unable to open history save: {exc}"
                notify(message)
                try:
                    set_drop_reason("history_save_open_exception", message)
                except Exception:
                    pass
                try:
                    GPTState.last_history_save_path = ""  # type: ignore[attr-defined]
                except Exception:
                    pass
                return None
        else:
            message = (
                "GPT: Unable to open history save; app.open action is unavailable."
            )
            notify(message)
            try:
                set_drop_reason("history_save_open_action_unavailable", message)
            except Exception:
                pass
            return path
        try:
            set_drop_reason("")
        except Exception:
            pass
        notify(f"GPT: Opened history save: {path}")
        return path

    def gpt_request_history_show_last_save_path():
        """Show the last saved history source path."""
        if _reject_if_request_in_flight():
            return None
        path = _last_history_save_path()
        if not path:
            return None
        try:
            set_drop_reason("")
        except Exception:
            pass
        notify(f"GPT: Last saved history path: {path}")
        return path


def _last_history_save_path() -> Optional[str]:
    """Internal helper for history save path retrieval with notifications."""
    try:
        path = getattr(GPTState, "last_history_save_path", "")  # type: ignore[attr-defined]
    except Exception:
        path = ""
    if not path:
        message = "GPT: No saved history path available; run 'model history save exchange' first"
        notify(message)
        try:
            set_drop_reason("history_save_path_unset", message)
        except Exception:
            pass
        return None
    real_path = os.path.realpath(path)
    if not os.path.exists(real_path) or not os.path.isfile(real_path):
        message = f"GPT: Saved history path not found: {real_path}; rerun 'model history save exchange'"
        notify(message)
        try:
            set_drop_reason("history_save_path_not_found", message)
        except Exception:
            pass
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

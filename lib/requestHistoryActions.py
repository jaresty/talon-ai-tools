import datetime
import os
import re

from talon import Module, actions, app, settings

from .modelConfirmationGUI import ConfirmationGUIState
from .modelHelpers import notify
from .modelState import GPTState
from .requestLog import latest, nth_from_latest, all_entries
from .axisMappings import axis_key_to_value_map_for

mod = Module()

_cursor_offset = 0


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
    return {
        "completeness": _filter_axis_tokens(
            "completeness", list(axes.get("completeness", []) or [])
        ),
        "scope": _filter_axis_tokens("scope", list(axes.get("scope", []) or [])),
        "method": _filter_axis_tokens("method", list(axes.get("method", []) or [])),
        "style": _filter_axis_tokens("style", list(axes.get("style", []) or [])),
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
        parts = [p for p in (recipe, prompt_snippet) if p]
        payload = " · ".join(parts) if parts else prompt_snippet
        lines.append(f"{idx}: {label} | {payload}")
    return lines


def _save_history_prompt_to_file(entry) -> None:
    """Save the given history entry's prompt to a markdown file.

    Uses the shared `user.model_source_save_directory` setting and a
    timestamped/slugged filename so history-driven saves align with other
    source saves.
    """
    if entry is None:
        notify("GPT: No request history available to save")
        return

    prompt = (getattr(entry, "prompt", "") or "").strip()
    if not prompt:
        notify("GPT: No source content available to save for this history entry")
        return

    base_dir = _model_source_save_dir()
    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception as exc:
        notify(f"GPT: Could not create source directory: {exc}")
        return

    now = datetime.datetime.utcnow()
    timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")

    slug_parts: list[str] = ["history"]
    request_id = getattr(entry, "request_id", "") or ""
    if request_id:
        slug_parts.append(_slugify_label(str(request_id)))
    recipe = (getattr(entry, "recipe", "") or "").strip()
    if recipe:
        # Use the first token of the recipe as an additional hint.
        slug_parts.append(_slugify_label(recipe.split(" · ", 1)[0]))

    filename = timestamp
    if slug_parts:
        filename += "-" + "-".join(slug_parts)
    filename += ".md"
    path = os.path.join(base_dir, filename)

    header_lines: list[str] = [
        f"saved_at: {now.isoformat()}Z",
        "source_type: history",
    ]
    if request_id:
        header_lines.append(f"request_id: {request_id}")
    if recipe:
        header_lines.append(f"recipe: {recipe}")
    axes = getattr(entry, "axes", {}) or {}
    for axis in ("completeness", "scope", "method", "style"):
        tokens = axes.get(axis) or []
        if isinstance(tokens, list) and tokens:
            joined = " ".join(str(t) for t in tokens if str(t).strip())
            if joined:
                header_lines.append(f"{axis}_tokens: {joined}")

    body = "# Source\n" + prompt
    content = "\n".join(header_lines) + "\n---\n\n" + body

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as exc:
        notify(f"GPT: Failed to save history source file: {exc}")
        return

    notify(f"GPT: Saved history source to {path}")


def _show_entry(entry) -> None:
    """Populate GPTState with a historic entry and open the response canvas."""
    if entry is None:
        notify("GPT: No request history available")
        return
    # Clear any stale presentation so paste uses the history entry text instead
    # of the last live model response.
    ConfirmationGUIState.current_presentation = None
    ConfirmationGUIState.display_thread = False
    ConfirmationGUIState.last_item_text = ""
    ConfirmationGUIState.show_advanced_actions = False
    GPTState.text_to_confirm = entry.response
    GPTState.last_response = entry.response
    GPTState.last_meta = entry.meta
    # Keep structured axis fields in sync with the stored axes/recipe so recaps
    # match the history entry instead of whatever the live state held.
    raw_recipe = getattr(entry, "recipe", "") or ""
    if getattr(entry, "axes", None):
        axes = getattr(entry, "axes", {}) or {}
        GPTState.last_axes = history_axes_for(axes)

        GPTState.last_static_prompt = raw_recipe.split(" · ")[0] if raw_recipe else ""
        GPTState.last_completeness = " ".join(
            GPTState.last_axes["completeness"]
        ).strip()
        GPTState.last_scope = " ".join(GPTState.last_axes["scope"]).strip()
        GPTState.last_method = " ".join(GPTState.last_axes["method"]).strip()
        GPTState.last_style = " ".join(GPTState.last_axes["style"]).strip()
        # Derive a concise, token-based recap from axes (token-only storage).
        recipe_parts = []
        # Ignore any legacy recipe content when axes are present; recap is token-only.
        for value in (
            GPTState.last_completeness,
            GPTState.last_scope,
            GPTState.last_method,
            GPTState.last_style,
        ):
            if value:
                recipe_parts.append(value)
        GPTState.last_recipe = " · ".join(recipe_parts)

    elif getattr(entry, "recipe", None):
        GPTState.last_recipe = raw_recipe
        try:
            from .modelPatternGUI import _parse_recipe
        except Exception:
            _parse_recipe = None
        if _parse_recipe is not None:
            try:
                (
                    static_prompt,
                    completeness,
                    scope,
                    method,
                    style,
                    directional,
                ) = _parse_recipe(GPTState.last_recipe)
                GPTState.last_static_prompt = static_prompt or ""
                GPTState.last_completeness = completeness or ""
                GPTState.last_scope = scope or ""
                GPTState.last_method = method or ""
                GPTState.last_style = style or ""
                GPTState.last_directional = directional or ""
                GPTState.last_axes = {
                    "completeness": [completeness] if completeness else [],
                    "scope": scope.split() if scope else [],
                    "method": method.split() if method else [],
                    "style": style.split() if style else [],
                }
            except Exception:
                pass
    else:
        GPTState.last_static_prompt = ""
        GPTState.last_completeness = ""
        GPTState.last_scope = ""
        GPTState.last_method = ""
        GPTState.last_style = ""
        GPTState.last_directional = ""
        GPTState.last_axes = {
            "completeness": [],
            "scope": [],
            "method": [],
            "style": [],
        }
    try:
        actions.user.model_response_canvas_open()
    except Exception:
        try:
            app.notify("GPT: Open response canvas to view history entry")
        except Exception:
            pass


@mod.action_class
class UserActions:
    def gpt_request_history_show_latest():
        """Open the last request/response/meta in the response canvas"""
        global _cursor_offset
        entry = latest()
        _cursor_offset = 0
        _show_entry(entry)

    def gpt_request_history_show_previous(offset: int = 1):
        """Open a previous request/response/meta by offset (1 = previous, 2 = two back)"""
        if offset < 0:
            notify("GPT: History offset must be non-negative")
            return
        entry = nth_from_latest(offset)
        _show_entry(entry)

    def gpt_request_history_prev():
        """Step backward in request history and open the entry"""
        global _cursor_offset
        _cursor_offset += 1
        entry = nth_from_latest(_cursor_offset)
        if entry is None:
            _cursor_offset -= 1
            notify("GPT: No older history entry")
            return
        _show_entry(entry)

    def gpt_request_history_next():
        """Step forward in request history and open the entry"""
        global _cursor_offset
        if _cursor_offset <= 0:
            notify("GPT: Already at latest history entry")
            return
        _cursor_offset -= 1
        entry = nth_from_latest(_cursor_offset)
        _show_entry(entry)

    def gpt_request_history_list(count: int = 5):
        """Show a short summary of recent history entries"""
        entries = all_entries()[-count:]
        if not entries:
            notify("GPT: No request history available")
            return
        lines = history_summary_lines(entries)
        message = "Recent model requests:\n" + "\n".join(lines)
        notify(message)

    def gpt_request_history_save_latest_source():
        """Save the latest request's source prompt to a markdown file."""
        entry = latest()
        _save_history_prompt_to_file(entry)

from talon import Module, actions, app

from .modelConfirmationGUI import ConfirmationGUIState
from .modelHelpers import notify
from .modelState import GPTState
from .requestLog import latest, nth_from_latest, all_entries
from .axisMappings import axis_key_to_value_map_for

mod = Module()

_cursor_offset = 0


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
        def _filter_tokens(axis: str, tokens: list[str]) -> list[str]:
            valid = axis_key_to_value_map_for(axis)
            return [t for t in tokens if t in valid]

        GPTState.last_axes = {
            "completeness": _filter_tokens("completeness", list(axes.get("completeness", []) or [])),
            "scope": _filter_tokens("scope", list(axes.get("scope", []) or [])),
            "method": _filter_tokens("method", list(axes.get("method", []) or [])),
            "style": _filter_tokens("style", list(axes.get("style", []) or [])),
        }
        GPTState.last_static_prompt = raw_recipe.split(" · ")[0] if raw_recipe else ""
        GPTState.last_completeness = " ".join(GPTState.last_axes["completeness"]).strip()
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
        GPTState.last_axes = {"completeness": [], "scope": [], "method": [], "style": []}
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
        lines = []
        for idx, entry in enumerate(reversed(entries)):
            prompt = (entry.prompt or "").strip().splitlines()[0] if entry.prompt else ""
            prompt_snippet = prompt[:60] + ("…" if len(prompt) > 60 else "")
            dur = f"{entry.duration_ms}ms" if entry.duration_ms is not None else ""
            label = entry.request_id if not dur else f"{entry.request_id} ({dur})"
            recipe = (getattr(entry, "recipe", "") or "").strip()
            parts = [p for p in (recipe, prompt_snippet) if p]
            payload = " · ".join(parts) if parts else prompt_snippet
            lines.append(f"{idx}: {label} | {payload}")
        message = "Recent model requests:\n" + "\n".join(lines)
        notify(message)

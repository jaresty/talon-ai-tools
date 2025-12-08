from talon import Module, actions, app

from .modelConfirmationGUI import ConfirmationGUIState
from .modelHelpers import notify
from .modelState import GPTState
from .requestLog import latest, nth_from_latest, all_entries

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
            lines.append(f"{idx}: {label} | {prompt_snippet}")
        message = "Recent model requests:\n" + "\n".join(lines)
        notify(message)

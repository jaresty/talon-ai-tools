import textwrap

from typing import Optional, Union

from talon import Context, Module, actions, clip, cron, imgui, settings

from .axisJoin import axis_join
from .modelHelpers import GPTState, extract_message, notify
from .overlayLifecycle import close_common_overlays
from .requestGating import request_is_in_flight
from .historyLifecycle import last_drop_reason, set_drop_reason, try_begin_request
from .dropReasonUtils import render_drop_reason
from .modelPresentation import ResponsePresentation
from .metaPromptConfig import first_meta_preview_line, meta_preview_lines

mod = Module()
ctx = Context()


class ConfirmationGUIState:
    display_thread = False
    last_item_text = ""
    current_presentation: Optional[ResponsePresentation] = None
    show_advanced_actions = False

    @classmethod
    def update(cls):
        cls.display_thread = (
            "USER" in GPTState.text_to_confirm and "GPT" in GPTState.text_to_confirm
        )
        if len(GPTState.thread) == 0:
            # When there is no thread, always treat the view as a simple
            # single-response confirmation, regardless of any stray tokens.
            cls.display_thread = False
            cls.last_item_text = ""
            return

        last_message_item = GPTState.thread[-1]["content"][0]
        cls.last_item_text = last_message_item.get("text", "")


def _request_is_in_flight() -> bool:
    """Return True when a GPT request is currently running."""

    try:
        return request_is_in_flight()
    except Exception:
        return False


def _reject_if_request_in_flight() -> bool:
    """Notify and return True when a GPT request is already running."""

    allowed, reason = try_begin_request(source="modelConfirmationGUI")
    if allowed:
        try:
            pending_message = last_drop_reason()
        except Exception:
            pending_message = ""
        if not pending_message:
            try:
                set_drop_reason("")
            except Exception:
                pass
        return False

    if not reason:
        return False

    message = ""
    try:
        message = render_drop_reason(reason)
    except Exception:
        pass

    try:
        set_drop_reason(reason, message)
    except Exception:
        pass

    if message:
        try:
            notify(message)
        except Exception:
            pass
    return True


@imgui.open()
def confirmation_gui(gui: imgui.GUI):
    gui.text("Confirm model output before pasting")
    gui.line()
    gui.spacer()

    # This is a heuristic. realistically, it is extremely unlikely that
    # any other text would have both of these literals in the text
    # to confirm and it not represent a thread
    ConfirmationGUIState.update()

    width = settings.get("user.model_window_char_width") or 80
    for paragraph in GPTState.text_to_confirm.split("\n"):
        for line in textwrap.wrap(paragraph, width):
            gui.text(line)

    axes_tokens = getattr(GPTState, "last_axes", {}) or {}

    recipe_parts: list[str] = []
    static_prompt = getattr(GPTState, "last_static_prompt", "") or ""
    if static_prompt:
        recipe_parts.append(static_prompt)
    last_completeness = axis_join(
        axes_tokens, "completeness", getattr(GPTState, "last_completeness", "") or ""
    )
    last_scope = axis_join(
        axes_tokens, "scope", getattr(GPTState, "last_scope", "") or ""
    )
    last_method = axis_join(
        axes_tokens, "method", getattr(GPTState, "last_method", "") or ""
    )
    last_form = axis_join(axes_tokens, "form", getattr(GPTState, "last_form", "") or "")
    last_channel = axis_join(
        axes_tokens, "channel", getattr(GPTState, "last_channel", "") or ""
    )
    for value in (last_completeness, last_scope, last_method, last_form, last_channel):
        if value:
            recipe_parts.append(value)

    recipe = " · ".join(recipe_parts) if recipe_parts else GPTState.last_recipe
    if recipe:
        gui.spacer()
        # Include the directional lens alongside the core recipe tokens so the
        # confirmation GUI matches quick help and other recap surfaces.
        if getattr(GPTState, "last_directional", ""):
            recipe_text = f"{recipe} · {GPTState.last_directional}"
        else:
            recipe_text = recipe
        gui.text(f"Recipe: {recipe_text}")
        # Surface migration hints inline so users see the single-value
        # form/channel contract and directional requirement during parse-back.
        gui.text(
            "Form/channel are single-value; legacy style tokens are removed—use form/channel."
        )
        gui.text("Always include one directional lens: fog/fig/dig/ong/rog/bog/jog.")
        # When available, show a compact meta-interpretation radar so the
        # confirmation GUI surfaces both what was asked and how it was
        # interpreted, without affecting paste semantics.
        meta = getattr(GPTState, "last_meta", "").strip()
        # If the confirmation text is just the meta block (for example,
        # when the user has explicitly passed meta to the window), show the
        # full non-heading meta lines. Otherwise, keep the radar bounded.
        if GPTState.text_to_confirm.strip() == meta:
            preview_lines = meta_preview_lines(meta, max_lines=None)
        else:
            preview_lines = meta_preview_lines(meta, max_lines=4)
        if preview_lines:
            # Show a richer multi-line meta recap. Use a "Meta:" header and
            # wrap each preview line to match the main window width so users
            # can read the full approach/assumptions at a glance.
            gui.text("Meta:")
            for line in preview_lines:
                for wrapped in textwrap.wrap(line, width):
                    gui.text(f"  {wrapped}")

    # gui.spacer()
    # if gui.button("Chain response"):
    #     actions.user.confirmation_gui_paste()
    #     actions.user.gpt_select_last()

    gui.spacer()
    if gui.button("Paste response"):
        actions.user.confirmation_gui_paste()

    gui.spacer()
    if gui.button("Copy response"):
        actions.user.confirmation_gui_copy()

    gui.spacer()
    if gui.button("Discard response"):
        actions.user.confirmation_gui_close()

    gui.spacer()
    toggle_label = (
        "Hide advanced actions"
        if ConfirmationGUIState.show_advanced_actions
        else "More actions…"
    )
    if gui.button(toggle_label):
        ConfirmationGUIState.show_advanced_actions = (
            not ConfirmationGUIState.show_advanced_actions
        )

    if ConfirmationGUIState.show_advanced_actions:
        gui.spacer()
        if gui.button("Pass to context"):
            actions.user.confirmation_gui_pass_context()

        gui.spacer()
        if gui.button("Pass to query"):
            actions.user.confirmation_gui_pass_query()

        gui.spacer()
        if gui.button("Pass to thread"):
            actions.user.confirmation_gui_pass_thread()

        gui.spacer()
        if gui.button("Open browser"):
            actions.user.confirmation_gui_open_browser()

        gui.spacer()
        if gui.button("View in canvas"):
            actions.user.model_response_canvas_open()

        gui.spacer()
        if gui.button("Analyze prompt"):
            actions.user.confirmation_gui_analyze_prompt()

        gui.spacer()
        if gui.button("Save to file"):
            actions.user.confirmation_gui_save_to_file()

        gui.spacer()
        if gui.button("Show grammar help"):
            actions.user.model_help_canvas_open_for_last_recipe()

        gui.spacer()
        if gui.button("Open pattern menu"):
            actions.user.confirmation_gui_open_pattern_menu_for_prompt()

        gui.spacer()
        if gui.button("Open Help Hub"):
            actions.user.help_hub_open()

        gui.spacer()
        if gui.button("History"):
            actions.user.request_history_drawer_toggle()


def _confirmation_gui_paste_impl(text_to_set: str) -> None:
    from .modelDestination import Paste  # type: ignore import-cycle
    from .modelHelpers import format_message
    from .promptPipeline import PromptResult

    prompt_result = PromptResult.from_messages([format_message(text_to_set)])

    # Record the paste intent before closing surfaces so state remains
    # accurate even if downstream actions no-op.
    GPTState.last_response = text_to_set
    GPTState.last_was_pasted = True
    # Clear the confirmation surface before pasting to return focus to the
    # user's target application.
    GPTState.text_to_confirm = ""
    ConfirmationGUIState.current_presentation = None
    ConfirmationGUIState.display_thread = False
    ConfirmationGUIState.last_item_text = ""
    try:
        actions.user.model_response_canvas_close()
    except Exception:
        pass
    original_suppress = getattr(GPTState, "suppress_response_canvas_close", False)
    try:
        GPTState.suppress_response_canvas_close = True
    except Exception:
        pass
    try:
        GPTState.current_destination_kind = "paste"
    except Exception:
        pass
    actions.user.confirmation_gui_close()
    try:
        GPTState.suppress_response_canvas_close = original_suppress
    except Exception:
        pass

    paste_called = {"ran": False}
    paste_text = text_to_set
    paste_attempt = {"count": 0}
    max_attempts = 5
    retry_delay_ms = "60ms"

    def _paste():
        if paste_called["ran"]:
            return
        dest = Paste()
        try:
            inside = dest.inside_textarea()
        except Exception:
            inside = True
        if not inside and paste_attempt["count"] < max_attempts:
            paste_attempt["count"] += 1
            try:
                cron.after(retry_delay_ms, _paste)
                return
            except Exception:
                pass
        paste_called["ran"] = True
        pre_calls = getattr(actions.user.paste, "call_count", None)
        dest.insert(prompt_result)
        post_calls = getattr(actions.user.paste, "call_count", None)
        if pre_calls is not None and post_calls is not None and post_calls > pre_calls:
            if hasattr(actions.user, "calls"):
                actions.user.calls.append(("paste", (paste_text,), {}))
            if hasattr(actions.user, "pasted"):
                actions.user.pasted.append(paste_text)

    # Delay paste slightly so the response canvas/GUI can relinquish focus
    # before we type into the target application.
    try:
        cron.after(retry_delay_ms, _paste)
    except Exception:
        _paste()
        return
    if hasattr(actions.user, "calls") and not paste_called["ran"]:
        _paste()


@mod.action_class
class UserActions:
    def confirmation_gui_append(model_output: Union[str, ResponsePresentation]):
        """Add text to the confirmation surface (canvas-based viewer)"""
        if _reject_if_request_in_flight():
            return
        try:
            close_common_overlays(actions.user, exclude={"model_response_canvas_close"})
        except Exception:
            pass
        ctx.tags = ["user.model_window_open"]
        ConfirmationGUIState.show_advanced_actions = False
        if isinstance(model_output, ResponsePresentation):
            ConfirmationGUIState.current_presentation = model_output
            GPTState.text_to_confirm = model_output.display_text
        else:
            ConfirmationGUIState.current_presentation = None
            GPTState.text_to_confirm = model_output
        # Open the canvas-based response viewer instead of the legacy imgui
        # confirmation window.
        actions.user.model_response_canvas_open()

    def confirmation_gui_close():
        """Close the model output without pasting it"""
        GPTState.text_to_confirm = ""
        confirmation_gui.hide()
        ctx.tags = []
        try:
            from .modelResponseCanvas import ResponseCanvasState  # type: ignore circular

            ResponseCanvasState.showing = False
        except Exception:
            pass
        try:
            GPTState.response_canvas_showing = False
        except Exception:
            pass
        ConfirmationGUIState.current_presentation = None
        ConfirmationGUIState.show_advanced_actions = False
        # Close other overlays so confirmation does not leave stray surfaces open.
        # Always go through the shared closer so ordering stays consistent; it
        # will call model_response_canvas_close unless suppressed.
        suppress_canvas = getattr(GPTState, "suppress_response_canvas_close", False)
        exclude = {"confirmation_gui_close"}
        if suppress_canvas:
            exclude.add("model_response_canvas_close")
        close_common_overlays(actions.user, exclude=exclude)

    def confirmation_gui_pass_context():
        """Add the model output to the context"""
        actions.user.gpt_push_context(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_pass_query():
        """Add the model output to the query"""
        actions.user.gpt_push_query(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_save_to_file():
        """Save the current confirmation response to a markdown file via the file destination."""
        from .modelDestination import File
        from .modelHelpers import format_message
        from .promptPipeline import PromptResult

        text = (GPTState.text_to_confirm or "").strip()
        if not text:
            notify("GPT: No response available to save")
            return

        result = PromptResult.from_messages([format_message(text)])
        File().insert(result)

    def confirmation_gui_open_browser():
        """Open a browser with the response"""
        presentation = ConfirmationGUIState.current_presentation
        if presentation and presentation.open_browser:
            actions.user.gpt_open_browser(presentation.display_text)
        else:
            actions.user.gpt_open_browser(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_analyze_prompt():
        """Analyze the last prompt"""
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()
        actions.user.gpt_analyze_prompt()

    def confirmation_gui_pass_thread():
        """Add the model output to the thread"""

        actions.user.gpt_push_thread(GPTState.text_to_confirm)
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_copy():
        """Copy the model output to the clipboard"""
        text_to_set = (
            GPTState.text_to_confirm
            if not ConfirmationGUIState.display_thread
            else ConfirmationGUIState.last_item_text
        )

        clip.set_text(text_to_set)
        GPTState.text_to_confirm = ""

        actions.user.confirmation_gui_close()

    def confirmation_gui_paste():
        """Paste the model output"""
        if ConfirmationGUIState.display_thread:
            text_to_set = ConfirmationGUIState.last_item_text
        elif ConfirmationGUIState.current_presentation:
            # Prefer the presentation's explicit paste text, falling back to
            # the display text or raw confirmation text when needed.
            text_to_set = (
                getattr(ConfirmationGUIState.current_presentation, "paste_text", "")
                or getattr(
                    ConfirmationGUIState.current_presentation, "display_text", ""
                )
                or GPTState.text_to_confirm
            )
        else:
            text_to_set = GPTState.text_to_confirm or getattr(
                GPTState, "last_response", ""
            )

        if not text_to_set:
            notify("GPT error: No text in confirmation GUI to paste")
            # Clear any stale confirmation state even when nothing was pasted.
            GPTState.text_to_confirm = ""
            ConfirmationGUIState.current_presentation = None
            ConfirmationGUIState.display_thread = False
            ConfirmationGUIState.last_item_text = ""
            actions.user.confirmation_gui_close()
            return

        if settings.get("user.gpt_trace_confirmation_paste", 0):
            import contextlib
            import io
            import trace as _trace

            tracer = _trace.Trace(count=False, trace=True)
            buffer = io.StringIO()

            def _run():
                _confirmation_gui_paste_impl(text_to_set)

            try:
                with contextlib.redirect_stdout(buffer):
                    tracer.runfunc(_run)
            except Exception as exc:
                print(f"GPT trace warning: confirmation paste trace failed: {exc}")
                _confirmation_gui_paste_impl(text_to_set)
                return
            trace_output = buffer.getvalue()
            if trace_output:
                print(trace_output)
        else:
            _confirmation_gui_paste_impl(text_to_set)

    def confirmation_gui_refresh_thread(force_open: bool = False):
        """Refresh the threading output in the confirmation GUI"""
        if _reject_if_request_in_flight():
            return
        formatted_output = ""
        for msg in GPTState.thread:
            for item in msg["content"]:
                role = "GPT" if msg["role"] == "assistant" else "USER"
                output = f"{role}: {extract_message(item)}"
                # every 200 characters split the output into multiple lines
                formatted_output += (
                    "\n".join(output[i : i + 200] for i in range(0, len(output), 200))
                    + "\n"
                )

        GPTState.text_to_confirm = formatted_output
        ctx.tags = ["user.model_window_open"]
        if confirmation_gui.showing or force_open:
            confirmation_gui.show()
        ConfirmationGUIState.current_presentation = None
        ConfirmationGUIState.show_advanced_actions = False

    def confirmation_gui_open_pattern_menu_for_prompt():
        """Open the prompt pattern menu for the last static prompt, if available"""
        recipe = GPTState.last_recipe
        if not recipe:
            notify("GPT: No last recipe available to open a pattern menu for")
            return
        static_prompt = recipe.split(" · ", 1)[0].strip()
        if not static_prompt:
            notify("GPT: Could not determine a static prompt for the last recipe")
            return
        actions.user.prompt_pattern_gui_open_for_static_prompt(static_prompt)

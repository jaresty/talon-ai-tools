import textwrap

from typing import Optional, Union

from talon import Context, Module, actions, clip, imgui, settings

from .modelHelpers import GPTState, extract_message, notify
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

    if GPTState.last_recipe:
        gui.spacer()
        # Include the directional lens alongside the core recipe tokens so the
        # confirmation GUI matches quick help and other recap surfaces.
        if getattr(GPTState, "last_directional", ""):
            recipe_text = f"{GPTState.last_recipe} · {GPTState.last_directional}"
        else:
            recipe_text = GPTState.last_recipe
        gui.text(f"Recipe: {recipe_text}")
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
        if gui.button("Show grammar help"):
            actions.user.model_help_canvas_open_for_last_recipe()

        gui.spacer()
        if gui.button("Open pattern menu"):
            actions.user.confirmation_gui_open_pattern_menu_for_prompt()


@mod.action_class
class UserActions:
    def confirmation_gui_append(model_output: Union[str, ResponsePresentation]):
        """Add text to the confirmation surface (canvas-based viewer)"""
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
        ConfirmationGUIState.current_presentation = None
        ConfirmationGUIState.show_advanced_actions = False

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
            text_to_set = GPTState.text_to_confirm

        if not text_to_set:
            notify("GPT error: No text in confirmation GUI to paste")
        else:
            actions.user.paste(text_to_set)
            GPTState.last_response = text_to_set
            GPTState.last_was_pasted = True
        GPTState.text_to_confirm = ""
        actions.user.confirmation_gui_close()

    def confirmation_gui_refresh_thread(force_open: bool = False):
        """Refresh the threading output in the confirmation GUI"""

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

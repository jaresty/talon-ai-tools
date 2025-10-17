import textwrap

from typing import Optional, Union

from talon import Context, Module, actions, clip, imgui, settings

from .modelHelpers import GPTState, extract_message, notify
from .modelPresentation import ResponsePresentation

mod = Module()
ctx = Context()


class ConfirmationGUIState:
    display_thread = False
    last_item_text = ""
    current_presentation: Optional[ResponsePresentation] = None

    @classmethod
    def update(cls):
        cls.display_thread = (
            "USER" in GPTState.text_to_confirm and "GPT" in GPTState.text_to_confirm
        )
        if len(GPTState.thread) == 0:
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

    for paragraph in GPTState.text_to_confirm.split("\n"):
        for line in textwrap.wrap(
            paragraph, settings.get("user.model_window_char_width")
        ):
            gui.text(line)

    # gui.spacer()
    # if gui.button("Chain response"):
    #     actions.user.confirmation_gui_paste()
    #     actions.user.gpt_select_last()

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
    if gui.button("Copy response"):
        actions.user.confirmation_gui_copy()

    gui.spacer()
    if gui.button("Paste response"):
        actions.user.confirmation_gui_paste()

    gui.spacer()
    if gui.button("Open browser"):
        actions.user.confirmation_gui_open_browser()

    gui.spacer()
    if gui.button("Analyze prompt"):
        actions.user.confirmation_gui_analyze_prompt()

    gui.spacer()
    if gui.button("Discard response"):
        actions.user.confirmation_gui_close()


@mod.action_class
class UserActions:
    def confirmation_gui_append(model_output: Union[str, ResponsePresentation]):
        """Add text to the confirmation gui"""
        ctx.tags = ["user.model_window_open"]
        if isinstance(model_output, ResponsePresentation):
            ConfirmationGUIState.current_presentation = model_output
            GPTState.text_to_confirm = model_output.display_text
        else:
            ConfirmationGUIState.current_presentation = None
            GPTState.text_to_confirm = model_output
        confirmation_gui.show()

    def confirmation_gui_close():
        """Close the model output without pasting it"""
        GPTState.text_to_confirm = ""
        confirmation_gui.hide()
        ctx.tags = []
        ConfirmationGUIState.current_presentation = None

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

        text_to_set = (
            ConfirmationGUIState.current_presentation.paste_text
            if ConfirmationGUIState.current_presentation
            and not ConfirmationGUIState.display_thread
            else (
            GPTState.text_to_confirm
            if not ConfirmationGUIState.display_thread
            else ConfirmationGUIState.last_item_text
        ))

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

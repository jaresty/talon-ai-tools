from typing import List

from ..lib.modelTypes import GPTTextItem
from ..lib.modelConfirmationGUI import confirmation_gui
from talon import actions, clip, settings, ui
from ..lib.modelState import GPTState
from ..lib.modelHelpers import (
    messages_to_string,
    format_messages,
    notify,
)
from ..lib.HTMLBuilder import Builder
from ..lib.modelPresentation import ResponsePresentation, render_for_destination


class ModelDestination:
    def insert(self, gpt_message: List[GPTTextItem]):
        presentation = render_for_destination(gpt_message, "default")
        if presentation.open_browser:
            Browser().insert(gpt_message)
        else:
            GPTState.text_to_confirm = presentation.display_text
            actions.user.confirmation_gui_append(presentation.display_text)

    # If this isn't working, you may need to turn on dication for electron apps
    #  ui.apps(bundle="com.microsoft.VSCode")[0].element.AXManualAccessibility = True
    def inside_textarea(self):
        try:
            return ui.focused_element().get("AXRole") in [
                "AXTextArea",
                "AXTextField",
                "AXComboBox",
                "AXStaticText",
            ]
        except Exception as e:
            # Handle exception or log error
            print(f"An error occurred: {e}")
            return False


class Above(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)

        actions.key("left")
        actions.edit.line_insert_up()
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "above")
        actions.user.paste(presentation.paste_text)


class Chunked(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)

        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "chunked")
        lines = presentation.browser_lines
        for i in range(0, len(lines), 10):
            chunk = "\n".join(lines[i : i + 10])
            actions.user.paste(chunk)
            actions.key("enter")


class Below(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        actions.key("right")
        actions.edit.line_insert_down()
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "below")
        actions.user.paste(presentation.paste_text)


class Clipboard(ModelDestination):
    def insert(self, gpt_message):
        presentation = render_for_destination(gpt_message, "clipboard")
        clip.set_text(presentation.paste_text)


class Snip(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        presentation = render_for_destination(gpt_message, "snip")
        actions.user.insert_snippet(presentation.paste_text)


class Context(ModelDestination):
    def insert(self, gpt_message):
        for message in gpt_message:
            GPTState.push_context(message)


class Query(ModelDestination):
    def insert(self, gpt_message):
        GPTState.push_query(format_messages("user", gpt_message))


class NewContext(ModelDestination):
    def insert(self, gpt_message):
        GPTState.clear_context()
        for message in gpt_message:
            GPTState.push_context(message)


class AppendClipboard(ModelDestination):
    def insert(self, gpt_message):
        presentation = render_for_destination(gpt_message, "appendClipboard")
        if clip.text() is not None:
            clip.set_text(clip.text() + "\n" + presentation.paste_text)  # type: ignore
        else:
            clip.set_text(presentation.paste_text)


class Browser(ModelDestination):
    def insert(self, gpt_message):
        presentation = render_for_destination(gpt_message, "browser")
        builder = Builder()
        builder.h1("Talon GPT Result")
        for line in presentation.browser_lines:
            builder.p(line)
        builder.render()


class TextToSpeech(ModelDestination):
    def insert(self, gpt_message):
        try:
            presentation = render_for_destination(gpt_message, "tts")
            actions.user.tts(presentation.paste_text)
        except KeyError:
            notify("GPT Failure: text to speech is not installed")


class Chain(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "chain")
        actions.user.paste(presentation.paste_text)
        actions.user.gpt_select_last()


class Paste(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "paste")
        actions.user.paste(presentation.paste_text)

class Draft(ModelDestination):
    def insert(self, gpt_message):
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "draft")
        actions.user.draft_editor_open()
        actions.user.delete_all()
        actions.user.paste(presentation.paste_text)


class Typed(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        presentation = render_for_destination(gpt_message, "typed")
        actions.auto_insert(presentation.paste_text)


class Thread(ModelDestination):
    def insert(self, gpt_message):
        GPTState.push_thread(format_messages("user", gpt_message))
        actions.user.confirmation_gui_refresh_thread()


class NewThread(ModelDestination):
    def insert(self, gpt_message):
        GPTState.new_thread()
        GPTState.push_thread(format_messages("user", gpt_message))
        actions.user.confirmation_gui_refresh_thread()


class Stack(ModelDestination):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def insert(self, gpt_message):
        GPTState.append_stack(gpt_message, self.stack_name)


class Default(ModelDestination):
    def insert(self, gpt_message):
        presentation = render_for_destination(gpt_message, "default")
        if confirmation_gui.showing:
            GPTState.last_was_pasted = True
            actions.user.paste(presentation.paste_text)
        else:
            actions.user.confirmation_gui_append(presentation)


def create_model_destination(destination_type: str) -> ModelDestination:
    if destination_type == "":
        destination_type = settings.get("user.model_default_destination")
    destination_map = {
        "above": Above,
        "below": Below,
        "chunked": Chunked,
        "clipboard": Clipboard,
        "snip": Snip,
        "context": Context,
        "query": Query,
        "newContext": NewContext,
        "appendClipboard": AppendClipboard,
        "browser": Browser,
        "textToSpeech": TextToSpeech,
        "chain": Chain,
        "paste": Paste,
        "typed": Typed,
        "thread": Thread,
        "newThread": NewThread,
        "draft": Draft,
    }

    if destination_type == "window":
        return ModelDestination()

    destination_cls = destination_map.get(destination_type)
    if destination_cls is not None:
        return destination_cls()

    return Default()

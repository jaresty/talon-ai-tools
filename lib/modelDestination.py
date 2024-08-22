from ..lib.modelTypes import GPTTextItem
from ..lib.modelConfirmationGUI import confirmation_gui
from talon import actions, clip, settings, ui
from ..lib.modelState import GPTState
from ..lib.modelHelpers import (
    extract_message,
    format_messages,
    notify,
)
from ..lib.HTMLBuilder import Builder


class ModelDestination:
    def insert(self, gpt_message: GPTTextItem):
        extracted_message = extract_message(gpt_message)
        GPTState.text_to_confirm = extracted_message
        actions.user.confirmation_gui_append(extracted_message)

    def inside_textarea(self):
        try:
            return ui.focused_element().get("AXRole") in [
                "AXTextArea",
                "AXTextField",
                "AXComboBox",
                "AXStaticText",
            ]
        except Exception:
            # Handle exception or log error
            return False


class Above(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)

        actions.key("left")
        actions.edit.line_insert_up()
        GPTState.last_was_pasted = True
        extracted_message = extract_message(gpt_message)
        actions.user.paste(extracted_message)


class Below(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        actions.key("right")
        actions.edit.line_insert_down()
        GPTState.last_was_pasted = True
        extracted_message = extract_message(gpt_message)
        actions.user.paste(extracted_message)


class Clipboard(ModelDestination):
    def insert(self, gpt_message):
        extracted_message = extract_message(gpt_message)
        clip.set_text(extracted_message)


class Snip(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        extracted_message = extract_message(gpt_message)
        actions.user.insert_snippet(extracted_message)


class Context(ModelDestination):
    def insert(self, gpt_message):
        GPTState.push_context(gpt_message)


class NewContext(ModelDestination):
    def insert(self, gpt_message):
        GPTState.clear_context()
        GPTState.push_context(gpt_message)


class AppendClipboard(ModelDestination):
    def insert(self, gpt_message):
        extracted_message = extract_message(gpt_message)
        if clip.text() is not None:
            clip.set_text(clip.text() + "\n" + extracted_message)  # type: ignore
        else:
            clip.set_text(extracted_message)


class Browser(ModelDestination):
    def insert(self, gpt_message):
        builder = Builder()
        builder.h1("Talon GPT Result")
        extracted_message = extract_message(gpt_message)
        for line in extracted_message.split("\n"):
            builder.p(line)
        builder.render()


class TextToSpeech(ModelDestination):
    def insert(self, gpt_message):
        try:
            extracted_message = extract_message(gpt_message)
            actions.user.tts(extracted_message)
        except KeyError:
            notify("GPT Failure: text to speech is not installed")


class Chain(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        extracted_message = extract_message(gpt_message)
        actions.user.paste(extracted_message)
        actions.user.gpt_select_last()


class Paste(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        extracted_message = extract_message(gpt_message)
        actions.user.paste(extracted_message)


class Thread(ModelDestination):
    def insert(self, gpt_message):
        GPTState.push_thread(format_messages("user", [gpt_message]))
        actions.user.confirmation_gui_refresh_thread()


class NewThread(ModelDestination):
    def insert(self, gpt_message):
        GPTState.new_thread()
        GPTState.push_thread(format_messages("user", [gpt_message]))
        actions.user.confirmation_gui_refresh_thread()


class Default(ModelDestination):
    def insert(self, gpt_message):
        if confirmation_gui.showing:
            GPTState.last_was_pasted = True
            extracted_message = extract_message(gpt_message)
            actions.user.paste(extracted_message)
        else:
            pass


def create_model_destination(destination_type: str) -> ModelDestination:
    if destination_type == "":
        destination_type = settings.get("user.model_default_destination")
    match destination_type:
        case "above":
            return Above()
        case "below":
            return Below()
        case "clipboard":
            return Clipboard()
        case "snip":
            return Snip()
        case "context":
            return Context()
        case "newContext":
            return NewContext()
        case "appendClipboard":
            return AppendClipboard()
        case "browser":
            return Browser()
        case "textToSpeech":
            return TextToSpeech()
        case "window":
            return ModelDestination()
        case "chain":
            return Chain()
        case "paste":
            return Paste()
        case "thread":
            return Thread()
        case "newThread":
            return NewThread()
        case _:
            return Default()

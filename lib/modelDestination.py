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


class ModelDestination:
    def insert(self, gpt_message: list[GPTTextItem]):
        extracted_message = messages_to_string(gpt_message)
        if len(extracted_message.split("\n")) > 100:
            Browser().insert(gpt_message)
        else:
            GPTState.text_to_confirm = extracted_message
            actions.user.confirmation_gui_append(extracted_message)

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
        extracted_message = messages_to_string(gpt_message)
        actions.user.paste(extracted_message)


class Chunked(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)

        GPTState.last_was_pasted = True
        extracted_message = messages_to_string(gpt_message)
        lines = extracted_message.splitlines()
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
        extracted_message = messages_to_string(gpt_message)
        actions.user.paste(extracted_message)


class Clipboard(ModelDestination):
    def insert(self, gpt_message):
        extracted_message = messages_to_string(gpt_message)
        clip.set_text(extracted_message)


class Snip(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        extracted_message = messages_to_string(gpt_message)
        actions.user.insert_snippet(extracted_message)


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
        extracted_message = messages_to_string(gpt_message)
        if clip.text() is not None:
            clip.set_text(clip.text() + "\n" + extracted_message)  # type: ignore
        else:
            clip.set_text(extracted_message)


class Browser(ModelDestination):
    def insert(self, gpt_message):
        builder = Builder()
        builder.h1("Talon GPT Result")
        extracted_message = messages_to_string(gpt_message)
        for line in extracted_message.split("\n"):
            builder.p(line)
        builder.render()


class TextToSpeech(ModelDestination):
    def insert(self, gpt_message):
        try:
            extracted_message = messages_to_string(gpt_message)
            actions.user.tts(extracted_message)
        except KeyError:
            notify("GPT Failure: text to speech is not installed")


class Chain(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        extracted_message = messages_to_string(gpt_message)
        actions.user.paste(extracted_message)
        actions.user.gpt_select_last()


class Paste(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        extracted_message = messages_to_string(gpt_message)
        actions.user.paste(extracted_message)


class Typed(ModelDestination):
    def insert(self, gpt_message):
        if not self.inside_textarea():
            return super().insert(gpt_message)
        GPTState.last_was_pasted = True
        extracted_message = messages_to_string(gpt_message)
        actions.auto_insert(extracted_message)


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
        if confirmation_gui.showing:
            GPTState.last_was_pasted = True
            extracted_message = messages_to_string(gpt_message)
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
        case "chunked":
            return Chunked()
        case "clipboard":
            return Clipboard()
        case "snip":
            return Snip()
        case "context":
            return Context()
        case "query":
            return Query()
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
        case "typed":
            return Typed()
        case "thread":
            return Thread()
        case "newThread":
            return NewThread()
        case _:
            return Default()

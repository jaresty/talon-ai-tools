import base64
from ..lib.modelTypes import GPTImageItem, GPTTextItem
from ..lib.modelState import GPTState
from talon import actions, clip, settings
from ..lib.modelHelpers import (
    chats_to_string,
    format_message,
    messages_to_string,
    notify,
)


class ModelSource:
    def get_text(self):
        raise NotImplementedError("Subclasses should implement this method")

    def format_message(self) -> GPTImageItem | GPTTextItem | None:
        text = self.get_text()
        if text.strip() != "" and text:
            return format_message(text)


def format_source_messages(
    prompt: str, source: ModelSource, additional_source: ModelSource | None = None
):
    prompt_chunks = prompt.split("{additional_source}")
    source_message = source.format_message()
    additional_source_message = None
    if additional_source is not None:
        additional_source_message = additional_source.format_message()
    additional_source_messages: list[GPTImageItem | GPTTextItem] = []
    if additional_source_message is not None:
        if len(prompt_chunks) == 1:
            additional_source_messages = [
                format_message(
                    "This background information has been provided to help you answer the subsequent prompt"
                ),
                additional_source_message,
            ]
        else:
            additional_source_messages = [
                format_message(prompt_chunks.pop()),
                additional_source_message,
            ]
    else:
        if len(prompt_chunks) > 1:
            raise Exception(
                "Tried to use a prompt with an additional source message without providing an additional source"
            )
    return additional_source_messages + [
        format_message(prompt_chunks[0]),
        source_message,
    ]


class Clipboard(ModelSource):
    def get_text(self):
        return clip.text()

    def format_message(self) -> GPTImageItem | GPTTextItem | None:
        clipped_image = clip.image()

        if clipped_image:
            data = clipped_image.encode().data()
            base64_image = base64.b64encode(data).decode("utf-8")
            image_item: GPTImageItem = {
                "type": "image_url",
                "image_url": {"url": f"data:image/;base64,{base64_image}"},
            }
            return image_item
        return super().format_message()


class Context(ModelSource):
    def get_text(self):
        if GPTState.context == []:
            notify("GPT Failure: Context is empty")
            raise Exception(
                "GPT Failure: User requested context, but there was no context stored"
            )
        return messages_to_string(GPTState.context)


class Thread(ModelSource):
    def get_text(self):
        return chats_to_string(GPTState.thread)


class GPTResponse(ModelSource):
    def get_text(self):
        if GPTState.last_response == "":
            raise Exception(
                "GPT Failure: User requested GPT response, but there was no GPT response stored"
            )
        return GPTState.last_response


class GPTRequest(ModelSource):
    def get_text(self):
        return chats_to_string(GPTState.request["messages"])


class Style(ModelSource):
    def get_text(self):
        return "\n".join(GPTState.system_prompt.format_as_array())


class GPTExchange(ModelSource):
    def get_text(self):
        return (
            chats_to_string(GPTState.request["messages"])
            + "\n\nassistant\n\n"
            + GPTState.last_response
        )


class LastTalonDictation(ModelSource):
    def get_text(self):
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            return last_output
        else:
            notify("GPT Failure: No last dictation to reformat")
            raise Exception(
                "GPT Failure: User requested last Talon dictation, but there was no text to reformat"
            )


class SelectedText(ModelSource):
    def get_text(self):
        return actions.edit.selected_text()


def create_model_source(source_type: str) -> ModelSource:
    if source_type == "":
        source_type = settings.get("user.model_default_source")
    match source_type:
        case "clipboard":
            return Clipboard()
        case "context":
            return Context()
        case "thread":
            return Thread()
        case "style":
            return Style()
        case "gptResponse":
            return GPTResponse()
        case "gptRequest":
            return GPTRequest()
        case "gptExchange":
            return GPTExchange()
        case "lastTalonDictation":
            return LastTalonDictation()
        case "this" | _:
            return SelectedText()

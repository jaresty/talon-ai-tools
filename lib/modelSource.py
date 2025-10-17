import base64
from copy import deepcopy
from typing import List, Optional, Union

from ..lib.modelTypes import GPTImageItem, GPTTextItem
from ..lib.modelState import GPTState
from talon import actions, clip, settings
from ..lib.modelHelpers import (
    chats_to_string,
    format_message,
    messages_to_string,
    notify,
)


GPTItem = Union[GPTImageItem, GPTTextItem]


class ModelSource:
    def get_text(self):
        raise NotImplementedError("Subclasses should implement this method")

    def format_message(self) -> GPTItem:
        text = self.get_text()
        return format_message(text)

    def format_messages(self) -> List[GPTItem]:
        return [self.format_message()]


def format_source_messages(
    prompt: str, source: ModelSource, additional_source: Optional[ModelSource] = None
):
    prompt_chunks = prompt.split("{additional_source}")
    source_messages = source.format_messages()
    additional_source_messages: List[GPTItem] = []
    if additional_source is not None:
        additional_source_messages = additional_source.format_messages()
        if len(prompt_chunks) == 1:
            additional_source_messages = [
                format_message(
                    "## This is the secondary content; if the prompt has a direction consider this to be to the left, origin, or history\n"
                )
            ] + additional_source_messages

        else:
            additional_source_messages = [
                format_message(prompt_chunks.pop())
            ] + additional_source_messages

    else:
        if len(prompt_chunks) > 1:
            raise Exception(
                "Tried to use a prompt with an additional source message without providing an additional source"
            )
    current_request: List[GPTItem] = [
        format_message("# Prompt\n"),
        format_message(prompt_chunks[0]),
        format_message("\n\n## This is the primary content; if the prompt has a direction consider this to be to the right, destination, or future\n"),
    ]
    current_request += source_messages
    return additional_source_messages + current_request


class Clipboard(ModelSource):
    def get_text(self):
        return clip.text()

    def format_message(self) -> GPTItem:
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

    def format_messages(self) -> List[GPTItem]:
        return deepcopy(GPTState.context)


class Thread(ModelSource):
    def get_text(self):
        return chats_to_string(GPTState.thread)


class SourceStack(ModelSource):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def get_text(self):
        return messages_to_string(GPTState.stacks[self.stack_name] or [])

    def format_messages(self) -> List[GPTItem]:
        return deepcopy(GPTState.stacks[self.stack_name] or [])


class CompoundSource(ModelSource):
    def __init__(self, model_sources: List[ModelSource]):
        self.model_sources = model_sources

    def get_text(self):
        return messages_to_string(self.format_messages())

    def format_messages(self) -> List[GPTItem]:
        aggregated_messages: List[GPTItem] = []

        for source in self.model_sources:
            messages = source.format_messages()
            aggregated_messages.extend(messages)

        return aggregated_messages


class Query(ModelSource):
    def get_text(self):
        return chats_to_string(GPTState.query)


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


class AllText(ModelSource):
    def get_text(self):
        actions.edit.select_all()
        return actions.edit.selected_text()


def create_model_source(source_type: str) -> ModelSource:
    if source_type == "":
        source_type = settings.get("user.model_default_source")
    source_map = {
        "clipboard": Clipboard,
        "context": Context,
        "query": Query,
        "thread": Thread,
        "style": Style,
        "gptResponse": GPTResponse,
        "gptRequest": GPTRequest,
        "gptExchange": GPTExchange,
        "lastTalonDictation": LastTalonDictation,
        "all": AllText,
    }

    source_cls = source_map.get(source_type)
    if source_cls is not None:
        return source_cls()

    return SelectedText()

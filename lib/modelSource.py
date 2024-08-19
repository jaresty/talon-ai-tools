from ..lib.modelState import GPTState
from talon import actions, clip, settings
from ..lib.modelHelpers import (
    chats_to_string,
    messages_to_string,
    notify,
)


class ModelSource:
    def get_text(self):
        raise NotImplementedError("Subclasses should implement this method")


class Clipboard(ModelSource):
    def get_text(self):
        return clip.text()


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

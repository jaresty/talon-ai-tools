import os

from ..lib.talonSettings import ApplyPromptConfiguration, PassConfiguration

from ..lib.modelDestination import Browser, Default, ModelDestination
from ..lib.modelSource import ModelSource, create_model_source, format_source_messages
from talon import Module, actions, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    append_request_messages,
    build_request,
    extract_message,
    format_message,
    format_messages,
    notify,
    send_request,
)
from ..lib.modelState import GPTState
from ..lib.modelTypes import GPTSystemPrompt, GPTTextItem

mod = Module()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)


def gpt_query():
    """Send a prompt to the GPT API and return the response"""

    # Reset state before pasting
    GPTState.last_was_pasted = False

    response = send_request()
    return response


@mod.action_class
class UserActions:
    def gpt_start_debug():
        """Enable debug logging"""
        GPTState.start_debug()

    def gpt_stop_debug():
        """Disable debug logging"""
        GPTState.stop_debug()

    def gpt_clear_context():
        """Reset the stored context"""
        GPTState.clear_context()

    def gpt_clear_stack(stack_name: str):
        """Reset the stored stack"""
        GPTState.clear_stack(stack_name)

    def gpt_clear_query():
        """Reset the stored query"""
        GPTState.clear_query()

    def gpt_clear_all():
        """Reset all state"""
        GPTState.clear_all()

    def gpt_clear_thread():
        """Create a new thread"""
        GPTState.new_thread()
        actions.user.confirmation_gui_refresh_thread()

    def gpt_enable_threading():
        """Enable threading of subsequent requests"""
        GPTState.enable_thread()

    def gpt_disable_threading():
        """Enable threading of subsequent requests"""
        GPTState.disable_thread()

    def gpt_push_context(context: str):
        """Add the selected text to the stored context"""
        GPTState.push_context(format_message(context))

    def gpt_push_query(query: str):
        """Add the selected text to the stored context"""
        GPTState.push_query(format_messages("user", [format_message(query)]))

    def gpt_push_thread(content: str):
        """Add the selected text to the active thread"""
        GPTState.push_thread(format_messages("user", [format_message(content)]))

    def gpt_additional_user_context() -> list[str]:
        """This is an override function that can be used to add additional context to the prompt"""
        return []

    def gpt_set_system_prompt(
        modelVoice: str,
        modelAudience: str,
        modelPurpose: str,
        modelTone: str,
    ) -> None:
        """Set the system prompt to be used when the LLM responds to you"""
        if modelVoice == "":
            modelVoice = GPTState.system_prompt.voice
        if modelAudience == "":
            modelAudience = GPTState.system_prompt.audience
        if modelTone == "":
            modelTone = GPTState.system_prompt.tone
        if modelPurpose == "":
            modelPurpose = GPTState.system_prompt.purpose
        new_system_prompt = GPTSystemPrompt(
            voice=modelVoice,
            audience=modelAudience,
            purpose=modelPurpose,
            tone=modelTone,
        )
        GPTState.system_prompt = new_system_prompt

    def gpt_reset_system_prompt():
        """Reset the system prompt to default"""
        GPTState.system_prompt = GPTSystemPrompt()

    def gpt_select_last() -> None:
        """select all the text in the last GPT output"""
        if not GPTState.last_was_pasted:
            notify("Tried to select GPT output, but it was not pasted in an editor")
            return

        lines = GPTState.last_response.split("\n")
        for _ in lines[:-1]:
            actions.edit.extend_up()
        actions.edit.extend_line_end()
        for _ in lines[0]:
            actions.edit.extend_left()

    def gpt_apply_prompt(apply_prompt_configuration: ApplyPromptConfiguration):
        """Apply an arbitrary prompt to arbitrary text"""
        prompt = apply_prompt_configuration.please_prompt
        source = apply_prompt_configuration.model_source
        additional_source = apply_prompt_configuration.additional_model_source
        destination = apply_prompt_configuration.model_destination

        actions.user.gpt_prepare_message(source, additional_source, prompt, "")
        response = gpt_query()

        actions.user.gpt_insert_response([response], destination)
        return response

    def gpt_run_prompt(
        prompt: str,
        source: ModelSource,
        additional_source: ModelSource = create_model_source(
            settings.get("user.model_default_source")
        ),
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        response = actions.user.gpt_prepare_message(
            source, additional_source, prompt, ""
        )
        response = gpt_query()

        return response.get("text")

    def gpt_analyze_prompt(destination: ModelDestination = Default()):
        """Explain why we got the results we did"""
        PROMPT = "Analyze the provided prompt and response. Explain how the prompt was understood to generate the given response. Provide only the explanation."

        append_request_messages(
            [format_messages("assistant", [format_message(GPTState.last_response)])]
        )
        append_request_messages([format_messages("user", [format_message(PROMPT)])])
        response = gpt_query()

        actions.user.gpt_insert_response(response, destination)

    def gpt_replay(destination: str):
        """Replay the last request"""
        response = gpt_query()

        actions.user.gpt_insert_response(response, destination)

    def gpt_pass(pass_configuration: PassConfiguration) -> None:
        """Passes a response from source to destination"""
        source: ModelSource = pass_configuration.model_source
        destination: ModelDestination = pass_configuration.model_destination
        actions.user.gpt_insert_response(source.format_messages(), destination)

    def gpt_help() -> None:
        """Open the GPT help file in the web browser"""
        # get the text from the file and open it in the web browser
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "lists", "staticPrompt.talon-list")
        with open(file_path, "r") as f:
            lines = f.readlines()[2:]

        builder = Builder()
        builder.h1("Talon GPT Prompt List")
        for line in lines:
            if "##" in line:
                builder.h2(line)
            else:
                builder.p(line)

        builder.render()

    def gpt_reformat_last(how_to_reformat: str) -> str:
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            actions.user.gpt_prepare_message("last", PROMPT, "")
            return extract_message(gpt_query())
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def gpt_insert_text(text: str, destination: ModelDestination = Default()) -> None:
        """Insert text using the helpers here"""
        actions.user.gpt_insert_response([format_message(text)], destination)

    def gpt_open_browser(text: str) -> None:
        """Open a browser with the response"""
        actions.user.gpt_insert_response([format_message(text)], Browser())

    def gpt_search_engine(search_engine: str, source: ModelSource) -> str:
        """Format the source for searching with a search engine and open a search"""

        prompt = f"""
        I want to search for the following using the {search_engine} search engine.
        Format the text into a succinct search to help me find what I'm looking for. Return only the text of the search query.
        Optimize the search for returning good search results leaving off anything that would not be useful in searching.
        Rather than searching for exact strings, I want to find a search that is as close as possible.
        I will take care of putting it into a search.
        """
        return actions.user.gpt_run_prompt(prompt, source)

    def gpt_insert_response(
        gpt_message: list[GPTTextItem],
        destination: ModelDestination = Default(),
    ) -> None:
        """Insert a GPT result in a specified way"""
        destination.insert(gpt_message)

    def gpt_get_source_text(spoken_text: str) -> str:
        """Get the source text that is will have the prompt applied to it"""
        return create_model_source(spoken_text).get_text()

    def gpt_prepare_message(
        model_source: ModelSource,
        additional_model_source: ModelSource,
        prompt: str,
        destination: ModelDestination = Default(),
    ) -> None:
        """Get the source text that will have the prompt applied to it"""

        if type(additional_model_source) is type(model_source):
            additional_model_source = create_model_source(
                settings.get("user.model_default_source")
            )

        build_request(destination)

        current_messages = format_source_messages(
            prompt,
            model_source,
            additional_model_source,
        )

        # Iterate over all of the system prompt messages and format them as messages
        system_prompt_messages: list[GPTTextItem] = []
        for message in GPTState.system_prompt.format_as_array():
            system_prompt_messages.append(format_message(message))
        append_request_messages([format_messages("system", system_prompt_messages)])
        append_request_messages(GPTState.query)

        current_request = format_messages(
            "user",
            current_messages,
        )
        if GPTState.thread_enabled:
            GPTState.push_thread(current_request)
        append_request_messages([current_request])

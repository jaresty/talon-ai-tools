import os

from ..lib.modelDestination import create_model_destination
from ..lib.modelSource import create_model_source, format_source_messages
from talon import Module, actions

from ..lib.HTMLBuilder import Builder
from ..lib.modelConfirmationGUI import confirmation_gui
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

    def gpt_push_thread(content: str):
        """Add the selected text to the active thread"""
        GPTState.push_thread(format_messages("user", [format_message(content)]))

    def gpt_additional_user_context() -> list[str]:
        """This is an override function that can be used to add additional context to the prompt"""
        return []

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

    def gpt_apply_prompt(
        prompt: str,
        source: str = "",
        additional_source: str = "",
        destination: str = "",
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        actions.user.gpt_prepare_message(source, additional_source, prompt, "")
        response = gpt_query()

        actions.user.gpt_insert_response(response, destination)
        return response

    def gpt_run_prompt(prompt: str, source: str = "", additional_source: str = ""):
        """Apply an arbitrary prompt to arbitrary text"""

        response = actions.user.gpt_prepare_message(
            source, additional_source, prompt, ""
        )
        response = gpt_query()

        return response.get("text")

    def gpt_analyze_prompt(destination: str):
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

    def gpt_pass(source: str = "", destination: str = "") -> None:
        """Passes a response from source to destination"""
        actions.user.gpt_insert_response(
            create_model_source(source).format_message(), destination
        )

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

    def gpt_insert_text(text: str, method: str = "") -> None:
        """Insert text using the helpers here"""
        actions.user.gpt_insert_response(format_message(text), method)

    def gpt_reset_system_prompt():
        """Reset the system prompt to default"""
        GPTState.system_prompt = GPTSystemPrompt()

    def gpt_insert_response(
        gpt_message: GPTTextItem,
        method: str = "",
    ) -> None:
        """Insert a GPT result in a specified way"""

        # If threading is enabled, and the window is open, refresh the confirmation GUI
        # unless the user explicitly wanted to pass the result to the window without viewing the rest of the thread
        if (
            GPTState.thread_enabled
            and confirmation_gui.showing
            and not method == "window"
            # If they ask for thread or newThread specifically,
            # it should be pushed to the thread and not just refreshed
            and not method == "thread"
            and not method == "newThread"
        ):
            # Skip inserting the response if the user is just viewing the thread in the window
            actions.user.confirmation_gui_refresh_thread()
            return

        create_model_destination(method).insert(gpt_message)

    def gpt_get_source_text(spoken_text: str) -> str:
        """Get the source text that is will have the prompt applied to it"""
        return create_model_source(spoken_text).get_text()

    def gpt_prepare_message(
        spoken_text: str,
        additional_source: str,
        prompt: str,
        destination: str = "",
    ) -> None:
        """Get the source text that will have the prompt applied to it"""
        build_request(destination)
        if spoken_text == additional_source:
            current_messages = format_source_messages(
                prompt,
                create_model_source(spoken_text),
            )
        else:
            additional_model_source = create_model_source(additional_source)
            current_messages = format_source_messages(
                prompt,
                create_model_source(spoken_text),
                additional_model_source,
            )
            if len(current_messages) < 4 and additional_model_source is not None:
                additional_source_message = additional_model_source.format_message()
                if additional_source_message is not None:
                    append_request_messages(
                        [format_messages("system", [additional_source_message])]
                    )

        # Iterate over all of the system prompt messages and format them as messages
        print("system prompt", GPTState.system_prompt.format_as_array())
        system_prompt_messages: list[GPTTextItem] = []
        for message in GPTState.system_prompt.format_as_array():
            system_prompt_messages.append(format_message(message))
        append_request_messages([format_messages("system", system_prompt_messages)])

        current_request = format_messages(
            "user",
            current_messages,
        )
        if GPTState.thread_enabled:
            GPTState.push_thread(current_request)
        append_request_messages([current_request])

import os
from typing import Optional

from ..lib.talonSettings import (
    ApplyPromptConfiguration,
    DEFAULT_COMPLETENESS_VALUE,
    PassConfiguration,
)
from ..lib.staticPromptConfig import STATIC_PROMPT_CONFIG

from ..lib.modelDestination import Browser, Default, ModelDestination, PromptPayload
from ..lib.modelSource import ModelSource, create_model_source
from talon import Module, actions, clip, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    format_message,
    format_messages,
    notify,
    send_request,
)
from ..lib.modelState import GPTState
from ..lib.modelTypes import GPTSystemPrompt
from ..lib.promptPipeline import PromptPipeline, PromptResult
from ..lib.promptSession import PromptSession
from ..lib.recursiveOrchestrator import RecursiveOrchestrator

mod = Module()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)


_prompt_pipeline = PromptPipeline()
_recursive_orchestrator = RecursiveOrchestrator(_prompt_pipeline)


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

    def gpt_tools() -> str:
        """This is an override function that will provide all of the tools available for tool calls as a JSON string"""
        return "[]"

    def gpt_call_tool(tool_name: str, parameters: str) -> str:
        """This will call the tool by name and return a string of the tool call results"""
        return ""

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
        # Also reset contract-style defaults so "reset writing" is a single
        # switch for persona and writing behaviour.
        settings.set("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        settings.set("user.model_default_scope", "")
        settings.set("user.model_default_method", "")
        settings.set("user.model_default_style", "")

    def gpt_set_default_completeness(level: str) -> None:
        """Set the default completeness level for subsequent prompts"""
        settings.set("user.model_default_completeness", level)
        GPTState.user_overrode_completeness = True

    def gpt_set_default_scope(level: str) -> None:
        """Set the default scope level for subsequent prompts"""
        settings.set("user.model_default_scope", level)
        GPTState.user_overrode_scope = True

    def gpt_set_default_method(level: str) -> None:
        """Set the default method for subsequent prompts"""
        settings.set("user.model_default_method", level)
        GPTState.user_overrode_method = True

    def gpt_set_default_style(level: str) -> None:
        """Set the default style for subsequent prompts"""
        settings.set("user.model_default_style", level)
        GPTState.user_overrode_style = True

    def gpt_reset_default_completeness() -> None:
        """Reset the default completeness level to its configured base value"""
        settings.set("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        GPTState.user_overrode_completeness = False

    def gpt_reset_default_scope() -> None:
        """Reset the default scope level to its configured base value"""
        settings.set("user.model_default_scope", "")
        GPTState.user_overrode_scope = False

    def gpt_reset_default_method() -> None:
        """Reset the default method to its configured base value (no strong default)"""
        settings.set("user.model_default_method", "")
        GPTState.user_overrode_method = False

    def gpt_reset_default_style() -> None:
        """Reset the default style to its configured base value (no strong default)"""
        settings.set("user.model_default_style", "")
        GPTState.user_overrode_style = False

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
        # If the pattern picker GUI is open, close it when any model prompt runs
        # so voice-triggered patterns and regular grammar both dismiss it.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        # Also close the prompt-specific pattern picker if it is open.
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass

        prompt = apply_prompt_configuration.please_prompt
        source = apply_prompt_configuration.model_source
        additional_source = apply_prompt_configuration.additional_model_source
        destination = apply_prompt_configuration.model_destination

        result = _recursive_orchestrator.run(
            prompt,
            source,
            destination,
            additional_source,
        )

        actions.user.gpt_insert_response(result, destination)
        return result.text

    def gpt_run_prompt(
        prompt: str,
        source: ModelSource,
        additional_source: Optional[ModelSource] = None,
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        result = _prompt_pipeline.run(
            prompt,
            source,
            destination="",
            additional_source=additional_source,
        )

        return result.text

    def gpt_recursive_prompt(
        prompt: str,
        source: ModelSource,
        destination: ModelDestination = Default(),
        additional_source: Optional[ModelSource] = None,
    ) -> str:
        """Run a controller prompt that may recursively delegate work to sub-sessions."""

        result = _recursive_orchestrator.run(
            prompt,
            source,
            destination,
            additional_source,
        )

        actions.user.gpt_insert_response(result, destination)
        return result.text

    def gpt_analyze_prompt(destination: ModelDestination = ModelDestination()):
        """Explain why we got the results we did"""
        PROMPT = "Analyze the provided prompt and response. Explain how the prompt was understood to generate the given response. Provide only the explanation."

        if not GPTState.last_response:
            notify("GPT Failure: No response available to analyze")
            return

        session = PromptSession(destination)
        session.begin(reuse_existing=True)
        session.add_messages(
            [
                format_messages(
                    "assistant", [format_message(GPTState.last_response)]
                ),
                format_messages("user", [format_message(PROMPT)]),
            ]
        )
        result = _prompt_pipeline.complete(session)

        actions.user.gpt_insert_response(result, destination)

    def gpt_replay(destination: str):
        """Replay the last request"""
        session = PromptSession(destination)
        session.begin(reuse_existing=True)
        result = _prompt_pipeline.complete(session)

        actions.user.gpt_insert_response(result, destination)

    def gpt_show_last_recipe() -> None:
        """Show a short summary of the last prompt recipe"""
        recipe = GPTState.last_recipe
        if not recipe:
            notify("GPT: No last recipe available")
            return
        actions.app.notify(f"Last recipe: {recipe}")

    def gpt_pass(pass_configuration: PassConfiguration) -> None:
        """Passes a response from source to destination"""
        source: ModelSource = pass_configuration.model_source
        destination: ModelDestination = pass_configuration.model_destination

        session = PromptSession(destination)
        session.begin(reuse_existing=True)

        result = PromptResult.from_messages(source.format_messages())

        actions.user.gpt_insert_response(result, destination)

    def gpt_help() -> None:
        """Open the GPT help file in the web browser"""
        # Build a consolidated, scannable help page from all related lists
        current_dir = os.path.dirname(__file__)
        lists_dir = os.path.join(current_dir, "lists")

        def read_list_lines(name: str) -> list[str]:
            path = os.path.join(lists_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    # Skip the first two lines (talon list header convention)
                    return f.readlines()[2:]
            except FileNotFoundError:
                return []

        def render_list_as_tables(
            title: str,
            filename: str,
            builder: Builder,
            comment_mode: str = "section_headers",  # "section_headers", "preceding_description", or "static_prompts"
            description_overrides: Optional[dict[str, str]] = None,
        ) -> None:
            lines = read_list_lines(filename)
            if not lines:
                return

            builder.h2(title)

            table_open = False
            last_comment_block: list[str] = []
            last_was_blank = True

            def ensure_table_open():
                nonlocal table_open
                if not table_open:
                    builder.start_table(["Trigger", "Description"])
                    table_open = True

            def close_table_if_open():
                nonlocal table_open
                if table_open:
                    builder.end_table()
                    table_open = False

            for raw in lines:
                line = raw.strip()
                if not line:
                    # keep spacing logical but avoid empty rows
                    last_was_blank = True
                    continue
                if line.startswith("#"):
                    # Comments: either section headers or descriptions depending on mode
                    header = line.lstrip("# ")
                    if comment_mode == "preceding_description":
                        # accumulate consecutive comment lines for the next key:value
                        if header:
                            last_comment_block.append(header)
                    elif comment_mode == "static_prompts":
                        # In static prompts, treat trailing-period comments as
                        # descriptions, and other comments that follow a blank
                        # line as section headers; remaining comments attach to
                        # the next key as descriptions.
                        if header.endswith("."):
                            if header:
                                last_comment_block.append(header)
                        elif last_was_blank and not last_comment_block:
                            close_table_if_open()
                            if header:
                                builder.h3(header)
                        else:
                            if header:
                                last_comment_block.append(header)
                    else:
                        close_table_if_open()
                        if header:
                            builder.h3(header)
                    last_was_blank = False
                    continue

                # Parse key: value rows (e.g., "emoji: Return only emoji.")
                if ":" in line:
                    parts = line.split(":", 1)
                    key = parts[0].strip()
                    if comment_mode in ("preceding_description", "static_prompts"):
                        # Use accumulated comment(s) as description; fall back to inline text if none
                        desc = " ".join(last_comment_block).strip() or parts[1].strip()
                        last_comment_block = []
                    else:
                        desc = parts[1].strip()
                    if description_overrides and key in description_overrides:
                        desc = description_overrides[key]
                    if key or desc:
                        ensure_table_open()
                        builder.add_row([key, desc])
                    last_was_blank = False

            close_table_if_open()

        builder = Builder()
        builder.title("Talon GPT Reference")
        builder.h1("Talon GPT Reference")

        builder.p(
            "Use modifiers after a static prompt to control completeness, method, "
            "scope, and style. You normally say at most one or two modifiers per call."
        )

        builder.h2("How to use the helpers (ADR 006)")
        builder.ul(
            "Patterns: say 'model patterns' (or 'model coding patterns' / 'model writing patterns') and click a pattern or say its name (for example, 'debug bug') to run a curated recipe.",
            "Prompt pattern menu: say 'model pattern menu <prompt>' (for example, 'model pattern menu describe') to see a few generic recipes for that static prompt; click or say 'quick gist', 'deep narrow rigor', or 'bulleted summary' while the menu is open.",
            "Recap: after running a model command, check the confirmation window's 'Recipe:' line, or say 'model last recipe' to see the last combination in a notification.",
            "Grammar help: say 'model quick help' for an overview, or 'model show grammar' to see the last recipe and an exact 'model …' line you can repeat or adapt.",
            "From the confirmation window, use 'Show grammar help' or 'Open pattern menu' buttons to quickly inspect or tweak what you just ran.",
        )

        builder.h2("Replaced prompts (ADR 007)")
        builder.ul(
            "`simple` → use `describe` with `gist` + `plain` (or the “Simplify locally” pattern).",
            "`short` → use `describe` with `gist` + `tight` (or the “Tighten summary” pattern).",
            "`how to` / `incremental` → use `todo` or `bridge` with `steps` + `checklist`/`minimal` (or the “Extract todos” pattern).",
        )

        # Order for easy scanning with Cmd-F
        # Static prompts prefer descriptions from STATIC_PROMPT_CONFIG so there
        # is a single source of truth, while section headers in the Talon list
        # still provide visual groupings in the help.
        render_list_as_tables(
            "Static Prompts",
            "staticPrompt.talon-list",
            builder,
            comment_mode="static_prompts",
            description_overrides={
                key: cfg["description"]
                for key, cfg in STATIC_PROMPT_CONFIG.items()
                if cfg.get("description")
            },
        )
        render_list_as_tables("Directional Modifiers", "directionalModifier.talon-list", builder)
        render_list_as_tables("Completeness Modifiers", "completenessModifier.talon-list", builder)
        render_list_as_tables("Scope Modifiers", "scopeModifier.talon-list", builder)
        render_list_as_tables("Method Modifiers", "methodModifier.talon-list", builder)
        render_list_as_tables("Style Modifiers", "styleModifier.talon-list", builder)
        render_list_as_tables("Goal Modifiers", "goalModifier.talon-list", builder)
        render_list_as_tables("Voice", "modelVoice.talon-list", builder)
        render_list_as_tables("Tone", "modelTone.talon-list", builder)
        render_list_as_tables("Audience", "modelAudience.talon-list", builder)
        render_list_as_tables("Purpose", "modelPurpose.talon-list", builder)
        # For Sources/Destinations, descriptions live in the preceding comment lines
        render_list_as_tables("Sources", "modelSource.talon-list", builder, comment_mode="preceding_description")
        render_list_as_tables("Destinations", "modelDestination.talon-list", builder, comment_mode="preceding_description")

        builder.h2("Default settings examples")
        builder.ul(
            "Set defaults: 'model set completeness skim', 'model set scope narrow', "
            "'model set method steps', 'model set style bullets'.",
            "Reset defaults: 'model reset writing' (persona + all defaults), or "
            "'model reset completeness', 'model reset scope', 'model reset method', "
            "'model reset style'.",
        )

        builder.render()

    def gpt_reformat_last(how_to_reformat: str) -> str:
        """Reformat the last model output"""
        PROMPT = f"""The last phrase was written using voice dictation. It has an error with spelling, grammar, or just general misrecognition due to a lack of context. Please reformat the following text to correct the error with the context that it was {how_to_reformat}."""
        last_output = actions.user.get_last_phrase()
        if last_output:
            actions.user.clear_last_phrase()
            source = create_model_source("last")
            result = _prompt_pipeline.run(PROMPT, source, Default())
            return result.text
        else:
            notify("No text to reformat")
            raise Exception("No text to reformat")

    def gpt_insert_text(text: str, destination: ModelDestination = Default()) -> None:
        """Insert text using the helpers here"""
        result = PromptResult.from_messages([format_message(text)])
        actions.user.gpt_insert_response(result, destination)

    def gpt_open_browser(text: str) -> None:
        """Open a browser with the response"""
        result = PromptResult.from_messages([format_message(text)])
        actions.user.gpt_insert_response(result, Browser())

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
        gpt_result: PromptPayload,
        destination: ModelDestination = Default(),
    ) -> None:
        """Insert a GPT result in a specified way"""
        actions.user.confirmation_gui_close()
        destination.insert(gpt_result)

    def gpt_get_source_text(spoken_text: str) -> str:
        """Get the source text that is will have the prompt applied to it"""
        return create_model_source(spoken_text).get_text()

    def gpt_prepare_message(
        model_source: ModelSource,
        additional_model_source: Optional[ModelSource],
        prompt: str,
        destination: ModelDestination = Default(),
    ) -> PromptSession:
        """Get the source text that will have the prompt applied to it"""

        session = PromptSession(destination)
        session.prepare_prompt(prompt, model_source, additional_model_source)
        return session

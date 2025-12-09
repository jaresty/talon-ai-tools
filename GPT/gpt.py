import os
import threading
from typing import Optional

from ..lib.talonSettings import (
    ApplyPromptConfiguration,
    DEFAULT_COMPLETENESS_VALUE,
    PassConfiguration,
    _axis_recipe_token,
    _axis_string_to_tokens,
    _axis_tokens_to_string,
    _canonicalise_axis_tokens,
    modelPrompt,
)

from ..lib.staticPromptConfig import STATIC_PROMPT_CONFIG

try:
    from ..lib.staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile
except ImportError:  # Talon may have a stale staticPromptConfig loaded
    def get_static_prompt_profile(name: str):
        return STATIC_PROMPT_CONFIG.get(name)

    def get_static_prompt_axes(name: str) -> dict[str, object]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, object] = {}
        for axis in ("completeness", "scope", "method", "style"):
            value = profile.get(axis)
            if value:
                if axis == "completeness":
                    axes[axis] = str(value)
                else:
                    if isinstance(value, list):
                        tokens = [str(v).strip() for v in value if str(v).strip()]
                    else:
                        tokens = [str(value).strip()]
                    if tokens:
                        axes[axis] = tokens
        return axes

from ..lib.modelDestination import (
    Browser,
    Clipboard,
    Default,
    ModelDestination,
    PromptPayload,
    Silent,
    create_model_destination,
)
from ..lib.modelSource import ModelSource, create_model_source
from talon import Module, actions, clip, settings

from ..lib.HTMLBuilder import Builder
from ..lib.modelHelpers import (
    format_message,
    format_messages,
    notify,
    send_request,
    messages_to_string,
)
from ..lib.modelState import GPTState
from ..lib.modelTypes import GPTSystemPrompt
from ..lib.promptPipeline import PromptPipeline, PromptResult
from ..lib.promptSession import PromptSession
from ..lib.recursiveOrchestrator import RecursiveOrchestrator
from ..lib.modelPatternGUI import (
    _axis_value as _axis_value_from_token,
    COMPLETENESS_MAP as _COMPLETENESS_MAP,
    SCOPE_MAP as _SCOPE_MAP,
    METHOD_MAP as _METHOD_MAP,
    STYLE_MAP as _STYLE_MAP,
    DIRECTIONAL_MAP as _DIRECTIONAL_MAP,
)
# Backward-compatible alias for directional map used during parsing.
DIRECTIONAL_MAP = _DIRECTIONAL_MAP
from ..lib.requestState import RequestPhase
from ..lib.requestBus import (
    emit_begin_send,
    emit_cancel,
    emit_complete,
    emit_fail,
    current_state,
    set_controller,
)
from ..lib.requestController import RequestUIController

# Ensure a default request UI controller is registered so cancel events have a sink.
try:
    from ..lib import requestUI  # noqa: F401
except Exception:
    pass


def _set_setting(key: str, value) -> None:
    """Best-effort setter for Talon settings across runtimes."""
    try:
        if hasattr(settings, "set"):
            settings.set(key, value)
            return
    except Exception:
        pass
    try:
        settings[key] = value
    except Exception:
        pass

mod = Module()
mod.tag(
    "model_window_open",
    desc="Tag for enabling the model window commands when the window is open",
)


_prompt_pipeline = PromptPipeline()
_recursive_orchestrator = RecursiveOrchestrator(_prompt_pipeline)
ASYNC_BLOCKING_SETTING = "user.model_async_blocking"


def _read_list_items(filename: str) -> list[tuple[str, str]]:
    """Read (key, description) pairs from a Talon list file in GPT/lists."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.join(current_dir, "lists")
    path = os.path.join(lists_dir, filename)
    items: list[tuple[str, str]] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                items.append((key.strip(), value.strip()))
    except FileNotFoundError:
        return []
    return items


def _await_handle_and_insert(handle, destination: str) -> None:
    """Wait on an async handle and insert the response when ready (background)."""
    def _runner():
        try:
            handle.wait(timeout=None)
        except Exception:
            pass
        result = getattr(handle, "result", None)
        if result is None:
            notify("GPT: Async run produced no result")
            return
        try:
            actions.user.gpt_insert_response(result, destination)
        except Exception:
            notify("GPT: Failed to insert async result")

    threading.Thread(target=_runner, daemon=True).start()


def _handle_async_result(handle, destination: str, block: bool = True) -> None:
    """Insert async result, either blocking or via background wait."""
    if block:
        try:
            handle.wait(timeout=None)
        except Exception:
            pass
        result = getattr(handle, "result", None)
        if result is None:
            notify("GPT: Async run produced no result")
            return
        try:
            actions.user.gpt_insert_response(result, destination)
        except Exception:
            notify("GPT: Failed to insert async result")
        return
    # Non-blocking path: background wait and insert.
    _await_handle_and_insert(handle, destination)


def _build_axis_docs() -> str:
    """Build a text block describing all axis and directional modifiers."""
    sections = [
        ("Completeness modifiers", "completenessModifier.talon-list"),
        ("Scope modifiers", "scopeModifier.talon-list"),
        ("Method modifiers", "methodModifier.talon-list"),
        ("Style modifiers", "styleModifier.talon-list"),
        ("Directional modifiers", "directionalModifier.talon-list"),
    ]
    lines: list[str] = [
        "Note: Axes capture how and in what shape the model should respond (completeness, scope, method, style, directional lens). "
        "For full semantics and examples, see ADR 005/012/013/016 and the GPT README axis cheat sheet.\n"
    ]
    for label, filename in sections:
        items = _read_list_items(filename)
        if not items:
            continue
        lines.append(f"{label}:")
        for key, desc in items:
            lines.append(f"- {key}: {desc}")
        lines.append("")
    return "\n".join(lines).rstrip()


def _build_static_prompt_docs() -> str:
    """Build a text block describing static prompts and their semantics."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.join(current_dir, "lists")
    path = os.path.join(lists_dir, "staticPrompt.talon-list")
    # Prefer descriptions from STATIC_PROMPT_CONFIG, and include default axes
    # when present; fall back to listing other prompts by name.
    lines: list[str] = [
        "Note: Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging, Slack/Jira formatting, taxonomy-style outputs) now live only as style/method axis values rather than static prompts; see ADR 012/013 and the README cheat sheet for axis-based recipes.\n"
    ]
    seen: set[str] = set()

    # First, profiled prompts with rich descriptions.
    for name in STATIC_PROMPT_CONFIG.keys():
        profile = get_static_prompt_profile(name)
        if profile is None:
            continue
        description = profile.get("description", "").strip()
        if not description:
            continue
        axes_bits: list[str] = []
        for label in ("completeness", "scope", "method", "style"):
            value = get_static_prompt_axes(name).get(label)
            if not value:
                continue
            if isinstance(value, list):
                rendered = " ".join(str(v) for v in value)
            else:
                rendered = str(value)
            if rendered:
                axes_bits.append(f"{label}={rendered}")
        if axes_bits:
            lines.append(
                f"- {name}: {description} (defaults: {', '.join(axes_bits)})"
            )
        else:
            lines.append(f"- {name}: {description}")
        seen.add(name)

    # Then, any remaining static prompts from the list so the model sees the
    # full token vocabulary.
    other_prompts: list[str] = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" not in line:
                    continue
                key, _ = line.split(":", 1)
                key = key.strip()
                if key and key not in seen:
                    other_prompts.append(key)
                    seen.add(key)
    except FileNotFoundError:
        pass

    if other_prompts:
        lines.append(
            "- Other static prompts (tokens only; see docs for semantics): "
            + ", ".join(sorted(other_prompts))
        )

    return "\n".join(lines)


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

    def gpt_copy_last_raw_exchange() -> None:
        """Copy the last raw GPT request/response JSON to the clipboard for debugging."""
        try:
            data = {
                "request": getattr(GPTState, "last_raw_request", {}) or {},
                "response": getattr(GPTState, "last_raw_response", {}) or {},
            }
        except Exception:
            data = {"request": {}, "response": {}}

        if not data["request"] and not data["response"]:
            notify("GPT debug: No last raw exchange available to copy")
            return

        try:
            import json as _json

            pretty = _json.dumps(data, indent=2, sort_keys=True)
        except Exception:
            # Fallback: best-effort string representation.
            pretty = str(data)

        clip.set_text(pretty)
        notify("GPT debug: Copied last raw request/response JSON to clipboard")

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
        _set_setting("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        _set_setting("user.model_default_scope", "")
        _set_setting("user.model_default_method", "")
        _set_setting("user.model_default_style", "")

    def gpt_set_default_completeness(level: str) -> None:
        """Set the default completeness level for subsequent prompts"""
        token = _axis_recipe_token("completeness", level)
        _set_setting("user.model_default_completeness", token)
        GPTState.user_overrode_completeness = True

    def gpt_set_default_scope(level: str) -> None:
        """Set the default scope level for subsequent prompts"""
        token = _axis_recipe_token("scope", level)
        _set_setting("user.model_default_scope", token)
        GPTState.user_overrode_scope = True

    def gpt_set_default_method(level: str) -> None:
        """Set the default method for subsequent prompts"""
        token = _axis_recipe_token("method", level)
        _set_setting("user.model_default_method", token)
        GPTState.user_overrode_method = True

    def gpt_set_default_style(level: str) -> None:
        """Set the default style for subsequent prompts"""
        token = _axis_recipe_token("style", level)
        _set_setting("user.model_default_style", token)
        GPTState.user_overrode_style = True

    def gpt_set_async_blocking(enabled: int) -> None:
        """Toggle async blocking mode for model runs (1=blocking, 0=non-blocking)"""
        _set_setting(ASYNC_BLOCKING_SETTING, bool(enabled))
        mode = "blocking" if enabled else "non-blocking"
        actions.app.notify(f"GPT: async mode set to {mode}")

    def gpt_reset_default_completeness() -> None:
        """Reset the default completeness level to its configured base value"""
        _set_setting("user.model_default_completeness", DEFAULT_COMPLETENESS_VALUE)
        GPTState.user_overrode_completeness = False

    def gpt_reset_default_scope() -> None:
        """Reset the default scope level to its configured base value"""
        _set_setting("user.model_default_scope", "")
        GPTState.user_overrode_scope = False

    def gpt_reset_default_method() -> None:
        """Reset the default method to its configured base value (no strong default)"""
        _set_setting("user.model_default_method", "")
        GPTState.user_overrode_method = False

    def gpt_reset_default_style() -> None:
        """Reset the default style to its configured base value (no strong default)"""
        _set_setting("user.model_default_style", "")
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
        # Close the response viewer at the start of a new run so it disappears
        # immediately (for example, when using `model again`) and will be
        # reopened with the fresh answer once the pipeline completes.
        try:
            actions.user.model_response_canvas_close()
        except Exception:
            pass
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
        # Close the suggestion picker as well so executing a prompt always
        # leaves at most one model window visible.
        try:
            actions.user.model_prompt_recipe_suggestions_gui_close()
        except Exception:
            pass
        # Close the Help Hub to avoid overlapping overlays during runs.
        try:
            actions.user.help_hub_close()
        except Exception:
            pass

        prompt = apply_prompt_configuration.please_prompt
        source = apply_prompt_configuration.model_source
        additional_source = apply_prompt_configuration.additional_model_source
        destination = apply_prompt_configuration.model_destination

        # Snapshot the primary source messages so plain `model again` can reuse
        # the same content even if the live source has changed.
        try:
            GPTState.last_source_messages = source.format_messages()
        except Exception:
            GPTState.last_source_messages = []

        result = None
        async_started = False
        raw_block = settings.get("user.model_async_blocking", False)
        block = False if raw_block is None else bool(raw_block)
        # Prefer async orchestrator path; optionally block for result.
        if hasattr(_recursive_orchestrator, "run_async"):
            try:
                handle = _recursive_orchestrator.run_async(
                    prompt,
                    source,
                    destination,
                    additional_source,
                )
                async_started = True
                _handle_async_result(handle, destination, block=block)
                result = getattr(handle, "result", None)
            except Exception:
                async_started = False
                result = None
        if result is None and not async_started:
            result = _recursive_orchestrator.run(
                prompt,
                source,
                destination,
                additional_source,
            )

        if result is not None:
            actions.user.gpt_insert_response(result, destination)
            return result.text
        # Non-blocking async path returns early; insertion handled in background.
        return ""

    def gpt_run_prompt(
        prompt: str,
        source: ModelSource,
        additional_source: Optional[ModelSource] = None,
    ):
        """Apply an arbitrary prompt to arbitrary text"""

        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)

        try:
            handle = _prompt_pipeline.run_async(
                prompt,
                source,
                destination="",
                additional_source=additional_source,
            )
            async_started = True
            _handle_async_result(handle, destination="", block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _prompt_pipeline.run(
                prompt,
                source,
                destination="",
                additional_source=additional_source,
            )

        if result is not None:
            return result.text
        return ""

    def gpt_recursive_prompt(
        prompt: str,
        source: ModelSource,
        destination: ModelDestination = Default(),
        additional_source: Optional[ModelSource] = None,
    ) -> str:
        """Run a controller prompt that may recursively delegate work to sub-sessions."""

        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)
        try:
            handle = _recursive_orchestrator.run_async(
                prompt,
                source,
                destination,
                additional_source,
            )
            async_started = True
            _handle_async_result(handle, destination, block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _recursive_orchestrator.run(
                prompt,
                source,
                destination,
                additional_source,
            )

        if result is not None:
            actions.user.gpt_insert_response(result, destination)
            return result.text if hasattr(result, "text") else str(getattr(result, "text", ""))  # type: ignore[arg-type]
        # Non-blocking async path returns early; insertion handled in background.
        return ""

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
        result = None
        async_started = False
        raw_block = settings.get(ASYNC_BLOCKING_SETTING, False)
        block = False if raw_block is None else bool(raw_block)
        try:
            handle = _prompt_pipeline.complete_async(session)
            async_started = True
            _handle_async_result(handle, destination, block=block)
            result = getattr(handle, "result", None)
        except Exception:
            async_started = False
            result = None

        if result is None and not async_started:
            result = _prompt_pipeline.complete(session)

        if result is not None:
            actions.user.gpt_insert_response(result, destination)

    def gpt_suggest_prompt_recipes(subject: str) -> None:
        """Suggest model prompt recipes using the default source."""
        source = create_model_source(settings.get("user.model_default_source"))
        UserActions.gpt_suggest_prompt_recipes_with_source(source, subject)

    def gpt_suggest_prompt_recipes_with_source(
        source: ModelSource, subject: str
    ) -> None:
        """Suggest model prompt recipes for an explicit source."""
        # When debug logging is enabled, surface details about how `model suggest`
        # resolved its source so users can diagnose unexpected content.
        if GPTState.debug_enabled:
            try:
                default_source_key = settings.get("user.model_default_source")
            except Exception:
                default_source_key = "<error>"
            resolved_source_key = getattr(source, "modelSimpleSource", "")
            notify(
                "GPT debug: model suggest using "
                f"default_source={default_source_key!r}, "
                f"resolved_source={resolved_source_key!r}, "
                f"source_class={source.__class__.__name__}"
            )

        try:
            content = source.get_text()
        except Exception:
            # Underlying helpers (for example, Context/GPTResponse) already
            # notify the user when no content is available. Clear any cached
            # suggestions so the GUI doesn't appear to reflect stale content.
            GPTState.last_suggested_recipes = []
            GPTState.last_suggest_source = ""
            return

        # Remember the canonical source key used for these suggestions so the
        # suggestion GUI can both display and reuse it when running recipes.
        source_key = getattr(source, "modelSimpleSource", "")
        if isinstance(source_key, str) and source_key:
            GPTState.last_suggest_source = source_key
        else:
            GPTState.last_suggest_source = ""

        subject = subject or ""
        content_text = str(content)
        if GPTState.debug_enabled:
            preview = content_text[:200].replace("\n", "\\n")
            notify(
                "GPT debug: model suggest content length="
                f"{len(content_text)}, preview={preview!r}"
            )

        if not content_text.strip() and not subject.strip():
            # If we have neither source content nor a subject, clear previous
            # suggestions to avoid showing stale recipes in the GUI.
            GPTState.last_suggested_recipes = []
            GPTState.last_suggest_source = ""
            notify("GPT: No source or subject available for suggestions")
            return

        axis_docs = _build_axis_docs()
        static_prompt_docs = _build_static_prompt_docs()
        prompt_subject = subject.strip() if subject else "unspecified"
        user_text = (
            "You are a prompt recipe assistant for the Talon `model` command.\n"
            "Based on the subject and content below, suggest 3–5 concrete prompt recipes.\n\n"
            "For each recipe, output exactly one line in this format:\n"
            "Name: <short human-friendly name> | Recipe: <staticPrompt> · <completeness> · <scopeTokens> · <methodTokens> · <styleTokens> · <directional>\n\n"
            "Where:\n"
            "- <staticPrompt> is exactly one static prompt token (do not include multiple static prompts or combine them).\n"
            "- <completeness> and <directional> are single axis tokens.\n"
            "- Directional is required: always include exactly one directional modifier from the directional list; never leave it blank.\n"
            "- <scopeTokens>, <methodTokens>, and <styleTokens> are zero or more space-separated axis tokens for that axis (respecting small caps: scope ≤ 2 tokens, method ≤ 3 tokens, style ≤ 3 tokens).\n"
            "Examples of multi-tag fields: scopeTokens='actions edges', methodTokens='structure flow', styleTokens='jira story'.\n\n"
            "Use only tokens from the following sets where possible.\n"
            "Axis semantics and available tokens:\n"
            f"{axis_docs}\n\n"
            "Static prompts and their semantics:\n"
            f"{static_prompt_docs}\n\n"
            f"Subject: {prompt_subject}\n\n"
            "Content:\n"
            f"{content_text}\n"
        )

        # Run suggestions through a silent destination so we never open the
        # confirmation surface for this helper. Keep a clipboard fallback to
        # expose the raw output without popping UI if parsing/GUI fails.
        destination = Silent()
        fallback_destination = Clipboard()
        session = PromptSession(destination)
        # Always emit UI lifecycle events so the pill shows even when the
        # pipeline is swapped out or does not drive the request bus.
        manual_request_id: Optional[str] = None
        try:
            manual_request_id = emit_begin_send()
        except Exception:
            manual_request_id = None
        # Suppress response canvas while suggestions are running so streaming
        # text never opens the confirmation viewer.
        prev_suppress = getattr(GPTState, "suppress_response_canvas", False)
        GPTState.suppress_response_canvas = True
        result = None
        # Start a fresh request for suggestions so we don't accidentally
        # reuse the previous GPTState.request (for example, from the last
        # `model` call). This avoids leaking prior prompt content into
        # the suggestion meta-prompt.
        try:
            session.begin()
            session.add_messages([format_messages("user", [format_message(user_text)])])
            try:
                handle = _prompt_pipeline.complete_async(session)
                handle.wait(timeout=10.0)
                result = getattr(handle, "result", None)
            except Exception:
                result = None
            if result is None:
                result = _prompt_pipeline.complete(session)
            if manual_request_id is not None:
                try:
                    emit_complete(request_id=manual_request_id)
                except Exception:
                    pass
        except Exception as exc:
            if manual_request_id is not None:
                try:
                    emit_fail(str(exc), request_id=manual_request_id)
                except Exception:
                    pass
            raise
        finally:
            try:
                GPTState.suppress_response_canvas = prev_suppress
            except Exception:
                pass

        # Attempt to parse the result text into structured suggestions so
        # future loops (for example, a suggestions GUI) can reuse them
        # without re-calling the model.
        suggestions: list[dict[str, str]] = []
        for raw_line in result.text.splitlines():
            line = raw_line.strip()
            if not line or "|" not in line:
                continue
            try:
                name_part, recipe_part = line.split("|", 1)
            except ValueError:
                continue
            if "Recipe:" not in recipe_part:
                continue
            # Allow both "Name: <label>" and bare labels before the pipe.
            if "Name:" in name_part:
                _, name_value = name_part.split("Name:", 1)
                name = name_value.strip()
            else:
                name = name_part.strip().strip(":")
            # Always require an explicit Recipe: label for the second half.
            _, recipe_value = recipe_part.split("Recipe:", 1)
            recipe_value = recipe_value.strip()
            if not name:
                continue
            # Enforce a single static prompt token by collapsing any
            # space-delimited static prompt segment to its first token.
            recipe_tokens = [t.strip() for t in recipe_value.split("·") if t.strip()]
            if not recipe_tokens:
                continue
            static_tokens = recipe_tokens[0].split()
            if len(static_tokens) > 1:
                recipe_tokens[0] = static_tokens[0]
            # Require a directional token (last segment); drop if missing.
            raw_directional = recipe_tokens[-1] if len(recipe_tokens) > 1 else ""
            dir_tokens = raw_directional.split()
            if len(dir_tokens) != 1:
                continue
            directional = dir_tokens[0]
            if directional not in _DIRECTIONAL_MAP:
                continue
            recipe_tokens[-1] = directional
            recipe = " · ".join(recipe_tokens)
            suggestions.append({"name": name, "recipe": recipe})
        GPTState.last_suggested_recipes = suggestions

        if suggestions:
            try:
                actions.user.model_prompt_recipe_suggestions_gui_open()
                # When the suggestion GUI opens successfully, we do not also
                # open the confirmation GUI; the picker becomes the primary
                # surface for these recipes.
            except Exception:
                # If the GUI is not available for any reason, still insert the
                # raw suggestions so the feature remains usable.
                actions.user.gpt_insert_response(result, fallback_destination)
        else:
            # If we didn't recognise any suggestions, fall back to the normal
            # insertion flow so the user can still see the raw output.
            actions.user.gpt_insert_response(result, fallback_destination)

    def gpt_replay(destination: str):
        """Replay the last request"""
        session = PromptSession(destination)
        session.begin(reuse_existing=True)
        result_handle = _prompt_pipeline.complete_async(session)
        raw_block = settings.get("user.model_async_blocking", False)
        block = False if raw_block is None else bool(raw_block)
        _handle_async_result(result_handle, destination, block=block)

    def gpt_show_last_recipe() -> None:
        """Show a short summary of the last prompt recipe"""
        recipe = GPTState.last_recipe
        if not recipe:
            notify("GPT: No last recipe available")
            return
        directional = getattr(GPTState, "last_directional", "")
        if directional:
            recipe_text = f"{recipe} · {directional}"
        else:
            recipe_text = recipe
        actions.app.notify(f"Last recipe: {recipe_text}")

    def gpt_show_last_meta() -> None:
        """Show the last meta-interpretation, if available."""
        meta = getattr(GPTState, "last_meta", "")
        if not meta.strip():
            actions.app.notify("GPT: No last meta interpretation available")
            return
        actions.app.notify(f"Last meta interpretation:\n{meta}")

    def gpt_cancel_request() -> None:
        """Best-effort cancel for in-flight model requests (UI + state only)."""
        # Ensure the bus has a controller so the cancel event updates state/UX.
        try:
            if current_state().phase == RequestPhase.IDLE:
                set_controller(RequestUIController())
        except Exception:
            set_controller(RequestUIController())
        try:
            from ..lib.modelHelpers import cancel_active_request

            cancel_active_request()
        except Exception:
            pass
        emit_cancel()
        notify("GPT: Cancel requested")

    def gpt_rerun_last_recipe(
        static_prompt: str,
        completeness: str,
        scope: str,
        method: str,
        style: str,
        directional: str,
    ) -> None:
        """Rerun the last prompt recipe with optional axis overrides, using the last or default source."""
        # Close the main confirmation window so the rerun does not briefly
        # show a mismatched recipe/response pair while state updates.
        try:
            actions.user.confirmation_gui_close()
        except Exception:
            pass

        if not GPTState.last_recipe:
            notify("GPT: No last recipe available to rerun")
            return

        base_static = getattr(GPTState, "last_static_prompt", "") or ""
        base_completeness = getattr(GPTState, "last_completeness", "") or ""
        base_scope = getattr(GPTState, "last_scope", "") or ""
        base_method = getattr(GPTState, "last_method", "") or ""
        base_style = getattr(GPTState, "last_style", "") or ""
        base_directional = getattr(GPTState, "last_directional", "") or ""

        new_static = static_prompt or base_static

        # Completeness remains scalar; overrides simply replace the base when
        # provided.
        new_completeness = completeness or base_completeness

        # Scope/method/style may conceptually be multi-valued. We treat
        # last_* values as already-serialised canonical sets and merge any
        # override tokens via the shared normaliser.
        base_scope_tokens = _axis_string_to_tokens(base_scope)
        override_scope_tokens = _axis_string_to_tokens(scope)
        merged_scope_tokens = _canonicalise_axis_tokens(
            "scope", base_scope_tokens + override_scope_tokens
        )
        new_scope = _axis_tokens_to_string(merged_scope_tokens)

        base_method_tokens = _axis_string_to_tokens(base_method)
        override_method_tokens = _axis_string_to_tokens(method)
        merged_method_tokens = _canonicalise_axis_tokens(
            "method", base_method_tokens + override_method_tokens
        )
        new_method = _axis_tokens_to_string(merged_method_tokens)

        base_style_tokens = _axis_string_to_tokens(base_style)
        override_style_tokens = _axis_string_to_tokens(style)
        merged_style_tokens = _canonicalise_axis_tokens(
            "style", base_style_tokens + override_style_tokens
        )
        new_style = _axis_tokens_to_string(merged_style_tokens)

        # If normalisation dropped axis tokens (due to caps or
        # incompatibilities), surface a short, non-modal hint so users can
        # see what changed.
        def _axis_drop_summary(
            axis_name: str,
            base_tokens: list[str],
            override_tokens: list[str],
            merged_tokens: list[str],
        ) -> str:
            original_tokens = [t for t in base_tokens + override_tokens if t]
            if not original_tokens:
                return ""
            original_set = set(original_tokens)
            merged_set = set(merged_tokens)
            if not original_set or original_set == merged_set:
                return ""
            original_str = " ".join(original_tokens)
            merged_str = " ".join(merged_tokens) if merged_tokens else "(none)"
            return f"{axis_name}={original_str} \u2192 {merged_str}"

        axis_drop_parts: list[str] = []
        for axis_name, base_tokens, override_tokens, merged_tokens in (
            ("scope", base_scope_tokens, override_scope_tokens, merged_scope_tokens),
            ("method", base_method_tokens, override_method_tokens, merged_method_tokens),
            ("style", base_style_tokens, override_style_tokens, merged_style_tokens),
        ):
            summary = _axis_drop_summary(axis_name, base_tokens, override_tokens, merged_tokens)
            if summary:
                axis_drop_parts.append(summary)

        if axis_drop_parts:
            notify(
                "GPT: Axes normalised (caps/incompatibilities); "
                + "; ".join(axis_drop_parts)
            )

        new_directional = directional or base_directional

        if not new_static:
            notify("GPT: Last recipe is not available to rerun")
            return

        # Build a lightweight object with the attributes expected by modelPrompt.
        class Match:
            pass

        match = Match()
        setattr(match, "staticPrompt", new_static)
        if new_completeness:
            setattr(
                match,
                "completenessModifier",
                _axis_value_from_token(new_completeness, _COMPLETENESS_MAP),
            )
        if new_scope:
            setattr(
                match,
                "scopeModifier",
                _axis_value_from_token(new_scope, _SCOPE_MAP),
            )
        if new_method:
            setattr(
                match,
                "methodModifier",
                _axis_value_from_token(new_method, _METHOD_MAP),
            )
        if new_style:
            setattr(
                match,
                "styleModifier",
                _axis_value_from_token(new_style, _STYLE_MAP),
            )
        if new_directional:
            setattr(
                match,
                "directionalModifier",
                _axis_value_from_token(new_directional, _DIRECTIONAL_MAP),
            )

        # Keep GPTState.last_recipe and structured fields in sync with the
        # effective recipe for this rerun.
        recipe_parts = [new_static]
        for token in (new_completeness, new_scope, new_method, new_style):
            if token:
                recipe_parts.append(token)
        GPTState.last_recipe = " · ".join(recipe_parts)
        GPTState.last_static_prompt = new_static
        GPTState.last_completeness = new_completeness or ""
        GPTState.last_scope = new_scope or ""
        GPTState.last_method = new_method or ""
        GPTState.last_style = new_style or ""
        GPTState.last_directional = new_directional or ""

        please_prompt = modelPrompt(match)

        # Resolve the source for this rerun:
        # - Prefer a cached snapshot of the last primary source messages so
        #   plain `model again` reuses the same content even if the live
        #   source (clipboard/selection/etc.) has changed.
        # - Fallback to the live default source when we have no snapshot.
        cached_messages = getattr(GPTState, "last_source_messages", [])
        if cached_messages:
            from copy import deepcopy

            class CachedSource(ModelSource):
                def __init__(self, messages):
                    self._messages = list(messages)

                def get_text(self):
                    return messages_to_string(self._messages)

                def format_messages(self):
                    return deepcopy(self._messages)

            source: ModelSource = CachedSource(cached_messages)
        else:
            source_key = getattr(GPTState, "last_again_source", "") or settings.get(
                "user.model_default_source"
            )
            source = create_model_source(source_key)

        config = ApplyPromptConfiguration(
            please_prompt=please_prompt,
            model_source=source,
            additional_model_source=None,
            model_destination=create_model_destination(
                settings.get("user.model_default_destination")
            ),
        )

        actions.user.gpt_apply_prompt(config)

    def gpt_rerun_last_recipe_with_source(
        source: ModelSource,
        static_prompt: str,
        completeness: str,
        scope: str,
        method: str,
        style: str,
        directional: str,
    ) -> None:
        """Rerun the last prompt recipe for an explicit source with optional axis overrides."""
        # Remember this source key for subsequent plain `model again` calls.
        source_key = getattr(source, "modelSimpleSource", None)
        if isinstance(source_key, str) and source_key:
            GPTState.last_again_source = source_key
        # Delegate to the default-source variant, which will resolve the
        # actual ModelSource from the stored key and apply the same axis logic.
        UserActions.gpt_rerun_last_recipe(
            static_prompt,
            completeness,
            scope,
            method,
            style,
            directional,
        )

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
        try:
            text = getattr(gpt_result, "text", "") or ""
            if isinstance(text, str) and not text.strip():
                actions.app.notify("GPT: Request cancelled")
                return
        except Exception:
            pass
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

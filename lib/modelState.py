from typing import ClassVar, Dict, List, Union

from talon import actions

from .modelTypes import (
    GPTImageItem,
    GPTMessage,
    GPTRequest,
    GPTSystemPrompt,
    GPTTextItem,
)


class GPTState:
    text_to_confirm: ClassVar[str] = ""
    last_response: ClassVar[str] = ""
    current_provider_id: ClassVar[str] = "openai"
    request_provider: ClassVar[object] = None
    # Optional meta-interpretation for the last response, when available.
    last_meta: ClassVar[str] = ""
    # Snapshot of the current streaming run (if any) so UI surfaces can render
    # progress and status via the streamingCoordinator façade.
    last_streaming_snapshot: ClassVar[Dict[str, object]] = {}
    # Last destination kind (for example, "window", "default", "paste") so UI
    # surfaces can tailor progress affordances per destination.
    current_destination_kind: ClassVar[str] = ""
    last_was_pasted: ClassVar[bool] = False
    # Human-readable summary of the last prompt recipe
    # (static prompt + effective completeness/scope/method/form/channel).
    last_recipe: ClassVar[str] = ""
    # Short token for the last directional lens (for example, "fog").
    last_directional: ClassVar[str] = ""
    # Structured fields for the last recipe. These are stored as short
    # tokens so they can be reused by shorthand grammars such as `model again`.
    # Scope and method may contain multiple tokens serialized as whitespace-
    # separated sets. External consumers that read these fields must treat
    # them as sets rather than assuming a single scalar token.
    last_static_prompt: ClassVar[str] = ""
    last_completeness: ClassVar[str] = ""
    last_scope: ClassVar[str] = ""
    last_method: ClassVar[str] = ""
    last_form: ClassVar[str] = ""
    last_channel: ClassVar[str] = ""
    # Authoritative axis tokens per ADR 034/048: completeness (scalar token),
    # scope/method/form/channel/directional as token lists.
    last_axes: ClassVar[Dict[str, List[str]]] = {
        "completeness": [],
        "scope": [],
        "method": [],
        "form": [],
        "channel": [],
        "directional": [],
    }
    # Snapshot of the primary source messages used for the last model run
    # so `model again` can reuse the same content even if the live source
    # (for example, clipboard or selection) has changed.
    last_source_messages: ClassVar[List[Union[GPTTextItem, GPTImageItem]]] = []
    # Last canonical source key used for the most recent run (for example, "clipboard", "context").
    last_source_key: ClassVar[str] = ""
    # Last explicit source key used with `model again` (for example, "clip", "this").
    last_again_source: ClassVar[str] = ""
    # Last source key used when generating prompt recipe suggestions, stored
    # as the canonical model source token (for example, "clipboard", "context").
    last_suggest_source: ClassVar[str] = ""
    # Last set of prompt recipe suggestions, if any, as a list of
    # {"name": ..., "recipe": ...} dictionaries derived from `model suggest`.
    last_suggested_recipes: ClassVar[List[Dict[str, str]]] = []
    # Snapshot of stance/default axes sent with the last suggest request so
    # the suggestion UI can surface the context used for generation.
    last_suggest_context: ClassVar[Dict[str, str]] = {}
    # Last subject string provided to `model suggest`, so we can rerun with
    # updated stance/intent without re-entering the subject.
    last_suggest_subject: ClassVar[str] = ""
    # Cached content text for the last suggest call to avoid re-reading sources.
    last_suggest_content: ClassVar[str] = ""
    # Last composed prompt text sent to the model (Task/Constraints/Directional).
    last_prompt_text: ClassVar[str] = ""
    context: ClassVar[List[Union[GPTTextItem, GPTImageItem]]] = []
    query: ClassVar[List[GPTMessage]] = []
    # Last fully constructed request envelope sent to the model so sources
    # like GPTRequest/GPTExchange can reference it safely.
    request: ClassVar[GPTRequest] = {
        "messages": [],
        "max_completion_tokens": 0,
        "tools": [],
        "reasoning_effort": "",
        "n": 1,
        "model": "",
        "tool_choice": "auto",
        "verbosity": "",
    }
    # Track whether the user has intentionally overridden per-axis defaults via
    # settings so that per-prompt profiles do not compete with user intent.
    user_overrode_completeness: ClassVar[bool] = False
    user_overrode_scope: ClassVar[bool] = False
    user_overrode_method: ClassVar[bool] = False
    user_overrode_form: ClassVar[bool] = False
    user_overrode_channel: ClassVar[bool] = False
    thread: ClassVar[List[GPTMessage]] = []
    tools = []
    stacks: ClassVar[Dict[str, List[Union[GPTTextItem, GPTImageItem]]]] = {}
    thread_enabled: ClassVar[bool] = False
    debug_enabled: ClassVar[bool] = False
    # Raw HTTP request/response payloads for the last model call, useful for
    # debugging or copying logs.
    last_raw_request: ClassVar[Dict] = {}
    last_raw_response: ClassVar[Dict] = {}
    system_prompt: ClassVar[GPTSystemPrompt] = GPTSystemPrompt()
    # Path to the most recently saved history source file (if any).
    last_history_save_path: ClassVar[str] = ""
    # When True, confirmation_gui_close should avoid closing the response canvas.
    suppress_response_canvas_close: ClassVar[bool] = False

    @classmethod
    def start_debug(cls):
        """Enable debug printing"""
        GPTState.debug_enabled = True
        actions.app.notify("Enabled debug logging")

    @classmethod
    def stop_debug(cls):
        """Disable debug printing"""
        GPTState.debug_enabled = False
        actions.app.notify("Disabled debug logging")

    @classmethod
    def clear_context(cls):
        """Reset the stored context"""
        cls.context = []
        actions.app.notify("Cleared user context")

    @classmethod
    def clear_query(cls):
        """Reset the stored query"""
        cls.query = []
        actions.app.notify("Cleared user query")

    @classmethod
    def clear_all(cls):
        """Reset all state"""
        cls.context = []
        cls.thread = []
        cls.query = []
        cls.stacks = {}
        cls.last_response = ""
        cls.last_meta = ""
        cls.last_was_pasted = False
        cls.last_recipe = ""
        cls.last_directional = ""
        cls.last_static_prompt = ""
        cls.last_completeness = ""
        cls.last_scope = ""
        cls.last_method = ""
        cls.last_form = ""
        cls.last_channel = ""
        cls.last_source_messages = []
        cls.last_source_key = ""
        cls.last_again_source = ""
        cls.last_suggest_source = ""
        cls.last_suggested_recipes = []
        cls.last_suggest_context = {}
        cls.last_prompt_text = ""
        cls.context = []
        cls.query = []
        cls.thread = []
        cls.user_overrode_completeness = False
        cls.user_overrode_scope = False
        cls.user_overrode_method = False
        cls.user_overrode_form = False
        cls.user_overrode_channel = False
        cls.last_raw_request = {}
        cls.last_raw_response = {}
        cls.last_axes = {
            "completeness": [],
            "scope": [],
            "method": [],
            "form": [],
            "channel": [],
            "directional": [],
        }
        cls.request["messages"] = []
        cls.request_provider = None
        cls.current_provider_id = "openai"
        actions.app.notify("Cleared all state")

    @classmethod
    def new_thread(cls):
        """Create a new thread"""
        cls.thread = []
        actions.app.notify("Created a new thread")

    @classmethod
    def append_stack(
        cls,
        message: List[Union[GPTTextItem, GPTImageItem]],
        stack: str,
    ):
        """Append a message to a stack"""
        if stack not in cls.stacks:
            cls.stacks[stack] = []
        cls.stacks[stack] += message
        actions.app.notify(f"Appended message to stack {stack}")

    @classmethod
    def new_stack(cls, message: List[Union[GPTTextItem, GPTImageItem]], stack: str):
        """Append a message to a new stack"""
        cls.stacks[stack] = []
        cls.stacks[stack] += message
        actions.app.notify(f"Appended message to stack {stack}")

    @classmethod
    def clear_stack(cls, stack: str):
        """Append a message to a stack"""
        cls.stacks[stack] = []
        actions.app.notify(f"Cleared stack {stack}")

    @classmethod
    def enable_thread(cls):
        """Enable threading"""
        cls.thread_enabled = True
        actions.app.notify("Enabled threading")

    @classmethod
    def disable_thread(cls):
        """Disable threading"""
        cls.thread_enabled = False
        actions.app.notify("Disabled threading")

    @classmethod
    def push_context(cls, context: GPTTextItem):
        """Add the selected text to the stored context"""
        if context.get("type") != "text":
            actions.app.notify(
                "Only text can be added to context. To add images, try using a prompt to summarize or otherwise describe the image to the context."
            )
            return
        cls.context += [context]
        actions.app.notify("Appended system context")

    @classmethod
    def push_query(cls, query: GPTMessage):
        """Add the selected item to the stored query"""
        query_message = query.get("content")[0]

        if query_message is None:
            actions.app.notify(
                "Tried to append None to the query but that is not allowed"
            )
            return
        cls.query += [query]
        actions.app.notify("Appended user query")

    @classmethod
    def push_thread(cls, context: GPTMessage):
        """Add the selected text to the current thread"""
        thread_message = context.get("content")[0]

        if thread_message is None:
            actions.app.notify(
                "Tried to append None to the thread but that is not allowed"
            )
            return
        cls.thread += [context]
        actions.app.notify("Appended to thread")

    @classmethod
    def reset_all(cls):
        cls.text_to_confirm = ""
        cls.last_response = ""
        cls.last_meta = ""
        cls.last_was_pasted = False
        cls.last_recipe = ""
        cls.last_directional = ""
        cls.last_static_prompt = ""
        cls.last_completeness = ""
        cls.last_scope = ""
        cls.last_method = ""
        cls.last_form = ""
        cls.last_channel = ""
        cls.last_source_messages = []
        cls.last_source_key = ""
        cls.last_again_source = ""
        cls.last_suggest_source = ""
        cls.last_suggested_recipes = []
        cls.last_suggest_subject = ""
        cls.last_suggest_content = ""
        cls.last_prompt_text = ""
        cls.context = []
        cls.query = []
        cls.thread = []
        cls.last_raw_request = {}
        cls.last_raw_response = {}
        cls.last_axes = {
            "completeness": [],
            "scope": [],
            "method": [],
            "form": [],
            "channel": [],
            "directional": [],
        }
        cls.user_overrode_completeness = False
        cls.user_overrode_scope = False
        cls.user_overrode_method = False
        cls.user_overrode_form = False
        cls.user_overrode_channel = False

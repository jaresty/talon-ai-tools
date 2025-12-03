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
    last_was_pasted: ClassVar[bool] = False
    # Human-readable summary of the last prompt recipe
    # (static prompt + effective completeness/scope/method/style).
    last_recipe: ClassVar[str] = ""
    # Short token for the last directional lens (for example, "fog").
    last_directional: ClassVar[str] = ""
    # Structured fields for the last recipe, stored as short tokens where
    # applicable so they can be reused by shorthand grammars such as
    # `model again`.
    last_static_prompt: ClassVar[str] = ""
    last_completeness: ClassVar[str] = ""
    last_scope: ClassVar[str] = ""
    last_method: ClassVar[str] = ""
    last_style: ClassVar[str] = ""
    # Snapshot of the primary source messages used for the last model run
    # so `model again` can reuse the same content even if the live source
    # (for example, clipboard or selection) has changed.
    last_source_messages: ClassVar[List[Union[GPTTextItem, GPTImageItem]]] = []
    # Last explicit source key used with `model again` (for example, "clip", "this").
    last_again_source: ClassVar[str] = ""
    # Last source key used when generating prompt recipe suggestions, stored
    # as the canonical model source token (for example, "clipboard", "context").
    last_suggest_source: ClassVar[str] = ""
    # Last set of prompt recipe suggestions, if any, as a list of
    # {"name": ..., "recipe": ...} dictionaries derived from `model suggest`.
    last_suggested_recipes: ClassVar[List[Dict[str, str]]] = []
    context: ClassVar[List[Union[GPTTextItem, GPTImageItem]]] = []
    query: ClassVar[List[GPTMessage]] = []
    request: ClassVar[GPTRequest]
    thread: ClassVar[List[GPTMessage]] = []
    tools = []
    stacks: ClassVar[Dict[str, List[Union[GPTTextItem, GPTImageItem]]]] = {}
    thread_enabled: ClassVar[bool] = False
    debug_enabled: ClassVar[bool] = False
    system_prompt: ClassVar[GPTSystemPrompt] = GPTSystemPrompt()
    # Track whether the user has intentionally overridden per-axis defaults via
    # settings so that per-prompt profiles do not compete with user intent.
    user_overrode_completeness: ClassVar[bool] = False
    user_overrode_scope: ClassVar[bool] = False
    user_overrode_method: ClassVar[bool] = False
    user_overrode_style: ClassVar[bool] = False

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
        cls.last_was_pasted = False
        cls.last_recipe = ""
        cls.last_directional = ""
        cls.last_static_prompt = ""
        cls.last_completeness = ""
        cls.last_scope = ""
        cls.last_method = ""
        cls.last_style = ""
        cls.last_source_messages = []
        cls.last_again_source = ""
        cls.last_suggest_source = ""
        cls.last_suggested_recipes = []
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
    def new_stack(
        cls, message: List[Union[GPTTextItem, GPTImageItem]], stack: str
    ):
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
        cls.last_was_pasted = False
        cls.last_recipe = ""
        cls.last_directional = ""
        cls.last_static_prompt = ""
        cls.last_completeness = ""
        cls.last_scope = ""
        cls.last_method = ""
        cls.last_style = ""
        cls.last_source_messages = []
        cls.last_again_source = ""
        cls.last_suggest_source = ""
        cls.last_suggested_recipes = []
        cls.context = []
        cls.query = []
        cls.thread = []
        cls.user_overrode_completeness = False
        cls.user_overrode_scope = False
        cls.user_overrode_method = False
        cls.user_overrode_style = False

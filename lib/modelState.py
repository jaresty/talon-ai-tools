from typing import ClassVar, Dict

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
    context: ClassVar[list[GPTTextItem | GPTImageItem]] = []
    query: ClassVar[list[GPTMessage]] = []
    request: ClassVar[GPTRequest]
    thread: ClassVar[list[GPTMessage]] = []
    stacks: ClassVar[Dict[str, list[GPTTextItem | GPTImageItem]]] = {}
    thread_enabled: ClassVar[bool] = False
    debug_enabled: ClassVar[bool] = False
    system_prompt: ClassVar[GPTSystemPrompt] = GPTSystemPrompt()

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
        actions.app.notify("Cleared all state")

    @classmethod
    def new_thread(cls):
        """Create a new thread"""
        cls.thread = []
        actions.app.notify("Created a new thread")

    @classmethod
    def append_stack(
        cls,
        message: list[GPTTextItem | GPTImageItem] | list[GPTTextItem],
        stack: str,
    ):
        """Append a message to a stack"""
        if stack not in cls.stacks:
            cls.stacks[stack] = []
        cls.stacks[stack] += message
        actions.app.notify(f"Appended message to stack {stack}")

    @classmethod
    def new_stack(cls, message: list[GPTTextItem | GPTImageItem], stack: str):
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
        cls.context = []
        cls.query = []
        cls.thread = []

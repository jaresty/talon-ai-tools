"""
Helpers for interacting with GPT models within a Talon environment.

All functions in this file have impure dependencies on either the model or the Talon APIs.
"""

import base64
import json
import os
from typing import Literal, List, Sequence, Optional, Union

import requests

from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import GPTImageItem, GPTRequest, GPTMessage, GPTTextItem, GPTTool


# --- Context class for tool call control ---
class ModelHelpersContext:
    def __init__(self):
        self.total_tool_calls = 0


MAX_TOTAL_CALLS = 3
context = ModelHelpersContext()


def messages_to_string(
    messages: Sequence[Union[GPTTextItem, GPTImageItem]],
) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
    return "\n\n".join(formatted_messages)


def chats_to_string(chats: List[GPTMessage]) -> str:
    """Format thread as a string"""
    formatted_messages = []
    for chat in chats:
        formatted_messages.append(chat.get("role"))
        formatted_messages.append(messages_to_string(chat.get("content", [])))
    return "\n\n".join(formatted_messages)


def notify(message: str):
    """Send a notification to the user. Defaults the Andreas' notification system if you have it installed"""
    try:
        actions.user.notify(message)
    except Exception:
        app.notify(message)
    # Log in case notifications are disabled
    print(message)


class MissingAPIKeyError(Exception):
    """Custom exception for missing API keys."""

    pass


def get_token() -> str:
    token = os.environ.get("OPENAI_API_KEY")
    if not token:
        raise MissingAPIKeyError("OPENAI_API_KEY not found in environment variables")
    return token


def format_messages(
    role: Literal["user", "system", "assistant"],
    messages: Sequence[Union[GPTTextItem, GPTImageItem]],
) -> GPTMessage:
    return {
        "role": role,
        "content": list(messages),
    }


def format_message(content: str) -> GPTTextItem:
    return {"type": "text", "text": content}


def extract_message(content: GPTTextItem) -> str:
    return content.get("text", "")


def build_chatgpt_request(
    user_messages: List[GPTMessage],
    system_messages: List[str],
    tools: Optional[List[GPTTool]] = None,
) -> GPTRequest:
    """Build a ChatGPT API request from system and user message lists, with optional tools."""
    system_content = "\n\n".join(system_messages) if system_messages else ""

    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})

    messages.extend(user_messages)

    request: GPTRequest = {
        "model": settings.get("user.openai_model"),
        "messages": messages,
        "max_tokens": 2024,
        "tools": tools or [],
        "temperature": settings.get("user.model_temperature"),
        "n": 1,  # always one completion
    }

    return request


def _get_additional_user_context_and_tools():
    """Fetch additional user context and tools, handling errors."""
    additional_user_context = []
    user_tools = []
    try:
        if hasattr(actions.user, "gpt_additional_user_context"):
            additional_user_context = actions.user.gpt_additional_user_context()
        if hasattr(actions.user, "gpt_tools"):
            user_tools = json.loads(actions.user.gpt_tools())
    except Exception as e:
        notify(f"An error occurred fetching user context/tools: {e}")
    return additional_user_context, user_tools


def _build_request_notification() -> str:
    """Compose the notification string for build_request."""
    notification = "GPT Task Started"
    if len(GPTState.context) > 0:
        notification += ": Reusing Stored Context"
    if len(GPTState.query) > 0:
        notification += ": Reusing Stored Query"
    if GPTState.thread_enabled:
        notification += ", Threading Enabled"
    return notification


def _build_snippet_context(destination: str) -> str | None:
    """Return snippet context if destination is 'snip', else None."""
    if destination == "snip":
        return (
            "\n\nReturn the response as a snippet with placeholders. "
            "A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). "
            "Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:}}). "
            "Choices, using ${1|one,two,three|}, prompt user selection."
        )
    return None


def _build_request_context(destination: str) -> list[str]:
    """Build the list of system messages for the request context."""
    language = actions.code.language()
    language_context = (
        f"The user is currently in a code editor for the programming language: {language}. You are an expert in this language and will return syntactically appropriate responses for insertion directly into this language. All commentary should be commented out so that you do not cause any syntax errors."
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}\n\nYou are an expert user of this application."
    snippet_context = _build_snippet_context(destination)
    system_messages = [
        m
        for m in [language_context, application_context, snippet_context]
        if m is not None
    ]
    full_system_messages = [
        strip_markdown(m.get("text", m) if isinstance(m, dict) else m)
        for m in GPTState.context
    ] + system_messages
    return full_system_messages


BUILTIN_ASK_CHATGPT_TOOL = {
    "type": "function",
    "function": {
        "name": "chatgpt_call",
        "description": "Ask the assistant a followup question during a tool call.",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The prompt to pass to the assistant.",
                }
            },
            "required": ["prompt"],
        },
    },
}


def build_request(destination: str):
    """Orchestrate the GPT request build process."""
    notify(_build_request_notification())
    full_system_messages = _build_request_context(destination)
    additional_user_context, user_tools = _get_additional_user_context_and_tools()
    # Always include the built-in Ask ChatGPT tool
    all_tools = (user_tools or []) + [BUILTIN_ASK_CHATGPT_TOOL]
    GPTState.tools = all_tools
    GPTState.request = build_chatgpt_request(
        user_messages=GPTState.thread or [],
        system_messages=full_system_messages,
        tools=GPTState.tools,
    )


def append_request_messages(messages: list[GPTMessage | GPTTool]):
    GPTState.request["messages"] = GPTState.request.get("messages", []) + messages


def call_tool(
    tool_id: str, function_name: str, arguments: str
) -> Union[GPTMessage, GPTTool]:
    """Call a tool and return a valid response message (tool or assistant)"""
    if context.total_tool_calls >= MAX_TOTAL_CALLS:
        content = "Error: total tool call limit exceeded."
        notify(content)
        return format_messages("assistant", [format_message(content)])

    context.total_tool_calls += 1

    if function_name == "chatgpt_call":
        # Handle recursive call
        try:
            args = json.loads(arguments)
            prompt = args.get("prompt", "")
        except Exception as e:
            notify(f"Invalid arguments for chatgpt_call: {e}")
            prompt = ""

        system_msg = (
            "You are a recursive assistant call at depth 1 of 1.\n"
            "Provide a concise and factual answer.\n"
            "Do NOT suggest or attempt to call yourself again.\n"
            "Only respond to the user prompt with useful information."
        )
        user_message = [format_messages("user", [format_message(prompt)])]
        nested_request = build_chatgpt_request(user_message, [system_msg])
        response = send_request_internal(nested_request)
        content = response["choices"][0]["message"].get("content", "").strip()

        # Return as assistant message instead of tool
        return format_messages("assistant", [format_message(content)])

    else:
        # Real tool call via actions
        content = actions.user.gpt_call_tool(function_name, arguments)

        return {
            "tool_call_id": tool_id,
            "type": "function",
            "name": function_name,
            "role": "tool",
            "content": content,
        }


def send_request(max_attempts: int = 10):
    """Generate run a GPT request and return the response, with a limit to prevent infinite loops"""
    context.total_tool_calls = 0

    message_content = None
    attempts = 0

    while message_content is None and attempts < max_attempts:
        json_response = send_request_internal(GPTState.request)

        message_response = json_response["choices"][0]["message"]
        message_content = message_response.get("content")

        append_request_messages(
            [format_messages("assistant", [format_message(message_content)])]
        )

        for tool_call in message_response.get("tool_calls", []):
            tool_id = tool_call["id"]
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            notify(f"Calling the tool {function_name} with arguments {arguments}")

            tool_response = call_tool(tool_id, function_name, arguments)
            append_request_messages([tool_response])

        attempts += 1

    if message_content is None:
        notify("GPT request failed after max attempts.")
        raise RuntimeError("GPT request failed after max attempts.")

    notify("GPT Task Completed")
    resp = message_content.strip()
    formatted_resp = strip_markdown(resp)

    GPTState.last_response = formatted_resp
    response = format_message(formatted_resp)

    if GPTState.thread_enabled:
        GPTState.push_thread(
            {
                "role": "assistant",
                "content": [response],
            }
        )

    return response


class GPTRequestError(Exception):
    """Custom exception for errors during GPT API requests."""

    def __init__(self, status_code, error_info):
        super().__init__(
            f"GPT API request failed with status {status_code}: {error_info}"
        )
        self.status_code = status_code
        self.error_info = error_info


def send_request_internal(request):
    TOKEN = get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    if GPTState.debug_enabled:
        print(request)

    url: str = settings.get("user.model_endpoint")  # type: ignore
    notify("GPT Sending Request")
    raw_response = requests.post(url, headers=headers, data=json.dumps(request))
    if raw_response.status_code == 200:
        notify("GPT Request Completed")
    else:
        error_info = None
        try:
            error_info = raw_response.json()
        except Exception:
            error_info = raw_response.text
        notify(f"GPT Failure: HTTP {raw_response.status_code} | {error_info}")
        raise GPTRequestError(raw_response.status_code, error_info)

    json_response = raw_response.json()
    if GPTState.debug_enabled:
        print(json_response)
    return json_response


class ClipboardImageError(Exception):
    """Custom exception for clipboard image errors."""

    pass


def get_clipboard_image():
    try:
        clipped_image = clip.image()
        if clipped_image is None:
            raise ClipboardImageError("No image found in clipboard.")

        try:
            data = clipped_image.encode().data()
        except Exception as encode_err:
            raise ClipboardImageError(f"Failed to encode clipboard image: {encode_err}")

        try:
            base64_image = base64.b64encode(data).decode("utf-8")
        except Exception as b64_err:
            raise ClipboardImageError(f"Failed to base64 encode image data: {b64_err}")

        return base64_image
    except ClipboardImageError as cie:
        print(f"ClipboardImageError: {cie}")
        raise
    except Exception as e:
        print(f"Unexpected error in get_clipboard_image: {e}")
        raise ClipboardImageError(
            "Invalid image in clipboard or clipboard API failure."
        )

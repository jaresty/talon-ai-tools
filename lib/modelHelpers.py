"""
Helpers for interacting with GPT models within a Talon environment.

All functions in this file have impure dependencies on either the model or the Talon APIs.
"""

import base64
import json
import os
import traceback
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


def _log(message: str):
    """Simple logger for debug and error messages."""
    print(f"[modelHelpers] {message}")


MAX_TOTAL_CALLS = settings.get("user.gpt_max_total_calls", 3)
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


def split_answer_and_meta(text: str) -> tuple[str, str]:
    """
    Split a raw assistant response into primary answer text and an optional
    trailing meta-interpretation section.

    Heuristic:
    - By default, treat the entire response as answer text.
    - If we find a Markdown heading whose text is exactly
      'Model interpretation' (for example, '## Model interpretation'),
      ignoring case and surrounding whitespace, treat that heading and
      everything after it as meta.
    """
    if not text.strip():
        return "", ""

    lines = text.split("\n")
    split_index = None

    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            # Require an explicit "Model interpretation" heading so we don't
            # accidentally split on unrelated headings that happen to contain
            # the word "interpretation".
            heading_text = stripped.lstrip("#").strip().lower()
            if heading_text == "model interpretation":
                split_index = idx
                break

    if split_index is None:
        return text, ""

    answer = "\n".join(lines[:split_index]).rstrip()
    meta = "\n".join(lines[split_index:]).lstrip()
    return answer, meta


def chats_to_string(chats: Sequence[Union[GPTMessage, GPTTool]]) -> str:
    """Format thread as a string"""
    formatted_messages = []
    for chat in chats:
        if isinstance(chat, dict):
            # GPTMessage or GPTTool, try to handle both
            role = chat.get("role")
            if role:
                formatted_messages.append(role)
            # GPTMessage: has 'content', GPTTool: may have 'content' or 'tool_call_id', etc.
            content = chat.get("content", [])
            if isinstance(content, str):
                formatted_messages.append(content)
            else:
                formatted_messages.append(messages_to_string(content))
        else:
            # fallback: just str or unknown type
            formatted_messages.append(str(chat))
    return "\n\n".join(formatted_messages)


def notify(message: str):
    """Send a notification to the user. Falls back to Talon/app notify, then logs."""
    try:
        actions.user.notify(message)
    except Exception:
        try:
            app.notify(message)
        except Exception:
            _log(f"notify fallback failed: {traceback.format_exc()}")
    _log(message)


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
    """Format a string as a GPTTextItem dictionary."""
    return {"type": "text", "text": content}


def extract_message(content: Union[GPTTextItem, GPTImageItem]) -> str:
    """Extract text from a GPT message item, ignoring non-text entries."""
    if content.get("type") == "text":
        return content.get("text", "")
    return ""


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
        "max_completion_tokens": 5000,
        "reasoning_effort": "minimal",
        "tools": tools or [],
        "tool_choice": "auto",
        "n": 1,
        "verbosity": "low",
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
            raw_tools = actions.user.gpt_tools()
            if raw_tools:
                user_tools = json.loads(raw_tools)
    except Exception as e:
        notify(
            f"An error occurred fetching user context/tools: {e}\n{traceback.format_exc()}"
        )
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


def _build_snippet_context(destination: str) -> Optional[str]:
    """Return snippet context if destination is 'snip', else None."""
    if destination == "snip":
        return (
            "\n\nReturn the response as a snippet with placeholders. "
            "A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). "
            "Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:}}). "
            "Choices, using ${1|one,two,three|}, prompt user selection."
        )
    return None


def _build_timeout_context() -> Optional[str]:
    """Describe the approximate client-side timeout so the model can budget its response."""
    try:
        timeout_seconds: int = settings.get(
            "user.model_request_timeout_seconds", 120  # type: ignore
        )
    except Exception:
        timeout_seconds = 120
    if timeout_seconds <= 0:
        return None
    return (
        "The client may cancel this request if it takes much longer than "
        f"{timeout_seconds} seconds to receive a response. Prefer concise, efficient responses that comfortably fit within that time budget."
    )


def _build_request_context(destination: object) -> list[str]:
    """Build the list of system messages for the request context."""
    destination_str = destination if isinstance(destination, str) else ""
    language = actions.code.language()
    language_context = (
        f"The user is currently in a code editor for the programming language: {language}. You are an expert in this language and will return syntactically appropriate responses for insertion directly into this language. All commentary should be commented out so that you do not cause any syntax errors."
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}\n\nYou are an expert user of this application."
    snippet_context = _build_snippet_context(destination_str)
    timeout_context = _build_timeout_context()
    system_messages = [
        m
        for m in [language_context, application_context, snippet_context, timeout_context]
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


def build_request(destination: object):
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


def append_request_messages(messages: Sequence[Union[GPTMessage, GPTTool]]):
    GPTState.request["messages"] = GPTState.request.get("messages", []) + list(messages)


def call_tool(
    tool_id: str, function_name: str, arguments: str
) -> Union[GPTMessage, GPTTool]:
    """Call a tool and return a valid response message (tool or assistant)"""
    if context.total_tool_calls >= MAX_TOTAL_CALLS:
        content = "Error: total tool call limit exceeded."
        notify(content)
        return format_messages("assistant", [format_message(content)])

    prompt = ""

    try:
        if function_name == "chatgpt_call":
            # Handle recursive call
            try:
                args = json.loads(arguments)
                prompt = args.get("prompt", "")
            except Exception as e:
                notify(
                    f"Invalid arguments for chatgpt_call: {e}\n{traceback.format_exc()}"
                )

            system_msg = (
                "You are a recursive assistant call at depth 1 of 1.\n"
                "Provide a concise and factual answer.\n"
                "Do NOT suggest or attempt to call yourself again.\n"
                "Only respond to the user prompt with useful information."
            )
            user_message = [format_messages("user", [format_message(prompt)])]
            nested_request = build_chatgpt_request(user_message, [system_msg])
            response = send_request_internal(nested_request)

            message_response = response["choices"][0]["message"]
            message_content = message_response.get("content", "")
            if message_content is None:
                notify("GPT Failure: No content returned from chatgpt_call")
                return format_messages("assistant", [format_message("No content")])

            # Return as assistant message instead of tool
            return format_messages("assistant", [format_message(message_content)])

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
    except Exception as e:
        notify(f"Error in call_tool for {function_name}: {e}\n{traceback.format_exc()}")
        return format_messages("assistant", [format_message(f"Tool call error: {e}")])
    finally:
        context.total_tool_calls += 1


def send_request(max_attempts: int = 10):
    """Generate run a GPT request and return the response, with a limit to prevent infinite loops"""
    context.total_tool_calls = 0

    message_content = None
    attempts = 0

    while message_content is None and attempts < max_attempts:
        json_response = send_request_internal(GPTState.request)

        message_response = json_response["choices"][0]["message"]
        message_content = message_response.get("content")

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

    answer_text, meta_text = split_answer_and_meta(formatted_resp)

    GPTState.last_response = answer_text
    GPTState.last_meta = meta_text
    response = format_message(answer_text)

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

    # Capture the raw request for debugging so it can be inspected or copied
    # after the fact, regardless of whether stdout is visible.
    GPTState.last_raw_request = request

    if GPTState.debug_enabled:
        print(request)

    url: str = settings.get("user.model_endpoint")  # type: ignore
    timeout_seconds: int = settings.get("user.model_request_timeout_seconds", 120)  # type: ignore
    notify("GPT Sending Request")
    try:
        raw_response = requests.post(
            url, headers=headers, data=json.dumps(request), timeout=timeout_seconds
        )
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out after {timeout_seconds} seconds"
        notify(f"GPT Failure: {error_msg}")
        raise GPTRequestError(408, error_msg)
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
    # Capture the raw JSON response alongside the request for debugging.
    GPTState.last_raw_response = json_response
    if GPTState.debug_enabled:
        print(json_response)
    return json_response


class ClipboardImageError(Exception):
    """Custom exception for clipboard image errors."""

    pass


def get_clipboard_image():
    """Get an image from the clipboard and return it as a base64-encoded string."""
    try:
        clipped_image = clip.image()
        if clipped_image is None:
            raise ClipboardImageError("No image found in clipboard.")
        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return base64_image
    except ClipboardImageError as cie:
        _log(f"ClipboardImageError: {cie}\n{traceback.format_exc()}")
        raise
    except Exception as e:
        _log(f"Unexpected error in get_clipboard_image: {e}\n{traceback.format_exc()}")
        raise ClipboardImageError(
            "Invalid image in clipboard or clipboard API failure."
        )

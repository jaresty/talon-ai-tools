import base64
import json
import os
from typing import Literal

import requests

# from ..lib.modelDestination import Default, ModelDestination
from talon import actions, app, clip, settings

from ..lib.pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import GPTImageItem, GPTMessage, GPTTextItem, GPTTool

""""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""


def messages_to_string(
    messages: list[GPTTextItem | GPTImageItem] | list[GPTTextItem],
) -> str:
    """Format messages as a string"""
    formatted_messages = []
    for message in messages:
        if message.get("type") == "image_url":
            formatted_messages.append("image")
        else:
            formatted_messages.append(message.get("text", ""))
    return "\n\n".join(formatted_messages)


def chats_to_string(chats: list[GPTMessage]) -> str:
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


def get_token() -> str:
    """Get the OpenAI API key from the environment"""
    try:
        return os.environ["OPENAI_API_KEY"]
    except KeyError:
        message = "GPT Failure: env var OPENAI_API_KEY is not set."
        notify(message)
        raise Exception(message)


def format_messages(
    role: Literal["user", "system", "assistant"],
    messages: list[GPTTextItem | GPTImageItem] | list[GPTTextItem],
) -> GPTMessage:
    return {
        "role": role,
        "content": messages,
    }


def format_message(content: str) -> GPTTextItem:
    return {"type": "text", "text": content}


def extract_message(content: GPTTextItem) -> str:
    return content.get("text", "")


def build_request(
    destination,
):
    notification = "GPT Task Started"
    if len(GPTState.context) > 0:
        notification += ": Reusing Stored Context"
    if len(GPTState.query) > 0:
        notification += ": Reusing Stored Query"
    if GPTState.thread_enabled:
        notification += ", Threading Enabled"

    notify(notification)

    language = actions.code.language()
    language_context = (
        f"The user is currently in a code editor for the programming language: {language}. You are an expert in this language and will return syntactically appropriate responses for insertion directly into this language. All commentary should be commented out so that you do not cause any syntax errors."
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}\n\nYou are an expert user of this application."
    snippet_context = (
        "\n\nPlease return the response as a snippet with placeholders. A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). Linked tabstops update together. Placeholders, such as ${1:foo}, allow easy changes and can be nested (${1:another ${2:}}). Choices, using ${1|one,two,three|}, prompt user selection."
        if destination == "snip"  # todo: change this to handle the type being snipped
        else None
    )
    additional_user_context = []
    try:
        additional_user_context = actions.user.gpt_additional_user_context()
    except Exception as e:
        # Handle the exception, log it, or print an error message
        notify(f"An error occurred: {e}")

    system_messages: list[GPTTextItem | GPTImageItem] = [
        {"type": "text", "text": item}
        for item in additional_user_context
        + [
            application_context,
            settings.get("user.model_system_prompt"),
            language_context,
            snippet_context,
        ]
        if item is not None
    ]

    system_messages = GPTState.context + system_messages

    GPTState.request = {
        "messages": [],
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "model": settings.get("user.openai_model"),
    }
    append_request_messages([format_messages("system", system_messages)])
    append_request_messages(GPTState.thread)


def append_request_messages(messages: list[GPTMessage]):
    GPTState.request["messages"] = GPTState.request.get("messages", []) + messages


def call_tool(tool_id: str, function_name: str, arguments: str) -> GPTTool:
    """Call a tool and return a response"""
    return {
        "tool_call_id": tool_id,
        "name": function_name,
        "role": "tool",
        "content": "",
    }


def send_request():
    """Generate run a GPT request and return the response"""

    message_content = None

    # loop until the message content is defined
    while message_content is None:
        # Send the request and get the response
        raw_response = send_request_internal(GPTState.request).json()["choices"][0][
            "message"
        ]
        for tool_call in getattr(raw_response, "tool_calls", []):
            tool_id = tool_call["id"]
            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]
            tool_response = call_tool(tool_id, function_name, arguments)
            GPTState.request["messages"].append(tool_response)

        # Check if the response content is valid
        if raw_response:
            message_content = raw_response["content"]
        else:
            # Optionally, handle the case where response is not valid
            print("No valid response received, retrying...")

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


def send_request_internal(request):
    TOKEN = get_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    if GPTState.debug_enabled:
        print(request)

    url: str = settings.get("user.model_endpoint")  # type: ignore
    raw_response = requests.post(url, headers=headers, data=json.dumps(request))
    match raw_response.status_code:
        case 200:
            notify("GPT Request Completed")
        case _:
            notify("GPT Failure: Check the Talon Log")
            raise Exception(raw_response.json())

    return raw_response


def get_clipboard_image():
    try:
        clipped_image = clip.image()
        if not clipped_image:
            raise Exception("No image found in clipboard")

        data = clipped_image.encode().data()
        base64_image = base64.b64encode(data).decode("utf-8")
        return base64_image
    except Exception as e:
        print(e)
        raise Exception("Invalid image in clipboard")

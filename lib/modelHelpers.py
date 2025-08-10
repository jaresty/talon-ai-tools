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

"""
All functions in this this file have impure dependencies on either the model or the talon APIs
"""

MAX_RECURSION_DEPTH = 3
MAX_TOTAL_CALLS = 10
total_calls = 0

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

def handle_chatgpt_tool_call(args, current_depth):
    """
    Handles a recursive ChatGPT tool call.
    """
    global total_calls

    # Increment counters
    total_calls += 1
    new_depth = current_depth + 1

    # Check limits
    if new_depth > MAX_RECURSION_DEPTH:
        return "Recursion limit reached."
    if total_calls > MAX_TOTAL_CALLS:
        return "Total call limit reached."

    # Construct the inner request using existing functions
    inner_request = {
        "messages": [
            format_messages("system", [{"type": "text", "text": "Be concise and factual."}]),
            format_messages("user", [{"type": "text", "text": args["prompt"]}]),
        ],
        "model": args.get("model", "gpt-4"),
        "max_tokens": 512,  # Adjust based on your use case
        "tools": [],
    }

    # Send the request and process the response
    inner_response = send_request_internal(inner_request).json()
    message_content = inner_response["choices"][0]["message"].get("content", "")
    return message_content.strip()

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

def run_conversation():
    """
    Orchestrates a conversation with ChatGPT, supporting recursive tool calls.
    """
    global total_calls
    total_calls = 0

    # Define ChatGPT-as-a-tool
    outer_tools = [
        {
            "type": "function",
            "function": {
                "name": "call_chatgpt",
                "description": "Call another ChatGPT instance with a given prompt and optional model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {"type": "string"},
                        "model": {"type": "string"}
                    },
                    "required": ["prompt"]
                }
            }
        }
    ]

    # Start conversation
    messages = [
        {"role": "system", "content": "You can call 'call_chatgpt' if you need more info."},
        {"role": "user", "content": "Write a poem about recursion in programming."}
    ]

    depth = 0
    while True:
        # Replace run_chatgpt_call with send_request_internal
        request = {
            "messages": messages,
            "model": "gpt-4",
            "tools": outer_tools,
            "max_tokens": 1024,
        }
        resp = send_request_internal(request).json()
        choice = resp["choices"][0]

        if choice.get("finish_reason") == "stop":
            print("Final output:\n", choice["message"]["content"])
            break

        if choice["message"].get("tool_calls"):
            for tool_call in choice["message"]["tool_calls"]:
                if tool_call["function"]["name"] == "call_chatgpt":
                    import json
                    args = json.loads(tool_call["function"]["arguments"])

                    tool_result = handle_chatgpt_tool_call(args, depth)

                    # Return tool output to the conversation
                    messages.append(choice["message"])
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result
                    })

                    depth += 1
                    break
        else:
            # No more tool calls — end loop
            break

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
        f"The user is currently in a code editor for the programming language: {language}. You are an expert in this language and will return syntactically appropriate responses for insertion dire[...]"
        if language != ""
        else None
    )
    application_context = f"The following describes the currently focused application:\n\n{actions.user.talon_get_active_context()}\n\nYou are an expert user of this application."
    snippet_context = (
        "\n\n Return the response as a snippet with placeholders. A snippet can control cursors and text insertion using constructs like tabstops ($1, $2, etc., with $0 as the final position). Li[...]"
        if destination == "snip"  # todo: change this to handle the type being snipped
        else None
    )
    additional_user_context = []
    GPTState.tools = []
    try:
        additional_user_context = actions.user.gpt_additional_user_context()
        GPTState.tools = json.loads(actions.user.gpt_tools())
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
        "tools": GPTState.tools,
        "max_tokens": 2024,
        "temperature": settings.get("user.model_temperature"),
        "n": 1,
        "model": settings.get("user.openai_model"),
    }
    append_request_messages([format_messages("system", system_messages)])
    append_request_messages(GPTState.thread)

def append_request_messages(messages: list[GPTMessage] | list[GPTTool]):
    GPTState.request["messages"] = GPTState.request.get("messages", []) + messages

def call_tool(tool_id: str, function_name: str, arguments: str) -> GPTTool:
    """Call a tool and return a response"""
    content = actions.user.gpt_call_tool(function_name, arguments)
    return {
        "tool_call_id": tool_id,
        "type": "function",
        "name": function_name,
        "role": "tool",
        "content": content,
    }

def send_request():
    """Generate run a GPT request and return the response"""
    message_content = None
    while message_content is None:
        json_response = send_request_internal(GPTState.request).json()
        if GPTState.debug_enabled:
            print(json_response)
        message_response = json_response["choices"][0]["message"]
        message_content = message_response.get("content", None)
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
    notify("GPT Sending Request")
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

"""
Helpers for interacting with GPT models within a Talon environment.

All functions in this file have impure dependencies on either the model or the Talon APIs.
"""

import base64
import json
import os
import re
import traceback
import time
import codecs
from typing import Literal, List, Sequence, Optional, Union

import requests

from talon import actions, app, clip, settings
from talon import cron

from .pureHelpers import strip_markdown
from .modelState import GPTState
from .modelTypes import GPTImageItem, GPTRequest, GPTMessage, GPTTextItem, GPTTool
from .requestAsync import start_async
from .requestBus import (
    emit_begin_send,
    emit_begin_stream,
    emit_complete,
    emit_fail,
    emit_reset,
    emit_cancel,
    set_controller,
    current_state,
)
from .requestController import RequestUIController
from .requestState import RequestState
from .requestLog import append_entry_from_request
from .uiDispatch import run_on_ui_thread
from .requestLifecycle import RequestLifecycleState, reduce_request_state
from .streamingCoordinator import (
    new_streaming_run,
    StreamingRun,
    record_streaming_snapshot,
    record_streaming_chunk,
    record_streaming_complete,
    record_streaming_error,
)
from .providerRegistry import (
    OPENAI_ENDPOINT,
    ProviderConfig,
    provider_registry,
    provider_token_hint,
    provider_tokens_setting,
)
from .providerCanvas import show_provider_canvas
from .axisCatalog import axis_catalog
import threading

# Ensure a default request UI controller is registered so lifecycle events
# surface minimal progress toasts even before richer UI hooks exist.
try:
    from . import requestUI  # noqa: F401
except Exception:
    # Best-effort; if Talon imports fail, continue without UI wiring.
    pass


_active_response_lock = threading.Lock()
_active_response = None


def _set_active_response(resp):
    global _active_response
    with _active_response_lock:
        _active_response = resp


def cancel_active_request():
    """Best-effort: close any in-flight HTTP response."""
    global _active_response
    with _active_response_lock:
        resp = _active_response
        _active_response = None
    try:
        if resp is not None:
            resp.close()
    except Exception:
        pass


# --- Context class for tool call control ---
class ModelHelpersContext:
    def __init__(self):
        self.total_tool_calls = 0


def _log(message: str):
    """Simple logger for debug and error messages."""
    print(f"[modelHelpers] {message}")


MAX_TOTAL_CALLS = settings.get("user.gpt_max_total_calls", 3)
context = ModelHelpersContext()
_last_notify_request_id = None
_last_notify_message = None


def _destination_kind(destination: object) -> str:
    """Derive a short destination kind for UI decisions."""
    try:
        if hasattr(destination, "kind"):
            kind = getattr(destination, "kind")
            if isinstance(kind, str) and kind:
                return kind.lower()
        if isinstance(destination, str):
            return (destination or "").lower()
        return destination.__class__.__name__.lower()
    except Exception:
        return ""


def _prefer_canvas_progress() -> bool:
    """Return True when the destination prefers in-canvas progress over a pill."""
    try:
        kind = getattr(GPTState, "current_destination_kind", "") or ""
    except Exception:
        kind = ""
    return kind in ("window", "default")


def _should_show_response_canvas() -> bool:
    """Gate response-canvas usage on destination preferences and explicit suppression."""
    try:
        if getattr(GPTState, "suppress_response_canvas", False):
            return False
    except Exception:
        pass
    return _prefer_canvas_progress()


def _refresh_response_canvas() -> None:
    """Open (if needed) and refresh the response canvas once on the UI thread."""

    def _open_and_refresh():
        try:
            actions.user.model_response_canvas_open()
        except Exception:
            pass
        try:
            actions.user.model_response_canvas_refresh()
        except Exception as e:
            try:
                app.notify(f"GPT: response canvas refresh failed: {e}")
            except Exception:
                pass

    run_on_ui_thread(_open_and_refresh)


def _update_stream_state_from_text(
    full_text: str,
    meta_throttle_ms: Optional[int] = None,
    last_meta_update_ms: Optional[list[int]] = None,
) -> None:
    """
    Normalise the in-flight streaming buffer so:
    - GPTState.text_to_confirm holds only the main answer body (meta removed).
    - GPTState.last_meta is kept in sync as soon as a meta section appears.
    - GPTState.last_streaming_snapshot["text"] mirrors the meta-stripped answer
      so canvas progress views never briefly show meta inside the main body.

    This keeps the response canvas layout stable while streaming, avoiding a
    late jump when the finished response is split into answer/meta.
    """
    try:
        # When meta updates are throttled and we've updated recently, skip the
        # split entirely to avoid redundant parsing work while the answer is
        # stable and only meta is streaming in.
        if meta_throttle_ms is not None and last_meta_update_ms is not None:
            last = last_meta_update_ms[0] if last_meta_update_ms else 0
            if last:
                now_ms = int(time.time() * 1000)
                if now_ms - last < meta_throttle_ms:
                    return

        answer, meta = split_answer_and_meta(full_text)
        GPTState.text_to_confirm = answer

        # Keep the streaming snapshot text aligned with the meta-stripped
        # answer so any canvas using the snapshot (for example, the response
        # viewer's inflight progress path) does not briefly render the meta
        # section as part of the main response.
        try:
            snap = getattr(GPTState, "last_streaming_snapshot", None)
        except Exception:
            snap = None
        if isinstance(snap, dict):
            updated = dict(snap)
            if answer:
                updated["text"] = answer
            else:
                # Preserve whatever text was already present when we don't have
                # a better split (for example, when the buffer is empty).
                updated["text"] = str(updated.get("text", ""))
            try:
                GPTState.last_streaming_snapshot = updated
            except Exception:
                pass

        if meta:
            if meta_throttle_ms is not None and last_meta_update_ms is not None:
                now_ms = int(time.time() * 1000)
                last = last_meta_update_ms[0] if last_meta_update_ms else 0
                if last and now_ms - last < meta_throttle_ms:
                    return
                if last_meta_update_ms:
                    last_meta_update_ms[0] = now_ms
                else:
                    last_meta_update_ms.append(now_ms)
            GPTState.last_meta = meta
    except Exception:
        # Fall back to the raw text if splitting fails so we still surface progress.
        GPTState.text_to_confirm = full_text


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

    heading_pattern = re.compile(r"^\s*#+\s*model interpretation\b", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if heading_pattern.match(line):
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
    """Send a notification to the user, deduplicating per request id."""
    global _last_notify_request_id, _last_notify_message

    try:
        request_id = getattr(current_state(), "request_id", None)
    except Exception:
        request_id = None

    try:
        suppress_id = getattr(GPTState, "suppress_inflight_notify_request_id", None)
    except Exception:
        suppress_id = None
    if suppress_id is None:
        try:
            # Optional import to pick up the module-level flag if available.
            from talon_user.GPT import gpt as gpt_module  # type: ignore

            suppress_id = getattr(gpt_module, "_suppress_inflight_notify_request_id", None)
        except Exception:
            pass

    if suppress_id is not None:
        if request_id is None:
            request_id = suppress_id
        if request_id == suppress_id:
            return

    if (
        request_id is not None
        and _last_notify_request_id == request_id
        and _last_notify_message == message
    ) or (
        request_id is None
        and _last_notify_request_id is None
        and _last_notify_message == message
    ):
        return

    _last_notify_request_id = request_id
    _last_notify_message = message

    delivered = False
    try:
        actions.user.notify(message)
        delivered = True
    except Exception:
        try:
            app.notify(message)
            delivered = True
        except Exception:
            _log(f"notify fallback failed: {traceback.format_exc()}")
    # Record the notification in call logs for tests, even when delivery succeeds.
    try:
        if hasattr(actions.user, "calls"):
            actions.user.calls.append(("notify", (message,), {}))
        if hasattr(actions.app, "calls"):
            actions.app.calls.append(("notify", (message,), {}))
    except Exception:
        pass
    _log(message)


def build_exchange_snapshot(result, kind: str = "response") -> dict:
    """Build a simple exchange snapshot for destinations like File.

    Uses GPTState to fill in prompt/response/meta text alongside the
    rendered presentation from the PromptResult-like object.
    """
    try:
        presentation = result.presentation_for("paste")
        response_text = getattr(presentation, "paste_text", "") or getattr(
            presentation, "display_text", ""
        )
    except Exception:
        response_text = ""

    prompt_text = getattr(GPTState, "last_prompt_text", "") or ""
    meta_text = getattr(GPTState, "last_meta", "") or ""

    return {
        "kind": kind,
        "prompt_text": prompt_text,
        "response_text": response_text,
        "meta_text": meta_text,
    }


class MissingAPIKeyError(Exception):
    """Custom exception for missing API keys."""

    pass


def get_token(provider: Optional[ProviderConfig] = None) -> str:
    provider = provider or provider_registry().active_provider()
    tokens = provider_tokens_setting()
    token = tokens.get(provider.id)
    token_source = "settings" if token else ""
    if not token:
        token = os.environ.get(provider.api_key_env)
        if token:
            token_source = "env"
    if not token:
        hint = provider_token_hint(provider.id, provider.api_key_env)
        _show_provider_error(
            f"Missing token ({hint})",
            provider.id,
            provider.api_key_env,
            hint=f"Set {hint}.",
        )
        raise MissingAPIKeyError(
            f"Token missing for provider '{provider.id}'. Configure {hint}."
        )
    try:
        GPTState.current_provider_id = provider.id  # type: ignore[attr-defined]
    except Exception:
        pass
    return token


def active_provider() -> ProviderConfig:
    """Return the active provider and mirror it into GPTState."""

    provider = provider_registry().active_provider()
    try:
        GPTState.current_provider_id = provider.id  # type: ignore[attr-defined]
    except Exception:
        pass
    return provider


def bound_provider() -> ProviderConfig:
    """Return the provider bound to the current request, falling back to active."""

    try:
        bound = getattr(GPTState, "request_provider", None)
        if bound:
            return bound  # type: ignore[return-value]
    except Exception:
        pass
    return active_provider()


def _ensure_request_supported(provider: ProviderConfig, request: dict) -> None:
    """Raise if the provider lacks capabilities required by the request."""

    try:
        messages = request.get("messages", []) or []
    except Exception:
        messages = []
    requires_vision = False
    for msg in messages:
        try:
            for content in msg.get("content") or []:
                if isinstance(content, dict) and content.get("type") == "image_url":
                    requires_vision = True
                    break
            if requires_vision:
                break
        except Exception:
            continue
    if requires_vision and not provider.features.get("vision", False):
        _show_provider_error(
            "Vision not supported for this provider", provider.id, provider.api_key_env
        )
        raise UnsupportedProviderCapability(provider.id, "vision")


def provider_endpoint(provider: ProviderConfig) -> str:
    """Return the effective endpoint with user override support."""

    override = settings.get("user.model_endpoint", None)
    if isinstance(override, str) and override.strip():
        return override.strip()
    return provider.endpoint or OPENAI_ENDPOINT


def _show_provider_error(
    message: str, provider_id: str, api_key_env: str, *, hint: Optional[str] = None
) -> None:
    """Render a provider error in the canvas for quick recovery."""

    lines = [f"Provider '{provider_id}' unavailable: {message}"]
    if hint:
        lines.append(hint)
    else:
        lines.append(
            f"Check {provider_token_hint(provider_id, api_key_env)} or provider capabilities."
        )
    try:
        show_provider_canvas("Provider error", lines)
    except Exception:
        try:
            notify(message)
        except Exception:
            pass


def _warn_streaming_disabled(provider: ProviderConfig) -> None:
    """Inform the user when streaming is disabled for the current provider."""

    lines = [
        f"Streaming disabled for provider '{provider.id}'.",
        "Running request without streaming.",
    ]
    try:
        show_provider_canvas("Provider warning", lines)
    except Exception:
        try:
            notify("Streaming disabled for this provider")
        except Exception:
            pass


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
    provider: Optional[ProviderConfig] = None,
) -> GPTRequest:
    """Build a ChatGPT API request from system and user message lists, with optional tools."""
    system_content = "\n\n".join(system_messages) if system_messages else ""

    provider = provider or active_provider()
    model_id = provider.default_model or None
    if provider.id == "openai":
        model_id = settings.get("user.openai_model", model_id)
    elif provider.id == "gemini":
        model_id = settings.get("user.model_provider_model_gemini", model_id)
    model_id = model_id or "gpt-5"

    messages = []
    if system_content:
        messages.append({"role": "system", "content": system_content})

    messages.extend(user_messages)

    request: GPTRequest = {
        "model": model_id,
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
            "user.model_request_timeout_seconds",
            120,  # type: ignore
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
        for m in [
            language_context,
            application_context,
            snippet_context,
            timeout_context,
        ]
        if m is not None
    ]
    full_system_messages = [
        strip_markdown(m.get("text", m) if isinstance(m, dict) else m)
        for m in GPTState.context
    ] + system_messages
    return full_system_messages


def build_system_prompt_messages(
    include_request_context: bool = False, destination: Optional[object] = None
) -> list[GPTTextItem]:
    """Return hydrated system-prompt messages, optionally including request context."""
    messages: list[GPTTextItem] = []
    context_lines: list[str] = []
    if include_request_context:
        try:
            context_lines = _build_request_context(destination if destination is not None else "")
        except Exception:
            context_lines = []
    for line in context_lines:
        if line:
            messages.append(format_message(line))

    try:
        prompt = getattr(GPTState, "system_prompt", None)
        prompt_lines = (
            prompt.format_as_array()
            if prompt is not None and hasattr(prompt, "format_as_array")
            else []
        )
    except Exception:
        prompt_lines = []

    for line in prompt_lines:
        if line:
            messages.append(format_message(line))

    return messages


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
    kind = _destination_kind(destination)
    try:
        print(f"[modelHelpers] build_request destination kind={kind}")
    except Exception:
        pass
    # Reset per-request buffers so stale meta/stream text do not bleed into the
    # next response.
    try:
        GPTState.text_to_confirm = ""
        GPTState.last_meta = ""
        GPTState.last_streaming_snapshot = {}
    except Exception:
        pass
    # For paste-like destinations, if there is no focused textarea we fall back
    # to the window surface; detect that up front so progress is routed to the
    # response canvas instead of a pill.
    try:
        if kind in {"paste", "above", "below", "chunked", "snip", "typed"}:
            if hasattr(destination, "inside_textarea") and callable(
                getattr(destination, "inside_textarea", None)
            ):
                if not destination.inside_textarea():
                    kind = "window"
                    print(
                        "[modelHelpers] inside_textarea=False; forcing destination kind=window"
                    )
    except Exception:
        pass
    try:
        GPTState.current_destination_kind = kind
    except Exception:
        GPTState.current_destination_kind = ""
    try:
        GPTState.text_to_confirm = ""
    except Exception:
        pass
    full_system_messages = _build_request_context(destination)
    additional_user_context, user_tools = _get_additional_user_context_and_tools()
    # Always include the built-in Ask ChatGPT tool
    all_tools = (user_tools or []) + [BUILTIN_ASK_CHATGPT_TOOL]
    GPTState.tools = all_tools
    provider = active_provider()
    GPTState.request_provider = provider
    GPTState.request = build_chatgpt_request(
        user_messages=GPTState.thread or [],
        system_messages=full_system_messages,
        tools=GPTState.tools,
        provider=provider,
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


class CancelledRequest(RuntimeError):
    """Raised internally when a cancel is requested mid-stream."""

    pass


class UnsupportedProviderCapability(RuntimeError):
    """Raised when a provider lacks required capabilities for the request."""

    def __init__(self, provider_id: str, feature: str):
        super().__init__(f"Provider '{provider_id}' does not support {feature}")
        self.provider_id = provider_id
        self.feature = feature


def _send_request_streaming(request, request_id: str) -> str:
    """Stream a response and append deltas into GPTState.text_to_confirm."""
    try:
        print("[modelHelpers] streaming entry")
    except Exception:
        pass

    managed_externally = False
    lifecycle = RequestLifecycleState()
    try:
        managed_externally = hasattr(GPTState, "last_lifecycle")
        if managed_externally:
            lifecycle = getattr(GPTState, "last_lifecycle", lifecycle)
        else:
            GPTState.last_lifecycle = lifecycle
    except Exception:
        managed_externally = True

    def _update_lifecycle(event: str) -> None:
        nonlocal lifecycle
        if managed_externally:
            return
        try:
            lifecycle = reduce_request_state(lifecycle, event)
            try:
                GPTState.last_lifecycle = lifecycle
            except Exception:
                pass
        except Exception:
            pass

    _update_lifecycle("start")

    provider = bound_provider()
    _ensure_request_supported(provider, request)
    try:
        TOKEN = get_token(provider)
    except MissingAPIKeyError:
        _show_provider_error("Missing API key", provider.id, provider.api_key_env)
        raise
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }
    url: str = provider_endpoint(provider)  # type: ignore
    timeout_seconds: int = settings.get("user.model_request_timeout_seconds", 120)  # type: ignore

    decoder = codecs.getincrementaldecoder("utf-8")()
    streaming_run: StreamingRun = new_streaming_run(request_id)
    try:
        catalog = axis_catalog()
        axes_map = catalog.get("axes", {}) or {}
        filtered_axes: dict[str, list[str]] = {}
        axes = request.get("axes") or {}
        for axis in (
            "completeness",
            "scope",
            "method",
            "form",
            "channel",
            "directional",
        ):
            vals = axes.get(axis) or []
            if isinstance(vals, list):
                tokens = [str(v) for v in vals if str(v)]
            else:
                tokens = [str(vals)] if vals else []
            known = set((axes_map.get(axis) or {}).keys())
            kept = [t for t in tokens if t in known]
            if kept:
                filtered_axes[axis] = kept
        streaming_run.axes = filtered_axes
    except Exception:
        pass
    parts: list[str] = streaming_run.chunks

    def _update_streaming_snapshot() -> None:
        record_streaming_snapshot(streaming_run)

    record_streaming_snapshot(streaming_run)
    first_chunk = True
    refresh_interval_ms = 250
    last_canvas_refresh_ms = 0
    last_meta_refresh_ms = [0]
    emit_begin_stream(request_id=request_id)
    # Seed the meta section at the top of the response so the layout stays
    # stable even before the real meta arrives from the stream.
    try:
        GPTState.last_meta = "## Model interpretation\n(pending…)"
    except Exception:
        pass
    # Open the response canvas up-front when using the window/default path so
    # progress (or buffered responses) are visible without waiting for the end.
    if _should_show_response_canvas():
        try:
            actions.user.model_response_canvas_open()
        except Exception:
            pass

    try:
        print(
            f"[modelHelpers] streaming path engaged url={url} "
            f"timeout={timeout_seconds}s"
        )
    except Exception:
        pass

    def _handle_streaming_error(exc: Exception) -> None:
        _update_lifecycle("error")
        emit_fail(str(exc), request_id=request_id)
        try:
            print(f"[modelHelpers] streaming error; falling back: {exc!r}")
        except Exception:
            pass

    # Explicitly request streaming from the API; some endpoints require the
    # `stream` flag in the JSON payload as well as an HTTP streaming response.
    request_with_stream = dict(request)
    request_with_stream["stream"] = True

    try:
        raw_response = requests.post(
            url,
            headers=headers,
            json=request_with_stream,
            timeout=timeout_seconds,
            stream=True,
        )
        _set_active_response(raw_response)
        try:
            print("[modelHelpers] streaming request started")
            content_type = raw_response.headers.get("content-type", "")
            if content_type and "text/event-stream" not in content_type.lower():
                print(
                    f"[modelHelpers] streaming requested but content-type='{content_type}'; "
                    "response may be buffered"
                )
                # If the server ignored streaming, parse the full JSON body once
                # and return immediately to avoid consuming the stream iterator.
                try:
                    parsed_full = raw_response.json()
                    if raw_response.status_code != 200:
                        error_info = parsed_full or raw_response.text
                        streaming_run.on_error(f"HTTP {raw_response.status_code}")
                        record_streaming_snapshot(streaming_run)
                        notify(
                            f"GPT Failure: HTTP {raw_response.status_code} | {error_info}"
                        )
                        raise GPTRequestError(raw_response.status_code, error_info)
                    text_piece = (
                        parsed_full.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    if text_piece:
                        record_streaming_chunk(streaming_run, text_piece)
                    full_text = streaming_run.text
                    _update_stream_state_from_text(
                        full_text,
                        meta_throttle_ms=refresh_interval_ms,
                        last_meta_update_ms=last_meta_refresh_ms,
                    )
                    _update_lifecycle("stream_start")
                    _update_lifecycle("stream_end")
                    if _should_show_response_canvas():
                        _refresh_response_canvas()
                    try:
                        print(
                            "[modelHelpers] non-stream response parsed via json(), "
                            f"len={len(text_piece or '')}"
                        )
                    except Exception:
                        pass
                    record_streaming_complete(streaming_run)
                    answer_text = full_text
                    GPTState.last_raw_response = parsed_full
                    _set_active_response(None)
                    return answer_text
                except Exception as e:
                    print(f"[modelHelpers] non-stream parse failed: {e!r}")
                    traceback.print_exc()
        except Exception:
            pass
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out after {timeout_seconds} seconds"
        notify(f"GPT Failure: {error_msg}")
        err = GPTRequestError(408, error_msg)
        record_streaming_error(streaming_run, error_msg)
        _handle_streaming_error(err)
        raise err
    except Exception as e:
        print(f"[modelHelpers] streaming requests.post failed: {e!r}")
        traceback.print_exc()
        record_streaming_error(streaming_run, str(e))
        _handle_streaming_error(e)
        raise
    if raw_response.status_code != 200:
        error_info = None
        try:
            error_info = raw_response.json()
        except Exception:
            error_info = raw_response.text
        record_streaming_error(streaming_run, f"HTTP {raw_response.status_code}")
        notify(f"GPT Failure: HTTP {raw_response.status_code} | {error_info}")
        raise GPTRequestError(raw_response.status_code, error_info)

    def _maybe_refresh_canvas(force: bool = False) -> None:
        nonlocal last_canvas_refresh_ms
        if not _should_show_response_canvas():
            return
        now_ms = int(time.time() * 1000)
        if (
            not force
            and last_canvas_refresh_ms
            and now_ms - last_canvas_refresh_ms < refresh_interval_ms
        ):
            return
        try:
            actions.user.model_response_canvas_refresh()
            last_canvas_refresh_ms = now_ms
        except Exception:
            pass

    def _append_text(text_piece: str):
        nonlocal first_chunk
        record_streaming_chunk(streaming_run, text_piece)
        full_text = streaming_run.text
        _update_stream_state_from_text(
            full_text,
            meta_throttle_ms=refresh_interval_ms,
            last_meta_update_ms=last_meta_refresh_ms,
        )
        if first_chunk:
            first_chunk = False
            _update_lifecycle("stream_start")
            if _should_show_response_canvas():
                try:
                    actions.user.model_response_canvas_open()
                except Exception:
                    pass
                _maybe_refresh_canvas(force=True)
                return
        _maybe_refresh_canvas()

    try:
        for raw_line in raw_response.iter_lines():
            try:
                state = current_state()
            except Exception:
                state = RequestState()
            if getattr(state, "cancel_requested", False):
                try:
                    print("[modelHelpers] streaming cancel detected; closing stream")
                    try:
                        phase = getattr(state, "phase", None)
                        print(f"[modelHelpers] streaming cancel state phase={phase}")
                    except Exception:
                        pass
                except Exception:
                    pass
                record_streaming_error(streaming_run, "cancelled")
                try:
                    set_controller(RequestUIController())
                    emit_cancel(request_id=request_id)
                except Exception:
                    pass
                try:
                    cancel_active_request()
                except Exception:
                    pass
                try:
                    raw_response.close()
                except Exception:
                    pass
                _set_active_response(None)
                raise CancelledRequest()
            if not raw_line:
                continue
            if raw_line.startswith(b":"):
                continue
            line = decoder.decode(raw_line)
            if not line:
                continue
            if line.startswith("data:"):
                line = line[len("data:") :].strip()
            if line == "[DONE]":
                break
            try:
                parsed = json.loads(line)
            except Exception:
                continue
            try:
                delta = parsed["choices"][0].get("delta", {})
                text_piece = delta.get("content")
            except Exception:
                text_piece = None
            if text_piece:
                _append_text(text_piece)
        try:
            state_after_stream = current_state()
        except Exception:
            state_after_stream = RequestState()
        if getattr(state_after_stream, "cancel_requested", False):
            try:
                print("[modelHelpers] streaming ended; cancel requested, aborting")
            except Exception:
                pass
            record_streaming_error(streaming_run, "cancelled")
            try:
                set_controller(RequestUIController())
                emit_cancel(request_id=request_id)
            except Exception:
                pass
            raise CancelledRequest()
        tail = decoder.decode(b"", final=True)
        if tail:
            _append_text(tail)
        # Fallback: if no chunks were received, try parsing a full JSON body
        # (some endpoints may ignore the stream flag and return a single JSON).
        if not streaming_run.chunks:
            try:
                parsed_full = raw_response.json()
                text_piece = (
                    parsed_full.get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                if text_piece:
                    record_streaming_chunk(streaming_run, text_piece)
                    full_text = streaming_run.text
                    _update_stream_state_from_text(
                        full_text,
                        meta_throttle_ms=refresh_interval_ms,
                        last_meta_update_ms=last_meta_refresh_ms,
                    )
                    if _should_show_response_canvas():
                        _refresh_response_canvas()
                    print(
                        "[modelHelpers] streaming fallback parsed full JSON, "
                        f"len={len(text_piece)} total_len={len(GPTState.text_to_confirm)}"
                    )
            except Exception as e:
                print(f"[modelHelpers] streaming fallback parse failed: {e}")
        else:
            try:
                print(
                    f"[modelHelpers] streaming completed with {len(streaming_run.chunks)} chunks"
                )
            except Exception:
                pass
    except CancelledRequest:
        # Cancel was requested upstream; just propagate without extra notifications.
        try:
            print("[modelHelpers] streaming CancelledRequest caught, closing")
        except Exception:
            pass
        try:
            cancel_active_request()
        except Exception:
            pass
        try:
            raw_response.close()
        except Exception:
            pass
        _set_active_response(None)
        record_streaming_error(streaming_run, "cancelled")
        _update_lifecycle("cancel")
        raise
    except Exception as e:
        # If cancel was requested (regardless of exception type), treat as cancel.
        try:
            state = current_state()
        except Exception:
            state = RequestState()
        if getattr(state, "cancel_requested", False):
            try:
                print(f"[modelHelpers] streaming exception during cancel: {e!r}")
            except Exception:
                pass
            try:
                raw_response.close()
            except Exception:
                pass
            _set_active_response(None)
            try:
                cancel_active_request()
            except Exception:
                pass
            raise CancelledRequest()
        # Some transports surface cancellation as AttributeError on the underlying
        # stream; treat those as cancels to avoid noisy tracebacks.
        if isinstance(e, AttributeError):
            try:
                raw_response.close()
            except Exception:
                pass
            _set_active_response(None)
            raise CancelledRequest()
        record_streaming_error(streaming_run, str(e))
        _handle_streaming_error(e)
        raise

    finally:
        try:
            raw_response.close()
        except Exception:
            pass

    record_streaming_complete(streaming_run)
    answer_text = streaming_run.text
    try:
        print(
            f"[modelHelpers] streaming complete parts={len(streaming_run.chunks)} answer_len={len(answer_text)} "
            f"meta_present={bool(GPTState.last_meta)}"
        )
    except Exception:
        pass
    _update_lifecycle("stream_end")
    GPTState.last_raw_response = {"choices": [{"message": {"content": answer_text}}]}
    _set_active_response(None)
    return answer_text


def send_request(max_attempts: int = 10):
    """Generate run a GPT request and return the response, with a limit to prevent infinite loops"""
    context.total_tool_calls = 0

    message_content = None
    attempts = 0

    lifecycle = RequestLifecycleState()
    try:
        GPTState.last_lifecycle = lifecycle
    except Exception:
        pass
    try:
        GPTState.last_streaming_snapshot = {}
    except Exception:
        pass

    request_id = emit_begin_send()
    try:
        GPTState.suppress_inflight_notify_request_id = request_id
    except Exception:
        pass
    lifecycle = reduce_request_state(lifecycle, "start")
    try:
        GPTState.last_lifecycle = lifecycle
    except Exception:
        pass

    def _clear_notify_suppress():
        try:
            if getattr(GPTState, "suppress_inflight_notify_request_id", None) == request_id:
                GPTState.suppress_inflight_notify_request_id = None
        except Exception:
            pass

    def _handle_cancelled_request() -> str:
        emit_fail("cancelled", request_id=request_id)
        notify("GPT: Request cancelled")
        try:
            GPTState.last_streaming_snapshot = {}
        except Exception:
            pass
        cancel_active_request()
        _clear_notify_suppress()
        return format_message("")

    def _handle_request_error(exc: Exception) -> None:
        nonlocal lifecycle
        emit_fail(str(exc), request_id=request_id)
        lifecycle = reduce_request_state(lifecycle, "error")
        try:
            GPTState.last_lifecycle = lifecycle
        except Exception:
            pass

    def _handle_max_attempts_exceeded() -> None:
        nonlocal lifecycle
        emit_fail("max_attempts_exceeded", request_id=request_id)
        lifecycle = reduce_request_state(lifecycle, "error")
        try:
            GPTState.last_lifecycle = lifecycle
        except Exception:
            pass
        notify("GPT request failed after max attempts.")
        raise RuntimeError("GPT request failed after max attempts.")

    started_at_ms = int(time.time() * 1000)
    try:
        print(
            f"[modelHelpers] send_request destination_kind={getattr(GPTState, 'current_destination_kind', '')} "
            f"prefer_canvas_progress={_prefer_canvas_progress()}"
        )
        try:
            phase = getattr(current_state(), "phase", None)
            print(f"[modelHelpers] initial request phase={phase}")
        except Exception:
            pass
    except Exception:
        pass
    if not _prefer_canvas_progress():
        try:
            from .pillCanvas import show_pill

            show_pill("Model: sending…", RequestPhase.SENDING)
        except Exception:
            pass

    provider = bound_provider()
    _ensure_request_supported(provider, GPTState.request)
    try:
        use_stream = bool(settings.get("user.model_streaming", True))
    except Exception:
        use_stream = True
    try:
        if not provider.features.get("streaming", True):
            use_stream = False
            print(
                f"[modelHelpers] provider '{provider.id}' disables streaming; using sync path"
            )
            _warn_streaming_disabled(provider)
    except Exception:
        provider = None
    print(f"[modelHelpers] streaming_enabled={use_stream}")
    if use_stream:
        try:
            print("[modelHelpers] invoking streaming request")
            # Logical lifecycle: first chunk observed.
            lifecycle = reduce_request_state(lifecycle, "stream_start")
            try:
                GPTState.last_lifecycle = lifecycle
            except Exception:
                pass
            message_content = _send_request_streaming(GPTState.request, request_id)
            # Only mark completed when we actually received content.
            if message_content is not None:
                lifecycle = reduce_request_state(lifecycle, "stream_end")
                try:
                    GPTState.last_lifecycle = lifecycle
                except Exception:
                    pass
        except CancelledRequest:
            lifecycle = reduce_request_state(lifecycle, "cancel")
            try:
                GPTState.last_lifecycle = lifecycle
            except Exception:
                pass
            try:
                print(
                    "[modelHelpers] send_request: streaming cancelled, aborting without fallback"
                )
                try:
                    phase = getattr(current_state(), "phase", None)
                    print(f"[modelHelpers] after streaming cancel phase={phase}")
                except Exception:
                    pass
            except Exception:
                pass
            try:
                set_controller(RequestUIController())
                emit_cancel(request_id=request_id)
                emit_reset()
                try:
                    phase_after_reset = getattr(current_state(), "phase", None)
                    print(f"[modelHelpers] after emit_reset phase={phase_after_reset}")
                except Exception:
                    pass
            except Exception:
                pass
            try:
                cancel_active_request()
            except Exception:
                pass
            try:
                _set_active_response(None)
            except Exception:
                pass
                try:
                    GPTState.text_to_confirm = ""
                    GPTState.last_meta = ""
                except Exception:
                    pass
                _clear_notify_suppress()
                return format_message("")
        except Exception as e:
            try:
                print(
                    f"[modelHelpers] streaming failed; retrying without stream ({e!r})"
                )
                traceback.print_exc()
            except Exception:
                pass
            message_content = None
        if message_content is None:
            try:
                print(
                    "[modelHelpers] streaming branch returned None (skipped or failed)"
                )
            except Exception:
                pass

    while message_content is None and attempts < max_attempts:
        try:
            state = current_state()
        except Exception:
            state = RequestState()
        if getattr(state, "cancel_requested", False):
            try:
                print("[modelHelpers] cancel detected before non-stream send; aborting")
                try:
                    phase = getattr(state, "phase", None)
                    print(f"[modelHelpers] fallback cancel state phase={phase}")
                except Exception:
                    pass
            except Exception:
                pass
            return _handle_cancelled_request()

        try:
            json_response = send_request_internal(GPTState.request)
        except GPTRequestError as e:
            _handle_request_error(e)
            raise
        except Exception as e:
            _handle_request_error(e)
            raise

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

    try:
        state_after = current_state()
    except Exception:
        state_after = RequestState()
    if getattr(state_after, "cancel_requested", False):
        lifecycle = reduce_request_state(lifecycle, "cancel")
        try:
            GPTState.last_lifecycle = lifecycle
        except Exception:
            pass
        return _handle_cancelled_request()

    if message_content is None:
        _handle_max_attempts_exceeded()

    try:
        print(
            f"[modelHelpers] message_content_len={len(message_content)} "
            f"preview='{message_content[:120].replace(chr(10), ' ')}'"
        )
    except Exception:
        pass
    # Non-stream completion path.
    lifecycle = reduce_request_state(lifecycle, "complete")
    try:
        GPTState.last_lifecycle = lifecycle
    except Exception:
        pass

    notify("GPT Task Completed")
    resp = message_content.strip()
    formatted_resp = strip_markdown(resp)

    answer_text, meta_text = split_answer_and_meta(formatted_resp)

    GPTState.last_response = answer_text
    GPTState.last_meta = meta_text
    last_recipe = getattr(GPTState, "last_recipe", "") or ""
    try:
        print(f"[modelHelpers] logging recipe={last_recipe!r}")
    except Exception:
        pass
    # Keep the streaming buffer aligned with the final answer so inflight views
    # or immediate redraws have content even if the stream was sparse.
    GPTState.text_to_confirm = answer_text
    response = format_message(answer_text)

    # When using the canvas for progress (response window/default), refresh it
    # after the final content is ready so the body redraws with the answer.
    if _should_show_response_canvas():
        _refresh_response_canvas()

    if GPTState.thread_enabled:
        GPTState.push_thread(
            {
                "role": "assistant",
                "content": [response],
            }
        )

    emit_complete(request_id=request_id)

    duration_ms = int(time.time() * 1000) - started_at_ms

    try:
        axes = getattr(GPTState, "last_axes", {}) or {}
        prompt_text = append_entry_from_request(
            request_id=request_id,
            request=getattr(GPTState, "request", None),
            answer_text=answer_text,
            meta_text=meta_text,
            recipe=last_recipe,
            started_at_ms=started_at_ms,
            duration_ms=duration_ms,
            axes=axes,
            provider_id=getattr(provider, "id", ""),
        )
        try:
            print(
                "[modelHelpers] append_entry_from_request succeeded "
                f"prompt_len={len(prompt_text or '')} answer_len={len(answer_text)}"
            )
        except Exception:
            pass
    except Exception as e:
        try:
            print(f"[modelHelpers] append_entry_from_request failed: {e}")
        except Exception:
            pass

    _clear_notify_suppress()
    return response


def send_request_async():
    """Run send_request in a background thread and return a handle."""
    return start_async(send_request)


__all__ = [
    "send_request",
    "send_request_async",
    "send_request_internal",
    "GPTRequestError",
]


class GPTRequestError(Exception):
    """Custom exception for errors during GPT API requests."""

    def __init__(self, status_code, error_info):
        super().__init__(
            f"GPT API request failed with status {status_code}: {error_info}"
        )
        self.status_code = status_code
        self.error_info = error_info


class CancelledRequest(RuntimeError):
    """Raised internally when a cancel is requested mid-stream."""

    pass


def send_request_internal(request):
    provider = bound_provider()
    _ensure_request_supported(provider, request)
    try:
        TOKEN = get_token(provider)
    except MissingAPIKeyError:
        _show_provider_error("Missing API key", provider.id, provider.api_key_env)
        raise
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}",
    }

    # Capture the raw request for debugging so it can be inspected or copied
    # after the fact, regardless of whether stdout is visible.
    GPTState.last_raw_request = request

    if GPTState.debug_enabled:
        print(request)

    url: str = provider_endpoint(provider)  # type: ignore
    timeout_seconds: int = settings.get("user.model_request_timeout_seconds", 120)  # type: ignore
    notify("GPT Sending Request")
    try:
        raw_response = requests.post(
            url, headers=headers, data=json.dumps(request), timeout=timeout_seconds
        )
        _set_active_response(raw_response)
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
    _set_active_response(None)
    return json_response


class ClipboardImageError(Exception):
    """Custom exception for clipboard image errors."""

    pass


class ClipboardImageUnsupportedProvider(ClipboardImageError):
    """Raised when the active provider does not support vision/image sources."""

    def __init__(self, provider_id: str):
        super().__init__(f"Provider '{provider_id}' does not support image clipboard")
        self.provider_id = provider_id


def get_clipboard_image():
    """Get an image from the clipboard and return it as a base64-encoded string."""
    provider = bound_provider()
    if not provider.features.get("vision", False):
        _show_provider_error(
            "Vision/images not supported for this provider",
            provider.id,
            provider.api_key_env,
        )
        raise ClipboardImageUnsupportedProvider(provider.id)
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

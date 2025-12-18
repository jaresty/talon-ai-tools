import datetime
import os
import re
import traceback
from typing import Iterable, List, Sequence, Union, cast, Iterator, Dict, Optional

from ..lib.modelSource import GPTItem
from ..lib.modelTypes import GPTTextItem
from ..lib.modelConfirmationGUI import confirmation_gui
from talon import actions, clip, settings, ui
from ..lib.modelState import GPTState
from ..lib.axisJoin import axis_join
from ..lib.modelHelpers import (
    format_messages,
    initialise_destination_runtime_state,
    notify,
)
from ..lib.HTMLBuilder import Builder
from ..lib.promptPipeline import PromptResult
from ..lib.suggestionCoordinator import (
    last_recipe_snapshot,
    recipe_header_lines_from_snapshot,
)


def _set_destination_kind(kind: str) -> None:
    try:
        GPTState.current_destination_kind = (kind or "").lower()
    except Exception:
        pass


def _response_canvas_showing() -> bool:
    """Return True when the canvas-based response viewer is currently open.

    When the response window is showing, destination insertions that would
    normally paste or type into the target application should instead route
    through the window/confirmation flow so users can review output first.
    """
    try:
        return bool(getattr(GPTState, "response_canvas_showing", False))
    except Exception:
        return False


def _trace_canvas_flow(event: str, **data) -> None:
    try:
        enabled = bool(settings.get("user.gpt_trace_canvas_flow", 1))
    except Exception:
        enabled = False
    if not enabled:
        return
    parts = [f"[canvas-flow] {event}"]
    if data:
        details = " ".join(f"{key}={value!r}" for key, value in data.items())
        parts.append(details)
    message = " ".join(parts)
    try:
        print(message)
    except Exception:
        pass
    try:
        stack = "".join(traceback.format_stack(limit=8))
        if stack:
            print(stack)
    except Exception:
        pass


PromptPayload = Union[PromptResult, Sequence[GPTItem], GPTItem]


def _iter_text_items(items: Iterable[GPTItem]) -> Iterator[GPTTextItem]:
    for item in items:
        if item["type"] == "text":
            yield cast(GPTTextItem, item)


def _coerce_prompt_result(payload: PromptPayload) -> PromptResult:
    if isinstance(payload, PromptResult):
        return payload
    if hasattr(payload, "messages") and hasattr(payload, "presentation_for"):
        return cast(PromptResult, payload)
    if isinstance(payload, dict):
        return PromptResult.from_messages([payload])
    return PromptResult.from_messages(payload)


def _emit_paragraphs(builder: Builder, lines: List[str]) -> None:
    """
    Render logical paragraphs from a sequence of lines.

    - Consecutive non-empty lines are joined with spaces into a single
      paragraph.
    - Blank lines start a new paragraph.
    """
    buffer: List[str] = []
    for raw in lines:
        line = raw.rstrip()
        if not line:
            if buffer:
                builder.p(" ".join(buffer))
                buffer = []
            continue
        buffer.append(line)
    if buffer:
        builder.p(" ".join(buffer))


def _emit_rich_answer(builder: Builder, lines: List[str]) -> None:
    """
    Render answer text with basic awareness of paragraphs and bullet lists.

    - Groups contiguous non-empty, non-bullet lines into paragraphs.
    - Groups contiguous bullet-style lines (starting with '-' or '*') into
      unordered lists.
    """
    paragraph_buffer: List[str] = []
    bullet_buffer: List[str] = []

    def flush_paragraphs() -> None:
        nonlocal paragraph_buffer
        if paragraph_buffer:
            _emit_paragraphs(builder, paragraph_buffer)
            paragraph_buffer = []

    def flush_bullets() -> None:
        nonlocal bullet_buffer
        if bullet_buffer:
            builder.ul(*bullet_buffer)
            bullet_buffer = []

    for raw in lines:
        line = raw.rstrip()
        if not line:
            # Blank line: end any current group.
            flush_bullets()
            flush_paragraphs()
            continue

        stripped = line.lstrip()
        is_bullet = stripped.startswith("- ") or stripped.startswith("* ")
        if is_bullet:
            # Move any pending paragraph content out before starting bullets.
            flush_paragraphs()
            # Drop the leading bullet marker for display purposes.
            bullet_text = stripped[2:].strip()
            bullet_buffer.append(bullet_text or stripped)
        else:
            # Non-bullet content: end any bullet group and continue paragraphing.
            flush_bullets()
            paragraph_buffer.append(line)

    flush_bullets()
    flush_paragraphs()


def _parse_meta(meta_text: str) -> Dict[str, Union[str, List[str]]]:
    """
    Best-effort parse of the structured meta bundle into named sections.

    The parser is intentionally conservative: when it cannot confidently
    classify content, it leaves it in the interpretation/extra buckets so that
    no information is lost.
    """
    result: Dict[str, Union[str, List[str]]] = {
        "interpretation": "",
        "assumptions": [],
        "gaps": [],
        "better_prompt": "",
        "suggestion": "",
        "extra": [],
    }
    if not meta_text.strip():
        return result

    lines = [line.strip() for line in meta_text.splitlines() if line.strip()]
    if not lines:
        return result

    # Strip markdown heading markers but keep the text.
    cleaned: List[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            # Collapse "## Heading ..." into just "Heading ..." for parsing.
            stripped = stripped.lstrip("#").strip()
        cleaned.append(stripped or line)

    section: str = "interpretation"

    def append_text(key: str, text: str) -> None:
        current = result.get(key, "")
        if isinstance(current, str):
            if current:
                result[key] = f"{current} {text}".strip()
            else:
                result[key] = text.strip()

    for line in cleaned:
        lower = line.lower()
        # Skip bare "Model interpretation" markers after stripping markdown
        # headings; they act as section headers rather than content.
        if lower == "model interpretation":
            continue
        # Label-based switches.
        if lower.startswith("interpretation:"):
            section = "interpretation"
            append_text("interpretation", line.split(":", 1)[1].strip())
            continue
        if lower.startswith("assumptions/constraints:") or lower.startswith(
            "assumptions:"
        ):
            section = "assumptions"
            tail = line.split(":", 1)[1].strip()
            if tail:
                cast(List[str], result["assumptions"]).append(tail)
            continue
        if (
            lower.startswith("gaps/caveats to verify:")
            or lower.startswith("gaps/caveats:")
            or lower.startswith("gaps:")
        ):
            section = "gaps"
            tail = line.split(":", 1)[1].strip()
            if tail:
                cast(List[str], result["gaps"]).append(tail)
            continue
        if lower.startswith("improved prompt:") or lower.startswith("better prompt:"):
            section = "better_prompt"
            append_text("better_prompt", line.split(":", 1)[1].strip())
            continue
        if lower.startswith("suggestion:"):
            section = "suggestion"
            suggestion_text = line.split(":", 1)[1].strip()
            if suggestion_text:
                result["suggestion"] = suggestion_text
            continue

        # Bullets under assumptions/gaps.
        if line.startswith("- ") or line.startswith("* "):
            tail = line[2:].strip()
            if section == "assumptions":
                cast(List[str], result["assumptions"]).append(tail)
            elif section == "gaps":
                cast(List[str], result["gaps"]).append(tail)
            else:
                cast(List[str], result["extra"]).append(tail)
            continue

        # Fallback: attribute text to the current section or extras.
        if section == "interpretation":
            append_text("interpretation", line)
        elif section == "better_prompt":
            append_text("better_prompt", line)
        elif section == "suggestion":
            if not result["suggestion"]:
                result["suggestion"] = line
            else:
                cast(List[str], result["extra"]).append(line)
        else:
            cast(List[str], result["extra"]).append(line)

    return result


class ModelDestination:
    kind = "window"

    def __init__(self) -> None:
        initialise_destination_runtime_state(self)

    def insert(self, gpt_output: PromptPayload):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("default")
        # Always route through the confirmation surface (canvas-based viewer),
        # even for long responses. Opening a browser becomes an explicit user
        # action rather than an automatic fallback.
        _trace_canvas_flow(
            "confirmation_append",
            dest=getattr(self, "kind", "window"),
            confirmation_showing=getattr(confirmation_gui, "showing", False),
        )
        actions.user.confirmation_gui_append(presentation)

    def _textarea_available_now(self) -> bool:
        method = getattr(self, "inside_textarea", None)
        if callable(method):
            try:
                return bool(method())
            except Exception:
                return False
        return False

    def _complete_via_window(self, result: PromptResult) -> None:
        if getattr(self, "_completed_via_window", False):
            return
        _trace_canvas_flow(
            "complete_via_window.start",
            dest=getattr(self, "kind", "window"),
            current_kind=getattr(GPTState, "current_destination_kind", None),
        )
        _set_destination_kind("window")
        try:
            GPTState.current_destination_kind = "window"
        except Exception:
            pass
        try:
            self._promoted_to_window = True
        except Exception:
            pass
        try:
            self._effective_destination_kind = "window"
        except Exception:
            pass
        ModelDestination.insert(self, result)
        _trace_canvas_flow(
            "complete_via_window.end",
            dest=getattr(self, "kind", "window"),
            completed_via_window=getattr(self, "_completed_via_window", False),
        )
        try:
            self._completed_via_window = True
        except Exception:
            pass

    def _ensure_textarea_and_maybe_fallback(self, result: PromptResult) -> bool:
        if getattr(self, "_initial_promoted_to_window", False):
            _trace_canvas_flow(
                "fallback_to_window",
                dest=getattr(self, "kind", "window"),
                trigger="initial_promoted_to_window",
            )
            self._complete_via_window(result)
            return False
        if _response_canvas_showing():
            _trace_canvas_flow(
                "fallback_to_window",
                dest=getattr(self, "kind", "window"),
                trigger="canvas_already_showing",
            )
            _trace_canvas_flow(
                "fallback_skip_close",
                dest=getattr(self, "kind", "window"),
            )
            self._complete_via_window(result)
            return False

        expects_textarea = getattr(self, "_expects_textarea_insert", None)
        if expects_textarea is None:
            expects_textarea = self._textarea_available_now()
            try:
                self._expects_textarea_insert = expects_textarea
            except Exception:
                pass

        if expects_textarea:
            if self._textarea_available_now():
                return True
            _trace_canvas_flow(
                "fallback_to_window",
                dest=getattr(self, "kind", "window"),
                trigger="expected_textarea_lost",
            )
            self._complete_via_window(result)
            return False

        initial_inside = getattr(self, "_initial_inside_textarea", None)
        if initial_inside is None:
            initial_inside = self._textarea_available_now()
            try:
                self._initial_inside_textarea = initial_inside
            except Exception:
                pass

        if initial_inside and self._textarea_available_now():
            return True

        _trace_canvas_flow(
            "fallback_to_window",
            dest=getattr(self, "kind", "window"),
            trigger="textarea_unavailable",
            initial_inside=initial_inside,
        )
        self._complete_via_window(result)
        return False

    # If this isn't working, you may need to turn on dication for electron apps
    #  ui.apps(bundle="com.microsoft.VSCode")[0].element.AXManualAccessibility = True
    def inside_textarea(self):
        debug_enabled = bool(getattr(GPTState, "debug_enabled", False))

        def log_detection(
            result: bool,
            reason: str,
            *,
            info: Optional[Dict[str, object]] = None,
            error: Optional[Exception] = None,
            force: bool = False,
        ) -> None:
            if not (force or debug_enabled or not result):
                return
            parts = [
                f"[modelDestination] inside_textarea={result} reason={reason}",
            ]
            if info:
                value = info.get("AXValue")
                if isinstance(value, str):
                    value_summary = f"str(len={len(value)})"
                elif value is None:
                    value_summary = "None"
                else:
                    value_summary = type(value).__name__
                fields = [
                    f"AXRole={info.get('AXRole')!r}",
                    f"AXSubrole={info.get('AXSubrole')!r}",
                    f"AXRoleDescription={info.get('AXRoleDescription')!r}",
                    f"AXSupportsTextSelection={info.get('AXSupportsTextSelection')!r}",
                    f"AXEditable={info.get('AXEditable')!r}",
                    f"AXValue={value_summary}",
                ]
                parts.append("; " + ", ".join(fields))
            if error is not None:
                parts.append(f" error={error}")
            print(" ".join(parts))

        def fallback_reason() -> Optional[str]:
            try:
                language = actions.code.language()
                if isinstance(language, str) and language.strip():
                    return f"fallback via language context '{language.strip()}'"
            except Exception:
                pass
            try:
                app_name = actions.app.name()
                if isinstance(app_name, str):
                    lowered = app_name.lower()
                    tokens = {
                        "code",
                        "studio",
                        "editor",
                        "text",
                        "notebook",
                        "notes",
                        "slack",
                        "chat",
                    }
                    if any(token in lowered for token in tokens):
                        return f"fallback via app name '{app_name}'"
            except Exception:
                pass
            try:
                bundle = actions.app.bundle()
                if isinstance(bundle, str):
                    lowered = bundle.lower()
                    known_bundles = (
                        "com.microsoft.vscode",
                        "com.microsoft.vscodeinsiders",
                        "com.visualstudio.code",
                        "com.jetbrains.",
                        "com.apple.dt.xcode",
                        "org.gnu.emacs",
                    )
                    if any(token in lowered for token in known_bundles):
                        return f"fallback via app bundle '{bundle}'"
            except Exception:
                pass
            return None

        try:
            element = ui.focused_element()
        except Exception as error:  # noqa: PERF203 - transparency outweighs perf here
            reason = fallback_reason()
            if reason:
                log_detection(True, reason, error=error, force=True)
                return True
            log_detection(False, "focused element lookup failed", error=error)
            return False

        if not element or not hasattr(element, "get"):
            reason = fallback_reason()
            if reason:
                log_detection(True, reason, force=True)
                return True
            log_detection(False, "no focused element")
            return False

        def attr(name: str):
            try:
                return element.get(name)
            except Exception:
                return None

        info = cast(
            Dict[str, object],
            {
                "AXRole": attr("AXRole"),
                "AXSubrole": attr("AXSubrole"),
                "AXRoleDescription": attr("AXRoleDescription"),
                "AXSupportsTextSelection": attr("AXSupportsTextSelection"),
                "AXEditable": attr("AXEditable"),
                "AXValue": attr("AXValue"),
            },
        )

        text_roles = {
            "AXTextArea",
            "AXTextField",
            "AXComboBox",
            "AXStaticText",
            "AXSearchField",
        }

        def is_text_role(value):
            if not isinstance(value, str):
                return False
            if value in text_roles:
                return True
            return value.lower().startswith("axtext")

        role = info["AXRole"]
        subrole = info["AXSubrole"]
        role_description = info["AXRoleDescription"]
        supports_selection_raw = info["AXSupportsTextSelection"]
        value = info["AXValue"]
        editable_raw = info["AXEditable"]

        result = False
        reason = "no match"

        if is_text_role(role):
            result = True
            reason = "AXRole matches text role"
        elif is_text_role(subrole):
            result = True
            reason = "AXSubrole matches text role"
        elif isinstance(role_description, str) and role_description.lower() in {
            "text area",
            "text field",
            "text input",
            "editor",
        }:
            result = True
            reason = "AXRoleDescription indicates text input"
        elif bool(supports_selection_raw) and isinstance(value, str):
            result = True
            reason = "AXSupportsTextSelection with string AXValue"
        elif bool(editable_raw):
            result = True
            reason = "AXEditable is truthy"

        log_detection(result, reason, info=info)
        return result


class Above(ModelDestination):
    kind = "above"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return

        actions.key("left")
        actions.edit.line_insert_up()
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("above")
        actions.user.paste(presentation.paste_text)


class Chunked(ModelDestination):
    kind = "chunked"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return

        GPTState.last_was_pasted = True
        presentation = result.presentation_for("chunked")
        lines = presentation.browser_lines
        for i in range(0, len(lines), 10):
            chunk = "\n".join(lines[i : i + 10])
            actions.user.paste(chunk)
            actions.key("enter")


class Below(ModelDestination):
    kind = "below"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return
        actions.key("right")
        actions.edit.line_insert_down()
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("below")
        actions.user.paste(presentation.paste_text)


class Clipboard(ModelDestination):
    kind = "clipboard"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("clipboard")
        clip.set_text(presentation.paste_text)


class File(ModelDestination):
    kind = "file"

    def insert(self, gpt_output):
        """Write a human-readable response snapshot to a markdown file.

        This destination focuses on the model's response (and, when cheaply
        available, its prompt/context) rather than raw HTTP logs.
        """
        result = _coerce_prompt_result(gpt_output)
        from .modelHelpers import build_exchange_snapshot  # type: ignore

        snapshot = build_exchange_snapshot(result, kind="response")

        # Resolve base directory from user setting, with a sensible default.
        try:
            base = settings.get("user.model_source_save_directory")
            if isinstance(base, str) and base.strip():
                base_dir = os.path.expanduser(base)
            else:
                raise ValueError("empty base directory setting")
        except Exception:
            base_dir = os.path.join(os.path.expanduser("~"), "talon-ai-model-sources")

        try:
            os.makedirs(base_dir, exist_ok=True)
        except Exception as exc:
            notify(f"GPT: Could not create file destination directory: {exc}")
            return

        now = datetime.datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%dT%H-%M-%SZ")

        # Build a short slug from the last recipe/axes for context.
        axes_tokens = getattr(GPTState, "last_axes", {}) or {}

        static_prompt = getattr(GPTState, "last_static_prompt", "") or ""
        slug_bits = []
        if static_prompt:
            slug_bits.append(static_prompt)
        last_completeness = axis_join(
            axes_tokens,
            "completeness",
            getattr(GPTState, "last_completeness", "") or "",
        )
        last_scope = axis_join(
            axes_tokens, "scope", getattr(GPTState, "last_scope", "") or ""
        )
        last_method = axis_join(
            axes_tokens, "method", getattr(GPTState, "last_method", "") or ""
        )
        last_form = axis_join(
            axes_tokens, "form", getattr(GPTState, "last_form", "") or ""
        )
        last_channel = axis_join(
            axes_tokens, "channel", getattr(GPTState, "last_channel", "") or ""
        )
        last_directional = getattr(GPTState, "last_directional", "") or ""
        for value in (
            last_completeness,
            last_scope,
            last_method,
            last_form,
            last_channel,
            last_directional,
        ):
            if value:
                slug_bits.append(value)

        def _slug(value: str) -> str:
            value = (value or "").strip().lower().replace(" ", "-")
            return re.sub(r"[^a-z0-9._-]+", "", value)

        slug = "-".join(_slug(bit) for bit in slug_bits if bit) or "response"
        filename = f"{timestamp}-{slug}.md"
        path = os.path.join(base_dir, filename)

        # Assemble a human-oriented header and sections.
        header_lines = [
            f"saved_at: {now.isoformat()}Z",
            "kind=response",
        ]
        model_name = settings.get("user.openai_model")
        if isinstance(model_name, str) and model_name.strip():
            header_lines.append(f"model: {model_name}")

        # Reuse the shared recipe/axis header façade so response snapshots
        # stay aligned with source snapshots and recap views.
        try:
            snapshot_header = recipe_header_lines_from_snapshot(last_recipe_snapshot())
            header_lines.extend(snapshot_header)
        except Exception:
            # Fall back to the previous inline behaviour if the façade is
            # unavailable or misconfigured in this runtime.
            recipe_value = getattr(GPTState, "last_recipe", "") or ""
            if recipe_value:
                header_lines.append(f"recipe: {recipe_value}")
            directional = getattr(GPTState, "last_directional", "") or ""
            if directional:
                header_lines.append(f"directional: {directional}")
            for axis_key, axis_value in (
                ("completeness", last_completeness),
                ("scope", last_scope),
                ("method", last_method),
                ("form", last_form),
                ("channel", last_channel),
            ):
                if axis_value:
                    header_lines.append(f"{axis_key}_tokens: {axis_value}")

        prompt_text = snapshot.get("prompt_text", "") or ""
        response_text = snapshot.get("response_text", "") or ""
        meta_text = snapshot.get("meta_text", "") or ""

        sections = []
        if prompt_text.strip():
            sections.append("# Prompt / Context\n" + prompt_text.strip() + "\n")
        sections.append("# Response\n" + response_text.strip() + "\n")
        if meta_text.strip():
            sections.append("# Meta\n" + meta_text.strip() + "\n")

        content = "\n".join(header_lines) + "\n---\n\n" + "\n\n".join(sections)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as exc:
            notify(f"GPT: Failed to write file destination output: {exc}")
            return

        notify(f"GPT: Saved response to {path}")


class Snip(ModelDestination):
    kind = "snip"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return
        presentation = result.presentation_for("snip")
        actions.user.insert_snippet(presentation.paste_text)


class Context(ModelDestination):
    kind = "context"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        for message in _iter_text_items(result.messages):
            GPTState.push_context(message)


class Query(ModelDestination):
    kind = "query"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.push_query(format_messages("user", result.messages))


class NewContext(ModelDestination):
    kind = "newContext"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.clear_context()
        for message in _iter_text_items(result.messages):
            GPTState.push_context(message)


class AppendClipboard(ModelDestination):
    kind = "appendClipboard"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("appendClipboard")
        if clip.text() is not None:
            clip.set_text(clip.text() + "\n" + presentation.paste_text)  # type: ignore
        else:
            clip.set_text(presentation.paste_text)


class Browser(ModelDestination):
    kind = "browser"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("browser")
        builder = Builder()
        builder.h1("Talon GPT Result")

        # Mirror the confirmation GUI's recipe recap so the browser view
        # carries the same orientation cues.
        axes_tokens = getattr(GPTState, "last_axes", {}) or {}

        static_prompt = getattr(GPTState, "last_static_prompt", "") or ""
        axis_parts: list[str] = []
        if static_prompt:
            axis_parts.append(static_prompt)
        last_completeness = axis_join(
            axes_tokens,
            "completeness",
            getattr(GPTState, "last_completeness", "") or "",
        )
        last_scope = axis_join(
            axes_tokens, "scope", getattr(GPTState, "last_scope", "") or ""
        )
        last_method = axis_join(
            axes_tokens, "method", getattr(GPTState, "last_method", "") or ""
        )
        last_form = axis_join(
            axes_tokens, "form", getattr(GPTState, "last_form", "") or ""
        )
        last_channel = axis_join(
            axes_tokens, "channel", getattr(GPTState, "last_channel", "") or ""
        )
        last_directional = axis_join(
            axes_tokens,
            "directional",
            getattr(GPTState, "last_directional", "") or "",
        )
        for value in (
            last_completeness,
            last_scope,
            last_method,
            last_form,
            last_channel,
            last_directional,
        ):
            if value:
                axis_parts.append(value)

        recipe_tokens = " · ".join(axis_parts) if axis_parts else ""
        last_recipe_value = getattr(GPTState, "last_recipe", "") or ""
        recipe = recipe_tokens or last_recipe_value
        # If the catalog-derived tokens are sparse (for example, only static
        # prompt + directional), prefer the richer last_recipe string when present.
        if last_recipe_value:
            populated_axes = sum(
                1
                for v in (
                    last_completeness,
                    last_scope,
                    last_method,
                    last_form,
                    last_channel,
                )
                if v
            )
            if len(axis_parts) < 4 or populated_axes < 3:
                recipe = last_recipe_value
        if recipe:
            builder.h2("Prompt recap")
            directional = getattr(GPTState, "last_directional", "") or ""
            recipe_text = recipe
            grammar_recipe = recipe.replace(" · ", " ")
            if directional and directional not in recipe_text:
                recipe_text = f"{recipe_text} · {directional}"
                grammar_recipe = f"{grammar_recipe} {directional}"
            grammar_phrase = f"model run {grammar_recipe}"

            builder.p(f"Recipe: {recipe_text}")
            builder.p(f"Say: {grammar_phrase}")

            # When possible, include a prompt-specific pattern menu hint that
            # matches the confirmation GUI + quick-help guidance.
            if static_prompt:
                builder.p(
                    f"Tip: Say 'model show grammar' for a detailed breakdown, "
                    f"or 'model pattern menu {static_prompt}' to explore nearby recipes."
                )

        meta = (
            getattr(presentation, "meta_text", "").strip()
            or getattr(GPTState, "last_meta", "").strip()
        )
        if meta:
            builder.h2("Model interpretation")
            parsed = _parse_meta(meta)
            interpretation = cast(str, parsed.get("interpretation", ""))
            assumptions = cast(List[str], parsed.get("assumptions", []))
            gaps = cast(List[str], parsed.get("gaps", []))
            better = cast(str, parsed.get("better_prompt", ""))
            suggestion = cast(str, parsed.get("suggestion", ""))
            extra = cast(List[str], parsed.get("extra", []))

            if interpretation:
                _emit_paragraphs(builder, [interpretation])
            if assumptions:
                builder.h3("Assumptions/constraints")
                builder.ul(*assumptions)
            if gaps:
                builder.h3("Gaps and checks")
                builder.ul(*gaps)
            if better:
                builder.h3("Better prompt")
                _emit_paragraphs(builder, [better])
            if suggestion:
                builder.h3("Axis tweak suggestion")
                builder.p(suggestion)
            if extra:
                _emit_paragraphs(builder, extra)
            builder.p(
                "Note: This interpretation section is diagnostic and is not pasted into documents; "
                "use the Response section below when copying content into other tools."
            )

        builder.h2("Response")

        _emit_rich_answer(builder, presentation.browser_lines)
        builder.render()


class TextToSpeech(ModelDestination):
    kind = "textToSpeech"

    def insert(self, gpt_output):
        try:
            result = _coerce_prompt_result(gpt_output)
            presentation = result.presentation_for("tts")
            actions.user.tts(presentation.paste_text)
        except KeyError:
            notify("GPT Failure: text to speech is not installed")


class Chain(ModelDestination):
    kind = "chain"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("chain")
        actions.user.paste(presentation.paste_text)
        actions.user.gpt_select_last()


class Paste(ModelDestination):
    kind = "paste"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)

        if not self._ensure_textarea_and_maybe_fallback(result):
            return

        GPTState.last_was_pasted = True
        presentation = result.presentation_for("paste")
        actions.user.paste(presentation.paste_text)


class ForcePaste(ModelDestination):
    kind = "forcePaste"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)

        if not self._ensure_textarea_and_maybe_fallback(result):
            return

        GPTState.last_was_pasted = True
        presentation = result.presentation_for("paste")
        actions.user.paste(presentation.paste_text)


class Draft(ModelDestination):
    kind = "draft"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("draft")
        actions.user.draft_editor_open()
        actions.user.delete_all()
        actions.user.paste(presentation.paste_text)


class Typed(ModelDestination):
    kind = "typed"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self._ensure_textarea_and_maybe_fallback(result):
            return
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("typed")
        actions.auto_insert(presentation.paste_text)


class Thread(ModelDestination):
    kind = "thread"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.push_thread(format_messages("user", result.messages))
        actions.user.confirmation_gui_refresh_thread()


class NewThread(ModelDestination):
    kind = "newThread"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.new_thread()
        GPTState.push_thread(format_messages("user", result.messages))
        actions.user.confirmation_gui_refresh_thread()


class Stack(ModelDestination):
    kind = "stack"

    def __init__(self, stack_name):
        super().__init__()
        self.stack_name = stack_name

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.append_stack(result.messages, self.stack_name)


class Default(ModelDestination):
    kind = "default"

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("default")
        if confirmation_gui.showing:
            GPTState.last_was_pasted = True
            actions.user.paste(presentation.paste_text)
        else:
            actions.user.confirmation_gui_append(presentation)


class Silent(ModelDestination):
    kind = "silent"

    def insert(self, gpt_output):
        # Consume the result without inserting or opening any UI surfaces.
        _coerce_prompt_result(gpt_output)
        _set_destination_kind("silent")


def create_model_destination(destination_type: str) -> ModelDestination:
    if destination_type == "":
        destination_type = settings.get("user.model_default_destination")
    destination_map = {
        "above": Above,
        "below": Below,
        "chunked": Chunked,
        "clipboard": Clipboard,
        "snip": Snip,
        "context": Context,
        "query": Query,
        "newContext": NewContext,
        "appendClipboard": AppendClipboard,
        "browser": Browser,
        "textToSpeech": TextToSpeech,
        "chain": Chain,
        "paste": Paste,
        "forcePaste": ForcePaste,
        "typed": Typed,
        "thread": Thread,
        "newThread": NewThread,
        "draft": Draft,
        "silent": Silent,
        "file": File,
    }

    if destination_type == "window":
        destination = ModelDestination()
        initialise_destination_runtime_state(destination)
        return destination

    destination_cls = destination_map.get(destination_type)
    if destination_cls is not None:
        destination = destination_cls()
        initialise_destination_runtime_state(destination)
        return destination

    destination = Default()
    initialise_destination_runtime_state(destination)
    return destination

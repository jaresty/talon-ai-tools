from typing import Iterable, List, Sequence, Union, cast, Iterator, Dict

from ..lib.modelSource import GPTItem
from ..lib.modelTypes import GPTTextItem
from ..lib.modelConfirmationGUI import confirmation_gui
from talon import actions, clip, settings, ui
from ..lib.modelState import GPTState
from ..lib.modelHelpers import format_messages, notify
from ..lib.HTMLBuilder import Builder
from ..lib.promptPipeline import PromptResult


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
    def insert(self, gpt_output: PromptPayload):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("default")
        if presentation.open_browser:
            Browser().insert(result)
        else:
            actions.user.confirmation_gui_append(presentation)

    # If this isn't working, you may need to turn on dication for electron apps
    #  ui.apps(bundle="com.microsoft.VSCode")[0].element.AXManualAccessibility = True
    def inside_textarea(self):
        try:
            return ui.focused_element().get("AXRole") in [
                "AXTextArea",
                "AXTextField",
                "AXComboBox",
                "AXStaticText",
            ]
        except Exception as e:
            # Handle exception or log error
            print(f"An error occurred: {e}")
            return False


class Above(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)

        actions.key("left")
        actions.edit.line_insert_up()
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("above")
        actions.user.paste(presentation.paste_text)


class Chunked(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)

        GPTState.last_was_pasted = True
        presentation = result.presentation_for("chunked")
        lines = presentation.browser_lines
        for i in range(0, len(lines), 10):
            chunk = "\n".join(lines[i : i + 10])
            actions.user.paste(chunk)
            actions.key("enter")


class Below(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)
        actions.key("right")
        actions.edit.line_insert_down()
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("below")
        actions.user.paste(presentation.paste_text)


class Clipboard(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("clipboard")
        clip.set_text(presentation.paste_text)


class Snip(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)
        presentation = result.presentation_for("snip")
        actions.user.insert_snippet(presentation.paste_text)


class Context(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        for message in _iter_text_items(result.messages):
            GPTState.push_context(message)


class Query(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.push_query(format_messages("user", result.messages))


class NewContext(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.clear_context()
        for message in _iter_text_items(result.messages):
            GPTState.push_context(message)


class AppendClipboard(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("appendClipboard")
        if clip.text() is not None:
            clip.set_text(clip.text() + "\n" + presentation.paste_text)  # type: ignore
        else:
            clip.set_text(presentation.paste_text)


class Browser(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("browser")
        builder = Builder()
        builder.h1("Talon GPT Result")

        # Mirror the confirmation GUI's recipe recap so the browser view
        # carries the same orientation cues.
        if GPTState.last_recipe:
            builder.h2("Prompt recap")
            if getattr(GPTState, "last_directional", ""):
                recipe_text = (
                    f"{GPTState.last_recipe} · {GPTState.last_directional}"
                )
                grammar_phrase = (
                    f"model {GPTState.last_recipe.replace(' · ', ' ')} "
                    f"{GPTState.last_directional}"
                )
            else:
                recipe_text = GPTState.last_recipe
                grammar_phrase = (
                    f"model {GPTState.last_recipe.replace(' · ', ' ')}"
                )

            builder.p(f"Recipe: {recipe_text}")
            builder.p(f"Say: {grammar_phrase}")

            # When possible, include a prompt-specific pattern menu hint that
            # matches the confirmation GUI + quick-help guidance.
            static_prompt = GPTState.last_static_prompt or recipe_text.split(
                " · ", 1
            )[0].strip()
            if static_prompt:
                builder.p(
                    f"Tip: Say 'model show grammar' for a detailed breakdown, "
                    f"or 'model pattern menu {static_prompt}' to explore nearby recipes."
                )

        meta = getattr(presentation, "meta_text", "").strip() or getattr(
            GPTState, "last_meta", ""
        ).strip()
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
    def insert(self, gpt_output):
        try:
            result = _coerce_prompt_result(gpt_output)
            presentation = result.presentation_for("tts")
            actions.user.tts(presentation.paste_text)
        except KeyError:
            notify("GPT Failure: text to speech is not installed")


class Chain(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("chain")
        actions.user.paste(presentation.paste_text)
        actions.user.gpt_select_last()


class Paste(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("paste")
        actions.user.paste(presentation.paste_text)

class Draft(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("draft")
        actions.user.draft_editor_open()
        actions.user.delete_all()
        actions.user.paste(presentation.paste_text)


class Typed(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        if not self.inside_textarea():
            return super().insert(result)
        GPTState.last_was_pasted = True
        presentation = result.presentation_for("typed")
        actions.auto_insert(presentation.paste_text)


class Thread(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.push_thread(format_messages("user", result.messages))
        actions.user.confirmation_gui_refresh_thread()


class NewThread(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.new_thread()
        GPTState.push_thread(format_messages("user", result.messages))
        actions.user.confirmation_gui_refresh_thread()


class Stack(ModelDestination):
    def __init__(self, stack_name):
        self.stack_name = stack_name

    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        GPTState.append_stack(result.messages, self.stack_name)


class Default(ModelDestination):
    def insert(self, gpt_output):
        result = _coerce_prompt_result(gpt_output)
        presentation = result.presentation_for("default")
        if confirmation_gui.showing:
            GPTState.last_was_pasted = True
            actions.user.paste(presentation.paste_text)
        else:
            actions.user.confirmation_gui_append(presentation)


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
        "typed": Typed,
        "thread": Thread,
        "newThread": NewThread,
        "draft": Draft,
    }

    if destination_type == "window":
        return ModelDestination()

    destination_cls = destination_map.get(destination_type)
    if destination_cls is not None:
        return destination_cls()

    return Default()

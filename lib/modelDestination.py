from typing import Iterable, List, Sequence, Union, cast, Iterator

from ..lib.modelSource import GPTItem
from ..lib.modelTypes import GPTTextItem
from ..lib.modelConfirmationGUI import confirmation_gui
from talon import actions, clip, settings, ui
from ..lib.modelState import GPTState
from ..lib.modelHelpers import (
    format_messages,
    notify,
)
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
            for line in meta.splitlines():
                builder.p(line)

        builder.h2("Response")

        for line in presentation.browser_lines:
            builder.p(line)
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

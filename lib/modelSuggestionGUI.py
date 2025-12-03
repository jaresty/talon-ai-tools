from dataclasses import dataclass
from typing import List

from talon import Context, Module, actions, imgui, settings

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState
from .talonSettings import ApplyPromptConfiguration, modelPrompt
from .modelPatternGUI import (
    _axis_value,
    _parse_recipe,
    COMPLETENESS_MAP,
    METHOD_MAP,
    SCOPE_MAP,
    STYLE_MAP,
    DIRECTIONAL_MAP,
)

mod = Module()
ctx = Context()
mod.tag(
    "model_suggestion_window_open",
    desc="Tag for enabling suggestion commands when the suggestion window is open",
)


@dataclass
class Suggestion:
    name: str
    recipe: str


class SuggestionGUIState:
    suggestions: List[Suggestion] = []


def _refresh_suggestions_from_state() -> None:
    SuggestionGUIState.suggestions = [
        Suggestion(name=item["name"], recipe=item["recipe"])
        for item in GPTState.last_suggested_recipes
        if item.get("name") and item.get("recipe")
    ]


def _run_suggestion(suggestion: Suggestion) -> None:
    """Execute a suggested recipe as if spoken via the model grammar."""
    static_prompt, completeness, scope, method, style, directional = _parse_recipe(
        suggestion.recipe
    )
    if not static_prompt:
        actions.app.notify("Suggestion has no static prompt; cannot run")
        return

    actions.app.notify(f"Running suggestion: {suggestion.name}")

    class Match:
        pass

    match = Match()
    setattr(match, "staticPrompt", static_prompt)
    if completeness:
        setattr(
            match,
            "completenessModifier",
            _axis_value(completeness, COMPLETENESS_MAP),
        )
    if scope:
        setattr(match, "scopeModifier", _axis_value(scope, SCOPE_MAP))
    if method:
        setattr(match, "methodModifier", _axis_value(method, METHOD_MAP))
    if style:
        setattr(match, "styleModifier", _axis_value(style, STYLE_MAP))
    if directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(directional, DIRECTIONAL_MAP),
        )

    please_prompt = modelPrompt(match)

    config = ApplyPromptConfiguration(
        please_prompt=please_prompt,
        model_source=create_model_source(settings.get("user.model_default_source")),
        additional_model_source=None,
        model_destination=create_model_destination(
            settings.get("user.model_default_destination")
        ),
    )

    # Dismiss the suggestion window immediately on selection so the
    # execution result can use the normal confirmation/destination
    # surfaces without overlapping modals.
    actions.user.model_prompt_recipe_suggestions_gui_close()
    actions.user.gpt_apply_prompt(config)

    # Keep last_recipe concise and token-based to reinforce speakable grammar.
    recipe_parts = [static_prompt]
    for token in (completeness, scope, method, style):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = completeness or ""
    GPTState.last_scope = scope or ""
    GPTState.last_method = method or ""
    GPTState.last_style = style or ""
    GPTState.last_directional = directional or ""


@imgui.open()
def model_suggestion_gui(gui: imgui.GUI):
    gui.text("Prompt recipe suggestions")
    gui.line()
    gui.spacer()

    if not SuggestionGUIState.suggestions:
        gui.text("No suggestions available. Run 'model suggest' first.")
        gui.spacer()
    else:
        for suggestion in SuggestionGUIState.suggestions:
            if gui.button(suggestion.name):
                _run_suggestion(suggestion)
                return
            gui.text(f"Recipe: {suggestion.recipe}")
            grammar_phrase = f"model {suggestion.recipe.replace(' · ', ' ')}"
            gui.text(f"Say: {grammar_phrase}")
            gui.spacer()

    if gui.button("Close"):
        actions.user.model_prompt_recipe_suggestions_gui_close()


@mod.action_class
class UserActions:
    def model_prompt_recipe_suggestions_gui_open():
        """Open the prompt recipe suggestion GUI for the last suggestions."""
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return

        # Close related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_gui_close()
        except Exception:
            pass

        model_suggestion_gui.show()

    def model_prompt_recipe_suggestions_gui_close():
        """Close the prompt recipe suggestion GUI."""
        model_suggestion_gui.hide()

    def model_prompt_recipe_suggestions_run_index(index: int):
        """Run the Nth suggested recipe (1-based index)."""
        _refresh_suggestions_from_state()
        if not SuggestionGUIState.suggestions:
            actions.app.notify("No prompt recipe suggestions available")
            return
        if index <= 0 or index > len(SuggestionGUIState.suggestions):
            actions.app.notify(f"No suggestion numbered {index}")
            return
        _run_suggestion(SuggestionGUIState.suggestions[index - 1])

from dataclasses import dataclass
import os
from typing import Literal, Optional

from talon import Context, Module, actions, imgui, settings

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .modelState import GPTState

try:
    # Prefer the shared static prompt domain helpers when available.
    from .staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile
except ImportError:  # Talon may have an older module state cached
    from .staticPromptConfig import STATIC_PROMPT_CONFIG

    def get_static_prompt_profile(name: str):
        return STATIC_PROMPT_CONFIG.get(name)

    def get_static_prompt_axes(name: str) -> dict[str, str]:
        profile = STATIC_PROMPT_CONFIG.get(name, {})
        axes: dict[str, str] = {}
        for axis in ("completeness", "scope", "method", "style"):
            value = profile.get(axis)
            if value:
                axes[axis] = value
        return axes
from .talonSettings import ApplyPromptConfiguration, modelPrompt

mod = Module()
ctx = Context()
mod.tag(
    "model_prompt_pattern_window_open",
    desc="Tag for enabling prompt-specific pattern commands when the prompt pattern picker is open",
)


PatternDomain = Literal["prompt"]


class PromptPatternGUIState:
    static_prompt: Optional[str] = None


@dataclass(frozen=True)
class PromptAxisPattern:
    name: str
    description: str
    completeness: str
    scope: str
    method: str
    style: str
    directional: str


def _load_axis_map(filename: str) -> dict[str, str]:
    """Load a Talon list file as key -> description mapping."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
    mapping: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("list:")
                    or line == "-"
                ):
                    continue
                if ":" in line:
                    key, value = line.split(":", 1)
                    mapping[key.strip()] = value.strip()
    except FileNotFoundError:
        return {}
    return mapping


def _axis_value(token: str, mapping: dict[str, str]) -> str:
    """Map a short token (e.g. 'gist') to its full description, if available."""
    if not token:
        return ""
    return mapping.get(token, token)


COMPLETENESS_MAP = _load_axis_map("completenessModifier.talon-list")
SCOPE_MAP = _load_axis_map("scopeModifier.talon-list")
METHOD_MAP = _load_axis_map("methodModifier.talon-list")
STYLE_MAP = _load_axis_map("styleModifier.talon-list")
DIRECTIONAL_MAP = _load_axis_map("directionalModifier.talon-list")


PROMPT_PRESETS: list[PromptAxisPattern] = [
    PromptAxisPattern(
        name="Quick gist",
        description="Short, focused summary of the main points.",
        completeness="gist",
        scope="focus",
        method="",
        style="plain",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Deep narrow rigor",
        description="Thorough, narrow analysis with explicit reasoning.",
        completeness="full",
        scope="narrow",
        method="rigor",
        style="plain",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Bulleted summary",
        description="Compact bullet-point summary for quick scanning.",
        completeness="gist",
        scope="focus",
        method="",
        style="bullets",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Abstraction ladder",
        description="Place the focal problem in the middle, with reasons above and consequences below.",
        completeness="full",
        scope="focus",
        method="ladder",
        style="plain",
        directional="rog",
    ),
    PromptAxisPattern(
        name="Cluster items",
        description="Group related items into labeled categories; clustered output only.",
        completeness="full",
        scope="narrow",
        method="cluster",
        style="plain",
        directional="fog",
    ),
    PromptAxisPattern(
        name="Rank items",
        description="Sort items in order of importance to the audience.",
        completeness="full",
        scope="narrow",
        method="prioritize",
        style="plain",
        directional="fog",
    ),
]


def _run_prompt_pattern(static_prompt: str, pattern: PromptAxisPattern) -> None:
    """Execute a prompt-specific axis pattern as if spoken via the model grammar."""
    actions.app.notify(f"Running prompt pattern: {static_prompt} · {pattern.name}")

    class Match:
        pass

    match = Match()
    setattr(match, "staticPrompt", static_prompt)
    if pattern.completeness:
        setattr(
            match,
            "completenessModifier",
            _axis_value(pattern.completeness, COMPLETENESS_MAP),
        )
    if pattern.scope:
        setattr(match, "scopeModifier", _axis_value(pattern.scope, SCOPE_MAP))
    if pattern.method:
        setattr(match, "methodModifier", _axis_value(pattern.method, METHOD_MAP))
    if pattern.style:
        setattr(match, "styleModifier", _axis_value(pattern.style, STYLE_MAP))
    if pattern.directional:
        setattr(
            match,
            "directionalModifier",
            _axis_value(pattern.directional, DIRECTIONAL_MAP),
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

    actions.user.gpt_apply_prompt(config)

    # Keep last_recipe concise and token-based to reinforce speakable grammar.
    recipe_parts = [static_prompt]
    for token in (
        pattern.completeness,
        pattern.scope,
        pattern.method,
        pattern.style,
    ):
        if token:
            recipe_parts.append(token)
    GPTState.last_recipe = " · ".join(recipe_parts)
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = pattern.completeness or ""
    GPTState.last_scope = pattern.scope or ""
    GPTState.last_method = pattern.method or ""
    GPTState.last_style = pattern.style or ""
    GPTState.last_directional = pattern.directional or ""

    actions.user.prompt_pattern_gui_close()


@imgui.open()
def prompt_pattern_gui(gui: imgui.GUI):
    static_prompt = PromptPatternGUIState.static_prompt
    gui.text("Prompt patterns")
    gui.line()
    gui.spacer()

    if not static_prompt:
        gui.text("No static prompt selected.")
        gui.spacer()
    else:
        gui.text(f"Prompt: {static_prompt}")
        profile = get_static_prompt_profile(static_prompt)
        description = profile["description"] if profile is not None else None
        if description:
            gui.text(description)
            gui.spacer()

        axes: list[str] = []
        profile_axes = get_static_prompt_axes(static_prompt)
        for label in ("completeness", "scope", "method", "style"):
            value = profile_axes.get(label)
            if value:
                axes.append(f"{label.capitalize()}: {value}")
        if axes:
            gui.text("Profile defaults:")
            for line in axes:
                gui.text(f"  {line}")
            gui.spacer()

        gui.text("Grammar template:")
        gui.text(
            f"  model {static_prompt} [completeness] [scope] [method] [style] <directional lens>"
        )
        gui.spacer()

        gui.text("Patterns for this prompt:")
        gui.spacer()

        for pattern in PROMPT_PRESETS:
            recipe_tokens = [static_prompt]
            for token in (
                pattern.completeness,
                pattern.scope,
                pattern.method,
                pattern.style,
                pattern.directional,
            ):
                if token:
                    recipe_tokens.append(token)
            recipe_str = " · ".join(recipe_tokens)
            if gui.button(pattern.name):
                _run_prompt_pattern(static_prompt, pattern)
            gui.text(recipe_str)
            gui.text(f"Say (grammar): model {recipe_str.replace(' · ', ' ')}")
            gui.text(pattern.description)
            gui.spacer()

        gui.text("Tip: Say 'close pattern menu' to close this menu.")
        gui.spacer()

    if gui.button("Close"):
        actions.user.prompt_pattern_gui_close()


@mod.action_class
class UserActions:
    def prompt_pattern_gui_open_for_static_prompt(static_prompt: str):
        """Open the prompt pattern picker GUI for a specific static prompt"""
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_gui_close()
        except Exception:
            pass
        PromptPatternGUIState.static_prompt = static_prompt
        prompt_pattern_gui.show()
        ctx.tags = ["user.model_prompt_pattern_window_open"]

    def prompt_pattern_gui_close():
        """Close the prompt pattern picker GUI"""
        prompt_pattern_gui.hide()
        ctx.tags = []

    def prompt_pattern_run_preset(preset_name: str):
        """Run a prompt pattern by preset name for the current static prompt"""
        static_prompt = PromptPatternGUIState.static_prompt
        if not static_prompt:
            actions.app.notify("No prompt selected for patterns")
            return
        for pattern in PROMPT_PRESETS:
            if pattern.name.lower() == preset_name.lower():
                _run_prompt_pattern(static_prompt, pattern)
                break

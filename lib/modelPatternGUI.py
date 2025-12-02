from dataclasses import dataclass
import os
from typing import Literal

from talon import Context, Module, actions, imgui, settings

from .modelDestination import create_model_destination
from .modelSource import create_model_source
from .talonSettings import ApplyPromptConfiguration, modelPrompt
from .modelState import GPTState

mod = Module()
ctx = Context()
mod.tag(
    "model_pattern_window_open",
    desc="Tag for enabling model pattern commands when the pattern picker is open",
)


PatternDomain = Literal["coding", "writing"]


class PatternGUIState:
    domain: PatternDomain | None = None


@dataclass(frozen=True)
class PromptPattern:
    name: str
    description: str
    recipe: str
    domain: PatternDomain


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
        # If the list file is missing, fall back to using raw tokens.
        return {}
    return mapping


def _axis_value(token: str, mapping: dict[str, str]) -> str:
    """Map a short token (e.g. 'gist') to its full description, if available."""
    if not token:
        return ""
    return mapping.get(token, token)


COMPLETENESS_TOKENS = {
    "skim",
    "gist",
    "full",
    "max",
    "minimal",
    "deep",
}

SCOPE_TOKENS = {
    "narrow",
    "focus",
    "bound",
    "edges",
}

METHOD_TOKENS = {
    "steps",
    "plan",
    "rigor",
    "rewrite",
    "diagnose",
}

STYLE_TOKENS = {
    "plain",
    "tight",
    "bullets",
    "table",
    "code",
}

COMPLETENESS_MAP = _load_axis_map("completenessModifier.talon-list")
SCOPE_MAP = _load_axis_map("scopeModifier.talon-list")
METHOD_MAP = _load_axis_map("methodModifier.talon-list")
STYLE_MAP = _load_axis_map("styleModifier.talon-list")
DIRECTIONAL_MAP = _load_axis_map("directionalModifier.talon-list")

# NOTE: For spoken commands, Talon list values for completeness/scope/method/style
# are already the full "Important: …" descriptions. For pattern buttons, we
# translate the short tokens through the same lists so that modelPrompt/system
# see the same semantics, then override GPTState.last_recipe back to a concise,
# token-based recap for readability.


PATTERNS: list[PromptPattern] = [
    # Coding patterns
    PromptPattern(
        name="Debug bug",
        description="Deeply debug the current code or text.",
        recipe="debug · full · narrow · rigor · rog",
        domain="coding",
    ),
    PromptPattern(
        name="Fix locally",
        description="Fix issues in the current selection.",
        recipe="fix · full · narrow · steps · ong",
        domain="coding",
    ),
    PromptPattern(
        name="Explain flow",
        description="Explain how this code or text flows.",
        recipe="flow · gist · focus · steps · fog",
        domain="coding",
    ),
    PromptPattern(
        name="Summarize selection",
        description="Summarize the selected text.",
        recipe="describe · gist · focus · bullets · fog",
        domain="coding",
    ),
    PromptPattern(
        name="Extract todos",
        description="Turn this into a todo list.",
        recipe="todo · gist · focus · steps · bullets · ong",
        domain="coding",
    ),
    # Writing / product / reflection patterns
    PromptPattern(
        name="Summarize gist",
        description="One-paragraph summary of the text.",
        recipe="describe · gist · focus · plain · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Product framing",
        description="Frame this through a product lens.",
        recipe="product · gist · focus · steps · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Retro / reflect",
        description="Reflect on what happened and why.",
        recipe="retro · full · focus · steps · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Pain points",
        description="List and order key pain points.",
        recipe="pain · gist · focus · bullets · fog",
        domain="writing",
    ),
]


def _parse_recipe(recipe: str) -> tuple[str, str, str, str, str, str]:
    """Parse a human-readable recipe into static prompt + axes + directional lens.

    The recipe format is:
      staticPrompt · [axes…] · directional
    where intermediate tokens map into completeness/scope/method/style by membership.
    """
    tokens = [t.strip() for t in recipe.split("·")]
    if not tokens:
        return "", "", "", "", "", ""

    static_prompt = tokens[0]
    directional = tokens[-1] if len(tokens) > 1 else ""

    completeness = ""
    scope = ""
    method = ""
    style = ""

    for token in tokens[1:-1]:
        if token in COMPLETENESS_TOKENS:
            completeness = token
        elif token in SCOPE_TOKENS:
            scope = token
        elif token in METHOD_TOKENS:
            method = token
        elif token in STYLE_TOKENS:
            style = token

    return static_prompt, completeness, scope, method, style, directional


def _run_pattern(pattern: PromptPattern) -> None:
    """Execute a model pattern as if spoken via the model grammar."""
    (
        static_prompt,
        completeness,
        scope,
        method,
        style,
        directional,
    ) = _parse_recipe(pattern.recipe)

    # Give immediate feedback that the pattern was recognised and is running.
    actions.app.notify(f"Running pattern: {pattern.name}")

    # Build a lightweight object with the attributes expected by modelPrompt.
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

    actions.user.gpt_apply_prompt(config)
    # Override last_recipe to keep a concise, token-based recap even though the
    # system prompt receives the full axis descriptions.
    recipe_parts = [static_prompt]
    if completeness:
        recipe_parts.append(completeness)
    if scope:
        recipe_parts.append(scope)
    if method:
        recipe_parts.append(method)
    if style:
        recipe_parts.append(style)
    GPTState.last_recipe = " · ".join(recipe_parts)

    actions.user.model_pattern_gui_close()


def _render_domain(gui: imgui.GUI, domain: PatternDomain) -> None:
    has_domain = any(p.domain == domain for p in PATTERNS)
    if not has_domain:
        return

    title = "Coding patterns" if domain == "coding" else "Writing / product / reflection"
    gui.text(title)
    gui.line()
    gui.spacer()
    gui.text("Tip: Say 'close patterns' to close this menu.")
    gui.spacer()

    for pattern in PATTERNS:
        if pattern.domain != domain:
            continue
        if gui.button(pattern.name):
            _run_pattern(pattern)
        gui.text(pattern.recipe)
        grammar_phrase = f"model {pattern.recipe.replace(' · ', ' ')}"
        gui.text(f"Say: {grammar_phrase}")
        gui.spacer()


@imgui.open()
def model_pattern_gui(gui: imgui.GUI):
    gui.text("Model patterns")
    gui.line()
    gui.spacer()
    gui.text(
        "Tip: Say the pattern name (for example, 'debug bug') or the full 'model …' grammar to run it; clicking also runs it."
    )
    gui.spacer()

    domain = PatternGUIState.domain
    if domain is None or domain == "coding":
        _render_domain(gui, "coding")
        gui.spacer()
    if domain is None or domain == "writing":
        _render_domain(gui, "writing")

    gui.spacer()
    if gui.button("Close"):
        actions.user.model_pattern_gui_close()


@mod.action_class
class UserActions:
    def model_pattern_gui_open():
        """Open the model pattern picker GUI"""
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_gui_close()
        except Exception:
            pass
        PatternGUIState.domain = None
        model_pattern_gui.show()
        ctx.tags = ["user.model_pattern_window_open"]

    def model_pattern_gui_open_coding():
        """Open the model pattern picker for coding patterns"""
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_gui_close()
        except Exception:
            pass
        PatternGUIState.domain = "coding"
        model_pattern_gui.show()
        ctx.tags = ["user.model_pattern_window_open"]

    def model_pattern_gui_open_writing():
        """Open the model pattern picker for writing/product/reflection patterns"""
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_gui_close()
        except Exception:
            pass
        PatternGUIState.domain = "writing"
        model_pattern_gui.show()

    def model_pattern_gui_close():
        """Close the model pattern picker GUI"""
        model_pattern_gui.hide()
        ctx.tags = []

    def model_pattern_run_name(pattern_name: str):
        """Run a model pattern by its display name and close the GUI"""
        for pattern in PATTERNS:
            if pattern.name.lower() == pattern_name.lower():
                _run_pattern(pattern)
                break

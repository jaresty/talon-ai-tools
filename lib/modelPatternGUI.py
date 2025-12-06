from dataclasses import dataclass
import os
from typing import Dict, Literal, Optional, Tuple

from talon import Context, Module, actions, canvas, settings, ui

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
    domain: Optional[PatternDomain] = None


@dataclass(frozen=True)
class PromptPattern:
    name: str
    description: str
    recipe: str
    domain: PatternDomain


class PatternCanvasState:
    """State specific to the canvas-based model pattern picker."""

    showing: bool = False


_pattern_canvas: Optional[canvas.Canvas] = None
_pattern_button_bounds: Dict[str, Tuple[int, int, int, int]] = {}

# Default geometry for the pattern picker window.
_PANEL_WIDTH = 720
_PANEL_HEIGHT = 600

try:  # Talon runtime
    from talon.types import Rect
except Exception:  # Tests / stubs

    class Rect:  # type: ignore[override]
        def __init__(self, x: float, y: float, width: float, height: float):
            self.x = x
            self.y = y
            self.width = width
            self.height = height


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


def _debug(msg: str) -> None:
    """Lightweight debug logging for the pattern canvas."""
    try:
        print(f"GPT pattern canvas: {msg}")
    except Exception:
        pass


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
    "relations",
    "system",
    "actions",
}

METHOD_TOKENS = {
    "steps",
    "plan",
    "rigor",
    "rewrite",
    "diagnose",
    "filter",
    "prioritize",
    "cluster",
    # Extended method axis tokens from ADR 012/013.
    "systemic",
    "experimental",
    "debugging",
    "structure",
    "flow",
    "compare",
    "motifs",
    "wasinawa",
    # Extended method axis tokens from ADR 015.
    "xp",
    "adversarial",
    "headline",
    "case",
    "scaffold",
    "liberating",
    "diverge",
    "converge",
    "mapping",
    "socratic",
}

STYLE_TOKENS = {
    "plain",
    "tight",
    "bullets",
    "table",
    "code",
    "cards",
    "checklist",
    # Heavier output/formatting styles from ADR 012.
    "diagram",
    "presenterm",
    "html",
    "gherkin",
    "shellscript",
    "emoji",
    "slack",
    "jira",
    "recipe",
    "abstractvisual",
    "commit",
    "adr",
    "taxonomy",
    "faq",
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
        recipe="describe · full · narrow · debugging · rog",
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
        recipe="describe · gist · focus · flow · fog",
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
        recipe="todo · gist · actions · steps · checklist · ong",
        domain="coding",
    ),
    PromptPattern(
        name="XP next steps",
        description="Suggest XP-flavoured next steps: tiny slices, tests, and production feedback.",
        recipe="describe · gist · actions · xp · bullets · ong",
        domain="coding",
    ),
    PromptPattern(
        name="Map dependencies",
        description="List and explain key dependencies and what they depend on.",
        recipe="dependency · gist · relations · steps · fog",
        domain="coding",
    ),
    # Writing / product / reflection patterns
    PromptPattern(
        name="Simplify locally",
        description="Rewrite the selected text in a simpler way, short but complete.",
        recipe="describe · gist · narrow · plain · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Tighten summary",
        description="Shorten the text while preserving its core meaning.",
        recipe="describe · gist · focus · tight · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Summarize gist",
        description="One-paragraph summary of the text.",
        recipe="describe · gist · focus · plain · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Explain for beginner",
        description="Explain this to a beginner from first principles with simple language.",
        recipe="describe · gist · focus · scaffold · plain · fog",
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
        name="Liberating facilitation",
        description="Frame this as a short Liberating Structures-style facilitation plan.",
        recipe="facilitate · full · focus · liberating · bullets · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Pain points",
        description="List and order key pain points.",
        recipe="pain · gist · focus · filter · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Risk scan",
        description="List and briefly explain key risks.",
        recipe="risky · gist · focus · filter · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Slack summary",
        description="Summarize this content for Slack.",
        recipe="describe · gist · focus · slack · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Jira ticket",
        description="Draft a Jira-style ticket description for this issue.",
        recipe="describe · full · focus · steps · jira · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Motif scan",
        description="Scan for recurring motifs and patterns.",
        recipe="describe · gist · relations · motifs · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Diverge options",
        description="Open up the option space with multiple angles and possibilities.",
        recipe="describe · gist · focus · diverge · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Converge decision",
        description="Weigh trade-offs and converge on a clear decision or short list.",
        recipe="describe · full · focus · converge · bullets · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Mapping scan",
        description="Map out elements and relationships rather than a linear narrative.",
        recipe="describe · gist · relations · mapping · bullets · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Tap map",
        description="Summarize this as a short taxonomy-style map of key categories and subtypes.",
        recipe="describe · full · system · mapping · taxonomy · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Cluster items",
        description="Group related items into labeled categories; clustered output only.",
        recipe="describe · full · narrow · cluster · plain · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Rank items",
        description="Sort items in order of importance to the audience.",
        recipe="describe · full · narrow · prioritize · plain · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Abstraction ladder",
        description="Use abstraction laddering: reasons above the problem, consequences below.",
        recipe="describe · full · focus · ladder · plain · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Type outline",
        description="Outline a type/taxonomy: categories, subtypes, and relationships.",
        recipe="describe · full · focus · taxonomy · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Sketch diagram",
        description="Convert this into a Mermaid-style diagram (code only).",
        recipe="describe · gist · focus · diagram · fog",
        domain="coding",
    ),
    PromptPattern(
        name="Architecture decision",
        description="Draft an Architecture Decision Record (ADR) for this situation.",
        recipe="describe · full · focus · adr · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Present slides",
        description="Render this as a Presenterm slide deck.",
        recipe="describe · full · focus · presenterm · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Multi-angle view",
        description="Lay out several distinct perspectives or stakeholders side by side.",
        recipe="describe · full · relations · diverge · cards · rog",
        domain="writing",
    ),
    PromptPattern(
        name="Flip it review",
        description="Stress-test this with a devil's advocate, adversarial review.",
        recipe="describe · gist · edges · adversarial · fog",
        domain="writing",
    ),
    PromptPattern(
        name="Systems path",
        description="Outline a short systems-level path from here to a desired outcome.",
        recipe="describe · gist · system · mapping · ong",
        domain="writing",
    ),
]


def _ensure_pattern_canvas() -> canvas.Canvas:
    """Create the pattern canvas if needed and register handlers."""
    global _pattern_canvas
    if _pattern_canvas is not None:
        return _pattern_canvas

    screen = ui.main_screen()
    try:
        screen_x = getattr(screen, "x", 0)
        screen_y = getattr(screen, "y", 0)
        screen_width = getattr(screen, "width", _PANEL_WIDTH + 80)
        screen_height = getattr(screen, "height", _PANEL_HEIGHT + 80)
        margin_x = 40
        margin_y = 40

        panel_width = min(_PANEL_WIDTH, max(screen_width - 2 * margin_x, 480))
        panel_height = min(_PANEL_HEIGHT, max(screen_height - 2 * margin_y, 360))

        start_x = screen_x + max((screen_width - panel_width) // 2, margin_x)
        start_y = screen_y + max((screen_height - panel_height) // 2, margin_y)
        rect = Rect(start_x, start_y, panel_width, panel_height)
        _pattern_canvas = canvas.Canvas.from_rect(rect)
        try:
            _pattern_canvas.blocks_mouse = True
        except Exception:
            pass
    except Exception:
        _pattern_canvas = canvas.Canvas.from_screen(screen)

    def _on_draw(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
        _draw_pattern_canvas(c)

    _pattern_canvas.register("draw", _on_draw)

    def _on_mouse(evt) -> None:  # pragma: no cover - visual only
        """Handle close hotspot, domain selection, and pattern clicks."""
        try:
            rect = getattr(_pattern_canvas, "rect", None)
            pos = getattr(evt, "pos", None)
            if rect is None or pos is None:
                return

            event_type = getattr(evt, "event", "") or ""
            button = getattr(evt, "button", None)
            gpos = getattr(evt, "gpos", None) or pos

            local_x = pos.x
            local_y = pos.y
            if local_x < 0 or local_y < 0:
                return
            abs_x = rect.x + local_x
            abs_y = rect.y + local_y

            header_height = 32
            hotspot_width = 80

            if event_type in ("mousedown", "mouse_down") and button in (0, 1):
                # Close hotspot in top-right header band.
                if (
                    0 <= local_y <= header_height
                    and rect.width - hotspot_width <= local_x <= rect.width
                ):
                    _debug("pattern canvas close click detected")
                    actions.user.model_pattern_gui_close()
                    return

                # Button hits for domain or patterns.
                for key, (bx1, by1, bx2, by2) in list(_pattern_button_bounds.items()):
                    if not (bx1 <= abs_x <= bx2 and by1 <= abs_y <= by2):
                        continue
                    if key == "domain_coding":
                        PatternGUIState.domain = "coding"
                        _pattern_canvas.show()
                    elif key == "domain_writing":
                        PatternGUIState.domain = "writing"
                        _pattern_canvas.show()
                    elif key.startswith("pattern:"):
                        name = key.split(":", 1)[1]
                        for pattern in PATTERNS:
                            if pattern.name == name:
                                _run_pattern(pattern)
                                break
                    return

            # Minimal drag: allow moving the panel by dragging the header.
            if event_type in ("mousemove", "mouse_move") and button in (0, 1):
                if 0 <= local_y <= header_height:
                    try:
                        dx = gpos.x - rect.x
                        dy = gpos.y - rect.y
                        _pattern_canvas.move(rect.x + dx, rect.y + dy)
                    except Exception:
                        pass
        except Exception:
            return

    try:
        _pattern_canvas.register("mouse", _on_mouse)
    except Exception:
        _debug("mouse handler registration failed for pattern canvas")

    def _on_key(evt) -> None:  # pragma: no cover - visual only
        try:
            if not getattr(evt, "down", False):
                return
            key = getattr(evt, "key", "") or ""
            if key.lower() in ("escape", "esc"):
                actions.user.model_pattern_gui_close()
        except Exception:
            return

    try:
        _pattern_canvas.register("key", _on_key)
    except Exception:
        _debug("key handler registration failed for pattern canvas")

    return _pattern_canvas


def _open_pattern_canvas(domain: Optional[PatternDomain]) -> None:
    canvas_obj = _ensure_pattern_canvas()
    PatternGUIState.domain = domain
    PatternCanvasState.showing = True
    canvas_obj.show()


def _close_pattern_canvas() -> None:
    global _pattern_canvas
    PatternCanvasState.showing = False
    if _pattern_canvas is None:
        return
    try:
        _pattern_canvas.hide()
    except Exception:
        pass


def _draw_pattern_canvas(c: canvas.Canvas) -> None:  # pragma: no cover - visual only
    rect = getattr(c, "rect", None)
    draw_text = getattr(c, "draw_text", None)
    if draw_text is None:
        return

    _pattern_button_bounds.clear()

    paint = getattr(c, "paint", None)
    if rect is not None and paint is not None:
        try:
            old_color = getattr(paint, "color", None)
            old_style = getattr(paint, "style", None)
            paint.color = "FFFFFF"
            if hasattr(paint, "Style") and hasattr(paint, "style"):
                paint.style = paint.Style.FILL
            c.draw_rect(rect)
            if old_style is not None:
                paint.style = old_style
            paint.color = old_color or "000000"
        except Exception:
            try:
                paint.color = "000000"
            except Exception:
                pass

    if rect is not None and hasattr(rect, "x") and hasattr(rect, "y"):
        x = rect.x + 40
        y = rect.y + 60
    else:
        x = 40
        y = 60
    line_h = 18
    approx_char = 8

    draw_text("Model patterns", x, y)
    if rect is not None and hasattr(rect, "width"):
        close_label = "[X]"
        close_y = rect.y + 24
        close_x = rect.x + rect.width - (len(close_label) * approx_char) - 16
        draw_text(close_label, close_x, close_y)
    y += line_h
    draw_text(
        "Tip: Say the pattern name or full 'model …' grammar; clicking also runs it.",
        x,
        y,
    )
    y += line_h * 2

    domain = PatternGUIState.domain
    if domain is None:
        draw_text("Choose a pattern domain:", x, y)
        y += line_h * 2
        # Coding domain button.
        label = "[Coding patterns]"
        draw_text(label, x, y)
        _pattern_button_bounds["domain_coding"] = (
            x,
            y - line_h,
            x + len(label) * approx_char,
            y + line_h,
        )
        y += line_h * 2
        # Writing/product/reflection domain button.
        label = "[Writing / product / reflection patterns]"
        draw_text(label, x, y)
        _pattern_button_bounds["domain_writing"] = (
            x,
            y - line_h,
            x + len(label) * approx_char,
            y + line_h,
        )
        y += line_h * 2
        draw_text(
            "Tip: Say 'model coding patterns' or 'model writing patterns' to jump straight to a domain.",
            x,
            y,
        )
        return

    # Domain-specific patterns.
    title = "Coding patterns" if domain == "coding" else "Writing / product / reflection"
    draw_text(title, x, y)
    y += line_h
    draw_text("Tip: Say 'close patterns' to close this menu.", x, y)
    y += line_h * 2

    for pattern in PATTERNS:
        if pattern.domain != domain:
            continue
        label = f"[{pattern.name}]"
        draw_text(label, x, y)
        _pattern_button_bounds[f"pattern:{pattern.name}"] = (
            x,
            y - line_h,
            x + len(label) * approx_char,
            y + line_h,
        )
        y += line_h
        draw_text(pattern.recipe, x, y)
        y += line_h
        grammar_phrase = f"model {pattern.recipe.replace(' · ', ' ')}"
        draw_text(f"Say: {grammar_phrase}", x, y)
        y += line_h * 2


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
    GPTState.last_static_prompt = static_prompt
    GPTState.last_completeness = completeness or ""
    GPTState.last_scope = scope or ""
    GPTState.last_method = method or ""
    GPTState.last_style = style or ""
    GPTState.last_directional = directional or ""

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
            actions.user.model_help_canvas_close()
        except Exception:
            pass
        _open_pattern_canvas(domain=None)
        ctx.tags = ["user.model_pattern_window_open"]

    def model_pattern_gui_open_coding():
        """Open the model pattern picker for coding patterns"""
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_canvas_close()
        except Exception:
            pass
        _open_pattern_canvas(domain="coding")
        ctx.tags = ["user.model_pattern_window_open"]

    def model_pattern_gui_open_writing():
        """Open the model pattern picker for writing/product/reflection patterns"""
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.model_help_canvas_close()
        except Exception:
            pass
        _open_pattern_canvas(domain="writing")

    def model_pattern_gui_close():
        """Close the model pattern picker GUI"""
        _close_pattern_canvas()
        ctx.tags = []

    def model_pattern_run_name(pattern_name: str):
        """Run a model pattern by its display name and close the GUI"""
        for pattern in PATTERNS:
            if pattern.name.lower() == pattern_name.lower():
                _run_pattern(pattern)
                break

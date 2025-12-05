import os

from talon import Context, Module, actions, imgui

from .modelState import GPTState

try:
    from .staticPromptConfig import get_static_prompt_axes, get_static_prompt_profile
except ImportError:  # Talon may have a stale staticPromptConfig loaded
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

mod = Module()
ctx = Context()


class HelpGUIState:
    section = "all"
    static_prompt = None


def _read_axis_keys(filename: str) -> list[str]:
    """Read modifier keys from a Talon list file in GPT/lists."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
    keys: list[str] = []
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
                    key, _ = line.split(":", 1)
                    keys.append(key.strip())
    except FileNotFoundError:
        return []
    return keys


def _read_axis_items(filename: str) -> list[tuple[str, str]]:
    """Read (key, description) pairs from a Talon list file."""
    current_dir = os.path.dirname(__file__)
    lists_dir = os.path.abspath(os.path.join(current_dir, "..", "GPT", "lists"))
    path = os.path.join(lists_dir, filename)
    items: list[tuple[str, str]] = []
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
                    items.append((key.strip(), value.strip()))
    except FileNotFoundError:
        return []
    return items


COMPLETENESS_KEYS = _read_axis_keys("completenessModifier.talon-list")
SCOPE_KEYS = _read_axis_keys("scopeModifier.talon-list")
METHOD_KEYS = _read_axis_keys("methodModifier.talon-list")
STYLE_KEYS = _read_axis_keys("styleModifier.talon-list")
DIRECTIONAL_KEYS = _read_axis_keys("directionalModifier.talon-list")

COMPLETENESS_ITEMS = _read_axis_items("completenessModifier.talon-list")
SCOPE_ITEMS = _read_axis_items("scopeModifier.talon-list")
METHOD_ITEMS = _read_axis_items("methodModifier.talon-list")
STYLE_ITEMS = _read_axis_items("styleModifier.talon-list")


def _wrap_and_render(gui: imgui.GUI, text: str, indent: str = "  ", width: int = 80) -> None:
    """Render long text with manual word-wrapping to avoid oversized dialogs."""
    words = text.split()
    if not words:
        return

    current = indent
    for word in words:
        # +1 for the space before the next word when needed.
        next_len = len(current) + (1 if current.strip() else 0) + len(word)
        if next_len > width:
            gui.text(current)
            current = f"{indent}{word}"
        else:
            if current.strip():
                current += " " + word
            else:
                current = indent + word
    if current.strip():
        gui.text(current)


def _group_directional_keys() -> dict[str, list[str]]:
    """Arrange directional lenses along vertical/horizontal cardinal axes."""
    groups: dict[str, list[str]] = {
        "up": [],
        "center_v": [],
        "down": [],
        "left": [],
        "center_h": [],
        "right": [],
        "central": [],
        "non_directional": [],
        "fused_other": [],
    }
    if not DIRECTIONAL_KEYS:
        return groups

    vertical_up = {"fog"}
    vertical_center = {"fig"}
    vertical_down = {"dig"}

    horizontal_left = {"rog"}
    horizontal_center = {"bog"}
    horizontal_right = {"ong"}

    central_names = {"jog"}

    seen_directional: set[str] = set()

    # First pass: classify by prefixes/suffixes and known singletons.
    for key in DIRECTIONAL_KEYS:
        base = key.strip()
        is_directional = False

        if " " in base:
            prefix, suffix = base.split(" ", 1)
            if prefix == "fly":
                groups["up"].append(base)
                is_directional = True
            elif prefix == "fip":
                groups["center_v"].append(base)
                is_directional = True
            elif prefix == "dip":
                groups["down"].append(base)
                is_directional = True

            if suffix == "rog":
                groups["left"].append(base)
                is_directional = True
            elif suffix == "bog":
                groups["center_h"].append(base)
                is_directional = True
            elif suffix == "ong":
                groups["right"].append(base)
                is_directional = True

            if not is_directional:
                groups["fused_other"].append(base)
        else:
            if base in vertical_up:
                groups["up"].append(base)
                is_directional = True
            if base in vertical_center:
                groups["center_v"].append(base)
                is_directional = True
            if base in vertical_down:
                groups["down"].append(base)
                is_directional = True

            if base in horizontal_left:
                groups["left"].append(base)
                is_directional = True
            if base in horizontal_center:
                groups["center_h"].append(base)
                is_directional = True
            if base in horizontal_right:
                groups["right"].append(base)
                is_directional = True

            if base in central_names:
                groups["central"].append(base)
                is_directional = True

        if is_directional:
            seen_directional.add(base)

    # Second pass: anything not seen and not fused is non-directional (for example, tap).
    for key in DIRECTIONAL_KEYS:
        base = key.strip()
        if " " not in base and base not in seen_directional:
            groups["non_directional"].append(base)

    return groups


def _show_axes(gui: imgui.GUI) -> None:
    gui.text("Axes")
    gui.text("  - Goal / static prompt")
    gui.text("  - Directional lens")
    gui.text("  - Completeness, Scope, Method, Style")
    gui.spacer()

    gui.text("Directional lenses")
    if DIRECTIONAL_KEYS:
        groups = _group_directional_keys()
        if groups["up"] or groups["center_v"] or groups["down"]:
            gui.text("  Vertical slices:")
            if groups["up"]:
                _wrap_and_render(gui, "Up: " + ", ".join(groups["up"]), indent="    ")
            if groups["center_v"]:
                _wrap_and_render(gui, "Center: " + ", ".join(groups["center_v"]), indent="    ")
            if groups["down"]:
                _wrap_and_render(gui, "Down: " + ", ".join(groups["down"]), indent="    ")

        if groups["left"] or groups["center_h"] or groups["right"]:
            gui.text("  Horizontal slices:")
            if groups["left"]:
                _wrap_and_render(gui, "Left: " + ", ".join(groups["left"]), indent="    ")
            if groups["center_h"]:
                _wrap_and_render(gui, "Center: " + ", ".join(groups["center_h"]), indent="    ")
            if groups["right"]:
                _wrap_and_render(gui, "Right: " + ", ".join(groups["right"]), indent="    ")

        if groups["central"]:
            _wrap_and_render(gui, "Central lenses: " + ", ".join(groups["central"]))
        if groups["non_directional"]:
            _wrap_and_render(gui, "Non-directional: " + ", ".join(groups["non_directional"]))
        gui.text("  Core lenses: fog, fig, dig, ong, rog, bog, jog")
    else:
        gui.text("  fog, fig, dig, ong, rog, bog, jog")
    gui.text("  (one lens per model call)")
    gui.spacer()


def _show_completeness(gui: imgui.GUI) -> None:
    gui.text("Completeness")
    if COMPLETENESS_ITEMS and HelpGUIState.section == "completeness":
        for key, desc in COMPLETENESS_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        # Fallback to a representative set of known completeness tokens if the
        # list cannot be loaded. When available, COMPLETENESS_KEYS comes from
        # completenessModifier.talon-list and should include the full set.
        keys = COMPLETENESS_KEYS or [
            "skim",
            "gist",
            "full",
            "max",
            "minimal",
            "deep",
        ]
        _wrap_and_render(gui, ", ".join(keys))
    gui.spacer()


def _show_scope(gui: imgui.GUI) -> None:
    gui.text("Scope")
    if SCOPE_ITEMS and HelpGUIState.section == "scope":
        for key, desc in SCOPE_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = SCOPE_KEYS or ["narrow", "focus", "bound", "edges", "relations"]
        _wrap_and_render(gui, ", ".join(keys))
    gui.spacer()


def _show_method(gui: imgui.GUI) -> None:
    gui.text("Method")
    if METHOD_ITEMS and HelpGUIState.section == "method":
        for key, desc in METHOD_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = METHOD_KEYS or [
            "steps",
            "plan",
            "rigor",
            "rewrite",
            "diagnose",
            "filter",
            "prioritize",
            "cluster",
            "systemic",
            "experimental",
            "debugging",
            "structure",
            "flow",
            "compare",
            "motifs",
            "wasinawa",
            "analysis",
        ]
        _wrap_and_render(gui, ", ".join(keys))
    gui.spacer()


def _show_style(gui: imgui.GUI) -> None:
    gui.text("Style")
    if STYLE_ITEMS and HelpGUIState.section == "style":
        for key, desc in STYLE_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = STYLE_KEYS or [
            "plain",
            "tight",
            "bullets",
            "table",
            "code",
            "cards",
            "checklist",
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
        ]
        _wrap_and_render(gui, ", ".join(keys))
    gui.spacer()


def _show_examples(gui: imgui.GUI) -> None:
    # Only show the full examples section when explicitly requested; this
    # keeps the default quick help view from becoming excessively tall.
    if HelpGUIState.section != "examples":
        return

    gui.text("Examples")
    gui.text("  Debug bug: describe · full · narrow · debugging · rog")
    gui.text("  Fix locally: fix · full · narrow · steps · ong")
    gui.text("  Summarize gist: describe · gist · focus · plain · fog")
    gui.text("  Sketch diagram: describe · gist · focus · diagram · fog")
    gui.text("  Architecture decision: describe · full · focus · adr · rog")
    gui.text("  Present slides: describe · full · focus · presenterm · rog")
    gui.text("  Format for Slack: describe · gist · focus · slack · fog")
    gui.text("  Format for Jira: describe · gist · focus · jira · fog")
    gui.text("  Systems sketch: describe · gist · focus · systemic · fog")
    gui.text("  Experiment plan: describe · full · focus · experimental · fog")
    gui.text("  Type/taxonomy: describe · full · focus · taxonomy · rog")
    gui.text("  Analysis only: describe · gist · focus · analysis · fog")
    gui.text("  Sample options: describe · samples · focus · diverge · fog")
    gui.spacer()
    gui.text("Replaced prompts")
    _wrap_and_render(
        gui,
        "simple → use describe · gist · plain (or the 'Simplify locally' pattern).",
    )
    _wrap_and_render(
        gui,
        "short → use describe · gist · tight (or the 'Tighten summary' pattern).",
    )
    _wrap_and_render(
        gui,
        "todo-style 'how to' → use todo · gist · checklist (or the 'Extract todos' pattern).",
    )
    gui.spacer()


@imgui.open()
def model_help_gui(gui: imgui.GUI):
    gui.text("Model grammar quick reference")
    gui.line()
    gui.spacer()
    if HelpGUIState.static_prompt:
        sp = HelpGUIState.static_prompt
        gui.text(f"Prompt: {sp}")
        axes = []
        profile_axes = get_static_prompt_axes(sp)
        for label in ("completeness", "scope", "method", "style"):
            value = profile_axes.get(label)
            if value:
                axes.append(f"{label.capitalize()}: {value}")
        if axes:
            gui.text("Profile defaults:")
            for line in axes:
                gui.text(f"  {line}")
        gui.text("Grammar skeleton:")
        gui.text(
            f"  model {sp} [completeness] [scope] [method] [style] <directional lens>"
        )
        gui.text(f"Tip: Say 'model pattern menu {sp}' to open a pattern menu for this prompt.")
        gui.spacer()
    elif GPTState.last_recipe:
        # When available, include the directional lens alongside the core
        # recipe tokens so the quick-help recap matches the full grammar.
        if getattr(GPTState, "last_directional", ""):
            recipe_text = f"{GPTState.last_recipe} · {GPTState.last_directional}"
            grammar_phrase = (
                f"model {GPTState.last_recipe.replace(' · ', ' ')} "
                f"{GPTState.last_directional}"
            )
        else:
            recipe_text = GPTState.last_recipe
            grammar_phrase = f"model {GPTState.last_recipe.replace(' · ', ' ')}"
        gui.text(f"Last recipe: {recipe_text}")
        gui.text(f"Say: {grammar_phrase}")
        gui.text(
            "Tip: Say 'model again' to rerun this recipe, or add axis tokens "
            "(for example, 'model again gist fog') to tweak it."
        )
        gui.spacer()

    section = HelpGUIState.section
    if section in ("all", "axes"):
        _show_axes(gui)
    if section in ("all", "completeness"):
        _show_completeness(gui)
    if section in ("all", "scope"):
        _show_scope(gui)
    if section in ("all", "method"):
        _show_method(gui)
    if section in ("all", "style"):
        _show_style(gui)
    if section in ("all", "examples"):
        _show_examples(gui)

    gui.text("Tip: Say 'model quick help' again or click Close to dismiss this window.")
    gui.spacer()

    if gui.button("Close"):
        actions.user.model_help_gui_close()


@mod.action_class
class UserActions:
    def model_help_gui_open():
        """Toggle the model grammar quick reference GUI"""
        if model_help_gui.showing:
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            model_help_gui.hide()
        else:
            # Close other related menus to avoid overlapping overlays.
            try:
                actions.user.model_pattern_gui_close()
            except Exception:
                pass
            try:
                actions.user.prompt_pattern_gui_close()
            except Exception:
                pass
            HelpGUIState.section = "all"
            HelpGUIState.static_prompt = None
            model_help_gui.show()

    def model_help_gui_open_for_last_recipe():
        """Open quick help with the last recipe and grammar reminder"""
        # Close other related menus to avoid overlapping overlays.
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "all"
        HelpGUIState.static_prompt = None
        model_help_gui.show()

    def model_help_gui_open_completeness():
        """Open quick help focused on completeness"""
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "completeness"
        HelpGUIState.static_prompt = None
        model_help_gui.show()

    def model_help_gui_open_scope():
        """Open quick help focused on scope"""
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "scope"
        HelpGUIState.static_prompt = None
        model_help_gui.show()

    def model_help_gui_open_method():
        """Open quick help focused on method"""
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "method"
        HelpGUIState.static_prompt = None
        model_help_gui.show()

    def model_help_gui_open_style():
        """Open quick help focused on style"""
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "style"
        HelpGUIState.static_prompt = None
        model_help_gui.show()

    def model_help_gui_close():
        """Close the model grammar quick reference GUI"""
        HelpGUIState.section = "all"
        HelpGUIState.static_prompt = None
        model_help_gui.hide()

    def model_help_gui_open_for_static_prompt(static_prompt: str):
        """Open quick help focused on a specific static prompt"""
        try:
            actions.user.model_pattern_gui_close()
        except Exception:
            pass
        try:
            actions.user.prompt_pattern_gui_close()
        except Exception:
            pass
        HelpGUIState.section = "all"
        HelpGUIState.static_prompt = static_prompt
        model_help_gui.show()

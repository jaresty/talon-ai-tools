from talon import Context, Module, actions, imgui
import os

from .modelState import GPTState
from .staticPromptConfig import STATIC_PROMPT_CONFIG

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


def _show_axes(gui: imgui.GUI) -> None:
    gui.text("Axes")
    gui.text("  - Goal / static prompt")
    gui.text("  - Directional lens")
    gui.text("  - Completeness, Scope, Method, Style")
    gui.spacer()

    gui.text("Directional lenses")
    if DIRECTIONAL_KEYS:
        gui.text("  " + ", ".join(DIRECTIONAL_KEYS))
    else:
        gui.text("  fog, fig, dig, ong, rog, bog")
    gui.text("  (plus combined forms like fly ong, fip rog, dip bog)")
    gui.spacer()


def _show_completeness(gui: imgui.GUI) -> None:
    gui.text("Completeness")
    if COMPLETENESS_ITEMS and HelpGUIState.section == "completeness":
        for key, desc in COMPLETENESS_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = COMPLETENESS_KEYS or ["skim", "gist", "full", "max"]
        gui.text("  " + ", ".join(keys))
    gui.spacer()


def _show_scope(gui: imgui.GUI) -> None:
    gui.text("Scope")
    if SCOPE_ITEMS and HelpGUIState.section == "scope":
        for key, desc in SCOPE_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = SCOPE_KEYS or ["narrow", "focus", "bound", "edges", "relations"]
        gui.text("  " + ", ".join(keys))
    gui.spacer()


def _show_method(gui: imgui.GUI) -> None:
    gui.text("Method")
    if METHOD_ITEMS and HelpGUIState.section == "method":
        for key, desc in METHOD_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = METHOD_KEYS or ["steps", "plan", "rigor", "rewrite", "diagnose", "filter", "prioritize", "cluster"]
        gui.text("  " + ", ".join(keys))
    gui.spacer()


def _show_style(gui: imgui.GUI) -> None:
    gui.text("Style")
    if STYLE_ITEMS and HelpGUIState.section == "style":
        for key, desc in STYLE_ITEMS:
            gui.text(f"  {key}: {desc}")
    else:
        keys = STYLE_KEYS or ["plain", "tight", "bullets", "table", "code", "checklist"]
        gui.text("  " + ", ".join(keys))
    gui.spacer()


def _show_examples(gui: imgui.GUI) -> None:
    gui.text("Examples")
    gui.text("  Debug bug: debug · full · narrow · rigor · rog")
    gui.text("  Fix locally: fix · full · narrow · steps · ong")
    gui.text("  Summarize gist: describe · gist · focus · plain · fog")
    gui.spacer()
    gui.text("Replaced prompts")
    gui.text("  simple → use describe · gist · plain (or the 'Simplify locally' pattern).")
    gui.text("  short → use describe · gist · tight (or the 'Tighten summary' pattern).")
    gui.text("  todo-style 'how to' → use todo · gist · checklist (or the 'Extract todos' pattern).")
    gui.spacer()


@imgui.open()
def model_help_gui(gui: imgui.GUI):
    gui.text("Model grammar quick reference")
    gui.line()
    gui.spacer()
    if HelpGUIState.static_prompt:
        sp = HelpGUIState.static_prompt
        gui.text(f"Prompt: {sp}")
        config = STATIC_PROMPT_CONFIG.get(sp, {})
        axes = []
        for label in ("completeness", "scope", "method", "style"):
            value = config.get(label)
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
        gui.text(f"Last recipe: {GPTState.last_recipe}")
        grammar_phrase = f"model {GPTState.last_recipe.replace(' · ', ' ')}"
        gui.text(f"Say: {grammar_phrase}")
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

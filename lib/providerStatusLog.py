from typing import List, Optional

from talon import Module

mod = Module()


class ProviderStatusLog:
    showing: bool = False
    title: str = ""
    lines: List[str] = []
    last_message: str = ""
    history: List[str] = []


def _format_status(title: Optional[str], lines: List[str]) -> str:
    parts: List[str] = []
    if title:
        parts.append(f"[{title}]")
    parts.extend(f"• {line}" for line in lines)
    return "\n".join(parts) if parts else "(no provider status available)"


def log_provider_status(title: str, lines: List[str]) -> None:
    ProviderStatusLog.title = title
    ProviderStatusLog.lines = list(lines)
    ProviderStatusLog.showing = True
    message = _format_status(title, ProviderStatusLog.lines)
    ProviderStatusLog.last_message = message
    ProviderStatusLog.history.append(message)
    print(message)


def clear_provider_status() -> None:
    ProviderStatusLog.showing = False
    ProviderStatusLog.title = ""
    ProviderStatusLog.lines = []
    ProviderStatusLog.last_message = ""


def show_provider_canvas(title: str, lines: List[str]) -> None:  # pragma: no cover
    log_provider_status(title, lines)


def hide_provider_canvas() -> None:  # pragma: no cover
    clear_provider_status()

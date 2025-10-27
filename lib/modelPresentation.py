from dataclasses import dataclass, field
from typing import List, Sequence

from .modelHelpers import messages_to_string
from .modelSource import GPTItem


@dataclass
class ResponsePresentation:
    display_text: str
    paste_text: str
    browser_lines: List[str] = field(default_factory=list)
    open_browser: bool = False


def render_for_destination(
    gpt_message: Sequence[GPTItem], destination_kind: str
) -> ResponsePresentation:
    extracted_message = messages_to_string(gpt_message)
    lines = extracted_message.split("\n")
    open_browser = destination_kind == "browser" or len(lines) > 60
    return ResponsePresentation(
        display_text=extracted_message,
        paste_text=extracted_message,
        browser_lines=lines,
        open_browser=open_browser,
    )

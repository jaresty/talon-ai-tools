from dataclasses import dataclass, field
from typing import List, Sequence

from .modelHelpers import messages_to_string, split_answer_and_meta
from .modelSource import GPTItem


@dataclass
class ResponsePresentation:
    display_text: str
    paste_text: str
    browser_lines: List[str] = field(default_factory=list)
    open_browser: bool = False
    # Optional meta-interpretation for the response, when available.
    meta_text: str = ""


def render_for_destination(
    gpt_message: Sequence[GPTItem], destination_kind: str
) -> ResponsePresentation:
    extracted_message = messages_to_string(gpt_message)
    answer_text, meta_text = split_answer_and_meta(extracted_message)
    lines = answer_text.split("\n")
    open_browser = destination_kind == "browser" or len(lines) > 60
    return ResponsePresentation(
        display_text=answer_text,
        paste_text=answer_text,
        browser_lines=lines,
        open_browser=open_browser,
        meta_text=meta_text,
    )

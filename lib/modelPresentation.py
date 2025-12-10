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

    # When the payload only contains meta (for example, `model pass meta`), the
    # main answer portion is empty. Fall back to the meta text so paste/display
    # flows still have content instead of silently inserting nothing.
    primary_text = answer_text or meta_text

    lines = primary_text.split("\n") if primary_text else []
    open_browser = destination_kind == "browser" or len(lines) > 60
    return ResponsePresentation(
        display_text=primary_text,
        paste_text=primary_text,
        browser_lines=lines,
        open_browser=open_browser,
        meta_text=meta_text,
    )

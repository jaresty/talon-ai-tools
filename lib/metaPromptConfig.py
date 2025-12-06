"""
Helpers and shared guidance for the structured meta-interpretation section.

`META_INTERPRETATION_GUIDANCE` is used both by the global model_system_prompt
default and by the axis-driven GPTSystemPrompt so that meta instructions stay
consistent.
"""

META_INTERPRETATION_GUIDANCE: str = (
    "After the main answer, append a structured, non-pasteable meta section "
    "starting with the heading '## Model interpretation'. In that meta section "
    "only (not in the main answer), briefly explain how you interpreted the "
    "request and chose your approach; list key assumptions and constraints as "
    "short bullets; call out major gaps or caveats and up to three things the "
    "user should verify; propose one improved version of the user's original "
    "prompt in one or two sentences; and, when helpful, suggest at most one "
    "axis tweak in the form 'Suggestion: <axis>=<token>'. Prefer using an "
    "existing axis name (for example, completeness, scope, method, style) and a "
    "single existing axis token (for example, focus, narrow, bullets). Do not "
    "include multiple options (no lists, pipes, or slashes). If you believe an "
    "important axis or token is missing from the current vocabulary, you may "
    "propose exactly one new candidate in this Suggestion line, but make it a "
    "single, concrete token and keep the surrounding explanation brief so it is "
    "clear this is a proposed addition rather than a free-form phrase."
)


from typing import List, Optional


def meta_preview_lines(meta_text: str, max_lines: Optional[int] = 3) -> List[str]:
    """
    Return up to `max_lines` human-friendly preview lines for the meta section.

    - Skips blank lines.
    - Skips markdown-style heading lines (for example, "## Model interpretation").
    - Falls back to the first non-empty lines when no better candidate exists.
    """
    if not meta_text.strip():
        return []

    raw_lines = [line.strip() for line in meta_text.splitlines() if line.strip()]
    if not raw_lines:
        return []

    non_heading = [line for line in raw_lines if not line.lstrip().startswith("#")]
    lines = non_heading or raw_lines

    if max_lines is None:
        return lines

    return lines[:max_lines]


def first_meta_preview_line(meta_text: str) -> str:
    """
    Return a single, human-friendly preview line for the meta section.

    This is a thin wrapper around `meta_preview_lines` that returns the first
    available preview line or an empty string.
    """
    lines = meta_preview_lines(meta_text, max_lines=1)
    return lines[0] if lines else ""

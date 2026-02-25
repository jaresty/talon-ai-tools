"""Generate axisConfig-style token->description maps from the axis registry.

Outputs a Python module defining AXIS_KEY_TO_VALUE plus the small dataclasses
used by the existing axisConfig façade. Intended as a deterministic generator
to keep axisConfig.py/README fragments in sync with the registry. Can also
emit a JSON mapping for consumers that want a structured SSOT feed.
"""

from __future__ import annotations

import argparse
from typing import Any
import json
import sys
import pprint
import textwrap
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.axisCatalog import serialize_axis_config  # type: ignore  # noqa: E402
from lib.personaConfig import PERSONA_KEY_TO_KANJI  # type: ignore  # noqa: E402


def _axis_payload() -> dict:
    """Return the full axis payload from the SSOT catalog serializer."""
    return serialize_axis_config(
        lists_dir=None, include_axis_lists=False, include_static_prompts=True
    )


def _axis_mapping() -> dict[str, dict[str, str]]:
    """Return axis token -> description mapping from the SSOT catalog serializer."""
    axes = _axis_payload().get("axes", {}) or {}
    # Ensure deterministic ordering for stable renders.
    return {
        axis: dict(sorted((axes.get(axis) or {}).items()))
        for axis in sorted(axes.keys())
    }


def _axis_label_mapping() -> dict[str, dict[str, str]]:
    """Return axis token -> label mapping (ADR-0109)."""
    labels = _axis_payload().get("axis_labels", {}) or {}
    return {
        axis: dict(sorted((labels.get(axis) or {}).items()))
        for axis in sorted(labels.keys())
        if labels.get(axis)
    }


def _axis_guidance_mapping() -> dict[str, dict[str, str]]:
    """Return axis token -> guidance mapping (ADR-0110)."""
    guidance = _axis_payload().get("axis_guidance", {}) or {}
    return {
        axis: dict(sorted((guidance.get(axis) or {}).items()))
        for axis in sorted(guidance.keys())
        if guidance.get(axis)
    }


def _axis_kanji_mapping() -> dict[str, Any]:
    """Return axis token -> kanji mapping (ADR-0143)."""
    kanji = _axis_payload().get("axis_kanji", {}) or {}
    result: dict[str, Any] = {
        axis: dict(sorted((kanji.get(axis) or {}).items()))
        for axis in sorted(kanji.keys())
        if kanji.get(axis)
    }
    # Add task kanji from static_prompt_kanji
    static_kanji = _axis_payload().get("static_prompt_kanji", {}) or {}
    if static_kanji:
        result["task"] = dict(sorted(static_kanji.items()))
    # Add persona kanji from persona.kanji
    persona_kanji = (_axis_payload().get("persona") or {}).get("kanji", {}) or {}
    if persona_kanji:
        result["persona"] = dict(
            sorted(
                {
                    axis: dict(sorted(tokens.items()))
                    for axis, tokens in persona_kanji.items()
                }.items()
            )
        )
    return result


def render_axis_config() -> str:
    """Render an axisConfig.py module based on the registry."""
    payload = _axis_payload()
    axes = payload.get("axes", {}) or {}
    mapping = {
        axis: dict(sorted((axes.get(axis) or {}).items()))
        for axis in sorted(axes.keys())
    }
    labels = payload.get("axis_labels", {}) or {}
    label_mapping = {
        axis: dict(sorted((labels.get(axis) or {}).items()))
        for axis in sorted(labels.keys())
        if labels.get(axis)
    }
    guidance = payload.get("axis_guidance", {}) or {}
    guidance_mapping = {
        axis: dict(sorted((guidance.get(axis) or {}).items()))
        for axis in sorted(guidance.keys())
        if guidance.get(axis)
    }
    use_when = payload.get("axis_use_when", {}) or {}
    use_when_mapping = {
        axis: dict(sorted((use_when.get(axis) or {}).items()))
        for axis in sorted(use_when.keys())
        if use_when.get(axis)
    }
    kanji = payload.get("axis_kanji", {}) or {}
    kanji_mapping: dict[str, Any] = {
        axis: dict(sorted((kanji.get(axis) or {}).items()))
        for axis in sorted(kanji.keys())
        if kanji.get(axis)
    }
    # Add task kanji from static_prompt_kanji
    static_kanji = payload.get("static_prompt_kanji", {}) or {}
    if static_kanji:
        kanji_mapping["task"] = dict(sorted(static_kanji.items()))
    # Add persona kanji from PERSONA_KEY_TO_KANJI
    if PERSONA_KEY_TO_KANJI:
        kanji_mapping["persona"] = dict(
            sorted(
                {
                    axis: dict(sorted(tokens.items()))
                    for axis, tokens in PERSONA_KEY_TO_KANJI.items()
                }.items()
            )
        )
    # Sort the final kanji_mapping to match expected order
    kanji_mapping = dict(sorted(kanji_mapping.items()))
    category = payload.get("axis_category", {}) or {}
    category_mapping: dict[str, Any] = {
        axis: dict(sorted((category.get(axis) or {}).items()))
        for axis in sorted(category.keys())
        if category.get(axis)
    }
    category_mapping = dict(sorted(category_mapping.items()))
    routing_concept = payload.get("axis_routing_concept", {}) or {}
    routing_concept_mapping: dict[str, Any] = {
        axis: dict(sorted((routing_concept.get(axis) or {}).items()))
        for axis in sorted(routing_concept.keys())
        if routing_concept.get(axis)
    }
    # Add task routing_concept from static_prompt_routing_concept
    static_routing_concept = payload.get("static_prompt_routing_concept", {}) or {}
    if static_routing_concept:
        routing_concept_mapping["task"] = dict(sorted(static_routing_concept.items()))
    routing_concept_mapping = dict(sorted(routing_concept_mapping.items()))
    # Use a very wide width to prevent pprint from splitting string literals
    # across lines (which creates ugly adjacent string concatenation)
    body = pprint.pformat(mapping, width=200, sort_dicts=True)
    label_body = pprint.pformat(label_mapping, width=200, sort_dicts=True)
    guidance_body = pprint.pformat(guidance_mapping, width=200, sort_dicts=True)
    use_when_body = pprint.pformat(use_when_mapping, width=200, sort_dicts=True)
    kanji_body = pprint.pformat(kanji_mapping, width=200, sort_dicts=True)
    category_body = pprint.pformat(category_mapping, width=200, sort_dicts=True)
    routing_concept_body = pprint.pformat(routing_concept_mapping, width=200, sort_dicts=True)
    header = textwrap.dedent(
        """\
        \"\"\"Axis configuration as static Python maps (token -> description).

        Generated from the axis registry; keep in sync with list edits.

        SYNC_WARNING: Changes to token names/descriptions affect:
        - internal/barcli/help_llm.go (hardcoded heuristics and usage patterns)
        - .opencode/skills/bar-workflow/skill.md (method categorization)
        - internal/barcli/help_llm_test.go (validation tests)

        When renaming/removing tokens:
        1. Update help_llm.go hardcoded references
        2. Update skill.md if method categories change
        3. Run `go test ./internal/barcli/ -run TestLLMHelp` to validate
        \"\"\"

        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import Dict, FrozenSet, Union
        """
    )
    dataclasses = textwrap.dedent(
        """\
        @dataclass(frozen=True)
        class AxisDoc:
            axis: str
            key: str
            description: str
            group: str | None = None
            flags: FrozenSet[str] = field(default_factory=frozenset)
        """
    )
    helpers = textwrap.dedent(
        """\

        def axis_key_to_value_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->description map for a given axis.\"\"\"
            return AXIS_KEY_TO_VALUE.get(axis, {})


        def axis_key_to_label_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->label map for a given axis (ADR-0109).\"\"\"
            return AXIS_KEY_TO_LABEL.get(axis, {})


        def axis_key_to_guidance_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->guidance map for a given axis (ADR-0110).\"\"\"
            return AXIS_KEY_TO_GUIDANCE.get(axis, {})


        def axis_key_to_use_when_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->use_when map for a given axis (ADR-0132).\"\"\"
            return AXIS_KEY_TO_USE_WHEN.get(axis, {})


        def axis_key_to_kanji_map(axis: str) -> Union[Dict[str, str], Dict[str, Dict[str, str]]]:
            \"\"\"Return the key->kanji map for a given axis (ADR-0143).

            For regular axes returns Dict[str, str] (token -> kanji).
            For 'persona' returns Dict[str, Dict[str, str]] (sub-axis -> token -> kanji).
            \"\"\"
            return AXIS_KEY_TO_KANJI.get(axis, {})


        def axis_key_to_category_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->category map for a given axis (ADR-0144).\"\"\"
            return AXIS_KEY_TO_CATEGORY.get(axis, {})


        def axis_key_to_routing_concept_map(axis: str) -> dict[str, str]:
            \"\"\"Return the key->routing_concept map for a given axis (ADR-0146).

            Returns per-token distilled routing concept phrases. Tokens sharing the same
            phrase form a multi-token routing bullet (e.g. thing+struct → 'Entities/boundaries').
            \"\"\"
            return AXIS_KEY_TO_ROUTING_CONCEPT.get(axis, {})


        def axis_docs_for(axis: str) -> list[AxisDoc]:
            \"\"\"Return AxisDoc objects for a given axis.\"\"\"
            mapping = axis_key_to_value_map(axis)
            return [
                AxisDoc(axis=axis, key=key, description=desc, group=None, flags=frozenset())
                for key, desc in mapping.items()
            ]


        def axis_docs_index() -> dict[str, list[AxisDoc]]:
            \"\"\"Return AxisDoc entries for all axes.\"\"\"

            index: dict[str, list[AxisDoc]] = {}
            for axis, mapping in AXIS_KEY_TO_VALUE.items():
                index[axis] = [
                    AxisDoc(axis=axis, key=key, description=desc, group=None, flags=frozenset())
                    for key, desc in mapping.items()
                ]
            return index
        """
    )
    patterns = payload.get("usage_patterns", []) or []

    def _format_pattern(p: dict) -> str:
        """Format a single pattern dict as a one-line Python dict literal."""
        parts = []
        for k, v in p.items():
            if isinstance(v, dict):
                inner = ", ".join(
                    f"{repr(ik)}: {repr(iv)}" for ik, iv in sorted(v.items())
                )
                parts.append(f"{repr(k)}: {{{inner}}}")
            else:
                parts.append(f"{repr(k)}: {repr(v)}")
        return "{" + ", ".join(parts) + "}"

    pattern_lines = ",\n    ".join(_format_pattern(p) for p in patterns)
    usage_patterns_block = f"""

USAGE_PATTERNS: list[dict] = [
    {pattern_lines},
]


def get_usage_patterns() -> list[dict]:
    \"\"\"Return the USAGE_PATTERNS list (ADR-0134 SSOT).\"\"\"
    return USAGE_PATTERNS
"""

    return (
        "\n\n".join(
            [
                header.rstrip(),
                f"AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {body}",
                f"# Short CLI-facing labels for token selection (ADR-0109).\n"
                f"# 3-8 words. Audience: selecting agent or human.\n"
                f"# Distinct from descriptions which are prompt-injection instructions.\n"
                f"AXIS_KEY_TO_LABEL: Dict[str, Dict[str, str]] = {label_body}",
                f"# Selection guidance for tokens where the description alone is ambiguous or\n"
                f"# where naming traps exist (ADR-0110). Not all tokens need this.\n"
                f"# Distinct from hard incompatibilities in hierarchy.incompatibilities.\n"
                f"AXIS_KEY_TO_GUIDANCE: Dict[str, Dict[str, str]] = {guidance_body}",
                f"# Task-type heuristics for when to apply each token (ADR-0132).\n"
                f"# Surfaces as 'When to use' helper text in UIs.\n"
                f"AXIS_KEY_TO_USE_WHEN: Dict[str, Dict[str, str]] = {use_when_body}",
                f"# Kanji icons for visual display (ADR-0143). 1-2 character kanji per token\n"
                f"# for faster visual scanning in help, SPA, and TUI2. Display only - not part\n"
                f"# of input grammar.\n"
                f"# Persona axis uses Dict[str, Dict[str, str]] (sub-axis -> token -> kanji);\n"
                f"# all other axes use Dict[str, str] (token -> kanji).\n"
                f"AXIS_KEY_TO_KANJI: Dict[str, Union[Dict[str, str], Dict[str, Dict[str, str]]]] = {kanji_body}",
                f"# Category assignments for method tokens (ADR-0144).\n"
                f"# Each method token is assigned to exactly one semantic family by primary use case.\n"
                f"# Tokens that span multiple families are placed by primary use case; contested\n"
                f"# placements are resolved by the authors and recorded here as the authoritative SSOT.\n"
                f"AXIS_KEY_TO_CATEGORY: Dict[str, Dict[str, str]] = {category_body}",
                f"# Distilled routing concept phrases for nav surfaces (ADR-0146 Phase 2).\n"
                f"# Each token maps to the shortest phrase that maps a user's framing to that token.\n"
                f"# Tokens sharing the same phrase group into a single routing bullet:\n"
                f"#   e.g. thing + struct → 'Entities/boundaries'\n"
                f"# Covered axes: scope and form only. Method routing uses editorial sub-group\n"
                f"# labels spanning multiple tokens and stays hardcoded until a future ADR.\n"
                f"AXIS_KEY_TO_ROUTING_CONCEPT: Dict[str, Dict[str, str]] = {routing_concept_body}",
                dataclasses.rstrip(),
                helpers.rstrip() + usage_patterns_block,
            ]
        ).rstrip()
        + "\n"
    )


def render_axis_markdown() -> str:
    """Render a simple Markdown fragment listing tokens per axis."""
    mapping = _axis_mapping()
    lines = ["# Axis tokens", ""]
    for axis in sorted(mapping.keys()):
        lines.append(f"## {axis}")
        for token in sorted(mapping[axis].keys()):
            lines.append(f"- {token}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_axis_catalog_json(lists_dir: Path | None = None) -> str:
    """Render the canonical axis catalog payload (axes + optional list tokens)."""

    payload = serialize_axis_config(
        lists_dir=lists_dir, include_axis_lists=True, include_static_prompts=True
    )
    return json.dumps(payload, indent=2, sort_keys=True)


def _format_with_black(text: str) -> str:
    """Format Python code with black if available, otherwise return unchanged."""
    try:
        result = subprocess.run(
            ["black", "--quiet", "-"],
            input=text,
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        # black not available or failed, return original
        return text


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        print(text)
        return
    output.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate axisConfig.py content from the axis registry"
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Path to write the generated module; prints to stdout when omitted.",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Render a Markdown fragment of axis tokens instead of Python module.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Render a JSON mapping of axis tokens instead of Python module.",
    )
    parser.add_argument(
        "--catalog-json",
        action="store_true",
        help="Render the canonical axis catalog JSON (axes + optional Talon list tokens).",
    )
    parser.add_argument(
        "--lists-dir",
        type=Path,
        default=None,
        help="Optional Talon lists directory for axis list tokens (catalog-only when omitted).",
    )
    args = parser.parse_args()
    if args.markdown:
        text = render_axis_markdown()
        _write_output(text, args.out)
    elif args.json:
        payload = _axis_mapping()
        text = json.dumps(payload, indent=2, sort_keys=True)
        if args.out is None:
            print(text)
        else:
            args.out.write_text(text + "\n", encoding="utf-8")
    elif args.catalog_json:
        text = render_axis_catalog_json(args.lists_dir)
        _write_output(text, args.out)
    else:
        text = render_axis_config()
        # Format Python code with black to match IDE formatting
        text = _format_with_black(text)
        _write_output(text, args.out)


if __name__ == "__main__":  # pragma: no cover
    main()

"""Generate axisConfig-style token->description maps from the axis registry.

Outputs a Python module defining AXIS_KEY_TO_VALUE plus the small dataclasses
used by the existing axisConfig façade. Intended as a deterministic generator
to keep axisConfig.py/README fragments in sync with the registry.
"""

from __future__ import annotations

import argparse
import sys
import pprint
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lib.axisConfig import axis_docs_for  # type: ignore  # noqa: E402
from lib.axisMappings import axis_registry  # type: ignore  # noqa: E402


def _axis_mapping() -> dict[str, dict[str, str]]:
    """Return axis token -> description mapping from the registry."""
    mapping: dict[str, dict[str, str]] = {}
    for axis in sorted(axis_registry().keys()):
        docs = axis_docs_for(axis)
        mapping[axis] = {doc.key: doc.description for doc in docs}
    return mapping


def render_axis_config() -> str:
    """Render an axisConfig.py module based on the registry."""
    mapping = _axis_mapping()
    body = pprint.pformat(mapping, width=100, sort_dicts=True)
    header = textwrap.dedent(
        """\
        \"\"\"Axis configuration as static Python maps (token -> description).

        Generated from the axis registry; keep in sync with list edits.\"\"\"

        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import Dict, FrozenSet
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
    return "\n\n".join(
        [
            header.rstrip(),
            f"AXIS_KEY_TO_VALUE: Dict[str, Dict[str, str]] = {body}",
            dataclasses.rstrip(),
        ]
    ).rstrip() + "\n"


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
    args = parser.parse_args()
    text = render_axis_markdown() if args.markdown else render_axis_config()
    _write_output(text, args.out)


if __name__ == "__main__":  # pragma: no cover
    main()

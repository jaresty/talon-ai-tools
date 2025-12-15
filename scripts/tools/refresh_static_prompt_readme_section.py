#!/usr/bin/env python3
"""Refresh the static prompt docs section in GPT/readme.md from the catalog generator."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from bootstrap import bootstrap  # type: ignore
except ModuleNotFoundError:
    bootstrap = None
else:
    bootstrap()

from scripts.tools.generate_static_prompt_docs import main as generate_static_prompt_docs  # type: ignore  # noqa: E402

START_MARKER = "## Help"
END_MARKER = "### Meta interpretation channel (ADR 019) and richer structure (ADR 020)"


def refresh_static_prompts(readme_path: Path, out_path: Path | None) -> None:
    tmp_path = readme_path.parent.parent / "tmp" / "static-prompt-docs.md"
    tmp_path.parent.mkdir(parents=True, exist_ok=True)
    generate_static_prompt_docs()
    content = readme_path.read_text(encoding="utf-8").splitlines()
    try:
        start_idx = next(i for i, line in enumerate(content) if line.strip() == START_MARKER)
        end_idx = next(i for i, line in enumerate(content) if line.strip() == END_MARKER)
    except StopIteration:
        raise RuntimeError("Could not find static prompts section markers in README")
    if end_idx <= start_idx:
        raise RuntimeError("End marker appears before start marker in README static prompts section")

    static_text = tmp_path.read_text(encoding="utf-8").splitlines()
    new_content = content[: start_idx + 1] + [""] + static_text + [""] + content[end_idx:]
    target_path = out_path or readme_path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("\n".join(new_content) + "\n", encoding="utf-8")
    print(f"Wrote refreshed static prompts section to {target_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--readme",
        type=Path,
        default=ROOT / "GPT" / "readme.md",
        help="Path to GPT README to update.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Optional output path; when set, write merged README content there instead of in-place.",
    )
    args = parser.parse_args()
    refresh_static_prompts(args.readme, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Capture a reproducible git log --stat snapshot for churn analysis.

This is a small, repo-local replacement for the AEM Manager
`churn-git-log-stat.mjs` helper referenced by the churn × complexity ADR
helper. It writes a text fixture that other tools (and humans) can inspect.

Environment variables:
    LINE_CHURN_SINCE   - git --since window (default: "90 days ago")
    LINE_CHURN_SCOPE   - comma-separated path prefixes
                          (default: "lib/,GPT/,copilot/,tests/")
    LINE_CHURN_OUTPUT  - output path for the log text
                          (default: "tmp/churn-scan/git-log-stat.txt")
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def build_git_args() -> list[str]:
    since = os.environ.get("LINE_CHURN_SINCE", "90 days ago")
    scope_raw = os.environ.get(
        "LINE_CHURN_SCOPE",
        "lib/,GPT/,copilot/,tests/",
    )
    # Allow simple comma-separated prefixes; ignore empties.
    scopes = [s.strip() for s in scope_raw.split(",") if s.strip()]

    args: list[str] = [
        "git",
        "log",
        "--stat",
        f"--since={since}",
        "--date=iso",
        "--no-color",
    ]
    if scopes:
        args.append("--")
        args.extend(scopes)

    return args


def main() -> None:
    output_path = Path(
        os.environ.get("LINE_CHURN_OUTPUT", "tmp/churn-scan/git-log-stat.txt")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_git_args()
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise SystemExit(
            f"git log failed with code {result.returncode}:\n{result.stderr}"
        )

    output_path.write_text(result.stdout, encoding="utf-8")
    print(f"wrote git log fixture to {output_path}")


if __name__ == "__main__":
    main()


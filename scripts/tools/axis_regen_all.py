#!/usr/bin/env python3
"""
Regenerate axis-derived artefacts into tmp/ for review.

This utility runs the existing generators to produce fresh axis outputs
without modifying tracked files. Outputs land in tmp/ so callers can
inspect diffs and apply manually.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


def run(cmd: list[str], env: Optional[Dict[str, str]] = None) -> None:
    subprocess.check_call(cmd, env=env)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    tmp_dir = repo_root / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["PYTHONPATH"] = str(repo_root)

    def _run_rel(args: list[str]) -> None:
        run([sys.executable, *args], env=env)

    # axisConfig and catalog outputs
    _run_rel(["scripts/tools/generate_axis_config.py", "--out", str(tmp_dir / "axisConfig.generated.py")])
    _run_rel(["scripts/tools/generate_axis_config.py", "--json", "--out", str(tmp_dir / "axisConfig.json")])
    _run_rel(["scripts/tools/generate_axis_config.py", "--catalog-json", "--out", str(tmp_dir / "axisCatalog.json")])
    # README axis lists and refreshed README section snapshot
    _run_rel(["scripts/tools/generate_readme_axis_lists.py", "--out", str(tmp_dir / "readme-axis-lists.md")])
    _run_rel(["scripts/tools/generate-axis-cheatsheet.py", "--out", str(tmp_dir / "readme-axis-cheatsheet.md")])
    _run_rel(
        [
            "scripts/tools/refresh_readme_axis_section.py",
            "--out",
            str(tmp_dir / "readme-axis-readme.md"),
        ]
    )
    # Static prompt docs snapshots
    _run_rel(["scripts/tools/generate_static_prompt_docs.py", "--out", str(tmp_dir / "static-prompt-docs.md")])
    _run_rel(
        [
            "scripts/tools/refresh_static_prompt_readme_section.py",
            "--out",
            str(tmp_dir / "static-prompt-readme.md"),
        ]
    )

    # Generate README axis tokens list for reference
    _run_rel(["scripts/tools/generate_axis_config.py", "--markdown", "--out", str(tmp_dir / "readme-axis-tokens.md")])

    # Validate the catalog/regenerated assets to catch drift early.
    validate_cmd = [
        sys.executable,
        "scripts/tools/axis-catalog-validate.py",
        "--skip-list-files",
    ]
    result = subprocess.run(validate_cmd, cwd=repo_root, text=True, capture_output=True, env=env)
    (tmp_dir / "axis-catalog-validate.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    result.check_returncode()
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Compatibility wrapper for churn-git-log-stat.

Delegates to the skill-scoped implementation so historical invocations keep
working while the helper now lives with the churn Concordance skill.
"""

from __future__ import annotations

import runpy
from pathlib import Path


def main() -> None:
    skill_script = (
        Path(__file__).resolve().parents[2]
        / ".claude"
        / "skills"
        / "churn-concordance-adr-helper"
        / "scripts"
        / "churn-git-log-stat.py"
    )
    runpy.run_path(str(skill_script), run_name="__main__")


if __name__ == "__main__":
    main()

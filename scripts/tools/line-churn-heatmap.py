"""Compatibility wrapper for line-churn-heatmap.

Maintains the historical entry point while delegating to the skill-scoped
implementation co-located with the churn Concordance ADR helper.
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
        / "line-churn-heatmap.py"
    )
    runpy.run_path(str(skill_script), run_name="__main__")


if __name__ == "__main__":
    main()

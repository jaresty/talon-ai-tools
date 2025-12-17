from pathlib import Path
from typing import Iterable, Optional


_AXIS_ARTIFACT_NAMES: tuple[str, ...] = (
    "axis-catalog-validate.log",
    "axisCatalog.json",
    "axisConfig.generated.py",
    "axisConfig.json",
    "readme-axis-cheatsheet.md",
    "readme-axis-lists.md",
    "readme-axis-readme.md",
    "readme-axis-tokens.md",
    "static-prompt-docs.md",
    "static-prompt-readme.md",
)


def cleanup_axis_regen_outputs(
    repo_root: Path, extra_names: Optional[Iterable[str]] = None
) -> None:
    """Remove generated axis artifacts under tmp/ to keep Talon scans clean."""

    tmp_dir = repo_root / "tmp"
    names = list(_AXIS_ARTIFACT_NAMES)
    if extra_names:
        names.extend(extra_names)
    for name in names:
        try:
            (tmp_dir / name).unlink()
        except FileNotFoundError:
            pass

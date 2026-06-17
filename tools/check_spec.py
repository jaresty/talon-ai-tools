#!/usr/bin/env python3
"""Schema checker for docs/api-spec.md.

Outputs lines prefixed with FAILED: for each missing required clause.
Exits 0 if all checks pass, 1 if any fail.
"""

import re
import sys
from pathlib import Path

SPEC_PATH = Path(__file__).parent.parent / "docs" / "api-spec.md"

REQUIRED_CLAUSES = [
    ("completeness", r"##\s+completeness", "FAILED: completeness clause absent"),
    ("authentication", r"##\s+authentication", "FAILED: authentication clause absent"),
    ("versioning", r"##\s+versioning", "FAILED: versioning clause absent"),
]


def check_spec(path: Path) -> list[str]:
    failures = []
    if not path.exists():
        for _, _, msg in REQUIRED_CLAUSES:
            failures.append(msg)
        return failures
    text = path.read_text().lower()
    for _name, pattern, msg in REQUIRED_CLAUSES:
        if not re.search(pattern, text):
            failures.append(msg)
    return failures


def main() -> int:
    failures = check_spec(SPEC_PATH)
    if failures:
        for line in failures:
            print(line)
        return 1
    print("OK: all required clauses present")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Protocol-conformance checker for protocols/meeting.md.

Parses the checklist and flags when required steps are absent.
Exits with a non-zero status when any required step is missing.

Output format on failure:
  FAIL
  <missing step name>

Output format on success:
  PASS
  <present step name>
  [... one line per required step ...]
"""

import sys
import re

REQUIRED_STEPS = [
    "acknowledgment confirmation",
]

CHECKLIST_ITEM_RE = re.compile(r"^\s*-\s*\[[ xX]\]\s*(.+)$", re.IGNORECASE)


def parse_steps(path: str) -> set[str]:
    """Return the set of checklist item labels found in *path* (lowercased)."""
    found = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = CHECKLIST_ITEM_RE.match(line)
                if m:
                    found.add(m.group(1).strip().lower())
    except FileNotFoundError:
        pass
    return found


def main(protocol_path: str = "protocols/meeting.md") -> int:
    present = parse_steps(protocol_path)

    missing = [s for s in REQUIRED_STEPS if s not in present]

    if missing:
        for step in missing:
            print("FAIL")
            print(step)
        return 1

    for step in REQUIRED_STEPS:
        print("PASS")
        print(step)
    return 0


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "protocols/meeting.md"
    sys.exit(main(path))

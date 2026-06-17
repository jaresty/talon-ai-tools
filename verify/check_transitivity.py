#!/usr/bin/env python3
"""
check_transitivity.py

Governing artifact for the transitivity property of the formal graph model.

Checks whether:
1. The spec document contains axiom A3 (closure under composition), which implies
   transitivity of the edge relation.
2. The spec document declares 'transitivity' as a verified property.

Output format:
  On success (property present and axiom implies it):
    PASS
    transitivity

  On failure (property absent or axiom missing):
    FAIL
    transitivity
"""

import re
import sys

SPEC_PATH = "docs/graph-model-spec.md"

AXIOM_PATTERN = re.compile(
    r"A3.*[Cc]losure under composition|"
    r"[Cc]losure under composition.*A3|"
    r"if.*\(u.*v\).*E.*and.*\(v.*w\).*E.*then.*\(u.*w\).*E",
    re.DOTALL,
)

PROPERTY_PATTERN = re.compile(r"(?m)^#+\s*[Pp]roperties\b")
TRANSITIVITY_DECLARED = re.compile(r"transitivity", re.IGNORECASE)


def check(spec_path: str) -> bool:
    try:
        with open(spec_path, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(2)

    # Check axiom A3 is present (prerequisite for transitivity being implied)
    if not AXIOM_PATTERN.search(content):
        return False

    # Find the Properties section
    prop_match = PROPERTY_PATTERN.search(content)
    if not prop_match:
        return False

    properties_section = content[prop_match.start():]

    # Check 'transitivity' is declared under Properties
    return bool(TRANSITIVITY_DECLARED.search(properties_section))


if __name__ == "__main__":
    result = check(SPEC_PATH)
    if result:
        print("PASS")
        print("transitivity")
    else:
        print("FAIL")
        print("transitivity")
    sys.exit(0 if result else 1)

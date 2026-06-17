"""Conformance checker for protocols/onboarding.md."""

import sys
import os

ONBOARDING_PATH = os.path.join(os.path.dirname(__file__), "..", "protocols", "onboarding.md")

REQUIRED_ITEMS = [
    ("conflict resolution", "FAILED: conflict resolution not found"),
]

def check():
    try:
        with open(ONBOARDING_PATH) as f:
            content = f.read().lower()
    except FileNotFoundError:
        print("FAILED: onboarding.md not found")
        sys.exit(1)

    failures = []
    for keyword, message in REQUIRED_ITEMS:
        if keyword not in content:
            failures.append(message)

    if failures:
        for msg in failures:
            print(msg)
        sys.exit(1)
    else:
        print("PASSED: all checks succeeded")
        sys.exit(0)

if __name__ == "__main__":
    check()

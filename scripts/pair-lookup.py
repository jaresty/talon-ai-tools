#!/usr/bin/env python3
"""Step 0 of ADR-0085's layer procedure: look a token pair up before writing any entry.

Answers the two questions the layer procedure cannot answer from judgement:
  1. Does a composition already ship for this pair?  (If yes, a cautionary is wrong by construction.)
  2. Does either token's definition already resolve it, or does its axis description?

Usage:
    python3 scripts/pair-lookup.py witness skim
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "lib"))

from axisConfig import (  # noqa: E402
    AXIS_KEY_TO_AXIS_DESC,
    AXIS_KEY_TO_VALUE,
    CROSS_AXIS_COMPOSITION,
)
from compositionConfig import COMPOSITIONS  # noqa: E402


def axes_of(token):
    return [axis for axis, d in AXIS_KEY_TO_VALUE.items() if token in d]


def main(a, b):
    axes_a, axes_b = axes_of(a), axes_of(b)
    for tok, axes in ((a, axes_a), (b, axes_b)):
        if not axes:
            print(f"unknown token: {tok}")
            return 2

    print(f"=== {a} ({'/'.join(axes_a)})  x  {b} ({'/'.join(axes_b)})\n")

    shipped = [e for e in COMPOSITIONS
               if set(x.strip() for x in e.get("name", "").split("+")) == {a, b}]
    if shipped:
        print("COMPOSITION EXISTS — a cautionary for this pair is wrong by construction:")
        for e in shipped:
            print(f"  {e['name']}: {e.get('prose', '').strip()}\n")
    else:
        print("composition: none\n")

    found = False
    for axis, d in CROSS_AXIS_COMPOSITION.items():
        for tok in (a, b):
            for oaxis, pair in (d.get(tok) or {}).items():
                other = b if tok == a else a
                reason = (pair.get("cautionary") or {}).get(other)
                if reason:
                    found = True
                    print(f"CAUTIONARY [{axis}.{tok}.{oaxis}.{other}]\n  {reason}\n")
                if other in (pair.get("natural") or []):
                    found = True
                    print(f"NATURAL [{axis}.{tok}.{oaxis}] lists {other}\n")
    if not found:
        print("cross-axis entries: none\n")

    for tok, axes in ((a, axes_a), (b, axes_b)):
        other = b if tok == a else a
        definition = AXIS_KEY_TO_VALUE[axes[0]][tok]
        if other in definition:
            print(f"DEFINITION of {tok} names {other} — read it before adding an entry:\n  {definition}\n")

    for axis in set(axes_a) | set(axes_b):
        desc = AXIS_KEY_TO_AXIS_DESC.get(axis)
        if desc and len(desc) > 120:
            print(f"AXIS DESCRIPTION ({axis}) carries a rule that may already govern this pair:\n  {desc}\n")

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2]))

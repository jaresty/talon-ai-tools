#!/usr/bin/env python3
"""
Generate a ranked method×method candidate list for composition discovery (ADR-0227 Loop-C).

Priority filter (output order):
  1. Same-category pairs (highest signal — tokens share structural framing)
  2. Cross-category pairs with semantic proximity (shared keywords in definitions)
  3. Cross-category pairs with no keyword overlap (lowest signal — additive by default)

Pairs already evaluated (any status) in docs/composition-candidates.md are excluded.

Usage:
    python3 scripts/composition-candidates-generate.py [--top N] [--category CAT]

Output: ranked table suitable for pasting into docs/composition-candidates.md pending section.
"""

import json
import re
import sys
import argparse
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).parent.parent

GRAMMAR_PATH = ROOT / "build" / "prompt-grammar.json"
CANDIDATES_PATH = ROOT / "docs" / "composition-candidates.md"

# Keywords that signal behavioral interaction potential — tokens sharing these
# are more likely to have emergent requirements when co-present.
INTERACTION_KEYWORDS = {
    "governing artifact", "artifact", "assertion", "failure", "predecessor",
    "evidence", "enforce", "verify", "gate", "cycle", "constraint",
    "derivation", "step", "termination", "scope", "implementation",
    "visible", "observable", "audit", "checkpoint",
}


def load_grammar():
    with open(GRAMMAR_PATH) as f:
        return json.load(f)


def load_evaluated_pairs():
    """Return set of frozensets of already-evaluated pairs from candidates.md."""
    evaluated = set()
    text = CANDIDATES_PATH.read_text()
    for line in text.splitlines():
        # Match table rows: | token + token | status | ...
        m = re.match(r"\|\s*([\w-]+)\s*\+\s*([\w-]+)\s*\|", line)
        if m:
            evaluated.add(frozenset([m.group(1).strip(), m.group(2).strip()]))
    return evaluated


def keyword_overlap(def_a: str, def_b: str) -> int:
    words_a = set(def_a.lower().split())
    words_b = set(def_b.lower().split())
    return sum(
        1 for kw in INTERACTION_KEYWORDS
        if any(kw in w for w in words_a) and any(kw in w for w in words_b)
    )


def generate_candidates(top_n: int, category_filter: str | None):
    grammar = load_grammar()
    evaluated = load_evaluated_pairs()

    method_defs = grammar["axes"]["definitions"].get("method", {})
    method_cats = grammar["axes"].get("categories", {}).get("method", {})
    tokens = sorted(method_defs.keys())

    candidates = []
    for a, b in combinations(tokens, 2):
        pair = frozenset([a, b])
        if pair in evaluated:
            continue
        if category_filter and method_cats.get(a) != category_filter and method_cats.get(b) != category_filter:
            continue

        cat_a = method_cats.get(a, "")
        cat_b = method_cats.get(b, "")
        same_cat = cat_a == cat_b and cat_a != ""
        overlap = keyword_overlap(method_defs[a], method_defs[b])

        # Priority score: same-category = 1000 + overlap; cross = overlap
        priority = (1000 if same_cat else 0) + overlap * 10

        rationale_parts = []
        if same_cat:
            rationale_parts.append(f"same category ({cat_a})")
        if overlap > 0:
            rationale_parts.append(f"{overlap} shared interaction keyword(s)")
        rationale = "; ".join(rationale_parts) if rationale_parts else "cross-category, low overlap"

        candidates.append((priority, a, b, cat_a, cat_b, rationale))

    candidates.sort(key=lambda x: -x[0])

    total_pairs = len(tokens) * (len(tokens) - 1) // 2
    total_same_cat = sum(
        1 for a, b in combinations(tokens, 2)
        if method_cats.get(a) == method_cats.get(b) and method_cats.get(a)
    )
    evaluated_same_cat = sum(
        1 for pair in evaluated
        if len(pair) == 2 and len(set(method_cats.get(t, '') for t in pair) - {''}) == 1
    )

    print(f"## Generated candidates (top {top_n})\n")
    print(f"Coverage: {len(evaluated)} / {total_pairs} pairs evaluated "
          f"({100*len(evaluated)/total_pairs:.1f}%) | "
          f"High-priority (same-category): {evaluated_same_cat} / {total_same_cat} "
          f"({100*evaluated_same_cat/total_same_cat:.1f}%)\n")
    print(f"| Pair | Priority | Rationale |")
    print(f"|---|---|---|")
    for _, a, b, cat_a, cat_b, rationale in candidates[:top_n]:
        tier = "high" if cat_a == cat_b and cat_a else "medium" if "keyword" in rationale else "low"
        print(f"| {a} + {b} | {tier} | {rationale} |")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--top", type=int, default=20, help="Number of candidates to output (default: 20)")
    parser.add_argument("--category", type=str, default=None, help="Filter to pairs involving this category")
    args = parser.parse_args()
    generate_candidates(args.top, args.category)

#!/usr/bin/env python3
"""
Detect usage of obsolete tokens in test files.

Usage:
    python scripts/tools/detect-obsolete-tokens.py [--strict] [--update-list]

This script helps prevent regressions by flagging removed tokens that
still appear in test files or code.
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Set


# Known obsolete tokens (removed in ADR 0091/0092 and other changes)
# Add tokens here when they're removed from the vocabulary
OBSOLETE_TOKENS = {
    # Scope tokens (removed/renamed)
    'focus',
    'narrow',
    'bound',
    'edges',
    'relations',
    'system',
    'actions',  # moved to form as 'actions', use 'act' for scope

    # Method tokens (removed/renamed)
    'steps',  # moved to form, use 'flow' for method
    'plan',   # use 'flow' for method (but 'plan' static prompt is valid)
    'xp',
    'cluster',
    'debugging',  # use 'diagnose'
    'liberating',
    'diverge',
    'filter',
    'structure',

    # Intent tokens (removed)
    'decide',
    'evaluate',

    # Static prompts (removed/renamed)
    'describe',  # use 'show'
    'todo',      # use 'make'
    'dependency',
    'product',
    'retro',
    'risky',
}

# Tokens that are valid in some contexts but not others
# Format: {token: allowed_contexts}
CONTEXTUAL_TOKENS = {
    'plan': ['static prompt', 'task name'],  # Valid as static prompt, not as method
    'actions': ['form axis'],                 # Valid as form token, not scope
    'steps': ['form axis'],                   # Valid as form token, not method
}


def extract_string_literals(file_path: Path) -> List[tuple[str, int]]:
    """
    Extract all string literals from a Python file with line numbers.

    Returns:
        List of (string_value, line_number) tuples
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except SyntaxError:
        return []

    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if hasattr(node, 'lineno'):
                strings.append((node.value, node.lineno))
    return strings


def check_file(file_path: Path, strict: bool = False) -> Dict[str, List[int]]:
    """
    Check a file for obsolete token usage.

    Args:
        file_path: Path to file to check
        strict: If True, report all occurrences; if False, only in string literals

    Returns:
        Dict mapping obsolete_token -> [line_numbers]
    """
    issues = {}

    if strict:
        # Simple text search (faster but more false positives)
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        for token in OBSOLETE_TOKENS:
            # Use word boundary to avoid matching substrings
            pattern = re.compile(rf'\b{re.escape(token)}\b')
            for line_num, line in enumerate(lines, start=1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                if pattern.search(line):
                    issues.setdefault(token, []).append(line_num)
    else:
        # Parse AST and check string literals only (more accurate)
        string_literals = extract_string_literals(file_path)

        for string_value, line_num in string_literals:
            for token in OBSOLETE_TOKENS:
                # Check if token appears as whole word in string
                if re.search(rf'\b{re.escape(token)}\b', string_value):
                    issues.setdefault(token, []).append(line_num)

    return issues


def update_obsolete_list():
    """
    Scan axis configuration and generate updated obsolete token list.

    This helps maintain the OBSOLETE_TOKENS list by comparing against
    historical token vocabulary.
    """
    print("Scanning current token vocabulary...")

    try:
        # Import current tokens
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from lib.axisCatalog import axis_catalog

        catalog = axis_catalog()
        axes = catalog.get('axes', {})

        current_tokens = set()
        for axis_name, axis_dict in axes.items():
            if axis_dict:
                current_tokens.update(axis_dict.keys())

        print(f"\nCurrent vocabulary: {len(current_tokens)} tokens across {len(axes)} axes")
        print("\nTo update OBSOLETE_TOKENS list:")
        print("1. Review tokens removed since last check")
        print("2. Add them to OBSOLETE_TOKENS in this script")
        print("3. Document context in comments if needed")

    except ImportError as e:
        print(f"Error importing axis catalog: {e}")
        return 1

    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Detect obsolete token usage in test files',
        epilog='''
Examples:
  # Check test files for obsolete tokens:
  python scripts/tools/detect-obsolete-tokens.py

  # Check all Python files (including lib/):
  python scripts/tools/detect-obsolete-tokens.py --strict

  # Update the obsolete token list:
  python scripts/tools/detect-obsolete-tokens.py --update-list
        '''
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Check all occurrences (not just string literals); may have false positives'
    )
    parser.add_argument(
        '--update-list',
        action='store_true',
        help='Show current token vocabulary to help update OBSOLETE_TOKENS list'
    )
    parser.add_argument(
        '--include-lib',
        action='store_true',
        help='Also check lib/ directory (not just tests)'
    )

    args = parser.parse_args()

    if args.update_list:
        return update_obsolete_list()

    if not OBSOLETE_TOKENS:
        print("No obsolete tokens defined in OBSOLETE_TOKENS.")
        print("Run with --update-list to see current vocabulary.")
        return 0

    # Find files to check
    repo_root = Path(__file__).resolve().parents[2]
    test_dir = repo_root / '_tests'
    files_to_check = list(test_dir.glob('test_*.py'))

    if args.include_lib:
        lib_dir = repo_root / 'lib'
        files_to_check.extend(lib_dir.glob('*.py'))

    if not files_to_check:
        print("No files found to check.")
        return 1

    print(f"Checking {len(files_to_check)} file(s) for {len(OBSOLETE_TOKENS)} obsolete token(s)...")
    if args.strict:
        print("(Strict mode: checking all occurrences, may have false positives)")
    print()

    # Check files
    total_issues = {}
    files_with_issues = 0

    for file_path in sorted(files_to_check):
        issues = check_file(file_path, strict=args.strict)
        if issues:
            files_with_issues += 1
            print(f"{file_path.relative_to(repo_root)}:")
            for token, line_nums in sorted(issues.items()):
                print(f"  {token}: line(s) {', '.join(map(str, line_nums))}")
                total_issues[token] = total_issues.get(token, 0) + len(line_nums)
            print()

    # Summary
    if total_issues:
        print(f"Found obsolete tokens in {files_with_issues} file(s):")
        for token, count in sorted(total_issues.items(), key=lambda x: -x[1]):
            print(f"  {token}: {count} occurrence(s)")
        print("\nTo fix:")
        print("  1. Review the token migration guide in docs/TROUBLESHOOTING_TEST_FAILURES.md")
        print("  2. Use scripts/tools/migrate-test-tokens.py for bulk replacements")
        print("  3. Manually verify context-sensitive changes")
        return 1
    else:
        print("No obsolete tokens found. ✓")
        return 0


if __name__ == '__main__':
    sys.exit(main())

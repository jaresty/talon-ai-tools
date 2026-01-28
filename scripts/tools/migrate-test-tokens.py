#!/usr/bin/env python3
"""
Migrate test files to use updated token vocabulary.

Usage:
    python scripts/tools/migrate-test-tokens.py [--dry-run] [--verbose]

This script automates the find/replace pattern when tokens are renamed,
removed, or moved between axes.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Token migrations: old_token -> new_token
# Add new migrations here when tokens change
TOKEN_MIGRATIONS: Dict[str, str] = {
    # Example migrations from ADR 0091/0092 Phase 1:
    # 'focus': 'struct',
    # 'actions': 'act',
    # 'steps': 'flow',
    # 'plan': 'flow',
    # 'decide': 'inform',
    # 'describe': 'show',
    # 'todo': 'make',
}

# Context-aware migrations: only replace in specific patterns
# Format: (old_token, new_token, regex_pattern)
CONTEXTUAL_MIGRATIONS: List[Tuple[str, str, str]] = [
    # Example: Replace 'plan' only when used as method token, not static prompt
    # ('plan', 'flow', r'GPTState\.last_method\s*=\s*["\']plan["\']'),
]


def migrate_file(file_path: Path, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
    """
    Migrate tokens in a single test file.

    Returns:
        Dict with counts of changes per token
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = {}

    # Apply simple token migrations
    for old_token, new_token in TOKEN_MIGRATIONS.items():
        # Count occurrences
        pattern = re.compile(rf'\b{re.escape(old_token)}\b')
        matches = pattern.findall(content)
        if matches:
            count = len(matches)
            changes[old_token] = changes.get(old_token, 0) + count
            content = pattern.sub(new_token, content)
            if verbose:
                print(f"  {old_token} -> {new_token}: {count} occurrence(s)")

    # Apply contextual migrations
    for old_token, new_token, regex_pattern in CONTEXTUAL_MIGRATIONS:
        pattern = re.compile(regex_pattern)
        matches = pattern.findall(content)
        if matches:
            count = len(matches)
            changes[f"{old_token} (contextual)"] = changes.get(f"{old_token} (contextual)", 0) + count
            content = pattern.sub(lambda m: m.group(0).replace(old_token, new_token), content)
            if verbose:
                print(f"  {old_token} -> {new_token} (contextual): {count} occurrence(s)")

    # Write changes if not dry run and content changed
    if not dry_run and content != original_content:
        file_path.write_text(content, encoding='utf-8')

    return changes


def main():
    parser = argparse.ArgumentParser(
        description='Migrate test files to updated token vocabulary',
        epilog='''
Examples:
  # Preview changes without writing:
  python scripts/tools/migrate-test-tokens.py --dry-run --verbose

  # Apply migrations:
  python scripts/tools/migrate-test-tokens.py

  # Migrate specific file:
  python scripts/tools/migrate-test-tokens.py --file _tests/test_foo.py
        '''
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would change without modifying files'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed changes per file'
    )
    parser.add_argument(
        '--file',
        type=Path,
        help='Migrate specific file instead of all test files'
    )

    args = parser.parse_args()

    # Check if migrations are defined
    if not TOKEN_MIGRATIONS and not CONTEXTUAL_MIGRATIONS:
        print("No token migrations defined in TOKEN_MIGRATIONS or CONTEXTUAL_MIGRATIONS.")
        print("Edit this script to add migrations, then run again.")
        return 1

    # Find test files
    if args.file:
        if not args.file.exists():
            print(f"Error: File not found: {args.file}")
            return 1
        test_files = [args.file]
    else:
        repo_root = Path(__file__).resolve().parents[2]
        test_dir = repo_root / '_tests'
        test_files = sorted(test_dir.glob('test_*.py'))

    if not test_files:
        print("No test files found.")
        return 1

    # Show migration plan
    print(f"{'DRY RUN: ' if args.dry_run else ''}Migrating {len(test_files)} test file(s)...")
    if TOKEN_MIGRATIONS:
        print("\nToken migrations:")
        for old, new in TOKEN_MIGRATIONS.items():
            print(f"  {old} -> {new}")
    if CONTEXTUAL_MIGRATIONS:
        print("\nContextual migrations:")
        for old, new, pattern in CONTEXTUAL_MIGRATIONS:
            print(f"  {old} -> {new} (pattern: {pattern})")
    print()

    # Migrate files
    total_changes = {}
    files_changed = 0

    for file_path in test_files:
        if args.verbose:
            print(f"Processing {file_path.name}...")

        changes = migrate_file(file_path, dry_run=args.dry_run, verbose=args.verbose)

        if changes:
            files_changed += 1
            if not args.verbose:
                print(f"  {file_path.name}: {sum(changes.values())} change(s)")

            for token, count in changes.items():
                total_changes[token] = total_changes.get(token, 0) + count

    # Summary
    print(f"\n{'Would change' if args.dry_run else 'Changed'} {files_changed} file(s):")
    for token, count in sorted(total_changes.items()):
        print(f"  {token}: {count} total occurrence(s)")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")

    return 0


if __name__ == '__main__':
    sys.exit(main())

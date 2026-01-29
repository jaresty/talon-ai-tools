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

# Go test token migrations: old_token -> new_token
# Populate this when migrating tokens in Go test files
GO_TOKEN_MIGRATIONS: Dict[str, str] = {
    # Example migrations from ADR 0091/0092 (already applied):
    # Uncomment and update these when new token migrations are needed
    # 'old_token': 'new_token',
}


def migrate_go_file(file_path: Path, dry_run: bool = False, verbose: bool = False) -> Dict[str, int]:
    """
    Migrate tokens in a Go test file.

    Returns:
        Dict with counts of changes per token
    """
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    changes = {}

    # Apply Go token migrations
    # Match string literals in Go: "token" (with word boundaries)
    for old_token, new_token in GO_TOKEN_MIGRATIONS.items():
        # Pattern matches quoted tokens with word boundaries
        # This handles: []string{"foo", "old_token", "bar"}
        pattern = re.compile(rf'"{re.escape(old_token)}"')
        matches = pattern.findall(content)
        if matches:
            count = len(matches)
            changes[old_token] = changes.get(old_token, 0) + count
            content = pattern.sub(f'"{new_token}"', content)
            if verbose:
                print(f"  {old_token} -> {new_token}: {count} occurrence(s)")

    # Write changes if not dry run and content changed
    if not dry_run and content != original_content:
        file_path.write_text(content, encoding='utf-8')

    return changes


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
  # Preview Python test changes:
  python scripts/tools/migrate-test-tokens.py --dry-run --verbose

  # Apply Python migrations:
  python scripts/tools/migrate-test-tokens.py

  # Preview Go test changes:
  python scripts/tools/migrate-test-tokens.py --go --dry-run

  # Apply Go migrations:
  python scripts/tools/migrate-test-tokens.py --go

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
    parser.add_argument(
        '--go',
        action='store_true',
        help='Migrate Go test files instead of Python test files'
    )

    args = parser.parse_args()

    # Check if migrations are defined
    if args.go:
        if not GO_TOKEN_MIGRATIONS:
            print("Warning: No Go token migrations defined in GO_TOKEN_MIGRATIONS.")
            print("Edit this script to add Go migrations when needed.")
            print()
    else:
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
        if args.go:
            # Find Go test files in internal/barcli/
            go_dir = repo_root / 'internal' / 'barcli'
            test_files = sorted(go_dir.glob('*_test.go'))
        else:
            # Find Python test files in _tests/
            test_dir = repo_root / '_tests'
            test_files = sorted(test_dir.glob('test_*.py'))

    if not test_files:
        print("No test files found.")
        return 1

    # Show migration plan
    file_type = "Go" if args.go else "Python"
    print(f"{'DRY RUN: ' if args.dry_run else ''}Migrating {len(test_files)} {file_type} test file(s)...")

    if args.go:
        if GO_TOKEN_MIGRATIONS:
            print("\nGo token migrations:")
            for old, new in GO_TOKEN_MIGRATIONS.items():
                print(f"  {old} -> {new}")
        else:
            print("\nNo Go token migrations configured (GO_TOKEN_MIGRATIONS is empty).")
    else:
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

        # Use appropriate migration function based on file type
        if args.go:
            changes = migrate_go_file(file_path, dry_run=args.dry_run, verbose=args.verbose)
        else:
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

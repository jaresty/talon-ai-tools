#!/usr/bin/env bash
# Validation for ADR 0097 Loop 3: Help text includes install-skills command
# Tests that general help output documents the install-skills command

set -e

# Use development bar if available, otherwise use system bar
if [ -x "$HOME/bin/bar" ]; then
    BAR="$HOME/bin/bar"
else
    BAR="bar"
fi

echo "Validating bar help includes install-skills command..."

# Test 1: General help mentions install-skills
if ! $BAR help 2>&1 | grep -q "install-skills"; then
    echo "ERROR: 'bar help' output does not mention install-skills"
    exit 1
fi
echo "✓ General help mentions install-skills"

# Test 2: Top-level usage includes install-skills
if ! $BAR 2>&1 | grep -q "install-skills"; then
    echo "ERROR: Top-level usage does not mention install-skills"
    exit 1
fi
echo "✓ Top-level usage includes install-skills"

# Test 3: install-skills help is accessible
if ! $BAR install-skills --help >/dev/null 2>&1; then
    echo "ERROR: 'bar install-skills --help' failed"
    exit 1
fi
echo "✓ install-skills help is accessible"

echo "Help text validation successful"
exit 0

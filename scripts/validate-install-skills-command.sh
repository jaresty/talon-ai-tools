#!/usr/bin/env bash
# Validation for ADR 0097 Loop 2: $BAR install-skills command exists and works
# Tests that the command can install embedded skills to target directory

set -e

# Use development bar if available, otherwise use system bar
if [ -x "$HOME/bin/bar" ]; then
    BAR="$HOME/bin/bar"
else
    BAR="bar"
fi

echo "Validating $BAR install-skills command (using: $BAR)..."

# Test 1: Command exists and shows help
if ! $BAR install-skills --help >/dev/null 2>&1; then
    echo "ERROR: '$BAR install-skills --help' failed"
    exit 1
fi
echo "✓ Command exists and shows help"

# Test 2: Dry-run mode works
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

if ! $BAR install-skills --dry-run --location "$TEMP_DIR/.claude/skills" >/dev/null 2>&1; then
    echo "ERROR: '$BAR install-skills --dry-run' failed"
    exit 1
fi
echo "✓ Dry-run mode works"

# Test 3: Actual installation works
if ! $BAR install-skills --location "$TEMP_DIR/.claude/skills" >/dev/null 2>&1; then
    echo "ERROR: '$BAR install-skills' installation failed"
    exit 1
fi

# Test 4: Verify skills were installed
REQUIRED_SKILLS=("bar-autopilot" "bar-workflow" "bar-suggest" "bar-manual")
for skill in "${REQUIRED_SKILLS[@]}"; do
    skill_file="$TEMP_DIR/.claude/skills/$skill/skill.md"
    if [ ! -f "$skill_file" ]; then
        echo "ERROR: Skill not installed: $skill_file"
        exit 1
    fi
done
echo "✓ All skills installed successfully"

echo "$BAR install-skills command validated successfully"
exit 0

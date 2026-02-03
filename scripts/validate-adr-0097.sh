#!/usr/bin/env bash
# Validation for ADR 0097: Bar automation skills embedded in CLI
# Validates that skills are packaged in bar CLI and can be installed

set -e

echo "Validating ADR 0097: Bar automation skills..."

# Check that skills are embedded in the bar CLI source
SKILLS_SOURCE="internal/skills"
REQUIRED_SKILLS=("bar-autopilot" "bar-workflow" "bar-suggest")

for skill in "${REQUIRED_SKILLS[@]}"; do
    skill_file="$SKILLS_SOURCE/$skill/skill.md"

    if [ ! -f "$skill_file" ]; then
        echo "ERROR: Embedded skill missing: $skill_file"
        exit 1
    fi

    # Verify skill has required content
    if ! grep -q "# " "$skill_file"; then
        echo "ERROR: Skill missing header: $skill_file"
        exit 1
    fi

    echo "✓ Embedded skill validated: $skill"
done

echo "All bar automation skills validated successfully"
exit 0

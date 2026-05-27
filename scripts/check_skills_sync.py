#!/usr/bin/env python3
"""Check that embedded skills in internal/barcli/skills/ match their .claude/skills/ sources.

Only checks skills that exist in internal/barcli/skills/ (the embedded set).
Skills in .claude/skills/ that are not embedded are ignored.

Exits 1 with a diff summary if any embedded SKILL.md differs from its source.
Run as a pre-commit hook to catch divergence before it lands.
"""
import sys
import filecmp
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC = ROOT / ".claude" / "skills"
EMBED = ROOT / "internal" / "barcli" / "skills"

def main() -> int:
    errors = []
    for skill_dir in sorted(EMBED.iterdir()):
        if not skill_dir.is_dir():
            continue
        for embed_file in sorted(skill_dir.rglob("SKILL.md")):
            rel = embed_file.relative_to(EMBED)
            src_file = SRC / rel
            if not src_file.exists():
                errors.append(f"  MISSING in .claude/skills/: {rel}")
                continue
            if not filecmp.cmp(src_file, embed_file, shallow=False):
                errors.append(f"  OUT OF SYNC: {rel}")

    if errors:
        print("Skills sync check FAILED — internal/barcli/skills/ differs from .claude/skills/:")
        for e in errors:
            print(e)
        print("\nFix: cp .claude/skills/<name>/SKILL.md internal/barcli/skills/<name>/SKILL.md")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())

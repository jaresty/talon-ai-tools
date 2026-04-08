package barcli

// Guard test: embedded skills in internal/barcli/skills/ must exactly match
// their counterparts in .claude/skills/. If they diverge, bar install-skills
// will install stale content.
//
// When updating a skill: edit .claude/skills/<name>/skill.md (source of truth),
// then cp it to internal/barcli/skills/<name>/skill.md (embedded copy).

import (
	"os"
	"path/filepath"
	"testing"
)

func TestEmbeddedSkillsMatchSourceSkills(t *testing.T) {
	// Locate repo root relative to this test file's package directory.
	// The test binary runs with working directory set to the package directory.
	repoRoot, err := filepath.Abs("../..")
	if err != nil {
		t.Fatalf("could not determine repo root: %v", err)
	}

	embeddedDir := filepath.Join(repoRoot, "internal", "barcli", "skills")
	sourceDir := filepath.Join(repoRoot, ".claude", "skills")

	entries, err := os.ReadDir(embeddedDir)
	if err != nil {
		t.Fatalf("could not read embedded skills dir %s: %v", embeddedDir, err)
	}

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		skillName := entry.Name()
		embeddedFile := filepath.Join(embeddedDir, skillName, "skill.md")
		sourceFile := filepath.Join(sourceDir, skillName, "skill.md")

		embeddedContent, err := os.ReadFile(embeddedFile)
		if err != nil {
			t.Errorf("skill %q: could not read embedded file %s: %v", skillName, embeddedFile, err)
			continue
		}
		sourceContent, err := os.ReadFile(sourceFile)
		if err != nil {
			t.Errorf("skill %q: could not read source file %s: %v — did you forget to create the source?", skillName, sourceFile, err)
			continue
		}
		if string(embeddedContent) != string(sourceContent) {
			t.Errorf("skill %q: embedded and source skill.md files differ.\n"+
				"Source of truth: %s\n"+
				"Embedded copy:   %s\n"+
				"Run: cp %s %s", skillName, sourceFile, embeddedFile, sourceFile, embeddedFile)
		}
	}
}

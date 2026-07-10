package barcli

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

func TestInstallSkillsDefaultLocation(t *testing.T) {
	t.TempDir() // ensure we don't accidentally write to real ~/.claude/skills
	// When no --location flag is given, the default must expand to ~/.claude/skills (not .claude/skills)
	opts := &cli.Config{}
	var stdout, stderr bytes.Buffer
	// We only check what location would be used — dry-run surfaces it without writing
	opts.DryRun = true
	code := runInstallSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("runInstallSkills dry-run exited %d: %s", code, stderr.String())
	}
	out := stdout.String()
	if strings.Contains(out, `".claude/skills"`) || (!strings.Contains(out, ".claude/skills") && !strings.Contains(out, "/.claude/skills")) {
		t.Errorf("expected default location to contain ~/.claude/skills, got: %s", out)
	}
	if strings.HasPrefix(out, "Would install bar skills to: .claude/skills") {
		t.Errorf("default location must not be project-relative .claude/skills, got: %s", out)
	}
	if !strings.Contains(out, "/.claude/skills") {
		t.Errorf("expected expanded home path in default location, got: %s", out)
	}
}

func TestBarSkillsListExcludesStub(t *testing.T) {
	opts := &cli.Config{Tokens: []string{"list"}}
	var stdout, stderr bytes.Buffer
	code := runSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("bar skills list exited %d: %s", code, stderr.String())
	}
	for _, line := range strings.Split(stdout.String(), "\n") {
		if strings.HasPrefix(strings.TrimSpace(line), "bar ") && !strings.HasPrefix(strings.TrimSpace(line), "bar-") {
			t.Errorf("bar skills list must not list the stub skill 'bar', got line: %s", line)
		}
	}
}

func TestBarSkillsList(t *testing.T) {
	opts := &cli.Config{
		Tokens: []string{"list"},
	}
	var stdout, stderr bytes.Buffer
	code := runSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("bar skills list exited %d: %s", code, stderr.String())
	}
	out := stdout.String()
	// Must list at least one skill with a name and description
	if !strings.Contains(out, "bar") {
		t.Errorf("expected skill names in output, got: %s", out)
	}
}

func TestBarSkillsGet(t *testing.T) {
	opts := &cli.Config{
		Tokens: []string{"get", "bar"},
	}
	var stdout, stderr bytes.Buffer
	code := runSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("bar skills get bar exited %d: %s", code, stderr.String())
	}
	out := stdout.String()
	// Must return non-empty skill content
	if len(strings.TrimSpace(out)) == 0 {
		t.Errorf("expected skill content, got empty output")
	}
}

func TestSkillDescriptionFormats(t *testing.T) {
	cases := []struct {
		name    string
		content string
		want    string
	}{
		{
			name: "plain",
			content: "---\nname: foo\ndescription: A plain description.\n---\n",
			want: "A plain description.",
		},
		{
			name: "quoted",
			content: "---\nname: foo\ndescription: \"A quoted description.\"\n---\n",
			want: "A quoted description.",
		},
		{
			name: "folded",
			content: "---\nname: foo\ndescription: >\n  A folded description that continues here.\n---\n",
			want: "A folded description that continues here.",
		},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			got := extractDescription(tc.content)
			if got != tc.want {
				t.Errorf("extractDescription(%q) = %q, want %q", tc.name, got, tc.want)
			}
		})
	}
}

func TestInstallSkillsOnlyInstallsStub(t *testing.T) {
	dir := t.TempDir()
	opts := &cli.Config{Location: dir, Force: true}
	var stdout, stderr bytes.Buffer
	code := runInstallSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("runInstallSkills exited %d: %s", code, stderr.String())
	}
	entries, err := os.ReadDir(dir)
	if err != nil {
		t.Fatalf("could not read install dir: %v", err)
	}
	for _, e := range entries {
		if e.Name() != "bar" {
			t.Errorf("install wrote unexpected entry %q — only bar/ stub should be installed", e.Name())
		}
	}
	if _, err := os.Stat(filepath.Join(dir, "bar", "SKILL.md")); err != nil {
		t.Errorf("bar/SKILL.md not found after install: %v", err)
	}
}

func TestInstallSkillsRemovesDeprecated(t *testing.T) {
	dir := t.TempDir()
	// Plant deprecated skill dirs in the target location
	deprecated := []string{"bar-autopilot", "bar-workflow", "bar-suggest", "bar-manual", "bar-dictionary"}
	for _, name := range deprecated {
		if err := os.MkdirAll(filepath.Join(dir, name), 0755); err != nil {
			t.Fatalf("setup: %v", err)
		}
		if err := os.WriteFile(filepath.Join(dir, name, "SKILL.md"), []byte("old content"), 0644); err != nil {
			t.Fatalf("setup: %v", err)
		}
	}

	opts := &cli.Config{Location: dir, Force: true}
	var stdout, stderr bytes.Buffer
	code := runInstallSkills(opts, &stdout, &stderr)
	if code != 0 {
		t.Fatalf("runInstallSkills exited %d: %s", code, stderr.String())
	}

	out := stdout.String()
	for _, name := range deprecated {
		// Each deprecated skill should be reported as removed
		if !strings.Contains(out, name) {
			t.Errorf("expected %q to be mentioned in removal output, got: %s", name, out)
		}
		// The deprecated dirs must be gone
		if _, err := os.Stat(filepath.Join(dir, name)); !os.IsNotExist(err) {
			t.Errorf("deprecated skill dir %q still exists after install", name)
		}
	}
}

func TestBarSkillsGetUnknown(t *testing.T) {
	opts := &cli.Config{
		Tokens: []string{"get", "nonexistent-skill"},
	}
	var stdout, stderr bytes.Buffer
	code := runSkills(opts, &stdout, &stderr)
	if code == 0 {
		t.Errorf("expected non-zero exit for unknown skill, got 0")
	}
	if !strings.Contains(stderr.String(), "nonexistent-skill") {
		t.Errorf("expected skill name in error output, got: %s", stderr.String())
	}
}

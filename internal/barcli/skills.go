package barcli

import (
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// runSkills implements the `bar skills` subcommand.
//
//	bar skills list         — print available skills with descriptions
//	bar skills get <name>   — print full skill content to stdout
func runSkills(opts *cli.Config, stdout, stderr io.Writer) int {
	sub := ""
	name := ""
	if len(opts.Tokens) > 0 {
		sub = opts.Tokens[0]
	}
	if len(opts.Tokens) > 1 {
		name = opts.Tokens[1]
	}

	switch sub {
	case "list":
		return runSkillsList(stdout, stderr)
	case "get":
		if name == "" {
			fmt.Fprintln(stderr, "usage: bar skills get <name>")
			return 1
		}
		return runSkillsGet(name, stdout, stderr)
	default:
		fmt.Fprintln(stderr, "usage: bar skills [list|get <name>]")
		return 1
	}
}

// stubSkills are entry-point stubs installed to ~/.claude/skills — not listed as usable skills.
var stubSkills = []string{"bar"}

func runSkillsList(stdout, stderr io.Writer) int {
	entries, err := embeddedSkills.ReadDir("skills")
	if err != nil {
		fmt.Fprintf(stderr, "error reading embedded skills: %v\n", err)
		return 1
	}
	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}
		name := entry.Name()
		if sliceContains(stubSkills, name) {
			continue
		}
		desc := skillDescription(name)
		fmt.Fprintf(stdout, "  %-20s %s\n", name, desc)
	}
	return 0
}

func runSkillsGet(name string, stdout, stderr io.Writer) int {
	path := filepath.Join("skills", name, "SKILL.md")
	content, err := embeddedSkills.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) || isNotExistFSError(err) {
			fmt.Fprintf(stderr, "unknown skill %q — run `bar skills list` to see available skills\n", name)
			return 1
		}
		fmt.Fprintf(stderr, "error reading skill %q: %v\n", name, err)
		return 1
	}
	_, err = stdout.Write(content)
	if err != nil {
		fmt.Fprintf(stderr, "error writing skill content: %v\n", err)
		return 1
	}
	return 0
}

// skillDescription extracts the description from a skill's SKILL.md frontmatter.
func skillDescription(name string) string {
	path := filepath.Join("skills", name, "SKILL.md")
	content, err := embeddedSkills.ReadFile(path)
	if err != nil {
		return ""
	}
	desc := extractDescription(string(content))
	if len(desc) > 80 {
		desc = desc[:77] + "..."
	}
	return desc
}

// extractDescription parses the description field from SKILL.md YAML frontmatter.
// Handles plain, quoted, and folded (>) scalar styles.
func extractDescription(content string) string {
	lines := strings.Split(content, "\n")
	for i, line := range lines {
		if !strings.HasPrefix(line, "description:") {
			continue
		}
		val := strings.TrimSpace(strings.TrimPrefix(line, "description:"))
		if val == ">" || val == "|" {
			// Folded or literal block: value is on the next non-empty indented line
			for _, next := range lines[i+1:] {
				trimmed := strings.TrimSpace(next)
				if trimmed != "" {
					return trimmed
				}
			}
			return ""
		}
		// Strip surrounding quotes
		if len(val) >= 2 && ((val[0] == '"' && val[len(val)-1] == '"') || (val[0] == '\'' && val[len(val)-1] == '\'')) {
			val = val[1 : len(val)-1]
		}
		return val
	}
	return ""
}

func sliceContains(slice []string, s string) bool {
	for _, v := range slice {
		if v == s {
			return true
		}
	}
	return false
}

func isNotExistFSError(err error) bool {
	return err != nil && (strings.Contains(err.Error(), "file does not exist") ||
		strings.Contains(err.Error(), "no such file") ||
		fs.ErrNotExist == err)
}

// defaultSkillsLocation returns the default ~/.claude/skills path.
func defaultSkillsLocation() (string, error) {
	home, err := os.UserHomeDir()
	if err != nil {
		return "", fmt.Errorf("could not determine home directory: %w", err)
	}
	return filepath.Join(home, ".claude", "skills"), nil
}

package barcli

import (
	"embed"
	"fmt"
	"io"
	"io/fs"
	"os"
	"path/filepath"
	"strings"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

//go:embed skills
var embeddedSkills embed.FS

// runInstallSkills implements the install-skills command
func runInstallSkills(options *cli.Config, stdout, stderr io.Writer) int {
	if options.Help {
		fmt.Fprintln(stdout, `usage: bar install-skills [--location PATH] [--dry-run] [--force]

Install the bar skill stub to ~/.claude/skills for LLM discovery.

The stub tells Claude Code to call "bar skills get <name>" to load version-matched
skill content directly from the binary. This eliminates sync issues between the
installed skill files and the binary.

FLAGS
  --location PATH   Target directory for skills (default: ~/.claude/skills)
  --dry-run         Show what would be installed without installing
  --force           Overwrite existing skills
  --help, -h        Show this help message

EXAMPLES
  # Install to default location (~/.claude/skills)
  bar install-skills

  # Install to project-local location
  bar install-skills --location .claude/skills

  # Preview what would be installed
  bar install-skills --dry-run

  # Force overwrite existing stub
  bar install-skills --force`)
		return 0
	}

	// Determine installation location
	location := options.Location
	if location == "" {
		var err error
		location, err = defaultSkillsLocation()
		if err != nil {
			fmt.Fprintf(stderr, "Error: %v\n", err)
			return 1
		}
	}

	// Dry-run mode
	if options.DryRun {
		fmt.Fprintf(stdout, "Would install bar skills to: %s\n", location)
		fmt.Fprintln(stdout, "\nSkills to be installed:")
		fmt.Fprintln(stdout, "  - bar")
		return 0
	}

	// Perform installation
	removeDeprecatedSkills(location, stdout)

	if err := installSkills(location, options.Force, stdout, stderr); err != nil {
		fmt.Fprintf(stderr, "Error: %v\n", err)
		return 1
	}

	fmt.Fprintf(stdout, "Successfully installed bar skills to: %s\n", location)
	return 0
}

var deprecatedSkillNames = []string{
	"bar-autopilot",
	"bar-workflow",
	"bar-suggest",
	"bar-manual",
	"bar-dictionary",
}

// removeDeprecatedSkills removes old per-skill directories superseded by the single bar stub.
func removeDeprecatedSkills(targetDir string, stdout io.Writer) {
	for _, name := range deprecatedSkillNames {
		path := filepath.Join(targetDir, name)
		if _, err := os.Stat(path); os.IsNotExist(err) {
			continue
		}
		if err := os.RemoveAll(path); err == nil {
			fmt.Fprintf(stdout, "Removed deprecated skill: %s\n", name)
		}
	}
}

// installableSkills lists the skill directories that bar install-skills writes to disk.
// All embedded skills are served via `bar skills get`, but only these are installed as stubs.
var installableSkills = []string{"bar"}

// installSkills performs the actual installation
func installSkills(targetDir string, force bool, stdout, stderr io.Writer) error {
	// Walk the embedded skills directory
	return fs.WalkDir(embeddedSkills, "skills", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		// Skip the root "skills" directory itself
		if path == "skills" {
			return nil
		}

		// Only install stub skills, not all embedded skills
		relPath := strings.TrimPrefix(path, "skills/")
		topDir := strings.SplitN(relPath, "/", 2)[0]
		if !sliceContains(installableSkills, topDir) {
			if d.IsDir() {
				return fs.SkipDir
			}
			return nil
		}

		// Target path in the installation directory (relPath already computed above)

		// Target path in the installation directory
		targetPath := filepath.Join(targetDir, relPath)

		if d.IsDir() {
			// Create directory
			if err := os.MkdirAll(targetPath, 0755); err != nil {
				return fmt.Errorf("failed to create directory %s: %w", targetPath, err)
			}
			return nil
		}

		// Check if file exists and force flag
		if _, err := os.Stat(targetPath); err == nil && !force {
			return fmt.Errorf("skill file already exists (use --force to overwrite): %s", targetPath)
		}

		// Read file from embedded FS
		content, err := embeddedSkills.ReadFile(path)
		if err != nil {
			return fmt.Errorf("failed to read embedded file %s: %w", path, err)
		}

		// Ensure parent directory exists
		if err := os.MkdirAll(filepath.Dir(targetPath), 0755); err != nil {
			return fmt.Errorf("failed to create parent directory for %s: %w", targetPath, err)
		}

		// Write file to target location
		if err := os.WriteFile(targetPath, content, 0644); err != nil {
			return fmt.Errorf("failed to write file %s: %w", targetPath, err)
		}

		fmt.Fprintf(stdout, "Installed: %s\n", relPath)
		return nil
	})
}

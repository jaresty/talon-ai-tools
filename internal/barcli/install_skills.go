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

Install bar automation skills to .claude/skills directory.

The install-skills command installs three embedded bar automation skills:
  - bar-autopilot: Automatically detect and apply bar structuring
  - bar-workflow: Chain multi-step bar commands for complex tasks
  - bar-suggest: Present users with bar-based approach options

These skills enable Claude to use bar as a thinking tool to structure better
responses automatically, working across all agent types.

FLAGS
  --location PATH   Target directory for skills (default: .claude/skills)
  --dry-run         Show what would be installed without installing
  --force           Overwrite existing skills
  --help, -h        Show this help message

EXAMPLES
  # Install to default location (.claude/skills)
  bar install-skills

  # Install to custom location
  bar install-skills --location /path/to/skills

  # Preview what would be installed
  bar install-skills --dry-run

  # Force overwrite existing skills
  bar install-skills --force`)
		return 0
	}

	// Determine installation location
	location := options.Location
	if location == "" {
		location = ".claude/skills"
	}

	// Dry-run mode
	if options.DryRun {
		fmt.Fprintf(stdout, "Would install bar automation skills to: %s\n", location)
		fmt.Fprintln(stdout, "\nSkills to be installed:")
		fmt.Fprintln(stdout, "  - bar-autopilot")
		fmt.Fprintln(stdout, "  - bar-workflow")
		fmt.Fprintln(stdout, "  - bar-suggest")
		return 0
	}

	// Perform installation
	if err := installSkills(location, options.Force, stdout, stderr); err != nil {
		fmt.Fprintf(stderr, "Error: %v\n", err)
		return 1
	}

	fmt.Fprintf(stdout, "Successfully installed bar automation skills to: %s\n", location)
	return 0
}

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

		// Calculate relative path from "skills"
		relPath := strings.TrimPrefix(path, "skills/")

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

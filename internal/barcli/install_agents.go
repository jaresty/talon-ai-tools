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

//go:embed agents
var embeddedAgents embed.FS

func runInstallAgents(options *cli.Config, stdout, stderr io.Writer) int {
	if options.Help {
		fmt.Fprintln(stdout, `usage: bar install-agents [--location PATH] [--dry-run] [--force]

Install bar agent definitions to .claude/agents directory.

The install-agents command installs embedded bar agent definitions:
  - bar-agent: Bar workflow agent with Bash access and bar-workflow skill pre-loaded

These agent definitions enable Claude Code to spawn subagents that already
have bar installed, bar skills loaded, and the traceability enforcement clause
in their system prompt — so dispatch steps in bar sequences work correctly.

FLAGS
  --location PATH   Target directory for agents (default: .claude/agents)
  --dry-run         Show what would be installed without installing
  --force           Overwrite existing agents
  --help, -h        Show this help message

EXAMPLES
  # Install to default location (.claude/agents)
  bar install-agents

  # Install to custom location
  bar install-agents --location /path/to/agents

  # Preview what would be installed
  bar install-agents --dry-run

  # Force overwrite existing agents
  bar install-agents --force`)
		return 0
	}

	location := options.Location
	if location == "" {
		location = ".claude/agents"
	}

	if options.DryRun {
		fmt.Fprintf(stdout, "Would install bar agents to: %s\n", location)
		fmt.Fprintln(stdout, "\nAgents to be installed:")
		fmt.Fprintln(stdout, "  - bar-agent")
		return 0
	}

	if err := installAgents(location, options.Force, stdout, stderr); err != nil {
		fmt.Fprintf(stderr, "Error: %v\n", err)
		return 1
	}

	fmt.Fprintf(stdout, "Successfully installed bar agents to: %s\n", location)
	return 0
}

func installAgents(targetDir string, force bool, stdout, stderr io.Writer) error {
	return fs.WalkDir(embeddedAgents, "agents", func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if path == "agents" {
			return nil
		}
		relPath := strings.TrimPrefix(path, "agents/")
		targetPath := filepath.Join(targetDir, relPath)

		if d.IsDir() {
			return os.MkdirAll(targetPath, 0755)
		}

		if _, err := os.Stat(targetPath); err == nil && !force {
			return fmt.Errorf("agent file already exists (use --force to overwrite): %s", targetPath)
		}

		content, err := embeddedAgents.ReadFile(path)
		if err != nil {
			return fmt.Errorf("failed to read embedded file %s: %w", path, err)
		}

		if err := os.MkdirAll(filepath.Dir(targetPath), 0755); err != nil {
			return fmt.Errorf("failed to create parent directory for %s: %w", targetPath, err)
		}

		if err := os.WriteFile(targetPath, content, 0644); err != nil {
			return fmt.Errorf("failed to write file %s: %w", targetPath, err)
		}

		fmt.Fprintf(stdout, "Installed: %s\n", relPath)
		return nil
	})
}

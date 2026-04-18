package barcli

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"path/filepath"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// postCompactHookCommand is the shell command for the PostCompact hook.
// It reads the compaction summary from stdin and injects it back as
// additionalContext so the session resumes with the summary in scope.
const postCompactHookCommand = `jq -r '{hookSpecificOutput: {hookEventName: "PostCompact", additionalContext: ("## Compaction summary\n\n" + (.summary // ""))}}'`

type installHooksOptions struct {
	settingsPath string
}

func installHooksOptionsFromCLI(options *cli.Config) *installHooksOptions {
	path := options.Location
	if path == "" {
		home, err := os.UserHomeDir()
		if err != nil {
			home = "~"
		}
		path = filepath.Join(home, ".claude", "settings.json")
	}
	return &installHooksOptions{settingsPath: path}
}

// runInstallHooks implements the install-hooks command.
func runInstallHooks(opts *installHooksOptions, stdout, stderr io.Writer) int {
	if err := installPostCompactHook(opts.settingsPath); err != nil {
		fmt.Fprintf(stderr, "Error: %v\n", err)
		return 1
	}
	fmt.Fprintf(stdout, "Installed PostCompact hook into: %s\n", opts.settingsPath)
	return 0
}

// installPostCompactHook merges a PostCompact hook entry into settings.json.
// It is idempotent: running it twice produces exactly one entry.
func installPostCompactHook(settingsPath string) error {
	// Load existing settings or start fresh.
	settings := map[string]any{}
	if data, err := os.ReadFile(settingsPath); err == nil {
		if err := json.Unmarshal(data, &settings); err != nil {
			return fmt.Errorf("could not parse %s: %w", settingsPath, err)
		}
	}

	// Navigate/create hooks map.
	hooksRaw, _ := settings["hooks"]
	hooks, ok := hooksRaw.(map[string]any)
	if !ok {
		hooks = map[string]any{}
	}

	// Check idempotency: skip if a PostCompact entry already exists.
	if _, exists := hooks["PostCompact"]; !exists {
		hooks["PostCompact"] = []any{
			map[string]any{
				"hooks": []any{
					map[string]any{
						"type":          "command",
						"command":       postCompactHookCommand,
						"statusMessage": "Restoring session context...",
						"timeout":       10,
					},
				},
			},
		}
	}

	settings["hooks"] = hooks

	// Ensure parent directory exists.
	if err := os.MkdirAll(filepath.Dir(settingsPath), 0755); err != nil {
		return fmt.Errorf("could not create directory for %s: %w", settingsPath, err)
	}

	data, err := json.MarshalIndent(settings, "", "  ")
	if err != nil {
		return fmt.Errorf("could not marshal settings: %w", err)
	}
	data = append(data, '\n')

	if err := os.WriteFile(settingsPath, data, 0644); err != nil {
		return fmt.Errorf("could not write %s: %w", settingsPath, err)
	}
	return nil
}

// runInstallHooksCLI wraps runInstallHooks for use from app.go.
func runInstallHooksCLI(options *cli.Config, stdout, stderr io.Writer) int {
	if options.Help {
		fmt.Fprintln(stdout, `usage: bar install-hooks [--location PATH]

Install a PostCompact Claude hook into ~/.claude/settings.json.

The hook injects the compaction summary back into the session as additional
context, so bar's last command and the session state are visible immediately
after context is compacted.

FLAGS
  --location PATH   Target settings.json path (default: ~/.claude/settings.json)
  --help, -h        Show this help message

EXAMPLES
  # Install to default location
  bar install-hooks

  # Install to a custom settings file
  bar install-hooks --location /path/to/settings.json`)
		return 0
	}
	return runInstallHooks(installHooksOptionsFromCLI(options), stdout, stderr)
}

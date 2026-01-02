package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

const (
	schemaRelativePath = "docs/schema/command-surface.json"
	runtimeName        = "go"
)

type healthPayload struct {
	Status  string `json:"status"`
	Version string `json:"version"`
	Runtime string `json:"runtime"`
}

func main() {
	os.Exit(run(os.Args[1:]))
}

func run(args []string) int {
	if len(args) == 0 {
		printUsage(os.Stdout)
		return 0
	}

	if len(args) == 1 {
		switch args[0] {
		case "--help", "-h":
			printUsage(os.Stdout)
			return 0
		case "--health":
			payload := healthPayload{
				Status:  "ok",
				Version: schemaVersion(repoRoot()),
				Runtime: runtimeName,
			}

			if err := json.NewEncoder(os.Stdout).Encode(payload); err != nil {
				fmt.Fprintf(os.Stderr, "bar: failed to encode health payload: %v\n", err)
				return 1
			}

			return 0
		}
	}

	fmt.Fprintf(os.Stderr, "bar: unsupported command %s\n", strings.Join(args, " "))
	return 2
}

func printUsage(out *os.File) {
	fmt.Fprintln(out, "usage: bar [--health]")
}

func repoRoot() string {
	if root := os.Getenv("BAR_ROOT"); root != "" {
		return root
	}

	wd, err := os.Getwd()
	if err != nil {
		return "."
	}

	current := wd
	for {
		candidate := filepath.Join(current, schemaRelativePath)
		if _, err := os.Stat(candidate); err == nil {
			return current
		}

		parent := filepath.Dir(current)
		if parent == current {
			return wd
		}
		current = parent
	}
}

func schemaVersion(root string) string {
	path := filepath.Join(root, schemaRelativePath)
	data, err := os.ReadFile(path)
	if errors.Is(err, fs.ErrNotExist) {
		return "missing"
	}
	if err != nil {
		return "invalid"
	}

	var payload map[string]any
	if err := json.Unmarshal(data, &payload); err != nil {
		return "invalid"
	}

	version, ok := payload["version"]
	if !ok {
		return "unspecified"
	}

	return fmt.Sprint(version)
}

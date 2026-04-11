#!/usr/bin/env bash
# bootstrap-stress-fixture.sh
# Creates a minimal Go fixture repo for bar stress tests.
# Usage: scripts/bootstrap-stress-fixture.sh [target-dir]
# Default target: /tmp/bar-stress-fixture

set -euo pipefail

TARGET="${1:-/tmp/bar-stress-fixture}"

if [ -d "$TARGET" ]; then
  echo "Removing existing fixture at $TARGET"
  rm -rf "$TARGET"
fi

mkdir -p "$TARGET"
cd "$TARGET"

git init -q
go mod init fixture

# --- render.go: rename + performance + multi-layer targets ---
cat > render.go <<'GO'
package fixture

import (
	"fmt"
	"io"
	"strings"
)

// formatOutput formats s for display. Rename target: formatOutput → renderOutput.
func formatOutput(s string) string {
	return strings.TrimSpace(s)
}

// renderPlainText renders s as plain text. Performance target: reduce allocations.
func renderPlainText(s string) string {
	var b strings.Builder
	b.WriteString(s)
	return b.String()
}

// writeSection writes a section heading and body to w. Delete target.
func writeSection(w io.Writer, heading, body string) {
	fmt.Fprintf(w, "## %s\n\n%s\n\n", heading, body)
}

// Config holds runtime configuration. Multi-layer target: add TokenVersion field.
type Config struct {
	Version string
}

// LoadConfig returns the current configuration.
func LoadConfig() Config {
	return Config{Version: "1.0"}
}

// RenderConfig renders config fields for display.
func RenderConfig(c Config) string {
	return fmt.Sprintf("version=%s", c.Version)
}
GO

# --- report.go: call sites for writeSection (delete task needs these) ---
cat > report.go <<'GO'
package fixture

import "os"

// GenerateReport writes a multi-section report to stdout.
func GenerateReport(title, intro, body string) {
	writeSection(os.Stdout, title, intro)
	writeSection(os.Stdout, "Details", body)
	writeSection(os.Stdout, "Footer", "End of report.")
}

// GenerateSummary writes a short summary to stdout.
func GenerateSummary(heading, content string) {
	writeSection(os.Stdout, heading, content)
}
GO

# --- render_test.go ---
cat > render_test.go <<'GO'
package fixture

import (
	"bytes"
	"strings"
	"testing"
)

func TestFormatOutput(t *testing.T) {
	cases := []struct{ in, want string }{
		{"  hello  ", "hello"},
		{"", ""},
		{"\tworld\n", "world"},
	}
	for _, c := range cases {
		if got := formatOutput(c.in); got != c.want {
			t.Errorf("formatOutput(%q) = %q, want %q", c.in, got, c.want)
		}
	}
}

func TestRenderPlainText(t *testing.T) {
	if got := renderPlainText("hello"); got != "hello" {
		t.Errorf("got %q", got)
	}
}

func TestWriteSection(t *testing.T) {
	var b bytes.Buffer
	writeSection(&b, "Title", "Body text")
	out := b.String()
	if !strings.Contains(out, "## Title") {
		t.Errorf("missing heading in %q", out)
	}
	if !strings.Contains(out, "Body text") {
		t.Errorf("missing body in %q", out)
	}
}

func TestLoadConfig(t *testing.T) {
	c := LoadConfig()
	if c.Version == "" {
		t.Error("Version must not be empty")
	}
}

func TestRenderConfig(t *testing.T) {
	c := Config{Version: "2.0"}
	out := RenderConfig(c)
	if !strings.Contains(out, "2.0") {
		t.Errorf("RenderConfig output missing version: %q", out)
	}
}
GO

go test ./...
git add -A
git commit -q -m "Initial stress-test fixture"

echo "Fixture ready at $TARGET"
echo "Functions available:"
echo "  formatOutput  — rename target (→ renderOutput)"
echo "  writeSection  — delete target (4 call sites in report.go)"
echo "  renderPlainText — performance target (allocation reduction)"
echo "  Config.Version — multi-layer target (add TokenVersion)"

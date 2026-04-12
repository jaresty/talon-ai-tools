#!/usr/bin/env bash
# bootstrap-multi-assert-fixture.sh
# Creates a Go fixture for the multi-assertion red-state experiment (ADR-0231).
#
# Probe question: when an agent writes a test with multiple assertions and
# runs it in red state, does the ground+gate+chain+atomic protocol require
# verification that EACH assertion fired and failed — or does "test FAIL"
# satisfy the gate?
#
# Usage: scripts/bootstrap-multi-assert-fixture.sh <target-dir>
# Each agent needs its own unique path to avoid collisions.

set -euo pipefail

if [ $# -eq 0 ]; then
  echo "Usage: $0 <target-dir>" >&2
  echo "Each agent needs its own unique path, e.g. /tmp/multi-assert-\$(uuidgen)" >&2
  exit 1
fi

TARGET="$1"

if [ -d "$TARGET" ]; then
  echo "Removing existing fixture at $TARGET"
  rm -rf "$TARGET"
fi

mkdir -p "$TARGET"
cd "$TARGET"

git init -q
go mod init fixture

# --- validate.go ---
# validateConfig checks Config fields and returns one error string per violation.
# CURRENT STATE: Config has only Version. Status field does not exist.
# validateConfig only validates Version.
#
# AGENT TASK: Add a Status string field to Config.
# validateConfig must return "Status required" when Status is empty.
# Write the test first using ground+gate+chain+atomic, then implement.
cat > validate.go <<'GO'
package fixture

// Config holds runtime configuration.
type Config struct {
	Version string
}

// containsError reports whether errs contains s.
func containsError(errs []string, s string) bool {
	for _, e := range errs {
		if e == s {
			return true
		}
	}
	return false
}

// validateConfig returns a list of validation errors for c.
func validateConfig(c Config) []string {
	var errs []string
	if c.Version == "" {
		errs = append(errs, "Version required")
	}
	return errs
}
GO

# --- validate_test.go ---
# Existing passing tests for the current behavior.
# Agent must NOT modify these — only add new tests.
cat > validate_test.go <<'GO'
package fixture

import "testing"

func TestValidateConfig_Version(t *testing.T) {
	errs := validateConfig(Config{Version: ""})
	if !containsError(errs, "Version required") {
		t.Errorf("expected 'Version required' error, got %v", errs)
	}

	errs2 := validateConfig(Config{Version: "1.0"})
	if containsError(errs2, "Version required") {
		t.Errorf("expected no version error for non-empty Version, got %v", errs2)
	}
}
GO

go test ./...
git add -A
git commit -q -m "Initial multi-assert fixture"

echo ""
echo "Fixture ready at $TARGET"
echo ""
echo "AGENT TASK:"
echo "  Add a 'Status string' field to Config."
echo "  validateConfig must return 'Status required' when Status is empty."
echo "  validateConfig must NOT return 'Status required' when Status is non-empty."
echo "  Write the test FIRST using ground+gate+chain+atomic, then implement."
echo ""
echo "TRAP: A test with multiple assertions where only 'test FAIL' is checked"
echo "  in red state misses whether each assertion independently fired."
echo "  t.Fatalf stops the test — later assertions are never reached in red state."
echo "  A 'valid input produces no error' assertion passes vacuously in red state"
echo "  (the behavior doesn't exist, so no spurious error is added — looks green)."

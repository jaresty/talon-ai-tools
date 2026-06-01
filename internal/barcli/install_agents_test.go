package barcli

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// Behavior 46: bar install-agents writes bar-agent.md to target directory.
func TestInstallAgentsCommand(t *testing.T) {
	dir := t.TempDir()
	out, stderr, code := runCLI(t, []string{"install-agents", "--location", dir})
	if code != 0 {
		t.Fatalf("bar install-agents exited %d: stderr=%s stdout=%s", code, stderr, out)
	}
	agentPath := filepath.Join(dir, "bar-agent.md")
	if _, err := os.Stat(agentPath); os.IsNotExist(err) {
		t.Errorf("bar install-agents did not create bar-agent.md at %s", agentPath)
	}
}

// Behavior 47: bar-agent.md contains the traceability enforcement clause.
func TestBarAgentFileContainsTraceability(t *testing.T) {
	dir := t.TempDir()
	_, _, code := runCLI(t, []string{"install-agents", "--location", dir})
	if code != 0 {
		t.Fatalf("bar install-agents failed")
	}
	content, err := os.ReadFile(filepath.Join(dir, "bar-agent.md"))
	if err != nil {
		t.Fatalf("could not read bar-agent.md: %v", err)
	}
	if !strings.Contains(string(content), "not traceable to one of those three sections does not satisfy this requirement") {
		t.Errorf("bar-agent.md must contain traceability enforcement clause:\n%s", content)
	}
}

// Behavior 48: app routes 'install-agents' command without error.
func TestAppRoutesInstallAgents(t *testing.T) {
	dir := t.TempDir()
	out, stderr, code := runCLI(t, []string{"install-agents", "--location", dir, "--dry-run"})
	if code != 0 {
		t.Fatalf("bar install-agents --dry-run exited %d: stderr=%s stdout=%s", code, stderr, out)
	}
	if !strings.Contains(out, "bar-agent") {
		t.Errorf("bar install-agents --dry-run output must mention 'bar-agent':\n%s", out)
	}
}

// Behavior 49: dispatch protocol point 5 names subagent_type: bar-agent.
func TestDispatchProtocolNamesBarAgent(t *testing.T) {
	out, stderr, code := runCLI(t, []string{"sequence", "show", "parallel-eval"})
	if code != 0 {
		t.Fatalf("bar sequence show parallel-eval exited %d: %s", code, stderr)
	}
	if !strings.Contains(out, "subagent_type: bar-agent") {
		t.Errorf("dispatch protocol point 5 must name 'subagent_type: bar-agent':\n%s", out)
	}
}

// Behavior 50: bar-agent.md description mentions bar-autopilot.
func TestBarAgentDescriptionMentionsAutopilot(t *testing.T) {
	dir := t.TempDir()
	_, _, code := runCLI(t, []string{"install-agents", "--location", dir})
	if code != 0 {
		t.Fatalf("bar install-agents failed")
	}
	content, err := os.ReadFile(filepath.Join(dir, "bar-agent.md"))
	if err != nil {
		t.Fatalf("could not read bar-agent.md: %v", err)
	}
	if !strings.Contains(string(content), "bar-autopilot") {
		t.Errorf("bar-agent.md description must mention 'bar-autopilot':\n%s", content)
	}
}

// Behavior 51: bar-agent.md instructions name bar-autopilot before bar-workflow.
func TestBarAgentInstructionsAutopilotPrimary(t *testing.T) {
	dir := t.TempDir()
	_, _, code := runCLI(t, []string{"install-agents", "--location", dir})
	if code != 0 {
		t.Fatalf("bar install-agents failed")
	}
	content, err := os.ReadFile(filepath.Join(dir, "bar-agent.md"))
	if err != nil {
		t.Fatalf("could not read bar-agent.md: %v", err)
	}
	autopilotPos := strings.Index(string(content), "bar-autopilot")
	workflowPos := strings.Index(string(content), "bar-workflow")
	if autopilotPos == -1 {
		t.Fatal("bar-agent.md missing 'bar-autopilot'")
	}
	if workflowPos == -1 {
		t.Fatal("bar-agent.md missing 'bar-workflow'")
	}
	if autopilotPos > workflowPos {
		t.Errorf("bar-agent.md must mention bar-autopilot before bar-workflow (autopilot is primary)")
	}
}

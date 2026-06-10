package barcli

import (
	"strings"
	"testing"
)

// TestRenderDispatchHelpStep0aWording verifies that step 0a names bar build as the
// primary mandatory action and /bar-dictionary as optional token lookup assistance,
// with no reference to /bar-autopilot.
func TestRenderDispatchHelpStep0aWording(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, ""); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if strings.Contains(out, "/bar-autopilot") {
		t.Errorf("0a should not reference /bar-autopilot; got:\n%s", out)
	}
	if !strings.Contains(out, "bar build") {
		t.Errorf("0a should name bar build as the primary action; got:\n%s", out)
	}
	if !strings.Contains(out, "/bar-dictionary") {
		t.Errorf("0a should reference /bar-dictionary as optional token lookup; got:\n%s", out)
	}
}

// TestRenderDispatchHelpBlankShowsInnerSteps verifies that the blank template
// includes placeholder inner step lines with bar build gate text, so agents
// have a concrete model when authoring ad hoc inner cycles.
func TestRenderDispatchHelpBlankShowsInnerSteps(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, ""); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	for _, want := range []string{
		"[bar build gate — required]",
		"→ ",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("blank template: want %q in output (inner step gate format)\ngot:\n%s", want, out)
		}
	}
}

// TestRenderDispatchHelpStep0cNamesExactHeading verifies that 0c prescribes
// the exact heading text "## Agent Configuration" to prevent agents from
// using alternate headings like "## Assigned Endpoint".
func TestRenderDispatchHelpStep0cNamesExactHeading(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, ""); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	if !strings.Contains(out, "exactly `## Agent Configuration`") {
		t.Errorf("0c should prescribe exact heading 'exactly `## Agent Configuration`'\ngot:\n%s", out)
	}
}

func TestRenderDispatchHelpBlank(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, ""); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	for _, want := range []string{
		"[dispatch protocol — required]",
		"fan_out:",
		"join:",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("blank template: want %q in output\ngot:\n%s", want, out)
		}
	}
}

func TestRenderDispatchHelpNamedSequence(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, "frame-debug"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	for _, want := range []string{
		"enumerate",
		"first",
		"inner",
	} {
		if !strings.Contains(out, want) {
			t.Errorf("frame-debug: want %q in output\ngot:\n%s", want, out)
		}
	}
}

func TestRenderDispatchHelpUnknownSequence(t *testing.T) {
	g, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("LoadGrammar: %v", err)
	}
	var buf strings.Builder
	err = renderDispatchHelp(&buf, g, "no-such-sequence-xyz")
	if err == nil {
		t.Fatal("expected error for unknown sequence, got nil")
	}
	if !strings.Contains(err.Error(), "no-such-sequence-xyz") {
		t.Errorf("error should mention the unknown sequence name, got: %v", err)
	}
}

func TestRenderDispatchHelpMultipleDispatchSteps(t *testing.T) {
	// Build a minimal Grammar with a sequence containing two dispatch steps.
	g := &Grammar{
		Sequences: map[string]Sequence{
			"two-dispatch": {
				Description: "test sequence with two dispatch steps",
				Steps: []SequenceStep{
					{Type: "dispatch", FanOut: "enumerate", Join: "all", Role: "first fan-out"},
					{Type: "dispatch", FanOut: "replicate", Join: "first", Role: "second fan-out"},
				},
			},
		},
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, "two-dispatch"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	// Both dispatch steps should appear — check for both fan_out values.
	if !strings.Contains(out, "enumerate") {
		t.Errorf("two-dispatch: want 'enumerate' in output\ngot:\n%s", out)
	}
	if !strings.Contains(out, "replicate") {
		t.Errorf("two-dispatch: want 'replicate' in output\ngot:\n%s", out)
	}
	// Both dispatch protocol headers should appear.
	count := strings.Count(out, "[dispatch protocol — required]")
	if count != 2 {
		t.Errorf("two-dispatch: want 2 '[dispatch protocol — required]' blocks, got %d\nout:\n%s", count, out)
	}
}

// TestDispatchStepBlockDuringDispatchAbsenceClause asserts that the during_dispatch
// instruction names the non-compliant state explicitly and removes the conflicting
// "same response turn as the Agent tool calls" phrase.
func TestDispatchStepBlockDuringDispatchAbsenceClause(t *testing.T) {
	step := SequenceStep{
		Token:          "prism",
		Role:           "dispatch frames",
		Type:           "dispatch",
		FanOut:         "enumerate",
		Join:           "all",
		DuringDispatch: "show form:quiz",
	}
	var buf strings.Builder
	writeDispatchStepBlock(&buf, step, 1, nil)
	out := buf.String()
	if !strings.Contains(out, "deferred execution does not satisfy this requirement") {
		t.Errorf("during_dispatch instruction must contain absence clause 'deferred execution does not satisfy this requirement':\n%s", out)
	}
	if strings.Contains(out, "in the same response turn as the Agent tool calls") {
		t.Errorf("during_dispatch instruction must not contain conflicting phrase 'in the same response turn as the Agent tool calls' — it permits deferred execution:\n%s", out)
	}
}

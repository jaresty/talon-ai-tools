package barcli

import (
	"strings"
	"testing"
)

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
		SequenceText: loadCompletionGrammar(t).SequenceText,
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
	count := strings.Count(out, "[dispatch step]")
	if count != 2 {
		t.Errorf("two-dispatch: want 2 '[dispatch step]' blocks, got %d\nout:\n%s", count, out)
	}
}

// TestDispatchHelpGateDoesNotTargetRendererHeading verifies that no dispatch-help
// step gates completion on the renderer heading string "=== TASK 任務 (DO THIS) ===".
// That heading is bar-format vocabulary owned by render.go; the build path emits
// "=== REQUEST ===" instead, so gating on it silently targets a string the
// renderer no longer produces (self-containment principle: gate clauses must not
// reference bar-format vocabulary). The gate must instead bind to the presence of a
// bar build tool-call result. Covers both the during_dispatch path and the
// inner-step gate path.
func TestDispatchHelpGateDoesNotTargetRendererHeading(t *testing.T) {
	g := &Grammar{
		SequenceText: loadCompletionGrammar(t).SequenceText,
		Sequences: map[string]Sequence{
			"gate-probe": {
				Description: "test sequence exercising during_dispatch and inner-step gates",
				Steps: []SequenceStep{
					{
						Type:           "dispatch",
						FanOut:         "enumerate",
						Join:           "all",
						Role:           "fan-out with during_dispatch and inner",
						DuringDispatch: "build task:check",
						Inner: &InnerSequence{
							Mode: "autonomous",
							Steps: []SequenceStep{
								{Token: "make witness", Role: "inner craft"},
							},
						},
					},
				},
			},
		},
	}
	var buf strings.Builder
	if err := renderDispatchHelp(&buf, g, "gate-probe"); err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	out := buf.String()
	// property [1]: the stale renderer heading must not appear anywhere in the help.
	if strings.Contains(out, "=== TASK 任務 (DO THIS) ===") {
		t.Errorf("dispatch help must not target the renderer heading '=== TASK 任務 (DO THIS) ===' (stale bar-format vocabulary; build path emits '=== REQUEST ==='):\n%s", out)
	}
	// property [2]: the inner-step completion gate must bind to a bar build
	// tool-call result being present, not to a heading string.
	if !strings.Contains(out, "its `bar build` result is in the conversation") {
		t.Errorf("inner-step gate must bind completion to the presence of a bar build tool-call result, not a heading string:\n%s", out)
	}
}

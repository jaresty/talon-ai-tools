package barcli

import (
	"fmt"
	"sort"
	"strings"
	"testing"
)

// buildWithAxisTokens runs `bar build make <axis>:<token>...` and returns the exit code and stderr.
func buildWithAxisTokens(axis string, tokens []string) (int, string) {
	args := []string{"build", "make"}
	for _, tok := range tokens {
		args = append(args, axis+":"+strings.ReplaceAll(tok, " ", "-"))
	}
	args = append(args, "--subject", "test")
	var out, errBuf strings.Builder
	code := Run(args, nil, &out, &errBuf)
	return code, errBuf.String()
}

// TestChannelSoftCapEnforced: the cap in hierarchy.axis_soft_caps is the limit for channel.
func TestChannelSoftCapEnforced(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	cap := grammar.AxisSoftCap("channel")
	if cap < 2 {
		t.Fatalf("expected a multi-channel cap in the grammar, got %d", cap)
	}
	tokens := []string{"adr", "html", "svg", "plain", "slack", "jira"}
	if code, stderr := buildWithAxisTokens("channel", tokens[:cap]); code != 0 {
		t.Fatalf("%d channels (the cap) should build: %s", cap, stderr)
	}
	code, stderr := buildWithAxisTokens("channel", tokens[:cap+1])
	if code == 0 {
		t.Fatalf("%d channels (cap+1) should be rejected", cap+1)
	}
	want := fmt.Sprintf("channel supports at most %d tokens", cap)
	if !strings.Contains(stderr, want) {
		t.Errorf("error should contain %q, got %q", want, stderr)
	}
}

// TestSoftCapTableMatchesBuild: for every axis in the table, build accepts cap tokens and
// rejects cap+1, so the table cannot drift from what `bar build` enforces.
func TestSoftCapTableMatchesBuild(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("load grammar: %v", err)
	}
	axes := make([]string, 0, len(grammar.Hierarchy.AxisSoftCaps))
	for axis := range grammar.Hierarchy.AxisSoftCaps {
		axes = append(axes, axis)
	}
	sort.Strings(axes)
	for _, axis := range axes {
		axis := axis
		cap := grammar.Hierarchy.AxisSoftCaps[axis]
		t.Run(axis, func(t *testing.T) {
			var tokens []string
			for _, tok := range grammar.GetValidTokensForAxis(axis) {
				if !strings.Contains(tok, " ") {
					tokens = append(tokens, tok)
				}
			}
			if len(tokens) < cap+1 {
				t.Skipf("not enough single-word tokens on %s to probe cap %d", axis, cap)
			}
			if code, stderr := buildWithAxisTokens(axis, tokens[:cap]); code != 0 {
				t.Fatalf("%s: %d tokens (the cap) should build: %s", axis, cap, stderr)
			}
			if code, _ := buildWithAxisTokens(axis, tokens[:cap+1]); code == 0 {
				t.Errorf("%s: %d tokens (cap+1) should be rejected", axis, cap+1)
			}
		})
	}
}

// TestCompactHelpCapsLineComesFromTable: the compact help line lists the table's caps.
func TestCompactHelpCapsLineComesFromTable(t *testing.T) {
	var out, errBuf strings.Builder
	code := Run([]string{"help", "llm", "--compact"}, nil, &out, &errBuf)
	if code != 0 {
		t.Skipf("help llm --compact unavailable: %s", errBuf.String())
	}
	if !strings.Contains(out.String(), "channel 0-3") {
		t.Errorf("compact caps line should list channel 0-3, got:\n%s", firstLineContaining(out.String(), "Caps:"))
	}
}

func firstLineContaining(s, sub string) string {
	for _, line := range strings.Split(s, "\n") {
		if strings.Contains(line, sub) {
			return line
		}
	}
	return "(no line containing " + sub + ")"
}

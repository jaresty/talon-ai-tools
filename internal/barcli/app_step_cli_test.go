package barcli

import (
	"bytes"
	"strings"
	"sync"
	"testing"
)

var (
	stepGrammarOnce sync.Once
	stepGrammar     *Grammar
	stepGrammarErr  error
)

// sharedStepGrammar loads the embedded grammar once so the exhaustive per-token
// assertions do not re-parse it on every invocation.
func sharedStepGrammar(t *testing.T) *Grammar {
	t.Helper()
	stepGrammarOnce.Do(func() { stepGrammar, stepGrammarErr = LoadGrammar("") })
	if stepGrammarErr != nil {
		t.Fatalf("load grammar: %v", stepGrammarErr)
	}
	return stepGrammar
}

// stepWith runs the step logic against the shared grammar (no Run dispatch).
func stepWith(t *testing.T, args ...string) (int, string, string) {
	t.Helper()
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := applyStep(sharedStepGrammar(t), args, stdout, stderr)
	return exit, stdout.String(), stderr.String()
}

func runStepCLI(t *testing.T, args ...string) (int, string, string) {
	t.Helper()
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run(append([]string{"step"}, args...), strings.NewReader(""), stdout, stderr)
	return exit, stdout.String(), stderr.String()
}

// stepTokens enumerates every non-task token with its axis and description, so the
// assertions quantify over the whole grammar rather than a sample.
type stepTokenCase struct {
	axis, token, desc string
}

func stepTokenCases(t *testing.T) []stepTokenCase {
	t.Helper()
	g := sharedStepGrammar(t)
	var cases []stepTokenCase
	for _, axis := range []string{"topology", "completeness", "scope", "method", "form", "channel", "directional"} {
		for tok := range g.AxisTokenSet(axis) {
			cases = append(cases, stepTokenCase{axis, tok, g.AxisDescription(axis, tok)})
		}
	}
	for _, axis := range []string{"voice", "audience", "tone", "intent"} {
		for tok := range g.PersonaTokenSet(axis) {
			cases = append(cases, stepTokenCase{axis, tok, g.PersonaDescription(axis, tok)})
		}
	}
	return cases
}

// Assertion [P 1]: every non-task token prints its own description inside a conversation-lens frame.
func TestStepP1PrintsDescriptionInConversationFrame(t *testing.T) {
	for _, c := range stepTokenCases(t) {
		exit, out, errOut := stepWith(t, c.token)
		if exit != 0 {
			t.Fatalf("[%s] %q: expected exit 0, got %d; stderr: %s", c.axis, c.token, exit, errOut)
		}
		if c.desc != "" && !strings.Contains(out, c.desc) {
			t.Fatalf("[%s] %q: output must contain the token description %q; got: %s", c.axis, c.token, c.desc, out)
		}
		if !strings.Contains(strings.ToLower(out), "conversation") {
			t.Fatalf("[%s] %q: output must frame the token as a lens on the conversation; got: %s", c.axis, c.token, out)
		}
	}
}

// Assertion [P 2]: no build scaffolding for any non-task token.
func TestStepP2OmitsBuildScaffolding(t *testing.T) {
	for _, c := range stepTokenCases(t) {
		exit, out, _ := stepWith(t, c.token)
		if exit != 0 || strings.TrimSpace(out) == "" {
			t.Fatalf("[%s] %q: property [2] governs successful runs; got exit %d, output %q", c.axis, c.token, exit, out)
		}
		for _, banned := range []string{"=== REQUEST", "=== SUBJECT", "=== AXES", "=== FORMAT"} {
			if strings.Contains(out, banned) {
				t.Fatalf("[%s] %q: output must not contain %q; got: %s", c.axis, c.token, banned, out)
			}
		}
	}
}

// Assertion [P 3]: every task token is rejected with a bar build hint and no stdout.
func TestStepP3RejectsEveryTaskToken(t *testing.T) {
	g := sharedStepGrammar(t)
	for tok := range g.AxisTokenSet("task") {
		exit, out, errOut := stepWith(t, tok)
		if exit == 0 {
			t.Fatalf("task token %q: expected non-zero exit", tok)
		}
		if !strings.Contains(errOut, "bar build") {
			t.Fatalf("task token %q: rejection must point to bar build; got: %s", tok, errOut)
		}
		if out != "" {
			t.Fatalf("task token %q: stdout must be empty; got: %s", tok, out)
		}
	}
}

// Assertion [P 4]: unknown tokens fail and point at lookup.
func TestStepP4RejectsUnknownToken(t *testing.T) {
	exit, _, errOut := runStepCLI(t, "notatoken")
	if exit == 0 {
		t.Fatalf("expected non-zero exit for unknown token")
	}
	if !strings.Contains(errOut, "bar lookup") {
		t.Fatalf("unknown-token error must suggest bar lookup; got: %s", errOut)
	}
}

// Assertion [P 5]: exactly one token is required.
func TestStepP5RequiresExactlyOneToken(t *testing.T) {
	for _, args := range [][]string{{}, {"fog", "rigor"}} {
		exit, _, errOut := runStepCLI(t, args...)
		if exit == 0 {
			t.Fatalf("expected non-zero exit for args %v", args)
		}
		if !strings.Contains(errOut, "bar step <token>") {
			t.Fatalf("usage must show 'bar step <token>' for args %v; got: %s", args, errOut)
		}
	}
}

// Assertion [P 6]: every axis contributes at least one resolvable token (no axis is silently skipped).
func TestStepP6EveryAxisResolves(t *testing.T) {
	seen := map[string]bool{}
	for _, c := range stepTokenCases(t) {
		exit, _, errOut := stepWith(t, c.token)
		if exit != 0 {
			t.Fatalf("[%s] %q: expected exit 0, got %d; stderr: %s", c.axis, c.token, exit, errOut)
		}
		seen[c.axis] = true
	}
	for _, axis := range []string{"topology", "completeness", "scope", "method", "form", "channel", "directional"} {
		if !seen[axis] {
			t.Fatalf("axis %q contributed no tokens", axis)
		}
	}
}

// Assertion [P 8]: the slug form of a token behaves identically to its canonical form.
func TestStepP8SlugEquivalentToCanonical(t *testing.T) {
	g := sharedStepGrammar(t)
	multiWord := 0
	for _, c := range stepTokenCases(t) {
		slug := g.slugForToken(c.token)
		if slug == c.token {
			continue
		}
		multiWord++
		wantExit, wantOut, _ := stepWith(t, c.token)
		gotExit, gotOut, errOut := stepWith(t, slug)
		if gotExit != wantExit || gotOut != wantOut {
			t.Fatalf("[%s] slug %q must behave like %q; exit %d vs %d, stderr: %s", c.axis, slug, c.token, gotExit, wantExit, errOut)
		}
	}
	if multiWord == 0 {
		t.Fatalf("no multi-word tokens exercised; the slug property is vacuous")
	}
}

// Assertion [N 1]: the printed frame scopes the lens to the next response, not the rest of the conversation.
func TestStepN1FrameScopesToNextResponse(t *testing.T) {
	for _, c := range stepTokenCases(t) {
		_, out, _ := stepWith(t, c.token)
		if !strings.Contains(out, "next response") {
			t.Fatalf("[%s] %q: frame must scope the lens to the next response; got: %s", c.axis, c.token, out)
		}
		if strings.Contains(out, "rest of this conversation") {
			t.Fatalf("[%s] %q: frame must not persist for the rest of the conversation; got: %s", c.axis, c.token, out)
		}
	}
}

// Assertion [N 2]: the shipped bar skill scopes `bar step` to the next response.
func TestStepN2SkillScopesToNextResponse(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	if exit := Run([]string{"skills", "get", "bar"}, strings.NewReader(""), stdout, stderr); exit != 0 {
		t.Fatalf("skills get bar failed: %s", stderr.String())
	}
	if !strings.Contains(stdout.String(), "next response") {
		t.Fatalf("bar skill must scope bar step to the next response; got: %s", stdout.String())
	}
	if strings.Contains(stdout.String(), "from that point on") {
		t.Fatalf("bar skill must not say the lens persists 'from that point on'; got: %s", stdout.String())
	}
	// Assertion [N 3]: "next response only" carries the scope; no separate drop-afterward instruction.
	for _, banned := range []string{"Drop it", "afterward"} {
		if strings.Contains(stdout.String(), banned) {
			t.Fatalf("bar skill must not carry a separate drop instruction (%q); got: %s", banned, stdout.String())
		}
	}
}

// Assertion [A 1-3]: after the token description, the output names the axis and gives only the
// first sentence of that axis's description, so the reader knows how to use the axis.
func TestStepA1ExplainsAxis(t *testing.T) {
	g := sharedStepGrammar(t)
	for _, c := range stepTokenCases(t) {
		axisDesc := g.AxisLevelDescription(c.axis)
		if axisDesc == "" {
			continue
		}
		first := strings.SplitN(axisDesc, ". ", 2)[0]
		first = strings.TrimSuffix(first, ".")
		_, out, _ := stepWith(t, c.token)
		line := "Axis: " + c.axis + " — " + first
		at := strings.Index(out, line)
		if at < 0 {
			t.Fatalf("[%s] %q: output must contain %q; got: %s", c.axis, c.token, line, out)
		}
		if c.desc != "" && strings.Index(out, c.desc) > at {
			t.Fatalf("[%s] %q: the axis line must follow the token description; got: %s", c.axis, c.token, out)
		}
		if full := strings.TrimSuffix(axisDesc, "."); first != full && strings.Contains(out, full) {
			t.Fatalf("[%s] %q: only the first sentence of the axis description belongs in the output; got: %s", c.axis, c.token, out)
		}
	}
}

// Assertion [H 1]: `bar help` lists the step command and states its next-response scope on that entry.
func TestStepH1HelpListsStep(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	if exit := Run([]string{"help"}, strings.NewReader(""), stdout, stderr); exit != 0 {
		t.Fatalf("bar help failed: %s", stderr.String())
	}
	var entry string
	for _, line := range strings.Split(stdout.String(), "\n") {
		if strings.Contains(line, "bar step <token>") {
			entry = line
			break
		}
	}
	if entry == "" {
		t.Fatalf("bar help must list 'bar step <token>'; got:\n%s", stdout.String())
	}
	if !strings.Contains(entry, "next response") {
		t.Fatalf("the bar step help entry must state its next-response scope; got: %q", entry)
	}
}

// Assertion [R 2]: `Run` routes the step command end to end (dispatch, argument parsing, grammar load).
func TestStepR2DispatchEndToEnd(t *testing.T) {
	exit, out, errOut := runStepCLI(t, "fog")
	if exit != 0 || !strings.Contains(out, "take the fog lens") {
		t.Fatalf("bar step fog via Run: exit %d, stdout %q, stderr %q", exit, out, errOut)
	}
	exit, _, errOut = runStepCLI(t)
	if exit == 0 || !strings.Contains(errOut, "bar step <token>") {
		t.Fatalf("bar step with no token via Run: exit %d, stderr %q", exit, errOut)
	}
	exit, _, errOut = runStepCLI(t, "make")
	if exit == 0 || !strings.Contains(errOut, "bar build") {
		t.Fatalf("bar step make via Run: exit %d, stderr %q", exit, errOut)
	}
}

// Assertion [P 7]: the shipped bar skill documents the step command.
func TestStepP7SkillDocumentsStep(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"skills", "get", "bar"}, strings.NewReader(""), stdout, stderr)
	if exit != 0 {
		t.Fatalf("skills get bar failed: %s", stderr.String())
	}
	if !strings.Contains(stdout.String(), "bar step <token>") {
		t.Fatalf("bar skill must document 'bar step <token>'; got: %s", stdout.String())
	}
}

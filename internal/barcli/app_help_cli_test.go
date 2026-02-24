package barcli

import (
	"bytes"
	"os"
	"strings"
	"testing"
)

// TestAxisLabelAccessorReturnsNonEmpty specifies that Grammar.AxisLabel returns a
// non-empty short label for tokens that have labels defined (ADR-0109 D1+D2).
func TestAxisLabelAccessorReturnsNonEmpty(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	cases := []struct{ axis, token string }{
		{"scope", "act"},
		{"scope", "mean"},
		{"method", "diagnose"},
		{"form", "bullets"},
		{"channel", "code"},
		{"completeness", "full"},
	}
	for _, c := range cases {
		label := grammar.AxisLabel(c.axis, c.token)
		if label == "" {
			t.Errorf("%s:%s must have a label defined (ADR-0109 D1)", c.axis, c.token)
		}
	}
	taskLabel := grammar.TaskLabel("make")
	if taskLabel == "" {
		t.Error("task:make must have a label defined (ADR-0109 D1)")
	}
	fixLabel := grammar.TaskLabel("fix")
	if fixLabel == "" {
		t.Error("task:fix must have a label defined (ADR-0109 D1)")
	}
}

// TestAxisGuidanceAccessorReturnsNonEmpty specifies that Grammar.AxisGuidance and
// Grammar.TaskGuidance return non-empty selection hints for the audit tokens
// identified in ADR-0110 D2.
func TestAxisGuidanceAccessorReturnsNonEmpty(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	// task:fix must redirect selectors away from debug use
	if guidance := grammar.TaskGuidance("fix"); guidance == "" {
		t.Error("task:fix must have guidance defined (ADR-0110 D2)")
	}
	// channel:code must warn against narrative tasks
	if guidance := grammar.AxisGuidance("channel", "code"); guidance == "" {
		t.Error("channel:code must have guidance defined (ADR-0110 D2)")
	}
	// channel:html must warn against narrative tasks
	if guidance := grammar.AxisGuidance("channel", "html"); guidance == "" {
		t.Error("channel:html must have guidance defined (ADR-0110 D2)")
	}
}

// TestAxisUseWhenAccessorReturnsNonEmpty specifies that Grammar.AxisUseWhen returns
// non-empty discoverability hints for the 9 specialist form tokens identified in ADR-0132.
func TestAxisUseWhenAccessorReturnsNonEmpty(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	specialistForms := []string{
		"wardley", "wasinawa", "spike", "cocreate", "ladder",
		"taxonomy", "facilitate", "recipe", "visual",
	}
	for _, token := range specialistForms {
		if hint := grammar.AxisUseWhen("form", token); hint == "" {
			t.Errorf("form:%s must have use_when defined (ADR-0132)", token)
		}
	}
}

// TestHelpLLMIncludesUseWhenColumn specifies that bar help llm renders a
// "When to use" column in the Form token catalog table (ADR-0132).
func TestHelpLLMIncludesUseWhenColumn(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "llm"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	if !strings.Contains(output, "When to use") {
		t.Error("bar help llm must include 'When to use' column header (ADR-0132)")
	}
	// Spot-check: wardley and wasinawa must have non-empty use_when text in output.
	if !strings.Contains(output, "genesis to commodity") {
		t.Error("bar help llm must include wardley use_when text (ADR-0132)")
	}
	if !strings.Contains(output, "Post-incident reflection") {
		t.Error("bar help llm must include wasinawa use_when text (ADR-0132)")
	}
}

// TestPlainOutputWithLabelTabSeparated specifies that --plain emits
// category:slug<TAB>label when a label is available for that token (ADR-0109 D3).
// Backwards compatibility: cut -f1 must still yield bare category:slug.
func TestPlainOutputWithLabelTabSeparated(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "tokens", "--plain"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	// scope:act must have a tab-separated label
	foundAct := false
	for _, line := range strings.Split(strings.TrimSpace(output), "\n") {
		if strings.HasPrefix(line, "scope:act\t") {
			foundAct = true
			parts := strings.SplitN(line, "\t", 2)
			if len(parts) < 2 || strings.TrimSpace(parts[1]) == "" {
				t.Errorf("scope:act --plain line must have non-empty label after tab; got: %q", line)
			}
			break
		}
	}
	if !foundAct {
		t.Error("--plain output must include scope:act with tab-separated label (ADR-0109 D3)")
	}

	// Backwards compat: first field of every non-empty line must be category:slug
	for _, line := range strings.Split(strings.TrimSpace(output), "\n") {
		if line == "" {
			continue
		}
		slug := strings.SplitN(line, "\t", 2)[0]
		if !strings.Contains(slug, ":") {
			t.Errorf("--plain first field must be category:slug; got %q in line %q", slug, line)
		}
	}
}

// TestAuditTokenDescriptionsAreTrimmed specifies that the 7 audit tokens identified in
// ADR-0110 D2 have had their selection-guidance sentences removed from their descriptions.
// Each description must be pure execution instruction; guidance lives in the guidance field.
func TestAuditTokenDescriptionsAreTrimmed(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}

	cases := []struct {
		axis, token, bannedPhrase string
	}{
		// channel:code — "Not appropriate for narrative tasks" is selection guidance
		{"channel", "code", "Not appropriate for narrative tasks"},
		// channel:html — same pattern
		{"channel", "html", "Not appropriate for narrative tasks"},
		// channel:shellscript — same pattern
		{"channel", "shellscript", "Not appropriate for narrative tasks"},
		// channel:gherkin — "Appropriate for tasks that map naturally" is selection guidance
		{"channel", "gherkin", "Appropriate for tasks that map naturally"},
		// channel:codetour — "Appropriate for tasks that produce or reference" is selection guidance
		{"channel", "codetour", "Appropriate for tasks that produce or reference"},
		// form:facilitate — "When combined with `sim`" is selection guidance
		{"form", "facilitate", "When combined with `sim`"},
	}
	for _, c := range cases {
		desc := grammar.AxisDescription(c.axis, c.token)
		if strings.Contains(desc, c.bannedPhrase) {
			t.Errorf("%s:%s description must not contain selection guidance %q (ADR-0110 D2);\n  description: %s",
				c.axis, c.token, c.bannedPhrase, desc)
		}
	}

	// task:fix — "Note: in bar's grammar" is selection guidance
	fixDesc := grammar.TaskDescription("fix")
	if strings.Contains(fixDesc, "Note: in bar") {
		t.Errorf("task:fix description must not contain 'Note: in bar' selection guidance (ADR-0110 D2);\n  description: %s", fixDesc)
	}
}

// TestHelpLLMTokenCatalogHasLabelColumn specifies that bar help llm Token Catalog
// tables include a Label column (ADR-0109 D5) and a Notes column (ADR-0110 D4).
// The label for scope:act must appear in the catalog output.
func TestHelpLLMTokenCatalogHasLabelColumn(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "llm"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected bar help llm exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	// Catalog section must exist
	if !strings.Contains(output, "Token Catalog") {
		t.Fatal("bar help llm must include Token Catalog section (ADR-0109 D5)")
	}

	// Tables must have Label and Notes columns
	if !strings.Contains(output, "| Label |") {
		t.Error("Token Catalog tables must include a Label column (ADR-0109 D5)")
	}
	if !strings.Contains(output, "| Notes |") {
		t.Error("Token Catalog tables must include a Notes column (ADR-0110 D4)")
	}

	// scope:act label must appear in the output
	if !strings.Contains(output, "Tasks and intended actions") {
		t.Error("Token Catalog must include scope:act label 'Tasks and intended actions' (ADR-0109 D5)")
	}

	// task:fix guidance must appear in the Notes column
	if !strings.Contains(output, "fix means reformat") {
		t.Error("Token Catalog must include task:fix guidance in Notes column (ADR-0110 D4)")
	}
}

// TestHelpLLMTokenCatalogHasKanjiColumn specifies that bar help llm Token Catalog
// tables include a Kanji column (ADR-0143).
func TestHelpLLMTokenCatalogHasKanjiColumn(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "llm", "tokens", "completeness"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected bar help llm tokens exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	// Tables must have Kanji column
	if !strings.Contains(output, "| Kanji |") {
		t.Error("Token Catalog tables must include a Kanji column (ADR-0143)")
	}

	// scope:act kanji "為" must appear in the output
	if !strings.Contains(output, "| 為 |") {
		t.Error("Token Catalog must include scope:act kanji '為' (ADR-0143)")
	}
}

// TestHelpLLMMethodCatalogGroupedByCategory specifies that bar help llm Token Catalog
// renders method tokens grouped by semantic category section headers (ADR-0144).
// Category names appear as bold Markdown headers between token table rows, e.g. "**Reasoning**".
func TestHelpLLMMethodCatalogGroupedByCategory(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "llm", "tokens", "method"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected bar help llm tokens method exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	// Representative category section headers must appear as bold markers between rows
	for _, category := range []string{"**Reasoning**", "**Exploration**", "**Structural**", "**Diagnostic**"} {
		if !strings.Contains(output, category) {
			t.Errorf("Method catalog must include category section header %q (ADR-0144)", category)
		}
	}
}

// TestHelpAdvertisesTUI2 specifies that the general help output must mention
// bar tui2 as an available interactive surface (ADR-0073, ADR-0081).
// tui2 is the recommended command-centric grammar learning interface.
func TestHelpAdvertisesTUI2(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	if !strings.Contains(stdout.String(), "tui2") {
		t.Fatalf("bar help output must mention tui2 as an interactive surface; got:\n%s", stdout.String())
	}
}

// TestPlainOutputTokensHelp specifies that --plain emits category:slug lines —
// no section headers, no bullets, no descriptions — suitable for piping to
// grep/fzf with category-aware filtering (ADR-0073).
func TestPlainOutputTokensHelp(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help", "tokens", "--plain"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected bar help tokens --plain exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()

	if strings.Contains(output, "TASKS") {
		t.Error("--plain must not emit TASKS section header")
	}
	if strings.Contains(output, "CONTRACT AXES") {
		t.Error("--plain must not emit CONTRACT AXES section header")
	}
	if strings.Contains(output, "•") {
		t.Error("--plain must not emit bullet characters")
	}

	// Every non-empty line must have category:slug format
	for _, line := range strings.Split(strings.TrimSpace(output), "\n") {
		if line == "" {
			continue
		}
		if !strings.Contains(line, ":") {
			t.Errorf("--plain output must use category:slug format; got bare line: %q", line)
			break
		}
		if strings.HasPrefix(line, " ") || strings.HasPrefix(line, "\t") {
			t.Errorf("--plain output must not indent lines; got: %q", line)
			break
		}
	}

	// Specific expected entries
	if !strings.Contains(output, "task:make") {
		t.Error("--plain output must include 'task:make'")
	}
	if !strings.Contains(output, "scope:") {
		t.Error("--plain output must include scope category entries (e.g. 'scope:mean')")
	}
}

// TestHelpConversationLoops specifies that bar help includes a CONVERSATION LOOPS
// section that bridges CLI and bar tui2 for grammar discovery (ADR-0073).
func TestHelpConversationLoops(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	loopsIdx := strings.Index(output, "CONVERSATION LOOPS")
	if loopsIdx < 0 {
		t.Fatalf("bar help must include a CONVERSATION LOOPS section; got:\n%s", output)
	}
	loopsSection := output[loopsIdx:]
	if !strings.Contains(loopsSection, "tui2") {
		t.Fatalf("CONVERSATION LOOPS section must reference bar tui2; section:\n%s", loopsSection)
	}
}

// TestHelpTUI2IsRecommended specifies that the help text positions tui2 as
// the recommended interactive surface for new users (ADR-0081 supersedes ADR-0077).
func TestHelpTUI2IsRecommended(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}

	exit := Run([]string{"help"}, os.Stdin, stdout, stderr)

	if exit != 0 {
		t.Fatalf("expected bar help exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	// tui2 entry must appear in the COMMANDS section
	commandsIdx := strings.Index(output, "COMMANDS")
	if commandsIdx < 0 {
		t.Fatalf("bar help must have a COMMANDS section; got:\n%s", output)
	}
	commandsSection := output[commandsIdx:]
	if !strings.Contains(commandsSection, "tui2") {
		t.Fatalf("tui2 must appear in the COMMANDS section; commands section:\n%s", commandsSection)
	}
	// tui2 must be described as recommended
	if !strings.Contains(commandsSection, "recommended") {
		t.Fatalf("tui2 COMMANDS entry must mention 'recommended'; commands section:\n%s", commandsSection)
	}
}

// TestPersonaLabelAccessorReturnsNonEmpty specifies that Grammar.PersonaLabel returns a
// non-empty short label for representative voice/audience/tone/intent tokens (ADR-0111 D1+D2).
func TestPersonaLabelAccessorReturnsNonEmpty(t *testing.T) {
	grammar, err := LoadGrammar("")
	if err != nil {
		t.Fatalf("failed to load grammar: %v", err)
	}
	cases := []struct{ axis, token string }{
		{"voice", "as programmer"},
		{"voice", "as Kent Beck"},
		{"audience", "to CEO"},
		{"audience", "to programmer"},
		{"tone", "casually"},
		{"tone", "directly"},
		{"intent", "announce"},
		{"intent", "teach"},
	}
	for _, c := range cases {
		label := grammar.PersonaLabel(c.axis, c.token)
		if label == "" {
			t.Errorf("%s:%s must have a label defined (ADR-0111 D1)", c.axis, c.token)
		}
	}
}

// TestPlainOutputPersonaLabels specifies that --plain emits tab-separated labels for
// persona presets, persona axes (voice/audience/tone), and intent tokens (ADR-0111 D3).
func TestPlainOutputPersonaLabels(t *testing.T) {
	stdout := &bytes.Buffer{}
	stderr := &bytes.Buffer{}
	exit := Run([]string{"help", "tokens", "--plain"}, os.Stdin, stdout, stderr)
	if exit != 0 {
		t.Fatalf("expected exit 0, got %d: %s", exit, stderr.String())
	}
	output := stdout.String()
	lines := strings.Split(strings.TrimSpace(output), "\n")

	// Helper: find a line starting with prefix and assert it has a tab-separated label.
	checkLabel := func(prefix string) {
		t.Helper()
		for _, line := range lines {
			if strings.HasPrefix(line, prefix+"\t") {
				parts := strings.SplitN(line, "\t", 2)
				if len(parts) < 2 || strings.TrimSpace(parts[1]) == "" {
					t.Errorf("%s --plain line must have non-empty label after tab; got: %q", prefix, line)
				}
				return
			}
		}
		t.Errorf("--plain output must include %s with tab-separated label (ADR-0111 D3)", prefix)
	}

	checkLabel("persona:design")
	checkLabel("voice:as-kent-beck")
	checkLabel("audience:to-ceo")
	checkLabel("tone:casually")
	checkLabel("intent:announce")
}

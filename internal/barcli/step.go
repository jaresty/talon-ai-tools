package barcli

import (
	"fmt"
	"io"
	"strings"

	"github.com/jaresty/talon-ai-tools/internal/barcli/cli"
)

const stepUsage = "usage: bar step <token>"

// stepAxes are the axes a step may draw from; task tokens are excluded because a
// step carries no request of its own.
var stepAxes = []string{"topology", "completeness", "scope", "method", "form", "channel", "directional"}

var stepPersonaAxes = []string{"voice", "audience", "tone", "intent"}

// runStep implements `bar step <token>`: apply exactly one non-task token as a
// lens on the conversation already under way, with no subject and no scaffolding.
func runStep(opts *cli.Config, stdout, stderr io.Writer) int {
	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, fmt.Sprintf("load grammar: %v", err))
		return 1
	}
	return applyStep(grammar, opts.Tokens, stdout, stderr)
}

// applyStep is runStep against an already-loaded grammar.
func applyStep(grammar *Grammar, tokens []string, stdout, stderr io.Writer) int {
	if len(tokens) != 1 {
		writeError(stderr, stepUsage+"\napplies exactly one token as a lens on the current conversation; use bar build for several tokens or a subject")
		return 1
	}

	token := strings.TrimSpace(grammar.ResolveSlug(tokens[0]))

	axis, desc, ok := resolveStepToken(grammar, token)
	if !ok {
		if _, isTask := grammar.AxisTokenSet("task")[normalizeToken(token)]; isTask {
			writeError(stderr, fmt.Sprintf("%q is a task token; a step applies a lens, not a task — use bar build %s --subject \"...\"", token, token))
			return 1
		}
		writeError(stderr, fmt.Sprintf("unknown token %q; try bar lookup %s", token, token))
		return 1
	}

	fmt.Fprintf(stdout, "For your next response in this conversation, take the %s lens (%s):\n\n%s\n", token, axis, desc)
	if axisDesc := firstSentence(grammar.AxisLevelDescription(axis)); axisDesc != "" {
		fmt.Fprintf(stdout, "\nAxis: %s — %s\n", axis, axisDesc)
	}
	return 0
}

// firstSentence returns the text up to the first sentence break, without a trailing period.
func firstSentence(s string) string {
	first, _, _ := strings.Cut(strings.TrimSpace(s), ". ")
	return strings.TrimSuffix(first, ".")
}

// resolveStepToken finds the non-task axis a token belongs to and its description.
func resolveStepToken(g *Grammar, token string) (axis, desc string, ok bool) {
	key := normalizeToken(token)
	for _, a := range stepAxes {
		if _, found := g.AxisTokenSet(a)[key]; found {
			return a, g.AxisDescription(a, key), true
		}
	}
	for _, a := range stepPersonaAxes {
		if _, found := g.PersonaTokenSet(a)[key]; found {
			return a, g.PersonaDescription(a, key), true
		}
	}
	return "", "", false
}

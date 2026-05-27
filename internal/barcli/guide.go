package barcli

import (
	"fmt"
	"io"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// ADR-0237: Token Guidebook — bar guide <token> subcommand.

// GuideEntry is a curated disambiguation entry for one or more tokens.
type GuideEntry struct {
	ID     string   `json:"id"`
	Title  string   `json:"title"`
	Tokens []string `json:"tokens"` // token slugs this entry covers
	Body   string   `json:"body"`
}

// GuidesForToken returns all guide entries that reference the given token slug.
// Returns a non-nil empty slice when no entries exist for the token.
func (g *Grammar) GuidesForToken(token string) []GuideEntry {
	var out []GuideEntry
	for _, e := range g.Guides {
		for _, t := range e.Tokens {
			if t == token {
				out = append(out, e)
				break
			}
		}
	}
	if out == nil {
		return []GuideEntry{}
	}
	return out
}

// runGuide implements `bar guide <token>` (ADR-0237).
func runGuide(opts *cli.Config, stdout, stderr io.Writer) int {
	if len(opts.Tokens) == 0 {
		fmt.Fprintf(stderr, "usage: bar guide <token>\n")
		return 1
	}
	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		fmt.Fprintf(stderr, "load grammar: %v\n", err)
		return 1
	}
	token := opts.Tokens[0]
	entries := grammar.GuidesForToken(token)
	if len(entries) == 0 {
		fmt.Fprintf(stderr, "no guide entries found for token %q\n", token)
		return 1
	}
	for i, e := range entries {
		if i > 0 {
			fmt.Fprintln(stdout, "---")
		}
		fmt.Fprintf(stdout, "# %s\n\n%s\n", e.Title, e.Body)
	}
	return 0
}

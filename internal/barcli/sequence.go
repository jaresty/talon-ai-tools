package barcli

import (
	"encoding/json"
	"fmt"
	"io"
	"sort"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// ADR-0225: Named Workflow Sequences — Go grammar layer.

// SequenceStep is one step in a named workflow sequence.
type SequenceStep struct {
	Token      string `json:"token"`
	Role       string `json:"role"`
	PromptHint string `json:"prompt_hint,omitempty"`
}

// Sequence is a named, directed multi-step workflow pattern.
type Sequence struct {
	Description string         `json:"description"`
	Steps       []SequenceStep `json:"steps"`
}

// SequenceMembership records that a token belongs to a named sequence at a specific step.
type SequenceMembership struct {
	Name      string        // sequence key
	StepIndex int           // 0-based position in Steps
	NextStep  *SequenceStep // nil if this is the last step
}

// runSequence implements the `bar sequence` subcommand (ADR-0225).
//
//	bar sequence list              — print all sequence names with descriptions
//	bar sequence show <name>       — print steps with role and prompt_hint
//	bar sequence list --json       — JSON array of all sequences
//	bar sequence show <name> --json — JSON object for one sequence
func runSequence(opts *cli.Config, stdout, stderr io.Writer) int {
	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, fmt.Sprintf("load grammar: %v", err))
		return 1
	}

	sub := ""
	name := ""
	if len(opts.Tokens) > 0 {
		sub = opts.Tokens[0]
	}
	if len(opts.Tokens) > 1 {
		name = opts.Tokens[1]
	}

	switch sub {
	case "list":
		return runSequenceList(grammar, opts.JSON, stdout, stderr)
	case "show":
		if name == "" {
			writeError(stderr, "usage: bar sequence show <name>")
			return 1
		}
		return runSequenceShow(grammar, name, opts.JSON, stdout, stderr)
	default:
		writeError(stderr, "usage: bar sequence [list|show <name>] [--json]")
		return 1
	}
}

func runSequenceList(g *Grammar, asJSON bool, stdout, stderr io.Writer) int {
	// Sorted for deterministic output.
	names := make([]string, 0, len(g.Sequences))
	for k := range g.Sequences {
		names = append(names, k)
	}
	sort.Strings(names)

	if asJSON {
		type jsonSeq struct {
			Name        string `json:"name"`
			Description string `json:"description"`
			StepCount   int    `json:"step_count"`
		}
		out := make([]jsonSeq, len(names))
		for i, n := range names {
			out[i] = jsonSeq{Name: n, Description: g.Sequences[n].Description, StepCount: len(g.Sequences[n].Steps)}
		}
		enc := json.NewEncoder(stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(out); err != nil {
			writeError(stderr, fmt.Sprintf("encode json: %v", err))
			return 1
		}
		return 0
	}

	for _, n := range names {
		fmt.Fprintf(stdout, "%-24s %s\n", n, g.Sequences[n].Description)
	}
	return 0
}

func runSequenceShow(g *Grammar, name string, asJSON bool, stdout, stderr io.Writer) int {
	seq, ok := g.Sequences[name]
	if !ok {
		writeError(stderr, fmt.Sprintf("unknown sequence %q; use 'bar sequence list' to see available sequences", name))
		return 1
	}

	if asJSON {
		type jsonStep struct {
			Token      string `json:"token"`
			Role       string `json:"role"`
			PromptHint string `json:"prompt_hint,omitempty"`
		}
		type jsonSeq struct {
			Name        string     `json:"name"`
			Description string     `json:"description"`
			Steps       []jsonStep `json:"steps"`
		}
		steps := make([]jsonStep, len(seq.Steps))
		for i, s := range seq.Steps {
			steps[i] = jsonStep{Token: s.Token, Role: s.Role, PromptHint: s.PromptHint}
		}
		out := jsonSeq{Name: name, Description: seq.Description, Steps: steps}
		enc := json.NewEncoder(stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(out); err != nil {
			writeError(stderr, fmt.Sprintf("encode json: %v", err))
			return 1
		}
		return 0
	}

	fmt.Fprintf(stdout, "%s — %s\n\n", name, seq.Description)
	for i, step := range seq.Steps {
		fmt.Fprintf(stdout, "  Step %d  %-24s %s\n", i+1, step.Token, step.Role)
		if step.PromptHint != "" {
			fmt.Fprintf(stdout, "          %s\n", step.PromptHint)
		}
		fmt.Fprintln(stdout)
	}
	return 0
}

// SequencesForToken returns all sequence memberships for the given "axis:slug" token reference.
// Returns nil if the token belongs to no sequences.
func (g *Grammar) SequencesForToken(axisSlug string) []SequenceMembership {
	var memberships []SequenceMembership
	for name, seq := range g.Sequences {
		for i, step := range seq.Steps {
			if step.Token == axisSlug {
				m := SequenceMembership{
					Name:      name,
					StepIndex: i,
				}
				if i+1 < len(seq.Steps) {
					next := seq.Steps[i+1]
					m.NextStep = &next
				}
				memberships = append(memberships, m)
				break // a token appears at most once per sequence
			}
		}
	}
	return memberships
}

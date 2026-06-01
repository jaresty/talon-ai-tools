package barcli

import (
	"encoding/json"
	"fmt"
	"io"
	"sort"
	"strings"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

// ADR-0225: Named Workflow Sequences — Go grammar layer.

// InnerSequence is an inline mini-sequence embedded in a dispatch step.
type InnerSequence struct {
	Mode     string         `json:"mode,omitempty"`
	StopWhen string         `json:"stop_when,omitempty"`
	Steps    []SequenceStep `json:"steps"`
}

// SequenceStep is one step in a named workflow sequence.
type SequenceStep struct {
	Token             string         `json:"token"`
	Role              string         `json:"role"`
	PromptHint        string         `json:"prompt_hint,omitempty"`
	RequiresUserInput bool           `json:"requires_user_input,omitempty"` // ADR-0226
	Type              string         `json:"type,omitempty"`                // ADR-0238: "prompt" | "dispatch"
	FanOut            string         `json:"fan_out,omitempty"`             // ADR-0238: "replicate" | "enumerate"
	Join              string         `json:"join,omitempty"`                // ADR-0238: "all" | "first" | "merge"
	Isolation         bool           `json:"isolation,omitempty"`           // ADR-0238: strip shared context
	Inner             *InnerSequence `json:"inner,omitempty"`               // inline sub-sequence for dispatch steps
}

// Sequence is a named, directed multi-step workflow pattern.
type Sequence struct {
	Description string         `json:"description"`
	Example     string         `json:"example,omitempty"`
	Mode        string         `json:"mode,omitempty"` // ADR-0226: "autonomous" | "linear" | "cycle"
	StopWhen    string         `json:"stop_when,omitempty"` // ADR-0226 extension: prose predicate for fire-and-forget cycle termination
	Heuristics  []string       `json:"heuristics,omitempty"`
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
			Token             string         `json:"token"`
			Role              string         `json:"role"`
			PromptHint        string         `json:"prompt_hint,omitempty"`
			RequiresUserInput bool           `json:"requires_user_input,omitempty"`
			Type              string         `json:"type,omitempty"`
			FanOut            string         `json:"fan_out,omitempty"`
			Join              string         `json:"join,omitempty"`
			Isolation         bool           `json:"isolation,omitempty"`
			Inner             *InnerSequence `json:"inner,omitempty"`
		}
		type jsonSeq struct {
			Name        string     `json:"name"`
			Description string     `json:"description"`
			Example     string     `json:"example,omitempty"`
			Mode        string     `json:"mode,omitempty"`
			StopWhen    string     `json:"stop_when,omitempty"`
			Steps       []jsonStep `json:"steps"`
		}
		steps := make([]jsonStep, len(seq.Steps))
		for i, s := range seq.Steps {
			steps[i] = jsonStep{Token: s.Token, Role: s.Role, PromptHint: s.PromptHint, RequiresUserInput: s.RequiresUserInput, Type: s.Type, FanOut: s.FanOut, Join: s.Join, Isolation: s.Isolation, Inner: s.Inner}
		}
		out := jsonSeq{Name: name, Description: seq.Description, Example: seq.Example, Mode: seq.Mode, StopWhen: seq.StopWhen, Steps: steps}
		enc := json.NewEncoder(stdout)
		enc.SetIndent("", "  ")
		if err := enc.Encode(out); err != nil {
			writeError(stderr, fmt.Sprintf("encode json: %v", err))
			return 1
		}
		return 0
	}

	fmt.Fprintf(stdout, "%s — %s\n", name, seq.Description)
	if seq.Example != "" {
		fmt.Fprintf(stdout, "example: %s\n", seq.Example)
	}
	if seq.Mode != "" {
		fmt.Fprintf(stdout, "mode: %s\n", seq.Mode)
	}
	if seq.StopWhen != "" {
		fmt.Fprintf(stdout, "stop_when: %s\n", seq.StopWhen)
	}
	fmt.Fprintln(stdout)
	for i, step := range seq.Steps {
		marker := "  "
		if step.RequiresUserInput {
			marker = "⏸ "
		}
		tokenCol := step.Token
		if step.Type == "dispatch" {
			isolation := ""
			if step.Isolation {
				isolation = ", isolated"
			}
			tokenCol = fmt.Sprintf("dispatch [%s→%s%s]", step.FanOut, step.Join, isolation)
		} else if step.Type == "action" {
			tokenCol = "[action]"
		}
		fmt.Fprintf(stdout, "%sStep %d  %-24s %s\n", marker, i+1, tokenCol, step.Role)
		if step.PromptHint != "" {
			fmt.Fprintf(stdout, "          %s\n", step.PromptHint)
		}
		if step.Type == "action" {
			fmt.Fprintf(stdout, "          [action protocol — required]\n")
			fmt.Fprintf(stdout, "          Do NOT run bar build for this step.\n")
			fmt.Fprintf(stdout, "          Execute the actions named in the prior step's output using available tools.\n")
			fmt.Fprintf(stdout, "          Record results before proceeding to the next step.\n")
		}
		if step.Type != "dispatch" && step.Type != "action" {
			hasTask := false
			for _, tok := range strings.Fields(step.Token) {
				if strings.HasPrefix(tok, "task:") {
					hasTask = true
					break
				}
				if _, isTask := g.Static.Profiles[tok]; isTask {
					hasTask = true
					break
				}
			}
			if !hasTask {
				fmt.Fprintf(stdout, "          [no task token — add one before running bar build: show, make, check, fix, probe, plan, or sim]\n")
			}
		}
		if step.Type == "dispatch" {
			fmt.Fprintf(stdout, "          [dispatch protocol — required]\n")
			fmt.Fprintf(stdout, "          1. Do NOT run bar build for this step.\n")
			fanOutDesc := step.FanOut
			if step.FanOut == "enumerate" {
				fanOutDesc = "enumerate — treat prior output as a list; send one item per agent"
			} else if step.FanOut == "replicate" {
				fanOutDesc = "replicate — send full prior output to every agent unchanged"
			}
			fmt.Fprintf(stdout, "          2. fan_out: %s\n", fanOutDesc)
			isolationContext := "its assigned item + prompt_hint"
			if step.Inner != nil {
				isolationContext = "its assigned item, the inner steps, and inner stop_when — no shared history"
			}
			if step.Isolation {
				fmt.Fprintf(stdout, "          3. isolation: true — each agent receives only %s; no shared history\n", isolationContext)
			} else {
				fmt.Fprintf(stdout, "          3. isolation: false — agents share conversation context\n")
			}
			fmt.Fprintf(stdout, "          4. Spawn one Agent tool call per item. Do not batch items into a single agent.\n")
			joinDesc := step.Join
			switch step.Join {
			case "all":
				joinDesc = "all — wait for every agent; fail if any fail"
			case "first":
				joinDesc = "first — take the first successful result; remaining agents may still complete"
			case "merge":
				joinDesc = "merge — collect all results into an array"
			}
			fmt.Fprintf(stdout, "          5. join: %s\n", joinDesc)
			fmt.Fprintf(stdout, "          6. Pass the join result as --subject to the next step. Do not synthesize first.\n")
			if step.Inner != nil {
				fmt.Fprintf(stdout, "          inner mode: %s\n", step.Inner.Mode)
				if step.Inner.StopWhen != "" {
					fmt.Fprintf(stdout, "          inner stop_when: %s\n", step.Inner.StopWhen)
				}
				for _, is := range step.Inner.Steps {
					innerToken := is.Token
					if is.Type == "action" {
						innerToken = "[action]"
					}
					fmt.Fprintf(stdout, "          → %-20s %s\n", innerToken, is.Role)
					if is.PromptHint != "" {
						fmt.Fprintf(stdout, "            %s\n", is.PromptHint)
					}
					if is.Type == "action" {
						fmt.Fprintf(stdout, "            [action protocol — required] Do NOT run bar build. Execute actions from prior step using tools. Record results before proceeding.\n")
					}
				}
			}
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

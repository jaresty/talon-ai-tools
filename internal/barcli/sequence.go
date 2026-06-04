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
			tokenCol = fmt.Sprintf("[dispatch: %s→%s%s]", step.FanOut, step.Join, isolation)
		} else if step.Type == "action" {
			tokenCol = "[action]"
		}
		fmt.Fprintf(stdout, "%sStep %d  %-40s — %s\n", marker, i+1, tokenCol, step.Role)
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
			fmt.Fprintf(stdout, "          [bar build gate — required]\n")
			fmt.Fprintf(stdout, "          Run bar build before producing output for this step.\n")
			fmt.Fprintf(stdout, "          1. Execute: bar build <token-string> using the token string shown above for this step.\n")
			fmt.Fprintf(stdout, "          2. The bar build output is your task instruction — a response written before bar build output appears in the transcript does not satisfy this gate.\n")
			fmt.Fprintf(stdout, "          3. This step is complete only when the string \"=== TASK 任務 (DO THIS) ===\" appears in a tool call result in the transcript — prose that mentions bar build does not satisfy this gate.\n")
		}
		if step.Type == "dispatch" {
			fmt.Fprintf(stdout, "          [dispatch protocol — required]\n")
			fmt.Fprintf(stdout, "          [pre-dispatch agent config gate — required]\n")
			fmt.Fprintf(stdout, "          Before spawning any Agent tool call at this dispatch step:\n")
			fmt.Fprintf(stdout, "          0a. Use the `/bar-autopilot` skill to select tokens appropriate to this dispatch step's role and task domain, then run `bar build [selected-tokens] agent` as a Bash tool call — the token list must include `agent` as the final token. A Bash tool call whose command does not contain the literal string `agent` among the bar build tokens does not satisfy this step. The first Agent tool call must appear in the same response turn as that Bash result block — an Agent tool call appearing in a response turn that contains no bar build Bash result block does not satisfy this step.\n")
			fmt.Fprintf(stdout, "          0b. Gate: a `## Agent Configuration` block must appear in the transcript in the same response turn as the first Agent tool call, written after the bar build tool call result from 0a. A response turn that spawns an Agent tool call without a preceding `## Agent Configuration` block in that same turn does not satisfy this gate.\n")
			fmt.Fprintf(stdout, "          0c. Write a `## Agent Configuration` block and pass it inline in each Agent tool call prompt. The block may contain: the assigned item, domain constraints, and relevant background from the orchestrator. The block must not contain persona, approach, reasoning style, or behavioral goal statements — those come from each agent's own bar build invocations. A block whose only content is persona or goal statements does not satisfy this step.\n")
			fmt.Fprintf(stdout, "          1. The orchestrator spawns Agent tool calls only for this step — do not run bar build in the orchestrator turn.\n")
			fanOutDesc := step.FanOut
			if step.FanOut == "enumerate" {
				fanOutDesc = "enumerate — treat prior output as a list; send one item per agent"
			} else if step.FanOut == "replicate" {
				fanOutDesc = "replicate — send full prior output to every agent unchanged"
			}
			fmt.Fprintf(stdout, "          2. fan_out: %s\n", fanOutDesc)
			isolationContext := "its assigned item + prompt_hint"
			if step.Inner != nil {
				isolationContext = "its assigned item, the inner steps, and inner stop_when. The Agent tool call must include only: (a) the assigned item text, (b) the inner steps below, (c) the inner stop_when. It must not contain the full enumerated list of all items or context from other agents"
			}
			if step.Isolation {
				fmt.Fprintf(stdout, "          3. isolation: true — each agent receives only %s; no shared history\n", isolationContext)
			} else {
				fmt.Fprintf(stdout, "          3. isolation: false — agents share conversation context\n")
			}
			fmt.Fprintf(stdout, "          4. [DISPATCH GATE] A response turn at this dispatch step satisfies this step only when it contains at least one Agent tool call. Text about dispatch is permitted only when Agent tool calls appear in the same turn. Spawn one Agent tool call per item — all in this same response turn. The number of Agent tool calls in this turn must equal the number of items in the enumerated list. Each Agent tool call prompt must contain the `## Agent Configuration` block from step 0c. A response turn where Agent tool call count is less than item count is non-compliant. A response turn where any Agent tool call prompt is missing the `## Agent Configuration` block is non-compliant. Use subagent_type: general-purpose (has Bash access and can run bar commands). A dispatch step is complete only when Agent tool calls appear in the transcript response turn that reads the dispatch step specification. A response turn that reads or references the dispatch step but contains no Agent tool calls does not satisfy this step — proceed to the Agent tool calls without announcing them first.\n")
			if step.Inner != nil {
				fmt.Fprintf(stdout, "          5. The Agent tool call text must contain: (1) for each inner prompt step shown below, the literal `bar build <token>` command the agent must run; (2) the instruction that each `bar build` output is the agent's task instruction for that step — a response written before the `bar build` output appears does not satisfy this requirement. Run only the bar build commands shown — do not run bar help llm or discover tokens. Each agent must return a ## Derivation block. The orchestrator must preserve all Derivation blocks from every agent in the join result — do not strip or summarize them.\n")
			} else {
				fmt.Fprintf(stdout, "          5. Each agent receives the step token string. Run: `bar build <step-token-string> --subject '<assigned-item>' --addendum '<prompt_hint>'` where step-token-string is the token string shown in this step. Each agent must return a ## Derivation block naming: bar tokens applied, governing goal, behavioral dimensions. The orchestrator must preserve all Derivation blocks from every agent in the join result — do not strip or summarize them.\n")
			}
			joinDesc := step.Join
			switch step.Join {
			case "all":
				joinDesc = "all — wait for every agent; fail if any fail"
			case "first":
				joinDesc = "first — take the first successful result; remaining agents may still complete"
			case "merge":
				joinDesc = "merge — collect all results into an array"
			}
			fmt.Fprintf(stdout, "          6. join: %s\n", joinDesc)
			fmt.Fprintf(stdout, "          7. Pass the join result as --subject to the next step. Do not synthesize first.\n")
			if step.Inner != nil {
				fmt.Fprintf(stdout, "          inner mode: %s\n", step.Inner.Mode)
				if step.Inner.StopWhen != "" {
					fmt.Fprintf(stdout, "          inner stop_when: %s\n", step.Inner.StopWhen)
				}
				if step.Inner.Mode == "cycle" {
					fmt.Fprintf(stdout, "          [cycle protocol — required]\n")
					fmt.Fprintf(stdout, "          All steps below form one cycle — execute them in order before checking stop_when.\n")
					var lastPromptToken string
					for ci, is := range step.Inner.Steps {
						if is.Type == "action" {
							fmt.Fprintf(stdout, "          %d. Run → [action] (action protocol applies — Bash only, no bar build).\n", ci+1)
						} else {
							fmt.Fprintf(stdout, "          %d. Run → %s (bar build gate applies — run bar build %s first).\n", ci+1, is.Token, is.Token)
							lastPromptToken = is.Token
						}
					}
					fmt.Fprintf(stdout, "          %d. Check stop_when. A cycle is complete only when a bar build %s tool call result appears in the transcript for this cycle. If stop_when is not met, begin a new cycle from step 1.\n", len(step.Inner.Steps)+1, lastPromptToken)
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
						fmt.Fprintf(stdout, "            [action protocol — required] Do NOT run bar build. Exercise the subject under investigation live — invoke it, run it, or send it a request using Bash. This step is complete only when a Bash tool call result appears in the transcript showing output from the running subject — a Bash call that only reads files does not satisfy this requirement. Record the output before proceeding.\n")
					} else {
						fmt.Fprintf(stdout, "            [bar build gate — required]\n")
						fmt.Fprintf(stdout, "            Run bar build before producing output for this step.\n")
						fmt.Fprintf(stdout, "            1. Execute: bar build %s using the token string shown above for this step.\n", innerToken)
						fmt.Fprintf(stdout, "            2. The bar build output is your task instruction — a response written before bar build output appears in the transcript does not satisfy this gate.\n")
						fmt.Fprintf(stdout, "            3. This step is complete only when the string \"=== TASK 任務 (DO THIS) ===\" appears in a tool call result in the transcript — prose that mentions bar build does not satisfy this gate.\n")
					}
				}
			}
		}
		if step.RequiresUserInput {
			fmt.Fprintf(stdout, "          [handoff protocol — required]\n")
			fmt.Fprintf(stdout, "          This step requires real-world action by the user before the sequence can continue.\n")
			fmt.Fprintf(stdout, "          After producing output for this step, emit exactly the following line and stop:\n")
			fmt.Fprintf(stdout, "          When you have results, paste them here and I will continue with step %d (%s).\n", i+2, func() string {
				if i+1 < len(seq.Steps) {
					return seq.Steps[i+1].Role
				}
				return "next step"
			}())
			fmt.Fprintf(stdout, "          This step is complete only when the string \"When you have results, paste them here\" appears in your response — a different phrasing does not satisfy this requirement.\n")
			fmt.Fprintf(stdout, "          Do not produce any further content after this line in the same response.\n")
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
			if step.Token == axisSlug || strings.HasSuffix(step.Token, " "+axisSlug) {
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

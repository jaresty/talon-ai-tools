package barcli

import (
	"fmt"
	"io"
)

// renderDispatchHelp renders the dispatch step protocol for bar help dispatch.
// With no sequenceName, renders a blank template with placeholders.
// With a sequenceName, renders each dispatch step found in that sequence.
func renderDispatchHelp(w io.Writer, grammar *Grammar, sequenceName string) error {
	if sequenceName == "" {
		fmt.Fprintln(w, "Dispatch step template — fill in fan_out, join, isolation, and inner for your use case.")
		fmt.Fprintln(w)
		placeholder := SequenceStep{
			Type:   "dispatch",
			FanOut: "enumerate|replicate",
			Join:   "all|first|merge",
			Role:   "<role of this step>",
			Inner: &InnerSequence{
				Mode:     "autonomous|cycle",
				StopWhen: "<prose condition — omit for autonomous>",
				Steps: []SequenceStep{
					{Token: "<step-1-tokens>", Role: "<step 1 role>"},
					{Token: "<step-2-tokens>", Role: "<step 2 role>"},
					{Token: "<step-3-tokens>", Role: "<step 3 role>"},
				},
			},
		}
		writeDispatchStepBlock(w, placeholder, 0, grammar)
		return nil
	}
	seq, ok := grammar.Sequences[sequenceName]
	if !ok {
		return fmt.Errorf("unknown sequence %q; use 'bar sequence list' to see available sequences", sequenceName)
	}
	dispatchNum := 0
	for i, step := range seq.Steps {
		if step.Type != "dispatch" {
			continue
		}
		dispatchNum++
		if dispatchNum > 1 {
			fmt.Fprintln(w)
		}
		fmt.Fprintf(w, "Dispatch step %d of sequence %q (sequence step %d — %s)\n", dispatchNum, sequenceName, i+1, step.Role)
		fmt.Fprintln(w)
		writeDispatchStepBlock(w, step, i+1, grammar)
	}
	if dispatchNum == 0 {
		fmt.Fprintf(w, "No dispatch steps found in sequence %q.\n", sequenceName)
	}
	return nil
}

// writeDispatchStepBlock renders the dispatch protocol block for a single dispatch step.
// Mirrors the dispatch rendering in runSequenceShow so both stay structurally in sync.
func writeDispatchStepBlock(w io.Writer, step SequenceStep, _ int, _ *Grammar) {
	fmt.Fprintf(w, "          [dispatch protocol — required]\n")
	fmt.Fprintf(w, "          [pre-dispatch agent config gate — required]\n")
	fmt.Fprintf(w, "          Before spawning any Agent tool call at this dispatch step:\n")
	fmt.Fprintf(w, "          0a. Run `bar build [tokens matching this dispatch step's role and task domain]` as a Bash tool call (no channel token — do not append `agent` or `skill`). Use `/bar-dictionary` to look up tokens by intent if needed (e.g. `bar lookup \"<role intent>\"`). Read the bar build output and use it to write the `## Agent Configuration` block. The first Agent tool call must appear in the same response turn as that Bash result block — an Agent tool call appearing in a response turn that contains no bar build Bash result block does not satisfy this step.\n")
	fmt.Fprintf(w, "          0b. Gate: a `## Agent Configuration` block must appear in the transcript in the same response turn as the first Agent tool call, written after the bar build tool call result from 0a. A response turn that spawns an Agent tool call without a preceding `## Agent Configuration` block in that same turn does not satisfy this gate.\n")
	fmt.Fprintf(w, "          0c. Write a block using exactly `## Agent Configuration` as the heading and pass it inline in each Agent tool call prompt. The block may contain: the assigned item, domain constraints, and relevant background from the orchestrator. The block must not contain persona, approach, reasoning style, or behavioral goal statements — those come from each agent's own bar build invocations. A block whose only content is persona or goal statements does not satisfy this step.\n")
	fmt.Fprintf(w, "          1. The orchestrator spawns Agent tool calls only for this step — do not run bar build in the orchestrator turn.\n")
	fanOutDesc := step.FanOut
	if step.FanOut == "enumerate" {
		fanOutDesc = "enumerate — treat prior output as a list; send one item per agent"
	} else if step.FanOut == "replicate" {
		fanOutDesc = "replicate — send full prior output to every agent unchanged"
	}
	fmt.Fprintf(w, "          2. fan_out: %s\n", fanOutDesc)
	isolationContext := "its assigned item + prompt_hint"
	if step.Inner != nil {
		isolationContext = "its assigned item, the inner steps, and inner stop_when. The Agent tool call must include only: (a) the assigned item text, (b) the inner steps below, (c) the inner stop_when. It must not contain the full enumerated list of all items or context from other agents"
	}
	if step.Isolation {
		fmt.Fprintf(w, "          3. isolation: true — each agent receives only %s; no shared history\n", isolationContext)
	} else {
		fmt.Fprintf(w, "          3. isolation: false — agents share conversation context\n")
	}
	fmt.Fprintf(w, "          4. [DISPATCH GATE] A response turn at this dispatch step satisfies this step only when it contains at least one Agent tool call. Text about dispatch is permitted only when Agent tool calls appear in the same turn. Spawn one Agent tool call per item — all in this same response turn. The number of Agent tool calls in this turn must equal the number of items in the enumerated list. Each Agent tool call prompt must contain the `## Agent Configuration` block from step 0c. A response turn where Agent tool call count is less than item count is non-compliant. A response turn where any Agent tool call prompt is missing the `## Agent Configuration` block is non-compliant. Use subagent_type: general-purpose (has Bash access and can run bar commands). A dispatch step is complete only when Agent tool calls appear in the transcript response turn that reads the dispatch step specification. A response turn that reads or references the dispatch step but contains no Agent tool calls does not satisfy this step — proceed to the Agent tool calls without announcing them first.\n")
	if step.Inner != nil {
		fmt.Fprintf(w, "          5. The Agent tool call text must contain: (1) for each inner prompt step shown below, the literal `bar build <token>` command the agent must run; (2) the instruction that each `bar build` output is the agent's task instruction for that step — a response written before the `bar build` output appears does not satisfy this requirement. Run only the bar build commands shown — do not run bar help llm or discover tokens. Each agent must return a ## Derivation block. The orchestrator must preserve all Derivation blocks from every agent in the join result — do not strip or summarize them.\n")
	} else {
		fmt.Fprintf(w, "          5. Each agent receives the step token string. Run: `bar build <step-token-string> --subject '<assigned-item>' --addendum '<prompt_hint>'` where step-token-string is the token string shown in this step. Each agent must return a ## Derivation block naming: bar tokens applied, governing goal, behavioral dimensions. The orchestrator must preserve all Derivation blocks from every agent in the join result — do not strip or summarize them.\n")
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
	fmt.Fprintf(w, "          6. join: %s\n", joinDesc)
	fmt.Fprintf(w, "          7. Pass the join result as --subject to the next step. Do not synthesize first.\n")
	fmt.Fprintf(w, "          Tip: add `topology:relay` to each agent's bar build token list when the agent's output will be passed as --subject to a subsequent step — it structures output for continuation (schemas, contracts, invariants explicit) rather than self-contained reading.\n")
	if step.Inner != nil {
		fmt.Fprintf(w, "          inner mode: %s\n", step.Inner.Mode)
		if step.Inner.StopWhen != "" {
			fmt.Fprintf(w, "          inner stop_when: %s\n", step.Inner.StopWhen)
		}
		if step.Inner.Mode == "cycle" {
			fmt.Fprintf(w, "          [cycle protocol — required]\n")
			fmt.Fprintf(w, "          All steps below form one cycle — execute them in order before checking stop_when.\n")
			var lastPromptToken string
			for ci, is := range step.Inner.Steps {
				if is.Type == "action" {
					fmt.Fprintf(w, "          %d. Run → [action] (action protocol applies — Bash only, no bar build).\n", ci+1)
				} else {
					fmt.Fprintf(w, "          %d. Run → %s (bar build gate applies — run bar build %s first).\n", ci+1, is.Token, is.Token)
					lastPromptToken = is.Token
				}
			}
			fmt.Fprintf(w, "          %d. Check stop_when. A cycle is complete only when a bar build %s tool call result appears in the transcript for this cycle. If stop_when is not met, begin a new cycle from step 1.\n", len(step.Inner.Steps)+1, lastPromptToken)
		}
		for _, is := range step.Inner.Steps {
			innerToken := is.Token
			if is.Type == "action" {
				innerToken = "[action]"
			}
			fmt.Fprintf(w, "          → %-20s %s\n", innerToken, is.Role)
			if is.PromptHint != "" {
				fmt.Fprintf(w, "            %s\n", is.PromptHint)
			}
			if is.Type == "action" {
				fmt.Fprintf(w, "            [action protocol — required] Do NOT run bar build. Exercise the subject under investigation live — invoke it, run it, or send it a request using Bash. This step is complete only when a Bash tool call result appears in the transcript showing output from the running subject — a Bash call that only reads files does not satisfy this requirement. Record the output before proceeding.\n")
			} else {
				fmt.Fprintf(w, "            [bar build gate — required]\n")
				fmt.Fprintf(w, "            Run bar build before producing output for this step.\n")
				fmt.Fprintf(w, "            1. Execute: bar build %s using the token string shown above for this step.\n", innerToken)
				fmt.Fprintf(w, "            2. The bar build output is your task instruction — a response written before bar build output appears in the transcript does not satisfy this gate.\n")
				fmt.Fprintf(w, "            3. This step is complete only when the string \"=== TASK 任務 (DO THIS) ===\" appears in a tool call result in the transcript — prose that mentions bar build does not satisfy this gate.\n")
			}
		}
	}
}

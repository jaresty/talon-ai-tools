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
	fmt.Fprintf(w, "          0a. Run `bar build [tokens matching this dispatch step's role and task domain]` as a Bash tool call (no channel token — do not append `agent` or `skill`). Consider adding `topology:relay` to structure the output for agent handoff — relay makes schemas, contracts, and terminology explicit so each agent can continue without prior context. Use `/bar-dictionary` to look up tokens by intent if needed (e.g. `bar lookup \"<role intent>\"`). Read the bar build output and use it to write the `## Agent Configuration` block. The first Agent tool call must appear in the same response turn as that Bash result block — an Agent tool call appearing in a response turn that contains no bar build Bash result block does not satisfy this step.\n")
	fmt.Fprintf(w, "          0b. Gate: a `## Agent Configuration` block must appear in the transcript in the same response turn as the first Agent tool call, written after the bar build tool call result from 0a. A response turn that spawns an Agent tool call without a preceding `## Agent Configuration` block in that same turn does not satisfy this gate.\n")
	fmt.Fprintf(w, "          0c. Write a block using exactly `## Agent Configuration` as the heading and pass it inline in each Agent tool call prompt. The block may contain: the assigned item, domain constraints, capability requirements (e.g. This step requires Bash tool call access — use subagent_type: general-purpose), and relevant background from the orchestrator. The block must not contain persona, approach, reasoning style, or behavioral goal statements — those come from each agent's own bar build invocations. A block whose only content is persona or goal statements does not satisfy this step.\n")
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
	if step.DuringDispatch != "" {
		fmt.Fprintf(w, "          4. [DISPATCH GATE] A response turn at this dispatch step satisfies this step only when it contains at least one Agent tool call. An evaluator determines whether a turn is the dispatch turn by locating the literal string `[DISPATCH GATE]` in the assistant's text output in that turn. Emit a line of the form `Dispatching N agents:` where N equals the count of items in the enumerated list. Spawn one Agent tool call per item — all in this same response turn. Set run_in_background: true on every Agent tool call. The number of Agent tool calls in this turn must equal N. An evaluator determines required Agent call count by reading N from the first `Dispatching N agents:` line in the turn. Each Agent tool call prompt must contain the `## Agent Configuration` block from step 0c. Use subagent_type: general-purpose (has Bash access and can run bar commands). Proceed to the Agent tool calls without announcing them first. After spawning all agents, immediately run `%s` as a Bash tool call in this same response turn — this is the during_dispatch task and runs concurrently while background agents execute. A turn in which the Bash tool call for this command does not appear in the same turn as the Agent tool calls does not satisfy this step — deferred execution does not satisfy this requirement. The bar build output is a task instruction — its output contains a TASK starting with the literal string \"=== TASK 任務 (DO THIS) ===\"; execute that task now. Background agents may return while you are executing the during_dispatch task — this is expected; when all background agents have returned results, stop the during_dispatch task at that point and proceed to the join step. Do not proceed to the join step until every background agent has returned a result — an evaluator determines compliance by confirming that a result block for each Agent tool call spawned in this step appears in the transcript before step 6 output.\n", step.DuringDispatch)
	} else {
		fmt.Fprintf(w, "          4. [DISPATCH GATE] A response turn at this dispatch step satisfies this step only when it contains at least one Agent tool call. An evaluator determines whether a turn is the dispatch turn by locating the literal string `[DISPATCH GATE]` in the assistant's text output in that turn. Before spawning agents, emit a line of the form `Dispatching N agents:` where N equals the count of items in the enumerated list. Spawn one Agent tool call per item — all in this same response turn. The number of Agent tool calls in this turn must equal N. An evaluator determines required Agent call count by reading N from the first `Dispatching N agents:` line in the turn. Each Agent tool call prompt must contain the `## Agent Configuration` block from step 0c. Use subagent_type: general-purpose (has Bash access and can run bar commands). Proceed to the Agent tool calls without announcing them first. Do not proceed to step 6 until every background agent has returned a result — an evaluator determines compliance by confirming that a result block for each Agent tool call spawned in this step appears in the transcript before step 6 output.\n")
	}
	if step.Inner != nil {
		fmt.Fprintf(w, "          5. The Agent tool call text must contain: (1) for each inner prompt step shown below, the literal `bar build <token>` command the agent must run; (2) the instruction that each `bar build` output is the agent's task instruction for that step — a response written before the `bar build` output appears does not satisfy this requirement. Run only the bar build commands shown — do not run bar help llm or discover tokens. Each agent must return a ## Derivation block. The join result must contain one ## Derivation block per agent, appearing verbatim as returned. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the count equals the number of agents — a join result containing fewer ## Derivation headings than agents does not satisfy this gate.\n")
	} else {
		fmt.Fprintf(w, "          5. Each agent receives the step token string. Run: `bar build <step-token-string> --subject '<assigned-item>' --addendum '<prompt_hint>'` where step-token-string is the token string shown in this step. Each agent must return a ## Derivation block naming: bar tokens applied, governing goal, behavioral dimensions. The join result must contain one ## Derivation block per agent, appearing verbatim as returned. An evaluator determines compliance by counting ## Derivation headings in the join result and confirming the count equals the number of agents — a join result containing fewer ## Derivation headings than agents does not satisfy this gate.\n")
	}
	joinDesc := step.Join
	switch step.Join {
	case "all":
		joinDesc = "all — wait for every agent; fail if any fail"
	case "first":
		joinDesc = "first — take the first successful result; remaining agents may still complete. Each Agent tool call prompt must contain: (a) an instruction to return the finding immediately upon confirming the result, and (b) a statement that its result will be taken as the join answer if it is first to confirm. An evaluator determines compliance by locating each Agent tool call prompt and checking whether both clauses are present as distinct sentences — a prompt containing neither clause does not satisfy this gate."
	case "merge":
		joinDesc = "merge — collect all results into an array"
	}
	fmt.Fprintf(w, "          6. join: %s\n", joinDesc)
	fmt.Fprintf(w, "          7. Before running bar build for the next step: reproduce each ## Derivation block from the join result verbatim in the output. An evaluator determines compliance by counting ## Derivation headings in the join result passed as --subject and confirming the same count appears in the output before the first bar build call for the next step — a count mismatch does not satisfy this gate. Then run bar build with the full join result as --subject.\n")
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
					if is.PromptHint != "" {
						fmt.Fprintf(w, "          %d. Run → %s (bar build gate applies — run bar build %s first). %s\n", ci+1, is.Token, is.Token, is.PromptHint)
					} else {
						fmt.Fprintf(w, "          %d. Run → %s (bar build gate applies — run bar build %s first).\n", ci+1, is.Token, is.Token)
					}
					lastPromptToken = is.Token
				}
			}
			fmt.Fprintf(w, "          %d. Check stop_when. A cycle is complete only when a bar build %s tool call result appears in the transcript for this cycle. The Findings block is permitted only when the final step result for this cycle contains the literal stop_when string. A final step result that does not contain that literal string requires a new cycle beginning from step 1 — the Findings block must not appear before the literal stop_when string appears in a bar build %s tool call result.\n", len(step.Inner.Steps)+1, lastPromptToken, lastPromptToken)
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

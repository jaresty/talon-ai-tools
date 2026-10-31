package barcli

import (
	"fmt"
	"io"
	"strings"
)

// renderDispatchHelp renders the dispatch step protocol for bar help dispatch.
// With no sequenceName, renders a blank template with placeholders.
// With a sequenceName, renders each dispatch step found in that sequence.
func renderDispatchHelp(w io.Writer, grammar *Grammar, sequenceName string) error {
	st := grammar.SequenceText
	if st == nil {
		return fmt.Errorf("grammar is missing sequence_text; regenerate it with make")
	}
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
		writeDispatchStepBlock(w, placeholder, st)
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
		writeDispatchStepBlock(w, step, st)
	}
	if dispatchNum == 0 {
		fmt.Fprintf(w, "No dispatch steps found in sequence %q.\n", sequenceName)
	}
	return nil
}

// writeDispatchStepBlock renders a dispatch step from the grammar's sequence text.
// It keeps the same functional requirements as the standard block (Agent Configuration,
// the Dispatching line, background agents, Derivation blocks, join and isolation
// behavior) without the gate-by-gate compliance language.
func writeDispatchStepBlock(w io.Writer, step SequenceStep, ps *SequenceText) {
	d := ps.Dispatch
	line := func(s string) { fmt.Fprintf(w, "          %s\n", s) }
	line(d.Header)
	for _, l := range d.Preflight {
		line(l)
	}
	line(d.OrchestratorOnly)
	switch step.FanOut {
	case "enumerate":
		line("2. fan_out: " + d.FanOutEnumerate)
	case "replicate":
		line("2. fan_out: " + d.FanOutReplicate)
	default:
		line("2. fan_out: " + step.FanOut)
	}
	ctx := "its assigned item + prompt_hint"
	if step.Inner != nil {
		ctx = "its assigned item, the inner steps, and the inner stop_when (not the full list of items)"
	}
	if step.Isolation {
		line("3. " + strings.ReplaceAll(d.IsolationTrue, "{ctx}", ctx))
	} else {
		line("3. " + d.IsolationFalse)
	}
	if step.DuringDispatch != "" {
		line(strings.ReplaceAll(d.StartDuring, "{cmd}", step.DuringDispatch))
	} else {
		line(d.Start)
	}
	if step.Inner != nil {
		line(d.AgentTaskInner)
	} else {
		line(d.AgentTask)
	}
	switch step.Join {
	case "all":
		line("6. " + d.JoinAll)
	case "first":
		line("6. " + d.JoinFirst)
	case "merge":
		line("6. " + d.JoinMerge)
	default:
		line("6. join: " + step.Join)
	}
	line(d.After)
	if step.Inner == nil {
		return
	}
	line("inner mode: " + step.Inner.Mode)
	if step.Inner.StopWhen != "" {
		line("inner stop_when: " + rewriteHint(ps, step.Inner.StopWhen))
	}
	if step.Inner.Mode == "cycle" {
		line(d.CycleIntro)
		var lastPromptToken string
		for ci, is := range step.Inner.Steps {
			if is.Type == "action" {
				line(fmt.Sprintf("%d. Run → [action] (Bash only, no bar build).", ci+1))
				continue
			}
			text := fmt.Sprintf("%d. Run → %s (run `bar build %s` first).", ci+1, is.Token, is.Token)
			if is.PromptHint != "" {
				text += " " + rewriteHint(ps, is.PromptHint)
			}
			line(text)
			lastPromptToken = is.Token
		}
		line(fmt.Sprintf("%d. %s", len(step.Inner.Steps)+1, strings.ReplaceAll(d.CycleCheck, "{tok}", lastPromptToken)))
	}
	for _, is := range step.Inner.Steps {
		innerToken := is.Token
		if is.Type == "action" {
			innerToken = "[action]"
		}
		fmt.Fprintf(w, "          → %-20s %s\n", innerToken, is.Role)
		if is.PromptHint != "" {
			fmt.Fprintf(w, "            %s\n", rewriteHint(ps, is.PromptHint))
		}
		if is.Type == "action" {
			fmt.Fprintf(w, "            %s\n", d.InnerAction)
			continue
		}
		for _, l := range ps.BuildGate {
			fmt.Fprintf(w, "            %s\n", strings.ReplaceAll(l, "<token-string>", innerToken))
		}
	}
}

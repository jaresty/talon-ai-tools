package barcli

import (
	"fmt"
	"io"
	"sort"
)

// renderSequencesHelp writes the narrative sequences guide to w.
// This is the output of `bar help sequences`.
func renderSequencesHelp(w io.Writer, grammar *Grammar) {
	fmt.Fprintln(w, "# Bar Named Sequences")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Named sequences are directed multi-step workflow patterns where step N's output")
	fmt.Fprintln(w, "makes step N+1 more effective than running it cold.")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "## When to use a sequence vs. an ad hoc chain")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Use a named sequence when:")
	fmt.Fprintln(w, "  - The workflow has a real-world pause between steps (experiment, deploy, interview)")
	fmt.Fprintln(w, "  - The pattern recurs and the step ordering is non-obvious")
	fmt.Fprintln(w, "  - You want the LLM to declare mode and pause/resume protocol explicitly")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "Use an ad hoc chain when:")
	fmt.Fprintln(w, "  - All steps can run on existing information without user action between them")
	fmt.Fprintln(w, "  - The pattern is one-off and unlikely to recur")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "## Execution modes")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "  autonomous  All steps run without pausing. Default for ad hoc chains.")
	fmt.Fprintln(w, "  linear      Pause after each step marked ⏸ for user to provide real-world results.")
	fmt.Fprintln(w, "  cycle       After each full pass, prompt the user to run another cycle or finish.")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "## Available sequences")
	fmt.Fprintln(w)

	names := make([]string, 0, len(grammar.Sequences))
	for k := range grammar.Sequences {
		names = append(names, k)
	}
	sort.Strings(names)

	for _, name := range names {
		seq := grammar.Sequences[name]
		fmt.Fprintf(w, "### %s\n", name)
		fmt.Fprintf(w, "  %s\n", seq.Description)
		if seq.Example != "" {
			fmt.Fprintf(w, "  Example: %s\n", seq.Example)
		}
		fmt.Fprintf(w, "  Mode: %s\n", seq.Mode)
		fmt.Fprintf(w, "  Steps:\n")
		for i, step := range seq.Steps {
			marker := "   "
			if step.RequiresUserInput {
				marker = " ⏸ "
			}
			fmt.Fprintf(w, "%sStep %d  %s — %s\n", marker, i+1, step.Token, step.Role)
		}
		fmt.Fprintln(w)
	}

	fmt.Fprintln(w, "## Discovering sequences")
	fmt.Fprintln(w)
	fmt.Fprintln(w, "  bar sequence list                  — list all named sequences")
	fmt.Fprintln(w, "  bar sequence show <name>           — show steps, mode, and example for one sequence")
	fmt.Fprintln(w, "  bar sequence show <name> --json    — machine-readable output")
}

package barcli

import (
	"fmt"
	"io"
	"sort"
)

// renderHelpComposition prints the prose for a named composition, or lists all names if name is empty.
func renderHelpComposition(w io.Writer, grammar *Grammar, name string) error {
	if name == "" {
		names := make([]string, 0, len(grammar.Compositions))
		for _, comp := range grammar.Compositions {
			names = append(names, comp.Name)
		}
		sort.Strings(names)
		fmt.Fprintln(w, "Available compositions (use: bar help composition <name>):")
		for _, n := range names {
			fmt.Fprintf(w, "  %s\n", n)
		}
		return nil
	}
	for _, comp := range grammar.Compositions {
		if comp.Name == name {
			fmt.Fprintln(w, comp.Prose)
			return nil
		}
	}
	names := make([]string, 0, len(grammar.Compositions))
	for _, comp := range grammar.Compositions {
		names = append(names, comp.Name)
	}
	sort.Strings(names)
	return fmt.Errorf("unknown composition %q; available: %v", name, names)
}

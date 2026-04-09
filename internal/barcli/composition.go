package barcli

// ADR-0227: Pairwise token compositions — Go grammar layer.
//
// A Composition defines prompt text injected into the COMPOSITION RULES section
// when all tokens in its set are co-present in a bar build command.

// Composition is a named pairwise token composition.
type Composition struct {
	Name   string   `json:"name"`
	Tokens []string `json:"tokens"`
	Prose  string   `json:"prose"`
}

// ActiveCompositions returns the compositions whose token sets are all present
// in the given active token set (map of axis -> set of active token slugs).
func (g *Grammar) ActiveCompositions(activeMethodTokens map[string]struct{}) []Composition {
	var active []Composition
	for _, comp := range g.Compositions {
		allPresent := true
		for _, tok := range comp.Tokens {
			if _, ok := activeMethodTokens[tok]; !ok {
				allPresent = false
				break
			}
		}
		if allPresent {
			active = append(active, comp)
		}
	}
	return active
}

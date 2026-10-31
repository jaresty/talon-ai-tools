package barcli

import "strings"

// rewriteHint applies the grammar's wording rewrites (gate language in step
// hints and stop conditions) to s. With no sequence text it returns s unchanged.
func rewriteHint(st *SequenceText, s string) string {
	if st == nil {
		return s
	}
	for _, pair := range st.Rewrites {
		if len(pair) == 2 {
			s = strings.ReplaceAll(s, pair[0], pair[1])
		}
	}
	return s
}

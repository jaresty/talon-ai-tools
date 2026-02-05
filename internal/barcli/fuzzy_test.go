package barcli

import (
	"reflect"
	"testing"
)

func TestFuzzyMatch(t *testing.T) {
	tests := []struct {
		name       string
		input      string
		candidates []string
		maxDist    int
		want       []string
	}{
		{
			name:       "exact match excluded",
			input:      "analyz",
			candidates: []string{"analyz", "analyze", "analysis"},
			maxDist:    2,
			want:       []string{"analyze"}, // Exact match "analyz" excluded; "analyze" distance 1, "analysis" distance 3
		},
		{
			name:       "single character typo",
			input:      "analyz",
			candidates: []string{"analyze", "analysis", "adversarial"},
			maxDist:    2,
			want:       []string{"analyze"}, // "analysis" is distance 3 from "analyz"
		},
		{
			name:       "missing dash",
			input:      "fly rog",
			candidates: []string{"fly-rog", "focus", "fog"},
			maxDist:    2,
			want:       []string{"fly-rog"},
		},
		{
			name:       "no matches within distance",
			input:      "xyz",
			candidates: []string{"analyze", "focus", "todo"},
			maxDist:    2,
			want:       []string{},
		},
		{
			name:       "prefix match prioritized",
			input:      "analy",
			candidates: []string{"analyze", "analysis", "adversarial", "analog"},
			maxDist:    2,
			want:       []string{"analyze", "analog"}, // Prefixes within distance 2; "analysis" is distance 3
		},
		{
			name:       "limit to 3 suggestions",
			input:      "focs",
			candidates: []string{"focus", "fog", "form", "flow", "formats", "facilitate"},
			maxDist:    2,
			want:       []string{"focus", "fog", "form"}, // First 3 within distance 2
		},
		{
			name:       "case insensitive matching",
			input:      "Analyz",
			candidates: []string{"analyze", "analysis"},
			maxDist:    2,
			want:       []string{"analyze"}, // "analysis" is distance 3 from "Analyz"
		},
		{
			name:       "empty input",
			input:      "",
			candidates: []string{"analyze", "focus"},
			maxDist:    2,
			want:       []string{},
		},
		{
			name:       "empty candidates",
			input:      "analyze",
			candidates: []string{},
			maxDist:    2,
			want:       []string{},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := fuzzyMatch(tt.input, tt.candidates, tt.maxDist)
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("fuzzyMatch(%q, %v, %d) = %v, want %v",
					tt.input, tt.candidates, tt.maxDist, got, tt.want)
			}
		})
	}
}

func TestLevenshteinDistance(t *testing.T) {
	tests := []struct {
		name string
		s1   string
		s2   string
		want int
	}{
		{
			name: "identical strings",
			s1:   "hello",
			s2:   "hello",
			want: 0,
		},
		{
			name: "single substitution",
			s1:   "hello",
			s2:   "hallo",
			want: 1,
		},
		{
			name: "single insertion",
			s1:   "hello",
			s2:   "helllo",
			want: 1,
		},
		{
			name: "single deletion",
			s1:   "hello",
			s2:   "helo",
			want: 1,
		},
		{
			name: "completely different",
			s1:   "abc",
			s2:   "xyz",
			want: 3,
		},
		{
			name: "empty strings",
			s1:   "",
			s2:   "",
			want: 0,
		},
		{
			name: "one empty",
			s1:   "hello",
			s2:   "",
			want: 5,
		},
		{
			name: "missing dash in multi-word token",
			s1:   "fly rog",
			s2:   "fly-rog",
			want: 1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := levenshteinDistance(tt.s1, tt.s2)
			if got != tt.want {
				t.Errorf("levenshteinDistance(%q, %q) = %d, want %d",
					tt.s1, tt.s2, got, tt.want)
			}
		})
	}
}

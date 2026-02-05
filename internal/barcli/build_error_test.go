package barcli

import (
	"strings"
	"testing"
)

func TestBuildUnrecognizedToken(t *testing.T) {
	tests := []struct {
		name              string
		args              []string
		expectExit        bool
		expectInMessage   []string
		unexpectInMessage []string
	}{
		{
			name:       "typo in method override shows axis-specific suggestions",
			args:       []string{"build", "method=analysi"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token for method",
				"analysi",
				"Did you mean",
				"analysis",
				"bar help tokens method",
			},
		},
		{
			name:       "typo in scope override shows axis-specific suggestions",
			args:       []string{"build", "scope=meen"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token for scope",
				"meen",
				"Did you mean",
				"mean",
				"bar help tokens scope",
			},
		},
		{
			name:       "typo in shorthand token shows general suggestions",
			args:       []string{"build", "meen"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token",
				"meen",
				"Did you mean",
				"mean",
				"bar help tokens",
			},
		},
		{
			name:       "completely unknown token shows help hint no suggestions",
			args:       []string{"build", "xyz123"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token",
				"xyz123",
				"bar help tokens",
			},
			unexpectInMessage: []string{
				"Did you mean",
			},
		},
		{
			name:       "typo in static prompt shows suggestions",
			args:       []string{"build", "mak"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token",
				"mak",
				"Did you mean",
				"make",
			},
		},
		{
			name:       "typo in form override shows axis-specific suggestions",
			args:       []string{"build", "form=caz"},
			expectExit: true,
			expectInMessage: []string{
				"unrecognized token for form",
				"caz",
				"Did you mean",
				"case",
				"bar help tokens form",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := runBuildCLI(t, tt.args, nil)

			if tt.expectExit && result.Exit == 0 {
				t.Errorf("expected non-zero exit, got 0")
			}

			for _, expected := range tt.expectInMessage {
				if !strings.Contains(result.Stderr, expected) {
					t.Errorf("expected stderr to contain %q\nGot:\n%s", expected, result.Stderr)
				}
			}

			for _, unexpected := range tt.unexpectInMessage {
				if strings.Contains(result.Stderr, unexpected) {
					t.Errorf("expected stderr NOT to contain %q\nGot:\n%s", unexpected, result.Stderr)
				}
			}
		})
	}
}

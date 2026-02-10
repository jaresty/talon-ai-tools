package barcli

import (
	"strings"
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

func TestParseArgsBuildCommand(t *testing.T) {
	opts, err := cli.Parse([]string{"build", "make", "struct", "--subject", "hello", "--json", "--output", "out.txt", "--env", "CHATGPT_API_KEY", "--env=ORG_ID"})

	if err != nil {
		t.Fatalf("cli.Parse returned error: %v", err)
	}
	if opts.Command != "build" {
		t.Fatalf("expected command 'build', got %q", opts.Command)
	}
	if got, want := len(opts.Tokens), 2; got != want {
		t.Fatalf("expected %d tokens, got %d", want, got)
	}
	if opts.Tokens[0] != "make" || opts.Tokens[1] != "struct" {
		t.Fatalf("unexpected tokens: %v", opts.Tokens)
	}
	if opts.Subject != "hello" {
		t.Fatalf("expected subject 'hello', got %q", opts.Subject)
	}
	if !opts.JSON {
		t.Fatalf("expected JSON flag to be true")
	}
	if opts.OutputPath != "out.txt" {
		t.Fatalf("expected output path 'out.txt', got %q", opts.OutputPath)
	}
	if got := opts.EnvAllowlist; len(got) != 2 || got[0] != "CHATGPT_API_KEY" || got[1] != "ORG_ID" {
		t.Fatalf("unexpected env allowlist: %v", got)
	}
}

func TestParseArgsEnvDedup(t *testing.T) {
	opts, err := cli.Parse([]string{"tui", "--env", "CHATGPT_API_KEY", "--env", "CHATGPT_API_KEY", "--env", "ORG_ID"})
	if err != nil {
		t.Fatalf("cli.Parse returned error: %v", err)
	}
	if opts.Command != "tui" {
		t.Fatalf("expected command 'tui', got %q", opts.Command)
	}
	if got := opts.EnvAllowlist; len(got) != 2 || got[0] != "CHATGPT_API_KEY" || got[1] != "ORG_ID" {
		t.Fatalf("expected deduped env allowlist, got %v", got)
	}
}

func TestParseArgsErrors(t *testing.T) {
	if _, err := cli.Parse([]string{}); err == nil {
		t.Fatalf("expected error for missing command")
	}
	if _, err := cli.Parse([]string{"build", "--prompt", "body"}); err == nil || !strings.Contains(err.Error(), "removed") {
		t.Fatalf("expected --prompt removed error, got: %v", err)
	}
	if _, err := cli.Parse([]string{"build", "--subject", "body", "--input", "path"}); err == nil || !strings.Contains(err.Error(), "cannot") {
		t.Fatalf("expected conflict error for subject/input, got: %v", err)
	}
	if _, err := cli.Parse([]string{"build", "--unknown"}); err == nil {
		t.Fatalf("expected error for unknown flag")
	}
}

func TestParseArgsFixtureDimensionErrors(t *testing.T) {
	cases := [][]string{
		{"tui", "--fixture-width", "0"},
		{"tui", "--fixture-width=0"},
		{"tui", "--width", "-5"},
		{"tui", "--fixture-height", "0"},
		{"tui", "--height", "0"},
	}
	for _, args := range cases {
		if _, err := cli.Parse(args); err == nil {
			t.Fatalf("expected fixture dimension error for args %v", args)
		}
	}
}

func TestParseArgsEnvValidation(t *testing.T) {
	if _, err := cli.Parse([]string{"tui", "--env", "CHATGPT_API_KEY", "--env=", "--env", "  ORG_ID  "}); err == nil {
		t.Fatalf("expected error for blank --env entry")
	}

	opts, err := cli.Parse([]string{"tui", "--env", " CHATGPT_API_KEY ", "--env", "ORG_ID", "--env", "CHATGPT_API_KEY"})
	if err != nil {
		t.Fatalf("unexpected parse error: %v", err)
	}
	expected := []string{"CHATGPT_API_KEY", "ORG_ID"}
	if got := opts.EnvAllowlist; len(got) != len(expected) || got[0] != expected[0] || got[1] != expected[1] {
		t.Fatalf("expected deduped env allowlist %v, got %v", expected, got)
	}
}

func TestParseArgsNoClipboard(t *testing.T) {

	opts, err := cli.Parse([]string{"tui", "--no-clipboard"})
	if err != nil {
		t.Fatalf("cli.Parse returned error: %v", err)
	}
	if !opts.NoClipboard {
		t.Fatalf("expected NoClipboard to be true")
	}
}

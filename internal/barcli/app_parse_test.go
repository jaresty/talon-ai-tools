package barcli

import (
	"testing"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
)

func TestParseArgsBuildCommand(t *testing.T) {
	opts, err := cli.Parse([]string{"build", "todo", "focus", "--prompt", "hello", "--json", "--output", "out.txt", "--env", "CHATGPT_API_KEY", "--env=ORG_ID"})

	if err != nil {
		t.Fatalf("cli.Parse returned error: %v", err)
	}
	if opts.Command != "build" {
		t.Fatalf("expected command 'build', got %q", opts.Command)
	}
	if got, want := len(opts.Tokens), 2; got != want {
		t.Fatalf("expected %d tokens, got %d", want, got)
	}
	if opts.Tokens[0] != "todo" || opts.Tokens[1] != "focus" {
		t.Fatalf("unexpected tokens: %v", opts.Tokens)
	}
	if opts.Prompt != "hello" {
		t.Fatalf("expected prompt 'hello', got %q", opts.Prompt)
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
	if _, err := cli.Parse([]string{"build", "--prompt"}); err == nil {
		t.Fatalf("expected error for missing --prompt value")
	}
	if _, err := cli.Parse([]string{"build", "--unknown"}); err == nil {
		t.Fatalf("expected error for unknown flag")
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

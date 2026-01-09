package barcli

import (
	"fmt"
	"io"

	"github.com/talonvoice/talon-ai-tools/internal/bartui"
)

var startTUI = defaultTUIStarter

func defaultTUIStarter(opts bartui.Options) error {
	program, err := bartui.NewProgram(opts)
	if err != nil {
		return err
	}
	return program.Start()
}

func runTUI(opts *cliOptions, stdin io.Reader, stdout, stderr io.Writer) int {
	if opts.JSON {
		writeError(stderr, "tui does not support --json output")
		return 1
	}
	if opts.Prompt != "" || opts.InputPath != "" {
		writeError(stderr, "tui captures subject input interactively; remove --prompt/--input")
		return 1
	}
	if opts.OutputPath != "" {
		writeError(stderr, "tui does not support --output")
		return 1
	}
	if opts.Force {
		writeError(stderr, "tui does not accept --force")
		return 1
	}

	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	tokens := append([]string(nil), opts.Tokens...)
	preview := func(subject string) (string, error) {
		result, buildErr := Build(grammar, tokens)
		if buildErr != nil {
			return "", fmt.Errorf("build prompt: %s", buildErr.Message)
		}
		result.Subject = subject
		result.PlainText = RenderPlainText(result)
		return result.PlainText, nil
	}

	err = startTUI(bartui.Options{
		Tokens:  tokens,
		Input:   stdin,
		Output:  stdout,
		Preview: preview,
	})
	if err != nil {
		writeError(stderr, fmt.Sprintf("launch tui: %v", err))
		return 1
	}
	return 0
}

// SetTUIStarter overrides the Bubble Tea starter for testing. It returns a restore
// function that resets the previous starter when invoked. Passing nil restores the
// default starter immediately.
func SetTUIStarter(starter func(bartui.Options) error) func() {
	previous := startTUI
	if starter == nil {
		startTUI = defaultTUIStarter
	} else {
		startTUI = starter
	}
	return func() {
		startTUI = previous
	}
}

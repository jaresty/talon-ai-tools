package barcli

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"os/exec"
	"time"

	"github.com/atotto/clipboard"
	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
	"github.com/talonvoice/talon-ai-tools/internal/bartui2"
)

var startTUI2 = defaultTUI2Starter

func defaultTUI2Starter(opts bartui2.Options) error {
	program, err := bartui2.NewProgram(opts)
	if err != nil {
		return err
	}
	_, err = program.Run()
	return err
}

func runTUI2(opts *cli.Config, stdin io.Reader, stdout, stderr io.Writer) int {
	if opts.NoInput {
		writeError(stderr, "tui2 requires an interactive terminal; use --fixture PATH for non-interactive testing or --no-input is not supported by tui2")
		return 1
	}
	if opts.JSON {
		writeError(stderr, "tui2 does not support --json output")
		return 1
	}
	if opts.InputPath != "" {
		writeError(stderr, "tui2 captures subject input interactively; remove --input")
		return 1
	}
	if opts.OutputPath != "" {
		writeError(stderr, "tui2 does not support --output")
		return 1
	}
	if opts.Force {
		writeError(stderr, "tui2 does not accept --force")
		return 1
	}

	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	tokenCategories := BuildTokenCategories(grammar)
	tokens := append([]string(nil), opts.Tokens...)

	preview := func(subject string, addendum string, tokenSet []string) (string, error) {
		result, buildErr := Build(grammar, tokenSet)
		if buildErr != nil {
			return "", fmt.Errorf("build prompt: %s", buildErr.Message)
		}
		result.Subject = subject
		result.Addendum = addendum
		result.PlainText = RenderPlainText(result)
		return result.PlainText, nil
	}

	runCommand := func(ctx context.Context, command string, stdin string) (string, string, error) {
		cmd := exec.CommandContext(ctx, "sh", "-c", command)
		cmd.Stdin = bytes.NewBufferString(stdin)

		var stdout, stderr bytes.Buffer
		cmd.Stdout = &stdout
		cmd.Stderr = &stderr

		err := cmd.Run()
		return stdout.String(), stderr.String(), err
	}

	crossAxisFor := func(axis, token string) (map[string][]string, map[string]map[string]string) {
		data := grammar.CrossAxisCompositionFor(axis, token)
		natural := make(map[string][]string)
		cautionary := make(map[string]map[string]string)
		for axisB, pair := range data {
			if len(pair.Natural) > 0 {
				natural[axisB] = pair.Natural
			}
			if len(pair.Cautionary) > 0 {
				cautionary[axisB] = pair.Cautionary
			}
		}
		return natural, cautionary
	}

	tuiOpts := bartui2.Options{
		InitialTokens:           tokens,
		TokenCategories:         tokenCategories,
		Preview:                 preview,
		ClipboardWrite:          clipboard.WriteAll,
		RunCommand:              runCommand,
		CommandTimeout:          30 * time.Second,
		InitialWidth:            opts.FixtureWidth,
		InitialHeight:           opts.FixtureHeight,
		NoAltScreen:             opts.NoAltScreen,
		InitialCommand:          opts.InitialCommand,
		CrossAxisCompositionFor: crossAxisFor,
		AxisDescriptions:        grammar.Axes.AxisDescriptions,
	}

	if err := startTUI2(tuiOpts); err != nil {
		writeError(stderr, fmt.Sprintf("tui2: %v", err))
		return 1
	}

	return 0
}

// SetTUI2Starter overrides the Bubble Tea starter for testing. It returns a restore
// function that resets the previous starter when invoked. Passing nil restores the
// default starter immediately.
func SetTUI2Starter(starter func(bartui2.Options) error) func() {
	previous := startTUI2
	if starter == nil {
		startTUI2 = defaultTUI2Starter
	} else {
		startTUI2 = starter
	}
	return func() {
		startTUI2 = previous
	}
}

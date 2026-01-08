package barcli

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"strings"
)

// Run executes the bar CLI with the provided arguments and streams.
func Run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	options, err := parseArgs(args)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	if options.Command != "build" {
		writeError(stderr, "usage: bar build [tokens...] [options]")
		return 1
	}

	grammar, loadErr := LoadGrammar(options.GrammarPath)
	if loadErr != nil {
		cliErr := &CLIError{Type: "io", Message: loadErr.Error()}
		emitError(cliErr, options.JSON, stdout, stderr)
		return 1
	}

	promptBody, promptErr := readPrompt(options, stdin)
	if promptErr != nil {
		cliErr := &CLIError{Type: "io", Message: promptErr.Error()}
		emitError(cliErr, options.JSON, stdout, stderr)
		return 1
	}

	result, buildErr := Build(grammar, options.Tokens)
	if buildErr != nil {
		emitError(buildErr, options.JSON, stdout, stderr)
		return 1
	}

	result.Subject = promptBody
	result.PlainText = RenderPlainText(result)

	if options.JSON {
		payload, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			cliErr := &CLIError{Type: "io", Message: err.Error()}
			emitError(cliErr, options.JSON, stdout, stderr)
			return 1
		}
		payload = append(payload, '\n')
		if err := writeOutput(options.OutputPath, payload, stdout); err != nil {
			cliErr := &CLIError{Type: "io", Message: err.Error()}
			emitError(cliErr, options.JSON, stdout, stderr)
			return 1
		}
		return 0
	}

	if err := writeOutput(options.OutputPath, []byte(result.PlainText), stdout); err != nil {
		cliErr := &CLIError{Type: "io", Message: err.Error()}
		emitError(cliErr, options.JSON, stdout, stderr)
		return 1
	}
	return 0
}

type cliOptions struct {
	Command     string
	Tokens      []string
	Prompt      string
	InputPath   string
	OutputPath  string
	JSON        bool
	GrammarPath string
}

func parseArgs(args []string) (*cliOptions, error) {
	opts := &cliOptions{}
	tokens := make([]string, 0, len(args))

	i := 0
	for i < len(args) {
		arg := args[i]
		switch {
		case arg == "--prompt":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--prompt requires a value")
			}
			opts.Prompt = args[i]
		case strings.HasPrefix(arg, "--prompt="):
			opts.Prompt = strings.TrimPrefix(arg, "--prompt=")
		case arg == "--input":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--input requires a path")
			}
			opts.InputPath = args[i]
		case strings.HasPrefix(arg, "--input="):
			opts.InputPath = strings.TrimPrefix(arg, "--input=")
		case arg == "--output" || arg == "-o":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("%s requires a path", arg)
			}
			opts.OutputPath = args[i]
		case strings.HasPrefix(arg, "--output="):
			opts.OutputPath = strings.TrimPrefix(arg, "--output=")
		case arg == "--json":
			opts.JSON = true
		case arg == "--grammar":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--grammar requires a path")
			}
			opts.GrammarPath = args[i]
		case strings.HasPrefix(arg, "--grammar="):
			opts.GrammarPath = strings.TrimPrefix(arg, "--grammar=")
		case strings.HasPrefix(arg, "--"):
			return nil, fmt.Errorf("unknown flag %s", arg)
		default:
			if opts.Command == "" {
				opts.Command = arg
			} else {
				tokens = append(tokens, arg)
			}
		}
		i++
	}

	if opts.Command == "" {
		return nil, fmt.Errorf("usage: bar build [tokens...] [options]")
	}
	if opts.Prompt != "" && opts.InputPath != "" {
		return nil, fmt.Errorf("--prompt and --input cannot be used together")
	}

	opts.Tokens = tokens
	return opts, nil
}

func readPrompt(opts *cliOptions, stdin io.Reader) (string, error) {
	if opts.Prompt != "" {
		return trimTrailingNewlines(opts.Prompt), nil
	}
	if opts.InputPath != "" {
		data, err := os.ReadFile(opts.InputPath)
		if err != nil {
			return "", err
		}
		return trimTrailingNewlines(string(data)), nil
	}
	if isPipedInput(stdin) {
		data, err := io.ReadAll(stdin)
		if err != nil {
			return "", err
		}
		return trimTrailingNewlines(string(data)), nil
	}
	return "", nil
}

func trimTrailingNewlines(value string) string {
	return strings.TrimRight(value, "\r\n")
}

func isPipedInput(r io.Reader) bool {
	if file, ok := r.(*os.File); ok {
		info, err := file.Stat()
		if err == nil {
			return (info.Mode() & os.ModeCharDevice) == 0
		}
	}
	return false
}

func writeOutput(path string, data []byte, stdout io.Writer) error {
	if path == "" {
		_, err := stdout.Write(data)
		return err
	}
	return os.WriteFile(path, data, 0o644)
}

func emitError(err *CLIError, jsonMode bool, stdout, stderr io.Writer) {
	if jsonMode {
		payload, marshalErr := json.MarshalIndent(map[string]*CLIError{"error": err}, "", "  ")
		if marshalErr != nil {
			writeError(stderr, err.Message)
			return
		}
		payload = append(payload, '\n')
		if _, werr := stdout.Write(payload); werr != nil {
			writeError(stderr, werr.Error())
		}
		return
	}
	writeError(stderr, err.Message)
}

func writeError(w io.Writer, message string) {
	if message == "" {
		return
	}
	fmt.Fprintf(w, "error: %s\n", message)
}

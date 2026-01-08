package barcli

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sort"
	"strings"
)

const (
	buildUsage = "usage: bar build [tokens...] [options]"
	topUsage   = "usage: bar [build|help|completion]"
)

var generalHelpText = strings.TrimSpace(`USAGE
  bar build <tokens>... [--prompt TEXT|--input FILE] [--output FILE] [--json]
  cat prompt.txt | bar build todo steps fog

  bar help
  bar help tokens [--grammar PATH]

   bar completion <shell> [--grammar PATH] [--output FILE]
     (shell = bash | zsh | fish)
 
   The CLI ships with an embedded prompt grammar. Use --grammar or
   BAR_GRAMMAR_PATH to point at alternate payloads for testing.
 
 TOKEN ORDER (SHORTHAND)

  1. Static prompt          (0..1 tokens, default infer)
  2. Completeness           (0..1)
  3. Scope                  (0..2)
  4. Method                 (0..3)
  5. Form                   (0..1)
  6. Channel                (0..1)
  7. Directional            (0..1)
  8. Persona hints / preset (voice, audience, tone, intent, persona=<preset>)

  After the first key=value override, *all* remaining tokens must be key=value.
  Multi-word shorthand (for example "fly rog" or "to team") may be supplied as
  separate words; the CLI will combine them automatically. Use quotes when your
  shell would otherwise split or glob the text.

COMMANDS
  build        Construct a prompt recipe from shorthand tokens or key=value overrides.
                Accepts input via --prompt, --input, or STDIN (piped).
  help         Show this message.
  help tokens  List available static prompts, contract axes, persona presets, and multi-word tokens
                using the exported prompt grammar.
  completion   Emit shell completion scripts (bash, zsh, fish) informed by the exported grammar.

TOPICS & EXAMPLES
  List available tokens:           bar help tokens
  Emit JSON for automation:        bar build --json todo focus steps fog
  Supply prompt content:           bar build todo focus --prompt "Fix onboarding"
   Mix shorthand with overrides:    bar build todo focus method=steps directional=fog
   Inspect another grammar file:    bar help tokens --grammar /path/to/grammar.json
   Generate fish completions:       bar completion fish > ~/.config/fish/completions/bar.fish



Flags such as --grammar override the grammar JSON path when necessary.
`) + "\n\n"

// Run executes the bar CLI with the provided arguments and streams.

func Run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	options, err := parseArgs(args)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	if options.Command == "help" {
		return runHelp(options, stdout, stderr)
	}

	if options.Command == "completion" {
		return runCompletion(options, stdout, stderr)
	}

	if options.Command == "__complete" {
		return runCompletionEngine(options, stdout, stderr)
	}

	if options.Command != "build" {
		writeError(stderr, topUsage)
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
		return nil, fmt.Errorf(topUsage)
	}
	if opts.Prompt != "" && opts.InputPath != "" {
		return nil, fmt.Errorf("--prompt and --input cannot be used together")
	}

	opts.Tokens = tokens
	return opts, nil
}

func runHelp(opts *cliOptions, stdout, stderr io.Writer) int {
	if len(opts.Tokens) == 0 {
		fmt.Fprint(stdout, generalHelpText)
		return 0
	}

	topic := opts.Tokens[0]
	switch topic {
	case "tokens":
		grammar, err := LoadGrammar(opts.GrammarPath)
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		renderTokensHelp(stdout, grammar)
		return 0
	default:
		writeError(stderr, fmt.Sprintf("unknown help topic %q", topic))
		fmt.Fprint(stdout, generalHelpText)
		return 1
	}
}

func runCompletion(opts *cliOptions, stdout, stderr io.Writer) int {
	if len(opts.Tokens) == 0 {
		writeError(stderr, "completion requires a shell (bash, zsh, or fish)")
		return 1
	}
	if len(opts.Tokens) > 1 {
		writeError(stderr, "completion accepts exactly one shell argument (bash, zsh, or fish)")
		return 1
	}

	shell := strings.ToLower(strings.TrimSpace(opts.Tokens[0]))
	grammar, err := LoadGrammar(opts.GrammarPath)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	script, err := GenerateCompletionScript(shell, grammar)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	if !strings.HasSuffix(script, "\n") {
		script += "\n"
	}
	if err := writeOutput(opts.OutputPath, []byte(script), stdout); err != nil {
		writeError(stderr, err.Error())
		return 1
	}
	return 0
}

func renderTokensHelp(w io.Writer, grammar *Grammar) {
	fmt.Fprintln(w, "STATIC PROMPTS")
	staticNames := make([]string, 0, len(grammar.Static.Profiles))
	for name := range grammar.Static.Profiles {
		staticNames = append(staticNames, name)
	}
	sort.Strings(staticNames)
	if len(staticNames) == 0 {
		fmt.Fprintln(w, "  (none)")
	} else {
		for _, name := range staticNames {
			desc := strings.TrimSpace(grammar.StaticPromptDescription(name))
			if desc == "" {
				desc = "(no description)"
			}
			fmt.Fprintf(w, "  - %s: %s\n", name, desc)
		}
	}

	fmt.Fprintln(w, "\nCONTRACT AXES")
	axisNames := make([]string, 0, len(grammar.Axes.Definitions))
	for axis := range grammar.Axes.Definitions {
		axisNames = append(axisNames, axis)
	}
	sort.Strings(axisNames)
	if len(axisNames) == 0 {
		fmt.Fprintln(w, "  (none)")
	} else {
		for _, axis := range axisNames {
			tokenSet := make(map[string]struct{})
			for token := range grammar.Axes.Definitions[axis] {
				tokenSet[token] = struct{}{}
			}
			if list := grammar.Axes.ListTokens[axis]; len(list) > 0 {
				for _, token := range list {
					tokenSet[token] = struct{}{}
				}
			}
			tokens := make([]string, 0, len(tokenSet))
			for token := range tokenSet {
				tokens = append(tokens, token)
			}
			sort.Strings(tokens)
			fmt.Fprintf(w, "  %s:\n", axis)
			for _, token := range tokens {
				desc := strings.TrimSpace(grammar.AxisDescription(axis, token))
				if desc == "" {
					fmt.Fprintf(w, "    • %s\n", token)
				} else {
					fmt.Fprintf(w, "    • %s: %s\n", token, desc)
				}
			}
		}
	}

	fmt.Fprintln(w, "\nPERSONA PRESETS")
	presetNames := make([]string, 0, len(grammar.Persona.Presets))
	for name := range grammar.Persona.Presets {
		presetNames = append(presetNames, name)
	}
	sort.Strings(presetNames)
	if len(presetNames) == 0 {
		fmt.Fprintln(w, "  (none)")
	} else {
		for _, name := range presetNames {
			preset := grammar.Persona.Presets[name]
			label := strings.TrimSpace(preset.Label)
			if label == "" {
				label = name
			}
			fmt.Fprintf(w, "  - %s: %s\n", name, label)
		}
	}

	fmt.Fprintln(w, "\nPERSONA AXES")
	personaAxes := make([]string, 0, len(grammar.Persona.Axes))
	for axis := range grammar.Persona.Axes {
		personaAxes = append(personaAxes, axis)
	}
	sort.Strings(personaAxes)
	if len(personaAxes) == 0 {
		fmt.Fprintln(w, "  (none)")
	} else {
		for _, axis := range personaAxes {
			tokens := append([]string(nil), grammar.Persona.Axes[axis]...)
			sort.Strings(tokens)
			fmt.Fprintf(w, "  %s:\n", axis)
			for _, token := range tokens {
				desc := strings.TrimSpace(grammar.PersonaDescription(axis, token))
				if desc == "" {
					fmt.Fprintf(w, "    • %s\n", token)
				} else {
					fmt.Fprintf(w, "    • %s: %s\n", token, desc)
				}
			}
		}
	}

	if intents, ok := grammar.Persona.Intent.AxisTokens["intent"]; ok && len(intents) > 0 {
		tokens := append([]string(nil), intents...)
		sort.Strings(tokens)
		fmt.Fprintln(w, "\nPERSONA INTENTS")
		for _, token := range tokens {
			desc := strings.TrimSpace(grammar.PersonaDescription("intent", token))
			if desc == "" {
				fmt.Fprintf(w, "  • %s\n", token)
			} else {
				fmt.Fprintf(w, "  • %s: %s\n", token, desc)
			}
		}
	}

	fmt.Fprintln(w, "\nMulti-word tokens (e.g., \"fly rog\") should be supplied exactly as listed above.")
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

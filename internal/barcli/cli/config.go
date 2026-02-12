package cli

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

// Config represents the parsed CLI state consumed by the bar command entry points.
type Config struct {
	Command       string
	Tokens        []string
	Prompt        string
	Subject       string
	Addendum      string
	InputPath     string
	OutputPath    string
	JSON          bool
	GrammarPath   string
	Force         bool
	Help          bool
	Version       bool
	FixturePath   string
	FixtureWidth  int
	FixtureHeight int
	NoAltScreen   bool
	NoClipboard   bool
	EnvAllowlist  []string

	// Shuffle-specific flags
	Seed    int64
	Include []string
	Exclude []string
	Fill    float64

	// install-skills specific flags
	Location string
	DryRun   bool

	// help llm specific flags
	Section string
	Compact bool

	// Plain strips decorations (headers, bullets, descriptions) from token
	// listings, emitting one slug per line for piping to grep/fzf.
	Plain bool

	// NoInput prevents interactive prompting; TUI commands exit with guidance.
	NoInput bool

	// InitialCommand seeds the Run Command field in bar tui2 at launch time.
	InitialCommand string
}

// Parse converts argv-like input into a Config.
func Parse(args []string) (*Config, error) {
	cfg := &Config{Fill: 0.5} // default fill probability
	tokens := make([]string, 0, len(args))

	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch {
		case arg == "--prompt", strings.HasPrefix(arg, "--prompt="):
			return nil, fmt.Errorf("--prompt flag has been removed.\n\nUse --subject to provide content for the LLM to act on,\nor --addendum to add clarification to the task.")
		case arg == "--subject":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--subject requires a value")
			}
			cfg.Subject = args[i]
		case strings.HasPrefix(arg, "--subject="):
			cfg.Subject = strings.TrimPrefix(arg, "--subject=")
		case arg == "--addendum":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--addendum requires a value")
			}
			cfg.Addendum = args[i]
		case strings.HasPrefix(arg, "--addendum="):
			cfg.Addendum = strings.TrimPrefix(arg, "--addendum=")
		case arg == "--input":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--input requires a path")
			}
			cfg.InputPath = args[i]
		case strings.HasPrefix(arg, "--input="):
			cfg.InputPath = strings.TrimPrefix(arg, "--input=")
		case arg == "--output" || arg == "-o":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("%s requires a path", arg)
			}
			cfg.OutputPath = args[i]
		case strings.HasPrefix(arg, "--output="):
			cfg.OutputPath = strings.TrimPrefix(arg, "--output=")
		case arg == "--json":
			cfg.JSON = true
		case arg == "--grammar":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--grammar requires a path")
			}
			cfg.GrammarPath = args[i]
		case strings.HasPrefix(arg, "--grammar="):
			cfg.GrammarPath = strings.TrimPrefix(arg, "--grammar=")
		case arg == "--fixture":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--fixture requires a path")
			}
			cfg.FixturePath = args[i]
		case strings.HasPrefix(arg, "--fixture="):
			cfg.FixturePath = strings.TrimPrefix(arg, "--fixture=")
		case arg == "--fixture-width":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--fixture-width requires a value")
			}
			width, err := strconv.Atoi(args[i])
			if err != nil || width <= 0 {
				return nil, fmt.Errorf("--fixture-width requires a positive integer")
			}
			cfg.FixtureWidth = width
		case strings.HasPrefix(arg, "--fixture-width="):
			value := strings.TrimPrefix(arg, "--fixture-width=")
			width, err := strconv.Atoi(value)
			if err != nil || width <= 0 {
				return nil, fmt.Errorf("--fixture-width requires a positive integer")
			}
			cfg.FixtureWidth = width
		case arg == "--width":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--width requires a value")
			}
			width, err := strconv.Atoi(args[i])
			if err != nil || width <= 0 {
				return nil, fmt.Errorf("--width requires a positive integer")
			}
			cfg.FixtureWidth = width
		case strings.HasPrefix(arg, "--width="):
			value := strings.TrimPrefix(arg, "--width=")
			width, err := strconv.Atoi(value)
			if err != nil || width <= 0 {
				return nil, fmt.Errorf("--width requires a positive integer")
			}
			cfg.FixtureWidth = width
		case arg == "--fixture-height":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--fixture-height requires a value")
			}
			height, err := strconv.Atoi(args[i])
			if err != nil || height <= 0 {
				return nil, fmt.Errorf("--fixture-height requires a positive integer")
			}
			cfg.FixtureHeight = height
		case strings.HasPrefix(arg, "--fixture-height="):
			value := strings.TrimPrefix(arg, "--fixture-height=")
			height, err := strconv.Atoi(value)
			if err != nil || height <= 0 {
				return nil, fmt.Errorf("--fixture-height requires a positive integer")
			}
			cfg.FixtureHeight = height
		case arg == "--height":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--height requires a value")
			}
			height, err := strconv.Atoi(args[i])
			if err != nil || height <= 0 {
				return nil, fmt.Errorf("--height requires a positive integer")
			}
			cfg.FixtureHeight = height
		case strings.HasPrefix(arg, "--height="):
			value := strings.TrimPrefix(arg, "--height=")
			height, err := strconv.Atoi(value)
			if err != nil || height <= 0 {
				return nil, fmt.Errorf("--height requires a positive integer")
			}
			cfg.FixtureHeight = height
		case arg == "--no-alt-screen":
			cfg.NoAltScreen = true
		case arg == "--no-clipboard":
			cfg.NoClipboard = true
		case arg == "--env":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--env requires a variable name")
			}
			name := strings.TrimSpace(args[i])
			if name == "" {
				return nil, fmt.Errorf("--env requires a non-empty variable name")
			}
			cfg.EnvAllowlist = appendEnvOnce(cfg.EnvAllowlist, name)
		case strings.HasPrefix(arg, "--env="):
			name := strings.TrimSpace(strings.TrimPrefix(arg, "--env="))
			if name == "" {
				return nil, fmt.Errorf("--env requires a non-empty variable name")
			}
			cfg.EnvAllowlist = appendEnvOnce(cfg.EnvAllowlist, name)
		case arg == "--force":
			cfg.Force = true
		case arg == "--help" || arg == "-h":
			cfg.Help = true
		case arg == "--version" || arg == "-v":
			cfg.Version = true
		case arg == "--location":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--location requires a path")
			}
			cfg.Location = args[i]
		case strings.HasPrefix(arg, "--location="):
			cfg.Location = strings.TrimPrefix(arg, "--location=")
		case arg == "--dry-run":
			cfg.DryRun = true
		case arg == "--seed":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--seed requires a value")
			}
			seed, err := strconv.ParseInt(args[i], 10, 64)
			if err != nil {
				return nil, fmt.Errorf("--seed requires an integer: %v", err)
			}
			cfg.Seed = seed
		case strings.HasPrefix(arg, "--seed="):
			value := strings.TrimPrefix(arg, "--seed=")
			seed, err := strconv.ParseInt(value, 10, 64)
			if err != nil {
				return nil, fmt.Errorf("--seed requires an integer: %v", err)
			}
			cfg.Seed = seed
		case arg == "--include":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--include requires a value")
			}
			cfg.Include = parseCSV(args[i])
		case strings.HasPrefix(arg, "--include="):
			cfg.Include = parseCSV(strings.TrimPrefix(arg, "--include="))
		case arg == "--exclude":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--exclude requires a value")
			}
			cfg.Exclude = parseCSV(args[i])
		case strings.HasPrefix(arg, "--exclude="):
			cfg.Exclude = parseCSV(strings.TrimPrefix(arg, "--exclude="))
		case arg == "--fill":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--fill requires a value")
			}
			fill, err := strconv.ParseFloat(args[i], 64)
			if err != nil || fill < 0 || fill > 1 {
				return nil, fmt.Errorf("--fill requires a value between 0.0 and 1.0")
			}
			cfg.Fill = fill
		case strings.HasPrefix(arg, "--fill="):
			value := strings.TrimPrefix(arg, "--fill=")
			fill, err := strconv.ParseFloat(value, 64)
			if err != nil || fill < 0 || fill > 1 {
				return nil, fmt.Errorf("--fill requires a value between 0.0 and 1.0")
			}
			cfg.Fill = fill
		case arg == "--section":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--section requires a section name")
			}
			cfg.Section = args[i]
		case strings.HasPrefix(arg, "--section="):
			cfg.Section = strings.TrimPrefix(arg, "--section=")
		case arg == "--compact":
			cfg.Compact = true
		case arg == "--plain":
			cfg.Plain = true
		case arg == "--no-input":
			cfg.NoInput = true
		case arg == "--command", arg == "--cmd":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("%s requires a value", arg)
			}
			cfg.InitialCommand = args[i]
		case strings.HasPrefix(arg, "--command="):
			cfg.InitialCommand = strings.TrimPrefix(arg, "--command=")
		case strings.HasPrefix(arg, "--cmd="):
			cfg.InitialCommand = strings.TrimPrefix(arg, "--cmd=")
		case strings.HasPrefix(arg, "--"):
			return nil, fmt.Errorf("unknown flag %s", arg)
		default:
			if cfg.Command == "" {
				cfg.Command = arg
			} else {
				tokens = append(tokens, arg)
			}
		}
	}

	if cfg.Command == "" && !cfg.Version {
		return nil, fmt.Errorf("usage: bar [build|shuffle|help|completion|preset|tui|tui2|install-skills]")
	}
	if cfg.Subject != "" && cfg.InputPath != "" {
		return nil, fmt.Errorf("--subject and --input cannot be used together")
	}

	cfg.Tokens = tokens
	return cfg, nil
}

// ResolveEnvValues returns environment variables allowed by the config and any that
// were requested but are missing from the current process environment.
func (cfg *Config) ResolveEnvValues() (map[string]string, []string) {
	envValues := make(map[string]string)
	missing := make([]string, 0, len(cfg.EnvAllowlist))
	for _, raw := range cfg.EnvAllowlist {
		name := strings.TrimSpace(raw)
		if name == "" {
			continue
		}
		if _, exists := envValues[name]; exists {
			continue
		}
		if value, ok := os.LookupEnv(name); ok {
			envValues[name] = value
		} else {
			missing = append(missing, name)
		}
	}
	return envValues, missing
}

func appendEnvOnce(list []string, name string) []string {
	for _, existing := range list {
		if existing == name {
			return list
		}
	}
	return append(list, name)
}

func parseCSV(value string) []string {
	parts := strings.Split(value, ",")
	result := make([]string, 0, len(parts))
	for _, part := range parts {
		trimmed := strings.TrimSpace(part)
		if trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

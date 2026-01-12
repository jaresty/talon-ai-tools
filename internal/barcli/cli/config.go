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
	InputPath     string
	OutputPath    string
	JSON          bool
	GrammarPath   string
	Force         bool
	FixturePath   string
	FixtureWidth  int
	FixtureHeight int
	NoAltScreen   bool
	NoClipboard   bool
	EnvAllowlist  []string
}

// Parse converts argv-like input into a Config.
func Parse(args []string) (*Config, error) {
	cfg := &Config{}
	tokens := make([]string, 0, len(args))

	for i := 0; i < len(args); i++ {
		arg := args[i]
		switch {
		case arg == "--prompt":
			i++
			if i >= len(args) {
				return nil, fmt.Errorf("--prompt requires a value")
			}
			cfg.Prompt = args[i]
		case strings.HasPrefix(arg, "--prompt="):
			cfg.Prompt = strings.TrimPrefix(arg, "--prompt=")
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

	if cfg.Command == "" {
		return nil, fmt.Errorf("usage: bar [build|help|completion|preset|tui]")
	}
	if cfg.Prompt != "" && cfg.InputPath != "" {
		return nil, fmt.Errorf("--prompt and --input cannot be used together")
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

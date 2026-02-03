package barcli

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"github.com/talonvoice/talon-ai-tools/internal/barcli/cli"
	"github.com/talonvoice/talon-ai-tools/internal/updater"
)

const (
	buildUsage = "usage: bar build [tokens...] [options]"
	topUsage   = "usage: bar [build|shuffle|help|completion|preset|tui|tui2]"
)

// barVersion holds the current version of bar, set by main package
var barVersion = "dev"

// updateClient is the GitHub client for update checks (can be overridden for testing)
var updateClient updater.GitHubClient

// SetVersion sets the bar version (called from main package)
func SetVersion(version string) {
	barVersion = version
}

// SetUpdateClient sets the update client (used for testing)
func SetUpdateClient(client updater.GitHubClient) {
	if client == nil {
		updateClient = updater.NewGitHubClient()
	} else {
		updateClient = client
	}
}

func init() {
	// Initialize default GitHub client if not already set (e.g., by tests)
	if updateClient == nil {
		updateClient = updater.NewGitHubClient()
	}
}

var generalHelpText = strings.TrimSpace(`USAGE
  bar build <tokens>... [--prompt TEXT|--input FILE] [--output FILE] [--json]
  cat prompt.txt | bar build todo focus steps fog

  bar shuffle [--prompt TEXT|--input FILE] [--output FILE] [--json]
              [--seed N] [--include CATS] [--exclude CATS] [--fill 0.0-1.0]

  bar help
  bar help tokens [section...] [--grammar PATH]
  bar tui [tokens...] [--grammar PATH] [--fixture PATH] [--fixture-width N|--width N] [--fixture-height N|--height N] [--no-alt-screen] [--no-clipboard] [--env NAME]...
 
   bar completion <shell> [--grammar PATH] [--output FILE]
      (shell = bash | zsh | fish)
 
    bar preset save <name> [--force]

   bar preset list
   bar preset show <name> [--json]
   bar preset use <name> [--json]
   bar preset delete <name> --force
 
    The CLI ships with an embedded prompt grammar. Use --grammar or
     BAR_GRAMMAR_PATH to point at alternate payloads for testing.
     Completion suggestions include the token category and a short description
     so shells can display richer context.
 
  TOKEN ORDER (SHORTHAND)



  1. Static prompt          (0..1 tokens, default: open-ended)
  2. Completeness           (0..1)
  3. Scope                  (0..2)
  4. Method                 (0..3)
  5. Form                   (0..1)
  6. Channel                (0..1)
  7. Directional            (0..1)
  8. Persona hints / preset (voice, audience, tone, intent, persona=<preset>)

  After the first key=value override, *all* remaining tokens must be key=value.
  Enter tokens the way they appear in "bar help tokens": single words stay the
  same (for example "todo", "focus"), while multi-word entries use dashed slugs
  such as "as-teacher" or "fly-rog". Label-form tokens (for example "as teacher")
  fail with an error that points to the slug. Key=value overrides accept canonical
  values like "scope=focus" as well as slug equivalents such as "directional=fly-rog".
  Use shell quotes when needed; completions list every value for convenience.
 
  QUICK NAVIGATION
 
    Use the skip sentinel "//next" to fast-forward persona/static stages:
      //next            Skip remaining persona hints and show static prompts.
      //next:<stage>    Skip the named stage (static, scope, method, etc.).
    Skip tokens do not appear in "bar build" output—they only influence completion ordering.
 
  Sections accepted by "bar help tokens":

    static            Show only static prompts (slug + canonical hints)
    axes              Show all contract axes (slug + canonical hints)
    completeness      Show only completeness axis tokens
    scope             Show only scope axis tokens
    method            Show only method axis tokens
    form              Show only form axis tokens
    channel           Show only channel axis tokens
    directional       Show only directional axis tokens
    persona           Show persona presets and persona axes
    persona-presets   Show only persona presets
    persona-axes      Show only persona axes
    persona-intents   Show persona intents (slug + spoken hints)

 COMMANDS

  build        Construct a prompt recipe from shorthand tokens or key=value overrides.
                 Accepts input via --prompt, --input, or STDIN (piped).
  shuffle      Generate a random prompt by selecting tokens from available categories.
                 Use --seed for reproducible results, --include/--exclude to control categories,
                 and --fill to adjust inclusion probability (default 0.5).
    help         Show this message.
    help tokens  List available static prompts, contract axes, persona presets, and multi-word tokens
                 using the exported prompt grammar.
    tui          Launch the Bubble Tea prompt editor to capture subject text and preview recipes.
                 Use --fixture PATH to emit a deterministic transcript for smoke testing and
                 --no-alt-screen to keep the TUI in the primary terminal buffer.
                 --no-clipboard to disable system clipboard calls (useful for headless testing).
                  --env NAME (repeatable) to pass specific environment variables to subprocesses.
    completion   Emit shell completion scripts (bash, zsh, fish) informed by the exported grammar.
    preset       Manage cached build presets (save/list/show/use/delete) derived from the last

                 successful "bar build" invocation.
                 Use "bar preset use <name>" with --prompt/--input or piped text to rebuild
                 the recipe against fresh subject content.
 
 
  TOPICS & EXAMPLES


  List available tokens:           bar help tokens
  List only static prompts:        bar help tokens static
  List persona sections:           bar help tokens persona persona-intents
  Emit JSON for automation:        bar build --json todo focus steps fog
  Supply prompt content:           bar build todo focus --prompt "Fix onboarding"
  Reuse a saved preset:            bar preset use daily-plan --prompt "Daily sync status"
  Skip persona stage quickly:      bar build //next todo full focus
   Mix shorthand with overrides:    bar build todo focus method=steps directional=fog
    Inspect another grammar file:    bar help tokens --grammar /path/to/grammar.json
     Generate fish completions:       bar completion fish > ~/.config/fish/completions/bar.fish




 Flags such as --grammar override the grammar JSON path when necessary.
`) + "\n\n"

// Run executes the bar CLI with the provided arguments and streams.

func Run(args []string, stdin io.Reader, stdout, stderr io.Writer) int {
	options, err := cli.Parse(args)
	if err != nil {
		writeError(stderr, err.Error())
		return 1
	}

	if options.Version {
		fmt.Fprintf(stdout, "bar version %s\n", barVersion)
		return 0
	}

	// Check for updates automatically (unless running update command itself)
	if options.Command != "update" {
		checkForUpdatesBackground(stderr)
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

	if options.Command == "preset" {
		return runPreset(options, stdin, stdout, stderr)
	}

	if options.Command == "tui" {
		return runTUI(options, stdin, stdout, stderr)
	}

	if options.Command == "tui2" {
		return runTUI2(options, stdin, stdout, stderr)
	}

	if options.Command == "shuffle" {
		return runShuffle(options, stdin, stdout, stderr)
	}

	if options.Command == "update" {
		return runUpdate(options, stdout, stderr)
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
	result.Tokens = append([]string(nil), options.Tokens...)
	result.PlainText = RenderPlainText(result)

	if err := saveLastBuild(result, options.Tokens); err != nil && !errors.Is(err, errStateDisabled) {
		fmt.Fprintf(stderr, "warning: failed to cache last build: %v\n", err)
	}

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

func runHelp(opts *cli.Config, stdout, stderr io.Writer) int {

	if len(opts.Tokens) == 0 {
		fmt.Fprint(stdout, generalHelpText)
		return 0
	}

	topic := opts.Tokens[0]
	switch topic {
	case "tokens":
		filters, filterErr := parseTokenHelpFilters(opts.Tokens[1:])
		if filterErr != nil {
			writeError(stderr, filterErr.Error())
			fmt.Fprint(stdout, generalHelpText)
			return 1
		}

		grammar, err := LoadGrammar(opts.GrammarPath)
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		renderTokensHelp(stdout, grammar, filters)
		return 0
	default:
		writeError(stderr, fmt.Sprintf("unknown help topic %q", topic))
		fmt.Fprint(stdout, generalHelpText)
		return 1
	}
}

func runCompletion(opts *cli.Config, stdout, stderr io.Writer) int {
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

func runPreset(opts *cli.Config, stdin io.Reader, stdout, stderr io.Writer) int {
	if len(opts.Tokens) == 0 {
		writeError(stderr, "preset requires a subcommand (save, list, show, use, delete)")
		fmt.Fprint(stdout, generalHelpText)
		return 1
	}

	sub := opts.Tokens[0]
	args := opts.Tokens[1:]

	switch sub {
	case "save":
		if len(args) == 0 {
			writeError(stderr, "preset save requires a name")
			return 1
		}
		build, err := loadLastBuild()
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		slug, err := savePreset(args[0], build, opts.Force)
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		fmt.Fprintf(stdout, "Saved preset %q (%s)\n", args[0], slug)
		return 0
	case "list":
		summaries, err := listPresets()
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		if len(summaries) == 0 {
			fmt.Fprintln(stdout, "No presets saved.")
			return 0
		}
		writePresetTable(stdout, summaries)
		return 0
	case "show":
		if len(args) == 0 {
			writeError(stderr, "preset show requires a name")
			return 1
		}
		preset, _, err := loadPreset(args[0])
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		if opts.JSON {
			payload, err := json.MarshalIndent(preset, "", "  ")
			if err != nil {
				writeError(stderr, err.Error())
				return 1
			}
			payload = append(payload, '\n')
			if _, err := stdout.Write(payload); err != nil {
				writeError(stderr, err.Error())
				return 1
			}
			return 0
		}
		renderPresetDetails(stdout, preset)
		return 0
	case "use":
		if len(args) == 0 {
			writeError(stderr, "preset use requires a name")
			return 1
		}
		preset, _, err := loadPreset(args[0])
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}

		grammar, loadErr := LoadGrammar(opts.GrammarPath)
		if loadErr != nil {
			writeError(stderr, loadErr.Error())
			return 1
		}

		promptBody, promptErr := readPrompt(opts, stdin)
		if promptErr != nil {
			writeError(stderr, promptErr.Error())
			return 1
		}

		result, buildErr := Build(grammar, preset.Tokens)

		if buildErr != nil {
			emitError(buildErr, opts.JSON, stdout, stderr)
			return 1
		}

		result.Subject = promptBody
		result.Tokens = append([]string(nil), preset.Tokens...)
		result.PlainText = RenderPlainText(result)

		if err := saveLastBuild(result, preset.Tokens); err != nil && !errors.Is(err, errStateDisabled) {
			fmt.Fprintf(stderr, "warning: failed to cache last build: %v\n", err)
		}

		if opts.JSON {
			payload, err := json.MarshalIndent(result, "", "  ")
			if err != nil {
				writeError(stderr, err.Error())
				return 1
			}
			payload = append(payload, '\n')
			if err := writeOutput(opts.OutputPath, payload, stdout); err != nil {
				writeError(stderr, err.Error())
				return 1
			}
			return 0
		}

		if err := writeOutput(opts.OutputPath, []byte(result.PlainText), stdout); err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		return 0
	case "delete":
		if len(args) == 0 {
			writeError(stderr, "preset delete requires a name")
			return 1
		}
		if !opts.Force {
			writeError(stderr, "preset delete requires --force confirmation")
			return 1
		}
		_, err := deletePreset(args[0], opts.Force)
		if err != nil {
			writeError(stderr, err.Error())
			return 1
		}
		fmt.Fprintf(stdout, "Deleted preset %q\n", args[0])
		return 0
	default:
		writeError(stderr, fmt.Sprintf("unknown preset subcommand %q", sub))
		fmt.Fprint(stdout, generalHelpText)
		return 1
	}
}

func runShuffle(opts *cli.Config, stdin io.Reader, stdout, stderr io.Writer) int {
	grammar, loadErr := LoadGrammar(opts.GrammarPath)
	if loadErr != nil {
		cliErr := &CLIError{Type: "io", Message: loadErr.Error()}
		emitError(cliErr, opts.JSON, stdout, stderr)
		return 1
	}

	promptBody, promptErr := readPrompt(opts, stdin)
	if promptErr != nil {
		cliErr := &CLIError{Type: "io", Message: promptErr.Error()}
		emitError(cliErr, opts.JSON, stdout, stderr)
		return 1
	}

	shuffleOpts := ShuffleOptions{
		Seed:    opts.Seed,
		Include: opts.Include,
		Exclude: opts.Exclude,
		Fill:    opts.Fill,
		Subject: promptBody,
	}

	result, shuffleErr := Shuffle(grammar, shuffleOpts)
	if shuffleErr != nil {
		emitError(shuffleErr, opts.JSON, stdout, stderr)
		return 1
	}

	if opts.JSON {
		payload, err := json.MarshalIndent(result, "", "  ")
		if err != nil {
			cliErr := &CLIError{Type: "io", Message: err.Error()}
			emitError(cliErr, opts.JSON, stdout, stderr)
			return 1
		}
		payload = append(payload, '\n')
		if err := writeOutput(opts.OutputPath, payload, stdout); err != nil {
			cliErr := &CLIError{Type: "io", Message: err.Error()}
			emitError(cliErr, opts.JSON, stdout, stderr)
			return 1
		}
		return 0
	}

	if err := writeOutput(opts.OutputPath, []byte(result.PlainText), stdout); err != nil {
		cliErr := &CLIError{Type: "io", Message: err.Error()}
		emitError(cliErr, opts.JSON, stdout, stderr)
		return 1
	}
	return 0
}

func runUpdate(opts *cli.Config, stdout, stderr io.Writer) int {
	updateHelpText := strings.TrimSpace(`
USAGE
  bar update <verb> [options]

VERBS
  check       Check for available updates to bar CLI
  install     Install the latest version or a specific version
  rollback    Revert to a previous version

OPTIONS
  --help, -h  Show this help message

EXAMPLES
  bar update check
  bar update install
  bar update rollback
`) + "\n"

	if opts.Help || len(opts.Tokens) == 0 {
		fmt.Fprint(stdout, updateHelpText)
		return 0
	}

	verb := opts.Tokens[0]
	switch verb {
	case "check":
		return runUpdateCheck(stdout, stderr)
	case "install":
		return runUpdateInstall(stdout, stderr)
	case "rollback":
		return runUpdateRollback(stdout, stderr)
	default:
		writeError(stderr, fmt.Sprintf("unknown update verb %q", verb))
		fmt.Fprint(stdout, updateHelpText)
		return 1
	}
}

func runUpdateCheck(stdout, stderr io.Writer) int {
	checker := &updater.UpdateChecker{
		Client:         updateClient,
		CurrentVersion: barVersion,
		Owner:          "talonvoice",
		Repo:           "talon-ai-tools",
	}

	ctx := context.Background()
	available, latestVersion, err := checker.CheckForUpdate(ctx)
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to check for updates: %v", err))
		return 1
	}

	if available {
		fmt.Fprintf(stdout, "A new version is available: %s (current: %s)\n", latestVersion, barVersion)
		fmt.Fprintf(stdout, "Run 'bar update install' to upgrade.\n")
	} else {
		fmt.Fprintf(stdout, "You are already on the latest version: %s\n", barVersion)
	}

	return 0
}

func runUpdateInstall(stdout, stderr io.Writer) int {
	ctx := context.Background()

	// Check for updates first
	checker := &updater.UpdateChecker{
		Client:         updateClient,
		CurrentVersion: barVersion,
		Owner:          "talonvoice",
		Repo:           "talon-ai-tools",
	}

	available, latestVersion, err := checker.CheckForUpdate(ctx)
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to check for updates: %v", err))
		return 1
	}

	if !available {
		fmt.Fprintf(stdout, "Already on the latest version: %s\n", barVersion)
		return 0
	}

	fmt.Fprintf(stdout, "Installing version %s...\n", latestVersion)

	// Get download URL for the asset
	assetName := updater.DetectPlatform()

	httpClient, ok := updateClient.(*updater.HTTPGitHubClient)
	if !ok {
		writeError(stderr, "update install requires real GitHub client")
		return 1
	}

	downloadURL, err := httpClient.GetAssetDownloadURL(ctx, "talonvoice", "talon-ai-tools", assetName)
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to get download URL: %v", err))
		return 1
	}

	// Download the artifact
	tmpDir, err := os.MkdirTemp("", "bar-update-")
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to create temp directory: %v", err))
		return 1
	}
	defer os.RemoveAll(tmpDir)

	downloadPath := filepath.Join(tmpDir, "bar-new")

	downloader := &updater.ArtifactDownloader{
		Client: httpClient.HTTPClient,
	}

	fmt.Fprintf(stdout, "Downloading %s...\n", assetName)
	if err := downloader.Download(ctx, downloadURL, downloadPath); err != nil {
		writeError(stderr, fmt.Sprintf("failed to download artifact: %v", err))
		return 1
	}

	// Get current binary path
	currentBinary, err := os.Executable()
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to determine current binary path: %v", err))
		return 1
	}

	// Install the new binary
	backupDir := filepath.Join(os.TempDir(), "bar-backups")
	installer := &updater.BinaryInstaller{
		BackupDir: backupDir,
	}

	fmt.Fprintf(stdout, "Installing new binary...\n")
	if err := installer.Install(ctx, downloadPath, currentBinary); err != nil {
		writeError(stderr, fmt.Sprintf("failed to install binary: %v", err))
		return 1
	}

	fmt.Fprintf(stdout, "Successfully updated to version %s\n", latestVersion)
	fmt.Fprintf(stdout, "Backup saved to: %s\n", backupDir)

	return 0
}

func runUpdateRollback(stdout, stderr io.Writer) int {
	ctx := context.Background()

	// Get current binary path
	currentBinary, err := os.Executable()
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to determine current binary path: %v", err))
		return 1
	}

	// Use same backup directory as install
	backupDir := filepath.Join(os.TempDir(), "bar-backups")
	installer := &updater.BinaryInstaller{
		BackupDir: backupDir,
	}

	// List available backups to show user what's available
	backups, err := installer.ListBackups()
	if err != nil {
		writeError(stderr, fmt.Sprintf("failed to list backups: %v", err))
		return 1
	}

	if len(backups) == 0 {
		writeError(stderr, "no backups available for rollback")
		fmt.Fprintf(stdout, "Run 'bar update install' first to create a backup before updating.\n")
		return 1
	}

	fmt.Fprintf(stdout, "Found %d backup(s). Rolling back to most recent backup...\n", len(backups))

	// Perform rollback
	if err := installer.Rollback(ctx, currentBinary); err != nil {
		writeError(stderr, fmt.Sprintf("failed to rollback: %v", err))
		return 1
	}

	fmt.Fprintf(stdout, "Successfully rolled back to previous version\n")
	fmt.Fprintf(stdout, "Backup directory: %s\n", backupDir)

	return 0
}

func checkForUpdatesBackground(stderr io.Writer) {
	// Skip if update client not set (e.g., in tests)
	if updateClient == nil {
		return
	}

	cache := updater.NewUpdateCache()

	// Check at most once per 24 hours
	if !cache.ShouldCheck(24 * time.Hour) {
		// Check if cached info shows an update is available
		info, err := cache.Read()
		if err == nil && info.Available {
			fmt.Fprintf(stderr, "New bar version %s available. Run 'bar update install' to upgrade.\n", info.LatestVersion)
		}
		return
	}

	// Perform update check
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	checker := &updater.UpdateChecker{
		Client:         updateClient,
		CurrentVersion: barVersion,
		Owner:          "talonvoice",
		Repo:           "talon-ai-tools",
	}

	available, latestVersion, err := checker.CheckForUpdate(ctx)
	if err != nil {
		// Silent failure - don't interrupt user's command with errors
		return
	}

	// Cache the result
	info := updater.UpdateInfo{
		Available:     available,
		LatestVersion: latestVersion,
		CheckedAt:     time.Now(),
	}
	_ = cache.Write(info) // Ignore cache write errors

	// Notify user if update is available
	if available {
		fmt.Fprintf(stderr, "New bar version %s available. Run 'bar update install' to upgrade.\n", latestVersion)
	}
}

func parseTokenHelpFilters(sections []string) (map[string]bool, error) {

	if len(sections) == 0 {
		return nil, nil
	}

	filters := make(map[string]bool)
	for _, raw := range sections {
		section := strings.ToLower(strings.TrimSpace(raw))
		if section == "" {
			continue
		}

		switch section {
		case "static":
			filters["static"] = true
		case "axes":
			filters["axes"] = true
		case "completeness", "scope", "method", "form", "channel", "directional":
			filters["axis:"+section] = true
		case "persona":
			filters["persona-presets"] = true
			filters["persona-axes"] = true
		case "persona-presets":
			filters["persona-presets"] = true
		case "persona-axes":
			filters["persona-axes"] = true
		case "persona-intents":
			filters["persona-intents"] = true
		default:
			return nil, fmt.Errorf("unknown tokens help section %q", raw)
		}
	}

	if len(filters) == 0 {
		return nil, nil
	}

	return filters, nil
}

func renderTokensHelp(w io.Writer, grammar *Grammar, filters map[string]bool) {
	shouldShow := func(key string) bool {
		if len(filters) == 0 {
			return true
		}
		return filters[key]
	}

	printed := false
	writeHeader := func(header string) {
		if printed {
			fmt.Fprintln(w)
		}
		fmt.Fprintln(w, header)
		printed = true
	}

	if shouldShow("static") {
		writeHeader("STATIC PROMPTS")
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
				display := name
				if slug := grammar.slugForToken(name); slug != "" && slug != name {
					display = fmt.Sprintf("%s (canonical: %s)", slug, name)
				}
				fmt.Fprintf(w, "  - %s: %s\n", display, desc)
			}
		}
	}

	// Check if any axis filters are present
	hasAxisFilters := false
	for key := range filters {
		if strings.HasPrefix(key, "axis:") {
			hasAxisFilters = true
			break
		}
	}

	if shouldShow("axes") || hasAxisFilters {
		// Use canonical ordering from tui_tokens.go
		orderedAxes := []string{"completeness", "scope", "method", "form", "channel", "directional"}

		// Add any additional axes from grammar that aren't in the canonical list
		seenAxes := make(map[string]bool)
		for _, axis := range orderedAxes {
			seenAxes[axis] = true
		}
		for axis := range grammar.Axes.Definitions {
			if !seenAxes[axis] {
				orderedAxes = append(orderedAxes, axis)
				seenAxes[axis] = true
			}
		}

		// Filter axes based on what should be shown
		axesToShow := make([]string, 0)
		for _, axis := range orderedAxes {
			if _, exists := grammar.Axes.Definitions[axis]; !exists {
				continue
			}
			// Show if:
			// - No filters (show all)
			// - "axes" filter is set
			// - Specific axis filter is set
			if len(filters) == 0 || filters["axes"] || filters["axis:"+axis] {
				axesToShow = append(axesToShow, axis)
			}
		}

		if len(axesToShow) > 0 {
			writeHeader("CONTRACT AXES")
		}

		if len(axesToShow) == 0 {
			if len(filters) == 0 || filters["axes"] {
				fmt.Fprintln(w, "  (none)")
			}
		} else {
			for _, axis := range axesToShow {
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
					slug := grammar.slugForToken(token)
					display := token
					if slug != "" && slug != token {
						display = fmt.Sprintf("%s (canonical: %s)", slug, token)
					}
					desc := strings.TrimSpace(grammar.AxisDescription(axis, token))
					if desc == "" {
						fmt.Fprintf(w, "    • %s\n", display)
					} else {
						fmt.Fprintf(w, "    • %s: %s\n", display, desc)
					}
				}
			}
		}
	}

	if shouldShow("persona-presets") {
		writeHeader("PERSONA PRESETS")
		presetNames := make([]string, 0, len(grammar.Persona.Presets))
		for name := range grammar.Persona.Presets {
			presetNames = append(presetNames, name)
		}
		sort.Strings(presetNames)
		if len(presetNames) == 0 {
			fmt.Fprintln(w, "  (none)")
		} else {
			readField := func(value *string) string {
				if value == nil {
					return ""
				}
				return strings.TrimSpace(*value)
			}
			for _, name := range presetNames {
				preset := grammar.Persona.Presets[name]
				label := strings.TrimSpace(preset.Label)
				if label == "" {
					label = name
				}
				slug := strings.TrimSpace(grammar.slugForToken(fmt.Sprintf("persona=%s", name)))
				spoken := readField(preset.Spoken)

				displayParts := []string{fmt.Sprintf("persona %s", name)}
				if slug != "" {
					displayParts = append(displayParts, fmt.Sprintf("slug: %s", slug))
				}
				if spoken != "" {
					displayParts = append(displayParts, fmt.Sprintf("say: persona %s", spoken))
				}

				fmt.Fprintf(w, "  - %s — %s\n", strings.Join(displayParts, " | "), label)

				stanceBits := make([]string, 0, 3)
				if voice := readField(preset.Voice); voice != "" {
					stanceBits = append(stanceBits, fmt.Sprintf("voice: %s", voice))
				}
				if audience := readField(preset.Audience); audience != "" {
					stanceBits = append(stanceBits, fmt.Sprintf("audience: %s", audience))
				}
				if tone := readField(preset.Tone); tone != "" {
					stanceBits = append(stanceBits, fmt.Sprintf("tone: %s", tone))
				}
				if len(stanceBits) > 0 {
					fmt.Fprintf(w, "    • %s\n", strings.Join(stanceBits, " · "))
				}
			}
		}
	}

	if shouldShow("persona-axes") {
		writeHeader("PERSONA AXES (voice, audience, tone)")
		allowedPersonaAxes := map[string]bool{"voice": true, "audience": true, "tone": true}
		personaAxes := make([]string, 0, len(grammar.Persona.Axes))
		for axis := range grammar.Persona.Axes {
			axisKey := strings.ToLower(strings.TrimSpace(axis))
			if !allowedPersonaAxes[axisKey] {
				continue
			}
			personaAxes = append(personaAxes, axisKey)
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
					display := strings.TrimSpace(token)
					slug := strings.TrimSpace(grammar.slugForToken(token))
					displayParts := []string{display}
					if slug != "" && !strings.EqualFold(slug, display) {
						displayParts = append(displayParts, fmt.Sprintf("slug: %s", slug))
					}
					desc := strings.TrimSpace(grammar.PersonaDescription(axis, token))
					joined := strings.Join(displayParts, " | ")
					if desc == "" {
						fmt.Fprintf(w, "    • %s\n", joined)
					} else {
						fmt.Fprintf(w, "    • %s: %s\n", joined, desc)
					}
				}
			}
		}
	}

	if shouldShow("persona-intents") {
		intents, ok := grammar.Persona.Intent.AxisTokens["intent"]
		if !ok {
			intents = nil
		}
		intentTokens := append([]string(nil), intents...)
		sort.Strings(intentTokens)
		writeHeader("PERSONA INTENTS (why)")
		if len(intentTokens) == 0 {
			fmt.Fprintln(w, "  (none)")
		} else {
			for _, token := range intentTokens {
				display := strings.TrimSpace(token)
				slug := strings.TrimSpace(grammar.slugForToken(token))
				displayParts := []string{display}
				if slug != "" && !strings.EqualFold(slug, display) {
					displayParts = append(displayParts, fmt.Sprintf("slug: %s", slug))
				}
				desc := strings.TrimSpace(grammar.PersonaDescription("intent", token))
				joined := strings.Join(displayParts, " | ")
				if desc == "" {
					fmt.Fprintf(w, "  • %s\n", joined)
				} else {
					fmt.Fprintf(w, "  • %s: %s\n", joined, desc)
				}
			}
		}
	}

	if printed {
		fmt.Fprintln(w)
	}
	fmt.Fprintln(w, "Multi-word tokens (e.g., \"fly rog\") should be supplied exactly as listed above.")
}

func readPrompt(opts *cli.Config, stdin io.Reader) (string, error) {
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

# Talon-AI-Tools

**Control large language models and AI tools through voice commands using the [Talon Voice](https://talon.wiki) dictation engine.**

This functionality is especially helpful for users who:

- want to quickly edit text and fix dictation errors
- code by voice using tools like [Cursorless](https://www.cursorless.org/)
- have health issues affecting their hands and want to reduce keyboard use
- want to speed up their workflow and use AI commands across the entire desktop

**Prompts and extends the following tools:**

- Github Copilot
- OpenAI API (with any GPT model) for text generation and processing
  - Any OpenAI compatible model endpoint can be used (Azure, local llamafiles, etc)
- OpenAI API for image generation and vision

## Help and Setup:

1. Download or `git clone` this repo into your Talon user directory.
1. [Obtain an OpenAI API key](https://platform.openai.com/signup).

1. Create a Python file anywhere in your Talon user directory.
1. Set the key environment variable within the Python file

> [!CAUTION]
> Make sure you do not push the key to a public repo!

```python
# Example of setting the environment variable
import os

os.environ["OPENAI_API_KEY"] = "YOUR-KEY-HERE"
```

5. See the [GPT](./GPT/readme.md) or [Copilot](./copilot/README.md) folders for usage examples.

> [!NOTE]
> You can use this repo without an OpenAI key by [customizing the endpoint url](./GPT/readme.md#configuration) to be your preferred model.
>
> You can also exclusively use this repo with just [Copilot](./copilot/README.md) if you do not need LLM integration

### Multiple providers (ADR 047)

- Switch providers by voice: `model provider list`, `model provider use <name>`, `model provider next/previous`, `model provider status`.
- Bundled providers: `openai`, `gemini`. Configure tokens via Talon settings (`user.model_provider_token_openai`, `user.model_provider_token_gemini`) or env (`OPENAI_API_KEY` / `GEMINI_API_KEY`). Add more via `user.model_provider_extra` in `talon-ai-settings.talon`.
- Switch provider + model together: `model provider use <name> model <model-id>` persists the model for built-ins (OpenAI uses `user.openai_model`; Gemini uses `user.model_provider_model_gemini`) and applies an in-session override for custom providers. Spoken model aliases are supported: Gemini via `user.model_provider_model_aliases_gemini` (e.g., `one five pro`), OpenAI via `user.model_provider_model_aliases_openai` (e.g., `four o`).
- Provider list/status render in a canvas with reachability hints (enable probes with `user.model_provider_probe = 1`).

### In-Talon help surfaces

- `model help hub` – central hub linking quick help, patterns, suggestions, history, docs. Button voice hints use the orchestrator stance commands (for example `persona mentor voice`, `intent decide display`) to stay aligned with Concordance.
- `model quick help` – grammar/axes cheat sheet; `model quick help patterns/suggestions/history/docs` for nearby surfaces.
- `model patterns` / `model pattern menu <prompt>` – curated recipes and per-prompt presets.
- `model suggest` / `model suggestions` – prompt recipe suggestions picker.
- `model history drawer` / `model history list` – recent requests/responses.
- `model history save exchange` – save the latest history entry’s prompt/response to a file; use `model history copy last save` / `model history open last save` / `model history show last save` to retrieve/copy/open the most recent save path. Requires a directional lens (fog/fig/dig/ong/rog/bog/jog) on the history entry; otherwise the save is rejected to keep history navigation aligned. The history drawer shows inline guidance when empty and accepts `s` to save the latest exchange and refresh the list.

### Quickstart Video

[![Talon-AI-Tools Quickstart](./.docs/video_thumbnail.jpg)](https://www.youtube.com/watch?v=FctiTs6D2tM "Talon-AI-Tools Quickstart")

## Release Notes

- **2026-01-09** – `bar tui` now supports a fixture-driven snapshot harness (`--fixture`, `--no-alt-screen`) with README instructions and a committed smoke transcript so pilots and CI runs capture deterministic previews.
- **2026-01-09** – CLI completion surfaces include `//next` skip sentinels with docs, help text, and examples (`bar help`, README, and docs quickstart) so you can jump persona/static stages without hunting for options.
- **2026-01-08** – Portable CLI completions now insert slug tokens (for example, `as-teacher`). The CLI no longer accepts the legacy human-readable labels; supply slugs directly to keep recipes predictable.

## Development

- Tests run with the lightweight Talon stub harness under `tests/`; the helper `bootstrap.py` wires the stubs, so simply run `python3 -m unittest discover -s tests` or `make test`.
- Axis catalog guardrails: `make axis-guardrails` (catalog validate + cheat sheet; skips on-disk list files), `make axis-catalog-validate` and `make axis-cheatsheet` as individual primitives; `make axis-guardrails-ci` is the faster catalog-only set; `make ci-guardrails` adds key parity tests; `make guardrails` is the CI guardrail alias; `make axis-guardrails-test` runs the full guardrail suite. Axis/static prompt .talon-lists are not tracked; `make talon-lists`/`make talon-lists-check` are optional helpers if you need to export or drift-check local list files. `make help` lists the available guardrail targets. For ad-hoc validation of a user-extensible Talon lists directory, use `python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists` (catalog-only by default via `--skip-list-files`; pass `--no-skip-list-files` with `--lists-dir` to enforce list checks—for example, `python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists --no-skip-list-files`). If you actually need list files locally, regenerate them with `make talon-lists` or `python3 scripts/tools/generate_talon_lists.py --out-dir <dir>` before running enforced list checks.
- Persona/intent metadata flows through `lib/personaOrchestrator.get_persona_intent_orchestrator()`. When you add tokens or presets in `lib/personaConfig.py`, reset the orchestrator cache (`reset_persona_intent_orchestrator_cache()`) and update any façade consumers/tests so help surfaces stay in sync.
- History guardrails: `make request-history-guardrails` exports telemetry summaries and `make request-history-guardrails-fast` offers a quicker snapshot. Each helper runs locally only (manual telemetry access required), so CI workflows omit them. Persona and drop-reason summaries are now sourced from `historyLifecycle.persona_*` helpers, so guardrail output matches in-Talon history surfaces.
- Before opening a PR, run `make guardrails` (or `make axis-guardrails-test` for the full suite) to catch catalog/list drift. In CI, call the appropriate `make` target directly (for example, `make guardrails` or `make axis-guardrails-ci`) or embed the commands you rely on.
- `tests/stubs/talon/__init__.py` mirrors the Talon APIs required by the repo; add new behaviors there when extending commands.
- GPT orchestration code should flow through `lib/promptSession.PromptSession` rather than manually mutating `GPTState`. The typical pattern is to create a session, call `prepare_prompt(...)`, optionally `begin(reuse_existing=True)` when reusing an in-flight request, then `execute()`.
- When adding new actions, keep the `UserActions` methods thin, prefer unit tests similar to `tests/test_gpt_actions.py`, and verify they assert the prompt session interactions you expect.

### Portable prompt grammar CLI

The `bar` CLI consumes the exported prompt grammar so you can assemble recipes outside Talon.

1. Regenerate the grammar when prompts, axes, or personas change:
   ```bash
   python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json
   ```
2. Install the CLI with Go (`go install github.com/talonvoice/talon-ai-tools/cmd/bar@latest`) or use the `scripts/install-bar.sh` helper to fetch a release binary.
   ```bash
   curl -fsSL https://raw.githubusercontent.com/jaresty/talon-ai-tools/main/scripts/install-bar.sh | bash
   ```
3. Explore the grammar and build recipes:
   ```bash
   bar help tokens                      # list prompts, axes, persona presets
   bar build todo focus steps fog --json
   echo "Fix onboarding" | bar build todo focus steps fog persona=facilitator intent=coach
   ```
4. Capture reusable builds with presets (subjects are **not** stored, so always supply fresh text when reusing):
   ```bash
   bar build todo focus steps fog persona=coach intent=teach
   bar preset save daily-standup               # writes ~/.config/bar/presets/daily-standup.json
   bar preset list                             # shows saved recipes and persona axes
    bar preset use daily-standup                # rebuilds using saved tokens; supply prompt via --prompt/--input/STDIN

   bar preset show daily-standup --json        # inspect metadata as JSON
   bar preset delete daily-standup --force     # remove a preset
   ```
   Cached state lives in `~/.config/bar/state/last_build.json` (override with `BAR_CONFIG_DIR`). Set `BAR_DISABLE_STATE=1` to skip persistence entirely.
5. If you add completions or installer changes, keep `bar help` and `bar completion` outputs aligned with `build/prompt-grammar.json`. The metadata-aware completion backend now emits tab-delimited suggestions (`value\tcategory\tdescription`) so shells can show axis information; older scripts simply ignore the extra columns.

   > [!NOTE]
   > CLI suggestions now insert slug tokens such as `as-teacher`. Shorthand must use slugs, but canonical key=value overrides remain valid (for example `scope=focus`). Update any scripts or shell history accordingly.
 
#### Bubble Tea prompt editor (`bar tui`)

Launch the interactive TUI to preview recipes while editing subjects:

```bash
bar tui todo focus steps                 # starts the TUI with shorthand tokens
```

- By default the program enables the terminal alt screen so your original prompt buffer is restored when you exit. Pass `--no-alt-screen` to stay in the primary screen (useful when capturing transcripts inside CI or when your terminal does not support alt screen mode).
- Supply a grammar file with `--grammar PATH` if you need to exercise alternate prompt bundles (defaults to the embedded grammar).
- Repeat `--env NAME` to pass specific environment variables (for example API keys) to the subprocess allowlist. Inside the TUI, press Tab again to focus the allowlist, use Up/Down to choose a variable, `Ctrl+E` to toggle it, `Ctrl+A` to re-enable all entries, and `Ctrl+X` to clear the allowlist entirely.

The TUI supports a deterministic snapshot harness for CI and manual smoke checks. Use the bundled fixture to verify the preview, layout, and output formatting without entering the interactive loop:

```bash
bar tui --fixture "$(dirname $(command -v bar))/bar-tui_smoke.json" --no-alt-screen
```

The fixture loader accepts the following fields:

- `tokens` – shorthand tokens (replaces CLI tokens when present)
- `subject` – subject text to inject in the snapshot
- `expected_preview` / `expected_view` – exact strings to match (set either field to an empty string to skip the assertion)
- `expect_view_contains` – optional list of substrings that must appear in the rendered view

Snapshot runs write the rendered view to STDOUT, perform all assertions, and exit without switching the terminal buffer. They pair nicely with `go test ./cmd/bar/...` which now includes `TestTUIFixtureEmitsSnapshot` to guard the fixture.

When running the interactive editor, keep these shortcuts close by:

- `Tab` cycles focus between the subject input, token controls, command input, and the environment allowlist.
- `Ctrl+L` loads subject text from the clipboard.
- `Ctrl+O` copies the rendered preview to the clipboard.
- `Ctrl+B` copies the current `bar build` command (subject + tokens) to the clipboard so you can drop straight back into scripts.
- `Ctrl+R` pipes the current preview into the configured shell command.
- `Ctrl+P` opens the token palette so you can browse or reset selections without leaving the session; search for “copy command”, press `Enter` to copy the CLI and close the palette, and press `Ctrl+W` while the palette is open to clear the current filter instantly.
- Within the token controls, use Left/Right to change categories, Up/Down to browse options, `Enter`/`Space` to toggle, `Delete` to remove the highlighted token, `Ctrl+W` to clear any active palette filter, and `Ctrl+Z` to undo the most recent change.
- `Ctrl+Y` replaces the subject with the most recent command stdout.
- `?` toggles the in-app shortcut overlay so you can review controls without leaving the session.
- `Ctrl+S` toggles the preset pane; inside it, use `Ctrl+N` to save the current tokens, `Delete` to remove the focused preset, and `Ctrl+Z` to undo the most recent deletion.
- When the environment allowlist is focused, use Up/Down to move between entries, `Ctrl+E` to toggle the selection, `Ctrl+A` to re-enable all entries, and `Ctrl+X` to clear the allowlist.

For a complete pilot walkthrough (interactive usage, fixture expectations, transcript capture tips) see `docs/bubble-tea-pilot-playbook.md`.

#### Completion skip sentinel

Use the skip sentinel `//next` whenever tab completion offers a stage you want to bypass:

- `//next` by itself skips the remaining persona hints and moves directly to “What” suggestions.
- `//next:<stage>` skips the named stage (for example `//next:static` hides all static prompts, `//next:scope` hides further scope tokens). The CLI suggests valid stage names inline.
- Insert the sentinel anywhere in the shorthand sequence; the build command ignores the token, so the final recipe only contains the tokens you kept.

Pair the sentinel with normal completions to fast-forward through stages. For instance, accepting `//next` followed by `todo` and `full` yields the same build as selecting persona suggestions manually, but keeps the persona stage out of the workflow.

6. Completion guardrail (requires Go 1.21+ and Python 3.11+):
   ```bash
   make bar-completion-guard

   ```
   (equivalent manual steps: `python3 -m venv .venv && .venv/bin/python -m pip install pytest && .venv/bin/python -m pytest _tests/test_bar_completion_cli.py`)
   This pytest slice exercises `bar completion` and the hidden `bar __complete` helper so shell installers stay grammar-aligned. The target also runs automatically via `make guardrails`/`make ci-guardrails`; install Go from https://go.dev/doc/install if it is not already available.
7. Developer sanity check:
   ```bash
   python3 -m unittest _tests.test_readme_portable_cli
   ```
   This guardrail ensures the README quickstart stays in sync with the exported grammar commands.

### CI example

```yaml
  - name: Run guardrails
    run: make axis-guardrails-ci
```

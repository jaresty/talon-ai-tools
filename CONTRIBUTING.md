# Contributing

Thank you for your interest in contributing to `talon-ai-tools`. We are happy to receive new contributions. If you have any questions about contributing, feel free to ask.

## Contributing Python

- For all PRs please describe the intent of the PR and give an example of any non-trivial functionality.
- Do not use external Python dependencies with `pip install`
  - This pollutes the Talon Python interpreter and can have unintended side effects
- Prefix all actions exposed from a module with `gpt_` or another appropriate prefix to distinguish it in the global namespace
  - i.e. Write a function like `actions.user.gpt_query()` not `actions.user.query()`
- Do not expose any actions globally with talon action classes if they don't need to be called from `.talon` files
- Comment all functions with doctrings and type annotations for arguments
- Any code that is intended to be reused within the repo should be placed within the `lib/` folder
- GPT orchestration should flow through `PromptPipeline`/`PromptSession`, and new actions should add unit tests mirroring `tests/test_gpt_actions.py` to pin expected pipeline calls.
- When implementing recursive flows, use `RecursiveOrchestrator` so controller directives stay JSON-encoded and the final delegate/controller output preserves the requested format.

## Contributing Talonscript

- Talon commands should follow a grammar that is intuitive for users or mimics the grammar of existing tools like Cursorless
  - Prefix all commands with an appropriate prefix like `model` or `pilot` to make sure they aren't accidentally run
- Duplicate commands following a similar syntax should be condensed into captures or lists _only_ if it improves readability for users or significantly reduces duplicate code for maintainers
  - It is better to duplicate code to make a command explicit and readable rather than overly condense the command within a fancy talon capture.
  - The commands inside a `.talon` file, to the extent possible, should be intuitive for a new user to understand. Numerous talon lists chained together requires a user to introspect code and adds friction to discoverability.
  - It is best to use talon commands that are very expliciti, even if overly verbose, and let the user customize them if desired. Brevity risks confusion.
- Any command that requires a capture or list should include a brief inline comment above it showing an example of the command and a one line description of what it does
- If a list is needed, `.talon-list` files should be used instead of defining lists inside Python
  - This makes it easier to customize list items by overriding the `.talon-list` and not needing to fork the Python.
- Avoid any configuration pattern that requires a user to fork this repository

## TDD Enforcement: Method Tokens (ground, gate, chain, atomic)

When contributing code—whether Python, Talon, or Go—use the method tokens `ground`, `gate`, `chain`, and `atomic` to apply a TDD enforcement discipline. These tokens form a protocol for making gaps between apparent completion and actual completion visible and costly to maintain.

### The Four Tokens and Their Process

**ground 地 (Derive the enforcement process)**
Before implementing a feature or fix, derive a process that makes the gap visible. Your process must:
1. Name at least one cheap path that would produce the appearance of completion without actual correctness (e.g., "I write code without tests," or "I write tests that pass trivially").
2. For each cheap path, specify what visible evidence would distinguish genuine compliance from that shortcut.
3. Include a completion check: return to the original intent, and for each requirement, produce visible evidence that it is satisfied.

*Example:* For a Python function `parse_config()`, the cheap path is "write the function without a test." Evidence that you did not take the shortcut: (a) a test file exists at `tests/test_parse_config.py`, (b) the test imports and calls `parse_config()` with real config data, (c) running `pytest tests/test_parse_config.py` passes.

**gate 門 (Assertions must precede behavior)**
An assertion is a verifiable binary check (PASS/FAIL) that fails when the behavior is absent and passes only when it is present. No behavior may be implemented until:
1. A governing assertion exists (a test, a type check, a static analysis rule, or a manual verification protocol).
2. The assertion has been verified to fail in the current state (proof that the behavior is missing).

When a natural executable assertion is not possible (e.g., "the documentation guides the reader correctly"), a manual verification protocol is required: specify who verifies, what procedure they follow, and what binary pass/fail condition is defined in advance.

*Example:* For a Go struct field that must be non-empty:
- Executable assertion: `func TestFieldRequired(t *testing.T) { s := &MyStruct{}; if s.Field != "" { t.Fail() } }` (fails before the field is added, passes after).
- Non-executable assertion example: "the field improves code clarity" — no test can verify this. Instead, declare: "Code reviewer (who), reads the struct definition and checks whether the field name is unambiguous (procedure), PASS if field name clearly indicates its purpose (pass/fail)."

**chain 繋 (Reproduce predecessor output before the next step)**
Each reasoning or implementation step must begin by reproducing the exact predecessor output—the actual output, not a paraphrase. This makes intermediate steps verifiable.

*Example:* Your test fails with the message:
```
FAILED tests/test_parse_config.py::test_parse_yaml - KeyError: 'version'
```
Before you implement a fix, reproduce this exact failure message in your step record or PR description. Then implement only the code that closes this failure. When you run the test again, reproduce the new output.

**atomic 粒 (One governing output, one step)**
Each implementation step opens from exactly one governing output (a test failure, a compile error, or a manual verification failure). Implement only what closes that one failure. Do not fix multiple problems, refactor unrelated code, or optimize beyond the current failure.

*Example:*
1. Run: `go test ./...` → Output: `undefined: ParseConfig` (first failure).
2. Step 1: Implement `ParseConfig()` skeleton; run again.
3. Output: `ParseConfig() returns uninitialized Config struct` (new failure, now open).
4. Step 2: Add field initialization; run again.
5. Output: all tests pass.

Do not merge steps 1 and 2 ("implement ParseConfig fully") because that violates the one-failure-per-step principle. Each step should be independently reviewable and traceable to the failure it closes.

### Applying All Four Tokens Together

When all four are active (ground + gate + chain + atomic):

1. **ground** governs the task process as a whole: you must have derived the enforcement process and included a completion check.
2. **gate** governs what must exist before each step begins: every behavior must have a governing assertion that has been verified to fail.
3. **chain** governs continuity between steps: each new step reproduces the exact predecessor failure or output.
4. **atomic** governs the scope of each step: implement only what closes the current governing failure.

They do not conflict—violations at one level are independent of the others.

### Checklist for Contributors

Before opening a PR, confirm:

- [ ] I have derived an enforcement process that names cheap paths and specifies visible evidence.
- [ ] Every behavior I implemented has a governing assertion (test, type check, static analysis, or manual protocol).
- [ ] Each assertion was verified to fail before I implemented the behavior.
- [ ] For each implementation step, I reproduced the governing output (test failure, error message, or manual verification note) before implementing.
- [ ] Each step closes exactly one governing failure; unrelated changes are in separate steps.
- [ ] I have completed the ground completion check: returning to the original intent, I have produced visible evidence for each requirement.

## Release checklist

- Review README release notes for the current cycle and ensure skip sentinel guidance (`//next` usage) remains listed.
- Verify CLI help (`bar help`) and the docs quickstart still show the skip sentinel instructions.
- Confirm `go test ./...` passes, including completion help tests that assert skip sentinel text.

## GPT prompts, axes, and ADRs

- Before adding or changing **static prompts** or axis lists, read:
  - `docs/adr/012-style-and-method-prompt-refactor.md`
  - `docs/adr/013-static-prompt-axis-refinement-and-streamlining.md`
  - `docs/adr/015-voice-audience-tone-intent-decomposition.md`
  - `docs/adr/040-axis-families-and-persona-contract-simplification.md`
- Design rules (summarised from those ADRs):
- Prefer **axes + patterns** (completeness/scope/method/style + directional lenses) for new behaviours.
- Think in **families**: Persona (Who: voice/audience/tone), Intent (Why: intent), Contract (How: completeness/scope/method/style). When adding a new behaviour, first decide which single question it primarily answers (Who, Why, or How); if it genuinely spans more than one, model it as a recipe/pattern that sets multiple axes rather than a new raw token.
- Add new static prompts only for clearly semantic/domain lenses or structured tasks that are not easily expressed via axes alone.
- Persona/intent tokens and presets must be routed through `lib/personaOrchestrator.get_persona_intent_orchestrator()`; after updating `lib/personaConfig.py`, reset the orchestrator cache and update façade consumers instead of touching surfaces directly.
- Keep Talon lists, pattern GUIs, help surfaces, and tests in sync whenever you change prompts or axes.
- Name axis tokens for speech: use short, single, pronounceable words without hyphens (for example, `shellscript` instead of `shell-script`); avoid punctuation or multi-word phrases in axis keys so they remain easy to speak and remember.
- Do **not** reintroduce axis-only behaviours (for example, `diagram`, `presenterm`, `HTML`, `gherkin`, `shell`, `code`, `emoji`, `format`, `recipe`, `lens`, `commit`, `ADR`, `debug`, `structure`, `flow`, `compare`, `type`, `relation`, `clusters`, `motifs`, `taxonomy`) as static prompts; they should remain on the style/method axes with patterns/recipes.
- When changing prompts or axes, run and update the guardrail tests described in ADR 012 (for example, `tests/test_axis_mapping.py`, `tests/test_static_prompt_docs.py`, `tests/test_model_pattern_gui.py`, `tests/test_model_help_gui.py`) so docs, patterns, and behaviour stay in sync.
- When deprecating or demoting a static prompt, follow the “Mini-checklist: deprecating a static prompt” subsection in ADR 012 to keep config, patterns, docs, and tests aligned.
- The catalog is the SSOT for axis/static prompt vocab. Axis/static prompt .talon-lists are not tracked; if you need local list files (for example, for Talon debugging), generate them ad hoc with `make talon-lists` (runs `scripts/tools/generate_talon_lists.py`) or drift-check an existing directory with `make talon-lists-check`.
- User-extensible lists (for example, `customPrompt.talon-list`, `modelDestination.talon-list`, persona/intent lists) remain file-backed; do not overwrite them with catalog output.
- Guardrails: `make axis-guardrails` (catalog + cheat sheet; skips on-disk list files), `make axis-guardrails-ci` (catalog-only), and `make axis-guardrails-test` (full suite including parity) keep axis/static prompt vocab aligned; run these after axis/static prompt changes. `make axis-catalog-validate` and `make axis-cheatsheet` are available as individual primitives. `make talon-lists`/`make talon-lists-check` are optional helpers if you need to export/check Talon lists locally. For ad-hoc validation of a user-extensible Talon lists directory, run `python3 scripts/tools/axis-catalog-validate.py --lists-dir /path/to/lists` (catalog-only by default via `--skip-list-files`; pass `--no-skip-list-files` to enforce list checks).
- History guardrails: `make request-history-guardrails` exports telemetry summaries and `make request-history-guardrails-fast` provides a slimmer snapshot. These helpers run locally only (manual telemetry access required), so automate them outside CI if needed.
- One-command guardrails: `make guardrails` runs the CI guardrails and key parity tests (now including the portable CLI completion guard); `make ci-guardrails` is the CI-friendly alias without the extra parity; use these before PRs to catch catalog/list drift.
- Portable prompt CLI: run `make bar-completion-guard` (or rely on the guardrails targets above) whenever you touch prompt grammar/completion code to keep the `bar completion` pytest guard green. This target requires Go 1.21+ (`go version` should succeed) and Python 3.11+ locally.
- CI entrypoint: call the appropriate `make` target directly (for example, `make ci-guardrails` or `make axis-guardrails-ci`) and upload any artifacts you need explicitly.
- If you force list checks with `--no-skip-list-files`, you must also pass `--lists-dir` to point at the Talon lists you want to validate.
- Prompt grammar artifact: whenever you change prompts, axes, persona vocabularies, or the exporter itself, run `python3 -m prompts.export --output build/prompt-grammar.json --embed-path internal/barcli/embed/prompt-grammar.json` and commit the refreshed JSON mirrors. CI now re-runs this command and fails if the tracked files drift, so keep both artifacts clean before sending a PR.

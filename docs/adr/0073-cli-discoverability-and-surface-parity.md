Proposed — CLI discoverability and surface parity alignment (2026-01-10)
Updated 2026-02-12 — redirected interactive surface references to `bar tui2` (ADR-0081).

## Context
- ADR 0065 and 0070 positioned the `bar` CLI as the grammar-driven entry point, but the default invocation still prints a usage error followed by a dense help wall.
- clig.dev guidance emphasises concise default help, clear escalation to full docs, and consistent interactive opt-outs; our CLI currently falls short on each dimension.
- Operators bounce between `bar build`, `bar help tokens`, and the interactive TUI surfaces, yet environment flags (`--no-alt-screen`, `--env`) and output modes (`--json`) are not advertised together.
- Automation teams requested stable machine-readable pathways (`--json`, `--plain`) plus an explicit `--no-input` guard so scripts fail fast when a subcommand tries to prompt.
- The help surface lacks concrete examples for cross-surface workflows (e.g., piping presets into `bar tui2` or copying configs back to `bar build`), leaving the shorthand grammar harder to learn.
- **Updated context (2026-02-12):** `bar tui2` (ADR-0081) has been implemented since this ADR was written. It is the command-centric grammar learning interface that supersedes `bar tui` (ADR-0077) as the preferred interactive surface. `bar tui2` teaches the `bar build` grammar through stage-based token selection and a live preview pane. `bar tui` remains available but `bar tui2` is the recommended path for new users and cross-surface loop documentation.

## Decision
- Replace the "unknown command" fallback with a concise default banner shown when `bar` is run without arguments; include a single-sentence description, two common examples, and a pointer to `bar --help`.
- Split help into tiers:
  - `bar --help` / `bar help` presents grouped sections (Core commands, Grammar navigation, Interactive surfaces, Automation flags) with succinct descriptions and top-three examples.
  - `bar help <topic>` retains deep dives (tokens, presets, tui) but adds "See also" footers linking between CLI and TUI docs.
- Introduce a global `--no-input` flag recognised by `bar build`, `bar preset use`, `bar tui`, and `bar tui2`; when set, any code path that would prompt must exit with guidance on the alternate flag.
- Add a `--command` (alias `--cmd`) flag to `bar tui2` so operators can seed the Run Command field at launch time, keeping CLI/TUI loops reproducible in demos and fixture smoke tests. (`bar tui2` is the preferred interactive surface; apply to `bar tui` only if warranted for backwards compatibility.)
- Advertise machine-friendly output consistently: document `--json` across commands and add a shared `--plain` formatter for textual reports (token listings, presets) that removes colour, headings, and multi-line cells.
- Extend the tiered help treatment to `bar tui2 --help` (and `bar tui --help`), mirroring the concise banner plus grouped sections (Core commands, Grammar navigation, Interactive surfaces, Automation flags) and the completion hints for `--fixture`, `--no-alt-screen`, `--env`, `--no-input`, and `--command`.
- Advertise `bar tui2` in the `generalHelpText` as the recommended interactive surface alongside `bar tui`.
- Publish a short "conversation loops" section in CLI help that points to commands for: start in CLI → inspect tokens → open `bar tui2` → copy equivalent CLI; this keeps the shorthand grammar discoverable without leaving the terminal.

## Rationale
- clig.dev frames concise default help as essential for human-first CLIs; the current error+wall sequence violates that expectation and slows onboarding.
- Normalising `--no-input` and `--plain` across subcommands gives automation users predictable escape hatches while keeping human defaults legible.
- Seeding `bar tui2` with `--command` keeps the Run Command history reproducible, allowing demos and CI fixtures to showcase automation parity without manual typing. `bar tui2`'s stage-based interaction model makes it a better learning environment than the original `bar tui` for demonstrating grammar structure.
- Grouped help reflects how operators actually chain commands, turning fragmented examples into narrative workflows that reinforce the grammar mental model; mirroring the tiers inside `bar tui2 --help` keeps the interactive surface anchored to the same grammar story.
- Advertising cross-surface loops acknowledges that TUI and CLI are complementary; pointing to `bar tui2` in the conversation loops section gives new users an immediately discoverable path to the grammar learning surface.

## Consequences
- Argument parsing must recognise the new global `--no-input` and propagate it through shared helpers; tests covering prompt reading need updates.
- `bar tui2` has to accept and forward `--command` input into the Run Command field while keeping fixture snapshots deterministic. `bartui2.Options` will need an `InitialCommand` field.
- Help text refactors will invalidate existing snapshot-based assertions and require refreshing completion fixture strings.
- Shell completion scripts should expose the new flags, necessitating regeneration and downstream installer updates.
- Documentation (README, usage guides, pilot playbook) must sync with the tiered help narrative, highlight the new automation affordances, and position `bar tui2` as the recommended interactive surface.

## Validation
- Extend `go test ./internal/barcli/...` with unit tests for `--no-input`, `--command` seeding on `bar tui2`, concise default help output, and `--plain` formatting on grammar listings.
- Update deterministic fixtures (e.g., `_tests/test_bar_completion_cli.py`, `cmd/bar/testdata/help_default.txt`) to cover the new messaging, including `bar tui2` in the help surface and the tiered `bar tui2 --help` copy.
- Smoke-test `bar tui2 --fixture … --no-input --command "echo hi"` to ensure the TUI honours both flags and exits with actionable messaging.

## Follow-up
- Regenerate shell completions and re-run `python3 -m pytest _tests/test_bar_completion_cli.py` to verify updated hints.
- Refresh onboarding docs with the concise banner, conversational workflows, the automation flag table, and examples of `bar tui2 --command` loops.
- Publish a short cookbook entry showing CLI → `bar tui2` hand-offs using `--command` so support teams can reference a single snippet.
- Monitor operator telemetry to see whether `--plain` uptake warrants additional machine-readable affordances (e.g., CSV export).

## Anti-goals
- Do not introduce new subcommands or change existing grammar semantics; focus solely on discoverability and parity improvements.
- Avoid bundling UI layout work here—layout refinements for `bar tui2` remain governed by ADR-0081's scope; original `bar tui` layout remains under ADR-0071.
- Do not deprecate interactive flows; the goal is to document escape hatches, not to remove guided inputs. Both `bar tui` and `bar tui2` remain available.

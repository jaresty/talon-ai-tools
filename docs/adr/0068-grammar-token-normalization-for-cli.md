## Status
Accepted — portable CLI now ships slug metadata, warnings, docs, and release communication (2026-01-08)

## Context
- Prompt grammar tokens intentionally preserve human-friendly spacing so the same vocabulary can be reused in Talon phrases, UI surfaces, and docs.
- The portable CLI copies those tokens directly, which forces shells to juggle multi-word entries by appending trailing spaces and relying on quoting rules that differ between Bash, Zsh, and Fish.
- Recent fixes restored trailing spaces in completion payloads so words like `as pm` insert correctly, but the experience remains brittle and surprises users who expect single-token completions.
- Multiple downstream consumers (CLI, prompts, docs) now depend on the shared grammar bundle, so any token change must continue serving human-readable contexts while making the CLI predictable.

## Decision
- Introduce a normalized slug for every grammar token that is intended for CLI use. Slugs are:
  - lower-cased,
  - de-duplicated,
  - stripped of punctuation, and
  - whitespace replaced with `-`.
- Preserve the existing human-friendly token as the canonical label that renders in documentation and GUI surfaces.
- Extend the grammar export to ship both representations (`label` and `slug`) so portable consumers can choose the appropriate form without guessing.
- Update the CLI parser and completion backend to operate on slugs for command-line insertion while still showing the human label (and description) in metadata columns.
- Teach shorthand normalization to accept either input (slug or label) and translate to the canonical token before hydration so existing scripts continue working during the transition.

## Rationale
- Slugs sidestep shell quoting oddities while creating an explicit contract for future tooling (e.g., integration tests, other CLIs) that rely on grammar tokens.
- Carrying both representations keeps existing UX intact: Talon surfaces continue to show readable phrases, while the CLI gains predictable, single-token suggestions.
- Explicit normalization allows us to deprecate the fragile "append a space" workaround and avoid additional shell-specific hacks.

## Consequences
- Grammar build scripts and artifacts must grow a slug-generation step; they will need regression tests to confirm stability.
- Every consumer of the grammar bundle (CLI, docs, Talon overlays) must be reviewed to ensure they pick the correct representation.
- Completion fixtures and CLI tests require updates to assert slug output as well as backward-compatible label matching.
- Documentation and release notes must call out the change so users know that slugs become the default CLI form.
- During the migration window we should emit deprecation warnings when labels are entered directly, eventually removing the fallback once scripts have been updated.

## Validation
- `go test ./internal/barcli` exercises the Go completion backend and shorthand normalization, ensuring slug tokens remain canonical while label fallbacks continue to be accepted with warnings.
- `python3 -m pytest _tests/test_bar_completion_cli.py` covers the portable CLI wrappers and metadata-emitting completions, guarding the command-line interfaces and shell installers against regressions in slug output.
- `python3 -m pytest _tests/test_generate_axis_cheatsheet.py` keeps the human-facing grammar documentation in sync with slug terminology so docs and release notes remain authoritative.

## Follow-up
- Label-input fallback removal is owned collectively by the bar CLI maintainers via the release checklist (tracked in issue `BAR-142`). Target release: `bar v0.2.0` (milestone confirmed in release planning on 2026-01-08). Before that tag ships, record telemetry acceptance and a sunset checklist in the work-log; if the scope grows beyond retiring the warning path, cut a dedicated follow-up ADR.

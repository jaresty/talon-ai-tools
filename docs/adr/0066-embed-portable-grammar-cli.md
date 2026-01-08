# 0066 — Embed prompt grammar in `bar`

## Status
Completed

## Context
- The `bar` CLI currently loads the prompt grammar from an external JSON file (`build/prompt-grammar.json`) at runtime. Completions and help flows depend on that file being present.
- Distributing the CLI as a standalone binary requires shipping the grammar JSON alongside it and expecting users to keep both in sync.
- The installer script and release artifacts aim to deliver a portable experience that works without cloning this repository or exporting the grammar manually.
- The CLI still needs the ability to target alternate grammar payloads for testing and overrides (e.g., future schema revisions, fixture-driven tests).

## Decision
- Embed the canonical `build/prompt-grammar.json` artifact directly into the `bar` binary at build time using Go's `//go:embed` facilities.
- At runtime, use the embedded grammar by default. Continue to honor `--grammar` and `BAR_GRAMMAR_PATH` overrides; when an override is provided, load that file instead of the embedded payload.
- Provide a helper in the build package to expose the embedded grammar as an `io.Reader` so completions, help, and tests can consume the same data path with minimal changes.
- Update release workflows to ensure the embedded grammar is regenerated before compilation so emitted binaries always reflect the latest exporter output.

## Rationale
- Embedding the grammar makes the CLI genuinely portable: users can download a single binary and immediately access completions and help without syncing auxiliary files.
- Maintaining override hooks preserves developer ergonomics (fixtures, regression tests, experimental grammars) without impacting end users.
- Embedding via `go:embed` keeps the implementation simple and avoids introducing bespoke asset pipelines or runtime network calls.
- Regenerating the grammar artifact prior to compilation ensures the embedded payload stays aligned with updates produced by the Python exporter.

## Consequences
- `go build ./cmd/bar` must run after `python3 -m prompts.export` (as today) so the embedded payload reflects the latest grammar; release CI will enforce this ordering.
- The exporter mirrors the artifact into `internal/barcli/embed/prompt-grammar.json` so the `go:embed` payload stays in sync with the tracked `build/prompt-grammar.json` source.
- Binary size will increase by the size of the grammar JSON (currently <1 MB), which is acceptable for the portability benefits gained.
- Any future schema migrations require bumping the embedded asset and accompanying code in a single change, keeping the CLI and grammar synchronized.
- Tests that previously relied on filesystem fixtures may be updated to use the embedded payload unless they explicitly validate override behavior.

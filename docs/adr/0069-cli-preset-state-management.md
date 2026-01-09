Proposed — CLI preset capture reuses last build state to persist shorthand contexts (2026-01-08)

## Context
- The `bar` CLI currently supports `build` to assemble prompt recipes from shorthand tokens but offers no persistent storage for frequently reused stances or token sequences.
- Users external to the Talon runtime lack access to the Python-side "suggest" helper and therefore repeat identical `bar build …` invocations (or manually copy/paste token strings) when iterating on similar requests.
- Earlier explorations considered re-implementing the Python suggest workflow in Go, but that adds significant complexity and risks divergence from the single-source prompt contract maintained on the Python side.
- We still want a portable, low-friction way for CLI users to capture and reuse successful build contexts without introducing a full LLM integration layer.

## Decision
- Introduce a lightweight preset facility that checkpoints the most recent successful `bar build` result and allows users to persist it by name.
- After every successful `bar build`, write the resulting `BuildResult` metadata (canonical tokens, persona stance, hydrated promptlets, and rendered axes) to `~/.config/bar/state/last_build.json` with permissions `0600`, omitting any captured subject text entirely.
- Add `bar preset save <name>` which copies the cached `last_build.json` payload into `~/.config/bar/presets/<slugged-name>.json` (again `0600`), persisting only the canonical token sequence and derived metadata so no subject text is stored. Names are slugged via lowercase + `-` to keep filenames portable; collisions overwrite only when explicitly confirmed via `--force`.
- Add auxiliary commands:
  - `bar preset list` to enumerate saved preset names alongside key axes (static prompt, persona voice/audience/tone).
  - `bar preset show <name>` to emit the stored JSON (or a formatted summary).
  - `bar preset delete <name>` to remove a preset file, with an interactive prompt unless `--force` is supplied.
  - `bar preset use <name>` to rebuild a recipe using the cached token sequence, accepting the same prompt input options as `bar build` (STDIN, `--prompt`, or `--input`). Presets intentionally omit the previous subject to avoid leaking sensitive content, so users must supply fresh context on each invocation.
- Store a schema version in every preset file so future migrations can invalidate or upgrade stale payloads when the underlying `BuildResult` structure changes.
- Documentation updates will describe the new commands, the cache location, and the relationship between `build` and `preset save` (i.e. users must run `bar build` before saving).

## Rationale
- Reusing the cached `BuildResult` preserves exactly what the user just verified, avoiding accidental drift that might come from re-parsing tokens or asking them to retype flags.
- Persisting presets as plain JSON keeps the feature transparent, scriptable, and easy to back up or share with collaborators.
- Leveraging the existing `BuildResult` schema eliminates the need to replicate the Python suggest prompt while still offering tangible productivity gains for CLI users.
- Rebuilding presets directly via `bar preset use` keeps the CLI parity with `bar build`, letting users reuse canonical recipes on new subject text without an extra piping step.
- Keeping the state in `~/.config/bar/` mirrors typical CLI conventions and avoids polluting the repository or requiring elevated permissions.

## Consequences
- The CLI now writes to disk after each successful `build`, so we must ensure atomic writes (temp file + rename) to avoid corrupting the cache on crashes.
- Preset files persist only canonical tokens and metadata, preventing stale subject leaks; `preset use` rebuilds recipes while requiring callers to provide the subject explicitly on each invocation.
- Users running multiple instances concurrently could race on `last_build.json`; we need to either serialize writes or accept “last writer wins” semantics and document it.
- We must ship migration guards: if the cached schema version does not match the binary’s expected version, commands that rely on it should instruct the user to rebuild before saving.
- Additional help text, completion metadata, and tests are required to cover the new preset commands and surface failure modes (no cached build, missing preset, permission errors).
- Security posture changes slightly: cached subjects and stance metadata land on disk; we should flag this in docs so users handling sensitive prompts can disable caching via an env var (e.g. `BAR_DISABLE_STATE=1`).

## Validation
- Extend `go test ./internal/barcli` with fixtures covering:
  - writing and reading `last_build.json` atomically,
  - saving, listing, showing, and deleting presets,
  - handling missing cache / mismatched versions / permission errors.
- Add integration-style tests (similar to existing CLI ones) that run `bar build …`, then `bar preset save/list/show/use` to exercise the full flow.
- Manual validation: run the CLI end-to-end on macOS/Linux, confirm preset files appear in `~/.config/bar/presets/`, and verify they round-trip after editing.

## Follow-up
- Implement the preset commands, state persistence helpers, and help text/completions per this ADR.
- Document the caching behaviour and opt-out env var in the README.
- Consider future enhancements (e.g. `preset run <name>` to directly invoke `bar build`) once the baseline feature proves useful.

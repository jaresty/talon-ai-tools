# ADR-0150 – Charm v2 Library Migration (Bubble Tea, Lip Gloss, Bubbles)
Status: Accepted
Date: 2026-03-02
Owners: CLI Working Group

## Context

The `bar` Go CLI and its TUI (`internal/bartui2`, `internal/bartui`) are built on the v1 generation of Charm's terminal UI libraries:

| Library | Current version | v2 version |
|---|---|---|
| `github.com/charmbracelet/bubbletea` | v0.25.0 | `charm.land/bubbletea/v2` |
| `github.com/charmbracelet/lipgloss` | v1.1.0 | `charm.land/lipgloss/v2` |
| `github.com/charmbracelet/bubbles` | v0.17.1 | `charm.land/bubbles/v2` |

Charm released v2.0.0 of all three libraries simultaneously (March 2026). These are coordinated breaking changes — all three libraries are designed to work together and the new features in each depend on the others' v2 APIs.

Beyond the Go source, this project maintains a set of local skill files under `.claude/skills/` that document v1 patterns and guide future Charm-based development. Every skill that references Charm APIs will produce subtly wrong code after the migration unless it is updated to reflect v2.

## Problem

- **Performance ceiling**: The v1 renderer cannot take advantage of the Cursed Renderer (ncurses-algorithm-based, "orders of magnitude" faster, especially relevant for the TUI's viewport-heavy token catalog and preview panes).
- **API debt**: Continued new work against v1 APIs will require a larger migration when v1 reaches end-of-life, and the growing v2 ecosystem (examples, documentation, community answers) increasingly assumes v2.
- **Stale skills**: After migration, any future TUI work guided by existing skills would produce code that uses deprecated v1 patterns (old import paths, removed `.Copy()` calls, renamed style fields, old key message types), silently re-introducing tech debt on every session.
- **Missing capabilities**: The TUI cannot access v2 features — viewport horizontal scrolling, regex highlights, real terminal cursor, declarative alt-screen/mouse configuration, OSC52 clipboard over SSH, synchronized rendering — without the migration.

## Decision

Migrate the Go CLI and all local Charm skills to the v2 libraries in a single coordinated effort, structured as sequential phases with a validation gate between each phase. The skill updates are a first-class deliverable alongside the source migration: the work is not complete until skills reflect v2 patterns and future development naturally leverages new features.

## Implementation Approach

### Phase 1 — Dependency update and import path sweep

Update `go.mod` to reference v2 module paths for all three libraries and perform a mechanical find-and-replace of import paths across the Go source tree. At the end of this phase `go build ./...` should succeed or fail only on known API changes, not on missing modules.

Files in scope: `go.mod`, `go.sum`, `internal/bartui/program.go`, `internal/bartui/program_test.go`, `internal/bartui2/program.go`, `internal/bartui2/program_test.go`, and any test helpers that import Charm packages.

**Import path changes:**
```
github.com/charmbracelet/bubbletea   →  charm.land/bubbletea/v2
github.com/charmbracelet/lipgloss    →  charm.land/lipgloss/v2
github.com/charmbracelet/bubbles/*   →  charm.land/bubbles/v2/*
```

Validation gate: `go build ./...` compiles (errors are acceptable; panics from missing symbols should not exist after import fixup).

### Phase 2 — Bubble Tea v2 source migration

Address all breaking API changes in the Bubble Tea layer, touching `internal/bartui/program.go`, `internal/bartui2/program.go`, and their tests.

**Required changes:**

1. **`View()` return type**: Change all `View()` method signatures from `func (m Model) View() string` to `func (m Model) View() tea.View`. Wrap the rendered string inside a `tea.View{}` struct literal. Any alt-screen, mouse, or focus-report activation currently done via `tea.Cmd` commands at program start should be migrated to declarative fields on this struct.

2. **Remove terminal control commands**: Delete any uses of `tea.EnterAltScreen`, `tea.EnableMouseCellMotion`, `tea.EnableMouseAllMotion`, `tea.EnableReportFocus`, and their disable counterparts. These are now set on the `View` struct returned by `View()`.

3. **Key message types**: Update all `case tea.KeyMsg:` switches to use `tea.KeyPressMsg` (for key-down events). The compound type alias `tea.KeyMsg` still exists but now matches both press and release; prefer `tea.KeyPressMsg` for action handlers. Update field references: `msg.Type` / `msg.Runes` → `msg.Code` / `msg.Text`. Update the space key match from `" "` to `"space"`.

4. **Mouse message types**: Replace any `tea.MouseMsg` switch arms with the new granular types: `tea.MouseClickMsg`, `tea.MouseReleaseMsg`, `tea.MouseWheelMsg`, `tea.MouseMotionMsg`.

5. **Paste events**: Update any bracketed-paste handling to use `tea.PasteMsg`, `tea.PasteStartMsg`, and `tea.PasteEndMsg`.

Validation gate: `go test ./internal/bartui/...` and `go test ./internal/bartui2/...` pass. Snapshot tests (`bar tui --fixture`) produce consistent output.

### Phase 3 — Lip Gloss v2 source migration

Address breaking API changes in the Lip Gloss layer.

**Required changes:**

1. **Color type**: `lipgloss.Color` is no longer a string type; it is a function returning `color.Color`. Audit every call site that passes a hex string directly (e.g., `lipgloss.Color("#ff0000")`) — this pattern still works as a constructor call but the returned value is now a `color.Color`, not a `lipgloss.Color` string. Verify theme structs that store `lipgloss.Color` as a field type are updated if they do type assertions.

2. **`AdaptiveColor`**: Move any `lipgloss.AdaptiveColor{}` usages to `compat.AdaptiveColor{}` from `charm.land/lipgloss/v2/compat`. The field types inside (`Light`, `Dark`) remain `lipgloss.Color`.

3. **`Style.Copy()` removed**: Replace all `.Copy()` chains with direct style assignments. In v2, `lipgloss.Style` is a value type; `s2 := s1` produces an independent copy without a method call. This includes the pattern `theme.Base.Copy().Border(...)` in skill references and any equivalent in source.

4. **Background color detection**: Remove any calls to the removed automatic background detection API. To support adaptive colors in Bubble Tea contexts, handle `tea.BackgroundColorMsg` in the root model's `Update` and call `lipgloss.HasDarkBackground(os.Stdin, os.Stderr)` for non-Bubble Tea contexts (e.g., `bar build` output styling).

5. **Output helpers**: Replace `fmt.Println(style.Render(...))` with `lipgloss.Println(style.Render(...))` in non-TUI render paths to ensure correct color downsampling.

Validation gate: `go test ./...` passes. Run `bar build --prompt "test"` in a terminal and confirm styled output renders without ANSI artifacts.

### Phase 4 — Bubbles v2 source migration

Address breaking API changes in the Bubbles components used in `bartui` and `bartui2`.

**Required changes:**

1. **`textinput`**: Replace direct field assignments on the `textinput.Styles{}` struct with the new `StyleState` API. Replace `ti.Width = n` with `ti.SetWidth(n)`. Replace `textinput.DefaultKeyMap` variable references with `textinput.DefaultKeyMap()` function calls.

2. **`textarea`**: Replace `ta.FocusedStyle` and `ta.BlurredStyle` fields with `ta.Styles.Focused` and `ta.Styles.Blurred`. Replace `ta.SetCursor(n)` with `ta.SetCursorColumn(n)`. Update `StyleState` references where previously named `Style`.

3. **`viewport`**: Replace `viewport.New(width, height)` constructor calls with the functional options pattern: `viewport.New(viewport.WithWidth(width), viewport.WithHeight(height))`. Replace direct field reads/writes for `Width`, `Height`, `YOffset` with the getter/setter methods (`vp.Width()`, `vp.SetWidth(n)`, etc.). Remove any uses of `HighPerformanceRendering` — it no longer exists.

4. **`list`**: Update any calls to `list.DefaultStyles()` or `list.NewDefaultItemStyles()` to pass a `bool` indicating dark mode: `list.DefaultStyles(isDark)`.

Validation gate: `go test ./...` passes. `bar tui --fixture testdata/tui_smoke.json --no-alt-screen` produces a snapshot diff of zero lines against the committed fixture. If the fixture itself changes due to rendering improvements, update it deliberately and commit the diff.

### Phase 5 — New feature adoption (intentional leverage)

With the migration complete, adopt v2 capabilities that directly improve the existing TUI. This phase is bounded to features with clear UX value; do not speculatively add capabilities.

**Targeted improvements:**

1. **Viewport enhancements in `bartui2`**: Enable `SoftWrap` on the preview viewport so long prompt previews word-wrap rather than truncate. Add a `LeftGutterFunc` to the token catalog viewport to display line numbers or selection state indicators. These are purely additive.

2. **Synchronized rendering**: Mode 2026 (synchronized updates) is enabled automatically by the Cursed Renderer. No source changes needed, but validate that snapshot tests pass, since rendering timing may differ.

3. **Real terminal cursor (opt-in)**: Where the `textinput` subject field currently uses a virtual cursor, evaluate enabling the real terminal cursor via `Cursor()` → `*tea.Cursor`. This gives sub-cell precision and correct blink. Gate behind the existing `NoAltScreen` option so fixture tests remain cursor-independent.

**Explicitly deferred** (do not scope into this ADR): inline image rendering, clipboard OSC52 over SSH, terminal color queries, raw escape sequences. These require design work beyond a library upgrade.

Validation gate: Manual TUI session confirms preview viewport wraps, no rendering glitches, and the cursor behaves correctly on real terminal vs. `--fixture` mode.

### Phase 6 — Skill file updates

Update all local skills under `.claude/skills/` that reference Charm v1 APIs. Each skill must reflect v2 import paths, updated API patterns, and — where applicable — note new v2 features available for future use.

**Skills requiring substantive updates:**

| Skill | Primary changes needed |
|---|---|
| `bubbles-inputs/SKILL.md` | Update import paths; note StyleState for textinput/textarea |
| `bubbles-inputs/references/form-inputs.md` | Replace `.Copy()` with value assignment; `ti.Width = n` → `ti.SetWidth(n)`; update style field names to v2 StyleState; fix import paths |
| `bubbletea-overlays/SKILL.md` | Update import paths; update View() description to return tea.View |
| `bubbletea-overlays/references/overlays.md` | Fix import paths; update `tea.KeyMsg` → `tea.KeyPressMsg`; add note on declarative View fields replacing terminal control commands |
| `bubbletea-dialog-stacking/SKILL.md` | Update cross-references and import paths |
| `lipgloss-theme-foundations/SKILL.md` | Update import path; update color constructor pattern; add dark/light mode detection via `tea.BackgroundColorMsg` / `lipgloss.HasDarkBackground()`; note `.Copy()` removal |
| `lipgloss-components/SKILL.md` | Update import paths; note Compositor/Layer is a first-class v2 API |
| `lipgloss-components/references/table-rendering.md` | Update import paths; verify `lipgloss/table` package path |
| `lipgloss-layout-utilities/SKILL.md` | Update import path; verify `lipgloss.JoinHorizontal`, `Place`, `Width`/`Height` still work (these are stable) |
| `markdown-diff-rendering/references/markdown.md` | Verify glamour import path (glamour is a separate library, not part of the Charm v2 bundle; likely no changes needed but confirm) |
| `components/SKILL.md` | Update cross-references to bubbles-inputs and lipgloss-components |

**Pattern additions for all Charm skills**: Add a short "v2 gotchas" section covering the three changes that will bite future developers most often: (1) no `.Copy()` on styles, (2) `View()` returns `tea.View` not `string`, (3) functional options on `viewport.New`.

Validation gate: A fresh session guided only by the updated skills should produce compilable code that passes `go build ./...` without requiring additional fixes.

## Consequences

- **Positive**: Access to the Cursed Renderer and all v2 performance improvements; declarative terminal control (cleaner program initialization); viewport horizontal scrolling and soft-wrap available for future token catalog or preview improvements; `Style.Copy()` elimination reduces accidental style mutation bugs; skill-guided development produces correct v2 code from the start.
- **Negative**: Phases 1–4 carry a non-trivial mechanical migration burden. The snapshot fixture file(s) under `testdata/` may need deliberate updates if the Cursed Renderer produces subtly different spacing or cell widths.
- **Risk**: The new import paths (`charm.land/...`) are a vanity-domain redirect. If the domain resolves differently across environments (CI, developer machines, offline), `go get` may fail. Verify module proxy caching works as expected before merging.
- **Sequencing constraint**: Phases 2–4 must be executed after Phase 1 completes. Phase 5 must follow Phase 4. Phase 6 can begin in parallel with Phase 5 but should not be merged before Phase 4 is complete, since skill examples should be validated against compilable code.

## Validation

- `go test ./...` passes after each phase.
- `bar tui --fixture cmd/bar/testdata/tui_smoke.json --no-alt-screen` produces zero snapshot diff against committed fixture (or a committed diff if rendering intentionally changed in Phase 5).
- `go build ./cmd/bar/...` produces a runnable binary that completes `bar build --prompt "test scope:system"` without panicking or producing ANSI artifacts.
- `make guardrails` (if it validates binary manifests) continues to pass.
- A manual session with `bar tui` on a real terminal confirms the TUI renders correctly, accepts keyboard input using the v2 key mapping, and the alt-screen is entered and exited cleanly.

## Salient Tasks

- Update `go.mod` and perform import path sweep across all Go source files.
- Migrate `View()` return types and remove deprecated terminal-control commands in `bartui` and `bartui2`.
- Update key message switch arms: `tea.KeyMsg` → `tea.KeyPressMsg`, field references `msg.Type`/`msg.Runes` → `msg.Code`/`msg.Text`, space match `" "` → `"space"`.
- Replace Lip Gloss `.Copy()` calls with value assignments; update color constructors and adaptive color imports.
- Migrate Bubbles components: textinput StyleState fields, `SetWidth()` setter, viewport functional options, list `DefaultStyles(isDark)`.
- Update or regenerate TUI snapshot fixtures if the Cursed Renderer changes visual output.
- Enable `SoftWrap` on the preview viewport and add a gutter to the token catalog viewport.
- Update all skill files in `.claude/skills/` that reference Charm APIs, adding v2 patterns and a "v2 gotchas" section.

## Anti-goals

- Do not refactor the TUI architecture or add new features beyond what is needed to compile and leverage the targeted Phase 5 improvements.
- Do not upgrade glamour, wish, or other Charm-adjacent libraries unless they are required dependencies of the v2 libraries; keep the dependency surface minimal.
- Do not add OSC52 SSH clipboard, inline image rendering, or terminal color query features — these require separate design work and ADRs.
- Do not change the `bar` CLI's user-visible command surface, flags, or output format; this is a library internals migration.

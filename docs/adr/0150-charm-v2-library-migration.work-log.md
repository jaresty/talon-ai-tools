# ADR-0150 Work Log — Charm v2 Library Migration

Helper version: helper:v20260227.1

---

<!-- Loops appended below -->

---

## Loop 1 — 2026-03-03T08:02:18Z

```
helper_version: helper:v20260227.1
focus: ADR-0150 Phase 1 — go.mod v2 dependency addition + import path sweep (T-1)
active_constraint: go.mod references only v0/v1 Charm modules; no v2 symbols are
  importable, blocking every subsequent API migration. Falsifiable: grep for v1 import
  paths in .go files returns non-zero; removing that state is the only path forward.
  Ranked higher than "API breakages" (Loop 2 scope) because import resolution
  precedes symbol resolution; fixing API without fixing imports yields the same
  compiler error set. Alternative considered: skip import sweep and patch API inline
  with v1 — rejected because v1 packages will lose support and the v2 performance
  gains (Cursed Renderer) require the new module.

validation_targets:
  - T-1: grep for v1 charm import paths in .go files returns 0 lines

evidence:
  - red  | 2026-03-03T08:02:18Z | count=14 | grep -r "github.com/charmbracelet/bubbletea|lipgloss|bubbles" --include="*.go" .
      helper:diff-snapshot=0 files changed (clean baseline)
      14 files with v1 imports; 0 with v2 — behaviour "v2 imports in source" fails | inline
  - green | 2026-03-03T08:02:48Z | count=0  | grep -r "github.com/charmbracelet/..." --include="*.go" .
      helper:diff-snapshot=6 files changed, 63 insertions(+), 22 deletions(-)
      0 v1 imports; 14 v2 imports — behaviour passes | inline
  - removal | 2026-03-03T08:02:52Z | exit 14 | git stash && grep (v1 count)
      git stash restored v1 count to 14; git stash pop restored green state | inline

rollback_plan: git restore go.mod go.sum internal/bartui/program.go
  internal/bartui/program_test.go internal/bartui2/program.go
  internal/bartui2/program_test.go — replay grep red to confirm failure returns.

delta_summary:
  helper:diff-snapshot: 6 files changed, 63 insertions(+), 22 deletions(-)
  go.mod: added charm.land/bubbletea/v2 v2.0.1, charm.land/lipgloss/v2 v2.0.0,
    charm.land/bubbles/v2 v2.0.0 plus transitive deps (ultraviolet, clipperhouse/uax29,
    go-colorful v1.3, x/termios, x/windows).
  4 source files: mechanical sed sweep of 14 import strings.
  go build ./... now fails with v2 API errors (expected; Loop 2 scope).

loops_remaining_forecast:
  5 loops remaining with medium-high confidence:
  Loop 2 — key/View/viewport API fixes → go build passes
  Loop 3 — Lip Gloss color/AdaptiveColor/output-helper fixes (if needed after build)
  Loop 4 — Bubbles textinput.SetWidth + viewport field-setter fixes
  Loop 5 — Phase 5 new feature adoption (SoftWrap, gutter)
  Loop 6 — Phase 6 skill file updates

residual_constraints:
  - "go build ./... fails due to v2 API breakages" (severity H×H×H=27): active next
    loop; mitigation = fix key/View/viewport/textinput APIs per ADR-0150 Phase 2-4.
    Monitoring trigger: Loop 2 green evidence. Owning loop: Loop 2.
  - "go.mod still contains v1 lipgloss v1.1.0 / bubbletea v0.25.0 / bubbles v0.17.1
    as direct/indirect deps" (severity M×M×L=4): will be removed by go mod tidy once
    go build passes. No action needed this loop.

next_work:
  Behaviour: go build ./... passes with v2 charm libraries (T-2)
  Validation: go build ./... → exit 0
  Scope: View() return type string→tea.View; key.Type/key.Runes → key.Code/key.Text;
    tea.KeyRunes → text check; tea.KeySpace → " "; viewport.New(w,h) → functional
    opts; textinput.Width= → SetWidth(); viewport Width/Height fields → setters if
    needed; plus any further errors the compiler surfaces.
```

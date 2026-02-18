# ADR-0138: Mobile UX Phase 2 Work Log

## In-Progress Loops

- **Loop 1**: Fix `showPreview` default bug — [COMPLETE]
- **Loop 2**: Relocate FAB and action overlay to layout root — [COMPLETE]
- **Loop 3**: Show rendered prompt inline; rename panel to "Output" — [PENDING]
- **Loop 4**: Token guidance bottom drawer on mobile — [PENDING]
- **Loop 5**: Touch targets (tabs, persona chips, selected chips, load-cmd-toggle) — [PENDING]
- **Loop 6**: iOS auto-zoom fix — [PENDING]
- **Loop 7**: PWA icon fix — [PENDING]

## History

### loop-1

**helper_version**: helper:v20251223.1

**focus**: ADR-0138 §Loop 1 — Fix `showPreview` default bug

**active_constraint**: `showPreview = $state(true)` causes `.visible` class to always be present on the preview panel, overriding `display: none` in mobile CSS. The toggle button is inert on first load on mobile.

**validation_targets**:
- `npm test -- mobile-preview` — specifying validation: preview panel starts without `.visible` class; toggle adds/removes it correctly.

**evidence**:
- red | 2026-02-18T22:21:52Z | exit 1 | npm test -- mobile-preview
    helper:diff-snapshot=0 files changed (specifying validation updated, implementation unchanged)
    Expected `classList.contains('visible')` to be false, received true | inline
- green | 2026-02-18T22:22:03Z | exit 0 | npm test -- mobile-preview
    helper:diff-snapshot=2 files changed, 9 insertions(+), 9 deletions(-)
    All 4 mobile-preview tests pass; panel starts hidden, toggles correctly | inline
- green | 2026-02-18T22:22:07Z | exit 0 | npm test
    All 89 tests pass | inline

**rollback_plan**: `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-preview.test.ts`

**delta_summary**: helper:diff-snapshot=2 files changed, 9 insertions(+), 9 deletions(-). Changed `showPreview = $state(true)` → `$state(false)`. Updated test to assert panel starts hidden. Also cleaned unused `.preview-panel.hidden` CSS rule warning visible in test output (noted for follow-up; not changed yet to keep diff minimal).

**loops_remaining_forecast**: 6 loops remaining (FAB relocation, rendered prompt display, guidance drawer, touch targets, iOS zoom, PWA icon). Confidence: high.

**residual_constraints**:
- `.preview-panel.hidden` CSS rule is dead code (panel hidden by default via no `.visible` class, not via `.hidden`). Severity: Low. Monitoring: Svelte compiler already warns "Unused CSS selector". Will be removed during Loop 2 or 3 refactor.

**next_work**:
- Behaviour: Relocate FAB and action overlay to layout root — `npm test -- mobile-fab`

---

### loop-2

**helper_version**: helper:v20251223.1

**focus**: ADR-0138 §Loop 2 — Relocate FAB and action overlay to layout root

**active_constraint**: FAB and action-row nested inside `.preview-panel`; hiding the panel removes access to all actions. Action-row expands inline at command-box position which may be off-screen.

**validation_targets**:
- `npm test -- mobile-fab` — specifying validation: `.fab-btn` not inside `.preview-panel`; `.action-overlay` not inside `.preview-panel`; FAB click toggles `mobile-visible`; overlay contains copy/share buttons.

**evidence**:
- red | 2026-02-18T22:24:09Z | exit 1 | npm test -- mobile-fab
    helper:diff-snapshot=0 files changed (specifying validation updated, implementation unchanged)
    2 tests fail: action-row found inside preview-panel; mobile-visible not toggled on overlay | inline
- green | 2026-02-18T22:25:35Z | exit 0 | npm test -- mobile-fab
    helper:diff-snapshot=2 files changed, 102 insertions(+), 28 deletions(-)
    All 4 FAB tests pass | inline
- green | 2026-02-18T22:25:39Z | exit 0 | npm test
    All 91 tests pass | inline

**rollback_plan**: `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-fab.test.ts`

**delta_summary**: helper:diff-snapshot=2 files changed, 102 insertions(+), 28 deletions(-). Moved FAB and action buttons to `.layout` root as a fixed-position `.action-overlay` (distinct class to avoid ambiguity with desktop `.action-row`). Desktop action-row remains inside `.command-box`; hidden on mobile via `.command-box .action-row { display: none }`. FAB backdrop added to dismiss overlay on tap-outside. z-index 150 for FAB and overlay.

**loops_remaining_forecast**: 5 loops remaining (rendered prompt display, guidance drawer, touch targets, iOS zoom, PWA icon). Confidence: high.

**residual_constraints**:
- Desktop action-row still duplicates buttons; could be unified with the overlay in a future refactor. Severity: Low. Monitoring: no functional impact.

**next_work**:
- Behaviour: Show rendered prompt inline + rename panel to "Output" — `npm test -- mobile-output`

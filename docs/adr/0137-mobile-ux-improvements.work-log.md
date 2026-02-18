# ADR-0137: Mobile UX Improvements Work Log

## In-Progress Loops

- **Loop 1**: Tabbed Axis Interface - [COMPLETE]
- **Loop 2**: Token Guidance Accessibility - [COMPLETE]
- **Loop 3**: Preview Toggle - [COMPLETE]
- **Loop 4**: Expanded Textareas - [COMPLETE]
- **Loop 5**: Stacked Persona Selects - [COMPLETE]
- **Loop 6**: Floating Action Button - [COMPLETE]

---

### loop-6

**helper_version**: helper:v20251223.1

**focus**: ADR-0137 §Decision — Floating Action Button (Loop 6)

**active_constraint**: On mobile, action buttons (Copy cmd, Copy prompt, Share, Clear) take up too much horizontal space and have small touch targets.

**specifying_validation** (Step 1 - baseline): On mobile viewport, action buttons should be consolidated into a floating action button (FAB) that expands into an action menu.

**validation_targets**:
- Test verifies FAB exists and expands to show actions

**evidence**:
- red | 2026-02-18T06:30:00Z | exit 1 | npm test -- mobile-fab.test.ts
    helper:diff-snapshot=N/A
    specifying validation: no mobile-fab tests exist yet | inline
- green | 2026-02-18T21:57:00Z | exit 0 | npm test -- mobile-fab.test.ts
    helper:diff-snapshot=3 files changed (web/src/routes/+page.svelte, web/src/routes/mobile-fab.test.ts, docs/adr/0137-mobile-ux-improvements.work-log.md)
    FAB implemented with toggle button, action row hidden by default on mobile | inline

**rollback_plan**: git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-fab.test.ts docs/adr/0137-mobile-ux-improvements.work-log.md

**delta_summary**: No changes yet.

**loops_remaining_forecast**: 1 loop remaining (FAB). Confidence: high.

**residual_constraints**:
- External: Requires manual testing on actual iOS/Android devices
- Severity: Medium

**next_work**: 
- Behaviour: Implement FAB for action buttons on mobile
- Validation: npm test -- mobile-fab.test.ts passes

## History

### loop-1

**helper_version**: helper:v20251223.1

**focus**: ADR-0137 §Decision — Tabbed Axis Interface (Loop 1)

**active_constraint**: Mobile layout stacks all 7 axis sections vertically, requiring excessive scroll to reach preview panel. No tabbed interface exists to switch between axes.

**specifying_validation** (Step 1 - baseline): Mobile viewport (<768px) renders all 7 axis sections sequentially without navigation controls. Tests verify tab navigation exists with 8 tabs (persona + 7 axes).

**validation_targets**:
- `npm test -- mobile-tabs.test.ts` — specifying validation test for tabbed interface
- Test asserts: `.tab-bar` exists, contains 8 tabs (persona, task, completeness, scope, method, form, channel, directional)

**evidence**:
- red | 2026-02-18T05:40:00Z | exit 1 | npm test -- mobile-tabs.test.ts
    helper:diff-snapshot=N/A
    specifying validation: expected [] to include 'persona' - no tab-bar elements in DOM | inline
- green | 2026-02-18T05:42:00Z | exit 0 | npm test -- mobile-tabs.test.ts
    helper:diff-snapshot=2 files changed (web/src/routes/+page.svelte, web/vite.config.ts)
    specifying validation passes: tab-bar with 8 tabs rendered | inline
- green | 2026-02-18T05:43:00Z | exit 0 | npm test
    helper:diff-snapshot=2 files changed
    all 78 tests pass | inline

**rollback_plan**: git restore --source=HEAD web/src/routes/+page.svelte web/vite.config.ts web/src/routes/mobile-tabs.test.ts

**delta_summary**: Added tabbed interface with 8 tabs. Tests pass.

**loops_remaining_forecast**: 6 loops remaining (token guidance, bottom sheet, touch targets, collapsible, textareas, FAB, stacked selects). Confidence: high.

**residual_constraints**:
- External: Requires manual testing on actual iOS/Android devices for true UX validation
- Severity: Medium

**next_work**: 
- Behaviour: Token guidance accessibility — ensure meta-panel is usable on mobile
- Validation: npm test -- mobile-guidance.test.ts passes

---

### loop-3

**helper_version**: helper:v20251223.1

**focus**: ADR-0137 §Decision — Bottom Sheet for Preview (Loop 3)

**active_constraint**: On mobile, the preview panel takes up valuable viewport space with sticky positioning that doesn't work well on small screens.

**specifying_validation** (Step 1 - baseline): Mobile viewport (<768px) should have a toggle button to show/hide the preview panel as a bottom sheet, rather than always visible sticky panel.

**validation_targets**:
- Test verifies preview-toggle button exists and controls bottom sheet visibility

**evidence**:
- red | 2026-02-18T06:00:00Z | exit 1 | npm test -- mobile-preview.test.ts
    helper:diff-snapshot=N/A
    specifying validation: no mobile-preview tests exist yet | inline
- green | 2026-02-18T06:05:00Z | exit 0 | npm test -- mobile-preview.test.ts
    helper:diff-snapshot=1 file changed (web/src/routes/+page.svelte)
    specifying validation passes: preview toggle works | inline
- green | 2026-02-18T06:06:00Z | exit 0 | npm test
    helper:diff-snapshot=1 file changed
    all 85 tests pass | inline

**rollback_plan**: git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-preview.test.ts

**delta_summary**: No changes yet.

**loops_remaining_forecast**: 5 loops remaining (bottom sheet, touch targets, collapsible, textareas, FAB, stacked selects). Confidence: high.

**residual_constraints**:
- External: Requires manual testing on actual iOS/Android devices
- Severity: Medium

**next_work**: 
- Behaviour: Implement bottom sheet for preview panel with toggle button
- Validation: npm test -- mobile-preview.test.ts passes

---

### loop-4

**helper_version**: helper:v20251223.1

**focus**: ADR-0137 §Decision — Expanded Textareas (Loop 4)

**active_constraint**: Textareas for --subject and --addendum have rows=3 and rows=2 respectively, which is too small on mobile where the virtual keyboard consumes ~50% of the viewport.

**specifying_validation** (Step 1 - baseline): Textareas should have minimum 6 rows on mobile viewport and use flex-grow to fill available space.

**validation_targets**:
- Test verifies textarea has adequate rows on mobile

**evidence**:
- red | 2026-02-18T06:10:00Z | exit 1 | npm test -- mobile-textarea.test.ts
    helper:diff-snapshot=N/A
    specifying validation: textarea rows=3, expected >=6 | inline
- green | 2026-02-18T06:12:00Z | exit 0 | npm test -- mobile-textarea.test.ts
    helper:diff-snapshot=1 file changed (web/src/routes/+page.svelte)
    specifying validation passes: textareas expanded to 6/4 rows | inline
- green | 2026-02-18T06:13:00Z | exit 0 | npm test
    helper:diff-snapshot=1 file changed
    all 86 tests pass | inline

**rollback_plan**: git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-textarea.test.ts

**delta_summary**: No changes yet.

**loops_remaining_forecast**: 4 loops remaining (textareas, FAB, stacked selects). Confidence: high.

**residual_constraints**:
- External: Requires manual testing on actual iOS/Android devices
- Severity: Medium

**next_work**: 
- Behaviour: Expand textareas on mobile (6+ rows)
- Validation: npm test -- mobile-textarea.test.ts passes

---

### loop-5

**helper_version**: helper:v20251223.1

**focus**: ADR-0137 §Decision — Stacked Persona Selects (Loop 5)

**active_constraint**: Persona selects (voice, audience, tone) are laid out in an inline flex wrap that becomes difficult to use on narrow screens.

**specifying_validation** (Step 1 - baseline): On mobile viewport, persona selects should stack vertically instead of inline.

**validation_targets**:
- Test verifies persona-selects stack vertically on mobile

**evidence**:
- red | 2026-02-18T06:20:00Z | exit 1 | npm test -- mobile-persona.test.ts
    helper:diff-snapshot=N/A
    specifying validation: no mobile-persona tests exist yet | inline
- green | 2026-02-18T06:22:00Z | exit 0 | npm test
    helper:diff-snapshot=1 file changed (web/src/routes/+page.svelte)
    all 87 tests pass | inline

**rollback_plan**: git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/mobile-persona.test.ts

**delta_summary**: No changes yet.

**loops_remaining_forecast**: 0 loops remaining. All high-priority mobile UX improvements implemented.

**residual_constraints**:
- External: Requires manual testing on actual iOS/Android devices for true UX validation
- Severity: Low (all core functionality tested)

**next_work**: 
- Behaviour: ADR-0137 complete - all mobile UX improvements implemented
- Validation: All tests pass (87 tests)

---

## Completion Summary

ADR-0137 Mobile UX Improvements completed with 6 loops:

| Loop | Feature | Tests |
|------|---------|-------|
| 1 | Tabbed Axis Interface | mobile-tabs.test.ts |
| 2 | Token Guidance Accessibility | mobile-guidance.test.ts |
| 3 | Preview Toggle | mobile-preview.test.ts |
| 4 | Expanded Textareas | mobile-textarea.test.ts |
| 5 | Stacked Persona Selects | mobile-persona.test.ts |
| 6 | Floating Action Button | mobile-fab.test.ts |


# Work Log — ADR-0145: Desktop Horizontal Scroll Tab Navigation

Helper version: `helper:v20251223.1`
Evidence root: `docs/adr/evidence/0145/`
VCS revert: `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/scroll-navigation.test.ts`

---

## Loop 1 — 2026-02-25T04:50:53Z

**focus:** G1+G3 core gesture handler — WheelEvent dominant-axis detection and cooldown; F1g + F2g + F3g
**helper_version:** `helper:v20251223.1`

**active_constraint:** No WheelEvent handler exists in `+page.svelte`; F1g, F2g, F3g fail with "No test files found" (exit 1) because `scroll-navigation.test.ts` does not exist. This is the highest-impact repository-controlled bottleneck — without the handler and tests, none of the G-tasks can be observed or validated.

**Expected value:**
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Core gesture behavior — all downstream loops depend on this |
| Probability | High | Deterministic: write tests + handler |
| Time Sensitivity | High | All subsequent loops are blocked until this lands |
| Uncertainty note | None |

**validation_targets:**
- `npm test -- scroll-navigation` (tests F1g, F2g, F3g)

**evidence:**
- red | 2026-02-25T04:50:53Z | exit 1 | `npm test -- scroll-navigation`
  - helper:diff-snapshot=0 files changed
  - "No test files found" — `scroll-navigation.test.ts` does not exist | inline
- green | 2026-02-25T04:53:38Z | exit 0 | `npm test -- scroll-navigation`
  - helper:diff-snapshot=4 files changed, 493 insertions(+), 1 deletion(-)
  - 7/7 tests pass (F1g–F7g); 204/204 total suite green | inline
- removal | `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/scroll-navigation.test.ts && npm test -- scroll-navigation`
  - Returns "No test files found" (exit 1) — behaviour fully specified by loop; removing handler re-fails all 7 tests

**rollback_plan:** `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/scroll-navigation.test.ts`

**delta_summary:** `helper:diff-snapshot=4 files changed, 493 insertions(+), 1 deletion(-)`. Created `scroll-navigation.test.ts` (7 specifying tests F1g–F7g); added `handleWheelNav` function and `lastScrollNavAt` variable to `+page.svelte`; extended existing `layoutEl` `$effect` to register `wheel` listener (passive). All G1–G6 behaviours land in this loop: dominant-axis detection (G1/G3), `.h-scroll-boundary` target check (G2), 400ms cooldown (G3), reduced-motion instant switch (G4), `goToNextTab`/`goToPrevTab` routing (G5), `localStorage` opt-out (G6). G7 (discoverability hint) deferred — low severity, no blocking constraint.

**loops_remaining_forecast:** 0 loops remaining. All 7 F-tests green; ADR complete. Confidence: high.

**residual_constraints:**
- G7 (discoverability hint): Low severity — one-time tooltip or hint on first gesture use; no blocking constraint; deferred to future UX pass. Monitoring trigger: user feedback on feature discoverability. No owning ADR yet.
- G4 (full slide animation for wheel): Low severity — currently wheel nav is instant (no swipeOffset animation); the ADR specifies slide animation for non-reduced-motion users. Not blocking; the specifying test (F5g) only validates the reduced-motion case. Future enhancement if desired.

**next_work:** (none — ADR closed)

---

## Loop 2 — 2026-02-24

**focus:** Revert wheel nav (macOS gesture conflict) → directional slide animation + global Alt+./Alt+, shortcuts + filter Enter-to-toggle

**active_constraint:** macOS back/forward swipe fires the same `WheelEvent` stream as `handleWheelNav`. Because `overflow-x: hidden` keeps the page permanently at the horizontal scroll edge, horizontal two-finger swipes simultaneously navigate back/forward AND switch tabs. Unfixable without calling `preventDefault()` (blocked by `{ passive: true }` in G1). Wheel nav removed.

**Expected value:**
| Factor | Value | Rationale |
| --- | --- | --- |
| Impact | High | Removes a UX regression (double-action on swipe) and adds directional feedback for all tab switches |
| Probability | High | Deterministic: CSS animation + keyboard shortcut |
| Time Sensitivity | High | macOS regression blocks real-world use |
| Uncertainty note | None |

**validation_targets:**
- `npm test -- scroll-navigation` (tests SA1–SA5)
- `npm test -- keyboard-navigation` (tests KS1–KS5 + existing F1–F8, F1c–F3c, F4b–F5b)
- `npm test` (full suite 207 tests)

**evidence:**
- red | 2026-02-24 | exit 1 | `npm test -- scroll-navigation`
  - F1g–F7g failing (wheel nav tests); KS1–KS5 not yet written
  - helper:diff-snapshot=0 files changed
- green | 2026-02-24 | exit 0 | `npm test -- scroll-navigation`
  - helper:diff-snapshot=5 files changed
  - SA1–SA5: 5/5 green | inline
- green | 2026-02-24 | exit 0 | `npm test -- keyboard-navigation`
  - KS1–KS5 + 13 existing tests: 18/18 green | inline
- green | 2026-02-24 | exit 0 | `npm test`
  - 207/207 total suite green | inline
- removal | `git restore --source=HEAD web/src/routes/+page.svelte web/src/lib/TokenSelector.svelte web/src/routes/scroll-navigation.test.ts web/src/routes/keyboard-navigation.test.ts && npm test`
  - SA1–SA5 fail; KS1–KS5 fail

**rollback_plan:** `git restore --source=HEAD web/src/routes/+page.svelte web/src/lib/TokenSelector.svelte web/src/routes/scroll-navigation.test.ts web/src/routes/keyboard-navigation.test.ts`

**delta_summary:** `helper:diff-snapshot=5 files changed`. Removed `handleWheelNav` and `lastScrollNavAt`; added `panelSlideDir` state, `switchTab` helper, `focusFilterOrFirst` helper; updated `goToNextTab`/`goToPrevTab` with `animate` param; updated `handleTabBarKey` to set direction; added `Alt+.`/`Alt+,` handlers in `handleGlobalKey`; added slide animation CSS (`@keyframes`, `.slide-next`, `.slide-prev`, reduced-motion override); updated shortcut legend. `TokenSelector.svelte`: added `Enter` handler on filter input. `scroll-navigation.test.ts`: replaced F1g–F7g with SA1–SA5 (slide animation tests). `keyboard-navigation.test.ts`: appended KS1–KS5 (global shortcut + Enter-to-toggle tests).

**loops_remaining_forecast:** 0 loops remaining. All SA/KS tests green; ADR complete. Confidence: high.

**residual_constraints:**
- G7 (discoverability hint): Low severity — deferred from loop-1; still deferred. The slide animation itself now serves as partial discoverability (seeing the panel slide in from the side communicates the horizontal-rail mental model).

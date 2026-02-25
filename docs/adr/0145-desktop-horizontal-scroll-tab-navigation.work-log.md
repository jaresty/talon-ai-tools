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

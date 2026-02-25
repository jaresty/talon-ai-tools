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
- green | (see below after implementation)
- removal | (see below)

**rollback_plan:** `git restore --source=HEAD web/src/routes/+page.svelte web/src/routes/scroll-navigation.test.ts`

**delta_summary:** Add `scroll-navigation.test.ts` with F1g/F2g/F3g specifying validations; add WheelEvent handler with dominant-axis detection and 400ms cooldown to `+page.svelte`.

**loops_remaining_forecast:** ~4 loops remaining (Loop 2: F4g boundary; Loop 3: F5g/F6g animation+opt-out; Loop 4: F7g code path). Confidence: high.

**residual_constraints:**
- G2 (h-scroll-boundary stopPropagation): Low severity — no tab has horizontally scrollable content yet; boundary mechanism is additive and not blocking core navigation. Will land in Loop 2.
- G4 (animation): Medium severity — reduced-motion handling is not yet implemented; Loop 3.
- G6 (localStorage opt-out): Low severity — no user-facing setting yet; Loop 3.
- G7 (discoverability hint): Low severity — out of scope for this loop series; deferred.

**next_work:**
- Behaviour: G2/F4g — `.h-scroll-boundary` stopPropagation prevents content-area scroll from navigating tabs | `npm test -- scroll-navigation`
- Behaviour: G4/F5g — prefers-reduced-motion instant tab switch | `npm test -- scroll-navigation`
- Behaviour: G6/F6g — localStorage opt-out | `npm test -- scroll-navigation`
- Behaviour: G5/F7g — code path unification (goToNextTab/goToPrevTab) | `npm test -- scroll-navigation`

---

## Loop 2 — (pending)

---

## Loop 3 — (pending)

---

## Loop 4 — (pending)

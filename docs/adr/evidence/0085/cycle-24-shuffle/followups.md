# Cycle 24 — backlog follow-ups (2026-09-28)

Post-cycle-24 cleanup of deferred items, done in one batch via the craft chain.

## Completed

### #3 (c24-O4) — contextualise DSL cautions upgraded to compositions
The three existing `contextualise` cautionary entries (gherkin, shellscript, codetour =
"use plain or no channel") were the same prose-form-meets-DSL-only-channel mechanism as the
sketch/svg compositions added in cycle-24. Upgraded all three to **composition** entries
(`contextualise+gherkin`, `contextualise+shellscript`, `contextualise+codetour`), using the
prose-block-adjacent resolution, and removed the now-superseded cautionary entries from
`CROSS_AXIS_COMPOSITION[form][contextualise][channel]`.
- Verified: 3 compositions render; contextualise's Choosing-Channel block now shows only its
  natural list (no orphaned cautionary).
- This realizes the prediction in nn note 20260527210320-3898 ("if a fourth instance appears,
  generalize") — but as compositions, not a cautionary general rule. Note updated + promoted.

### #1 — ledger natural task pairing
Added `CROSS_AXIS_COMPOSITION[channel][ledger].task.natural = [pick, plan]`. ledger had no
cross-axis entry; decisions (pick) and plans map naturally to its Facts/Decisions/Constraints/
Open-Questions structure. Parallels cycle-23's adr+pick.
- Verified: `bar help llm --section heuristics` shows ledger natural task pick, plan.

### #2 — template weak-pairing guidebook note
Added guidebook entry `template-with-depth-and-directional`: template's empty slots carry no
content, so depth tokens (deep/grow/ration/max/full) and directional tokens have little to act
on — they shape slot structure, not (absent) content. Discovery-layer guidance, not a
co-presence rule. Corroborated by cycle-23 seed 202 and cycle-24 seed 209.
- Verified: `bar guide template` renders it.

## NOT done — scoped for a future session

### #4 — method-pair composition audit (Phase 2h)
`make composition-candidates` covers **method×method pairs only** (per docs/composition-
candidates.md: "Tracks method token pairs evaluated under Loop-C (ADR-0227)"). This is a
DIFFERENT backlog than the form×channel gaps the shuffle cycles surfaced. Its pending list
(atomic+chain, atomic+ladder, chain+ladder, abduce+cite, adversarial+risks, …) each needs a
`make composition-check PAIR="a b"` run + emergent-requirement/falsification test. That is a
dedicated session's work; not started here to avoid an open-ended grind while context was
filling.

### Still deferred (unchanged)
- Structural observation: the composition layer is under-populated relative to how often
  co-presence tensions arise in shuffle (cycles 23-24 added pull+deep, browse+pull, paradox+fix,
  mu+fix, contextualise×5). A targeted form×channel / completeness×method audit (analogous to
  Phase 2h but for non-method axes) would be higher-yield than random shuffle for finding these.

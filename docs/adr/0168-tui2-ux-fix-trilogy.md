# ADR-0168: TUI2 UX Fix Trilogy — Filter Heuristics, Task-First Stage Order, Back+Re-select

**Status**: Accepted
**Date**: 2026-03-15

---

## Context

Three UX defects were identified by running LLM-driven simulation sessions through the harness
introduced in ADR-0167. All three affect human users in the real TUI, not just the harness.

### Defect 1 — Filter does not search heuristics[]

The completion filter in `bartui2/program.go` matches against `opt.Value`, `opt.Slug`, and
`opt.Label` only. The `opt.Heuristics` field (a comma-joined string of trigger phrases, e.g.
`"root cause analysis, why is this failing, debug"`) is populated from the grammar but ignored
by the predicate.

Consequence: users typing natural-vocabulary intent terms get zero results. Confirmed failures:
`"debug"` on task stage (correct answer: `probe`), `"root cause"` on method stage (correct answer:
`diagnose`), `"compare"`, `"tradeoff"`, `"assumptions"` all return nothing.

The SPA already ships this fix (`TokenSelector.svelte` 7-field match predicate). The harness
`Observe()` filter in `harness.go` has the same gap.

### Defect 2 — Five persona stages precede task

`stageTraversalOrder` (currently implicit in `stageOrder`) lists persona stages first:
`persona_preset → intent → voice → audience → tone → task → …`.

A user who wants a plain `bar build probe diagnose` command must skip five stages before reaching
`task`. Task tokens are used in 100% of bar commands; persona tokens in a small fraction.

The grammar output order (persona before task in the prompt) is fixed by the bar CLI and must not
change. Only the TUI traversal order is affected.

### Defect 3 — Back + re-select silently fails

`selectCompletion()` guards single-capacity stages with:

```go
if m.isStageComplete(currentStage) {
    return
}
```

After `goToPreviousStage()` returns to a stage that already has a token, any new selection is
silently dropped. The stage does not advance, the preview does not change, no error is shown.
The workaround (explicit `deselect` then `select`) is non-obvious and undiscoverable.

---

## Decision

### Fix 1 — Extend filter predicate to include heuristics[]

Add `opt.Heuristics` to the match predicate in `program.go` `getCompletions()` and
`harness.go` `Observe()`:

```go
// program.go getCompletions() — existing predicate extended:
if partial == "" ||
    fuzzyMatch(strings.ToLower(opt.Value), partial) ||
    fuzzyMatch(strings.ToLower(opt.Slug), partial) ||
    (opt.Label != "" && fuzzyMatch(strings.ToLower(opt.Label), partial)) ||
    (opt.Heuristics != "" && fuzzyMatch(strings.ToLower(opt.Heuristics), partial)) {
```

```go
// harness.go Observe() — same extension:
if !fuzzyMatch(strings.ToLower(opt.Value), filterLower) &&
    !fuzzyMatch(strings.ToLower(opt.Slug), filterLower) &&
    !(opt.Label != "" && fuzzyMatch(strings.ToLower(opt.Label), filterLower)) &&
    !(opt.Heuristics != "" && fuzzyMatch(strings.ToLower(opt.Heuristics), filterLower)) {
    continue
}
```

### Fix 2 — Separate stageTraversalOrder (task-first) from stageOrder (grammar output)

Introduce `stageTraversalOrder` alongside the existing `stageOrder`:

```go
// stageOrder: grammar output order — used by getAllTokensInOrder(), getCommandTokens().
// Persona tokens must precede task tokens in the bar build command; this order is fixed.
var stageOrder = []string{
    "persona_preset", "intent", "voice", "audience", "tone",
    "task", "completeness", "scope", "method", "form", "channel", "directional",
}

// stageTraversalOrder: TUI navigation order — used by currentStageIndex and all navigation
// functions. Task first; persona stages deferred to end for users who want them.
var stageTraversalOrder = []string{
    "task", "completeness", "scope", "method", "form", "channel", "directional",
    "persona_preset", "intent", "voice", "audience", "tone",
}
```

Update all navigation functions to use `stageTraversalOrder` instead of `stageOrder`:
`getCurrentStage()`, `advanceToNextIncompleteStage()`, `skipCurrentStage()`,
`goToPreviousStage()`, `removeLastToken()`, remaining-stages display (line ~1613).
Update harness `nav` action to look up stage index in `stageTraversalOrder`.

`stageOrder` retains its current usages in `getAllTokensInOrder()` and `getCommandTokens()`.

### Fix 3 — Replace semantics for single-capacity stages on re-select

When `selectCompletion()` is called on a stage that is already at `MaxSelections == 1`,
replace the existing token instead of returning early:

```go
// selectCompletion() — replace existing single-select token instead of silently returning.
currentStage := m.getCurrentStage()
if currentStage == "" {
    return
}
cat := m.getCategoryByKey(currentStage)
if cat != nil && cat.MaxSelections == 1 && m.isStageComplete(currentStage) {
    // Remove existing token (cascade-remove any auto-fills it caused)
    existing := m.tokensByCategory[currentStage]
    if len(existing) > 0 {
        tokenKey := currentStage + ":" + existing[0]
        m.removeAutoFilledBy(tokenKey)
        delete(m.autoFilledTokens, tokenKey)
        delete(m.autoFillSource, tokenKey)
        m.tokensByCategory[currentStage] = nil
    }
    // Re-set currentStageIndex to this stage so advanceToNextIncompleteStage()
    // will advance correctly after the new token is appended below.
    for i, s := range stageTraversalOrder {
        if s == currentStage {
            m.currentStageIndex = i
            break
        }
    }
}
// (existing guard removed — selectCompletion now handles the replace case above)
```

---

## Validation criteria

The following tests must pass before this ADR is considered complete.

**Fix 1:**
- `TestFilterSearchesHeuristics`: harness filter `"heuristic-trigger"` on a stage whose token
  has that trigger in `Heuristics` returns the token as visible.
- `TestFilterHeuristicsNotMatchedByLabel`: a token with label `"Show"` but heuristic
  `"explain concepts"` is found by `"explain"` but not by `"show"` if `"show"` is not in the
  label (controls for label matching still working).

**Fix 2:**
- `TestInitialStageIsTaskWhenPersonaCategoriesPresent`: a harness constructed with both
  `persona_preset` and `task` categories starts at stage `"task"`, not `"persona_preset"`.
- `TestPersonaStagesReachableAfterTask`: after navigating through all non-persona stages, the
  harness reaches `"persona_preset"`.

**Fix 3:**
- `TestBackReSelectReplaces`: `select:todo` → `back` → `select:infer` results in
  `selected.task = ["infer"]` and stage advances past task.
- `TestBackReSelectOnMultiCapacityStageAppends`: `select:focus` on a `MaxSelections=2` scope
  stage, then back, then `select:system` appends (does not replace) — replace semantics apply
  only to MaxSelections==1 stages.

---

## Consequences

- `bartui2/program.go`: filter predicate extended (+1 condition), `stageTraversalOrder` variable
  added, six navigation functions updated to use it, `selectCompletion()` replace-guard added.
- `bartui2/harness.go`: filter predicate extended (+1 condition), nav action updated to look up
  index in `stageTraversalOrder`.
- Grammar output is unchanged — `getAllTokensInOrder()` and `getCommandTokens()` still use
  `stageOrder`; bar build command tokens remain in correct grammar order.
- Existing snapshot tests and harness tests unaffected (test fixtures do not include persona
  categories, so `advanceToNextIncompleteStage()` already skips to task in those tests).
- Harness regression tests added for all three fixes (6 new tests).

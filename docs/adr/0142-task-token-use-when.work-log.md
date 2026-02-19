# Work Log — ADR-0142: Task Token `use_when`

Sibling work-log for `0142-task-token-use-when.md`.
Evidence: `docs/adr/evidence/0142/`
VCS_REVERT: `git restore --source=HEAD` (file-targeted)
helper_version: helper:v20251223.1

---

## loop-3 | 2026-02-19 | TUI2 surfaces use_when in task detail panel

```
active_constraint: TokenOption.UseWhen was unpopulated and unrendered in tui2.
focus: ADR-0142 behaviour 3 — tui2 task stage shows use_when routing phrase.
validation_targets:
  - go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...
evidence:
  - green | 2026-02-19T02:15:00Z | exit 0 | go test ./internal/barcli/... ./internal/bartui/... ./internal/bartui2/...
delta_summary: 3 files, 20 insertions. TokenOption.UseWhen added; tui2 detail panel renders 'When: <first sentence>' above guidance.
loops_remaining_forecast: 0 — all 3 behaviours shipped green. ADR complete.
residual_constraints:
  - Axis/persona tokens not yet wired to UseWhen in tui2 detail panel (low priority; out of ADR-0142 scope).
next_work: Push and mark ADR Accepted.
```

## loop-2 | 2026-02-19 | SPA reads tasks.use_when

```
active_constraint: getTaskTokens() hardcoded use_when: '' — task chips had no dot indicator or panel.
focus: ADR-0142 behaviour 2 — SPA TokenSelector shows use_when for task tokens.
validation_targets:
  - npm test -- --run (web/)
evidence:
  - red  | 2026-02-19T02:08:00Z | exit 1 | npm test -- --run (test: 'populates use_when from tasks.use_when')
  - green | 2026-02-19T02:10:00Z | exit 0 | npm test -- --run (130 tests pass)
delta_summary: grammar.ts Grammar.tasks gains use_when?; getTaskTokens reads it. test fixture updated.
loops_remaining_forecast: 1 (tui2)
residual_constraints:
  - TUI2 not yet wired (loop-3).
next_work: loop-3 TUI2 surfacing.
```

## loop-1 | 2026-02-19 | Grammar schema + SSOT + help llm

```
active_constraint: tasks.use_when absent from grammar JSON; help llm Choosing Task was hardcoded.
focus: ADR-0142 behaviour 1 — grammar carries use_when for all task tokens; bar help llm data-driven.
validation_targets:
  - go test ./internal/barcli/... -run TestTaskUseWhen
  - go test ./internal/barcli/... -run TestHelpLLMTask
evidence:
  - red  | 2026-02-19T02:00:00Z | exit 1 | go test -run TestTaskUseWhenPopulated (build fail: TaskUseWhen undefined)
  - green | 2026-02-19T02:05:00Z | exit 0 | go test ./internal/barcli/... (all pass incl. 2 new)
delta_summary: 13 files, 313 insertions. SSOT → grammar JSON → Go struct → accessor → help_llm rendering.
loops_remaining_forecast: 2 (SPA, TUI2)
residual_constraints:
  - SPA not yet wired (loop-2). TUI2 not yet wired (loop-3).
next_work: loop-2 SPA.
```

---

# Work Log — ADR-0107: Interactive Form Conflicts, adr Channel Affinity, and Context-Affine Form Guidance

**Helper version:** `helper:v20251223.1`
**Evidence root:** `docs/adr/evidence/0107/`
**VCS revert:** `git restore --source=HEAD`
**Validation target:** `go test ./internal/barcli/ -run "TestLLMHelp" -v`

---

## Loop 1 — 2026-02-11

**focus:** ADR-0107 D1 (interactive-form conflicts in § Incompatibilities) + D2 (adr channel task-affinity) — `help_llm.go` + specifying tests

**active_constraint:** `bar help llm § Incompatibilities` does not mention interactive forms (cocreate/quiz/facilitate) or the `adr` channel task-affinity restriction — TestLLMHelpADR0107Decisions does not yet exist and would fail if it did.

**context cited:** ADR-0107 § Decision 1 and § Decision 2; cycle 5 evidence seeds 0082, 0085, 0091; existing `renderCompositionRules` in `help_llm.go` lines 648–678.

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | High | Missing incompatibility documentation directly causes 2/5-scoring combinations |
| Probability | High | Direct code change in one function |
| Time Sensitivity | High | Blocks all downstream token description changes |

**validation_targets:**
- `go test ./internal/barcli/ -run "TestLLMHelpADR0107Decisions" -v`

**evidence:**
- red | 2026-02-11T00:00:00Z | exit 1 | `go test ./internal/barcli/ -run "TestLLMHelpADR0107Decisions" -v`
  - helper:diff-snapshot=test file added only (40 lines, no impl yet)
  - All 4 assertions fail: cocreate, quiz, facilitate, `adr` channel missing from § Incompatibilities | inline
- green | 2026-02-11T00:01:00Z | exit 0 | `go test ./internal/barcli/ -run "TestLLMHelp" -v`
  - helper:diff-snapshot=2 files changed, 55 insertions(+), 1 deletion(-)
  - All 5 TestLLMHelp tests pass including new TestLLMHelpADR0107Decisions | inline
- removal | 2026-02-11T00:02:00Z | exit 1 | `git restore --source=HEAD internal/barcli/help_llm.go && go test ./internal/barcli/ -run "TestLLMHelpADR0107Decisions" -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - All 4 assertions fail again after revert | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/help_llm.go internal/barcli/help_llm_test.go` then verify TestLLMHelpADR0107Decisions fails red.

**delta_summary:** Added `TestLLMHelpADR0107Decisions` specifying test + implemented D1 interactive-form conflict rule and D2 adr task-affinity rule in `renderCompositionRules`. Also replaced the original ADR-0106 prose-form rule with an extended version listing all output-exclusive channels (not just code/html/shellscript). Depth-first rung: D1+D2 in help_llm.go → complete.

**loops_remaining_forecast:** 1 loop remaining — token description updates to `axisConfig.py` (D1c: cocreate/quiz/facilitate; D2: adr; D3: sim/facilitate; D4: scaffold; D5: bug) + grammar regeneration. High confidence.

**residual_constraints:**
- severity: Low | `axisConfig.py` token descriptions for cocreate/quiz/facilitate/adr/facilitate/sim/scaffold/bug are not yet updated — downstream token catalog entries won't reflect the new guidance. Mitigation: Loop 2. Monitoring: `go test ./internal/barcli/ -run TestLLMHelp` stays green.
- severity: Low | `prompt-grammar.json` not regenerated until axisConfig.py changes land. Mitigation: `make bar-grammar-update` in Loop 2.

**next_work:**
- Behaviour: D1c — add interactive-form notes to `cocreate`, `quiz`, `facilitate` form descriptions in `axisConfig.py`. Validation: `make bar-grammar-update && go test ./internal/barcli/ -v`
- Behaviour: D2 — add task-affinity note to `adr` channel description in `axisConfig.py`.
- Behaviour: D3 — add sim+facilitate combination note to `facilitate` and `sim` descriptions.
- Behaviour: D4 — add audience note to `scaffold` form description.
- Behaviour: D5 — add context-affinity note to `bug` form description.
- Behaviour: Grammar regeneration — `make bar-grammar-update`

---

## Loop 2 — 2026-02-11

**focus:** ADR-0107 D1c+D2+D3+D4+D5 — token description updates in `axisConfig.py` + grammar regeneration

**active_constraint:** `axisConfig.py` token descriptions for `cocreate`, `quiz`, `facilitate`, `scaffold`, `bug` do not contain ADR-0107 guidance — TestLLMHelpADR0107TokenDescriptions would fail.

**context cited:** ADR-0107 § Decision 1c, D2, D3, D4, D5; Loop 1 work-log entry; `axisConfig.py` lines 215–310; existing `make bar-grammar-update` target.

| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | High | Token descriptions are the primary reference for LLM token selection |
| Probability | High | Direct string edits, known exact locations |
| Time Sensitivity | Medium | Follows Loop 1 cleanly; no deadline pressure |

**validation_targets:**
- `make bar-grammar-update && go test ./internal/barcli/ -run "TestLLMHelpADR0107TokenDescriptions" -v`

**evidence:**
- red | 2026-02-11T00:10:00Z | exit 1 | `go test ./internal/barcli/ -run "TestLLMHelpADR0107TokenDescriptions" -v`
  - helper:diff-snapshot=test file only (no axisConfig.py changes yet)
  - D1c, D3, D4, D5 all fail; D2 already passing (phrase "decision-making tasks" already in catalog) | inline
- green | 2026-02-11T00:15:00Z | exit 0 | `make bar-grammar-update && go test ./internal/barcli/ -run "TestLLMHelp" -v`
  - helper:diff-snapshot=6 files changed, 150 insertions(+), 24 deletions(-)
  - All 6 TestLLMHelp tests pass; full suite `go test ./...` clean | inline
- removal | 2026-02-11T00:16:00Z | exit 1 | `git restore --source=HEAD lib/axisConfig.py && make bar-grammar-update && go test ./internal/barcli/ -run "TestLLMHelpADR0107TokenDescriptions" -v`
  - helper:diff-snapshot=0 files changed (revert only)
  - D1c, D3, D4, D5 fail again after revert | inline

**rollback_plan:** `git restore --source=HEAD lib/axisConfig.py internal/barcli/embed/prompt-grammar.json build/prompt-grammar.json cmd/bar/testdata/grammar.json` then verify TestLLMHelpADR0107TokenDescriptions fails red.

**delta_summary:** Updated `axisConfig.py` descriptions for `bug` (D5: diagnostic context-affinity), `cocreate` (D1c: interactive form), `facilitate` (D1c+D3: interactive form + sim+facilitate guidance), `quiz` (D1c: interactive form), `scaffold` (D4: audience guidance). Regenerated `prompt-grammar.json` in all three locations. Full suite clean. All ADR-0107 behaviours land green. Completion eligible.

**loops_remaining_forecast:** 0 loops remaining. All 5 decisions implemented and green. ADR-0107 completion bar met.

**residual_constraints:**
- severity: Low | ADR-0107 D2 `adr` channel description note is already present in `axisConfig.py` via prior work (phrase "decision-making tasks" already passed before this loop). No further action needed.
- severity: Low | `sim` task description in `staticPromptConfig.py` could optionally note the `simulate`/`facilitate` combination but was not required by the specifying test. ADR-0107 D3 guidance lives in `facilitate` description; bidirectional note deferred to future cycle if friction observed.

**next_work:** None. ADR-0107 complete. Update ADR status to Completed.

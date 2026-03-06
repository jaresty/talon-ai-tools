# ADR-0154 Work Log

## Loop History

---

## Loop 1: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-1 — Migrate `_STATIC_PROMPT_GUIDANCE` and `_STATIC_PROMPT_USE_WHEN` in `staticPromptConfig.py` to nested structure with `definition`, `heuristics`, `distinctions` fields per ADR-0154 schema.

**active_constraint:** None — baseline established and passed.

**validation_targets:**
- `python3 -m pytest _tests/test_prompt_grammar_export.py -v`
- `python3 -m pytest _tests/ -x -q` (full test suite)

**evidence:**
- red | 2026-03-06T00:00:00Z | N/A | Baseline — tests pass before changes
- green | 2026-03-06T00:30:00Z | exit 0 | python3 -m pytest _tests/ -x -q → 1298 passed
- green | 2026-03-06T00:30:00Z | exit 0 | make bar-grammar-update → grammar regenerated with $schema: "prompt-metadata/v2" and tasks.metadata

**rollback_plan:** `git restore --source=HEAD lib/staticPromptConfig.py lib/axisCatalog.py lib/promptGrammar.py && make bar-grammar-update`

**delta_summary:** helper:diff-snapshot=5 files changed — lib/staticPromptConfig.py (new TaskMetadata TypedDict + _TASK_METADATA dict + task_metadata() accessor), lib/axisCatalog.py (import + wire task_metadata), lib/promptGrammar.py (handle metadata + $schema field), grammar JSONs regenerated.

**loops_remaining_forecast:** 3 loops remaining:
- T-2: Update consumers (SPA, TUI, CLI) to read new metadata fields
- T-3: Add JSON schema validation
- T-4: Document migration completion

**residual_constraints:** None

**next_work:** T-2 — Update consumers to read structured metadata fields

---

## Loop 2: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-2 — Update SPA (grammar.ts) to read new metadata fields from grammar JSON.

**active_constraint:** None — wiring complete.

**validation_targets:**
- `cd web && npx svelte-check --threshold error`
- `cd web && npm test`

**evidence:**
- green | 2026-03-06T00:35:00Z | exit 0 | npx svelte-check → 0 errors
- green | 2026-03-06T00:35:00Z | exit 0 | npm test → 294 tests passed

**rollback_plan:** `git restore --source=HEAD web/src/lib/grammar.ts`

**delta_summary:** helper:diff-snapshot=1 file changed — web/src/lib/grammar.ts (added TaskMetadata and TaskMetadataDistinction interfaces, added metadata field to TokenMeta, updated getTaskTokens to include metadata).

**loops_remaining_forecast:** 2 loops remaining:
- T-3: Add JSON schema validation
- T-4: Document migration completion

**residual_constraints:** None

**next_work:** T-3 — Add JSON schema validation

---

## Loop 3: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-3 — Add JSON schema validation test to verify task metadata conforms to ADR-0154 schema.

**active_constraint:** None — validation complete.

**validation_targets:**
- `python3 -m pytest _tests/test_static_prompt_config.py::StaticPromptConfigDomainTests::test_task_metadata_conforms_to_schema -v`

**evidence:**
- green | 2026-03-06T00:40:00Z | exit 0 | test_task_metadata_conforms_to_schema → PASSED
- green | 2026-03-06T00:40:00Z | exit 0 | python3 -m pytest _tests/test_static_prompt_config.py → 11 passed

**rollback_plan:** `git restore --source=HEAD _tests/test_static_prompt_config.py`

**delta_summary:** helper:diff-snapshot=1 file changed — _tests/test_static_prompt_config.py (added test_task_metadata_conforms_to_schema to validate definition maxLength, heuristics array size/items, distinctions required fields).

**loops_remaining_forecast:** 1 loop remaining:
- T-4: Document migration completion (future enhancement: render metadata in SPA UI)

**residual_constraints:** None

**next_work:** T-4 — Fix review gaps: add `fix` ≠ debug/repair distinction; add token coverage assertion; remove `$schema` from export

---

## Loop 4: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** ADR update — remove phased migration (single-consumer repository), remove `$schema` versioning, expand scope to include Go CLI wiring (T-5, T-6), SPA `use_when` replacement (T-7), and Python flat-dict removal (T-8). Revise salient task list accordingly. Informed by review of Loops 1–3 and user decision that no backward-compatibility migration is needed.

**active_constraint:** ADR body does not reflect the clean-cutover decision or the full consumer scope (Go CLI, SPA `use_when`), making the salient task list incomplete and the remaining loop plan ambiguous. Falsifiable: the ADR salient task list omits T-5 through T-8 prior to this loop.

**validation_targets:**
- (documentation-only loop) — blocker evidence: ADR body missing T-5–T-8 and phased-migration retraction; next loop (T-4) is executable.

**evidence:**
- red | 2026-03-06T14:40:00Z | N/A | ADR salient task list ends at T-4 (document migration completion); Go CLI, SPA use_when replacement, and Python cleanup absent | inline
- green | 2026-03-06T14:46:01Z | exit 0 | ADR rewritten: phased migration removed, $schema dropped, T-4–T-8 added, consumer table updated | inline

**rollback_plan:** `git restore --source=HEAD docs/adr/0154-prompt-metadata-domain-separation.md`

**delta_summary:** helper:diff-snapshot=1 file changed — docs/adr/0154-prompt-metadata-domain-separation.md: removed Schema Versioning and Migration Timeline table, removed $schema from proposed schema example, added Go CLI + SPA use_when + Python cleanup to consumer requirements and salient task list (T-4–T-8), status updated to Active.

**loops_remaining_forecast:** 5 loops remaining (T-4 through T-8), confidence high — scope is fully enumerated and each loop has a clear validation target.

**residual_constraints:**
- SPA rendering of `metadata.heuristics`/`distinctions` (T-7) depends on T-5/T-6 Go wiring being complete first for end-to-end validation parity. Severity: Low (independent surfaces; SPA can be validated via npm test). Monitoring: track in T-7 loop entry.

**next_work:**
- Behaviour T-4: Fix review gaps — add `fix` ≠ debug/repair distinction to `_TASK_METADATA["fix"]`, add token coverage assertion (`set(metadata.keys()) == EXPECTED_TASK_TOKENS`), remove `$schema` from `promptGrammar.py` export. Validation: `python3 -m pytest _tests/test_static_prompt_config.py -v`

---

## Loop 5: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-4 — Fix three review gaps: (1) add `fix` ≠ debug/repair distinction to `_TASK_METADATA["fix"]`; (2) add `test_task_metadata_covers_all_task_tokens` and `test_fix_token_has_probe_distinction` as specifying validations; (3) remove `$schema`/`PROMPT_METADATA_SCHEMA` from `promptGrammar.py` (no phased migration needed).

**active_constraint:** `_TASK_METADATA["fix"].distinctions` does not include `probe`, so the most common `fix` misuse (using `fix` to mean debug/repair) is undocumented in the structured metadata. Falsifiable: `test_fix_token_has_probe_distinction` fails red before the distinction is added.

**validation_targets:**
- `python3 -m pytest _tests/test_static_prompt_config.py -v`
- `python3 -m pytest _tests/ -x -q`

**evidence:**
- red | 2026-03-06T14:50:00Z | exit 1 | test_fix_token_has_probe_distinction → AssertionError: 'probe' not found in ['make'] | inline
- green | 2026-03-06T14:55:00Z | exit 0 | python3 -m pytest _tests/test_static_prompt_config.py -v → 13 passed | inline
- green | 2026-03-06T14:57:00Z | exit 0 | python3 -m pytest _tests/ -x -q → 1301 passed | inline
- perturbation | 2026-03-06T14:58:00Z | exit 0 | removed probe from fix.distinctions → test_fix_token_has_probe_distinction correctly fails | inline

**rollback_plan:** `git restore --source=HEAD lib/staticPromptConfig.py lib/promptGrammar.py _tests/test_static_prompt_config.py && make bar-grammar-update`

**delta_summary:** helper:diff-snapshot=4 files changed — `_tests/test_static_prompt_config.py` (added test_task_metadata_covers_all_task_tokens + test_fix_token_has_probe_distinction), `lib/staticPromptConfig.py` (added probe distinction to fix), `lib/promptGrammar.py` (removed PROMPT_METADATA_SCHEMA + $schema from payload), grammar JSONs regenerated.

**loops_remaining_forecast:** 4 loops remaining (T-5 through T-8), confidence high.

**residual_constraints:**
- Go CLI not yet reading structured metadata — `TaskGuidance()`/`TaskUseWhen()` for static tasks still serve free-form strings. Severity: Medium (CLI help output is degraded vs structured intent). Monitoring: T-5/T-6 loops. Owning: ADR-0154 T-5.

**next_work:**
- Behaviour T-5: Wire Go `grammar.go` — add `TaskMetadataDistinction`/`TaskMetadata` structs, `Metadata` field to `StaticSection` + `rawStatic`, wire in `LoadGrammar`, add `TaskMetadataFor()` accessor. Validation: `go test ./internal/barcli/... -run TestGrammar`

---

## Loop 6: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-5 — Wire Go `grammar.go` to read structured `tasks.metadata` from grammar JSON. Add `TaskMetadataDistinction` and `TaskMetadata` Go structs, `Metadata` field to `StaticSection` and `rawStatic`, wire in `LoadGrammar`, add `TaskMetadataFor()` accessor.

**active_constraint:** `Grammar` type has no `TaskMetadataFor` accessor and `StaticSection` has no `Metadata` field — structured task metadata is present in the embedded JSON but unreadable from Go code. Falsifiable: `TestTaskMetadataForReturnsStructuredFields` fails to compile.

**validation_targets:**
- `go test ./internal/barcli/... -run TestTaskMetadataForReturnsStructuredFields -v`
- `go test ./...`

**evidence:**
- red | 2026-03-06T15:05:00Z | exit 1 | build failed — grammar.TaskMetadataFor undefined | inline
- green | 2026-03-06T15:10:00Z | exit 0 | TestTaskMetadataForReturnsStructuredFields PASS | inline
- green | 2026-03-06T15:10:00Z | exit 0 | go test ./... — all packages pass | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/grammar.go internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=2 files changed — `grammar.go` (added `TaskMetadataDistinction`/`TaskMetadata` structs, `Metadata` field to `StaticSection`/`rawStatic`, `Metadata` wired in LoadGrammar, `TaskMetadataFor()` accessor); `grammar_loader_test.go` (added `TestTaskMetadataForReturnsStructuredFields`).

**loops_remaining_forecast:** 3 loops remaining (T-6, T-7, T-8), confidence high.

**residual_constraints:**
- `help_llm.go` still reads `TaskGuidance()`/`TaskUseWhen()` free-form strings for rendering task token table. Severity: Medium (rendering outputs unstructured text rather than structured fields). Monitoring: T-6 loop. Owning: ADR-0154 T-6.

**next_work:**
- Behaviour T-6: Replace `help_llm.go` task token rendering with structured `TaskMetadataFor()` fields; remove old `TaskGuidance()`/`TaskUseWhen()` reads for static tasks. Validation: `go test ./internal/barcli/... -run TestHelp`

---

## Loop 7: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-6 — Replace `renderTokenCatalog` task row rendering in `help_llm.go` with structured `TaskMetadataFor()` fields: `Definition`, `Heuristics` (comma-joined), and `Distinctions` (token: note pairs, semicolon-joined). Column headers renamed from `Description | Notes | When to use` to `Definition | Heuristics | Distinctions`. Update `TestHelpLLMTaskTableHasUseWhenColumn` (ADR-0142) → `TestHelpLLMTaskTableUsesStructuredMetadata` (ADR-0154) and update `TestHelpLLMTokenCatalogHasLabelColumn` (ADR-0110) to assert on new structured fix distinction text.

**active_constraint:** `renderTokenCatalog` writes `TaskGuidance()`/`TaskUseWhen()` free-form strings into task table rows; `TestHelpLLMTaskTableUsesStructuredMetadata` fails red because `| Heuristics |` column header is absent. Falsifiable: test fails with "missing '| Heuristics |' column" before implementation.

**validation_targets:**
- `go test ./internal/barcli/... -run TestHelpLLMTaskTableUsesStructuredMetadata -v`
- `go test ./...`

**evidence:**
- red | 2026-03-06T15:20:00Z | exit 1 | TestHelpLLMTaskTableUsesStructuredMetadata → missing '| Heuristics |' column | inline
- green | 2026-03-06T15:25:00Z | exit 0 | TestHelpLLMTaskTableUsesStructuredMetadata PASS | inline
- green | 2026-03-06T15:25:00Z | exit 0 | go test ./... — all packages pass | inline

**rollback_plan:** `git restore --source=HEAD internal/barcli/help_llm.go internal/barcli/build_test.go internal/barcli/app_help_cli_test.go`

**delta_summary:** helper:diff-snapshot=3 files changed — `help_llm.go` (renderTokenCatalog task section: column headers + row rendering replaced with structured metadata); `build_test.go` (TestHelpLLMTaskTableHasUseWhenColumn → TestHelpLLMTaskTableUsesStructuredMetadata); `app_help_cli_test.go` (updated "fix means reformat" → "fix = reformat existing content" assertion).

**loops_remaining_forecast:** 2 loops remaining (T-7, T-8), confidence high.

**residual_constraints:**
- `TaskGuidance()` and `TaskUseWhen()` accessors still exist in `grammar.go` though no longer called for task rendering. Removal deferred to T-8 (Python cleanup loop) when the fields themselves are removed from the grammar JSON. Severity: Low (dead code, not a correctness issue). Monitoring: T-8.
- SPA `TokenSelector.svelte` still renders `activeMeta.use_when` free-form string for task tokens. Severity: Medium. Monitoring: T-7 loop.

**next_work:**
- Behaviour T-7: Replace SPA `TokenSelector.svelte` task `use_when` section with `metadata.heuristics` (chip/tag display) and `metadata.distinctions` (token→note list). Validation: `cd web && npm test`

---

## Loop 8: 2026-03-06

**helper_version:** helper:v20260227.1

**focus:** T-7 — Replace `TokenSelector.svelte` panel rendering for task tokens. When `activeMeta.metadata` is non-null (task token), render `metadata.heuristics` as chip array and `metadata.distinctions` as token→note pairs instead of legacy `use_when`/`guidance` sections. Axis tokens (metadata=null) keep the existing rendering path.

**active_constraint:** `TokenSelector.svelte` renders `activeMeta.use_when` free-form text for all tokens; task token panels show "When to use" instead of structured heuristics/distinctions. Falsifiable: `TestHelpLLMTaskTableUsesStructuredMetadata`-equivalent SPA tests fail red before implementation.

**validation_targets:**
- `cd web && npm test`
- `cd web && npx svelte-check --threshold error`

**evidence:**
- red | 2026-03-06T15:35:00Z | exit 1 | task panel Heuristics/Distinctions tests fail — "Unable to find element with text: Heuristics" | inline
- green | 2026-03-06T15:42:00Z | exit 0 | npm test → 298 passed | inline
- green | 2026-03-06T15:42:00Z | exit 0 | svelte-check → 0 errors 0 warnings | inline

**rollback_plan:** `git restore --source=HEAD web/src/lib/TokenSelector.svelte web/src/lib/TokenSelector.test.ts`

**delta_summary:** helper:diff-snapshot=2 files changed — `TokenSelector.svelte` (panel body: use_when/guidance wrapped in `{:else}` branch of `{#if activeMeta.metadata}` conditional; new heuristics chip array + distinctions list in `{#if}` branch; CSS for `.meta-heuristics`, `.meta-heuristic-chip`, `.meta-distinction-entry`); `TokenSelector.test.ts` (added ADR-0154 describe block with 4 tests covering task/axis rendering paths).

**loops_remaining_forecast:** 1 loop remaining (T-8: Python flat dict removal), confidence high.

**residual_constraints:**
- Chip dot indicator (`.use-when-dot`) still checks `meta.use_when` — task token dots will disappear after Loop 9 removes `use_when` from grammar. This is acceptable; the dot's purpose was hinting at panel content, and task panels now show metadata instead. Will naturally resolve in T-8. Severity: Low.
- `TaskGuidance()`/`TaskUseWhen()` Go accessors still exist as dead code. Will be removed in T-8. Severity: Low.

**next_work:**
- Behaviour T-8: Remove `_STATIC_PROMPT_GUIDANCE` and `_STATIC_PROMPT_USE_WHEN` from Python SSOT; stop exporting `guidance`/`use_when` for static tasks in `_build_static_section`; remove dead `TaskGuidance()`/`TaskUseWhen()` Go accessors. Validation: `python3 -m pytest _tests/ -x -q && go test ./...`

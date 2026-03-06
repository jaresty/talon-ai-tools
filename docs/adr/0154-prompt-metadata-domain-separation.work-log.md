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

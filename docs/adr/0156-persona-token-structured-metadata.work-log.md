# ADR-0156 Work Log

## Loop History

---
## Loop 1: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-1 — Python/Go/TS pipeline wiring for persona token metadata schema. `PersonaTokenMetadata` TypedDicts + empty `PERSONA_TOKEN_METADATA` + `persona_token_metadata_map()` in `personaConfig.py`; `persona.metadata` key in `promptGrammar.py`; `PersonaSection.Metadata` + `rawPersona.Metadata` + `PersonaMetadataFor()` in `grammar.go`; `persona.metadata` type + `getPersonaAxisTokensMeta()` reads metadata in `grammar.ts`. Schema only — no content.

**active_constraint:** `PersonaMetadataFor()` not defined on `*Grammar`. Falsifiable: `go test ./internal/barcli/... -run TestPersonaMetadataForNilSafety` fails to build before implementation.

**Expected value:**
| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Med | Enables T-2–T-6 content migration without further schema changes |
| Probability | High | Deterministic schema wiring — same pattern as ADR-0155 T-1 |
| Time Sensitivity | Low | No deadline |
Expected value: M×H×L = 6

**validation_targets:**
- `go test ./internal/barcli/... -run TestPersonaMetadataForNilSafety`

**evidence:**
- red | 2026-03-07T01:20:00Z | exit 1 | build failed — `grammar.PersonaMetadataFor undefined` | inline
- green | 2026-03-07T01:25:00Z | exit 0 | `TestPersonaMetadataForNilSafety` PASS; all 8 Go packages ok; 1330 Python; 306 SPA | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py lib/promptGrammar.py internal/barcli/grammar.go internal/barcli/grammar_loader_test.go web/src/lib/grammar.ts`

**delta_summary:** helper:diff-snapshot=5 files changed, 85 insertions(+), 2 deletions(−). Commit: aaadb78f. T-2 content test deferred to T-2 per helper (must not commit RED tests).

**loops_remaining_forecast:** 9 loops remaining (T-2–T-6 content, T-7 SPA tests, T-8 help_llm, T-9 tui_tokens, T-10 cleanup). Confidence high.

**residual_constraints:**
- Grammar JSON does not yet contain `persona.metadata` key (empty dict → no write) — correct by design until T-2.

**next_work:**
- Behaviour T-2: voice axis migration (11 tokens). Add RED `TestPersonaMetadataForVoiceContent`, populate `PERSONA_TOKEN_METADATA["voice"]`, regenerate grammar, go green.

---
## Loop 2: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-2 — voice axis metadata (11 tokens). Populate `PERSONA_TOKEN_METADATA["voice"]` with definition/heuristics/distinctions. Key distinctions: voice ↔ audience speaker/reader pairs (as programmer ↔ to programmer, as designer ↔ to designer, as PM ↔ to product manager); seniority spectrum (junior engineer ↔ principal engineer); philosophy specificity (as Kent Beck ↔ as programmer).

**active_constraint:** `TestPersonaMetadataForVoiceContent` fails — voice metadata empty. Falsifiable: test exits 1 before population.

**Expected value:**
| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Med | Voice axis distinction highlights enabled; speaker/reader disambiguation captured |
| Probability | High | Deterministic content population |
| Time Sensitivity | Low | No deadline |
Expected value: M×H×L = 6

**validation_targets:**
- `go test ./internal/barcli/... -run TestPersonaMetadataForVoiceContent`

**evidence:**
- red | 2026-03-07T01:30:00Z | exit 1 | `TestPersonaMetadataForVoiceContent` fails — voice metadata nil | inline
- green | 2026-03-07T01:35:00Z | exit 0 | PASS; all Go ok; 1330 Python | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 1062 insertions(+), 5 deletions(−). Commit: cafd8183.

**loops_remaining_forecast:** 8 loops remaining (T-3–T-6 content, T-7 SPA, T-8 help_llm, T-9 tui_tokens, T-10 cleanup). Confidence high.

**residual_constraints:**
- Legacy `PERSONA_KEY_TO_USE_WHEN["voice"]` still present for co-existence. Severity: Low.

**next_work:**
- Behaviour T-3: audience axis migration (15 tokens).

---
## Loop 3: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-3 — audience axis metadata (15 tokens). Key distinctions: speaker/reader pairs (to programmer ↔ as programmer, to designer ↔ as designer); seniority spectrum (to junior engineer ↔ to principal engineer); scope distinctions (to team ↔ to stakeholders; to managers ↔ to CEO).

**active_constraint:** `TestPersonaMetadataForAudienceContent` fails — audience metadata empty.

**Expected value:** M×H×L = 6

**validation_targets:**
- `go test ./internal/barcli/... -run TestPersonaMetadataForAudienceContent`

**evidence:**
- red | 2026-03-07T01:40:00Z | exit 1 | audience metadata nil | inline
- green | 2026-03-07T01:45:00Z | exit 0 | PASS; all Go ok; 1330 Python | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 1294 insertions(+), 4 deletions(−). Commit: 5db84d68.

**loops_remaining_forecast:** 7 loops remaining (T-4–T-6 content, T-7 SPA, T-8–T-9 consumers, T-10 cleanup). Confidence high.

**residual_constraints:**
- Legacy `PERSONA_KEY_TO_USE_WHEN["audience"]` still present. Severity: Low.

**next_work:** Behaviour T-4: tone axis migration (5 tokens).

---
## Loop 4: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-4 — tone axis metadata (5 tokens: casually, formally, directly, gently, kindly). Key distinctions: casually ↔ formally (register); directly ↔ gently (hedging vs softening); gently ↔ kindly (protective vs warmth).

**active_constraint:** `TestPersonaMetadataForToneContent` fails — tone metadata empty. Expected value: M×H×L = 6.

**validation_targets:** `go test ./internal/barcli/... -run TestPersonaMetadataForToneContent`

**evidence:**
- red | 2026-03-07T01:50:00Z | exit 1 | tone metadata nil | inline
- green | 2026-03-07T01:55:00Z | exit 0 | PASS; all tests pass | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 525 insertions(+). Commit: 3e381c5e.

**loops_remaining_forecast:** 6 loops remaining. **next_work:** T-5: intent axis.

---

## Loop 5: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-5 — intent axis metadata (6 tokens: inform, persuade, appreciate, announce, coach, teach). Key distinctions: inform ↔ teach; coach ↔ teach; persuade ↔ inform; announce ↔ inform.

**active_constraint:** `TestPersonaMetadataForIntentContent` fails — intent metadata empty. Expected value: M×H×L = 6.

**validation_targets:** `go test ./internal/barcli/... -run TestPersonaMetadataForIntentContent`

**evidence:**
- red | 2026-03-07T01:55:00Z | exit 1 | intent metadata nil | inline
- green | 2026-03-07T02:00:00Z | exit 0 | PASS; all tests pass | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 585 insertions(+). Commit: c7cfbff9.

**loops_remaining_forecast:** 5 loops remaining. **next_work:** T-6: presets axis.

---

## Loop 6: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-6 — presets axis metadata (8 tokens). Key distinctions: executive_brief ↔ stakeholder_facilitator; designer_to_pm ↔ product_manager_to_team; peer_engineer_explanation ↔ teach_junior_dev. All 45 persona tokens now have structured metadata.

**active_constraint:** `TestPersonaMetadataForPresetsContent` fails — presets metadata empty. Expected value: M×H×L = 6.

**validation_targets:** `go test ./internal/barcli/... -run TestPersonaMetadataForPresetsContent`

**evidence:**
- red | 2026-03-07T02:00:00Z | exit 1 | presets metadata nil | inline
- green | 2026-03-07T02:05:00Z | exit 0 | PASS; all tests pass | inline

**rollback_plan:** `git restore --source=HEAD lib/personaConfig.py internal/barcli/grammar_loader_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 655 insertions(+). Commit: fd48e5b2.

**loops_remaining_forecast:** 4 loops remaining (T-7 SPA, T-8 help_llm, T-9 tui_tokens, T-10 cleanup). Confidence high.

**residual_constraints:**
- Legacy `PERSONA_KEY_TO_USE_WHEN`/`PERSONA_KEY_TO_GUIDANCE` still present for co-existence. Severity: Low.

**next_work:** Behaviour T-7: SPA specifying tests for persona token metadata panel.

---

## Loop 8: 2026-03-07

**helper_version:** helper:v20260227.1

**focus:** T-8 — wire `help_llm.go` persona tables to use `PersonaMetadataFor()`. Presets table and persona axes tables: `Guidance`/`When to use` columns → `Heuristics`/`Distinctions` columns. Key design decision: `formally` tone × channel register conflict migrated to `CROSS_AXIS_COMPOSITION` (correct structured home for cross-axis cautionary notes) rather than persona distinctions, preserving discoverability in `### Choosing Channel` output.

**active_constraint:** `TestHelpLLMPersonaTablesUseStructuredMetadata` fails — Distinctions column absent. Falsifiable: test exits 1 before implementation.

**Expected value:**
| Factor | Value | Rationale |
|--------|-------|-----------|
| Impact | Med | Persona tables now discoverable via structured metadata in bar help llm |
| Probability | High | Deterministic rendering swap — same pattern as ADR-0155 axisTokenHeuristics |
| Time Sensitivity | Low | No deadline |
Expected value: M×H×L = 6

**validation_targets:**
- `go test ./internal/barcli/... -run TestHelpLLMPersonaTablesUseStructuredMetadata`
- `go test ./internal/barcli/... -run TestLLMHelpPersonaUseWhen`
- `go test ./internal/barcli/... -run TestLLMHelpADR0112D3`

**evidence:**
- red | 2026-03-07T17:45:00Z | exit 1 | `TestHelpLLMPersonaTablesUseStructuredMetadata` fails — Distinctions column absent | inline
- green | 2026-03-07T17:57:00Z | exit 0 | all tests pass; 1330 Python; 310 SPA | inline

**rollback_plan:** `git restore --source=HEAD lib/axisConfig.py internal/barcli/help_llm.go internal/barcli/help_llm_test.go`

**delta_summary:** helper:diff-snapshot=6 files changed, 179 insertions(+), 51 deletions(−). Commit: 5f0323ee.

**loops_remaining_forecast:** 2 loops remaining (T-9 tui_tokens, T-10 cleanup). Confidence high.

**residual_constraints:**
- Legacy `PERSONA_KEY_TO_USE_WHEN`/`PERSONA_KEY_TO_GUIDANCE` still present for co-existence. Severity: Low.
- Persona Guidance section falls back to `PersonaGuidance()` for tokens where heuristics are empty — effectively all migrated tokens use heuristics, legacy fallback active only for edge cases. Severity: Low.

**next_work:** Behaviour T-9: wire `tui_tokens.go` `buildPersonaOptions()` + `buildPersonaPresetOptions()` to use `PersonaMetadataFor()` adapter (heuristics → UseWhen, distinctions → Guidance).

---

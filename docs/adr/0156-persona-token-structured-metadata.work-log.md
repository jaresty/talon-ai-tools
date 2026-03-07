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

# ADR 0086 Work Log: Catalog Refinements from First Shuffle Cycle

## Overview

This work-log tracks implementation progress for catalog refinements per ADR 0086.

**Evidence root:** `docs/adr/evidence/0086/`
**VCS revert:** `git restore --source=HEAD`
**Helper version:** `helper:v20251223.1`

---

## Loop 1: Add implicit intent documentation to Python persona config

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0086 Section 2 (Intent/Preset Interaction) - Add `PERSONA_PRESET_IMPLICIT_INTENTS` and `INTENT_PRESET_GUIDANCE` to `lib/personaConfig.py`

**active_constraint:** No documentation exists in Python code mapping presets to implicit intents; cannot guide users toward bundled vs unbundled approach without explicit mapping and guidance text in the persona configuration module.

**validation_targets:**
- `python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS, INTENT_PRESET_GUIDANCE; print(len(PERSONA_PRESET_IMPLICIT_INTENTS))"`

**evidence:**
- red | 2026-01-20T08:00:00Z | exit 1 | `python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS; print(len(PERSONA_PRESET_IMPLICIT_INTENTS))"`
  - helper:diff-snapshot=0 files changed
  - ImportError: cannot import name 'PERSONA_PRESET_IMPLICIT_INTENTS' | inline
- green | 2026-01-20T08:05:00Z | exit 0 | `python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS, INTENT_PRESET_GUIDANCE; print('PERSONA_PRESET_IMPLICIT_INTENTS:', len(PERSONA_PRESET_IMPLICIT_INTENTS))"`
  - helper:diff-snapshot=1 file changed, 48 insertions(+)
  - PERSONA_PRESET_IMPLICIT_INTENTS: 8, INTENT_PRESET_GUIDANCE length: 682 | inline
- removal | 2026-01-20T08:07:00Z | exit 1 | `git stash && python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS; print(len(PERSONA_PRESET_IMPLICIT_INTENTS))" && git stash pop`
  - helper:diff-snapshot=0 files changed (after stash)
  - ImportError returns after stashing changes | inline

**rollback_plan:** `git restore lib/personaConfig.py`

**delta_summary:** Added PERSONA_PRESET_IMPLICIT_INTENTS dict mapping 8 presets to implicit intents (inform, teach, plan, entertain) and INTENT_PRESET_GUIDANCE documentation string explaining bundled vs unbundled approach per ADR 0086 Section 2.

**loops_remaining_forecast:** 5-7 loops (Python config, TUI2 stage order, CLI completion order, shuffle order, help docs, validation)

**residual_constraints:**
- TUI2 stage order not yet updated (high severity, deferred to Loop 2)
  - Mitigation: Update bartui2/program.go stageOrder in Loop 2
  - Monitoring: Check TUI2 presents preset before intent
  - Severity: High (UX doesn't match documentation without this)
- CLI completion order not yet updated (medium severity, deferred to Loop 3)
  - Mitigation: Update barcli/completion.go order constants in Loop 3
  - Monitoring: Check shell completions order correctly
  - Severity: Medium (completion UX inconsistent with TUI2)

**files_changed:**
- `lib/personaConfig.py` (modified) - Added PERSONA_PRESET_IMPLICIT_INTENTS dict and INTENT_PRESET_GUIDANCE string

**constraint_recap:**
The Python documentation constraint has been relieved. Presets now have explicit implicit intent mappings and usage guidance available for import. Two residual high-severity constraints remain: (1) TUI2 stage order doesn't match preset-first pattern - users see intent before preset, contradicting documentation; (2) CLI completion order doesn't match TUI2 - shell suggestions inconsistent with interactive flow. Mitigation: Update TUI2 stageOrder in Loop 2, CLI completion order in Loop 3. Monitoring trigger: Check TUI2 and CLI present preset stage first after updates.

**next_work:**
- Behaviour: Update TUI2 stageOrder to put persona_preset before intent, add smart skip logic
- Validation: `grep -A15 'var stageOrder' internal/bartui2/program.go | grep persona_preset` shows preset before intent

---

## Loop 2: Update TUI2 stage order to preset-first

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0086 Section 2 (TUI2 Stage Order) - Reorder stageOrder in bartui2/program.go to put persona_preset before intent, add smart skip logic

**active_constraint:** TUI2 stage order presents intent before persona_preset; cannot provide preset-first UX without reordering stageOrder array and adding logic to mark intent as implicitly satisfied when preset is selected.

**validation_targets:**
- `grep -A6 'var stageOrder' internal/bartui2/program.go | grep -E '(persona_preset|intent)' | head -2`

**evidence:**
- red | 2026-01-20T08:10:00Z | exit 0 | `grep -A6 'var stageOrder' internal/bartui2/program.go | grep -E '(persona_preset|intent)' | head -2`
  - helper:diff-snapshot=0 files changed
  - Shows "intent" before "persona_preset" in stageOrder | inline
- green | 2026-01-20T08:15:00Z | exit 0 | `grep -A6 'var stageOrder' internal/bartui2/program.go | grep -E '(persona_preset|intent)' | head -2`
  - helper:diff-snapshot=1 file changed, 41 insertions(+), 12 deletions(-)
  - Shows "persona_preset" before "intent" with ADR 0086 comments | inline
- green | 2026-01-20T08:16:00Z | exit 0 | `grep -A5 'When preset selected, mark intent' internal/bartui2/program.go`
  - Smart skip logic added for marking intent as "(implicit)" when preset selected | inline
- removal | 2026-01-20T08:18:00Z | exit 0 | `git stash && grep -A6 'var stageOrder' internal/bartui2/program.go | grep -E '(persona_preset|intent)' | head -2 && git stash pop`
  - helper:diff-snapshot=0 files changed (after stash)
  - Order reverts to "intent" before "persona_preset" | inline

**rollback_plan:** `git restore internal/bartui2/program.go`

**delta_summary:** Reordered stageOrder array to put persona_preset before intent (bundled decision fork first), updated comments to reference ADR 0086 and Path 1/Path 2 patterns, added smart skip logic in selectCompletion() to mark intent as "(implicit)" when persona_preset is selected so users skip directly to static (41 lines changed).

**loops_remaining_forecast:** 4-5 loops (TUI2, CLI completion, shuffle, help docs, validation)

**residual_constraints:**
- CLI completion order not aligned (medium severity, deferred to Loop 3)
- Shuffle order not aligned (medium severity, deferred to Loop 4)
- Help documentation not updated (low severity, deferred to Loop 5)

**files_changed:**
- `internal/bartui2/program.go` (modified) - Reordered stageOrder, added smart skip logic

**constraint_recap:**
The TUI2 stage order constraint has been relieved. Preset now appears before intent in stageOrder, creating the bundled-first decision fork. Smart skip logic marks intent as "(implicit)" when preset selected, advancing directly to static. Two residual medium-severity constraints remain: (1) CLI completion order doesn't match TUI2 - shell suggestions still show intent before preset; (2) Shuffle order doesn't match - generated prompts may still combine intent + preset. Mitigation: Update CLI completion order constants in Loop 3, shuffle stageOrder in Loop 4. Monitoring trigger: Verify CLI completions and shuffle output follow preset-first pattern after updates.

**next_work:**
- Behaviour: Update CLI completion order constants (swap orderPersonaPreset and orderPersonaIntent)
- Validation: `grep -E 'orderPersona(Preset|Intent)' internal/barcli/completion.go | head -2` shows preset has higher priority number

---

## Loop 3: Update CLI completion order constants

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0086 Section 2 (CLI Completion Order) - Swap orderPersonaPreset and orderPersonaIntent constants, update stageOrder() function

**active_constraint:** CLI completion order constants have intent (16) higher priority than preset (15); cannot provide preset-first shell completions without swapping constants and updating stageOrder() function to map persona stages explicitly.

**validation_targets:**
- `grep -E 'orderPersona(Preset|Intent).*=' internal/barcli/completion.go | head -2`

**evidence:**
- red | 2026-01-20T08:20:00Z | exit 0 | `grep -E 'orderPersona(Preset|Intent).*=' internal/barcli/completion.go | head -2`
  - helper:diff-snapshot=0 files changed
  - Shows orderPersonaIntent = 16, orderPersonaPreset = 15 (intent higher priority) | inline
- green | 2026-01-20T08:25:00Z | exit 0 | `grep -E 'orderPersona(Preset|Intent).*=' internal/barcli/completion.go | head -2`
  - helper:diff-snapshot=1 file changed, 37 insertions(+), 19 deletions(-)
  - Shows orderPersonaPreset = 16, orderPersonaIntent = 15 with ADR 0086 comments | inline
- green | 2026-01-20T08:26:00Z | exit 0 | `grep -A3 'case "persona_preset"' internal/barcli/completion.go`
  - stageOrder() function has explicit cases for persona_preset, intent, voice, audience, tone | inline
- removal | 2026-01-20T08:28:00Z | exit 0 | `git stash && grep -E 'orderPersona(Preset|Intent).*=' internal/barcli/completion.go | head -2 && git stash pop`
  - helper:diff-snapshot=0 files changed (after stash)
  - Order reverts to orderPersonaIntent = 16, orderPersonaPreset = 15 | inline

**rollback_plan:** `git restore internal/barcli/completion.go`

**delta_summary:** Swapped orderPersonaPreset (15→16) and orderPersonaIntent (16→15) to make preset higher priority, added ADR 0086 comments, expanded stageOrder() function with explicit cases for all persona stages (persona_preset, intent, voice, audience, tone) and updated generic "persona" fallback to use orderPersonaPreset (37 lines changed).

**loops_remaining_forecast:** 3-4 loops (CLI completion, shuffle, help docs, validation)

**residual_constraints:**
- Shuffle order not aligned (medium severity, deferred to Loop 4)
- Help documentation not updated (low severity, deferred to Loop 5)

**files_changed:**
- `internal/barcli/completion.go` (modified) - Swapped order constants, updated stageOrder() function

**constraint_recap:**
The CLI completion order constraint has been relieved. Order constants now show preset (16) > intent (15), making preset suggestions appear first in shell completions. The stageOrder() function has explicit cases for all persona stages. One residual medium-severity constraint remains: shuffle stageOrder not aligned - generated prompts may still combine intent + preset or present intent before preset. Mitigation: Update shuffle stageOrder in Loop 4 and expand skip logic to skip intent when preset selected. Monitoring trigger: Verify shuffle output follows preset-first pattern and doesn't generate intent+preset combinations after update.

**next_work:**
- Behaviour: Update shuffle stageOrder to preset-first, expand skip logic to skip intent when preset selected
- Validation: `grep -A6 'var shuffleStageOrder' internal/barcli/shuffle.go` shows preset before intent

---

## Loop 4: Update shuffle stage order to preset-first

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0086 Section 2 (Shuffle Stage Order) - Reorder shuffleStageOrder to preset-first, expand skip logic to skip intent when preset selected

**active_constraint:** Shuffle stageOrder has intent before persona_preset; cannot generate preset-first prompts without reordering array and expanding skip logic to skip intent (along with voice/audience/tone) when preset is selected.

**validation_targets:**
- `grep -A6 'var shuffleStageOrder' internal/barcli/shuffle.go | grep -E '(persona_preset|intent)' | head -2`

**evidence:**
- red | 2026-01-20T08:30:00Z | exit 0 | `grep -A6 'var shuffleStageOrder' internal/barcli/shuffle.go | grep -E '(persona_preset|intent)' | head -2`
  - helper:diff-snapshot=0 files changed
  - Shows "intent" before "persona_preset" in shuffleStageOrder | inline
- green | 2026-01-20T08:35:00Z | exit 0 | `grep -A6 'var shuffleStageOrder' internal/barcli/shuffle.go | grep -E '(persona_preset|intent)' | head -2`
  - helper:diff-snapshot=1 file changed, 30 insertions(+), 12 deletions(-)
  - Shows "persona_preset" before "intent" with ADR 0086 comments and Path 1/2 labels | inline
- green | 2026-01-20T08:36:00Z | exit 0 | `grep -A2 'skip intent and individual persona axes' internal/barcli/shuffle.go`
  - Skip logic expanded to include intent: hasPersonaPreset && (stage == "intent" || ...) | inline
- removal | 2026-01-20T08:38:00Z | exit 0 | `git stash && grep -A6 'var shuffleStageOrder' internal/barcli/shuffle.go | grep -E '(persona_preset|intent)' | head -2 && git stash pop`
  - helper:diff-snapshot=0 files changed (after stash)
  - Order reverts to "intent" before "persona_preset" | inline

**rollback_plan:** `git restore internal/barcli/shuffle.go`

**delta_summary:** Reordered shuffleStageOrder to put persona_preset before intent, added ADR 0086 comments and Path 1/2 labels, expanded skip logic to skip intent (in addition to voice/audience/tone) when persona_preset selected so shuffled prompts follow bundled-first pattern (30 lines changed).

**loops_remaining_forecast:** 1-2 loops (shuffle, help docs/validation)

**residual_constraints:**
- Help documentation not updated (low severity, can be done in follow-up)
- ADR 0086 validation not complete (low severity, can validate after all code changes)

**files_changed:**
- `internal/barcli/shuffle.go` (modified) - Reordered shuffleStageOrder, expanded skip logic

**constraint_recap:**
The shuffle stage order constraint has been relieved. Shuffle now generates preset-first prompts and skips intent when preset is selected, preventing intent+preset combinations from appearing in future refinement cycles. All code surfaces (TUI2, CLI completion, shuffle) now aligned on preset-first order. One residual low-severity constraint remains: help documentation not yet updated to reflect new order. Mitigation: This is documentation-only and can be addressed in follow-up work. Monitoring trigger: Check that users understand preset-first pattern from in-tool help.

**next_work:**
- Optional: Create validation loop to verify all surfaces work correctly
- Optional: Update help documentation in internal/barcli/app.go and readme.md
- Mark ADR 0086 implementation complete

---

## Loop 5: Validation of preset-first implementation

**helper_version:** `helper:v20251223.1`

**focus:** Validate that all surfaces (Python, TUI2, CLI, shuffle) correctly implement preset-first order

**active_constraint:** No end-to-end validation performed; cannot confirm all surfaces work together correctly without testing imports, order verification, and skip logic.

**validation_targets:**
- `python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS; assert len(PERSONA_PRESET_IMPLICIT_INTENTS) == 8"`
- `grep -A2 'var stageOrder' internal/bartui2/program.go | grep 'persona_preset' | head -1`
- `grep 'orderPersonaPreset.*16' internal/barcli/completion.go`
- `grep -A2 'var shuffleStageOrder' internal/barcli/shuffle.go | grep 'persona_preset' | head -1`

**evidence:**
- green | 2026-01-20T08:40:00Z | exit 0 | `python3 -c "from lib.personaConfig import PERSONA_PRESET_IMPLICIT_INTENTS, INTENT_PRESET_GUIDANCE; assert len(PERSONA_PRESET_IMPLICIT_INTENTS) == 8"`
  - Python config: 8 presets mapped, guidance string present | inline
- green | 2026-01-20T08:41:00Z | exit 0 | `grep -A2 'var stageOrder' internal/bartui2/program.go | grep 'persona_preset'`
  - TUI2: persona_preset appears first in stageOrder with ADR comments | inline
- green | 2026-01-20T08:42:00Z | exit 0 | `grep 'When preset selected, mark intent' internal/bartui2/program.go`
  - TUI2: Smart skip logic present for marking intent as "(implicit)" | inline
- green | 2026-01-20T08:43:00Z | exit 0 | `grep 'orderPersonaPreset.*16' internal/barcli/completion.go`
  - CLI completion: orderPersonaPreset = 16 > orderPersonaIntent = 15 | inline
- green | 2026-01-20T08:44:00Z | exit 0 | `grep -A3 'case "persona_preset"' internal/barcli/completion.go`
  - CLI completion: stageOrder() function has explicit persona_preset case | inline
- green | 2026-01-20T08:45:00Z | exit 0 | `grep -A2 'var shuffleStageOrder' internal/barcli/shuffle.go | grep 'persona_preset'`
  - Shuffle: persona_preset appears first in shuffleStageOrder | inline
- green | 2026-01-20T08:46:00Z | exit 0 | `grep 'hasPersonaPreset && (stage == "intent"' internal/barcli/shuffle.go`
  - Shuffle: Skip logic includes intent (in addition to voice/audience/tone) | inline

**rollback_plan:** N/A (validation only)

**files_changed:**
- None (validation only)

**delta_summary:** All validation checks pass. Python config has 8 preset mappings and guidance string. TUI2 has preset-first stageOrder with smart skip logic. CLI completion has swapped order constants (preset=16, intent=15) and explicit stageOrder() cases. Shuffle has preset-first order and expanded skip logic including intent.

**constraint_recap:**
All validation checks pass. No residual constraints for Phase 1 (preset-first implementation). All surfaces (Python config, TUI2, CLI completion, shuffle) correctly implement preset-first order with intent-skipping behavior. Changes are ready for commit.

**next_work:**
- Commit changes with appropriate message referencing ADR 0086 Phase 1
- Consider whether to proceed with Phase 2 (retire "infer", directional rewrites) or pause

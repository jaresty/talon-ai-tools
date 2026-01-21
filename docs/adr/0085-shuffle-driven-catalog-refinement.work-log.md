# ADR 0085 Work Log: Shuffle-Driven Catalog Refinement

## Overview

This work-log tracks implementation progress for shuffle-driven catalog refinement per ADR 0085.

**Evidence root:** `docs/adr/evidence/0085/`
**VCS revert:** `git restore --source=HEAD`
**Helper version:** `helper:v20251223.1`

---

## Loop 1: Create shuffle corpus generation script

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0085 Phase 1 (Generation) - Create script to generate reproducible shuffle corpus

**active_constraint:** No script exists to generate reproducible shuffle corpus; cannot systematically evaluate catalog without automated corpus generation that produces diverse, reproducible samples across sampling strategies.

**validation_targets:**
- `./scripts/shuffle_corpus.sh --count 10 --output /tmp/test_corpus`

**evidence:**
- red | 2026-01-20T02:00:00Z | exit 127 | `./scripts/shuffle_corpus.sh --count 10 --output /tmp/test_corpus`
  - helper:diff-snapshot=0 files changed
  - script does not exist; no such file or directory | inline
- green | 2026-01-20T02:10:00Z | exit 0 | `./scripts/shuffle_corpus.sh --count 10 --output /tmp/test_corpus`
  - helper:diff-snapshot=1 file changed, 127 insertions(+)
  - script generated 10 JSON files with valid structure | inline
- removal | 2026-01-20T02:15:00Z | exit 127 | `rm scripts/shuffle_corpus.sh && ./scripts/shuffle_corpus.sh --count 10 --output /tmp/test_corpus`
  - helper:diff-snapshot=0 files changed
  - script removed; no such file or directory error returns | inline

**rollback_plan:** `rm scripts/shuffle_corpus.sh` (file not yet in git)

**delta_summary:** Created scripts/shuffle_corpus.sh with argument parsing (--count, --output, --seed-start, --fill, --bar), validation, and corpus generation loop. Script generates N shuffled prompts with reproducible seeds and saves as JSON files.

**loops_remaining_forecast:** 4-5 loops (corpus script, evaluation template, recommendation aggregator, first refinement cycle, validation)

**residual_constraints:**
- Evaluation rubric requires human judgment (high severity, deferred to Loop 2)
  - Mitigation: Create evaluation template with clear scoring criteria
  - Monitoring: Check if evaluations produce inconsistent scores
  - Severity: High (cannot evaluate without clear rubric)
- LLM-assisted evaluation not yet implemented (low severity, deferred to future extension)
  - Mitigation: Manual evaluation for first cycle
  - Monitoring: Track time spent on manual evaluation
  - Severity: Low (manual process works but is time-intensive)

**files_changed:**
- `scripts/shuffle_corpus.sh` (new) - Corpus generation script with argument parsing and validation

**constraint_recap:**
The script generation constraint has been relieved. One residual high-severity constraint remains: evaluation requires a structured template with clear scoring criteria to ensure consistency. Without this template, evaluators cannot produce comparable assessments across prompts. Mitigation involves creating an evaluation markdown template in Loop 2. Monitoring trigger: If initial evaluations show high variance in scores for similar prompts, strengthen the rubric guidance.

**next_work:**
- Behaviour: Create evaluation template with scoring rubric and structured fields per ADR 0085 Phase 2
- Validation: Template file exists at docs/adr/evidence/0085/evaluation-template.md and contains all required scoring criteria

---

## Loop 2: Create evaluation template with scoring rubric

**helper_version:** `helper:v20251223.1`

**focus:** ADR 0085 Phase 2 (Evaluation) - Create structured template for evaluating shuffled prompts against prompt key

**active_constraint:** No evaluation template exists with structured rubric; cannot consistently score generated prompts without standardized format and clear criteria anchored to ADR 0083 prompt key.

**validation_targets:**
- `test -f docs/adr/evidence/0085/evaluation-template.md && grep -q "Task clarity" docs/adr/evidence/0085/evaluation-template.md`

**evidence:**
- red | 2026-01-20T02:20:00Z | exit 1 | `test -f docs/adr/evidence/0085/evaluation-template.md && grep -q "Task Clarity" docs/adr/evidence/0085/evaluation-template.md`
  - helper:diff-snapshot=0 files changed
  - template does not exist | inline
- green | 2026-01-20T02:30:00Z | exit 0 | `test -f docs/adr/evidence/0085/evaluation-template.md && grep -q "Task Clarity" docs/adr/evidence/0085/evaluation-template.md`
  - helper:diff-snapshot=1 file changed, 214 insertions(+)
  - template exists with all 5 scoring criteria | inline
- removal | 2026-01-20T02:35:00Z | exit 1 | `rm -rf docs/adr/evidence/0085 && test -f docs/adr/evidence/0085/evaluation-template.md`
  - helper:diff-snapshot=0 files changed
  - template removed; test fails | inline

**rollback_plan:** `rm -rf docs/adr/evidence/0085`

**delta_summary:** Created evaluation-template.md with structured format anchored to ADR 0083. Template includes 5 scoring criteria (Task Clarity, Constraint Independence, Persona Coherence, Category Alignment, Combination Harmony) with 1-5 rubrics, recommendation YAML schemas for all action types (retire/edit/recategorize/add), and metadata fields.

**loops_remaining_forecast:** 3-4 loops (evaluation template, recommendation aggregator, first refinement cycle, validation)

**residual_constraints:**
- Recommendation aggregation format not yet defined (medium severity, deferred to Loop 3)
  - Mitigation: Define YAML schema for recommendations in Loop 3
  - Monitoring: Check if manual aggregation is error-prone
  - Severity: Medium (can aggregate manually but structured format improves consistency)
- First refinement cycle not yet executed (high severity, deferred to Loop 4)
  - Mitigation: Generate corpus and perform evaluations in Loop 4
  - Monitoring: Track catalog drift signals
  - Severity: High (cannot validate process until executed)

**files_changed:**
- `docs/adr/evidence/0085/evaluation-template.md` (new) - Evaluation template with scoring rubric

**constraint_recap:**
The evaluation template constraint has been relieved. One residual medium-severity constraint remains: recommendation aggregation needs a structured format. Without schema documentation, it's unclear how to collect and prioritize recommendations from multiple evaluations. Mitigation involves creating a README that documents the full workflow and recommendation schema in Loop 3. Monitoring trigger: If initial evaluations produce inconsistent recommendation formats, strengthen the schema guidance.

**next_work:**
- Behaviour: Create README documenting the refinement workflow and recommendation aggregation process
- Validation: `test -f docs/adr/evidence/0085/README.md && grep -q "Workflow" docs/adr/evidence/0085/README.md` exits 0

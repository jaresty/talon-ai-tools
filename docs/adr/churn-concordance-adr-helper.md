# Churn × Complexity Concordance ADR Helper

This helper defines a repeatable workflow for producing a **churn × complexity (statement-level) + Concordance** analysis and drafting the resulting ADR directly on disk. It is **not** an ADR itself.

---

## Outcome & Deliverable
- Run this helper when prompted to “run the churn × complexity Concordance ADR helper.”
- Deliverable: a new markdown ADR committed to the project’s ADR catalog.
- Let `ADR_HOME` denote the directory that stores numbered ADRs (for example, `docs/adr/`).
- Determine the next identifier and slug automatically:
  - List existing files in `ADR_HOME` matching `^\d{4}-.*\.md$` (exclude `*.work-log.md`).
  - Parse the numeric prefixes, choose `ADR_ID = max + 1`, left padded to four digits.
  - Derive a human-readable title from the analysis theme, then produce `ADR_TITLE_SLUG` by lowercasing and replacing punctuation/whitespace with single hyphens.
- Write the ADR to `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md` using the editor tools available in this environment; do not rely on copy/paste through chat. If the file already exists, evolve it in place.

## Inputs & Default Scope Assumptions
- Establish the churn analysis scope that matters for your project (paths, components, services). Keep it consistent between log capture and heatmap generation.
- Ensure access to tooling that can:
  - Capture a reproducible git log/stat fixture for the chosen scope/window (`CHURN_LOG_COMMAND`).
  - Produce a statement-level churn × complexity heatmap with machine-readable output (`HEATMAP_COMMAND`).
- If those helpers do not exist yet, build lightweight scripts or makefile targets that:
  - Wrap `git log --stat` with consistent filters, output path, and environment overrides.
  - Walk the same commit window to score per-line churn, complexity (AST depth, branching factor, or lints), and coordination weight, then aggregate into a JSON structure with `nodes` and `lines` collections.
  - Accept configuration via environment variables or flags so the helper can be reused across repositories without code changes.
- Agree on the default window (for example, "90 days") and maximum number of hotspots (`LINE_CHURN_LIMIT`, default 200). Override as needed via environment variables or CLI flags.
- Record where the commands write their artifacts:
  - `CHURN_LOG_PATH` (text fixture of git log --stat).
  - `HOTSPOTS_JSON` (JSON payload with node-level churn metrics).
- Document the helper commands (inputs, outputs, env vars) alongside this file so future runs can regenerate the data without rediscovering the conventions.

## Workflow Overview

### 1. Harvest churn signals
- Run `CHURN_LOG_COMMAND` to refresh `CHURN_LOG_PATH` for the agreed window and scope.
- Run `HEATMAP_COMMAND` to regenerate `HOTSPOTS_JSON` (the statement-level churn × complexity data source).
- If alternative windows or scopes are required, re-run with the appropriate overrides.

### 2. Inventory hotspots
- Parse `HOTSPOTS_JSON`.
- Capture the top `nodes` (by score) with at least: `file`, `symbolName`, `nodeKind`, `nodeStartLine`, `totalChurn`, `avgComplexity`, `totalCoordination`, `score`, optional `role`, and representative change episodes.
- Prepare two artifacts for the ADR draft:
  - **Individual Hotspots** – ranked list/table of nodes with the captured metrics.
  - **Hotspot Clusters** – group nodes by shared responsibilities or coordination pain. Defer refactor proposals until later steps.

### 3. Map Concordance domains
- Concordance measures coordination load across three primary pressures:
  - **Visibility** – how explicit the coordination contracts are.
  - **Scope** – how far changes in the hotspot propagate.
  - **Volatility** – how frequently the hotspot churns.
- Canonicalization is a lever, not a metric: collapsing behaviour into a single explicit articulation raises visibility, narrows scope, and damps volatility.
- Improving Concordance means making the system easier to coordinate by:
  - Increasing visibility through explicit orchestrators and contracts.
  - Narrowing scope via better-aligned boundaries.
  - Reducing volatility through stable interfaces, guardrails, and tests.
  - Using semantic deduplication and canonical sources of truth to reinforce those gains and resist autocomplete-driven drift.
- For each hotspot cluster, infer the hidden domain/tune, describe its visibility/scope/volatility profile, and record the implied coordination cost.

### 4. Canonicalize and refine recommendations
- Treat canonicalization as the practical lever for relieving the identified visibility, scope, and volatility pressures.
- Use the semantic deduplication loop to move from analysis to action:
  1. **Surface similarity pressure** – confirm the churn data indicates overlapping intent.
  2. **Declare canonical intent** – name the abstraction or contract that should own the behaviour.
  3. **Collapse equivalents** – outline refactor steps that eliminate redundant variants in favour of the canonical form.
  4. **Re-shape future generation** – add “gravity” (utilities, documentation, prompt design) so autocomplete prefers the canonical path.
- For each hidden domain, draft recommendations that reduce coordination cost and clarify boundaries.
- Align every draft with prior art before finalising:
  - Search for existing domain homes or patterns (modules, services, workflows) already solving similar problems.
  - Prefer extending those patterns over creating new concepts.
- Record in the ADR for each domain:
  - `Original Draft` recommendation.
  - `Similar Existing Behavior` illustrating prior art.
  - `Revised Recommendation` aligned to the existing pattern.

### 5. Tests-first coverage plan
- Treat characterization coverage as a gate before any behaviour-changing refactor.
- For each revised recommendation:
  1. List the affected modules/functions and their current tests.
  2. Assess branch coverage (true/false, error paths, early exits).
  3. Decide whether new characterization tests are required; reuse existing branch-focused tests when they already capture the behaviour, adding new ones only to close real gaps.
- Capture the following commitment in the ADR:

  > We will review existing tests before each refactor slice, add focused characterization tests only where coverage is insufficient, and guard the refactor with those tests. When current branch-focused tests already cover the behaviour, we will extend and rely on them instead of duplicating coverage.

### 6. Assemble the ADR
- Title the document `# ADR-ADR_ID – HUMAN-READABLE TITLE` and mark `Status: Proposed` (unless directed otherwise). Include date and owners.
- Structure the ADR with these sections:
  1. **Context** – summarize the churn hotspots, Concordance findings, and hidden domains.
  2. **Problem** – explain how current coordination patterns, duplication, and boundary drift sustain high Concordance scores.
  3. **Decision** – describe the domain boundaries, orchestrators/facades, and reuse of existing patterns that will restore visibility, narrow scope, reduce volatility, and reinforce canonical paths as the means to hold those gains. Make explicit that the goal is to lower sustained Concordance scores through genuine structural/test improvements, not by weakening guardrails.
  4. **Tests-First Principle** – restate the commitment above (bold or blockquote).
  5. **Refactor Plan** – phased slices tying canonicalization steps to the characterization tests that must pass before and after each slice.
  6. **Consequences** – expected positive outcomes, risks, mitigations, and anticipated Concordance-score effects.
  7. **Salient Tasks** (optional but recommended) – behaviour-focused tasks that advance the plan without deferring everything to future ADRs.
- Write the ADR to `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md` using the editing tools. If updating an existing ADR, modify it in place.

## Final response back to the user
After writing or updating the ADR, return a concise summary covering:
- Where the churn analysis was run and where the log and heatmap artifacts were written (`CHURN_LOG_PATH`, `HOTSPOTS_JSON`).
- The hidden domains/tunes discovered and the dominant Concordance improvements targeted.
- The primary refactor and canonicalization decisions.
- The ADR file path that now contains the detailed plan.
- Immediate next slices (for example, “add characterization tests for X before extracting Y façade”).
- Avoid pasting the full ADR body into chat unless explicitly requested; the file on disk is the source of truth.

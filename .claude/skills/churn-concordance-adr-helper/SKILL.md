---
name: churn-concordance-adr-helper
description: Declarative workflow for running churn × complexity Concordance analysis and landing a numbered ADR with bundled scripts.
---

# Churn × Complexity Concordance ADR Helper

## Activation
- Load this skill whenever a task asks to run the churn × complexity Concordance ADR helper or to produce a Concordance-focused ADR from churn hotspots.
- The skill preps the following commands and artefact expectations so each run is reproducible.

## Bundled Commands
- `CHURN_LOG_COMMAND=python3 .claude/skills/churn-concordance-adr-helper/scripts/churn-git-log-stat.py`
- `HEATMAP_COMMAND=python3 .claude/skills/churn-concordance-adr-helper/scripts/line-churn-heatmap.py`
- `make churn-scan` runs both helpers sequentially with default environment values (`LINE_CHURN_OUTPUT` paths under `tmp/churn-scan/`).

## Default Environment
- `LINE_CHURN_SINCE="90 days ago"`
- `LINE_CHURN_SCOPE="lib/,GPT/,copilot/,tests/"`
- `LINE_CHURN_LIMIT=200` (heatmap only)
- `CHURN_LOG_PATH=${LINE_CHURN_OUTPUT:-tmp/churn-scan/git-log-stat.txt}`
- `HOTSPOTS_JSON=${LINE_CHURN_OUTPUT:-tmp/churn-scan/line-hotspots.json}`
- Override variables as needed, but keep scope/window aligned across both commands.

## Concordance Glossary
- **Visibility**: How explicit the coordination contracts are; higher visibility means clearer orchestrators, interfaces, and behavioural declarations.
- **Scope**: The breadth of modules/features a change touches; narrower scope confines churn to well-bounded domains.
- **Volatility**: Strong connascence (timing, execution order, shared algorithms) makes behaviour sensitive to when and how work executes, forcing tightly coupled change sets across the participating code paths.
- **Canonicalization**: Collapsing overlapping intent into a single named contract so future work gravitates toward the same implementation path.

## Execution Checklist
1. **Scope & ADR setup**
   - Confirm analysis scope (paths/services) and keep it consistent.
   - Set `ADR_HOME` (default `docs/adr/`), list `^\d{4}-.*\.md$` (excluding `*.work-log.md`), derive next `ADR_ID` (four digits) and `ADR_TITLE_SLUG`.
2. **Harvest churn signals**
   - Run `CHURN_LOG_COMMAND` (or `make churn-scan`) to refresh `CHURN_LOG_PATH`.
   - Run `HEATMAP_COMMAND` to build `HOTSPOTS_JSON` with the same scope/window.
3. **Inventory hotspots**
   - Parse `HOTSPOTS_JSON` for top nodes with: `file`, `symbolName`, `nodeKind`, `nodeStartLine`, `totalChurn`, `avgComplexity`, `totalCoordination`, `score`, optional `role`, representative episodes/sample lines.
   - Produce artefacts for individual hotspots (ranked list/table) and hotspot clusters grouped by coordination pain.
4. **Map Concordance domains**
   - For each cluster, assess Visibility, Scope, and Volatility pressures.
   - Identify hidden domains/tunes and document the coordination cost.
5. **Canonicalize recommendations**
   - Apply the semantic deduplication loop: surface overlap → declare canonical owner → collapse variants → reinforce future generation (utilities, docs, prompt design).
   - Align each recommendation with existing patterns: record Original Draft, Similar Existing Behaviour, Revised Recommendation.
6. **Tests-first coverage plan**
   - List affected modules/functions and current tests per recommendation.
   - Evaluate branch coverage; add characterization tests only where gaps remain.
   - Commit to the guardrail: review existing tests before each refactor slice, add focused coverage when required, rely on existing branch-focused tests when sufficient.
7. **Assemble the ADR**
   - Write `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md` with header `# ADR-ADR_ID – HUMAN-READABLE TITLE`, `Status: Proposed`, date, owners.
   - Include sections: Context, Problem, Decision, Tests-First Principle (quote the guardrail), Refactor Plan (slices tied to characterization tests), Consequences, and optional Salient Tasks.
   - Use editor tools to create/update the ADR file (no copy/paste through chat).

## Deliverable & Reporting
- Deliverable: committed ADR markdown at `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md`.
- Final user summary must enumerate:
  - `CHURN_LOG_PATH` and `HOTSPOTS_JSON` artefact locations.
  - Hidden domains and Concordance improvements targeted.
  - Canonicalization/refactor decisions.
  - ADR file path.
  - Immediate next slices (e.g., characterization tests before extracting a façade).
- Do not paste the full ADR body into chat unless explicitly requested; the file on disk is authoritative.

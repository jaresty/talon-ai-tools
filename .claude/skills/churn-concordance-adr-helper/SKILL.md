---
name: churn-concordance-adr-helper
description: Runs the churn × complexity Concordance ADR workflow with repo-provided scripts and delivers a numbered ADR.
---

# Churn × Complexity Concordance ADR Helper

## Trigger Conditions
- User asks to “run the churn × complexity Concordance ADR helper” or equivalent phrasing.
- Work requires combining churn × complexity hotspot analysis with Concordance domain mapping to produce a new ADR.

## Required Tooling
- `python3 scripts/tools/churn-git-log-stat.py` (`CHURN_LOG_COMMAND`) captures the reproducible `git log --stat` fixture.
- `python3 scripts/tools/line-churn-heatmap.py` (`HEATMAP_COMMAND`) emits the statement-level churn × complexity heatmap JSON.
- Both commands honor shared environment variables:
  - `LINE_CHURN_SINCE` (default `"90 days ago"`).
  - `LINE_CHURN_SCOPE` (comma-separated prefixes, default `"lib/,GPT/,copilot/,tests/"`).
  - `LINE_CHURN_OUTPUT` (text or JSON output path; defaults `tmp/churn-scan/git-log-stat.txt` and `tmp/churn-scan/line-hotspots.json`).
  - `LINE_CHURN_LIMIT` (default `200`, heatmap only).

## Pre-flight
1. Choose the churn analysis scope (paths, services, components) and keep it consistent across commands.
2. Confirm `ADR_HOME` (default `docs/adr/`) and compute the next ADR identifier by listing files matching `^\d{4}-.*\.md$` (skip `*.work-log.md`).
3. Derive `ADR_ID` = max + 1 (four digits) and `ADR_TITLE_SLUG` from the final ADR title (lowercase, punctuation & whitespace replaced with single hyphens).

## Workflow
1. **Harvest churn signals**
   - Run `CHURN_LOG_COMMAND` to refresh `CHURN_LOG_PATH`.
   - Run `HEATMAP_COMMAND` to build `HOTSPOTS_JSON` with matching scope/window.
   - Override environment variables if a different window or scope is required.
2. **Inventory hotspots**
   - Parse `HOTSPOTS_JSON`.
   - Capture top node metrics: `file`, `symbolName`, `nodeKind`, `nodeStartLine`, `totalChurn`, `avgComplexity`, `totalCoordination`, `score`, optional `role`, representative episodes/lines.
   - Prepare two ADR artifacts: ranked individual hotspots and clustered groups by shared responsibility or coordination pain.
3. **Map Concordance domains**
   - Frame hotspots against Visibility, Scope, and Volatility pressures.
   - Identify hidden domains/tunes and record coordination costs.
4. **Canonicalize and refine recommendations**
   - Treat canonicalization as the lever to relieve the Concordance pressures.
   - Follow the semantic deduplication loop:
     1. Surface overlapping intent from churn data.
     2. Declare canonical ownership/contract.
     3. Collapse redundant variants toward the canonical form.
     4. Reinforce future generation (utilities, docs, prompt design) around the canonical path.
   - Cross-check existing patterns and align recommendations with prior art, capturing original, similar existing behaviour, and revised recommendation per domain.
5. **Tests-first coverage plan**
   - For each recommendation, list affected modules/functions and current tests.
   - Assess branch coverage gaps and add characterization tests only where needed.
   - Commit to the guardrail: *review existing tests before refactor slices, add focused characterization coverage only when required, and rely on existing branch-focused tests when sufficient*.
6. **Assemble the ADR**
   - Write `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md` with front matter: `# ADR-ADR_ID – HUMAN-READABLE TITLE`, `Status: Proposed`, date, owners.
   - Sections: Context, Problem, Decision, Tests-First Principle (quote the commitment), Refactor Plan (phased slices tied to characterization tests), Consequences, and optional Salient Tasks.
   - If file exists, update in place; otherwise create it using editor tools (no copy/paste through chat).

## Deliverable & Reporting
- A committed ADR markdown file at `ADR_HOME/ADR_ID-ADR_TITLE_SLUG.md`.
- Final summary back to user must include:
  - Paths for churn artifacts (`CHURN_LOG_PATH`, `HOTSPOTS_JSON`).
  - Hidden domains discovered and Concordance improvements targeted.
  - Primary canonicalization/refactor decisions.
  - ADR file path containing the plan.
  - Immediate next slices (e.g., “add characterization tests for X before extracting Y façade”).
- Do not paste full ADR content into chat unless explicitly requested; the on-disk ADR is authoritative.

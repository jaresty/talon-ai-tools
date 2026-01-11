---
name: bootstrap-detection-refresh
description: Loads when bootstrap detection or harness detector configuration changes; outlines required refresh and validation workflow.
---

# Bootstrap Detection Refresh

## Trigger Conditions
- The task modifies bootstrap detection code, harness detector manifests, or property-specific detection configuration files.
- The task questions which follow-up refresh and validation steps are mandatory after detector edits.

## Refresh Workflow
- Run `rcef property:refresh <PROPERTY_ID>` for each affected real property so scaffolds and generated artifacts align with the updated detection logic.
- Keep a checklist of every refreshed property and capture output logs for ADR evidence when relevant.

## Validation Workflow
- After each refresh, rerun the focused harness and guard suites that enforce bootstrap assumptions.
- Confirm the following invariants still hold: no direct `kohlsFM.computedState.*` writers outside approved helpers, and `apollo.*` helpers remain the only `computedState` providers.
- Investigate and resolve deviations before concluding the detector change.

## Documentation
- Record refreshed property IDs, command output, and resulting validations in the associated ADR or work-log entry so future loops know the state of the detection rollout.

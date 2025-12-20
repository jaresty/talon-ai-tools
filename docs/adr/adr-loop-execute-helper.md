# ADR Loop / Execute Helper Prompt (Single-Agent Sequential Process)

This helper keeps ADR loops observable and safe while letting a single agent advance work in concise, auditable slices.

**Current helper version:** `helper:v20251220` (update this string when the helper changes; work-log entries must reference it exactly).

**Treat every invocation as fresh.** Rebuild context from the ADR text, its work-log, and current repo state; do not rely on conversational history.

---

## Named Placeholders

- `<EVIDENCE_ROOT>` – directory that stores detailed transcripts. Default: `docs/adr/evidence`.
- `<VALIDATION_TARGET>` – minimal command or scripted set proving the slice end-to-end (e.g., `python3 -m pytest tests/foo_test.py::case`).
- `<ARTEFACT_LOG>` – aggregated markdown (e.g., `<EVIDENCE_ROOT>/<adr>/2025-Q1.md`) that records full red/green transcripts when summaries are insufficient.
- `<VCS_REVERT>` – revert command for the repository (default `git checkout -- <path>`). Adjust these placeholders per repo and cite the mapping once per ADR.

---

## Core Principles

1. **Guardrails first.** Surface a failing automated check before behaviour edits. Documentation-only loops meet this bar by citing the governing guardrail and recording the removal-evidence summary; run the guardrail when automation exists.
2. **Single meaningful slice.** Each loop addresses one behaviour, guardrail, or documented decision end-to-end.
3. **Observable delta.** Every loop produces a change that matters if reverted and carries a rollback plan.
4. **Evidence-led logging.** Keep planning light but capture commands, outputs, touched files, and removal tests for every slice.
5. **Adversarial mindset.** Assume gaps remain; re-scan goals before declaring completion.

---

## Loop Contract

A loop entry is compliant when all statements hold:

**Focus declared**
- Relevant red checks for the ADR are cleared or logged with evidence.
- The contributor re-reads the ADR/work-log sections tied to the slice and notes which parts were refreshed.
- In-repo work remains for the ADR; otherwise record a status-only loop with evidence.

**Slice qualifies**
- All edits address the same behaviour, feature flag, or guardrail decision.
- At most one major component boundary is crossed; config + implementation + docs counts as one when governed by the same behaviour.
- Exactly one `<VALIDATION_TARGET>` proves the slice, even though it will run twice (red then green). Additional commands require justification in the work-log before execution.
- Documentation-only loops cite the relevant ADR clause, include a removal test, and identify the guardrail (or explain why automation is unavailable).

**Validation registered**
- The pre-plan names the `<VALIDATION_TARGET>` and where evidence artefacts will live.
- Before implementation edits, the contributor captures red evidence: updated expectation, fresh failing test, or, if coverage is missing, a minimal reversible regression (toggle, assertion, etc.) that is removed immediately after recording the failure.
- After edits, the same `<VALIDATION_TARGET>` is rerun for green.
- The contributor temporarily reverts the behaviour change using `<VCS_REVERT>` (or finer-grained equivalent) to confirm the guardrail fails again; if it stays green, the slice is tightened until the failure returns.

**Evidence block complete**
- The work-log entry carries paired red/green summaries with command, timestamp (UTC preferred), exit status, and either a key snippet or a checksum.
- When summaries alone are insufficient, transcripts are appended to `<ARTEFACT_LOG>` rather than creating per-loop files; reference the exact heading from the work-log.
- By default, helper automation sets `<ARTEFACT_LOG>` to `<EVIDENCE_ROOT>/<adr>/artefacts.md` and records the pointer as `inline` when the summary is sufficient; contributors override by declaring alternatives in the loop header.
- The removal test is recorded in the same block (command and outcome). If revert attempts fail, the blocker evidence is logged.
- When no transcript is needed, the pointer field is recorded as `inline`.

**Next work queued**
- Deliverables and guardrails are bullet-listed (e.g., `Guardrail: tests/foo_test.py::case`).
- Status-only entries schedule the next behaviour/guardrail slice before closing the loop.
- Helper upgrades (new version strings) note the change and queue any reconciliation loop required by the stricter rules.

---

## Evidence Specification

Every compliant loop includes a structured block similar to:
```
- red | 2025-12-19T17:42Z | exit 1 | <VALIDATION_TARGET>
    expected helpers: apollo.userDetectedAnalyticsV2 | inline
- green | 2025-12-19T17:55Z | exit 0 | <VALIDATION_TARGET>
    helpers include apollo.userDetectedAnalyticsV2 | <ARTEFACT_LOG>#loop-217
- removal | 2025-12-19T18:01Z | exit 1 | <VCS_REVERT> <path> && <VALIDATION_TARGET>
    guardrail fails when reverted | inline
```
Replace placeholders with real commands, timestamps, and pointers. When aggregation is used, append headings inside `<ARTEFACT_LOG>` (`## loop-217 red`, `## loop-217 green`) so auditors can trace evidence quickly.

---

## Completion Bar

An ADR can be marked complete when:
1. All loop entries satisfy the contract above and reference the same helper version string.
2. Every ADR task/subtask is closed, reclassified with evidence, or explicitly parked with a trigger.
3. A final adversarial entry restates motivations, lists remaining realistic gaps (if any), cites fresh guardrail runs or explains why prior evidence still holds, and confirms the next trigger required to reopen work.
4. Repository metadata reflects the new status (e.g., ADR header/state, issue labels) if applicable.

---

## Portable Defaults & Overrides

- Override `<EVIDENCE_ROOT>`, `<ARTEFACT_LOG>`, and `<VCS_REVERT>` in the ADR header or initial loop entry when repositories require different paths or tooling. Subsequent entries inherit the mapping unless restated.
- Prefer text artefacts (markdown, JSON). When binary evidence is unavoidable, store a SHA-256 checksum alongside reconstruction notes.
- Tooling may auto-validate loops by checking for the placeholders above; keep names stable to stay compatible.

---

## Operational Tips (Optional)

- Maintain a scratch list of candidate slices, validation targets, and file pointers; refresh after every loop.
- Inspect diffs before recording green runs to ensure only intentional edits remain.
- Favour narrow tooling (single tests, targeted scripts) and document rationale before running broader suites or formatters.

By following this helper, each loop lands a well-tested, observable slice; the work-log remains the single source of truth; and completion checks stay decisive without overfitting to a specific codebase.

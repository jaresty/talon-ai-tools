# ADR Loop / Execute Helper Prompt (Single-Agent Sequential Process)

This helper keeps ADR loops observable and safe while letting a single agent advance work in concise, auditable slices.

**Current helper version:** `helper:v20251221.4` (update this string when the helper changes; work-log entries must reference it exactly).

**Context cited per loop.** Entries state which ADR sections, work-log notes, and repository evidence informed the slice; conversational history is out of scope.

---

## Named Placeholders

- `<EVIDENCE_ROOT>` – project-defined store for detailed transcripts that auditors can read (e.g., `docs/evidence`, `ops/adr/evidence`).
- `<VALIDATION_TARGET>` – project-specific minimal guardrail command or script that proves the slice end-to-end (e.g., the smallest test, lint, or validation command that exercises the targeted behaviour).
- `<ARTEFACT_LOG>` – aggregated evidence record (markdown, JSON, database entry, etc.) that captures full red/green transcripts when summaries are insufficient.
- `<VCS_REVERT>` – capability that temporarily rolls back the slice so guardrails can re-fail. Document the concrete command or procedure once per ADR (e.g., `git restore --source=HEAD`, `p4 revert`, migration rollback script).


---

## Compliance Signals

- Guardrail failure recorded before behaviour changes, or automation gap justified with evidence.
- Slice scope describes a single cohesive behaviour or decision, with multi-guardrail plans enumerated and observable.
- Each loop probes or resolves the highest-impact open assumption whose failure would jeopardize the ADR outcome before tackling lower-risk work.
- When multiple candidate slices exist, the executor selects the slice that interrogates the riskiest assumption without waiting for external direction; if choices appear indistinguishable, the executor picks any of them without blocking.
- Loop summary demonstrates the ADR completion horizon changed (or remained unchanged with justification) since the prior entry, naming the domains or tasks still open.
- Observable delta and rollback plan documented so reverts clearly undo the slice.
- Evidence block captures commands, outputs, touched files, and removal tests without excess narrative.
- Residual risks, mitigations, and monitoring triggers listed at loop close.
- Validation commands execute within the project workspace (no external directories required).

---

**Risk heuristic.** Risk refers to unproven assumptions whose failure would derail or materially delay the ADR’s objective; loops surface or resolve the riskiest remaining assumption as early as possible, using smaller slices to reach confidence quickly. Documentation work is only prioritized when it directly unlocks probing that assumption.

## Loop Contract

A loop entry is compliant when all statements hold:

**Focus declared**
- Relevant red checks for the ADR are cleared or logged with evidence.
- Refreshed ADR/work-log sections tied to the slice are identified in the entry.
- The entry names the riskiest open assumption (i.e., the unproven behaviour most likely to derail or delay the ADR) based on probability × impact, defaulting to the least-validated dependency when uncertainty ties, and explains how the slice tests or resolves it now, documenting any higher-risk items intentionally deferred.
- Remaining work is noted; when the riskiest assumption cannot be advanced, the loop records the blocker with concrete evidence (e.g., guardrail output, failing log), otherwise a status-only update confirms completion.

**Slice qualifies**
- All edits address the same cohesive behaviour, feature flag, or guardrail decision. Crossing multiple files or components is fine when the behaviour demands it, provided the loop keeps the change observable.
- Multi-guardrail slices list the guardrails/files covered and record evidence for each item.
- A single `<VALIDATION_TARGET>` is recorded when one command exercises all guardrails. When guardrails require different commands, the entry documents a minimal list mapping each guardrail to a target; every target has red/green/removal evidence and any extra command is justified in the work-log.
- Documentation-only loops occur only when they unblock or record progress on the riskiest open assumption; they pair with a behaviour slice in the same cycle or provide the blocker evidence above, cite the relevant ADR clause, record the governing guardrail (or justify missing automation), and capture a reversible red failure or equivalent detection signal before edits land.

**Validation registered**
- Loop pre-plan identifies the `<VALIDATION_TARGET>` (or bounded list) and the evidence locations, mapping each guardrail to its target.
- Red evidence exists before behaviour edits land: updated expectation, fresh failing test, or, where coverage is absent, a minimal reversible regression removed immediately after the failure is recorded. The entry states why the failure output covers the targeted behaviour and demonstrates the full guardrail surface; partial failures cite missing facets and queue tightening work before proceeding.
- Green evidence reuses the same `<VALIDATION_TARGET>` (or mapped target).
- Removal evidence uses `<VCS_REVERT>` (or finer-grained equivalent) to restore the pre-change baseline, states when the baseline is back in place, and re-runs the primary guardrail so the targeted failure is observable again; if it stays green, tighten the slice until the failure returns.

**Evidence block complete**
- The work-log entry carries paired red/green summaries with command, timestamp (UTC preferred), exit status, and either a key snippet or a checksum. Include a short diff/hash snapshot (e.g., `git diff --stat` or a checksum) so reviewers can verify the observable delta quickly. Red evidence includes the minimal failure excerpt (assertion, traceback line, or error code) demonstrating the targeted behaviour.
- When summaries alone are insufficient, transcripts are appended to `<ARTEFACT_LOG>` rather than creating per-loop files; the entry references the exact heading and notes any temporary per-loop files with a migration plan. Evidence writers append to the declared aggregated location and mark pointers as `inline` only when the inline-size rule is satisfied.
- The removal test is recorded in the same block (command and outcome). If revert attempts fail, the blocker evidence is logged.
- Close each loop with an adversarial “risk recap” paragraph naming at least one residual risk, the mitigation or monitoring action queued, and any triggers that would reopen the work.
- When no transcript is needed, the pointer field is recorded as `inline`.

**Next work queued**
- Deliverables and guardrails are bullet-listed (e.g., `Guardrail: tests/foo_test.py::case`).
- New high-level tasks appear only when they replace or consolidate existing scope while interrogating the riskiest assumption, and the entry states that relationship explicitly.
- Status-only entries schedule the next behaviour/guardrail slice before closing the loop.
- Helper upgrades (new version strings) note the change and queue any reconciliation loop required by the stricter rules.

---

## Evidence Specification

Every compliant loop includes a structured block similar to:
```
- red | 2025-12-19T17:42Z | exit 1 | <VALIDATION_TARGET>
    guardrail <name> fails with missing expectation <id> | inline
- green | 2025-12-19T17:55Z | exit 0 | <VALIDATION_TARGET>
    guardrail <name> passes with expectation <id> restored | <ARTEFACT_LOG>#loop-217
- removal | 2025-12-19T18:01Z | exit 1 | <VCS_REVERT> && <VALIDATION_TARGET>
    guardrail <name> fails again after temporary revert | inline
```
Replace placeholders with real commands, timestamps, and pointers. When aggregation is used, append headings inside `<ARTEFACT_LOG>` (`## loop-217 red`, `## loop-217 green`) so auditors can trace evidence quickly. Teams using multiple validation targets should append one red/green/removal trio per target under a shared loop heading.

---

## Helper Upgrades

- Work-log entries for a given ADR cite a single helper version; when the version changes, a reconciliation entry records the migration outcome before new loops land.
- Version changes note any required follow-up (e.g., aggregated evidence adoption, refreshed validation mappings) so remaining tasks are queued explicitly.

---

## Completion Bar

Completion is eligible once every loop satisfies this contract under a single helper version, outstanding tasks are closed or parked with evidence, a final adversarial entry restates motivations and residual gaps, and repository metadata reflects the updated ADR state.

---

## Portable Defaults & Overrides

- Override `<EVIDENCE_ROOT>`, `<ARTEFACT_LOG>`, and `<VCS_REVERT>` in the ADR header or initial loop entry when repositories require different paths or tooling. Subsequent entries inherit the mapping unless restated, and aggregated artefact paths must be kept in sync with automation templates.
- Prefer text artefacts (markdown, JSON). When binary evidence is unavoidable, store a SHA-256 checksum alongside reconstruction notes.
- Tooling may auto-validate loops by checking for the placeholders above; keep names stable to stay compatible.

---

## Optional Patterns

Teams may keep local scratch notes or checklists to help satisfy the contract, but compliance is determined solely by the declarative rules above.

By following this helper, each loop lands a well-tested, observable slice; the work-log remains the single source of truth; and completion checks stay decisive without overfitting to a specific codebase.

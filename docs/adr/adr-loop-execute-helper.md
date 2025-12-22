# ADR Loop / Execute Helper Prompt (Single-Agent Sequential Process)

This helper keeps ADR loops observable and safe while letting a single agent advance work in concise, auditable slices.

**Current helper version:** `helper:v20251221.5` (update this string when the helper changes; work-log entries must reference it exactly).

**Context cited per loop.** Entries state which ADR sections, work-log notes, and repository evidence informed the slice; conversational history is out of scope.

---

## Named Placeholders

- `<EVIDENCE_ROOT>` – project-defined store for detailed transcripts that auditors can read (e.g., `docs/evidence`, `ops/adr/evidence`).
- `<VALIDATION_TARGET>` – project-specific minimal guardrail command or script that proves the slice end-to-end (e.g., the smallest test, lint, or validation command that exercises the targeted behaviour).
- `<ARTEFACT_LOG>` – aggregated evidence record (markdown, JSON, database entry, etc.) that captures full red/green transcripts when summaries are insufficient.
- `<VCS_REVERT>` – capability that temporarily rolls back the slice so guardrails can re-fail. Document the concrete command or procedure once per ADR (e.g., `git restore --source=HEAD`, `p4 revert`, migration rollback script).

## Canonical Helper Commands

Use the following named helpers unless the ADR header overrides them. When a local equivalent is required, cite it explicitly in the loop entry.

- `helper:diff-snapshot` → `git diff --stat`
- `helper:rerun <command>` → re-executes the recorded `<VALIDATION_TARGET>` using the same working directory and environment.
- `helper:timestamp` → UTC ISO-8601 stamp (e.g., `2025-12-21T17:42:00Z`).

The `<ARTEFACT_LOG>` must record headings matching the helper command names when transcripts are aggregated (e.g., `## loop-217 green | helper:diff-snapshot`).

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

## Loop Entry Field Checklist

Each entry must populate the following fields; omit none. References column lists the helper section governing the requirement.

| Field | Required Content | References |
| --- | --- | --- |
| `helper_version` | Literal `helper:v20251221.5` | **Loop Contract → Focus declared** |
| `focus` | ADR/section IDs plus short summary of slice scope | **Loop Contract → Focus declared** |
| `riskiest_assumption` | Statement of probability × impact; include deferrals | **Loop Contract → Focus declared** |
| `validation_targets` | List of commands; one per guardrail | **Loop Contract → Validation registered** |
| `evidence` | Triplets of `red/green/removal` records (command, UTC timestamp, exit status, pointer) | **Evidence Specification** |
| `rollback_plan` | `<VCS_REVERT>` command plus reminder to replay red failure | **Loop Contract → Focus declared** |
| `delta_summary` | `helper:diff-snapshot` hash or stat plus change rationale | **Evidence Specification** |
| `residual_risks` | At least one risk with mitigation and monitoring trigger | **Loop Contract → Slice qualifies** |
| `next_work` | Guardrail/task bullets covering remaining scope | **Loop Contract → Next work queued** |

---

## Loop Contract


A loop entry is compliant when all statements hold:

**Focus declared**
- For every guardrail in scope, the corresponding red check is either cleared within the slice or logged with command/timestamp/exit evidence linked to the guardrail ID.
- The entry cites the exact ADR sections and work-log notes refreshed by this slice; omit generic references.
- The riskiest open assumption is named with probability × impact rationale. Each higher-risk deferral includes the evidence pointer documenting the blocker.
- When the riskiest assumption cannot advance, blocker evidence (command, failure excerpt, pointer) is present. Status-only entries must additionally state the next riskiest assumption.

**Slice qualifies**
- All edits address the same cohesive behaviour, feature flag, or guardrail decision. Crossing multiple files or components is fine when the behaviour demands it, provided the loop keeps the change observable.
- For every guardrail touched, the entry names the updated artefacts and attaches guardrail-specific evidence.
- When one `<VALIDATION_TARGET>` covers multiple guardrails, the mapping is explicit. When multiple commands are required, each additional command carries justification and a 1:1 red/green/removal trio per guardrail.
- Documentation-only loops are allowed only when paired with blocker evidence, governing ADR clause, named guardrail or automation gap, and reversible red failure before edits land.

**Validation registered**
- Loop pre-plan identifies the `<VALIDATION_TARGET>` (or bounded list) and the evidence locations, mapping each guardrail to its target before edits begin.
- Red evidence exists before behaviour edits land: command fails with non-zero exit, UTC ISO-8601 timestamp, and failure excerpt demonstrating the targeted behaviour surface end-to-end. Partial coverage notes missing facets and lists the tightening work.
- Green evidence reuses the same `<VALIDATION_TARGET>` command (or mapped target) and records exit 0 with matching timestamp format.
- Removal evidence concatenates `<VCS_REVERT>` with the red command, shows baseline restoration (non-zero re-run), and records the UTC timestamp of restoration. If failure does not reappear, the entry states the tightening action required.

**Evidence block complete**
- Each red/green/removal record lists: command string, UTC ISO-8601 timestamp, exit status, diff/hash snapshot (`helper:diff-snapshot` output or checksum), and a pointer (`inline` or `<ARTEFACT_LOG>#heading`). Red evidence must include the failure excerpt proving the targeted behaviour.
- When summaries are insufficient, transcripts append to `<ARTEFACT_LOG>` using headings of the form `loop-### {kind} | helper:diff-snapshot`; temporary per-loop files note their migration plan. Use `inline` pointers only when the excerpt fits within existing size limits.
- Removal records document the same command pairing, the `<VCS_REVERT>` invocation, and the re-run failure snippet. If any step fails (e.g., revert blocked), log the blocker evidence immediately.
- The adversarial “risk recap” paragraph names at least one residual risk, the mitigation, the monitoring trigger, and the reopen condition.

**Next work queued**
- Deliverables and guardrails are bullet-listed (e.g., `Guardrail: tests/foo_test.py::case`).
- New high-level tasks appear only when they replace or consolidate existing scope while interrogating the riskiest assumption, and the entry states that relationship explicitly.
- Status-only entries schedule the next behaviour/guardrail slice before closing the loop.
- Helper upgrades (new version strings) note the change and queue any reconciliation loop required by the stricter rules.

---

## Evidence Specification

Every compliant loop includes a structured block similar to:
```
- red | 2025-12-19T17:42:00Z | exit 1 | <VALIDATION_TARGET>
    helper:diff-snapshot=2 files changed, 4 insertions(+)
    guardrail <name> fails with missing expectation <id> | inline
- green | 2025-12-19T17:55:12Z | exit 0 | <VALIDATION_TARGET>
    helper:diff-snapshot=2 files changed, 4 insertions(+)
    guardrail <name> passes with expectation <id> restored | <ARTEFACT_LOG>#loop-217 green
- removal | 2025-12-19T18:01:20Z | exit 1 | <VCS_REVERT> && <VALIDATION_TARGET>
    helper:diff-snapshot=0 files changed
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

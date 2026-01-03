# ADR Loop / Execute Helper Prompt (Single-Agent Sequential Process)

This helper keeps ADR loops observable and safe while letting a single agent advance work in concise, auditable slices.

**Current helper version:** `helper:v20251223.1` (update this string when the helper changes; work-log entries must reference it exactly).
**Work-log separation:** ADR bodies remain directional references; each ADR tracks in-flight loops in its sibling `*.work-log.md` file while detailed evidence continues under `docs/adr/evidence/<adr-id>/loop-<n>.md`. Keep ADR edits focused on decisions, guardrails, and validation contracts; defer incremental progress updates to the work-log and evidence tree.

**Work-log maintenance:** Derive the work-log filename from the ADR slug on first use (for example, `0123-sample-adr.md` → `0123-sample-adr.work-log.md`), create the file with a heading when it does not exist, and append a dated entry for every slice. Each loop records which heading was updated so later readers can replay the sequence without guessing.

**Context cited per loop.** Entries state which ADR sections, work-log notes, and repository evidence informed the slice; conversational history is out of scope.

---

## Named Concepts

- **Behaviour outcome** – the ADR-defined behaviour or decision this loop changes or observes.
- **Validation command** – the smallest executable that exercises a behaviour outcome and records red/green/removal evidence.
- **Blocker evidence** – the command, excerpt, and pointer proving a behaviour cannot advance in this slice (logged as `red` evidence).
- **Residual risk** – a remaining operational or process risk, recorded with mitigation and monitoring trigger in `residual_risks`.
- **Risk severity** – classification of a behaviour outcome’s probability × impact. When severity is low (probability low or impact low), the item stays in `residual_risks` and does not drive new slices.
- **Diminishing return** – additional effort that only reduces low-severity residual risk; such work is optional unless governance explicitly requires it.
- **Canonical intent** – the minimal, shared representation of a behaviour outcome that loops converge on (e.g., a single helper, type, or invariant).
- **Equivalence evidence** – observations showing multiple implementations express the same behaviour (tests, telemetry comparisons, structural analysis) that justify canonicalization.
- **Future-shaping action** – a change that biases future contributors and tooling toward the canonical intent (examples: centralising helpers, documenting invariants, tightening type contracts).

## Named Placeholders

- `<EVIDENCE_ROOT>` – project-defined store for detailed transcripts that auditors can read (e.g., `docs/evidence`, `ops/adr/evidence`).
- `<VALIDATION_TARGET>` – project-specific minimal command or script that proves the slice end-to-end (e.g., the smallest test, lint, or validation command that exercises the targeted behaviour).
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

- Each loop addresses the highest-severity open behaviour from the ADR’s salient task list, cites its task ID, and places lower-severity items in `residual_risks`.
- Documentation-only loops appear only when blocker evidence proves the behaviour cannot advance in the current slice.
- Validation commands exercise the canonical behaviour path (for example, compiled CLI, schema generator, parity guardrail); string or grep checks do not qualify.
- Recording a validation target denotes that the command executed within the loop; entries without matching red or green evidence for that target are non-compliant.
- Every `validation_targets` entry references the cited salient task artefact and runs end-to-end in the repository workspace.
- `loops_remaining_forecast` enumerates the remaining behaviours with their validation command or blocker evidence and adds a confidence note.
- Loop summary explains how the ADR completion horizon shifted (or why it stayed steady) since the prior entry, naming the domains or salient tasks still open.
- Residual risks record updated severity and mitigation progress; unchanged text is treated as non-compliant.
- Loops whose observable delta is documentation-only remain compliant only when the entry records the associated blocker evidence for the targeted behaviour. Removal evidence is optional for these loops as long as no executable artefacts change.
- Observable delta, rollback plan, and evidence block remain concise and auditable.

---

## Loop Entry Field Checklist

Each entry must populate the following fields; omit none. References column lists the helper section governing the requirement.

| Field | Required Content | References |
| --- | --- | --- |
| `helper_version` | Literal `helper:v20251223.1` | **Loop Contract → Focus declared** |
| `focus` | ADR/section IDs plus short summary of slice scope | **Loop Contract → Focus declared** |
| `riskiest_assumption` | Falsifiable highest-impact uncertainty (probability × impact) about a behaviour outcome, naming the validation command or blocker evidence; include deferrals | **Loop Contract → Focus declared** |
| `validation_targets` | Validation commands for the behaviours under change; one command per outcome being validated | **Loop Contract → Validation registered** |
| `evidence` | Triplets of `red/green/removal` records (command, UTC timestamp, exit status, pointer) | **Evidence Specification** |
| `rollback_plan` | `<VCS_REVERT>` command plus reminder to replay red failure | **Loop Contract → Focus declared** |
| `delta_summary` | `helper:diff-snapshot` hash or stat plus change rationale and the current depth-first rung or recorded pivot | **Evidence Specification** |
| `loops_remaining_forecast` | Numeric estimate of loops left, task anchors, and confidence note | **Loop Contract → Focus declared** |
| `residual_risks` | At least one risk with mitigation and monitoring trigger; reminder-style notes live here, not in `riskiest_assumption` | **Loop Contract → Slice qualifies** |
| `next_work` | Behaviours still open plus their validation commands or blocker pointers | **Loop Contract → Next work queued** |

---

## Loop Contract


A loop entry is compliant when all statements hold:

**Focus declared**
- Red evidence is recorded before edits land and green/removal evidence after, keeping guardrail commands limited to the validation channel for that behaviour.
- The ADR section and salient task ID for the targeted behaviour are cited, and the entry states that this behaviour is the highest-severity open item while demoting lower-severity items to `residual_risks`.
- A depth-first path enumerates the mitigation ladder for the cited behaviour: salient task → nested sub-decisions → concrete artefacts. Loops stay on this path until the targeted rung lands green or blocker evidence is recorded.
- The work-log entry updated in this slice is cited by heading or timestamp so auditors can trace the refreshed note alongside the code change.
- Prioritization favours depth-first slices that de-risk the cited behaviour before opening lateral scope; each entry notes how the slice advances that depth-first path.
- When severity reassessment elevates another behaviour, the loop documents the pivot, parks the interrupted rung in `residual_risks` with its blocker or mitigation plan, and restates the new depth-first path before editing.
- The riskiest assumption is expressed as a falsifiable statement with probability × impact rationale, explains why it outranks every other medium/high risk, and references the canonical intent and any equivalence evidence it reinforces.
- When the behaviour cannot advance, the loop captures blocker evidence (command, failure excerpt, pointer) before closing; documentation-only entries include this blocker evidence.


**Slice qualifies**
- Each loop edits only the cited behaviour or decision; cross-file work remains acceptable when it serves that behaviour and stays observable.
- Every touched artefact maps to the validation command that exercises it; when one `<VALIDATION_TARGET>` covers multiple behaviours, the mapping is explicit, otherwise each behaviour carries its own command with a red/green/removal trio.
- Documentation-only loops appear only after this slice records blocker evidence for the behaviour.

**Validation registered**
- The loop pre-plan names the `<VALIDATION_TARGET>` that exercises the cited salient task artefact before editing begins; validation commands are omitted only for documentation-only loops that already logged blocker evidence.
- A recorded `<VALIDATION_TARGET>` denotes that the command executed within the loop; missing red or green evidence for that target renders the entry non-compliant.
- Red evidence records the canonical command failing end-to-end with non-zero exit, UTC ISO-8601 timestamp, and failure excerpt for the targeted behaviour.
- Green evidence reuses the same command (or mapped target) and records exit 0, and removal evidence runs `<VCS_REVERT>` followed by the red command to show the failure returning or documents the tightening required when it does not.

**Evidence block complete**
- Each red/green/removal record lists: command string, UTC ISO-8601 timestamp, exit status, diff/hash snapshot (`helper:diff-snapshot` output or checksum), and a pointer (`inline` or `<ARTEFACT_LOG>#heading`). Red evidence must include the failure excerpt proving the targeted behaviour.
- When summaries are insufficient, transcripts append to `<ARTEFACT_LOG>` using headings of the form `loop-### {kind} | helper:diff-snapshot`; temporary per-loop files note their migration plan. Use `inline` pointers only when the excerpt fits within existing size limits.
- Removal records document the same command pairing, the `<VCS_REVERT>` invocation, and the re-run failure snippet. Documentation-only loops that do not touch executable artefacts may omit this removal record once blocker evidence is captured. If any required step fails (e.g., revert blocked), log the blocker evidence immediately.
- The adversarial “risk recap” paragraph names at least one residual risk, the mitigation, the monitoring trigger, and the reopen condition.

**Next work queued**
- `next_work` contains `Behaviour:` bullets tied to salient task IDs, each citing the validation command or blocker evidence that will advance the next highest-severity assumption and the future-shaping action that keeps the canonical intent aligned.
- New bullets appear only when replacing or consolidating scope for the riskiest assumption; discoveries outside the ADR behaviours record blocker evidence and defer to ADR-level triage.
- Status-only entries schedule the next behaviour slice (or evidence refresh) before closing, and helper upgrades note any reconciliation loop required.

---

## Evidence Specification

Every compliant loop includes a structured block similar to:
```
- red | 2025-12-19T17:42:00Z | exit 1 | <VALIDATION_TARGET>
    helper:diff-snapshot=2 files changed, 4 insertions(+)
    behaviour <name> fails with missing expectation <id> | inline
- green | 2025-12-19T17:55:12Z | exit 0 | <VALIDATION_TARGET>
    helper:diff-snapshot=2 files changed, 4 insertions(+)
    behaviour <name> passes with expectation <id> restored | <ARTEFACT_LOG>#loop-217 green
- removal | 2025-12-19T18:01:20Z | exit 1 | <VCS_REVERT> && <VALIDATION_TARGET>
    helper:diff-snapshot=0 files changed
    behaviour <name> fails again after temporary revert | inline
```
Replace placeholders with real commands, timestamps, and pointers. When aggregation is used, append headings inside `<ARTEFACT_LOG>` (`## loop-217 red`, `## loop-217 green`) so auditors can trace evidence quickly. Teams using multiple validation targets should append one red/green/removal trio per target under a shared loop heading.

---

## Helper Upgrades

- Work-log entries for a given ADR cite a single helper version; when the version changes, a reconciliation entry records the migration outcome before new loops land.
- Version changes note any required follow-up (e.g., aggregated evidence adoption, refreshed validation mappings) so remaining tasks are queued explicitly.

---

## Completion Bar

Completion is eligible once every loop satisfies this contract under a single helper version, outstanding tasks are closed or parked with evidence, a final adversarial entry restates motivations and residual gaps, and repository metadata reflects the updated ADR state. Completion requires the targeted behaviour to land (code, tests, docs, automation) with green evidence; planning-only loops must keep the series open until the behaviour ships or is explicitly deferred with blocker evidence.

---

## Portable Defaults & Overrides

- Override `<EVIDENCE_ROOT>`, `<ARTEFACT_LOG>`, and `<VCS_REVERT>` in the ADR header or initial loop entry when repositories require different paths or tooling. Subsequent entries inherit the mapping unless restated, and aggregated artefact paths must be kept in sync with automation templates.
- Prefer text artefacts (markdown, JSON). When binary evidence is unavoidable, store a SHA-256 checksum alongside reconstruction notes.
- Tooling may auto-validate loops by checking for the placeholders above; keep names stable to stay compatible.

---

## Optional Patterns

Teams may keep local scratch notes or checklists to help satisfy the contract, but compliance is determined solely by the declarative rules above.

By following this helper, each loop lands a well-tested, observable slice; the work-log remains the single source of truth; and completion checks stay decisive without overfitting to a specific codebase.

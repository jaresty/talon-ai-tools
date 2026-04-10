# ADR-0229 — Ground+Gate Protocol Stress Test

**Date:** 2026-04-10
**Status:** Active — gaps identified, remediation pending

---

## Context

The ground+gate+chain+atomic token combination defines the TDD enforcement protocol for the bar prompt system. This ADR records the results of a structured stress test using 5 haiku subagents on task types specifically chosen to probe failure modes: refactor, delete, prose, performance, and multi-layer. Each agent was asked to apply the full protocol, then answer structured scoring questions. Followup questions were sent to each agent before closing.

---

## Task Coverage

| Task | Type | Probe target |
|------|------|-------------|
| Rename `formatPromptlet` → `renderPromptlet` | Refactor | Compiler as governing artifact; is grep theater? |
| Remove `writeSection`, replace call sites | Delete | Absence verification; behavioral scope creep |
| Write CONTRIBUTING.md method-token section | Prose | "No natural assertion" clause |
| Buffer pool for `RenderPlainText` | Performance | Benchmark threshold; step validity |
| `token_version` field through 5 layers | Multi-layer | Layer independence; pressure to stop early |

---

## Findings

### 1. Compiler as governing artifact (Refactor)

For type-system-enforced changes (renames, moved functions, signature changes), `go build` is already the complete executable automated assertion. Adding a grep check is structural theater — it observes text, not behavior, and cannot detect failures that the compiler would also catch.

**Gap in protocol:** The fourth requirement ("assertion type must match behavior type") implies this but doesn't state it. The protocol needs an explicit corollary:

> If the compiler enforces the constraint, `go build` passing is the executable automated assertion and is sufficient. Manual text search adds no coverage guarantee for compiler-verified structural changes.

**Line between full gate and lightweight gate:** Behavioral changes (new logic, new code paths, prompt text, config values, JSON fields, runtime-only paths) require full gate. Pure structural changes where the type system enforces correctness do not require additional assertions beyond compilation.

---

### 2. Behavioral scope creep during deletion (Delete)

Replacing `writeSection` with `writeSectionWithContract` introduced a behavioral side effect: EXECUTION_REMINDER and PLANNING_DIRECTIVE sections now support inline contracts they previously did not. The protocol surfaced this during the completion check but did not gate on it — it noted it and continued.

**Gap in protocol:** When a side effect is discovered during implementation, the protocol treats it as an observation. It should be a decision point:

> If a step produces a behavioral side effect not stated in the original intent, the step must pause and require explicit accept/reject before proceeding. Naming a side effect does not close it.

**Corollary from the delete agent:** Tests validate outputs against known inputs. Completion checks validate structural correctness of the transformation itself — these are different coverage classes. A function can be orphaned (unused but still defined) while all tests pass. The completion check must verify absence via source structure, not just test passage.

---

### 3. "No natural assertion" clause — floor + ceiling structure (Prose)

The prose agent correctly invoked the "no natural assertion" clause for instructional documentation ("guides the reader correctly" is a behavioral claim about the reader's mental state, not a referential claim about the artifact). However, the clause as written is an escape hatch: invoking it allows proceeding without any verification structure.

**Gap in protocol:** When "no natural assertion" is invoked, the gate should require:

1. **Floor (structural assertions still required):** File exists, required headings present, all cited file paths resolve, all referenced identifiers exist. These are necessary but not sufficient.
2. **Ceiling (manual verification protocol declared):** Who verifies (a role with specified domain knowledge, not the author), what they do (concrete procedure that cannot be passed by charitable reading), and a binary pass/fail condition defined in advance and checkable by someone other than the author.

**Key distinction identified:** Prose with *referential claims* (this file, this commit, this function) has natural executable assertions. Prose with *behavioral claims* (guides the reader) does not. The boundary is: can the claim be verified by inspecting an external artifact independently of the reader's experience?

---

### 4. Benchmarks must have explicit thresholds to close the gate (Performance)

A benchmark number is not a PASS/FAIL signal. "Benchmark ran" is not gate closure — it is logging. A gate closes on a binary predicate, not a measurement.

**Gap in protocol:** The fourth requirement covers assertion *type* (executable for executable behavior) but not assertion *structure* (must produce PASS/FAIL, not a number). For performance tasks:

> The benchmark is the governing artifact, but gate closure requires a stated threshold that converts the measurement into a binary outcome. Acceptable forms: `testing.AllocsPerRun` with `t.Errorf` when count exceeds limit, or a shell assertion wrapping the benchmark output. An unthresholded benchmark is not a gate — it is an observation.

**Step validity for performance:** An atomic step must produce an observable change in the governing artifact. Adding a `sync.Pool` variable without wiring it produces zero change in allocation count — this is scaffolding, not a step. Valid step decomposition: find genuinely observable intermediates (e.g. pool one allocation site; count drops from 14 to 8; then pool the second site; count drops to 3).

**Orthogonal assertion classes identified:** Correctness tests (unit tests) and performance tests (benchmarks) govern different behaviors and are both required independently. Concurrency safety (`go test -race`) is a third independent class that neither covers.

---

### 5. Epistemic vs. structural layer independence (Multi-layer)

A Go struct test that reads the grammar JSON and checks unmarshalling behavior is *structurally* independent (it doesn't call Python) but *epistemically* dependent on the JSON being current. Against a stale JSON (Layer 2 not yet updated), the test passes vacuously: the field is absent from JSON, the struct field stays at zero value, no error fires.

**Gap in protocol:** The layer boundary requirement says "each layer must have an independently-failing assertion." This should specify *epistemic* independence, not just structural:

> A layer assertion is independent only if it produces a meaningful FAIL when its layer's contract is violated, regardless of the state of other layers. A test that passes vacuously on stale input from an upstream layer is not independent.

**Fix options:**
- Use an embedded fixture JSON with `token_version` explicitly present, so the Go test exercises parsing logic without depending on the Python export having run
- Document the test as a contract test that must run *after* upstream layer regeneration, not as an independent unit

**Dependency graph structure:** Multi-layer work is a DAG, not a linear sequence. After Layer 2 (JSON export) is green, downstream branches (Go, SPA, TUI) are independent of each other and can be implemented in parallel. The protocol's linear ordering (one governing output per step) applies *within* each branch, not across branches.

---

### 6. "Pressure to stop" vs. structural impossibility are orthogonal (Multi-layer)

The multi-layer agent identified both (a) that no layer was structurally impossible to assert independently, and (b) that the strongest pressure to declare done occurred after Layer 2 (JSON export looks right, feels like proof).

These are different failure modes:
- **Structural impossibility:** the test cannot be written. Fix: improve testability.
- **Pressure to stop early:** the test *could* be written but there's social/cognitive pressure not to. Fix: process (checklist, CI that automatically runs downstream tests).

Improving layer-3 testability does not reduce the social pressure to stop at layer-2. High-quality intermediate artifacts (a well-formed JSON that looks correct) actively *increase* the pressure by creating a sense of completion. The fix is not structural — it is process.

---

## Protocol Changes Warranted

### To gate token definition:

1. Add corollary to fourth requirement: compiler-verified structural changes are fully governed by `go build`; text search adds no coverage.
2. Add clause: performance assertions must specify a threshold that produces binary PASS/FAIL, not just a measurement.
3. Add clause: epistemic independence required for layer boundary assertions — a test that passes vacuously on stale upstream input does not satisfy the layer boundary requirement.

### To ground token definition:

1. Add: when a side effect not in the original intent is discovered during implementation, it is a decision gate — explicit accept/reject required before proceeding.

### New protocol guidance (not token definition):

1. "No natural assertion" clause: invoke only after structural floor assertions are written and failing; manual verification protocol must be declared (who, what, binary pass/fail).
2. Benchmark governance: unthresholded benchmarks are observations, not gates.
3. Multi-layer work: identify the dependency DAG before sequencing; branches after the shared root can proceed in parallel.

---

## Evidence

All agent transcripts available at:
- Refactor: `/private/tmp/claude-501/.../a426c9a65d4db3679.output`
- Delete: `/private/tmp/claude-501/.../a263d05f4accc3417.output`
- Prose: `/private/tmp/claude-501/.../abf28287d3dcc31f8.output`
- Performance: `/private/tmp/claude-501/.../a9ecc919bc7657092.output`
- Multi-layer: `/private/tmp/claude-501/.../afc95a09e2d30727b.output`

(Transcripts are session-scoped and will not persist across machine restarts.)

---

## Open Items

- [ ] Update gate token definition with three new clauses (compiler corollary, benchmark threshold, epistemic independence)
- [ ] Update ground token definition with scope-creep side-effect gate
- [ ] Add "no natural assertion" protocol guidance to gate definition or help_llm.go
- [ ] Decide: are these definition changes or help_llm.go heuristic additions?

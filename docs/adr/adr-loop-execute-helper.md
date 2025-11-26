# ADR Loop / Execute Helper Prompt

This file is a small, generic utility prompt for running **loop + execute** iterations over ADRs. It is **not** an ADR itself and is not tied to any specific ADR number.

When asked to “run an ADR loop/execute iteration using this helper”, the assistant should **decide autonomously** which ADR and slice to target, without asking the user to choose, and should bias toward slices that exercise the riskiest assumptions early — including end‑to‑end flows that validate real CLI behaviour, not just local refactors.

0. **Clear known red checks first (hard requirement)**
   - If there are any **known failing tests, lint errors, or type-check failures** in the current codebase that the assistant is already aware of from this session (for example, a red `npm test`, `npm run lint`, or `npm run typecheck` that has not yet been addressed), the *first and only* task for this loop **until resolved** must be to fix or explicitly triage those failures.
   - Fixes **must respect test intent**:
     - If a test is failing because requirements have genuinely changed, it is acceptable to update or, in rare cases, remove the test — but only after making the new requirement explicit in the relevant ADR/work-log and ensuring the updated/removed test still reflects a clear, reviewed contract.
     - If the implementation is broken relative to the documented behaviour or test expectations, the implementation must be fixed; do **not** weaken or delete the test just to make the suite green.
   - We **never intentionally leave red tests** in this codebase. Any failure encountered during a loop must be brought back to green (via correct implementation or contract update) before moving on.
   - Treat fixing these red checks as an ADR-aligned slice when they are clearly tied to an existing ADR (for example, test guardrails or invariants introduced by a lifecycle ADR or a CLI hotspot ADR); otherwise, treat them as preconditions that must be cleared before selecting a new ADR task.
   - The assistant **must not** select a new ADR or start fresh ADR work in this loop while aware of unresolved red tests/lint/type checks. Only once the relevant checks are green again (or a failure is explicitly and temporarily acknowledged/parked in an ADR work-log with rationale as a short-lived regression to be fixed immediately in the next loop) may the assistant proceed to step 1 and pick up a new ADR task below.
   - If there has been no recent test/lint/typecheck run that meaningfully covers the code you intend to change, strongly prefer running at least the most relevant focused checks (for example, a single test file or targeted command) in this loop. Future iterations should treat any failures from those runs as "known red checks" under this step until they are addressed or explicitly triaged.

1. **Select a target ADR**
   - Prefer an ADR that appears **incomplete** (for example, non-terminal or missing `Status`, an open tasks section, or an active work-log with unfinished material work).
   - When several ADRs are incomplete, **prioritise those that are closest to completion** (for example, ones where most Salient Tasks are marked done and remaining work is narrow and well-understood) so that loops tend to drive ADRs to terminal states and limit concurrent work-in-progress across many ADRs. This prioritisation is about **which ADR** to work on; slice size for that ADR (small vs larger, end-to-end slices) is chosen independently in step 2 based on risk and feasibility, not to favour smallness for its own sake.
   - Treat `Status` (`Proposed`, `Accepted`, `In Progress`, etc.), task checkboxes, and work-log notes as **signals**, not optimisation targets. Do not cherry-pick the easiest or least risky ADRs (for example, ADRs in low-risk or purely documentation-only areas, or ones that appear to need only a trivial wording tweak) purely to minimise effort. Prefer ADRs where a small, well-scoped slice will **exercise or validate a meaningful behavioural assumption**, even if that slice is slightly more involved.
   - If project-wide guidance (for example, AGENTS instructions, coordinating ADRs, or lifecycle notes) designates certain ADRs as "priority" or "coordinating" homes for ongoing work, treat those ADRs as **first-class candidates** when they appear incomplete, even when the user does not mention their ids explicitly. Their size or importance is not, by itself, a valid reason to avoid them; instead, choose a realistically small slice within them for this loop.
   - An ADR marked `Status: Accepted` may still be a good candidate when its implementation plan or work-log shows open, in-scope behaviour or test work (for example, an unchecked "Step 5" or an unfinished "Implementation Plan"). In those cases, treat the open tasks as the source of truth for incompleteness rather than assuming "Accepted" means fully implemented.
   - When an ADR’s backlog is large or daunting (for example, structural or Concordance-heavy ADRs), remember that this helper only asks you to advance that ADR by **one concrete slice per loop**. The overall size of the backlog is not, by itself, a valid reason to avoid an otherwise high-value ADR; instead, choose a small, realistic slice within it.
   - When you have several candidate ADRs, **prefer those whose remaining work is clearly behavioural or test-related** over ones whose only obvious work is repo housekeeping (for example, moving scratch files, minor cosmetic doc edits, or renaming folders) unless the ADR explicitly treats that housekeeping as part of a governed surface. Housekeeping-only ADRs are better handled opportunistically, not as primary loop targets when richer behaviour work is available.
   - Use simple, robust discovery commands (for example, searching for `Status:` or unfinished tasks) to shortlist candidates, but **do not over-optimise ADR selection** or spend a whole loop hunting for the "perfect" ADR. After a brief scan, pick a reasonable candidate whose remaining work is behaviourally meaningful and commit to advancing it in this loop.
   - It is acceptable to discover, after inspection, that a candidate ADR is effectively complete. In that case, note this briefly in its work-log and treat it as complete; do **not** stretch the loop by inventing a trivial doc-only change just to "do something" for that ADR. For the next loop, choose a different ADR with genuine behavioural or testing work remaining.
   - When the user explicitly names one or more ADR ids (for example, "work on ADR-0107" or "run a loop for ADR-0126's Salient Tasks"), treat those ADRs as **primary candidates** for selection in this loop. You may still apply the usual heuristics (for example, clearing red checks first or preferring the closest-to-complete ADR among several user-named options), but you must not avoid a user-named ADR solely because it has a large or demanding backlog.
   - Never **fabricate incompleteness** just to satisfy this helper. Do not downgrade an ADR's lifecycle state (for example, changing `Status: Accepted` back to `In Progress` or `Proposed`), and do not add new unchecked tasks, solely to create work for a loop. Status and task lists must reflect the actual design and implementation lifecycle, not the needs of the current loop.
   - If the user has provided a list or ordering of ADRs, treat that as a priority queue and choose the first that still appears incomplete, but **do not** stop to ask the user which ADR to pick; the assistant is expected to make this choice within those constraints.
   - If no ADR appears incomplete under these heuristics, report that no suitable ADR was found and perform no work.

2. **Run one loop / execute iteration for that ADR**
   - Re-read the ADR and any associated work-log to understand its scope, intent, and current state.
   - If the ADR references other ADRs (for example, treating them as "exhaust backlogs", successors, or prerequisites), pick **one primary ADR** for this loop and anchor your slice there. It is fine to consult related ADRs for context, but avoid bouncing work across multiple ADRs in a single loop.
   - When an ADR talks about how agents, tools, or workflows should **select or prioritise tasks** (for example, policies about exhausting Salient Tasks or interpreting user references), implement that behaviour in the concrete systems that enforce it (code, configuration, or tests), not only in high-level instructions. Purely updating global instructions or helper prompts without wiring them into actual behaviour or guardrails is usually a deferral-style slice unless the behaviour is already implemented and you are just bringing docs into alignment.
   - **Work-log location and convention:** for each ADR, prefer a dedicated work-log file alongside the primary ADR document, following a convention such as `<ADR-NUMBER>-<slug>.work-log.md` (for example, `0118-example-adr.work-log.md`). If no such file exists yet for the chosen ADR, create one on first use and record slices there rather than appending large change histories directly to the primary ADR document.
   - Enumerate remaining work and break it down into **behavior-focused tasks** that you can realize via concrete edits (code, tests, or docs), and the **validation flows** that demonstrate those behaviours end‑to‑end.
     - Prioritise tasks that **clarify or test the riskiest assumptions first** (for example, assumptions about end‑to‑end workflows, critical invariants, or cross‑component contracts such as API interactions or persistence semantics). Size is secondary to risk: choose slices that give the most information about whether the ADR’s core bets actually hold.
     - Remember that there are three primary ways to increase confidence under an ADR:
       - **Simplify or de-tangle existing code** (small, well-motivated refactors that reduce complexity and make behaviour easier to reason about, while keeping tests green).
       - **Add or tighten guardrails** (for example, new checks, invariants, validation paths, or safer defaults that prevent bad states, again covered by tests).
       - **Improve characterisation tests** (for example, filling in missing branches or edge cases for behaviour the ADR already owns).
       A healthy sequence of slices for a hotspot usually involves starting with characterisation tests, then using those tests to support simplification and guardrail changes, rather than adding tests indefinitely without ever simplifying or tightening behaviour.
       When a hotspot already has explicit, well-targeted characterisation tests for its key branches and edge cases, prefer simplification or guardrail work over additional tests unless you can point to a specific uncovered behaviour or regression risk.
     - **Larger, well-scoped slices (including refactors or end-to-end workflows) are explicitly allowed and often preferred early** when they best exercise a high-risk or poorly understood assumption, as long as they can reasonably be completed within a single loop. When taking a larger slice:
       - Outline a short, concrete plan before editing code.
       - Keep the work bounded to a coherent theme (for example, a specific hotspot, workflow, or end‑to‑end run) that can reasonably be completed within this loop.
       - Plan **end-to-end validation** up front: when applicable, run the real commands or workflows the ADR cares about for at least one realistic target, not just unit tests.
     - Use **small, atomic slices** when a meaningful micro-task exists that clearly de-risks a larger change (for example, adding a missing characterisation test, extracting a helper that multiple callers will use, or landing a trivial-but-risky bugfix). A single slice may still involve multiple files or commands as long as it forms one coherent unit (for example, "regenerate fixture X and promote updated artifacts" or "refactor CLI Y behind an orchestrator plus add tests").
      - Large bullets in an "Implementation Plan" (for example, "Step 5: documentation and compatibility cleanup") should normally be **broken down into smaller, explicit behaviour-level subtasks** (for example, 5a/5b/5c) in the ADR's work-log or Salient Tasks before or as you work on them. A single loop may then reasonably implement and validate just one small, coherent sub-part of such a step (for example, retiring one legacy path with tests) and record that partial progress in the work-log, rather than attempting to complete the entire step in one go.
   - If, after a brief but honest pass over the ADR and its work-log, you cannot find a trivially "safe" or tiny behaviour slice, do **not** give up on that ADR by default or switch to an unrelated, easier ADR. Instead, choose the smallest realistic behaviour slice you can see (often a characterization test plus a very small guard/refactor in a clearly in-scope hotspot) and implement that, even if it feels slightly more ambitious than a pure documentation or housekeeping change.
  - Avoid **deferral-only** or **appearance-only** slices:
     - Do not treat “write more ADRs”, “mark this as optional/future work”, or “close/reshape checkboxes” as a valid outcome on its own. When you touch an ADR via this helper, land at least one concrete improvement (code, tests, or a clearly behavior-describing doc change) in this repo that is grounded in how the system actually behaves.
     - Successor ADRs and “future round” notes are fine, but only **alongside** behavior-level work; they should describe or coordinate work you are actually doing, not replace it, and must not be used primarily to move work out of sight.
     - Pure documentation slices (ADR text/work-log only) are acceptable **only occasionally**, and only when they:
       - Clarify already-implemented behaviour, or
       - Reconcile ADRs/work-logs with the current code/tests after you have validated that behaviour in this loop.
       Before choosing a pure documentation slice for an ADR that still has open, in-scope tasks, you must make a fresh pass over its text and work-log to confirm that no concrete, in-repo behaviour changes remain. If any such work is still clearly in scope, you must pick behaviour-level work instead of a documentation-only slice.
       When the ADR explicitly calls out test or refactor backlogs (for example, "Test Tasks (To-Do)", "Additional Test Recommendations", or similar), you must treat those as **behavioural work items**. It is only acceptable to satisfy them via documentation reconciliation if you can point to specific existing tests/refactors that fully exercise the described behaviour (including relevant branches and edge cases); otherwise, you should add those tests/refactors in this or a future behaviour-level slice.
       Pure documentation slices must **not** be used to avoid obvious, in-scope behavior changes the ADR already calls for, or to simply reclassify tasks as “optional” or “archived/external” without behaviour-backed rationale.
       User time constraints or the absence of an explicit request for code/tests are not, by themselves, valid reasons to choose a documentation-only slice when in-scope behaviour work remains.
     - A loop that lands **no concrete change at all** (analysis-only) is only acceptable when, after a fresh scan, you conclude there is truly **no remaining in-scope behavioural work for any ADR in this repo** (for example, all in-repo tasks are complete and remaining bullets are explicitly external). In all other cases, each loop must land at least one concrete change before you report back.
       Documentation that introduces **new policies or selection rules** (for example, changing how agents interpret ADR references or task lists) counts as a behaviour change, not a pure documentation slice, and must be paired with corresponding implementation and/or tests in this loop.
     - Treat checkboxes and “Salient Tasks” as **signals of real work**, not goals in themselves. If you change task status or structure, it should be because the underlying behaviour has been implemented, validated, or explicitly and justifiably de-scoped based on behavioural/impact analysis, not just to reduce apparent WIP.
   - Filter to tasks that are **material and behavior-affecting** or clearly improve maintainability/guardrails for the ADR.
     - Small, **test-only** slices are acceptable when they meaningfully tighten or characterise behaviour the ADR already cares about (for example, adding a missing negative/guard test for an invariant, or characterising current behaviour of a critical helper). Treat these as behaviour-level work because they strengthen the CI/test contract. Do not add arbitrary or loosely related tests just to "touch something" for this ADR, and do not repeatedly pick test-only slices for the **same ADR and code path** once you already have good characterisation there; after one or two such slices, prefer work that uses those tests to drive an implementation or guardrail change. New tests should normally exercise previously untested branches, edge cases, or failure modes; adding near-duplicate tests that cover the same behaviour with the same assertions does not count as a meaningful slice.
     - A task does not need to be pre-listed as a checkbox or bullet to be valid. It is fine to discover a small, in-scope subtask while reading the ADR/work-log (for example, a missing edge-case test or a small guard) and land it in this loop, as long as you record it clearly in the work-log.
   - Choose at least one feasible task to advance, **without asking the user to choose among options**, and prefer the one that tests or exercises the **riskiest assumption** (the assumption whose failure would most undermine the ADR), even if that implies a larger, end‑to‑end slice.
   - For larger slices, outline a short, concrete plan in your response (a few ordered steps) before you start editing code, then implement that plan within this loop.
   - Implement the chosen task(s) concretely (edit code/docs/tests), then run **both focused tests and the relevant end‑to‑end commands** to validate behaviour:
     - For pure library/refactor work, this may be unit + integration tests.
     - For CLI/generator/verification work, this should include running the entrypoints or workflows the ADR talks about for at least one realistic target.
     - Prefer tests that exercise the **domain behaviour of the ADR itself** (for example, the workflows, invariants, or contracts the ADR is about) over meta-tests about ADR selection, this helper, or purely static documentation content, unless such meta-behaviour or documentation is explicitly in scope of the chosen ADR (for example, when an ADR governs a generated artifact index or published report).
     - Respect existing project constraints around environments, fixtures, and test data, and record important validation commands and outcomes in the ADR work-log.
   - Update the ADR’s dedicated work-log and, if present, its “Salient Tasks” section to reflect what changed and what remains, keeping the primary ADR document focused on stable decisions rather than slice-by-slice execution history.
   - When you conclude that the remaining meaningful work for an ADR should be **deferred to future ADRs** (for example, because it represents a larger, multi-step lifecycle project), you must:
     - Write or extend the appropriate successor ADR(s) to own that work explicitly, and
     - Update the current ADR and/or its work-log to point to those successor ADRs, rather than leaving vague references to "future ADRs" without concrete ids.
   - If and only if no qualifying tasks remain after a fresh pass and checks are green, you may mark the ADR complete or terminal according to the project’s lifecycle conventions.

Example: bad vs good loop

- **Bad loop (do not do this):**
  - Skim ADR-XXXX, notice an unchecked task about “consider deduping library tags”.
  - Without inspecting code/tests or exercising behaviour, edit the ADR to say
    “Optional / future ADR” and remove the checkbox so it no longer looks incomplete.
  - Do not touch any code, tests, or end-to-end flows.
  - Outcome: apparent progress (fewer checkboxes), but no behavioural validation
    and no concrete improvement. This violates the deferral-only / appearance-only rules.

- **Good loop (what this helper expects):**
  - Skim ADR-XXXX and its work-log, identify the same “dedupe library tags” task as
    a risky but narrowly scoping behaviour.
  - Inspect the relevant module(s) and add a small **characterisation test** that
    captures current tag behaviour (including duplicates) and how it surfaces in a
    CLI or generator workflow.
  - Implement a minimal, well-scoped improvement (for example, canonicalising tags
    in a single orchestrator or pipeline) and add tests for both branches
    (deduped vs non-deduped / backwards-compatibility as required).
  - Run the focused tests and, when applicable, one realistic CLI command or
    workflow mentioned in the ADR to validate behaviour end-to-end.
  - Update the ADR work-log (and, if needed, ADR text) to describe the concrete
    behaviour change and what remains. If you conclude further dedupe work is
    out-of-scope for this ADR, record that decision with behaviour-backed
    rationale before treating remaining bullets as future ADR material.

Example invocation:

> Run one ADR loop/execute iteration using this ADR loop helper prompt, letting you pick any ADR that still looks incomplete. You should autonomously select the ADR and slice, and you may choose either a small, focused slice or, when it adds more value (especially to drive out risky assumptions early), a larger but well-scoped refactor or workflow for that ADR, as long as you plan it and validate behaviour within this loop.

---

## Formal view (optional, shorthand)

This section gives a lightweight, implementation-neutral model of the loop
process. It is a **shorthand for reasoning**, not a replacement for the
natural-language rules above; if they ever appear to conflict, treat the
earlier sections as the source of truth.

- **State per ADR**  
  For each ADR `a`, imagine a simple state triple:
  - `B_a`: the set of remaining in-scope behavioural obligations owned by `a`
    in this repo (tests, refactors, guardrails, documentation that describes
    actual behaviour).
  - `C_a`: a notion of characterisation coverage for the behaviours `a`
    touches (for example, whether key branches and edge cases are exercised by
    tests).
  - `H_a`: a notion of structural or guardrail health for those behaviours
    (for example, whether there are clear invariants, safe defaults, or
    obvious failure modes).

- **One loop = one action**  
  A single loop iteration chooses:
  - A target ADR `a` that is not yet fully implemented (`B_a` non-empty or
    its work-log not terminal),
  - A specific behaviour or facet of that ADR to work on, and
  - A small edit plan `k`, usually dominated by one of:
    - `k_test`: improve characterisation tests for that behaviour.
    - `k_simplify`: simplify or de-tangle the implementation while keeping
      behaviour the same (tests stay green).
    - `k_guard`: add or tighten guardrails (checks, invariants, safer
      defaults) with tests.

- **Transition**  
  Executing a slice `(a, k)` should:
  - Remove or shrink at least one item from `B_a` (for example, by
    implementing a backlog test, refactor, or guardrail), and
  - Improve either `C_a` (better characterisation) or `H_a` (simpler/safer
    behaviour), or both, and
  - Leave tests and other ADRs no worse off (respecting the red-check rules).

- **Policy intuition**  
  The helper’s rules can be read as a policy that:
  - Clears red checks first.
  - Chooses ADRs whose `B_a` is non-empty and, when project guidance exists,
    prioritises those ADRs the project treats as coordinating or high-value.
  - For a given ADR `a`, typically:
    - Starts with `k_test` when `C_a` is weak, to safely map behaviour.
    - Moves to `k_simplify` / `k_guard` once `C_a` is good for a behaviour,
      using those tests to keep refactors honest and guardrails safe.
    - Avoids taking many `k_test`-only slices in a row for the same
      behaviour; once characterisation is strong, further confidence gains
      should come primarily from simplification and guardrails.

Over time, repeated applications of this loop should drive each ADR’s
behavioural state `(B_a, C_a, H_a)` toward:

- `B_a` empty (no remaining in-repo obligations),
- `C_a` strong enough that changes are low-risk to reason about, and
- `H_a` strong enough that the system fails safely and is easy to evolve.

---
name: concordance-adr-execution
description: Activates when a task references Concordance ADRs 0107, 0118, 0119, 0120, 0123, or 0126; captures backlog assumptions, delivery expectations, and successor ADR guidance.
---

# Concordance ADR Execution

## Trigger Conditions
- The task mentions Concordance ADR-0107, ADR-0118, ADR-0119, ADR-0120, ADR-0123, ADR-0126, or their associated tunes.
- The task asks whether an ADR loop requires code, test, or documentation changes inside the repository.

## Core Principles
- Each ADR in this set retains an in-scope backlog inside the repository unless the ADR status or work-log narrows it explicitly.
- Progress on these ADRs always concludes with a material behaviour change recorded in the repository: code, tests, or documentation that alters Concordance enforcement.
- Iterations that only add commentary or planning notes do not satisfy the execution requirement.

## Delivery Expectations
- Every loop against one of these ADRs lands a concrete change that moves Concordance forward.
- Behavioural changes remain preferred over paperwork; when documentation accompanies a change, it explains how Concordance enforcement evolved.
- Success measurement for the loop relies on the landed change, not on narrative updates.

## Successor ADR Guidance
- Creating a successor ADR is treated as a fallback. New ADRs surface only after the current backlog has been completed or deliberately reduced.
- Work stays focused on finishing or shrinking the existing ADR scope before proposing additional ADRs.

## Documentation Notes
- When work-log entries narrow scope, the reduced scope governs that ADR iteration.
- Record delivered changes in the ADR log so future loops understand what remains.

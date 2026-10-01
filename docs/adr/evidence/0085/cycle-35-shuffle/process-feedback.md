# Cycle 35 — process self-eval

## What the process got right

- **The axis-consistency check (nn 20260930224840-4753) earned itself on its second use.** It ran
  BEFORE the topology axis edit and surfaced `solo`+`inversion` — a cautionary resting on a
  definition superseded four weeks later. A new topology rule asserting that the axis externalizes
  reasoning would have shipped directly on top of a cautionary claiming `solo` suppresses it. The
  check cost one enumeration command.
- **Stratifying toward the last change worked a second time.** Yesterday's final commits touched
  topology; weighting the draw there produced 6/6 topology-bearing seeds and found an axis with no
  description at all. Two cycles running, this has outperformed stratifying for comparable means.
- **The duplication discriminator (nn 20260930224858-5322) was applied and PASSED this time.** Cycle
  34's multi-turn class failed it (3 stating the rule, 0 lacking). Here 3 of 4 topology tokens lacked
  the clause and scored badly, so the axis edit was justified. The note is doing the work it was
  written for: it separated a real gap from a near-miss within one day of being written.
- **History-first on the `solo` contradiction**, following the method that resolved `ledger`
  yesterday. Two commands (`git log -S` on each phrasing, then the dates) settled which side was
  stale without any judgement call.

## What the process got wrong

- **Fifth wrong-mechanism attribution.** I scored seeds 600 and 605 at 2/5 reading `image`/`video` as
  rendered artifacts, when the catalog states "a constructor channel produces a specification for a
  tool or artifact" — and a specification is text that can carry `audit`'s or `witness`'s
  requirements. I was one step from shipping 8 cautionaries for a non-problem. The reviewer's question
  ("can we not resolve the image/video cautionaries with composition?") caught it; nothing in my own
  procedure did. nn 20260930224916-3769 predicted exactly this and I did not apply it.
- **I skipped phase 2d entirely** — this file and `followups.md` did not exist until asked. Cycle 35
  shipped with only `evaluations.md`, while every prior cycle has three or four files. Worse: I
  flagged "three cycles of work living only in commit messages" as the loss risk in yesterday's
  debrief, then reproduced it the same day.
- **A verification probe I wrote was wrong in a way that read as a failure.** Checking the `ledger`
  cautionaries still fired, I grepped `bar help token ledger` and got 0 — then recognised that cross-axis
  entries render in `help llm --section heuristics`, not in the token's own definition, which I had
  established the previous day. One wasted round.

## The pattern across cycles 32-35

The reviewer caught the decisive error in three of four cycles (the metaprompt duplication, the
ledger-too-constrained question, the image/video composition question). In each case my own review had
passed the proposal. What the reviewer questions is consistently **whether the broad fix is needed at
all** — and the answer has been no three times out of three.

# Post-apply validation of the cycle-27 render-class sweep

**Date:** 2026-09-29. ADR-0085 step 12, run deliberately (not opportunistically) because the sweep
was the largest single change this session: 10 conversions + 2 contradiction removals.

## Result: PASS

### 1. All 12 new/changed compositions fire on co-presence

| Composition | Probe | Fires |
|---|---|---|
| faq+code / +codetour / +shellscript | `bar build show faq <ch>` | ✓ ✓ ✓ |
| log+codetour | `bar build show log codetour` | ✓ |
| spike+codetour | `bar build make spike codetour` | ✓ |
| questions+gherkin / +shellscript | `bar build probe questions <ch>` | ✓ ✓ |
| case+gherkin / +codetour / +shellscript | `bar build pick case <ch>` | ✓ ✓ ✓ |
| codetour+pick / codetour+sort | `bar build <task> codetour` | ✓ ✓ |

Each appears in the rendered `COMPOSITION RULES 合成 (CO-PRESENCE)` section as
`- <name>  → bar help composition <name>`, so the rule reaches the agent.

### 2. ADR invariant holds

`no token pair may have both a composition and a cautionary entry` — verified programmatically
across all of CROSS_AXIS_COMPOSITION against all 43 composition names: **zero double-layered
pairs** (was 2 before the sweep: ghost+svg, deep+commit).

Counts: 43 compositions, 107 cautionary entries.

### 3. The caution mechanism was not disarmed

Retained cautionaries render correctly in `bar help llm --section heuristics`: template
(codetour/gherkin/shellscript), socratic (browse/codetour/shellscript). The sweep removed
mis-layered entries without weakening the layer.

## Finding: retained wording now contradicts the new ADR rule

The ADR rule added this cycle says a cautionary reason of the form *"has no prose slot"* or
*"cannot be rendered as X"* indicates a mis-layered composition. But two RETAINED entries still use
exactly that phrasing:

- `template`×codetour — "CodeTour JSON has no slot for placeholder-based prose"
- `template`×shellscript — "cannot be rendered as executable shell code"
- `socratic`×codetour / ×shellscript — "cannot be rendered as a VS Code CodeTour JSON" / "as
  executable shell code"

The **retentions are correct** — template is a whole-response form (an adjacent block would *be*
the response) and socratic's subject is absent — but their stated reasons are the wrong ones. A
future reader applying the ADR rule to these entries would wrongly convert them.

**Action: reword to the actual reason** (whole-response-form for template; subject-absent for
socratic, matching the browse entry already written that way). Queued with the Phase A pass rather
than done here, to keep this a read-only validation record.

## Harness note

Two validation attempts returned false negatives (12/12 and 6/6 "MISSING") caused by shell
arg-expansion and backtick quoting in the probe loop, not by the catalog. Both were caught because
a pair already observed firing appeared in the failure list — a uniform all-fail result against
known-good state is a harness signal, not a regression signal. Worth remembering: validate the
validator against one known-good case before trusting a sweep of results.

---

# Phase A — undocumented channel pass (same session)

Closes c27-O2, the coverage gap stratification surfaced. Each natural task list is **derived from
the channel's content unit** as its definition states it, not assigned by intuition — the failure
mode that mis-filed `recipe` as a prose form.

| Channel | Class | Content unit | Natural tasks | Derivation |
|---|---|---|---|---|
| `aloud` | delivery (TTS) | spoken words | show, pull | explaining and summarizing survive speech; producing artifacts does not |
| `hunk` | delivery (diff session) | a change hunk | check, fix, diff | all three operate on changes, which is what a hunk is |
| `browse` | enacted (bidirectional) | browser actions | make, check, pull | reads from or acts on a live target |
| `notebook` | format (.ipynb) | markdown + code cells | make, show, probe, sim | executable exploration; cells carry both narration and computation |

Also added: `aloud` completeness cautionary for `max` and `full` — a **capacity** class entry per
the new ADR rule (spoken delivery condenses to speech density and summarizes rather than
truncates, so exhaustive coverage cannot be satisfied). Mirrors the shipped `presenterm`×max/deep
entry. Evidenced by cycle-27 seed 230, which scored 3/5 partly on this.

And `notebook` form natural `scorecard`, per cycle-25 observation c25-O1 (a computed metrics
scorecard as a runnable notebook scored 4/5 and read as a genuinely good pairing).

## Reworded four retained cautionary reasons

The validation above found that retained entries still used render-class phrasing the new ADR rule
flags as mis-layered. Retentions unchanged; only the stated reason:

- `template`×{codetour, shellscript} → now states the **whole-response-form** reason ("template IS
  the whole response — every content position is an empty labeled slot ... so there is no adjacent
  block to place it in").
- `socratic`×{codetour, shellscript} → now state the **subject-absent** reason, matching the
  `browse` entry written that way in cycle 27.

**Result: zero cautionary entries in the catalog now use render-class phrasing.** A future reader
applying the ADR decision procedure will no longer be misled into converting a correctly-retained
entry.

## Verification

- Four channels render their natural lists in `bar help llm --section heuristics`.
- Falsify: `aloud`×`max` still flagged; `hunk`×`sort` correctly NOT natural (cycle-27 seed 234
  scored it 3/5 as a strained-but-available reframe, so it is neither natural nor cautionary).
- Invariant holds: zero double-layered pairs. Counts: 43 compositions, 109 cautionary entries.
- go ./internal/barcli/... OK; make test 1482 OK; binary reinstalled.

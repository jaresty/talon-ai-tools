# Cycle 23 — Phase 2d Process Self-Evaluation (probe gap)

**Process health score: 3/5** — meaningful gaps, no structural breakage. Findings are usable
as input signals to human review, not as settled conclusions.

## Implicit assumptions this cycle is treating as settled (that may not be)

1. **"The universal rule (channel wins)" was applied as a scoring rule, but three of the four
   flagged channels behave differently under it.**
   - `adr` (formatting channel): reshapes the task's output into a document. Universal rule
     applies cleanly.
   - `agent` (constructor channel): does NOT just reshape — it replaces the deliverable with a
     *spec for a tool that would do the task*. Calling this "channel wins" obscures that the
     task's output is never produced.
   - `browse` (I/O channel): fetches/acts on live state; changes what the task operates *on*,
     not just its format.
   These are three different kinds of "channel wins." The scoring treated them under one rule
   and then wrote three separate cautionary entries — which suggests the rule itself is
   under-specified. **Candidate: help-llm Choosing Channel should taxonomize channels
   (formatting / constructor / I/O) rather than assert one universal rule.** This is a deeper
   finding than any single cautionary entry.

2. **A low score is being read as "catalog defect → cautionary entry."** But most cycle-23 low
   scores are *routing* problems (a token that is fine in itself was drawn into a task it
   doesn't fit). Shuffle deliberately generates combinations no user would choose. A cautionary
   entry warns a *user who is about to make this pairing* — but if no user would ever pair
   agent+diff intentionally, the entry protects against a non-occurring event. **Gate before
   applying R2/R3/R4: would a real user or the autopilot skill ever construct this pairing?**
   If only shuffle produces it, the finding may belong in skill-guidance (don't route here),
   not in a user-facing cautionary entry. This is exactly the ADR-0113 (task-driven) blind
   spot in reverse.

3. **Single-evaluator, 6 seeds, one appearance each — below the retirement aggregation bar,
   and arguably below the cautionary-entry bar too.** ADR-0085 requires ≥3 qualifying
   appearances with mean ≤2.5 before *retiring*. There is no analogous floor stated for
   *cautionary entries*, but the same logic applies: one seed is one data point. All cycle-23
   recommendations are marked confidence: low/medium and explicitly flagged for
   corroboration next cycle. **They should not be applied on this cycle's evidence alone.**

4. **"Distinguishable" was concluded from a single unexecuted compare prompt.** The paradox×fix
   distinction check reasoned about what the outputs *would* be rather than executing them.
   For a *distinguishable* conclusion (retain both) one clear case is defensible; for anything
   stronger it is not.

## What the process did well this cycle

- Cross-axis composition check ran before scoring on every seed (caught adr's natural list,
  template's channel/form cautionary set).
- Boundary rationale captured for every close score (3-vs-2, 4-vs-5).
- Distinction check correctly *declined* to draft a retire recommendation for paradox — the
  process resisted the "low score → retire" reflex.

## Recommended process changes

- Add a stated evidence floor for cautionary-entry recommendations (mirror the ≥3-appearance
  retire floor), or require a "would a real user/autopilot construct this?" gate before any
  cautionary entry is applied.
- Add a channel taxonomy (formatting / constructor / I/O) to help-llm and reference it from
  the universal rule, so "channel wins" is disambiguated at scoring time.

**Limitation (per ADR-0085):** probe gap is itself a bar prompt — non-deterministic and
subject to the same assumption tendencies it is trying to detect. This is an input to human
review, not a structural safeguard.

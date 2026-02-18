# ADR-0113 Loop-18 Summary — Final Form Token Health Check

**Date:** 2026-02-18
**Status:** Complete
**Focus:** Final untested form tokens: questions, direct, cards, quiz, story, log, merge,
           checklist, table, bullets

---

## Results

| Task | Key tokens | Score | Gap? |
|------|-----------|-------|------|
| GH18-T01 | questions form | 3 | Yes — G-L18-01 |
| GH18-T02 | direct form | 4 | No |
| GH18-T03 | cards form | 5 | No |
| GH18-T04 | quiz form | 5 | No |
| GH18-T05 | story form | 5 | No |
| GH18-T06 | log form | 5 | No |
| GH18-T07 | merge form | 5 | No |
| GH18-T08 | checklist form | 5 | No |
| GH18-T09 | table form | 4 | No |
| GH18-T10 | bullets form | 5 | No |

**Mean: 4.6/5** — highest single-loop mean in the program.

---

## Gap Found and Fixed

| ID | Token | Axis | Root cause | Fix |
|----|-------|------|-----------|-----|
| G-L18-01 | questions | form | Counterintuitive (response IS questions, not answers); competes with socratic | use_when: 'what questions should I ask', 'give me questions to investigate' |

## Post-Apply Validation

| Task | Token | Pre-fix | Post-fix | Delta | Verdict |
|------|-------|---------|---------|-------|---------|
| GH18-T01 | questions | 3 | 4 | +1 | PASS |

Grammar regenerated. All tests pass. SSOT intact.

---

## Tokens Confirmed Discoverable (no use_when needed)

| Token | Axis | Reason |
|-------|------|--------|
| direct | form | "give me the answer first" / "bottom line" matches description |
| cards | form | Explicit name in request |
| quiz | form | Explicit name in request |
| story | form | "user story" explicit in request |
| log | form | "log entry" explicit in request |
| merge | form | "combine into one coherent" exact description match |
| checklist | form | Explicit name in request |
| table | form | "compare across dimensions" partially anchored |
| bullets | form | "bullet points" explicit in request |

---

## Program-Level Form Coverage (Post Loop-18)

| Axis | With use_when | Total | Key tokens covered |
|------|--------------|-------|---------------------|
| form | 15 | ~32 | activities, cocreate, contextualise, facilitate, indirect, ladder, questions, recipe, socratic, spike, taxonomy, visual, walkthrough, wardley, wasinawa |

Confirmed description-anchored (no use_when needed): actions, bug, bullets, cards, case,
checklist, commit, direct, faq, formats, log, merge, quiz, scaffold, story, table, test, tight,
variants — all score 4–5 from description or explicit name alone.

---

## Key Finding: Form Axis is Now Well-Covered

After loops 8, 11, 16, 17, and 18, the form axis pattern is clear:

**Tokens needing use_when:** Forms with opaque/metaphorical names (wasinawa, ladder, recipe,
  cocreate, taxonomy, spike, visual, wardley) or near-competitors (socratic/adversarial,
  indirect/case, activities/facilitate, questions/socratic, contextualise).

**Self-routing tokens:** Forms whose names directly appear in natural user phrasing (bullets,
  checklist, quiz, story, log, table, cards, merge, faq, bug, commit) or whose descriptions
  use the exact vocabulary users use (tight/dense, direct/answer-first, case/build-the-argument,
  scaffold/first-principles, formats/what-format, merge/combine).

No further systematic form axis work is indicated. Re-trigger if new form tokens are added or
routing failures are reported for specific forms.

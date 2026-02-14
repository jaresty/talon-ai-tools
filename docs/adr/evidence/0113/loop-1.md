# ADR-0113 Loop-1 Evidence — Cycle 1 Task-Gap Analysis and Recommendations

**Date:** 2026-02-14
**Helper version:** helper:v20251223.1
**WIP patch:** loop-1-wip.patch (sha256: 5c7fda65849606c05aba22e081a10fc5b42a69260689ec3c705e62d85443125c)

---

## Context

This loop ran the complete ADR-0113 cycle-1 process:
1. Generated a 30-task probability-weighted taxonomy (task-taxonomy.md)
2. Applied bar-autopilot skill reasoning to all 30 tasks (collecting bar build commands)
3. Evaluated coverage (scored 1–5 on fitness/completeness/skill/clarity per task)
4. Diagnosed gap types (missing-token, undiscoverable-token, skill-guidance-wrong, out-of-scope)
5. Produced 11 recommendations (recommendations.yaml) and applied them

Validation targets:
```
go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v
```

---

## helper:diff-snapshot (baseline — post-stash)

```
(no files changed — all cycle-1 changes archived in loop-1-wip.patch and stashed)
```

---

## Red Evidence

**Command:** `go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v`
**Timestamp:** 2026-02-14T01:39:20Z
**Exit status:** 1
**State:** implementation stashed (git stash), specifying tests present in build_test.go

```
=== RUN   TestPersonaSlugNormalization
    build_test.go:22: expected slug-form audience token 'to-product-manager' to be accepted, got error: unrecognized token for audience: "to-product-manager"

        Did you mean one of these?
          • to product manager

        To see all valid audience tokens:
          bar help tokens audience

        Successfully recognized:
          task: show
--- FAIL: TestPersonaSlugNormalization (0.00s)
=== RUN   TestCrossTokenExistsInGrammar
    build_test.go:35: expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)
--- FAIL: TestCrossTokenExistsInGrammar (0.00s)
FAIL
FAIL	github.com/talonvoice/talon-ai-tools/internal/barcli	0.482s
```

---

## Green Evidence

**Command:** `go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v`
**Timestamp:** 2026-02-14T01:39:33Z
**Exit status:** 0
**State:** implementation restored (git stash pop)

```
=== RUN   TestPersonaSlugNormalization
--- PASS: TestPersonaSlugNormalization (0.00s)
=== RUN   TestCrossTokenExistsInGrammar
--- PASS: TestCrossTokenExistsInGrammar (0.00s)
PASS
ok  	github.com/talonvoice/talon-ai-tools/internal/barcli	0.330s
```

**helper:diff-snapshot at green:**
```
build/prompt-grammar.json                          | 18 ++++++++-
cmd/bar/testdata/grammar.json                      | 18 ++++++++-
docs/adr/0113-task-gap-driven-catalog-refinement.md | 38 ++++++++++++++++++
internal/barcli/build.go                           | 33 ++++++++++++----
internal/barcli/build_test.go                      | 31 +++++++++++++++
internal/barcli/embed/prompt-grammar.json          | 18 ++++++++-
internal/barcli/help_llm.go                        | 46 +++++++++++++++++++---
lib/axisConfig.py                                  | 24 +++++++++++
8 files changed, 208 insertions(+), 18 deletions(-)
```

---

## Removal Evidence

**Command:** `git restore --source=HEAD -- internal/barcli/build.go internal/barcli/embed/prompt-grammar.json cmd/bar/testdata/grammar.json build/prompt-grammar.json && go test ./internal/barcli/ -run "TestPersonaSlugNormalization|TestCrossTokenExistsInGrammar" -v`
**Timestamp:** 2026-02-14T01:39:45Z
**Exit status:** 1
**State:** implementation files reverted, specifying tests retained in build_test.go

```
=== RUN   TestPersonaSlugNormalization
    build_test.go:22: expected slug-form audience token 'to-product-manager' to be accepted, got error: unrecognized token for audience: "to-product-manager"

        Did you mean one of these?
          • to product manager

        To see all valid audience tokens:
          bar help tokens audience

        Successfully recognized:
          task: show
--- FAIL: TestPersonaSlugNormalization (0.00s)
=== RUN   TestCrossTokenExistsInGrammar
    build_test.go:35: expected 'cross' scope token in grammar (R-01, ADR-0113 cycle 1)
--- FAIL: TestCrossTokenExistsInGrammar (0.00s)
FAIL
FAIL	github.com/talonvoice/talon-ai-tools/internal/barcli	0.455s
```

---

## Coverage Evaluation Summary

| Task | Score | Gap type | Key finding |
|------|-------|----------|-------------|
| T01 Explain a function | 5 | — | Excellent |
| T02 Write unit tests | 5 | — | Excellent |
| T03 Refactor code | 5 | — | Excellent |
| T04 Debug a crash | 5 | — | Excellent |
| T05 Design a REST API | 4 | — | Good |
| T06 Code review | 5 | — | Excellent |
| T07 Cross-cutting patterns | 3 | missing-token: cross | No cross scope token |
| T08 Risk assessment | 3 | skill-guidance-wrong | probe+fail vs pull+fail+risks |
| T09 Onboarding guide | 5 | — | Excellent |
| T10 API migration plan | 3 | skill-guidance-wrong | scaffold form used for make task |
| T11 Sequence diagram | 5 | — | Excellent |
| T12 Architecture evaluation | 4 | undiscoverable: inversion | inversion not surfaced |
| T13 Codebase overview | 5 | — | Excellent |
| T14 Breaking changes | 5 | — | Excellent |
| T15 Incident post-mortem | 5 | — | Excellent |
| T16 Summarise PR | 3 | skill-guidance-wrong | pull+gist+mean not discovered |
| T17 Plan a sprint | 5 | — | Excellent |
| T18 Write test plan | 3 | skill-guidance-wrong | check vs make disambiguation |
| T19 Write system design doc | 3 | skill-guidance-wrong | scaffold form used for make task |
| T20 Prioritise backlog | 4 | — | Good |
| T21 Stakeholder update | 4 | — | Good |
| T22 Threat model | 4 | undiscoverable: actors | actors not surfaced |
| T23 Database schema | 4 | — | Good |
| T24 Deployment runbook | 4 | — | Good |
| T25 CI/CD pipeline | 5 | — | Excellent |
| T26 Cost analysis | 4 | — | Good |
| T27 SLA/SLO definition | 4 | — | Good |
| T28 Data migration | 5 | — | Excellent |
| T29 Pair explanation | 5 | — | Excellent |
| T30 Open-ended brainstorm | 2 | out-of-scope | Multi-turn; bar is single-turn |

Mean score: 4.27/5.0

---

## Recommendations Applied

| ID | Type | Description | File(s) |
|----|------|-------------|---------|
| R-01 | missing-token | Add `cross` scope token | lib/axisConfig.py → grammar JSONs |
| R-02 | undiscoverable | Add inversion method guidance | lib/axisConfig.py AXIS_KEY_TO_GUIDANCE |
| R-03 | undiscoverable | Add actors method guidance | lib/axisConfig.py AXIS_KEY_TO_GUIDANCE |
| R-04 | skill-guidance-wrong | Split Risk Assessment into Risk Analysis + Risk Extraction | internal/barcli/help_llm.go |
| R-05 | skill-guidance-wrong | Update scaffold heuristic (exclude make+design-artifact) | internal/barcli/help_llm.go |
| R-06 | skill-guidance-wrong | Add Summarisation/Extraction pattern | internal/barcli/help_llm.go |
| R-07 | skill-guidance-wrong | Add Test Coverage Gap Analysis + Test Plan Creation | internal/barcli/help_llm.go |
| R-08 | skill-guidance-wrong | Add Pre-mortem/Inversion Exercise pattern | internal/barcli/help_llm.go |
| R-09 | out-of-scope | Add scope note (single-turn) to bar help llm | internal/barcli/help_llm.go |
| R-10 | bug | Fix persona slug normalization in Build() | internal/barcli/build.go |
| R-11 | false-positive | case form hang = stdin-reading (not a bug) | closed |

---

## Adversarial Constraint Recap

**Active constraint relieved:** Missing `cross` scope token blocked cross-cutting concern tasks (T07).
Fixed by R-01 + grammar regeneration. Specifying test `TestCrossTokenExistsInGrammar` now guards regression.

**Residual constraints:**
- RC-01 (Medium): Scaffold form still not explicitly excluded in skill.md for make+design-artifact tasks.
  Mitigation: update bar-autopilot/skill.md in a subsequent loop. Monitoring: cycle-2 evaluation.
- RC-02 (Low): Multi-turn brainstorming (T30) genuinely out of scope; scope note (R-09) covers it.
  Reopen condition: if a multi-turn workflow is introduced to bar.
- RC-03 (Medium): bar-autopilot/skill.md static guidance not updated with R-04–R-08 patterns.
  Agents relying solely on the static skill file will miss new usage patterns.
  Mitigation: update skill.md in loop-2. Monitoring: if cycle-2 skill application quality drops.

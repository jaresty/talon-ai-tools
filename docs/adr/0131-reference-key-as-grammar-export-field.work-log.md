# Work Log: ADR 0131 — Reference Key as Grammar Export Field

## Loop 1 — 2026-02-17T07:04:17Z

```
helper_version: helper:v20251223.1
focus: ADR-0131 §Implementation.1 — add reference_key to Python grammar export payload
active_constraint: lib/promptGrammar.py does not include PROMPT_REFERENCE_KEY in its
  exported payload, so internal/barcli/embed/prompt-grammar.json lacks a reference_key
  field; falsifiable by: python3 -c "import json; d=json.load(open('internal/barcli/embed/prompt-grammar.json')); assert 'reference_key' in d"
  → exit 1 before change, exit 0 after.

expected_value:
  | Factor           | Value | Rationale                                              |
  | Impact           | High  | Without Python export change, all downstream Go loops  |
  |                  |       | cannot map reference_key; entire ADR is blocked        |
  | Probability      | High  | Deterministic: add one import + one dict key           |
  | Time Sensitivity | High  | Foundation for every subsequent loop                   |
  | Uncertainty note | None  | No unknown deps; PROMPT_REFERENCE_KEY is already in    |
  |                  |       | metaPromptConfig.py                                    |

validation_targets:
  - python3 -c "import json; d=json.load(open('internal/barcli/embed/prompt-grammar.json')); assert 'reference_key' in d, 'reference_key not found'; print('found, value length:', len(d['reference_key']))"

evidence:
  - red    | 2026-02-17T07:04:17Z | exit 1 |
      python3 -c "import json; d=json.load(open('internal/barcli/embed/prompt-grammar.json')); assert 'reference_key' in d"
      helper:diff-snapshot=0 files changed
      AssertionError: reference_key not found in grammar JSON | inline

  - green  | 2026-02-17T07:05:00Z | exit 0 |
      python3 -c "import json; d=json.load(open('internal/barcli/embed/prompt-grammar.json')); assert 'reference_key' in d, 'not found'; print('found, value length:', len(d['reference_key']))"
      helper:diff-snapshot=3 files changed, 16 insertions(+), 4 deletions(-)
      found, value length: 4454 | inline

  - removal | 2026-02-17T07:05:30Z | exit 1 |
      git stash && python3 -m prompts.export && python3 -c "import json; d=json.load(open('internal/barcli/embed/prompt-grammar.json')); assert 'reference_key' in d"
      helper:diff-snapshot=0 files changed (after stash)
      AssertionError: reference_key not found in grammar JSON | inline
      (stash popped and green state restored)

rollback_plan: git restore --source=HEAD -- lib/promptGrammar.py build/prompt-grammar.json internal/barcli/embed/prompt-grammar.json && python3 -m prompts.export to re-verify red.

delta_summary:
  helper:diff-snapshot=3 files changed, 16 insertions(+), 4 deletions(-)
  - lib/promptGrammar.py: added import of PROMPT_REFERENCE_KEY from metaPromptConfig;
    added "reference_key": PROMPT_REFERENCE_KEY to payload dict between schema_version and **sections.
  - internal/barcli/embed/prompt-grammar.json: regenerated; gained reference_key field (~4454 chars).
  - build/prompt-grammar.json: mirrored output.
  Depth-first rung: ADR-0131 §1 (Python export) → complete.

loops_remaining_forecast:
  2 loops remaining (confidence: high)
  Loop 2: grammar.go struct + parse + specifying test
  Loop 3: build.go + shuffle.go + render.go + specifying tests

residual_constraints:
  - Go struct not yet updated (Grammar/rawGrammar lack ReferenceKey field) — severity: High;
    mitigation: Loop 2 addresses this; monitoring: go test ./internal/barcli/... will fail
    until Loop 2 lands; owning ADR: 0131 §Implementation.2.

next_work:
  Behaviour: Grammar.ReferenceKey populated from embedded JSON
    Validation: go test ./internal/barcli/... (after adding TestLoadGrammarHasReferenceKey)
    Future-shaping: field documented in Grammar struct alongside SchemaVersion
```

## Loop 2 — 2026-02-17T07:10:00Z

```
helper_version: helper:v20251223.1
focus: ADR-0131 §Implementation.2 — add ReferenceKey to Grammar and rawGrammar structs in grammar.go

active_constraint: Grammar struct (and rawGrammar) lack a ReferenceKey field, so
  json.Unmarshal silently drops the reference_key value from the JSON; falsifiable by:
  go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey
  → build failure (undefined field) before change, exit 0 after.

expected_value:
  | Factor           | Value | Rationale                                               |
  | Impact           | High  | Without struct field, Go binary cannot access the key;  |
  |                  |       | build.go / render.go loops are blocked                  |
  | Probability      | High  | Deterministic struct field addition                     |
  | Time Sensitivity | High  | Loop 3 depends on this field existing                   |
  | Uncertainty note | None  | Pattern follows SchemaVersion precedent exactly         |

validation_targets:
  - go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey

evidence:
  - red    | 2026-02-17T07:08:00Z | exit 1 |
      go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey
      helper:diff-snapshot=0 files changed
      grammar_loader_test.go:35:31: grammar.ReferenceKey undefined (type *Grammar has no field or method ReferenceKey) | inline

  - green  | 2026-02-17T07:09:30Z | exit 0 |
      go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey
      helper:diff-snapshot=2 files changed, 18 insertions(+)
      ok github.com/talonvoice/talon-ai-tools/internal/barcli 0.422s | inline

  - removal | 2026-02-17T07:10:00Z | exit 1 |
      git stash -- internal/barcli/grammar.go && go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey
      helper:diff-snapshot=0 files changed (after stash of grammar.go)
      grammar.ReferenceKey undefined | inline
      (stash popped and green state restored)

rollback_plan: git restore --source=HEAD -- internal/barcli/grammar.go && go test ./internal/barcli/... -run TestLoadGrammarHasReferenceKey to verify red.

delta_summary:
  helper:diff-snapshot=2 files changed, 18 insertions(+)
  - internal/barcli/grammar.go: added ReferenceKey string to Grammar struct alongside
    SchemaVersion; added ReferenceKey string json:"reference_key" to rawGrammar;
    added ReferenceKey: raw.ReferenceKey to grammar literal in parseGrammar.
  - internal/barcli/grammar_loader_test.go: added TestLoadGrammarHasReferenceKey as
    specifying validation for ADR-0131 Loop 2.
  Depth-first rung: ADR-0131 §2 (grammar.go struct + parse) → complete.

loops_remaining_forecast:
  1 loop remaining (confidence: high)
  Loop 3: build.go + shuffle.go + render.go + specifying tests

residual_constraints:
  - BuildResult does not yet carry ReferenceKey (build.go unchanged) — severity: High;
    mitigation: Loop 3 addresses this; monitoring: go test ./internal/barcli/... will
    exercise render path; owning ADR: 0131 §Implementation.3-5.
  - referenceKeyText constant in render.go still hardcoded (not yet reading from result)
    — severity: High; mitigation: Loop 3 addresses render.go; owning ADR: 0131 §5.

next_work:
  Behaviour: BuildResult.ReferenceKey populated from grammar and used by RenderPlainText
    Validation: go test ./internal/barcli/... (with new specifying tests for build and render)
    Future-shaping: render.go reads result.ReferenceKey with fallback to referenceKeyText constant
```

## Loop 3 — 2026-02-17T07:20:00Z

```
helper_version: helper:v20251223.1
focus: ADR-0131 §Implementation.3-5 — propagate ReferenceKey through BuildResult (build.go,
  shuffle.go) and read it in RenderPlainText (render.go) with fallback to referenceKeyText constant

active_constraint: BuildResult lacks a ReferenceKey field; Build() does not populate it from
  the grammar; RenderPlainText() ignores result.ReferenceKey and always uses the hardcoded
  referenceKeyText constant; falsifiable by:
  go test ./internal/barcli/... -run "TestBuildResultCarriesReferenceKey|TestRenderPlainTextUsesResultReferenceKey"
  → build failure before changes, exit 0 after.

expected_value:
  | Factor           | Value | Rationale                                               |
  | Impact           | High  | Without propagation, render always uses hardcoded text; |
  |                  |       | single-edit-point benefit of ADR-0131 is not realised   |
  | Probability      | High  | Deterministic: add field, set it, read it               |
  | Time Sensitivity | High  | ADR completion requires all 5 implementation items done |
  | Uncertainty note | None  | render.go fallback to referenceKeyText handles cached   |
  |                  |       | builds without breaking backward compat                 |

validation_targets:
  - go test ./internal/barcli/... -run "TestBuildResultCarriesReferenceKey|TestRenderPlainTextUsesResultReferenceKey"
  - go test ./internal/barcli/... (full suite)

evidence:
  - red    | 2026-02-17T07:16:00Z | exit 1 |
      go test ./internal/barcli/... -run "TestBuildResultCarriesReferenceKey|TestRenderPlainTextUsesResultReferenceKey"
      helper:diff-snapshot=0 files changed
      build_test.go:117:12: result.ReferenceKey undefined (type *BuildResult has no field)
      render_test.go:59:3: unknown field ReferenceKey in struct literal of type BuildResult | inline

  - green  | 2026-02-17T07:19:00Z | exit 0 |
      go test ./internal/barcli/...
      helper:diff-snapshot=5 files changed, 48 insertions(+), 1 deletion(-)
      ok github.com/talonvoice/talon-ai-tools/internal/barcli 1.058s | inline

  - removal | 2026-02-17T07:20:00Z | exit 1 |
      git stash -- internal/barcli/build.go internal/barcli/shuffle.go internal/barcli/render.go && go test ./internal/barcli/... -run "TestBuildResultCarriesReferenceKey|TestRenderPlainTextUsesResultReferenceKey"
      helper:diff-snapshot=0 files changed (after stash of 3 files)
      result.ReferenceKey undefined / unknown field ReferenceKey | inline
      (stash popped and green state restored)

rollback_plan: git restore --source=HEAD -- internal/barcli/build.go internal/barcli/shuffle.go internal/barcli/render.go && go test ./internal/barcli/... to verify red.

delta_summary:
  helper:diff-snapshot=5 files changed, 48 insertions(+), 1 deletion(-)
  - internal/barcli/build.go: added ReferenceKey string json:"reference_key,omitempty" to
    BuildResult; set ReferenceKey: s.grammar.ReferenceKey in result literal.
  - internal/barcli/shuffle.go: added result.ReferenceKey = g.ReferenceKey after Build() call,
    before PlainText rendering (so render uses the populated value).
  - internal/barcli/render.go: replaced direct referenceKeyText with refKey := result.ReferenceKey;
    fallback to referenceKeyText when empty (backward compat for cached builds pre-ADR-0131).
  - internal/barcli/build_test.go: added TestBuildResultCarriesReferenceKey specifying validation.
  - internal/barcli/render_test.go: added TestRenderPlainTextUsesResultReferenceKey specifying validation.
  Depth-first rung: ADR-0131 §3-5 (build + shuffle + render) → complete.

loops_remaining_forecast:
  0 loops remaining (all ADR-0131 behaviours landed green).
  ADR-0131 is complete: all 5 implementation items done, all specifying validations green.

residual_constraints:
  - referenceKeyText constant lingers in render.go as fallback for cached builds pre-ADR-0131
    — severity: Low; mitigation: future cleanup when state schema version is bumped (per ADR-0131
    §Tradeoffs); monitoring: no active risk; owning ADR: 0131 §Tradeoffs.
  - test grammar at cmd/bar/testdata/grammar.json lacks reference_key — severity: Low;
    TestBuildResultCarriesReferenceKey uses embedded grammar instead; monitoring: if test grammar
    is ever regenerated, it will gain the field automatically; owning ADR: 0131.

next_work:
  ADR-0131 complete. No further loops required.
  Cleanup opportunity (future): remove referenceKeyText constant and fallback when state schema
    version is bumped; this is deferred per ADR-0131 §Tradeoffs.
```

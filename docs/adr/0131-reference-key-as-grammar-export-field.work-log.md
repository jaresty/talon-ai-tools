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

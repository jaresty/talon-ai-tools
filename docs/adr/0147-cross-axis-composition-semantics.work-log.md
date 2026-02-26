# ADR-0147 Work Log

---

## Loop 4 — 2026-02-26 | Phase 3b: renderCrossAxisComposition in help_llm.go

```yaml
helper_version: helper:v20251223.1
focus: ADR-0147 Phase 3b — add renderCrossAxisComposition(w, grammar) to help_llm.go; fix CrossAxisPair.Reframe→Cautionary in grammar.go; wire into renderTokenSelectionHeuristics

active_constraint: >
  bar help llm does not render a "Choosing Channel" section; CROSS_AXIS_COMPOSITION data is loaded
  in grammar but not surfaced to LLM users. Additionally CrossAxisPair.Reframe JSON tag was "reframe"
  (old name) but grammar JSON now uses "cautionary" key — cautionary data silently missing at runtime.
  Validated by: /tmp/bar-new help llm | grep "Choosing Channel" → exit 1 (not found)

validation_targets:
  - go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep -c "Choosing Channel"  # must be ≥1
  - go test ./...  # must pass (0 failures); TestLLMHelpHeuristicsTokensExist must pass

evidence:
  - red    | 2026-02-26 | exit 1 | /tmp/bar-new help llm | grep "Choosing Channel" → not found | inline
  - green  | 2026-02-26 | exit 0 | help llm now contains Choosing Channel section with natural+cautionary per channel token | inline
  - green  | 2026-02-26 | exit 0 | go test ./... 0 failures; TestLLMHelpHeuristicsTokensExist passes | inline
  - removal | 2026-02-26 | exit 1 | git stash && go build; grep "Choosing Channel" → not found; git stash pop | inline

rollback_plan: git restore --source=HEAD internal/barcli/grammar.go internal/barcli/help_llm.go

delta_summary: |
  helper:diff-snapshot — 2 files changed, 91 insertions(+), 5 deletions(-)
  internal/barcli/grammar.go: CrossAxisPair.Reframe→Cautionary (json:"reframe"→json:"cautionary");
    updated struct comment and accessor comment
  internal/barcli/help_llm.go: added renderCrossAxisComposition(w, grammar) — iterates over
    grammar.Axes.CrossAxisComposition in stable order (channel before form, tokens sorted alpha),
    renders natural lists and cautionary bullets per token; audience tokens use audience=token form
    to pass TestLLMHelpHeuristicsTokensExist; form tokens labeled with "(form)" qualifier not
    in backticks; wired call at end of renderTokenSelectionHeuristics
  Bug fixed: CrossAxisPair.Reframe used json:"reframe" but Python pivot renamed key to "cautionary" —
    cautionary data was loaded as nil silently; now correctly reads cautionary warnings

loops_remaining_forecast: 1 loop (Phase 4 ADR-0085 validation); medium confidence

residual_constraints:
  - id: R2-prose-duplication
    description: AXIS_KEY_TO_GUIDANCE prose still contains cross-axis notes overlapping CROSS_AXIS_COMPOSITION
    severity: Low
    mitigation: Deferred to Phase 5 audit
    monitoring_trigger: Phase 5 bar split audit
  - id: R3-coverage-incomplete
    description: Many channel+task pairs not yet listed; unlisted pairs fall back to universal rule
    severity: Low
    mitigation: ADR-0085 shuffle cycles additive
    monitoring_trigger: Next meta-analysis
  - id: R4-reframe-quality-empirical
    description: Universal rule quality for shellscript+sim, code+sim empirically unknown
    severity: Medium
    mitigation: Phase 4 ADR-0085 validation (seeds 531, 560, 588, 615)
    monitoring_trigger: Phase 4 shuffle re-run

next_work:
  - Behaviour: Phase 4 — ADR-0085 validation; re-run seeds 531, 560, 588, 615; evaluate score improvement
    validation: bar build shellscript sim --subject "..." (seed 531) | score manually; update process-feedback.md
```

---

## Loop 3 — 2026-02-26 | Phase 3a: Reference Key universal rule (metaPromptConfig.py)

```yaml
helper_version: helper:v20251223.1
focus: ADR-0147 Phase 3a — extend Channel bullet + Precedence bullet in PROMPT_REFERENCE_KEY with universal task-as-content-lens rule

active_constraint: >
  PROMPT_REFERENCE_KEY Channel bullet says "delivery context: platform formatting conventions only" with no
  task-as-lens rule; Precedence section only covers specification channels (gherkin, codetour, adr).
  LLM has no first-principles rule for executable/delivery channels (shellscript, code, presenterm) at
  execution time. Validated by: /tmp/bar-new build make struct --subject x | grep -A1 "Channel 経路" | grep "task becomes"
  → exit 1 (not found)

validation_targets:
  - go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new build make struct --subject x | grep -A1 "Channel 経路" | grep "task becomes"  # must exit 0
  - /tmp/bar-new build make struct --subject x | grep "all channels"  # must exit 0
  - go test ./...  # must pass (0 failures)

evidence:
  - red    | 2026-02-26 | exit 1 | /tmp/bar-new build make struct --subject x | grep -A1 "Channel 経路" | grep "task becomes" → not found | inline
  - red    | 2026-02-26 | exit 1 | /tmp/bar-new build make struct --subject x | grep "all channels" → not found | inline
  - green  | 2026-02-26 | exit 0 | Channel bullet now contains "task becomes a content lens"; Precedence bullet now says "all channels: executable...specification...delivery" | inline
  - green  | 2026-02-26 | exit 0 | go test ./... passes 0 failures | inline
  - removal | 2026-02-26 | exit 1 | git stash && go build -o /tmp/bar-new; grep check → not found; git stash pop | inline

rollback_plan: git restore --source=HEAD lib/metaPromptConfig.py && make bar-grammar-update

delta_summary: |
  helper:diff-snapshot — 6 files changed
  lib/metaPromptConfig.py: Channel bullet extended with task-as-lens rule; Precedence bullet
    universalized from specification-only to all channels (executable, specification, delivery);
    existing probe+gherkin / diff+codetour examples preserved under specification channel clause
  build/prompt-grammar.json + internal/barcli/embed/prompt-grammar.json + cmd/bar/testdata/grammar.json
    + web/static/prompt-grammar.json: regenerated — includes both Phase 3a reference_key update and
    pivot-commit reframe→cautionary changes that were missing from those files
  Note: cmd/bar/testdata/grammar.json and web/static/prompt-grammar.json were omitted from the prior
    pivot commit; this loop regeneration corrects the omission

loops_remaining_forecast: 2 loops (Phase 3b help_llm Choosing Channel, Phase 4 ADR-0085 validation); medium confidence

residual_constraints:
  - id: R2-prose-duplication
    description: AXIS_KEY_TO_GUIDANCE prose still contains cross-axis notes overlapping CROSS_AXIS_COMPOSITION
    severity: Low
    mitigation: Deferred to Phase 5 audit
    monitoring_trigger: Phase 5 bar split audit
  - id: R3-coverage-incomplete
    description: Many channel+task pairs not yet listed; unlisted pairs fall back to universal rule
    severity: Low
    mitigation: ADR-0085 shuffle cycles additive
    monitoring_trigger: Next meta-analysis
  - id: R4-reframe-quality-empirical
    description: Universal reframe quality for shellscript+sim, code+sim is empirically unknown
    severity: Medium
    mitigation: Phase 4 ADR-0085 validation (seeds 531, 560, 588, 615)
    monitoring_trigger: Phase 4 shuffle re-run

next_work:
  - Behaviour: Phase 3b — renderCrossAxisComposition in help_llm.go; fix TestLLMHelpHeuristicsTokensExist persona token issue
    validation: go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep -c "Choosing Channel"  # must be ≥1 && go test ./...
```

---

## Loop 2 — 2026-02-25 | Phase 2: Grammar export

```yaml
helper_version: helper:v20251223.1
focus: ADR-0147 Phase 2 — export CROSS_AXIS_COMPOSITION through axisCatalog→promptGrammar→grammar.go into prompt-grammar.json

active_constraint: >
  cross_axis_composition key absent from build/prompt-grammar.json["axes"]; KeyError on access.
  Validated by: python3 -c "import json; d=json.load(open('build/prompt-grammar.json')); d['axes']['cross_axis_composition']['channel']['shellscript']['task']"

validation_targets:
  - python3 -c "import json; d=json.load(open('build/prompt-grammar.json')); c=d['axes']['cross_axis_composition']['channel']['shellscript']['task']; assert 'natural' in c and 'reframe' in c; print('PASS')"
  - go test ./...  # must pass (0 failures)

evidence:
  - red   | 2026-02-25 | exit 1 | KeyError: 'cross_axis_composition' in grammar JSON | inline
  - green | 2026-02-25 | exit 0 | grammar JSON contains cross_axis_composition with correct structure; go test ./... passes | inline

rollback_plan: git restore --source=HEAD lib/promptGrammar.py internal/barcli/grammar.go && make bar-grammar-update

delta_summary: |
  helper:diff-snapshot — 4 files changed (promptGrammar.py, grammar.go, prompt-grammar.json x2, tui_smoke.json)
  lib/promptGrammar.py: added cross_axis_composition passthrough from catalog to axis section JSON
  internal/barcli/grammar.go: CrossAxisPair struct; CrossAxisComposition field (3-level map) in AxisSection + rawAxisSection; wired in LoadGrammar; CrossAxisCompositionFor() accessor
  Note: initial rawAxisSection type was 2-level (bug); corrected to 3-level during loop

loops_remaining_forecast: 2 loops (Phase 3 help_llm rendering, Phase 4 validation); medium confidence

residual_constraints:
  - id: R2-prose-duplication
    description: AXIS_KEY_TO_GUIDANCE prose still contains cross-axis notes overlapping CROSS_AXIS_COMPOSITION
    severity: Low
    mitigation: Deferred to Phase 5 audit
    monitoring_trigger: Phase 5 bar split audit
  - id: R3-coverage-incomplete
    description: Many channel+task pairs not yet listed
    severity: Low
    mitigation: ADR-0085 shuffle cycles additive
    monitoring_trigger: Next meta-analysis

next_work:
  - Behaviour: Phase 3 — renderCrossAxisComposition in help_llm.go
    validation: go build -o /tmp/bar-new ./cmd/bar/main.go && /tmp/bar-new help llm | grep -c "Choosing Channel"  # must be ≥1
```

---

## Loop 1 — 2026-02-25 | Phase 1: CROSS_AXIS_COMPOSITION data structure

```yaml
helper_version: helper:v20251223.1
focus: ADR-0147 Phase 1 — add CROSS_AXIS_COMPOSITION dict + helper function + catalog wiring + generate_axis_config.py update

active_constraint: >
  CROSS_AXIS_COMPOSITION does not exist in lib/axisConfig.py; importing it raises ImportError.
  Validated by: python3 -c "from lib.axisConfig import CROSS_AXIS_COMPOSITION, get_cross_axis_composition; ..."

validation_targets:
  - python3 -c "from lib.axisConfig import CROSS_AXIS_COMPOSITION, get_cross_axis_composition; sc=get_cross_axis_composition('channel','shellscript'); assert 'task' in sc and 'natural' in sc['task'] and 'reframe' in sc['task']; print('PASS')"
  - python3 -c "from lib.axisCatalog import serialize_axis_config; p=serialize_axis_config(); assert 'channel' in p['cross_axis_composition']; print('PASS')"
  - python3 scripts/tools/generate_axis_config.py | grep -c 'CROSS_AXIS_COMPOSITION'  # must be ≥2

evidence:
  - red  | 2026-02-25 | exit 1 | ImportError: cannot import name 'CROSS_AXIS_COMPOSITION' from 'lib.axisConfig' | inline
  - green | 2026-02-25 | exit 0 | all three validation commands pass | inline
  - removal | 2026-02-25 | exit 1 | git restore --source=HEAD lib/axisConfig.py && python3 import check → ImportError returns | inline

rollback_plan: git restore --source=HEAD lib/axisConfig.py lib/axisCatalog.py scripts/tools/generate_axis_config.py

delta_summary: |
  helper:diff-snapshot — 3 files changed
  lib/axisConfig.py: added Any to typing import, appended CROSS_AXIS_COMPOSITION dict (6 channels, 1 form) + get_cross_axis_composition() helper
  lib/axisCatalog.py: added cross_axis_composition key to axis_catalog() + serialize_axis_config()
  scripts/tools/generate_axis_config.py: added Any to header import, cross_axis_body extraction, CROSS_AXIS_COMPOSITION block in output, get_cross_axis_composition helper in helpers string

loops_remaining_forecast: 3 loops (Phase 2 grammar export, Phase 3 help_llm rendering, Phase 4 validation); medium confidence

residual_constraints:
  - id: R2-prose-duplication
    description: AXIS_KEY_TO_GUIDANCE prose for shellscript/code/adr/etc still contains cross-axis avoidance notes that overlap with CROSS_AXIS_COMPOSITION
    severity: Low
    mitigation: Deferred to Phase 5 audit per ADR-0147 Phase 1 step 4
    monitoring_trigger: Phase 5 bar split audit
  - id: R3-coverage-incomplete
    description: Many channel+task combinations not yet listed; unlisted pairs have no reframe guidance
    severity: Low (additive dict; no regression)
    mitigation: ADR-0085 shuffle cycles will surface new entries as needed
    monitoring_trigger: Next ADR-0085 meta-analysis

next_work:
  - Behaviour: Phase 2 — grammar export (CROSS_AXIS_COMPOSITION → prompt-grammar.json)
    validation: make bar-grammar-update && python3 -c "import json; d=json.load(open('build/prompt-grammar.json')); c=d['axes']['cross_axis_composition']['channel']['shellscript']['task']; assert 'natural' in c and 'reframe' in c; print('PASS')"
```

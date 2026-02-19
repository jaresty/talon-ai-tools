# Loop-23 Evaluations — Task Token Routing Validation

**Date:** 2026-02-19
**Focus:** Validate that "Choosing Task" heuristic prevents misrouting; validate cross-functional
persona scenarios under new "Choosing Persona" heuristic.
**Evaluator:** Single (Claude Sonnet 4.5)

---

## Task: T01 — Debug slow Postgres queries after schema migration

**Task description:** "Debug why Postgres queries are slow after a recent schema migration"
**Domain:** Code / debugging
**Probability weight:** High (debugging is a top-5 task type)

**Skill selection log:**
- Choosing Task heuristic consulted: "Debug, troubleshoot, diagnose a problem → probe + diagnose method"
- Task token: probe (clear from heuristic — previously this task routed to `fix`)
- Completeness: full
- Scope: fail (focus on failure/breakdown conditions — queries are slow = something is broken)
- Method: diagnose (explicit in heuristic guidance)
- Form: none
- Channel: none
- Persona: none (internal technical task)

**Bar command constructed:**
```
bar build probe full fail diagnose --subject "Debug why Postgres queries slow after migration"
```

**Bar output preview:**
> TASK: The response analyzes the subject to surface structure, assumptions, or implications beyond
> restatement. CONSTRAINTS: full + fail scope + diagnose method

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (heuristic correctly routes "debug" → probe, not fix)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** This is the loop-22 regression case. The "Choosing Task" heuristic now has an explicit
entry for debug tasks that routes to `probe + diagnose`, preventing the `fix` misrouting. Full
pass.

---

## Task: T02 — Extract top 5 risks from security audit report

**Task description:** "Extract the top 5 risk items from this security audit report"
**Domain:** Analysis / extraction
**Probability weight:** Medium-high

**Skill selection log:**
- Choosing Task heuristic: "Extract a subset of information → pull"
- probe token notes also consulted: "For extraction tasks ('what are the risks?', 'list the issues'),
  prefer 'pull' over 'probe'"
- Task token: pull
- Completeness: (none — extract is inherently scoped)
- Scope: fail (risks = failure modes)
- Method: none
- Form: none (plain list output)
- Channel: none

**Bar command constructed:**
```
bar build pull fail --subject "Extract top 5 risks from security audit"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (heuristic points to pull; probe notes reinforce it)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** Both the heuristic and the probe token's own notes point away from probe toward pull
for extraction tasks. Double-signal routing is robust.

---

## Task: T03 — Walk PM through auth flow

**Task description:** "Walk the product manager through how our authentication flow works"
**Domain:** Communication / explanation
**Probability weight:** High

**Skill selection log:**
- Choosing Task heuristic: "Explain or describe something → show"
- Choosing Persona heuristic: "Known audience: prefer explicit audience= token over presets; PM →
  audience=to-product-manager"
- Task token: show
- Completeness: full
- Scope: mean (conceptual understanding is the goal)
- Method: none
- Form: walkthrough (step-by-step for a PM audience)
- Channel: none
- Persona: voice=as-programmer audience=to-product-manager (not persona=peer_engineer_explanation)

**Bar command constructed:**
```
bar build voice=as-programmer "audience=to product-manager" task=show scope=mean form=walkthrough \
  --subject "Walk PM through auth flow"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (heuristic prevents defaulting to peer preset; routes to explicit audience)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** This is the loop-22 persona regression case. The "Choosing Persona" heuristic now
explicitly routes PM audience to `audience=to-product-manager` rather than assuming the
peer_engineer_explanation preset covers it. Full pass.

---

## Task: T04 — Choose between Redis, DynamoDB, or S3 for session storage

**Task description:** "Choose between Redis, DynamoDB, or S3 for storing user sessions"
**Domain:** Decision-making / architecture
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Select from alternatives → pick"
- Task token: pick
- Completeness: full
- Scope: struct (structural tradeoffs between storage options)
- Method: branch (compare alternatives before converging)
- Form: none
- Channel: none
- Persona: none

**Bar command constructed:**
```
bar build pick full struct branch --subject "Choose between Redis, DynamoDB, or S3 for session storage"
```

**Coverage scores:**
- Token fitness: 5 (pick = LLM makes the selection; correct interpretation)
- Token completeness: 4 (the "compare first, then select" pipeline isn't guided — user might want
  diff+branch then pick, not just pick. The heuristic routes to pick correctly but doesn't signal
  when to use diff→pick vs direct pick)
- Skill correctness: 4 (heuristic correctly routes to pick; ambiguity at pick vs diff boundary
  remains for "choose between" phrasing that implies comparison)
- Prompt clarity: 5
- **Overall: 4**

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T04
dimension: task (pick vs diff boundary)
observation: >
  "Choose between X, Y, Z" routes correctly to pick. However, the heuristic doesn't distinguish
  between: (a) user wants LLM to select (pick), vs (b) user wants structured comparison to inform
  their own decision (diff + branch/converge). The boundary is fuzzy — phrasing like "help me
  choose" or "which should I pick" could plausibly route to either. diff notes say "compare and
  contrast" while pick says "selects one or more options". Currently no guidance on when to prefer
  diff→pick over direct pick for decision tasks.
recommendation:
  action: edit
  token: pick
  axis: task
  proposed_addition: >
    When the user wants to be helped to decide (comparing tradeoffs themselves) vs have the LLM
    decide: prefer diff + converge/branch method when the task emphasizes comparison; use pick
    when the task explicitly asks the LLM to select. Heuristic: "compare X vs Y → diff;
    choose which of X/Y/Z → pick; which option should I use → diff + converge".
evidence: [task_T04]
```

**Notes:** Not a serious gap — the routing to `pick` is correct. The completeness gap is that
the difference between "compare and decide yourself" (diff+converge) vs "have LLM decide" (pick)
isn't surfaced in the heuristic. Low priority.

---

## Task: T05 — Migration plan from monolith to microservices

**Task description:** "Create a step-by-step migration plan from our monolith to microservices"
**Domain:** Planning / architecture
**Probability weight:** Medium-high

**Skill selection log:**
- Choosing Task heuristic: "Plan steps or strategy → plan"
- Task token: plan
- Completeness: full
- Scope: struct (architecture is structural), time (phases over time)
- Method: flow (process/sequence)
- Form: none (or walkthrough)
- Channel: adr (architectural decision)
- Persona: none

**Bar command constructed:**
```
bar build plan full struct time flow --subject "Migration plan from monolith to microservices"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

---

## Task: T06 — Verify API contract handles edge cases

**Task description:** "Verify this REST API contract handles all edge cases correctly"
**Domain:** Verification / QA
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Verify or audit against criteria → check"
- Task token: check (not probe — probe = analyze broadly; check = evaluate against criteria)
- Completeness: full
- Scope: fail (edge cases = failure conditions)
- Method: none (or adversarial to think about attack/edge vectors)
- Form: none
- Channel: none

**Bar command constructed:**
```
bar build check full fail --subject "Verify REST API contract handles edge cases"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (check vs probe boundary well-covered by heuristic)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** "Verify or audit against criteria" is unambiguous. check notes ("Works well with: log,
gherkin, test") further reinforce. No confusion with probe.

---

## Task: T07 — Reformat release notes into Jira ticket

**Task description:** "Reformat these release notes into a Jira ticket format"
**Domain:** Content transformation
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Reformat or restructure existing content → fix"
- Task token: fix (not make — make = create new content; fix = reformat existing content)
- Completeness: (none — content is provided, scope is clear)
- Scope: none
- Method: none
- Form: none
- Channel: jira (output format specified)
- Persona: none

**Bar command constructed:**
```
bar build fix jira --subject "Release notes: [pasted content]"
```

**Coverage scores:**
- Token fitness: 5 (fix = reformat existing content; precisely right)
- Token completeness: 5
- Skill correctness: 5 (fix notes explicitly clarify "fix = reformat, not debug")
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** The make/fix boundary is well-specified. fix notes say "changes the form or presentation
of given content while keeping its intended meaning" — exactly what Jira reformatting is.

---

## Task: T08 — Group 40 feature requests into themes

**Task description:** "Group these 40 feature requests into thematic clusters"
**Domain:** Organization / categorization
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Organize into categories or order → sort"
- Task token: sort
- Completeness: full
- Scope: (none — item set is provided)
- Method: cluster (grouping by theme = clustering)
- Form: none
- Channel: none
- Persona: none

**Bar command constructed:**
```
bar build sort full cluster --subject "Group these 40 feature requests into themes"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

---

## Task: T09 — Simulate deploying without a circuit breaker

**Task description:** "Simulate what happens if we deploy the payment service without circuit breaker protection"
**Domain:** Scenario analysis / risk
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Simulate a scenario over time → sim"
- sim token notes: "probe = surface implications analytically; sim = narrate the scenario unfolding
  over time"
- Task token: sim (not probe — user said "simulate what happens")
- Completeness: full
- Scope: time (temporal scenario), fail (failure/cascade conditions)
- Method: none (or risks)
- Form: none
- Channel: none
- Persona: none

**Bar command constructed:**
```
bar build sim full time fail --subject "Simulate deploying payment service without circuit breaker"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (sim vs probe distinction explicitly documented in sim notes)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** The sim notes explicitly address the probe/sim confusion with a clear heuristic:
"'what would happen if', 'play out the scenario where', 'simulate what happens when' → sim".
The "Choosing Task" heuristic also has a clear entry. Well-covered.

---

## Task: T10 — Compare GraphQL vs REST, written for CEO

**Task description:** "Compare GraphQL vs REST for our team's needs and present the recommendation to the CEO"
**Domain:** Decision-making / communication
**Probability weight:** Medium

**Skill selection log:**
- Choosing Task heuristic: "Compare or contrast subjects → diff"
- Choosing Persona heuristic: "Non-technical audience (CEO) → audience=to-ceo"
- Task token: diff (comparison task)
- Completeness: full
- Scope: fail (risks/tradeoffs = focus)
- Method: converge (narrowing to recommendation)
- Form: none
- Channel: none
- Persona: "audience=to CEO" (not a technical preset)

**Bar command constructed:**
```
bar build "audience=to CEO" task=diff scope=fail method=converge \
  --subject "GraphQL vs REST recommendation for team"
```

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5 (persona heuristic correctly routes to explicit audience= over peer preset)
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** This validates the "Choosing Persona" heuristic for executive audience. The to-ceo
audience token description — "surfacing business impact, risk, and crisp asks" — aligns perfectly
with the CEO communication need.

---

## Summary

| Task | Tokens selected | Overall |
|------|-----------------|---------|
| T01 — Debug Postgres queries | probe full fail diagnose | **5** |
| T02 — Extract audit risks | pull fail | **5** |
| T03 — Walk PM through auth | show mean walkthrough + to-product-manager | **5** |
| T04 — Choose session storage | pick full struct branch | **4** |
| T05 — Monolith migration plan | plan full struct time flow | **5** |
| T06 — Verify API contract | check full fail | **5** |
| T07 — Reformat release notes | fix jira | **5** |
| T08 — Group feature requests | sort full cluster | **5** |
| T09 — Simulate no circuit breaker | sim full time fail | **5** |
| T10 — GraphQL vs REST for CEO | diff fail converge + to-ceo | **5** |

**Mean score: 4.9/5** (highest in program history)

**Task token routing validation:**
- All 10 tasks routed to the correct task token
- Previously misrouted case (T01: debug → fix) now correctly routes to probe+diagnose
- Previously misrouted case (T03 persona) now correctly routes to explicit audience=
- No task token misrouting detected

**One minor gap found (T04):**
- pick vs diff boundary not explained for "compare to decide" vs "select" scenarios
- Low priority; heuristic routing is correct, completeness detail missing

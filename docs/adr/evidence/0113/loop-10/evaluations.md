# ADR-0113 Loop-10 Evaluations — Output Channel Discoverability

**Date:** 2026-02-17
**Binary:** /tmp/bar-new (built from source, commit a539dd6)
**Focus:** Channel token selection

---

## T183 — Write an ADR for choosing PostgreSQL over MongoDB

**Task description:** "Write an Architecture Decision Record for choosing PostgreSQL over MongoDB for our user data storage"
**Domain:** Documentation

**Skill selection log:**
- Task: make (creating an artifact)
- Completeness: full
- Scope: diff + thing (comparison of two options)
- Method: (none needed — comparing concrete choices)
- Form: case (decision-oriented structure)
- Channel: **adr** — user says "ADR" explicitly; Token Catalog `adr` description matches
- Directional: (none)

**Bar command:** `bar build make diff thing full case adr`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** "ADR" is self-naming. The `adr` channel is visible in the Token Catalog and the user's
explicit mention makes this a trivial match. No discoverability issue.

---

## T184 — Create a Presenterm slide deck for architecture review

**Task description:** "Create a Presenterm slide deck summarizing our microservices architecture for the engineering all-hands"
**Domain:** Presentation

**Skill selection log:**
- Task: make
- Completeness: full
- Scope: struct (architectural structure)
- Method: (none)
- Form: (none — channel defines format)
- Channel: **presenterm** — user mentions "Presenterm" by name
- Directional: (none)

**Bar command:** `bar build make struct full presenterm`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** Presenterm is a named tool. Users who know it say "Presenterm slide deck" directly.
No discoverability gap when explicitly named.

---

## T185 — Write a shell script to bootstrap dev environment

**Task description:** "Write a shell script that bootstraps our development environment: installs dependencies, sets up environment variables, and runs database migrations"
**Domain:** Code tooling

**Skill selection log:**
- Task: make
- Completeness: full
- Scope: act (action-focused steps)
- Method: (none)
- Form: (none)
- Channel: **shellscript** — "shell script" is explicit; description says "shell script output format"
- Directional: (none)

**Bar command:** `bar build make act full shellscript`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** "Shell script" is explicit enough. The `shellscript` channel name maps directly.

---

## T186 — Write Gherkin acceptance criteria for payment flow

**Task description:** "Write Gherkin acceptance criteria for our payment processing flow, covering happy path and edge cases"
**Domain:** Specification

**Skill selection log:**
- Task: **make** or **check**? User says "write" → make. But Gherkin is behavior specification (check domain). Guidance says `gherkin` best for `check, plan, or make when defining system behavior`. Task is creating new criteria → make.
- Completeness: full
- Scope: fail (edge cases → failure/boundary scope)
- Method: (none)
- Form: (none)
- Channel: **gherkin** — user says "Gherkin" explicitly
- Directional: (none)

**Bar command:** `bar build make fail full gherkin`

**Coverage scores:**
- Token fitness: 4 (channel correct; task token "make" is right but some autopilots might pick "check")
- Token completeness: 5
- Skill correctness: 4 (make vs check ambiguity; `gherkin` Notes say "best for check, plan, or make")
- Prompt clarity: 4
- **Overall: 4**

**Gap diagnosis:** minor — make vs check ambiguity for "write Gherkin criteria" task phrasing.
No new channel discoverability gap; the `gherkin` Notes already document this.

**Notes:** Channel discovery is fine. Minor task-token uncertainty (create vs. evaluate Gherkin).

---

## T187 — Format documentation for Jira

**Task description:** "Format this architecture overview documentation page for Jira, using appropriate Jira markup"
**Domain:** Documentation

**Skill selection log:**
- Task: fix (reformatting existing content)
- Completeness: (none — short reformatting task)
- Scope: (none)
- Method: (none)
- Form: (none)
- Channel: **jira** — user says "Jira markup" explicitly
- Directional: (none)

**Bar command:** `bar build fix jira`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** "Jira markup" is self-naming. Channel discovery is not a problem here.

---

## T188 — Create a session plan for design sprint kickoff

**Task description:** "Create a session plan for tomorrow's design sprint kickoff — 3 hours with the team, covering context, problem framing, and ideation exercises"
**Domain:** Collaboration / facilitation

**Skill selection log:**
- Task: plan (planning output) or make (creating artifact)?
- Scope: act (action steps)
- Method: (none — plan task covers this)
- Form: **facilitate**? autopilot might pick facilitate for "session plan"
- Channel: **sync** — should be selected. But is there any heuristic?
  - `sync` Token Catalog: "synchronous or live session plan (agenda, steps, cues)"
  - User says "session plan" — word-for-word match with `sync` description
  - But: no usage pattern for `sync` in bar help llm. Autopilot is likely to pick
    `plan` task + `facilitate` form without selecting `sync` channel at all.
  - `facilitate` form also says "facilitation plan" — autopilot will likely pick this
    over `sync` channel since form is more prominent in skill guidance.

**Bar command (autopilot likely):** `bar build plan act full facilitate`
**Bar command (ideal):** `bar build plan act full facilitate sync`

**Coverage scores:**
- Token fitness: 3 (form+task correct but sync channel missed, losing session-plan shaping)
- Token completeness: 3 (sync channel not selected → response lacks agenda/timing/cue structure)
- Skill correctness: 3 (no usage pattern to route sync; facilitate picked over sync+facilitate)
- Prompt clarity: 3 (without sync, output is facilitation plan but not session-plan formatted)
- **Overall: 3**

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T188 — Create session plan for design sprint kickoff
dimension: channel
observation: >
  `sync` channel (synchronous or live session plan with agenda, steps, cues) is
  not selected by autopilot for "session plan" tasks. No usage pattern exists
  for sync in bar help llm. Autopilot routes to `plan` task + `facilitate` form,
  which covers facilitation but not the channel-level session-plan shaping.
  The word match ("session plan" in user request vs "session plan" in sync description)
  would help, but agents routing by usage patterns won't find it.
recommendation:
  action: add-usage-pattern
  channel: sync
  proposed_pattern: "bar build plan act full sync"
  proposed_heuristic: >
    "session plan", "live workshop agenda", "meeting plan with timing cues",
    "real-time facilitation script" → add sync channel.
    Combine with facilitate form when facilitator role is explicit.
  also: add use_when to AXIS_KEY_TO_USE_WHEN["channel"]["sync"]
evidence: [task_T188]
```

---

## T189 — Create a D2 diagram of microservices architecture

**Task description:** "Create a D2 diagram showing the relationships and dependencies between our microservices"
**Domain:** Visual output

**Skill selection log:**
- Task: make (creating a diagram artifact)
- Completeness: full
- Scope: struct (structural relationships)
- Method: depends (dependency mapping)
- Form: (none)
- Channel: user says "D2 diagram" → should be **sketch** (D2 source) not **diagram** (Mermaid)
  - `sketch` Token Catalog: "emits only pure D2 diagram source"
  - `diagram` Token Catalog: "converts to Mermaid diagram code"
  - User says "D2" explicitly — if autopilot reads Token Catalog carefully, it finds `sketch`
  - But: no usage pattern for `sketch`. Autopilot might default to `diagram` (well-known Mermaid)
  - The word "diagram" in the user request maps to `diagram` token name, pulling away from `sketch`

**Bar command (autopilot likely):** `bar build make struct full depends diagram`
**Bar command (ideal):** `bar build make struct full depends sketch`

**Coverage scores:**
- Token fitness: 3 (wrong channel selected — Mermaid vs D2)
- Token completeness: 4 (all other axes correct)
- Skill correctness: 3 (autopilot likely picks `diagram` over `sketch` due to name salience)
- Prompt clarity: 3 (output would generate Mermaid, not D2)
- **Overall: 3**

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T189 — Create D2 diagram of microservices
dimension: channel
observation: >
  `sketch` channel (D2 diagram source) is invisible when user says "diagram".
  The word "diagram" maps to the `diagram` channel (Mermaid), pulling autopilot
  away from `sketch`. No heuristic distinguishes D2 from Mermaid in skill guidance.
  sketch description says "D2 diagram source" but there's no routing signal unless
  the user explicitly says "D2" or "sketch".
recommendation:
  action: add-use-when
  channel: sketch
  proposed_use_when: >
    D2 diagram output: when user explicitly requests D2 format or "sketch diagram".
    Heuristic: 'D2 diagram', 'D2 format', 'sketch diagram' → sketch.
    Distinct from diagram channel (Mermaid output).
evidence: [task_T189]
```

---

## T190 — Plain-prose explanation, no lists or bullets

**Task description:** "Give me a plain-prose explanation of our authentication and authorization model — no lists, no bullets, just flowing paragraphs"
**Domain:** Documentation / explanation

**Skill selection log:**
- Task: show (explaining something)
- Completeness: full
- Scope: mean (conceptual understanding)
- Method: (none)
- Form: (none)
- Channel: **plain** — user explicitly says "no lists, no bullets, just paragraphs" → matches `plain`
  - `plain` Token Catalog: "plain prose with natural paragraphs... no structural conventions
    such as bullets, tables, or code blocks"
  - Word-for-word match with user's request ("no lists, no bullets")
  - BUT: no usage pattern for `plain`. Autopilot might not add `plain` channel, since
    not adding a channel is the default (the model decides structure itself).
  - Without `plain` channel, autopilot would just use `show mean full` with no channel.
  - The prompt would produce good output, but the anti-decoration constraint is lost.

**Bar command (autopilot likely):** `bar build show mean full`
**Bar command (ideal):** `bar build show mean full plain`

**Coverage scores:**
- Token fitness: 3 (plain channel missed → no explicit prose-only constraint in prompt)
- Token completeness: 3 (user's explicit formatting preference not encoded)
- Skill correctness: 3 (no routing signal for "plain prose / no bullets" → plain channel)
- Prompt clarity: 3 (LLM may still use bullets without the `plain` channel constraint)
- **Overall: 3**

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T190 — Plain prose explanation, no lists
dimension: channel
observation: >
  `plain` channel (suppress structural formatting) is not selected when user
  explicitly requests "no lists, no bullets". Autopilot routes to `show` task
  without a channel, leaving formatting up to the LLM. The `plain` channel is
  invisible because: (a) no usage pattern exists for it in bar help llm, and
  (b) the default behavior when no channel is selected is often similar to plain
  prose anyway, so there's no urgency signal.
recommendation:
  action: add-usage-pattern
  channel: plain
  proposed_pattern: "bar build show <scope> full plain"
  proposed_heuristic: >
    "no lists", "no bullets", "no formatting", "plain prose", "continuous prose",
    "paragraph form", "flowing paragraphs" → add plain channel.
    Plain channel explicitly suppresses bullets, tables, and code blocks.
  also: add use_when to AXIS_KEY_TO_USE_WHEN["channel"]["plain"]
evidence: [task_T190]
```

---

## T191 — Generate an SVG icon for data flow

**Task description:** "Generate an SVG icon representing data flow between our microservices for use in our documentation"
**Domain:** Visual output

**Skill selection log:**
- Task: make
- Channel: **svg** — user says "SVG" explicitly
- Bar command: `bar build make svg`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 4 (scope might help — struct for architecture, thing for entity)
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none (minor: scope optional but not critical)

---

## T192 — Write a Slack message for v2.0 release

**Task description:** "Write a Slack message to the #engineering channel announcing our v2.0 release, including key features and any breaking changes"
**Domain:** Collaboration

**Skill selection log:**
- Task: make
- Completeness: (none — focused message)
- Scope: (none)
- Channel: **slack** — user says "Slack message" explicitly
- Bar command: `bar build make slack`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

---

## T193 — Plan a remote-delivery retrospective

**Task description:** "Help me plan a retrospective for our distributed engineering team — it needs to work well in a remote setting with people across timezones"
**Domain:** Collaboration / facilitation

**Skill selection log:**
- Task: plan or make (planning a session)
- Form: **facilitate** (planning a retrospective workshop)
- Form: wasinawa? (retrospective structure) — but wasinawa is for post-incident reflection, not workshop planning
- Channel: **remote** — user says "remote setting"
  - `remote` Token Catalog: "optimised for remote delivery, ensuring instructions work in
    distributed or online contexts and surfacing tooling or interaction hints suitable for
    video, voice, or screen sharing"
  - User says "remote setting" — meaning matches description
  - BUT: "remote" in user task means the team is distributed. Does autopilot map
    "remote-delivery" to the `remote` channel? The channel shapes the response for
    remote delivery, which is exactly what's needed here.
  - No usage pattern for `remote`. Autopilot will likely focus on the facilitation
    content and miss the delivery-optimization channel.

**Bar command (autopilot likely):** `bar build plan act full facilitate`
**Bar command (ideal):** `bar build plan act full facilitate remote`

**Coverage scores:**
- Token fitness: 3 (remote channel missed — no delivery-optimization hints in output)
- Token completeness: 3 (channel omission weakens the "works in remote setting" aspect)
- Skill correctness: 3 (no usage pattern routes "remote retrospective" to remote channel)
- Prompt clarity: 4 (response still useful; remote optimization is secondary)
- **Overall: 3**

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T193 — Remote-delivery retrospective planning
dimension: channel
observation: >
  `remote` channel (remote-delivery optimization) is not discovered when user
  describes a remote/distributed context. The channel is ambiguous: "remote"
  in user requests usually describes the team situation, not a format preference.
  No usage pattern exists. Autopilot focuses on the facilitation content and
  omits the remote-optimization channel.
recommendation:
  action: add-use-when
  channel: remote
  proposed_use_when: >
    Optimizing output for remote/distributed delivery contexts (video calls, screen sharing,
    async follow-up). Heuristic: 'remote setting', 'distributed team', 'video call',
    'screen sharing', 'async participants' → add remote channel.
    Distinct from the team being "remote" — this shapes HOW the response is delivered.
evidence: [task_T193]
```

---

## T194 — Show auth module as VS Code CodeTour

**Task description:** "Walk me through the authentication module as a VS Code CodeTour file for onboarding new engineers"
**Domain:** Code tooling

**Skill selection log:**
- Task: show (explaining/navigating code)
- Completeness: full
- Scope: flow (how it works end-to-end)
- Form: (none)
- Channel: **codetour** — user says "VS Code CodeTour" explicitly
  - `codetour` Token Catalog: "valid VS Code CodeTour .tour JSON file"
  - User explicitly names the tool

**Bar command:** `bar build show flow full codetour`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

**Notes:** "CodeTour" is explicit enough. The channel name maps directly.

---

## T195 — Write HTML documentation page for REST API

**Task description:** "Write an HTML documentation page for our REST API endpoints, with clean semantic markup"
**Domain:** Documentation

**Skill selection log:**
- Task: make
- Channel: **html** — user says "HTML" explicitly

**Bar command:** `bar build make html`

**Coverage scores:**
- Token fitness: 5
- Token completeness: 5
- Skill correctness: 5
- Prompt clarity: 5
- **Overall: 5**

**Gap diagnosis:** none

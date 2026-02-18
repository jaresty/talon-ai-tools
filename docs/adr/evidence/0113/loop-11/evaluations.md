# ADR-0113 Loop-11 Evaluations

**Date:** 2026-02-18
**Binary:** /tmp/bar-new (built from source)
**Focus:** Part A — Post-apply validation of loop-10 channel fixes (T188, T189, T190, T193)
           Part B — Completeness axis discoverability (T196–T200)

---

# Part A — Post-Apply Validation of Loop-10 Channel Fixes

Re-evaluating the 4 gapped tasks from loop-10 after adding `use_when` entries and usage
patterns for `plain`, `sync`, `sketch`, and `remote` channels.

Applied fixes verified in `lib/axisConfig.py` AXIS_KEY_TO_USE_WHEN["channel"]:
- `plain`: "no bullets", "no formatting", "plain prose", "flowing paragraphs" → plain channel
- `sync`: "session plan", "live workshop agenda", "meeting agenda with timing cues" → sync channel
- `sketch`: "D2 diagram", "D2 format", "sketch diagram", "d2 source" → sketch channel
- `remote`: "remote delivery", "distributed session", "video call context", "screen sharing" → remote channel

Usage patterns added to `help_llm.go`:
- "Plain Prose Output": `bar build show <scope> full plain`
- "Synchronous Session Plan": `bar build plan act full sync`

---

## T188 — Create a session plan for design sprint kickoff

**Task description:** "Create a session plan for tomorrow's design sprint kickoff — 3 hours with the team, covering context, problem framing, and ideation exercises"
**Domain:** Collaboration / facilitation
**Loop-10 score:** 3 (sync channel undiscoverable — no routing signal)

**Post-fix skill selection log:**
- Task: plan (planning output)
- Completeness: full
- Scope: act (action steps for the session)
- Method: (none)
- Form: facilitate (planning a session with structure and cues)
- Channel: **sync** — now discoverable via:
  - use_when heuristic: "session plan" → sync channel ✅
  - Usage pattern: "Synchronous Session Plan" → "bar build plan act full sync" ✅
  - Word "session plan" in user request directly matches the use_when trigger
- Directional: (none)

**Bar command (pre-fix likely):** `bar build plan act full facilitate`
**Bar command (post-fix):** `bar build plan act full facilitate sync`

**Coverage scores (post-fix):**
- Token fitness: 4 (sync adds agenda/timing/cue structure; form+task correct)
- Token completeness: 4 (all axes now covered; facilitate+sync combination is appropriate)
- Skill correctness: 5 (usage pattern + use_when provide strong routing signal for "session plan")
- Prompt clarity: 4 (sync channel shapes output as live session agenda; combined with facilitate, clear)
- **Overall: 4** ✅ (was 3, now ≥4)

**Fix verdict:** PASS — "session plan" trigger lands. The `sync` use_when heuristic
directly matches the task phrase. Usage pattern reinforces with example command.

---

## T189 — Create a D2 diagram of microservices architecture

**Task description:** "Create a D2 diagram showing the relationships and dependencies between our microservices"
**Domain:** Visual output
**Loop-10 score:** 3 (sketch channel confused with diagram/Mermaid — no routing signal)

**Post-fix skill selection log:**
- Task: make
- Completeness: full
- Scope: struct (structural relationships)
- Method: depends (dependency mapping)
- Form: (none)
- Channel: **sketch** — now discoverable via:
  - use_when heuristic: "D2 diagram" → sketch (distinct from diagram = Mermaid) ✅
  - Disambiguation now explicit: "if user says 'diagram' without D2 → diagram channel;
    if user says 'D2 diagram' → sketch channel" ✅
  - User says "D2 diagram" — word-for-word match with use_when trigger

**Bar command (pre-fix likely):** `bar build make struct full depends diagram`
**Bar command (post-fix):** `bar build make struct full depends sketch`

**Coverage scores (post-fix):**
- Token fitness: 4 (correct channel; D2 source produced; minor: "D2 diagram" phrasing needed)
- Token completeness: 4 (all axes covered)
- Skill correctness: 4 (use_when routes "D2 diagram" to sketch; disambiguation now documented)
- Prompt clarity: 4 (sketch channel produces D2 source; unambiguous)
- **Overall: 4** ✅ (was 3, now ≥4)

**Fix verdict:** PASS — "D2 diagram" trigger lands. User must say "D2" explicitly; if they
say just "diagram", routing to `diagram` (Mermaid) is correct. The disambiguation is now
documented in the use_when note.

---

## T190 — Plain-prose explanation, no lists or bullets

**Task description:** "Give me a plain-prose explanation of our authentication and authorization model — no lists, no bullets, just flowing paragraphs"
**Domain:** Documentation / explanation
**Loop-10 score:** 3 (plain channel undiscoverable — no routing signal; model ignores channel)

**Post-fix skill selection log:**
- Task: show (explaining something)
- Completeness: full
- Scope: mean (conceptual understanding)
- Method: (none)
- Form: (none)
- Channel: **plain** — now discoverable via:
  - use_when heuristic: "no bullets", "plain prose", "flowing paragraphs" → plain channel ✅
  - Usage pattern: "Plain Prose Output" → "bar build show <scope> full plain" ✅
  - User phrase "no lists, no bullets, just flowing paragraphs" — multiple exact heuristic matches

**Bar command (pre-fix likely):** `bar build show mean full`
**Bar command (post-fix):** `bar build show mean full plain`

**Coverage scores (post-fix):**
- Token fitness: 5 (plain channel explicitly suppresses structural decoration — exact match to user request)
- Token completeness: 5 (all important axes now covered; plain adds the explicit constraint)
- Skill correctness: 5 (usage pattern + use_when have "no bullets", "no lists", "flowing paragraphs" — all match user phrasing)
- Prompt clarity: 5 (plain channel instruction is unambiguous; suppresses bullets/tables/code)
- **Overall: 5** ✅ (was 3, now 5)

**Fix verdict:** PASS — strongest fix of the four. The user's phrasing ("no lists, no
bullets, just flowing paragraphs") hits three heuristic triggers simultaneously. This
is now the highest-confidence routing in the channel axis.

---

## T193 — Plan a remote-delivery retrospective

**Task description:** "Help me plan a retrospective for our distributed engineering team — it needs to work well in a remote setting with people across timezones"
**Domain:** Collaboration / facilitation
**Loop-10 score:** 3 (remote channel ambiguous — "remote" describes team context, not format)

**Post-fix skill selection log:**
- Task: plan (planning output)
- Completeness: full
- Scope: act (action steps)
- Method: (none)
- Form: facilitate (planning a retrospective workshop)
- Channel: **remote** — now partially discoverable via:
  - use_when heuristic: "distributed session" → matches "distributed engineering team" ✅
  - use_when note: "user saying their team is 'remote' describes context — use remote channel
    only when delivery optimization is the explicit goal" ⚠️
  - User phrase "needs to work well in a remote setting" IS a delivery goal statement → should trigger
  - But: "remote setting" as context description still risks being overlooked

**Bar command (pre-fix likely):** `bar build plan act full facilitate`
**Bar command (post-fix):** `bar build plan act full facilitate remote`

**Coverage scores (post-fix):**
- Token fitness: 4 (remote channel adds tooling hints for distributed/async contexts; needed here)
- Token completeness: 4 (channel now adds delivery-optimization dimension)
- Skill correctness: 3 (use_when is better — "distributed session" matches — but phrasing ambiguity
  persists; a careful autopilot picks it; a less careful one still treats "remote" as context only)
- Prompt clarity: 4 (when remote channel is selected, response includes video/screen-sharing hints)
- **Overall: 4** ✅ (was 3, now ≥4 — borderline improvement)

**Fix verdict:** BORDERLINE PASS — "distributed session" heuristic fires for "distributed
engineering team". The explicit delivery goal ("needs to work well in a remote setting")
provides the intent signal. Routing is better but not as strong as T188/T189/T190. A
second usage pattern for remote (e.g., "bar build plan act full facilitate remote") could
further strengthen this.

---

## Part A Summary

| Task | Channel | Pre-fix | Post-fix | Delta | Verdict |
|------|---------|---------|---------|-------|---------|
| T188 | sync | 3 | 4 | +1 | PASS |
| T189 | sketch | 3 | 4 | +1 | PASS |
| T190 | plain | 3 | 5 | +2 | PASS |
| T193 | remote | 3 | 4 | +1 | BORDERLINE PASS |

**Mean pre-fix:** 3.0 → **Mean post-fix:** 4.25 ✅ (target ≥4.0)

All 4 gapped tasks now score ≥4. Loop-10 fixes are confirmed to land.

---

# Part B — Completeness Axis Discoverability

**Question:** Does bar-autopilot select the right completeness token (gist, full, deep, max,
minimal, narrow, skim) for typical user task phrasings?

**Observation before evaluation:** Completeness tokens have no `use_when` entries in
AXIS_KEY_TO_USE_WHEN. Only `skim` has a note (about directional incompatibilities).
All routing must come from token descriptions alone.

---

## T196 — Quick overview of the authentication flow

**Task description:** "Give me a quick overview of how authentication works in our system"
**Domain:** Code / explanation
**Expected completeness:** `gist`

**Skill selection log:**
- Task: show (explaining)
- Completeness: **gist** — "short but complete answer or summary that touches the main points once"
  - "quick overview" maps to "short but complete summary" — reasonable description match
  - But: no heuristic / use_when entry for gist
  - Autopilot risk: defaults to `full` (safe default) rather than explicitly selecting `gist`
  - "quick" signal is moderate — some autopilots will pick gist, others skip completeness
- Scope: mean (conceptual understanding)
- Form: (none)

**Bar command (autopilot likely):** `bar build show mean full` (or `bar build show mean gist`)
**Bar command (ideal):** `bar build show mean gist`

**Coverage scores:**
- Token fitness: 3 (gist often NOT selected; "full" used as default when completeness unclear)
- Token completeness: 3 (key user constraint — "quick" — not captured without gist)
- Skill correctness: 3 (no heuristic routes "quick overview" to gist; autopilot may pick full)
- Prompt clarity: 3 (without gist, response may be more thorough than user wants)
- **Overall: 3** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T196 — Quick overview of authentication flow
dimension: completeness
observation: >
  `gist` completeness (brief but complete summary) is not reliably selected when
  user asks for a "quick overview". No use_when entry or heuristic connects
  "quick", "overview", "brief summary", or "tldr" to the gist token. Autopilot
  defaults to full (safe choice) or omits completeness. The gist description is
  accurate but not heuristic-linked.
recommendation:
  action: add-use-when
  axis: completeness
  token: gist
  proposed_use_when: >
    User wants a brief, complete answer: 'quick summary', 'overview', 'brief',
    'tldr', 'just the main points', 'high-level'. Heuristic: 'quick', 'brief
    summary', 'overview', 'just the gist', 'tldr' → gist. Distinct from skim
    (light pass only) and full (thorough).
evidence: [task_T196]
```

---

## T197 — Exhaustive documentation of all API endpoints

**Task description:** "Write exhaustive documentation for all our API endpoints — cover every parameter, error code, and edge case"
**Domain:** Documentation
**Expected completeness:** `max`

**Skill selection log:**
- Task: make (creating documentation)
- Completeness: **max** — "as exhaustive as reasonable, covering essentially everything relevant"
  - "exhaustive" appears word-for-word in user request AND in max description
  - Self-describing: if autopilot reads "exhaustive" → max description says "exhaustive"
  - Strong routing signal from description alone

**Bar command:** `bar build make act full max` → or `bar build make act max`
**Bar command (ideal):** `bar build make act max`

**Coverage scores:**
- Token fitness: 5 (max matches "exhaustive" exactly; description is a word-for-word match)
- Token completeness: 5 (max is the right token; user intent fully captured)
- Skill correctness: 4 (description match is strong; no use_when needed; slight risk of full as default)
- Prompt clarity: 4 (max instructs "treat omissions as errors" — exactly right for exhaustive docs)
- **Overall: 4** ✅

**Gap diagnosis:** none — `max` is described as "exhaustive" and user says "exhaustive".
The description-to-phrase match is strong enough without a use_when.

---

## T198 — Minimal change to fix this bug

**Task description:** "Make the smallest possible change to fix this authentication bug — don't refactor anything, just fix the immediate issue"
**Domain:** Code / bug fix
**Expected completeness:** `minimal`

**Skill selection log:**
- Task: fix or make (fixing a bug)
- Completeness: **minimal** — "smallest change or provides the smallest answer that satisfies the request"
  - "smallest possible change" in user request matches "smallest change" in minimal description
  - Token name itself is "minimal" — semi-self-naming
  - "don't refactor anything, just fix the immediate issue" reinforces minimal intent

**Bar command:** `bar build fix minimal` or `bar build make minimal`
**Bar command (ideal):** `bar build fix minimal`

**Coverage scores:**
- Token fitness: 5 (minimal perfectly captures "smallest possible change" constraint)
- Token completeness: 5 (user's intent encoded exactly)
- Skill correctness: 4 (description match strong; minimal is semi-self-naming; slight autopilot variation)
- Prompt clarity: 5 (minimal instructs "smallest change that satisfies the request" — precise)
- **Overall: 4** ✅

**Gap diagnosis:** none — `minimal` is sufficiently self-describing for "smallest change" phrasings.

---

## T199 — Deep dive into the caching layer

**Task description:** "Give me a deep dive into how our Redis caching layer works — I want to understand the implementation in detail, including edge cases and failure modes"
**Domain:** Code / analysis
**Expected completeness:** `deep`

**Skill selection log:**
- Task: probe (surfacing implications) or show (explaining)
- Completeness: **deep** — "substantial depth within the chosen scope, unpacking reasoning layers"
  - "deep dive" in user request is idiomatic for `deep`
  - Token name "deep" + user phrase "deep dive" = near-self-naming
  - "understand the implementation in detail" reinforces depth intent

**Bar command:** `bar build probe fail mean full deep` or `bar build show struct deep`
**Bar command (ideal):** `bar build probe fail mean deep`

**Coverage scores:**
- Token fitness: 5 (deep matches "deep dive" exactly; name + description both signal)
- Token completeness: 5 (user intent for depth captured)
- Skill correctness: 5 (deep is near-self-naming; "deep dive" → deep is idiomatic)
- Prompt clarity: 5 (deep adds reasoning-layer depth instruction)
- **Overall: 5** ✅

**Gap diagnosis:** none — `deep` is self-naming for "deep dive" phrasings.

---

## T200 — High-level summary for the weekly standup

**Task description:** "Give me a high-level summary of what changed this sprint — I'll share it at the standup, keep it very brief"
**Domain:** Communication / summary
**Expected completeness:** `skim` or `gist`

**Skill selection log:**
- Task: pull (extracting a summary) or show
- Completeness: **gist** or **skim** — which?
  - `gist`: "short but complete answer that touches the main points once"
  - `skim`: "very light pass, addressing only the most obvious or critical issues"
  - User says "high-level" and "very brief" — both fit gist and skim
  - Standup context → gist (complete picture) or skim (light pass)?
  - Neither has a routing heuristic. Autopilot might pick either, or default to full.
  - Risk: "keep it very brief" doesn't clearly distinguish gist vs skim.
  - Autopilot may pick `gist` (more common, better described for summaries) OR default to `full`

**Bar command (autopilot likely):** `bar build pull mean full` (full is the safe default)
**Bar command (ideal):** `bar build pull mean gist`

**Coverage scores:**
- Token fitness: 2 (gist vs skim ambiguity; autopilot likely defaults to full, missing the brevity intent)
- Token completeness: 2 (user's "very brief" constraint not encoded without explicit completeness token)
- Skill correctness: 2 (no heuristic routes "high-level summary", "standup", "very brief" to gist or skim)
- Prompt clarity: 3 (full produces a thorough response; user wanted brief)
- **Overall: 2** ⚠️

**Gap diagnosis:**
```yaml
gap_type: undiscoverable-token
task: T200 — High-level summary for standup
dimension: completeness
observation: >
  Neither `gist` ("short but complete") nor `skim` ("light pass, obvious issues
  only") is reliably selected for "high-level", "very brief", or "standup"
  contexts. Autopilot defaults to `full` as the safe choice. No use_when entry
  exists for either token. The gist/skim distinction itself is not obvious to
  autopilot — they are described differently but both applicable to "brief"
  tasks. For standup summaries, gist is better (complete picture, just concise),
  but skim is also defensible. Without heuristics, the selection is unreliable.
recommendation:
  action: add-use-when
  axis: completeness
  token: gist
  proposed_use_when: >
    Brief but complete response needed: 'quick summary', 'high-level overview',
    'standup update', 'tldr', 'main points only', 'brief but complete'.
    Heuristic: 'overview', 'brief', 'just the key points', 'standup', 'tldr' → gist.
    Prefer gist over skim when completeness matters; prefer skim when the user
    wants a light pass over a subset (review context).
  also:
  - add use_when for skim: 'light review', 'just check for obvious issues',
    'quick pass', 'surface-level look' → skim
evidence: [task_T200, task_T196]
```

---

## Part B Summary

| Task | Expected Token | Autopilot Selection | Score | Notes |
|------|----------------|---------------------|-------|-------|
| T196 | gist | full (default) | 3 | No use_when; "quick" doesn't reliably route |
| T197 | max | max | 4 | "exhaustive" is word-for-word in description |
| T198 | minimal | minimal | 4 | Near-self-naming for "smallest change" |
| T199 | deep | deep | 5 | Self-naming; "deep dive" → deep |
| T200 | gist/skim | full (default) | 2 | "brief" ambiguous; autopilot defaults to full |

**Mean score (Part B):** 3.6/5 — below the 4.0 target

**Fully discoverable:** `max` (description match), `minimal` (semi-self-naming), `deep` (self-naming)
**Undiscoverable:** `gist` (no heuristic for "quick/brief/overview"), `skim` (no heuristic for "light pass/review")
**Never tested:** `narrow` — appears to have no natural task phrasings that clearly route to it

---

## Gaps Found (Part B)

### G-L11-01 — gist: No routing heuristic for "brief/quick/overview" requests
**Gap type:** undiscoverable-token
**Severity:** High — "quick overview" and "brief summary" are very common request phrasings;
autopilot defaults to `full` which produces over-thorough responses
**Fix:** Add use_when for `gist` — "quick", "brief", "overview", "tldr", "main points", "standup" → gist

### G-L11-02 — skim: No routing heuristic for "light pass/quick review" requests
**Gap type:** undiscoverable-token
**Severity:** Medium — "skim" is less common than gist but serves a distinct use case
(surface review vs. brief completeness)
**Fix:** Add use_when for `skim` — "light review", "quick pass", "just obvious issues",
"surface-level look", "spot check" → skim

### G-L11-03 — narrow: Completely invisible — no known task phrasing routes to it
**Gap type:** undiscoverable-token
**Severity:** Low — `narrow` is a valid token but has no idiomatic trigger phrase;
users would need to know it exists to use it
**Fix (optional):** Add use_when — "just X and nothing else", "only about Y", "restricted
to Z", "specifically" → narrow

# ADR-0241: bar token catalog — design-system audit and recommended fixes

Status: proposed
Date: 2026-11-08

## Context

The `design-system` sequence (`lib/sequenceConfig.py`: probe motifs induce → make ontology dimension
reify → make axiom → check snag) was run inline over the bar token catalog in
`build/prompt-grammar.json`: 258 tokens on 7 axes (topology 6, completeness 14, scope 19, method 117,
form 54, channel 32, directional 16), 11 tasks, persona, 57 compositions, 27 sequences. The steps
were measured with scripts rather than executed through `bar build`; counts below are from that run.

## Findings

### Motifs
- Every definition opens "The response ..." with a fixed verb per axis (scope "focuses on", method
  "enhances the task" in 73/117, directional "additionally orients").
- 242 of 258 tokens declare `distinctions` ("X = ...; Y = ..."): 560 directed edges. The first draft
  said 257/258; that was a miscount found when the A2 validator ran. Fifteen tokens have none: channel
  adr, code, codetour, gherkin, html, jira, notebook, plain, remote, shellscript, slack, svg; form
  dialogue, wardley; method own. `jog` is the null directional and is exempt. Densest
  cross-axis seams: method<->scope 21, form<->method 13, completeness<->method 6.
- Heavy tokens carry procedure (negative clauses, named markers). Length varies from ~100 characters
  to `ground` 31.6 KB, `falsify` 15.6 KB, `shoshin` 12.5 KB, `hollow` 7.3 KB, `quiz` 6.7 KB.
- Compositions: 28 channel x form, 14 method x method, 15 other; none involve three tokens.

### Ontology
Primitives and the dimension each owns: task (verb), topology (reasoning visibility), completeness
(extent), scope (subject focus), method (procedure), form (output organization), channel (delivery),
directional (orientation), persona (register). Token names are globally unique across axes.
`directional` flattens two dimensions: its 16 tokens are vertical {none, fog, dig, fig} x
horizontal {none, rog, ong, bog}, with `jog` the null cell.

### Axioms (derived; enforcement not verified)
- A1 token names belong to exactly one axis (holds).
- A2 every token states a distinction against its nearest neighbour (violated by 15 tokens; `jog` exempt).
- A3 singleton axes take one value; soft caps scope 2, method 5, form 1, channel 3, directional 1.
- A4 conflicts resolve by priority topology > completeness > scope > method > form > channel.
- A5 same-axis conflicts are enforced through `hierarchy.axis_incompatibilities`; cross-axis conflicts are
  advisory and live in `cross_axis_composition`. Each kind has exactly one home.
- A6 a composition adds only what neither token says alone.

### Snags
- A5 (corrected): `hierarchy.axis_incompatibilities` is empty for every axis, but it is a live
  enforcement hook, not a duplicate store. `lib/talonSettings.py` uses it for last-wins eviction in
  `_canonicalise_axis_tokens`; `internal/barcli/help_llm.go` renders it under "Grammar-enforced
  restrictions" and already says cross-axis incompatibilities are advisory; `web/src/lib/incompatibilities.ts`
  consumes it. It is same-axis only, so it cannot hold the cross-axis entries. The first draft of this
  ADR called it a violation; that was wrong.
- Declared two-owner concepts: method<->scope (adversarial/fail, assume/gap/unknowns,
  authority/actors/control, bound/dam, flow/time, mapping/struct); form doing method's work
  (ontology/gloss, coupling/snag, argue/ibis/case, gate/runbook); completeness doing method's work
  (minimal/prune, narrow/redact, grow/lazy, zoom/ladder/navigate); form<->channel (axiom/formal,
  chart/diagram, plain/tight, snap/ledger/store).
- A6 violated: `ground+falsify` (~7 KB) restates Gate 1-3 and the `§ ground complete` marker.
- 289 of 560 distinctions are one-directional.
- Undeclared near-duplicates: html~svg (0.57 similarity); adversarial~unknowns (0.41).
- Eight distinctions target task names, not tokens (compare->check, sense->check, winnow->pick, ...).
- Method x topology has three declared seams (ground/live, pin/witness, falsify/audit) although
  topology constrains every method.
- Hierarchy omits directional from the priority order and persona entirely; topology and
  completeness have no soft cap.

## Decision (proposed fixes, in order)

1. Keep `hierarchy.axis_incompatibilities`; do not delete it. Document the division (same-axis
   enforced, cross-axis advisory) where the catalog describes the hierarchy. Deleting it would touch
   Python, Go and the web SPA, plus their tests, to remove a hook that is empty by design.
2. Declare the missing seams: html/svg first, then adversarial/unknowns. Check each with the
   duplication discriminator from ADR-0085.
3. Mirror the 289 one-way distinctions, or record in the guidebook that one-way is intentional.
   Prefer a generated check over hand edits.
4. Do not slim `ground+falsify`. Corrected after measuring: the composition (11.6 KB, not ~7 KB) does
   not restate the definitions (0 of 75 sentences overlap a definition by more than 30%). It holds the
   adequacy seam (the property<->assertion bijection, distinguishing-state construction, the
   `Adequacy:` / `Audit:` / `Coverage:` verdicts), which exists only when both tokens are active. That
   is where the orthogonality protocol and falsify design laws 5 and 7 (nn `20260816151723-4445`) put it.
   The real work on these three texts is separate and already planned: the falsify domain-agnostic
   rewrite (`20260817012812-4903`, "not yet an implementation", blocked on the cross-model eval that
   note says to run before mutating falsify), restoring `ground`'s epistemic opener (`20260719224020-0703`),
   and the deny-list rewrites below. Measured: "does not satisfy" ground 9, falsify 4, composition 6;
   software vocabulary per KB ground 2.0, falsify 8.5, composition 6.4 (domain-agnostic protocol
   `20260716164822-9216`).
5. Model directional as two axes (vertical, horizontal) in the grammar, keeping the 16 spoken
   tokens as aliases so existing usage does not break.
6. Add a catalog test that enforces A1 and A2, and that no cross-axis pair is registered in
   `axis_incompatibilities` (A5), so the audit does not need rerunning by hand.

## Progress (2026-11-08)

- A2 closed: distinctions authored for the 15 tokens, each stated from both sides (24 pairs); two
  existing notes (`tight`->`plain`, `demo`->`shellscript`) restated affirmatively; `dialogue` gained a
  metadata entry and heuristics. `validate_token_names_unique_across_axes` and
  `validate_distinctions_present` run in `axis-catalog-validate.py`; the A5 same-axis check is a unit
  test because reading the hierarchy imports `lib.talonSettings`, which the CLI cannot always load.
- Small fixes: `jog` label and routing concept now state the null orientation ("No directional push",
  "No compass push") instead of "Execute intent directly, no clarification", which contradicted its
  definition; `adversarial`/`unknowns` declare each other; `validate_directional_compounds_name_their_parts`
  checks that each of the 9 compounds plus `fig` and `bog` states distinctions against exactly its two
  components, which is the only record that the flat compound tokens are built from two parts.
- Decided not to split `directional`; the compound check above is the mitigation.
- Soft caps: `topology` and `completeness` added to `_AXIS_SOFT_CAPS` (both 1). They were already
  single-valued (`bar build` rejects a second token on either), but through hardcoded checks the table
  never saw; the earlier note here that a missing cap "means no cap" was wrong. TUI and web already
  defaulted a missing cap to 1, so only Python's `_canonicalise_axis_tokens` changed behavior (it now
  keeps the latest token, as it already did for form and directional).
- Channel cap made consistent: multi-channel was intended (`8ee51840`, "allow multiple channel
  tokens"), which raised the table to 3 and removed Go's single-channel check, but Go never enforced
  the cap and accepted four channels. `bar build` now enforces the table's channel cap on the shorthand
  path (`channel supports at most 3 tokens`), and the `bar help llm --compact` caps line is generated
  from the table instead of the hardcoded "others 0-1". `TestSoftCapTableMatchesBuild` runs every axis
  in the table through `bar build` at cap and cap+1, so the table cannot drift from build again.
- Voice surface vs `bar build`: the Talon grammar is deliberately narrower. The `modelPrompt` capture
  rule has scope x2, method x3, form x1, channel x1 and directional x1 slots, so strings saying
  "method <= 3" and "channel=1" are correct for spoken commands; the readme's one-channel claim is
  verified. What was inconsistent was that those limits lived only as scattered literals (the replay
  clamps `[-2:]`, `[-3:]`, `[-1:]`) and that the help canvas showed `bar build`'s caps (method 5,
  channel 3), which cannot be spoken. `_VOICE_AXIS_SLOTS` in `lib/talonSettings.py` now names them once,
  `_tests/test_voice_axis_slots.py` checks the constant against the capture rule, and the replay clamp
  and help canvas use it. `_AXIS_SOFT_CAPS` remains the limit for `bar build`. Left as literals
  (correct for voice, not worth the churn): `lib/helpHub.py:556`, `GPT/gpt.py:521`, readme method line.
- Correction: two "override oddities" reported earlier were misdiagnoses. `channel=a,b` is compare
  mode (ADR-0161, one prompt per variant), and the "channel accepts a single token" error on repeated
  `channel=` keys came from an installed `bar` that predates the multi-channel commit; a fresh build
  accepts up to the cap. The installed binary needs `make bar-install`.
- Reciprocity: 258 one-way token-to-token distinctions mirrored (so 609 -> 867 directed edges).
  240 are mechanical clause-order flips of the existing note, so no content was invented; 18 were
  written by hand because the original had three clauses, an `axis:` prefix, or one clause only
  (e.g. `chain` -> `gate`, `fail` -> `adversarial`, the three `shoshin` pairs). `validate_distinctions_reciprocal`
  now enforces it. Exempt by design: distinctions against a task (8, tasks have no distinction metadata
  here) and directional compound -> part edges (22), which the compound check already derives from
  the token name. 41 of the mirrored notes carry negation wording that was already in the original
  ("without", "no", "not"); they were mirrored verbatim, not reworded, and belong to the deny-list
  follow-up below as distinction text, not definition text.
- Not done: `directional` absent from `axis_priority` and persona absent from the hierarchy, and the
  deny-list rewrites below.

## Follow-up: deny-list phrasing in definitions

Token definitions should state what the output contains, not what it must not do (nn
`20260513141540-7254`, prior art for `blind` and `solo`). Measured on the catalog: the phrase
"does not satisfy" appears in 18 definitions (about 35 occurrences): all six topology tokens, scope
`jobs`, method `eliminate`, `falsify` (4), `gate`, `ground` (9), `mark`, `own`, `prism` (3), `redact`,
`shoshin` (2), form `quiz`, channel `zettel` (2). Many other tokens use other negations; those are
not yet classified. Each rewrite is a token-rewrite sequence run (definition rewrites), so this is its
own piece of work. Open question to settle first: some closing clauses were added deliberately to
close escape routes found by hollow audits, so each needs an allow-list restatement that keeps the
observable requirement.


### Progress: topology six done (2026-11-08)

Ran the token-rewrite sequence on `audit`, `blind`, `live`, `relay`, `solo` and `witness`. In all six the
closing "does not satisfy this requirement" sentence was the contrapositive of the universal sentence
before it, so removing it loses no observable requirement and closes two clashes (`blind`: the closer's
trigger "when prior context is in play" differed from the opening's "section that uses ... context";
`audit`: claim/conclusion). `solo`'s "includes an intermediate step only when ..." was restated
affirmatively as "The response names, in the opening sentence of each intermediate step it includes, ...".
`_tests/test_topology_definitions.py` pins both and checks each definition keeps its observable anchors.
Behavioral check: three isolated haiku agents applied `audit`, `solo` and `relay` to three diverse
subjects (nn integration receipt `20261109012420-8107`, partially adopted). It shows the new text is
followable; it has no baseline against the old text, so it does not show the closers were needed or not.

Findings deferred from that run, now resolved (2026-11-08, receipt `20261109013042-4389`):
- `live`: the clash between "precedes or accompanies each paragraph" and "appears within the same
  paragraph" is resolved to the finalized intent in nn `20260515162048-8287` ("preceded or accompanied
  ... in the same segment"): the observation line sits within the paragraph, before or alongside the
  content. The original wording read as outside the paragraph.
- `solo`: "Output depth is governed by the completeness token independently" named another token
  (orthogonality protocol `20260715194839-8169`); now "Depth of coverage is set independently of this
  requirement."
- `relay`: earlier described here as satisfiable nominally. More precisely, the first agent's verdict was
  wrong (it counted a heading mention as defining two of the five categories); the definition required
  all five. Added "each appear under their own label" so presence is a literal check; a fresh agent
  produced five labeled sections, all before the dependent section.
  `_tests/test_topology_definitions.py` pins all three. Behavioral checks are one haiku run per token
  on one subject each with no baseline against the old text.
### Progress: batch 1 of the remaining closers (2026-11-08)

`own`, `redact` and `mark` rewritten (receipt `20261109013729-2303`; `_tests/test_deny_list_definitions.py`
holds a `CLEARED` table later batches extend). `redact` and `mark` were redundant or anti-escape closers
and became affirmative statements ("Every named category is absent from the rewritten output";
"protocol requirements, gate conditions, and artifact preconditions are each satisfied by their own named
artifacts"). `own` is the cautionary case: I deleted its closer as redundant, and a haiku agent then passed
every recommendation by treating "uploading" as "creating a new artifact". A baseline run of the original
definition reasoned about single-step sharing and avoided synced directories; my first affirmative
replacement ("suffices to share an artifact that already exists") did not reproduce that, and a third
form that states the test ("An artifact is accessible to others when a single transmission step could
share it.") did. Lesson for the remaining batches: a closer that is the contrapositive of the preceding
sentence can go; one that adds a decision rule must be restated as the rule, and checked against a
baseline run of the original, not only against the new text. Limits: one subject per token, haiku only;
`mark`'s anti-escape clause was not exercised (no gate in the subject); the `own` check reads "single
transmission" mostly as automatic sync.
### Progress: batch 2 (2026-11-08)

`eliminate`, `jobs` and `quiz` rewritten (receipt `20261109014331-9692`), each tested as original versus
rewrite on the same subject, eight agent runs in all. `eliminate`: both versions met every requirement
with consistent counts, so its closer was redundant and is gone. `jobs`: no behavioral difference between
versions (the agent partitioned the response between `jobs` and `product` either way); the closer named a
sibling scope's domain ("a specific product ... is about the product"), which `product` plus `jobs`
permits to contradict, so it is removed on the principle in nn `20261009190642`, and the boundary already
lives in the two `jobs`/`product` distinctions. `quiz`: the closer is a decision rule, so it was kept as a
test, in its minimal form "A Predict: line satisfies the gate when it appears in a human message turn."
My first rewording ("comes from the reader ... records no reader expectation") made a haiku agent rule
FAIL on the same model-written placeholder line that the original passed, so it was rejected; the
original passed on two runs and the minimal form on one. That minimal-form run wrote two questions where
the originals wrote one: treated as variance, not checked further. Replacing a value by regex failed on
`quiz` (adjacent string literals), so the edit used the `ast` module's source positions.
### Progress: batch 3 (2026-11-08)

`gate` and `prism` (receipt `20261109015020-4404`). `gate`: dropped "a gate condition block from a prior
action does not satisfy this requirement for a subsequent action"; with and without it each governed
action got its own block, and the clause is implied by "each governed action requires its own gate
condition block". `prism`: two of its three closers are gone (frame headings and block counts, which every
rewrite run still met). The third stays: "a frame body that enumerates alternative approaches, methods,
or investigation paths does not satisfy this requirement". Original runs (2) wrote descriptive frames;
every run of three rewordings (5 runs: a definition, "its body works from that one vantage point", and
"describes the subject as seen from that vantage point in statements about the subject") wrote frame
bodies that list things to evaluate, and each agent reported PASS on its own list. Here the prohibition
carried the behavior at this model size, so `_tests/test_deny_list_definitions.py` records it in
`ALLOWED_DENY_SENTENCES` (one allowed occurrence, with the evidence).

Across the three batches: a closer that restates the preceding sentence can go (topology six, redact,
eliminate, gate, prism's first and third); one that adds a decision rule must be restated as a rule and
checked against a baseline of the original (`own` took three wordings, `quiz` two); and `prism`'s is the
one so far no affirmative wording reproduced. All of this is haiku on one or two subjects per token.

Follow-up on `prism` (receipt `20261109015555-9917`): a `bar build probe hollow` audit of the four
frame-body wordings explained the result. By `hollow`'s own criterion a governing clause must name a
string or structure that is present in a compliant transcript and absent in a non-compliant one, and a
deny-list clause must be converted to an allow-list condition naming that observable. The stance
wordings ("works from that one vantage point", "a vantage point is one place from which the subject is
viewed") are concept-description clauses and bind nothing; "describes the subject ... in statements
about the subject" is borderline; the original deny sentence is invalid by `hollow` but names a concrete
failure the model can match. The observable that separates a descriptive frame from a list of advice is
the sentence opening: descriptive sentences open with a noun phrase naming part of the subject, the lists
agents wrote open with verbs ("Evaluate", "Assess", "Consider") or question words. Wording E, "each
sentence in its body opens with a noun phrase naming part of the subject and states a property of that
part as seen from that vantage point", produced 0 verb or question openings over 73 frame-body
sentences (extracted from the retained responses, not the agents' self-checks) on two advice-style
subjects, and replaces the deny sentence; `prism` now has no "does not satisfy" and
`ALLOWED_DENY_SENTENCES` is empty. Caveat: E is stricter than the original, which only barred lists of
approaches; frame bodies are now declarative statements about parts of the subject, so `prism` output
reads as descriptive facts, not advice. Open question: is that the intended use of a vantage-point frame.
Method note: this suggests the rule for the rest, that a decision-rule closer converts only when the
rewrite names something visible in the response's own text (a sentence opening, a literal string, an
operational test like `own`'s single transmission step), not a stance.

Correction to the `prism` follow-up above (receipt `20261109020538-9050`): the sentence-opening rule
(wording E) was the wrong target. It enforced the grammar of sentences inside each frame and nothing
about what `prism` is for. The catalog's heuristics ("think about this as a regulator, then as a user,
then as an engineer", "force structurally different restatements") and distinctions ("complementary
frames ... surface what each independently reveals") describe cognitive frames, and so does the
reference the owner supplied: a schema that simplifies and organizes information, supplies background
understanding that is never stated, and makes the same information read differently (the framing
effect). Under E and under the original, every run produced topic areas (Technical, Financial, Team,
Risk; Economic, Environmental, Mobility, Social) with no frame construing the subject differently,
nothing unstated, and no shared facts read two ways. `prism` now requires, per frame block, `Construal:`
(what the subject is taken to be), `Presupposes:` (background supplied unstated) and one `Reads fact K:`
line per shared fact in a numbered list stated once in the enumeration artifact, with at least one fact
read differently by every frame. Four runs on two subjects: construals differ in kind, readings of the
same fact differ (word overlap of readings 0.25 or less; on the pollution fact one frame reads
"the direct primary benefit" and another "secondary to the economic cost"), and `Presupposes:` carried
real assumptions. The E baseline on the city subject gave four topic areas with no readings. Limits:
haiku only, two subjects; city-subject labels still sound like topics, and what makes them frames is
the construals and readings; frames lack the `Foregrounds:`/`Backgrounds:` lines and any decision
implication, left out on purpose. The `spur`/`prism` and `shoshin`/`prism` distinction notes now say
"cognitive frames". The sentence-opening wording and its caveat above are superseded.

Tightening of the cognitive-frame wording (receipt `20261109021150-5445`): the owner asked whether the
frames were cognitive. In the first cognitive-frame sample the `Construal:` lines mostly said what the
question was about ("The question concerns competitive advantage ..."), and `Presupposes:` gave beliefs, not
the roles and sequence a frame supplies (the "restaurant" frame brings menus, waitstaff, ordering, paying).
`Construal:` now must begin "The subject is taken to be" and name a kind of thing or problem, and
`Presupposes:` must name the roles present under the frame, what each expects, and what normally happens
next. Four runs on two subjects: `Presupposes:` gave roles, expectations and a "Normally, ..." sequence in
three of four runs (it gave beliefs in none of the four before), often with a success criterion; the
readings of shared facts were unchanged (20 `Reads` lines per run, word overlap 0.20 or less between
frames); `Construal:` moved from "the question concerns X" to problem schemas ("a logistical
optimization problem for moving people and goods through constrained urban space", "a binding-constraint
capability challenge"). Still open: construals name problem types, not what the subject is; none wrote
"a commons" or "a conduit", so the commons-versus-corridor kind of schema still appears only inside a
`Reads` line; one database run fell back to noun lists in `Presupposes:`.

`gate` self-echo loophole (receipt `20261109023307-4462`, attempted and left unchanged): in both first
`gate` runs each agent satisfied its gate by `echo`-ing the exact string it then named in the gate block,
so a gate can be met by text the agent just produced. Two provenance wordings were tried: (1) the string
"must first occur in the transcript inside a qualifying result block — output the response did not itself
write —", and (2) the result must be "produced by a command whose text is free of that string". Neither
changed behavior. Measured from the raw retained events by pairing each result with its producing command:
the original arm echoed in one run and used `date`/`pwd` output in the other; wording 2 produced 0 of 4
compliant gate strings in the two runs of the loophole task (one run echoed, one named a string that appears
in no result at all); wording 1 echoed again in the run I could score. The honest case (a script that prints
its own pass line, then run) passes under the original and under both wordings, because the command that
runs the script does not contain the line, so the worry that the stricter rule would reject honest use did
not materialize. Conclusion: at this model size a provenance clause does not stop the cheapest compliance;
a mechanical check (a hook comparing each gate string with the commands before it) would, and is a
different piece of work. `gate` is unchanged.
### Progress: zettel (2026-11-08)

`zettel` (receipt `20261109021722-9653`) lost both closers: "A single body carrying more than one of the
composite's parts does not satisfy the one-claim rule, and a note set with no entry note ... does not
preserve what the composite conveyed", and "a response where the ID appears only in prose does not satisfy
this requirement". Tested original versus rewrite, two runs each, with a stub `nn` that logs every
command and returns fake IDs, so no real notes were written (`zbin/nn` in the session scratchpad); judged from
the command logs. All four runs made six notes (an entry note plus five single-claim notes) and ran
`nn suggest-links` on IDs the stub returned. The only run that did not follow each `nn new` with its own
`suggest-links` was an original run. n=2 per arm, one subject, haiku only.

Gap found, then fixed (receipt `20261109022742-0670`): only one of four runs linked the entry note to the
claim notes; the other three bulk-linked each note to the stub's single suggestion, because the definition says
the entry note "links them" but its step list gave no command or observable for that link. `zettel` now
ends with "For a composite, after the last note: (5) run `nn bulk-link` once more with the entry note's ID
and every claim note's ID as literal arguments." Two runs through the stub: six notes each, every
`suggest-links` on a returned ID, and one `bulk-link` carrying all six created IDs (was 1 of 4 before).
### Progress: shoshin (2026-11-08)

`shoshin` (receipt `20261109022133-7451`) had both occurrences in its last sentence, which had three clauses:
(a) an eligible response with no disposition lines "has not established that its frame set was chosen rather
than inherited"; (b) a delegation block with no disposition lines at an earlier position "does not satisfy
this token"; (c) a delegation block with no `Forwarded:` line at an earlier position does not, "since the
items ... were not audited for inherited framing". (b) restates sentence 11 (a delegation block must appear
at a later transcript position than the disposition lines it enforces) and (c) restates sentence 37 (every
item entering an isolated context is `Forwarded:`-audited, each line at an earlier position than the block).
(a) is different: sentences 1 and 3 give only one direction ("invoke it only where ...", and a response in
which no point meets the trigger "emits no invocations and is compliant"); the converse, that a response in
which a point does meet the trigger must invoke, appeared only in (a). The sentence is replaced by that
converse stated affirmatively: "A response in which a point meets the trigger emits an invocation whose
disposition lines establish that its frame set was chosen rather than inherited." Tested original versus
rewrite on a subject where the trigger is met ("Is a hot dog a sandwich?") and one where it is not ("What is
17 times 3?"), in-thread only: both arms invoked on the first with all five parts (Trigger, Pool and sort,
Reason, Reconcile, Leak) and 4 to 5 disposition lines, both declined on the second with zero disposition
lines, and no run called an Agent or Task tool. n=1 per arm per subject, haiku only; the delegation clauses
(b) and (c) were not exercised since they restate earlier sentences.

Verification gap found after the pass (2026-11-08): `tests/` (run by CI with `pytest tests/`, separate from
`_tests/`) pinned wording this pass removed on purpose and was never run during it. Three assertions failed:
`tests/test_gate_definition.py` required "a gate condition block from a prior action does not satisfy"
(removed with `gate`'s closer), and `tests/test_prism_definition.py` required the old single-vantage-point
clause and the approach prohibition (replaced by the cognitive-frame design). They now pin the current
text: "each governed action requires its own gate condition block", and for `prism` the cognitive-frame
clause, the `Construal:`/`Presupposes:`/`Reads fact K:` lines and the differing-reading requirement.
The CI set is `pytest _tests/`, `pytest tests/`, `go test ./...`, `cd web && npm test`,
`make axis-import-guard`, `make ci-guardrails`, the grammar regeneration sync check and pyright; all pass
now except pyright's existing errors (65 at the start of the pass, 61 now; two this pass had added in
`GPT/gpt.py` and the reciprocity validator were fixed). Rule for repeating a definition pass: run the
whole CI set, not only the suites the edited files are known to touch.

Summary of the deny-list pass: 16 definitions lost every "does not satisfy" sentence, `prism` was redesigned
around cognitive frames instead, and `own`, `quiz` and `shoshin`'s (a) clause kept their rule in affirmative
form. Remaining: `falsify` (4 occurrences) and `ground` (9), blocked on their design notes
(`20260817012812-4903`, the cross-model eval, and `20260719224020-0703`).

## Consequences

- Fixes 1-3 are data-only and low risk. Fix 4 touches the largest definitions and needs the
  craft-pack evals rerun. Fix 5 changes grammar shape and the generated artifacts
  (`prompt-grammar.json` copies), so it should be its own ADR.
- Any edit to a token description or composition entry is governed by the bar token protocols.

## Not checked

Whether the tool enforces A3/A4 at build time; whether one-way distinctions were deliberate;
per-token behaviour of the heavy definitions.

### prism `Construal:` — wording J adopted

The `Construal:` clause now requires a sentence whose grammatical subject is the subject's own noun phrase (copied from the subject or the shared facts) and whose predicate names a kind of thing the subject is taken to be. Measured over 16 construals: 6 name a kind of thing, against 0 of 16 before (city 5 of 8, database 1 of 8).

Open escape hatches, not closed by this wording:
- one database run copied the whole question as the "subject" ("How should a small team decide … is a problem of …");
- some database lines were not "is a" statements ("is constrained by …", "must align with …").

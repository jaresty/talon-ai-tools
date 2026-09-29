# Cycle 27 — Phase 2e Distinction Check

Rule (cycles 24-26): **composition** when a coherent output satisfies both tokens, including two
coexisting artifacts. **Cautionary** only when honoring one structurally starves the other.
Above both (cycle 25-26): first check whether a token is **mis-describing itself** — the fix may
be the classification, not the pairing.

## codetour + pick → CAUTIONARY (extends the shipped codetour+sort entry)

Mis-description check first: is `pick` or `codetour` mis-described? No. pick = "selecting from
alternatives — the LLM makes the choice"; codetour = "a valid VS Code CodeTour `.tour` JSON ...
with steps ... omitting extra prose". Both accurate. So this is a genuine pairing conflict.

Coexistence test: could the tour stay pure with the selection in an adjacent block? That is the
`prep+code` resolution. It FAILS here for a different reason than format — the deliverable
itself is wrong. codetour's content unit is a *navigable step through existing code*; a selection
verdict is not a step, and a "tour of the options" never commits, so pick's success condition
(a named committed choice) is not met by the artifact. Putting the verdict adjacent would mean the
tour is decoration around an answer the channel was not asked to carry.

Decisive precedent: codetour **already cautions `sort`** with the identical mechanism — "sorted
items have no navigable code structure". `pick` produces the same class of output (a selection/
ordering verdict) and fails the same way. This is a one-member extension of a shipped cautionary,
with wording that mirrors it.

**Result: cautionary.**

## socratic + browse → CAUTIONARY (extends socratic's channel cautionary, with a better reason)

Mis-description check: socratic's definition is precise and accurate — "interrogates the user's
stated or implied position ... name the specific claim, belief, or reasoning step from the user's
input that will be examined". Not a mis-description.

Coexistence test: could browse drive the browser with socratic's questions in an adjacent block?
This is where it differs from `interactive`. interactive was rescuable because its named current
state could BE the artifact — the artifact supplied what the form needed. socratic's requirement
is not satisfiable by any artifact: it needs *a claim from the user's input* to interrogate. A
browser-driving response has no user position in it; the object socratic operates on is absent,
not merely unrenderable. One token starves the other.

Note this is a SHARPER reason than socratic's two existing entries, which are format-based
("cannot be rendered as executable shell code" / "as a VS Code CodeTour JSON"). The real
constraint is subject-based and applies to enacted/delivery channels generally (browse, github,
store, zettel, hunk, aloud) — not just to the two formats currently listed.

**Result: cautionary**, and the new entry should state the subject-based reason rather than copy
the format-based phrasing.

## aloud + vet / aloud + full → NOT ACTED (single seed, pattern-watch)

Two plausible candidates from seed 230: spoken condensation erodes vet's analytic distinctions,
and `full`/`max` completeness cannot survive spoken density (same shape as the shipped
`presenterm` completeness cautionary, which cautions max/deep and lists minimal/gist natural).
aloud has NO cross-axis entry at all, so this would mean creating one. Deferred: single seed, and
new-entry creation has been held to a higher bar than extension throughout cycles 24-26.

## hunk + sort, diff + code → NOT ACTED (derivable reframes)

Both have available resolutions (group the hunks by category; show both implementations), so
neither is a starvation case. hunk's absent cross-axis entry is noted as a coverage gap.

**Limitation:** single evaluator; compare prompts reasoned, not executed by a fresh model. Both
acted findings are one-member extensions of shipped cautionary families, so the mechanisms are
already tested and only membership is new.

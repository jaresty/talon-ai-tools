## Static prompt catalog snapshots

## Static prompt catalog details

Note: Some behaviours (for example, diagrams, Presenterm decks, ADRs, shell scripts, debugging, Slack/Jira formatting, taxonomy-style outputs) now live only as form/channel/method axis values rather than static prompts; see ADR 012/013 and the README cheat sheet for axis-based recipes.

- make: The response creates new content that did not previously exist, based on the input and constraints. (defaults: completeness=full)
- fix: The response changes the form or presentation of given content while keeping its intended meaning. (defaults: completeness=full)
- pull: The response selects or extracts a subset of the given information without altering its substance. (defaults: completeness=gist)
- sort: The response arranges items into categories or an order using a specified or inferred scheme.
- diff: The response compares two or more subjects, highlighting relationships such as similarities, differences, or tradeoffs.
- show: The response explains or describes the subject for the stated audience.
- probe: The response analyzes the subject to surface structure, assumptions, or implications beyond restatement. (defaults: method=analysis)
- pick: The response chooses one or more options from a set of alternatives. (defaults: method=converge)
- plan: The response proposes steps, structure, or strategy to move from the current state toward a stated goal.
- sim: The response plays out a concrete or hypothetical scenario over time under stated or inferred conditions.
- check: The response evaluates the subject against a condition and reports whether it passes or fails.
- Other static prompts (tokens only; see docs for semantics): (none)

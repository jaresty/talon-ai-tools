# 0067 — Enrich `bar` CLI completions with multi-stage context

## Status
Proposed

## Context
- The embedded grammar now powers the `bar` CLI completions across Bash, Zsh, and Fish.
- Fish completions expose only the next staged suggestion: when multiple contract axes are simultaneously valid (for example, both `scope` and `method`), only a single class of tokens is offered even though the canonical shorthand allows multiple paths.
- Completion listings return bare tokens without indicating their axis, persona dimension, or hydration source. Users cannot tell whether an entry represents a scope, method, persona preset, or override suggestion, nor whether it carries additional descriptive metadata.
- Making completions richer benefits every shell because the completion backend (`bar __complete`) feeds all scripts; the current limitation is most visible in Fish but impacts suggestion quality overall.

## Decision
- Extend the completion engine to return multi-axis suggestion sets when parallel stages are valid so shell front-ends can surface all applicable tokens instead of forcing a single pathway.
- Augment completion payloads with structured metadata describing:
  - the semantic category (axis, preset, override, flag, etc.),
  - the hydration origin (static prompt, persona catalog, axis list, override key), and
  - any human-readable label or description already present in the grammar.
- Update shell completion scripts (Fish, Bash, Zsh) to format metadata appropriately:
  - Fish completions should display category plus label in suggestion listings,
  - Bash/Zsh should include metadata in the description field (where supported) or inline label text.
- Preserve backward compatibility for tooling that consumes the existing text-only suggestions by providing sensible defaults when metadata is absent.

## Rationale
- Showing all valid next steps keeps the CLI aligned with the prompt grammar’s combinatorial rules, reducing user friction and guesswork when constructing shorthand recipes.
- Metadata makes completions self-documenting; users can distinguish axes, persona presets, overrides, and understand how a token will hydrate into a prompt without consulting external docs.
- Structuring metadata at the completion engine layer ensures every shell and future integration benefits consistently without duplicating logic per script.

## Consequences
- The completion backend must evolve from returning simple strings to richer structures (e.g., delimited fields or JSON) and remain performant.
- Shell scripts require formatting tweaks to display metadata succinctly; Fish will likely need to split the metadata into description columns, while Bash/Zsh may rely on `compadd -d`/`compopt` equivalents.
- Tests covering completion ordering and content need to expand to verify multi-stage output and metadata rendering.
- Documentation (help text and installer guidance) should note the richer completions once implemented to set user expectations.

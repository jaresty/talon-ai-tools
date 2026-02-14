# Supplementary Findings — Cycle 1

These findings arose during the evaluation but don't cleanly fit a single task's gap type.
They affect usability or tooling rather than the catalog itself.

---

## SF-01 — Persona tokens hang bar build in shorthand mode

**Observed during:** T01 (explain to product manager), T27 (cross-domain translation)

### Observation

When using persona tokens (audience, voice) in shorthand mode before the static token —
the grammar's documented ordering for persona — bar commands appear to hang in certain
contexts:

```bash
# This hung (audience key=value before task):
bar build audience=to-product-manager show full time flow walkthrough
# Error: unrecognized token for audience: "to-product-manager"
# (Expected: "to product manager" with spaces in canonical form)

# This also hung (shorthand persona before task):
bar build to-product-manager show full time flow walkthrough
# No output — appears to enter interactive TUI state
```

Bar build works fine without persona tokens. The key=value syntax rejects slug format
for audience tokens (`to-product-manager`) and requires the canonical label with spaces
(`to product manager`), which is inconsistent with how other multi-word tokens work.

### Impact

Bar-autopilot cannot easily add audience persona tokens to commands. The skill guidance
says persona tokens go before the static token in shorthand mode, but this appears to
trigger interactive TUI behavior in the CLI, blocking automated skill usage.

### Classification

Not a catalog gap — the tokens exist. This is a **tooling/UX gap** at the CLI level:
- Inconsistency: slug format works for directional tokens (`fly-rog`) but not audience tokens (`to-product-manager`)
- Shorthand-mode persona before static token may trigger TUI instead of being parsed as CLI input

### Recommendation

Investigate and fix slug normalization for persona token key=value syntax. Audience tokens
should accept `audience=to-product-manager` (slug) just as `directional=fly-rog` (slug)
works for directional tokens. This would make bar-autopilot persona application reliable.

Also verify that shorthand persona tokens (listed before static token) work correctly in
non-interactive `bar build` contexts.

---

## SF-02 — `case` form conflicts with `fail+time+origin` combination

**Observed during:** T20 (incident postmortem)

### Observation

`bar build probe full fail time origin case` hung when run. Replacing `case` with
`walkthrough` produced output normally:
```bash
# Hung:
bar build probe full fail time origin case

# Works:
bar build probe full fail time origin walkthrough
```

The `case` form ("structures reasoning by building the case before the conclusion") would
be semantically appropriate for postmortem analysis (build the evidence, then conclude).
But the combination with `fail+time+origin` (or some subset thereof) causes the command
to hang.

### Classification

Potential **incompatibility rule** or **bug** in the grammar's `case` form handling.
The `case` form may have an undocumented conflict with certain scope or method combinations.

### Recommendation

Run `bar shuffle` with `case` form fixed to identify which combinations produce the hang.
Or check the grammar's incompatibility rules for `case` form to see if `fail+time+origin`
triggers a conflict that causes an error prompt rather than failing cleanly.

If this is an undocumented incompatibility, add it to the grammar's conflict list and
ensure bar build exits cleanly with an error message rather than hanging.

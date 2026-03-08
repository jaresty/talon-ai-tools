# ADR-0157: Retire `bar tui`, Promote TUI2 as Sole Interactive Editor

## Status

Proposed

## Context

ADR-0081 introduced TUI2 (`bar tui2`) as a redesigned, command-centric replacement for the
original TUI (`bar tui`). TUI2 has been the recommended path since its introduction — the help
text labels it "recommended for new users" — but the original TUI has never been formally retired.

As a result, the codebase maintains two parallel interactive editor implementations:

| | `bar tui` | `bar tui2` |
|---|---|---|
| Package | `internal/bartui/` | `internal/bartui2/` |
| CLI adapter | `internal/barcli/tui.go` | `internal/barcli/tui2.go` |
| Introduced | ADR-0070/0071/0077 | ADR-0081 |
| Status | Unlabeled in help | "recommended for new users" |

The old TUI receives no active development; all feature work (cross-axis warnings, ADR-0148;
distinction highlights, ADR-0155; etc.) targets TUI2 only. Keeping both packages in the binary
and test suite adds dead weight: the `internal/bartui` package, its adapter, and its test
references must be compiled and maintained despite having no production users.

### Stale field name: `UseWhen`

The `UseWhen string` field in both TUI token structs (`internal/bartui/tokens.go:19` and
`internal/bartui2/program.go:71`) is a holdover from ADR-0142, when `use_when` was a free-form
grammar string. Since ADR-0155, the field is populated from `meta.Heuristics` (a `[]string` joined
with `, `) — not from any `use_when` field. The name misrepresents what the field contains.

Stale ADR-0142 comments referencing `use_when` also remain in `help_llm.go` and `tui_tokens.go`.

## Decision

Retire `bar tui` and remove the old TUI implementation entirely. Rename `UseWhen` to `Heuristics`
in the remaining TUI2 token struct. Clean up stale `use_when` / ADR-0142 comments.

`bar tui2` becomes `bar tui` — the subcommand is renamed so existing users of `bar tui2` are
unaffected by muscle memory, and `bar tui` becomes the canonical name going forward.

> **Alternative framing considered**: simply remove `bar tui` and keep `bar tui2` as-is.
> Rejected: renaming `tui2` → `tui` removes an artifact of the transition ("2" implies a sequel,
> not a finished product) and gives the interactive editor a stable, unsuffixed name. `bar tui2`
> can be kept as an alias during a transition window if needed.

## Salient Task List

- **T-1** Rename `bar tui2` → `bar tui` in `app.go` command dispatch and usage strings.
  Add `bar tui2` as a deprecated alias (same handler, prints a one-time deprecation notice to stderr).
- **T-2** Delete `internal/bartui/` package entirely.
- **T-3** Delete `internal/barcli/tui.go` (the old TUI adapter).
- **T-4** Remove the old `"tui"` dispatch branch from `app.go` (the alias in T-1 replaces it).
- **T-5** Migrate `cmd/bar/main_test.go`: remove `bartui` import; update any tests that reference
  `bartui.Snapshot` or `barcli.SetTUIStarter` to use `bartui2` equivalents.
- **T-6** Rename `UseWhen string` → `Heuristics string` in `internal/bartui2/program.go` token struct
  and all assignment sites within that file.
- **T-7** Update `internal/barcli/tui_tokens.go`: rename `UseWhen:` field assignments → `Heuristics:`;
  remove stale ADR-0142 comments.
- **T-8** Remove stale `use_when` / ADR-0142 references from `internal/barcli/help_llm.go` comments.
- **T-9** Update help text: `bar tui` description no longer needs "recommended for new users"
  qualifier (it is now the only option). Remove `tui2` from the top-level usage string once the
  alias deprecation window closes.

## Alternatives Considered

### Keep both TUI and TUI2 indefinitely
Rejected: TUI2 has been the de facto standard for all new feature work. The old TUI will
increasingly diverge. Maintenance cost compounds over time with no user benefit.

### Remove `bar tui`, keep `bar tui2` as-is (no rename)
Valid. Simpler than the rename. Downside: `tui2` suffix is a transition artifact — it implies
"version 2 of a thing" rather than "the thing." Rename is low-cost and produces a cleaner long-term
surface. Either approach is acceptable; the rename is preferred.

### Rename `UseWhen` only, defer TUI removal
The field rename is a one-line change and clearly correct regardless. But doing it in isolation
(without the TUI removal) leaves the old package intact and adds a partial cleanup that's harder
to track. Grouping both under one ADR is cleaner.

## Consequences

### Positive
- Binary and test surface simplified: one TUI package, one adapter, one set of tests
- `UseWhen` field name accurately reflects its content (`Heuristics`)
- Stale ADR-0142 comments removed — no misleading references to `use_when` in Go source
- `bar tui` becomes a stable, unversioned subcommand name

### Negative
- **Breaking change**: users calling `bar tui` today will get the new TUI2 behavior. In practice
  this is an improvement, but it is a behavior change. The deprecated `bar tui2` alias softens
  the inverse: users calling `bar tui2` continue to work during the transition window.
- Test migration in `cmd/bar/main_test.go` requires care: `bartui.SetTUIStarter` and
  `bartui.Snapshot` have TUI2 equivalents but call signatures may differ.

### Residual
- Deprecation alias for `bar tui2` can be removed in a follow-up once the transition window closes.

---

*Work-log: `0157-retire-bar-tui-promote-tui2.work-log.md`*

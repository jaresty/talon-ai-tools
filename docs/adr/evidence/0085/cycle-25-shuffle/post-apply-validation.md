# Cycle 25 — Post-Apply Validation (ADR-0085 step 12-13, first run across cycles 23-25)

**Date:** 2026-09-29

## What was tested

Re-drew combinations that exercise SHIPPED edits from cycles 23-24 and confirmed each
composition/entry actually fires (is injected into the COMPOSITION RULES section / rendered
in help).

| Shipped edit | Cycle | Fires in current-source binary? | Fires in installed binary (before)? |
|---|---|---|---|
| browse+pull | 23 | ✓ | ✗ (stale) |
| paradox+fix | 23 | ✓ | ✗ (stale) |
| contextualise+sketch | 24 | ✓ | ✗ (stale) |
| contextualise+gherkin | 24-followup | ✓ | ✗ (stale) |
| ledger natural [pick,plan] | 24-followup | ✓ | ✗ (stale) |

## Finding: RELEASE LAG (ADR-0085 step 11a)

- **Correctness: PASS.** Every shipped edit fires correctly in a binary built from current
  source (`go build ./cmd/bar`). The per-cycle verifications this session used that fresh binary
  (`/tmp/bar-new`), so they were valid.
- **Propagation: WAS FAILING.** The installed binary at `/opt/homebrew/bin/bar` (a manually
  placed 17MB file dated before this session — NOT a brew formula, NOT a symlink) predated the
  grammar regen, so plain `bar` reported "unknown composition browse+pull" etc. `bar --version`
  is "dev" for both stale and fresh builds, so the version string cannot detect this gap — the
  reliable tell is composition membership.

## Resolution

Rebuilt (`go build -o /tmp/bar-fresh ./cmd/bar`) and copied over `/opt/homebrew/bin/bar`
(user-approved). Verified the installed `bar` now knows browse+pull, contextualise+sketch,
paradox+fix, and ledger's natural pick/plan. Propagation: PASS.

## Process lesson

- There is no `make bar-install` target and `bar` is not brew-managed — refreshing the installed
  binary is a manual `go build -o /opt/homebrew/bin/bar ./cmd/bar`. This is easy to forget after
  `make bar-grammar-update`, which updates the embedded JSON in source but not the installed
  binary.
- **Verification hygiene going forward:** either verify against a freshly-built binary (as this
  session did with /tmp/bar-new) OR reinstall before verifying with plain `bar`. Verifying a
  catalog edit with a stale installed `bar` would produce a false "not present" result.
- Candidate: add a `make bar-install` target (build + copy to the bin path) so the reinstall step
  is one command and can follow `bar-grammar-update` in the refinement cycle.

# ADR-0169: User-Defined Token Sets — Decentralized Token Ownership

**Status**: Proposed
**Date**: 2026-03-15

---

## Context

The bar token library is currently a single monolithic set maintained in this repository
(`lib/axisConfig.py`, `lib/staticPromptConfig.py`, `lib/personaConfig.py`). Every token
addition, removal, or edit requires a PR to this repo. This creates two problems:

1. **Ownership bottleneck**: Users and teams who want domain-specific tokens (industry
   vocabulary, organization-specific method tokens, persona presets for their team) have no
   path to do so without forking or waiting for a merge.

2. **Library scaling**: As the token library grows, the grammar becomes harder to curate
   centrally. Distributing ownership allows organic specialization without burdening the
   canonical grammar.

The goal is a mechanism that lets users bring their own token sets, combine them with the
built-in grammar at runtime, and optionally share them — without requiring changes to the
core library.

---

## Decision

Implement user-defined token sets in four independently shippable phases. Each phase leaves
the next reachable without requiring any rework.

### Precondition: stabilize the grammar JSON schema

Before phase 1 ships, the grammar JSON schema must be declared stable as a public contract.
External token sets depend on knowing which fields are required, optional, and typed.
The merge-order semantics must also be documented: user tokens win on same-axis+key conflict
(user-last-wins), so user tokens shadow built-ins with identical keys.

Produce a `docs/grammar-schema.md` (or equivalent) documenting the public shape of
`prompt-grammar.json` before phase 1 is accepted.

---

### Phase 1 — Single extension file

**Mechanism**: Add a config key `extra_grammar` (path or `BAR_EXTRA_GRAMMAR` env var)
pointing to a JSON file following the same schema as `prompt-grammar.json`. At load time,
bar merges the user file into the built-in grammar. User tokens win on same-axis+key conflict.

**Scope**: Additive tokens on any axis; same-key tokens shadow built-ins.
**Distribution**: User manages the file directly (git repo, dotfiles, symlink).
**Implementation cost**: Low — one config key, one merge pass in `LoadGrammar`.
**Leaves reachable**: Phase 2 (list of paths → directory scan).

---

### Phase 2 — Directory-based multi-set loading

**Mechanism**: Extend config to accept a list of paths. Additionally define
`~/.bar/tokens/` as a conventional scan directory: bar discovers all `*.json` files there
at startup and merges them in alphabetical order (deterministic load order).

Phase 1's single-path config key becomes a shorthand for prepending one path to the list.

**Distribution**: Drop files into `~/.bar/tokens/`; symlinks work; package managers can
install token sets by placing files in the directory.
**Implementation cost**: Low-medium — directory scan + multi-file merge pass.
**Leaves reachable**: Phase 3 (namespace prefixes) and Phase 4 (remote registry).

---

### Phase 3 — Optional namespace prefixes

**Mechanism**: Token set JSON files may declare an optional top-level `"namespace": "myorg"`
field. When present, bar makes all tokens in that set addressable as `myorg:token` in
`bar build` in addition to their bare key. Non-namespaced tokens continue working as before.

This resolves multi-set collision without requiring filesystem isolation alone: namespaced
sets coexist with each other and with the built-in grammar without shadowing.

**Schema change**: Add optional `namespace` field to token set JSON; extend CLI token
argument parsing to accept `prefix:token` syntax.
**Implementation cost**: Medium — schema change + CLI argument parsing.
**Leaves reachable**: Phase 4 (stable namespaced identities enable a registry).

---

### Phase 4 — Remote registry with lockfile

**Mechanism**: `bar add <url>` fetches a token set JSON into `~/.bar/tokens/` and records
the source URL and content hash in `~/.bar/lockfile.json`. `bar update` refreshes;
`bar remove <namespace>` deletes.

The package manager is thin because phase 2 defines the storage convention and phase 3
gives sets stable namespaced identities. Runtime merge behavior is unchanged.

**Implementation cost**: High — remote fetch, lockfile management, version pinning.
**Enables**: Community ecosystem of publishable, versioned, namespaced token sets.

---

## Consequences

- Users and teams can maintain domain-specific token sets without changes to this repo
- The canonical grammar remains the default; user sets are opt-in overlays
- Merge-order is explicit and deterministic (user-last-wins, alphabetical within directory)
- Phase 1 and 2 can ship without any grammar schema change; phase 3 requires one
- Phase 4 is optional infrastructure; phases 1–3 deliver the core value

## What is not decided here

- The exact format of `docs/grammar-schema.md` (precondition, separate work item)
- Whether `~/.bar/tokens/` is the right conventional directory (may depend on bar's XDG
  config structure, if any)
- Whether `bar add` in phase 4 should support git URLs, raw HTTPS, or both
- Whether namespace prefixes in phase 3 require quoting in shell contexts

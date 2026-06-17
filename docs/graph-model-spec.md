# Formal Graph Model Specification

## Overview

This document specifies the formal properties of the directed graph model used
throughout this codebase to represent token dependency and ordering relationships.

## Definitions

- **G = (V, E)**: A directed graph where V is the set of nodes and E ⊆ V × V is the set of directed edges.
- **reachable(u, v)**: Node v is reachable from u if there exists a path u → ... → v in G.
- **precedes(u, v)**: u precedes v if (u, v) ∈ E (direct edge).

## Axioms

The following axioms govern the graph model:

### A1 — Irreflexivity
For all v ∈ V: (v, v) ∉ E.
No node has an edge to itself.

### A2 — Asymmetry
For all u, v ∈ V: if (u, v) ∈ E then (v, u) ∉ E.
Edges are one-directional; no pair of nodes forms a mutual edge.

### A3 — Closure under composition
For all u, v, w ∈ V: if (u, v) ∈ E and (v, w) ∈ E then (u, w) ∈ E.
The edge relation is closed under path composition.

## Properties

### transitivity

**Statement**: For all u, v, w ∈ V: if (u, v) ∈ E and (v, w) ∈ E then (u, w) ∈ E.

**Derivation**: Follows directly from Axiom A3 (Closure under composition). A3 states
that the edge relation is closed under path composition, which is precisely the
definition of transitivity for a binary relation. Therefore transitivity is not an
independent assumption but a theorem derivable from A3.

**Verified by**: `verify/check_transitivity.py`

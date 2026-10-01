# Cycle 35 — followups

1. **`blind` × `aloud` (seed 602) — one seed, genuine.** `blind` requires each conclusion to name the
   assumption block it draws from *by label*; spoken delivery has no stable label a listener can refer
   back to across a stream. The new topology axis rule covers the channel-construct case, but a
   spoken channel has no referenceable-label construct, and `aloud` offers no adjacent block either
   (same structural point as the `table`/`twin` entries shipped in cycle 34). Candidate: an `aloud`
   topology cautionary for `blind`, pointing at `witness` or `relay`. Held at one seed.

2. **`presenterm` + enumerating methods at `full`** (carried from cycle 34, still one seed). Its
   completeness cautionary covers max/deep/zoom but not a method like `models` that enumerates every
   absent item against a 12-slide cap.

3. **`falsify` and "semantic red" — decision still open.** `falsify` already covers the RED direction
   well: items 46-48 state that an application not producing an A result cannot witness A "regardless
   of the cause or form of the application's outcome", with the canonical illustration that a build
   error "fails identically no matter which property is absent". The gap is narrower — the
   *no-A-fail-observed* branch (item 51) prescribes constructing a perturbation but does not name the
   mundane cause first: that the applied procedure may not contain the assertion at all. Two options:
   (a) one clause in item 51's branch; (b) leave `falsify` alone and treat it as an application
   failure captured in the notebook. Leaning (b) — the rule exists, and `falsify` is already 15.5k
   characters. Needs the consistency check against `ground+falsify` and `falsify+atomic` either way.

4. **Proposed ADR-0085 check, still not written into the ADR:** the duplication discriminator from
   nn 20260930224858-5322. It has now been applied twice (cycle 34 rejected an edit, cycle 35
   justified one), so it has earned its place in the Risks section.

5. **A stale note to correct:** `20260513145454-0928` ("topology axis: wired into bar build, TUI2,
   SPA, and metaprompt") asserts the axis was wired in, while cycle 35 found it shipped with no axis
   description for roughly four months. The wiring was real; the claim is incomplete in a way that let
   the gap persist.

6. Carried: Python full-suite verification still blocked by two pre-existing defects that reproduce on
   a clean tree (nn 20260930174045-0290).

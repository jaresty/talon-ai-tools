# 048 – Grammar Control Plane Simplification (Stance/Contract Split)

- Status: Accepted  
- Date: 2025-12-15  
- Context: Current grammar exposes Persona (voice/audience/tone), Intent (purpose), Contract (completeness/scope/method/style/directional), static prompts, and destinations/sources all in one utterance. Directional lenses are mnemonic and opaque; style mixes container and channel; persona and purpose lists carry low-signal items. Users must remember 6–7 families, optional defaults, and composite directionals, leading to slow recall, mis-parses, and noisy confirmations.

---

## Summary (for users)

- Two verbs:  
  - `model set …` → stance and defaults (Who/Why and optional Contract defaults).  
  - `model run …` → per-call contract (prompt + axes + directional + destination/source).
- Simpler lenses and style: keep the seven core directionals with short glosses (no renames); style split into Form vs Channel with single-value enforcement and legacy style tokens removed.
- Presets and stance defaults reduce repetition; “again” keeps tweaks small.

---

## Decision

1) **Separate stance from per-call contract (required)**
   - Keep existing `persona <preset>` grammar (or explicit voice/audience/tone) and the already-implemented `persona status` / `persona reset`; no grammar change.  
   - Keep existing `intent <preset>` grammar; split the preset list into task vs relational buckets (see #2). No new `relation` alias; use `intent` for both buckets.  
   - Stance + defaults persist for the session; “run” is always per-call. Existing default setters for completeness/scope/method/style remain.

2) **Tighten persona/intent surface (required)**
   - Collapse persona into a small preset set (5–7 high-signal roles); keep raw axes accessible but de-emphasised.  
   - Trim/alias low-yield voice/audience entries (platform/stream-aligned/XP-enthusiast) into presets instead of raw axes.  
   - Split purpose into task intents (decide/teach/evaluate/plan/brainstorm/inform/announce/walkthrough/triage) vs relational intents (persuade/appreciate/coach/collaborate/entertain). Keep a single `intent <preset>` grammar, surface both buckets in help, and allow combining task+relational via presets or sequential commands—not by widening the capture.

3) **Simplify directionals (no renames, required)**
   - Keep the seven core lenses as-is: `fog`, `fig`, `dig`, `ong`, `rog`, `bog`, `jog`. Provide short glosses in docs/help, but do not rename tokens.  
   - Hide composite `fly/fip/dip` values from primary help (advanced shorthand only); keep them as aliases.  
   - Require exactly one directional lens per `run`; allow `jog` as the neutral confirmation lens.

4) **Split style into Form vs Channel (concept + migration)**
   - Form: bullets, table, code, adr, story, checklist, plain, tight, faq, headline, diagram, recipe, bug, spike, log.  
   - Channel bias: slack, jira, presenterm, announce, sync, remote, html.  
   - Grammar shape stays: … `[method]? [method]? [method]? [form]? [channel]? {directional}`; slot order remains stable while the axis name shifts from “style” to “form/channel”.  
   - Enforce Form = 1 and Channel = 1 (replace prior style multiplicity).  
   - Convert existing style tokens to this split now: `slack`, `jira`, `presenterm`, `announce`, `remote`, `sync`, `html` become Channel values (announce also sets Form=headline by default). Remove legacy style tokens rather than keeping alias coverage; update lists/grammar/help/tests to reflect the new Form/Channel vocab.

5) **Presets as first-class control (optional/extend)**
   - `model preset save <name>` from last run; `preset run <name>`; `preset list`.  
   - A preset = prompt + persona + intent/relation + contract axes + directional + destination (extends current persona/intent presets).  
   - Encourage JTBD (summaries, critiques, plans, explanations) to rely on presets instead of long ad-hoc utterances.

6) **Execution grammar shape (required for consistency)**
   - `model run [<prompt>] [<completeness>] [<scope>] [<scope>] [<method>] [<method>] [<method>] [<form>] [<channel>] <directional> [to <destination>] [from <source>] [using <additionalSource>]`.  
   - Minimal path: `model run <prompt> <directional>` (source/destination default). Form/Channel are optional but, when present, must appear at most once each and fall back to defaults/last-run values when omitted.  
   - `model again [<prompt>] [<completeness>] [<scope>] [<scope>] [<method>] [<method>] [<method>] [<form>] [<channel>] [<directional?>]` (directional optional; reuse last).  
   - Apply the same explicit-cardinality `<prompt/axes form>` (scope×2, method×3, form×1, channel×1, directional×1) to other consumers (run-again-with-source, suggest, pattern menus, replay/history).  
   - Axis caps: completeness single; scope up to 2; method up to 3; form exactly 1; channel exactly 1; directional exactly 1.

7) **Discoverability and feedback**
   - `model help who|why|how|form` focuses help panes on persona, intent, contract, style/destination.  
   - Parse-back after capture: “Persona: … | Intent: … | Contract: … | Dest: …”.  
   - Primary help shows only core directionals and Form/Channel split; remove legacy style tokens rather than maintaining alias appendices.

---

## Consequences

### Benefits

- Lower recall burden: fewer visible directionals; style clarified; persona/purpose trimmed.  
- Faster common paths: minimal `run` form; stance defaults reduce repetition; presets cover JTBDs.  
- Clear state separation: stance/defaults vs per-call contract reduces accidental over-specification.  

### Risks and mitigations

- **Risk:** Users relying on composite directionals or long-tail styles may feel items “missing”.  
  - **Mitigation:** keep composite directional aliases; surface an advanced/compat section in help; map composites to core recipes.  
- **Risk:** Removing legacy style tokens during the Form/Channel split can break memorised utterances.  
  - **Mitigation:** convert all style entries to Form/Channel now, update help/cheatsheets/tests, and provide a short migration notice in help.  
- **Risk:** Added verbs (`set`, `preset`) introduce new commands to learn.  
  - **Mitigation:** minimal `run` path stays; help panes and parse-back narrate active stance/defaults.  
- **Risk:** Preset management adds state.  
  - **Mitigation:** small guardrail tests; clear status/list; “preset save” derives from last run only.

---

## Implementation sketch

1) **Grammar/captures**
   - Keep `intent` as the sole setter for task/relational presets; no `relation` alias.  
   - Update `model run` capture to require one directional and accept exactly one Form and one Channel; apply the same Form/Channel caps to `again`, replay/history, suggest, and pattern consumers.  
   - Adjust `again` to allow optional directional reuse.

2) **Token surfacing**
   - Core directional names + aliases; hide composites from default help.  
   - Style lists refactored into Form/Channel buckets with no legacy style aliases retained.  
   - Persona/purpose lists trimmed; keep aliases for retired items mapped to presets or canonical tokens.

3) **Presets**
   - Store presets (prompt + persona + intent/relation + contract + directional + dest).  
   - Commands: `preset save/run/list`; small canvas or spoken feedback on apply.

4) **UI/help/feedback**
   - Help panes for `who/why/how/form`; parse-back summaries after capture; axis docs updated to reflect Form/Channel and core directionals.  
   - Quick help shows minimal surface; compatibility appendix lists aliases.

5) **Tests/guardrails**
   - Grammar capture tests for new verbs and required directional.  
   - Alias resolution tests (composite directionals; Form/Channel enforced without legacy style aliases).  
   - Preset save/run coverage and stance/default persistence.  
   - Parse-back text assertions to prevent regressions in user feedback.  
   - Post-migration guardrails to assert single-value Form/Channel across captures, replay/history, and UI surfacing.

---

## Outstanding follow-ups (tracked for implementation)
- Completed: grammar consumers (`modelPrompt`, run/again, replay/history) enforce `[form] [channel] <directional>` with axis caps; `suggest` remains free-form on input but suggestion recipes are normalised/validated to the same caps with a required directional, and legacy style tokens are rejected. Direction-less history entries are hidden from summaries/open.
- Help/cheatsheets/parse-back: surface migration messaging (legacy style removal), Form/Channel defaults fallback, and cardinality in recap/help surfaces; ensure parse-back shows form/channel + directional. ✅ Response canvas, help canvas, and Help Hub cheat sheet now remind users form+channel are optional singletons (defaults/last-run apply) and one directional lens is required.
- Guardrails/tests: drift checks remain red if style tokens reappear; parse-back/help canvases and Help Hub cheat sheet are covered by guardrails for form=1/channel=1/directional=1 messaging and axis caps on recaps/history; negative legacy-style capture test remains in place.
- Intent combinations: keep `intent <preset>` single-valued in capture; allow task+relational pairing only via presets or sequential commands (per ADR). If we decide to support dual intent tokens, add a follow-up to widen storage/state/help/tests explicitly. ✅ Enforced today; no open work.
- Execution order: complete; capture/history/help/parse-back surfaces migrated and guarded. No remaining open implementation items.

---

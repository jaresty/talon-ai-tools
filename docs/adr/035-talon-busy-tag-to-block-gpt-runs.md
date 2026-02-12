# 035 — Talon Busy Tag to Block GPT Runs During In-Flight Requests

## Status

Accepted (2026-02-11) — tag lifecycle, grammar gating, and startup cleanup shipped;
see ADR-0080 work-log Loops 3–4 for evidence.

## Context / Problem

- We already enforce a runtime guard in Python that rejects starting a new GPT request while one is in-flight. However, Talon can still recognize “model run …” voice commands during a run, which leads to user confusion (spurious notifications, potential clipboard/selection side effects) and frequent accidental invocations when using control surfaces (help, canvas, history) whose phrases overlap with run prefixes.
- We want a stronger, user-visible block at the grammar layer to prevent any GPT run commands from even matching while a request is active, without muting non-run control commands.

## Decision (proposed)

- Introduce a Talon tag (e.g., `gpt_busy`) that is set when a GPT request begins sending/streaming and cleared on completion, failure, or cancel.
- While `gpt_busy` is set, disable the “model run …” command contexts so Talon will not match run invocations. Non-run commands (help, history, canvas actions) remain available.
- Keep the existing Python-side in-flight guard as a second layer; the tag is additive and user-facing.
- On startup/reload, ensure the tag is cleared to avoid sticky-disabled commands if Talon restarts mid-run.
- Emit a brief notify when a run command is rejected because `gpt_busy` is active, so users understand why the command didn’t fire.

## Rationale

- Prevents accidental duplicate runs and reduces user confusion in noisy environments or when reusing overlapping prefixes for help/pattern controls.
- Keeps non-run control surfaces usable during a run (viewing help, closing canvases, history).
- The tag provides immediate feedback at recognition time, while the Python guard remains a safety net.

## Implementation sketch

- Define `tag: gpt_busy` in a Talon module.
- When request phase enters sending/streaming (e.g., via requestBus/controller callbacks), add the tag; on complete/fail/cancel, remove it. On Talon startup/reload, remove it defensively.
- Scope the “model run …” contexts to `not gpt_busy` (or equivalently, enable them only when the tag is absent).
- Add a short notify when a blocked run command is attempted (optional, if Talon offers a hook), but keep the Python guard notification as well.

## Consequences / Open Questions

- Need to ensure tag cleanup on all terminal paths to avoid stuck-disabled commands.
- Minor added state coupling between request lifecycle and grammar activation.
- If desired, we could also dim/annotate UI surfaces (canvas/patterns) when busy, but that is out of scope for this ADR.

## Definition of done

- `gpt_busy` tag exists and is toggled appropriately on send/stream complete/fail/cancel and cleared on startup/reload.
- “model run …” contexts are disabled when the tag is set; non-run commands remain available.
- Python in-flight guard remains in place (no regression to existing protections).
- Optional: user notification when a run command is blocked due to busy tag.***

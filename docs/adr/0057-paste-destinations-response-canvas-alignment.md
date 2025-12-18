# 0057 – Align paste destinations with the response canvas

## Status
Proposed

## Context
- Paste-oriented destinations (for example `paste`, `above`, `below`, `chunked`, `typed`) are the default expectation when users are working inside an editable control.
- Users rely on the confirmation/response canvas to preview and manage results when they are **not** in an editable control, when they explicitly open the canvas, or when they want to interrupt a paste.
- Existing behaviour routes many destinations through the response canvas whenever a focused textarea cannot be detected, but the rules are unclear when the canvas is already open or when users explicitly request a paste.
- Streaming feedback is currently only obvious inside the response canvas; when a request takes a long time the “paste” happy-path provides little feedback besides the standard progress pill.
- Voice commands such as `paste response` and `model pass response` must feel predictable regardless of whether the canvas is showing.
- Losing focus during a run invalidates the assumption that a paste can succeed, so the system must re-check focus before inserting.

## Decision
- **Destination evaluation at request start**
  - When a paste-type destination is requested, check `inside_textarea()` immediately.
  - If the response canvas is already open (or a prior request set `current_destination_kind` to `window`), promote the destination to `window` so the in-flight request streams into the canvas and does not paste automatically.
  - If no textarea is focused (or detection fails) promote to `window` so the result streams into the canvas instead of disappearing.
  - Otherwise keep the paste-type destination but remember that the user expects an actual paste.
- **Streaming feedback for textarea pastes**
  - Always keep the request progress pill visible while the paste run is inflight.
  - Add a `Show response` affordance on the pill that opens the canvas immediately when clicked/tapped.
  - After a configurable delay (for example 1–2 seconds) surface a lightweight toast reminding the user that they can say `model show response` to open the canvas if they want to watch streaming.
  - Do **not** auto-open the canvas when a textarea is detected; this preserves the quick-insert workflow while still giving feedback.
- **Canvas/pill parity**
  - When the user closes the canvas while a request is still streaming, show the progress pill again so feedback continues.
  - When the canvas is open, hide or minimise the pill to avoid duplicate surfaces unless debug mode explicitly requests both.
- **Focus re-check before paste**
  - Immediately before inserting, call `inside_textarea()` again. If focus has left the input field, convert the destination to `window`, stream the finished result into the canvas, and suppress the paste.
- **`paste response` command**
  - If the response canvas is open, close it, restore focus to the original app, and paste.
  - If the canvas is closed and a textarea is focused, paste directly.
  - If no textarea is focused, open the canvas instead of attempting to paste.
- **`model pass response` family**
  - Treat `model pass response`, `model pass response to this`, and similar commands as paste-type destinations that follow the same rules: paste when inside an editable control, otherwise stream into the canvas.
  - When these commands are invoked while the canvas is open, respect the existing content and avoid auto-pasting; the user can explicitly invoke `paste response` afterwards.
- **Response canvas streaming guarantee**
  - Any time the canvas is opened (either because the user already had it open, or because we promoted the destination to `window`) ensure streaming continues into the canvas so requirement (4) is honoured.
- **State synchronisation**
  - Update `GPTState.current_destination_kind` every time we promote or demote destinations so subsequent commands (`paste response`, reruns, pass commands) see consistent semantics.

## Rationale
- Requirement (1) is satisfied by retaining paste destinations when a textarea is focused, and re-validating focus right before insertion.
- Requirement (2) is met because the paste promotion rules honour an already-open canvas and keep the result in that surface.
- Requirement (3) is handled by promoting paste destinations to the response canvas when no textarea is present, ensuring visibility instead of a lost paste.
- Requirement (4) is reinforced by explicitly guaranteeing that any open canvas keeps streaming.
- Requirement (5) is addressed through the progress pill, the `Show response` affordance, and the reminder toast, giving feedback without breaking the quick insert flow.
- Requirement (6) is covered by the focus re-check prior to paste; if focus moved, we fall back to the canvas.
- Requirements (7) and (8) are codified in the `paste response` command behaviour.
- Requirements (9) and (10) are satisfied by reusing the same destination evaluation for `model pass response`.

## Interaction scenarios
| Scenario | Destination start | Focus check result | Canvas state | Outcome |
| --- | --- | --- | --- | --- |
| User says `model run …` with default paste destination while caret is in a textarea | paste | inside textarea | closed | Progress pill + reminder toast; on completion paste result directly |
| Same as above but response canvas already open | paste | inside textarea | open | Promote to window; stream into canvas; no paste |
| Caret starts in textarea but user clicks away before completion | paste | start inside textarea, end outside | either | Re-check fails; promote to window; stream into canvas |
| `paste response` spoken while canvas open | N/A | n/a | open | Close canvas, restore focus, paste |
| `paste response` spoken with no textarea focused | N/A | outside textarea | closed | Open canvas, do not paste |
| `model pass response` while caret in textarea | paste | inside textarea | closed | Paste directly |
| `model pass response` while not in textarea | paste | outside textarea | either | Promote to window; stream into canvas |

## Implementation notes
- Consolidate destination promotion logic inside `ModelDestination` (paste-type subclasses) so `gpt_insert_response` and `gpt_pass` share behaviour.
- Ensure `GPTState.current_destination_kind` mirrors the effective destination after promotion.
- Add regression tests covering
  - Paste destination with/without textarea
  - Canvas-open cases for paste and `paste response`
  - Focus change mid-run
  - `model pass response` with textarea and non-textarea focus
- Update docs/help surfaces to explain the reminder toast, the pill `Show response` affordance, and the explicit `paste response` follow-up when the canvas is open.

## Risks and mitigations
- **False negatives from accessibility focus detection.** Mitigation: keep existing fallback heuristics (app name/bundle) before promoting to window.
- **Reminder toast fatigue.** Mitigation: throttle to one reminder per request and provide a setting to disable the hint.
- **Latency added by re-checking focus.** Mitigation: perform the re-check just before paste; the call is inexpensive compared with the model latency.
- **User confusion if promotion decisions appear inconsistent.** Mitigation: log promotion decisions in debug mode and document the rules in help/quick start guides.

# Work log – 0057 Align paste destinations with the response canvas

## 2025-12-17
- kind: behaviour
- focus: destination promotion + paste/canvas parity groundwork
- plan: Review `lib/modelDestination.py`, `GPT/gpt.py`, and request UI surfaces; refactor shared promotion logic to honour textarea focus, response canvas state, and focus re-check before paste; adjust `paste response` command handling; ensure pill/canvas toggling hooks are discoverable.
- next: implement code changes, add regression coverage, update ADR tasks as needed.

## 2025-12-17
- kind: behaviour
- focus: destination promotion + pill parity implementation
- change: Added shared destination surface evaluation (`prepare_destination_surface`) and textarea re-check helpers; updated paste-type destinations and `confirmation_gui_paste` to reuse paste fallback logic; introduced pill dual-action affordance with show-response region and hid/show parity when the canvas toggles; extended tests covering paste, confirmation GUI, pill canvas, and response canvas close flows.
- artefacts: lib/modelDestination.py, lib/modelHelpers.py, lib/modelConfirmationGUI.py, lib/pillCanvas.py, lib/modelResponseCanvas.py, _tests/test_model_destination.py, _tests/test_model_confirmation_gui.py, _tests/test_request_history_actions.py, _tests/test_pill_canvas.py, _tests/test_model_response_canvas_close.py, _tests/test_gpt_actions.py.
- tests: `python3 -m pytest _tests/test_model_destination.py _tests/test_model_confirmation_gui.py _tests/test_request_history_actions.py _tests/test_pill_canvas.py _tests/test_model_response_canvas_close.py _tests/test_gpt_actions.py`.
- adversarial: Manual UI verification still needed to confirm pill hit-target layout and canvas/pill transitions in real Talon runtime; telemetry/logging already captures destination promotions for additional monitoring.

# History Guardrail Checklist (helper:v20251221.0)

This checklist captures the manual commands that must run before resetting history gating counters so telemetry and Concordance artefacts stay archived. Run the steps from the repository root unless noted.

## Primary commands

1. Archive the current history summary without resetting counters:
   - `python3 scripts/tools/history-axis-validate.py --summary-path artifacts/history-axis-summaries/history-validation-summary.json`
2. Export the streaming gating summary for dashboards:
   - `python3 scripts/tools/history-axis-validate.py --summarize-json artifacts/history-axis-summaries/history-validation-summary.json --summary-format streaming`
3. Export the persona/intent summary JSON used to monitor alias drift:
   - `python3 scripts/tools/history-axis-validate.py --summarize-json artifacts/history-axis-summaries/history-validation-summary.json --summary-format json > artifacts/history-axis-summaries/history-validation-summary.streaming.json`
4. Generate the telemetry payload with last-drop metadata:
   - `python3 scripts/tools/history-axis-export-telemetry.py artifacts/history-axis-summaries/history-validation-summary.json --output artifacts/history-axis-summaries/history-validation-summary.telemetry.json --top 5 --pretty`
5. Reset gating counters **after** the summary files exist:
   - `python3 scripts/tools/history-axis-validate.py --summary-path artifacts/history-axis-summaries/history-validation-summary.json --reset-gating`
6. Capture a parity run for CI/job-summary alignment (optional but recommended):
   - `scripts/tools/run_guardrails_ci.sh request-history-guardrails`

## Helper shortcuts

- CLI helper: `python3 scripts/tools/history-guardrail-checklist.py` (use `--format json` for machine-readable output).
- Make target: `make history-guardrail-checklist` prints the same helper text via the Makefile.

## Artefact expectations

- Summary JSON: `artifacts/history-axis-summaries/history-validation-summary.json`
- Streaming summary: `artifacts/history-axis-summaries/history-validation-summary.streaming.json`
- Telemetry export: `artifacts/history-axis-summaries/history-validation-summary.telemetry.json`

## Notes

- Archive or upload the summary/telemetry files before invoking `--reset-gating` so Concordance dashboards retain the latest drop data.
- When running inside GitHub Actions, ensure the guardrail workflow uploads these artefacts to the `history-axis-summaries` artifact with 30-day retention.
- Record the `Last gating drop` and `Streaming last drop` lines from guardrail output alongside the summary artefacts for incident audits.

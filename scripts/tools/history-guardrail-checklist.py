#!/usr/bin/env python3
"""Print the manual guardrail checklist for ADR-0056 history telemetry runs."""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from dataclasses import dataclass
from typing import Any, Iterable

HELPER_VERSION = "helper:v20251221.0"
SUMMARY_PATH = "artifacts/history-axis-summaries/history-validation-summary.json"
TELEMETRY_PATH = (
    "artifacts/history-axis-summaries/history-validation-summary.telemetry.json"
)
STREAMING_SUMMARY_PATH = (
    "artifacts/history-axis-summaries/history-validation-summary.streaming.json"
)
MAKE_TARGET = "request-history-guardrails"
CI_COMMAND = "scripts/tools/run_guardrails_ci.sh request-history-guardrails"


@dataclass(frozen=True)
class ChecklistStep:
    """Represent a single checklist action."""

    id: str
    description: str
    command: str


CHECKLIST_STEPS: tuple[ChecklistStep, ...] = (
    ChecklistStep(
        id="capture-summary",
        description="Capture the latest request history summary before resetting gating counters",
        command=(
            "python3 scripts/tools/history-axis-validate.py --summary-path "
            f"{SUMMARY_PATH}"
        ),
    ),
    ChecklistStep(
        id="export-streaming-summary",
        description=(
            "Export the streaming gating summary for dashboards and CI artefacts"
        ),
        command=(
            "python3 scripts/tools/history-axis-validate.py --summarize-json "
            f"{SUMMARY_PATH} --summary-format streaming"
        ),
    ),
    ChecklistStep(
        id="export-persona-summary",
        description=(
            "Export the persona and intent summary JSON to monitor alias drift"
        ),
        command=(
            "python3 scripts/tools/history-axis-validate.py --summarize-json "
            f"{SUMMARY_PATH} --summary-format json > {STREAMING_SUMMARY_PATH}"
        ),
    ),
    ChecklistStep(
        id="export-telemetry",
        description="Persist telemetry snapshot with last-drop metadata for downstream ingestion",
        command=(
            "python3 scripts/tools/history-axis-export-telemetry.py "
            f"{SUMMARY_PATH} --output {TELEMETRY_PATH} --top 5 --pretty"
        ),
    ),
    ChecklistStep(
        id="reset-gating",
        description=("Reset gating counters only after the summary has been archived"),
        command=(
            "python3 scripts/tools/history-axis-validate.py --summary-path "
            f"{SUMMARY_PATH} --reset-gating"
        ),
    ),
    ChecklistStep(
        id="ci-parity",
        description=(
            "Run the CI helper to confirm the guardrail job summary matches local output"
        ),
        command=CI_COMMAND,
    ),
    ChecklistStep(
        id="make-target",
        description=(
            "Run the full Makefile guardrail target when parity with automation is ok"
        ),
        command=f"make {MAKE_TARGET}",
    ),
)


def iter_plain_lines(steps: Iterable[ChecklistStep]) -> Iterable[str]:
    yield f"History guardrail checklist ({HELPER_VERSION})"
    yield (
        ""
        "This checklist captures telemetry before guardrail resets so Concordance artefacts stay archived."
        " "
    )
    yield ""
    yield f"Primary summary path: {SUMMARY_PATH}"
    yield f"Telemetry export path: {TELEMETRY_PATH}"
    yield ""
    for index, step in enumerate(steps, start=1):
        wrapped = textwrap.fill(
            step.description,
            width=88,
            initial_indent=f"{index}. ",
            subsequent_indent="   ",
        )
        yield wrapped
        yield f"   Command: {step.command}"
    yield ""
    yield "Reminder: archive the JSON artefacts alongside CI job summaries before gating resets."


def format_plain(steps: Iterable[ChecklistStep]) -> str:
    return "\n".join(iter_plain_lines(steps))


def format_json(steps: Iterable[ChecklistStep]) -> str:
    payload: dict[str, Any] = {
        "helper_version": HELPER_VERSION,
        "artifact_path": SUMMARY_PATH,
        "telemetry_path": TELEMETRY_PATH,
        "streaming_summary_path": STREAMING_SUMMARY_PATH,
        "make_target": MAKE_TARGET,
        "ci_command": CI_COMMAND,
        "steps": [
            {
                "id": step.id,
                "description": step.description,
                "command": step.command,
            }
            for step in steps
        ],
    }
    return json.dumps(payload, indent=2, sort_keys=True)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Print the manual guardrail checklist that archives telemetry before resetting"
            " request history gating counters."
        )
    )
    parser.add_argument(
        "--format",
        choices=("plain", "json"),
        default="plain",
        help="Select output format (plain text or JSON).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.format == "json":
        print(format_json(CHECKLIST_STEPS))
        return 0
    print(format_plain(CHECKLIST_STEPS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

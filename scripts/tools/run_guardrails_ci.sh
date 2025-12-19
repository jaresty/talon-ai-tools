#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/tools/run_guardrails_ci.sh [TARGET]

CI-friendly guardrail runner: validates axis/static prompt catalog and list drift (catalog-only by default; no talon-lists generation).
- TARGET: optional Make target (default: GUARDRAILS_TARGET env or "guardrails").
          The default guardrails target runs overlay lifecycle/helper guardrails and request-history guardrails (see request-history-guardrails[-fast]).

Examples:
  GUARDRAILS_TARGET=axis-guardrails-ci scripts/tools/run_guardrails_ci.sh
  scripts/tools/run_guardrails_ci.sh axis-guardrails-ci
EOF
}

if [[ ${1-} == "-h" || ${1-} == "--help" ]]; then
  usage
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TARGET="${1:-${GUARDRAILS_TARGET:-guardrails}}"

REQUIRE_SUMMARY="false"
case "${TARGET}" in
  guardrails|ci-guardrails|request-history-guardrails|request-history-guardrails-fast)
    REQUIRE_SUMMARY="true"
    ;;
  *)
    REQUIRE_SUMMARY="false"
    ;;
esac

cd "${ROOT}"

# Run the guardrails target (defaults to CI guardrails + parity tests).
echo "Running guardrails target: ${TARGET}"
make "${TARGET}"

SUMMARY_DIR="artifacts/history-axis-summaries"
SUMMARY_FILE="${SUMMARY_DIR}/history-validation-summary.json"

if [[ -f "${SUMMARY_FILE}" ]]; then
  echo "History validation summary (JSON): ${SUMMARY_FILE}"
  cat "${SUMMARY_FILE}"
  echo "History summary recorded at ${SUMMARY_FILE}; job summary will reference this file when running in GitHub Actions."
  TOTAL_ENTRIES=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
print(data.get("total_entries", "unknown"))
PY
)
  GATING_DROPS=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
print(data.get("gating_drop_total", "unknown"))
PY
)
  echo "History summary stats: total_entries=${TOTAL_ENTRIES} gating_drop_total=${GATING_DROPS}"
  GATING_REASONS=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary", {})
counts = summary.get("counts")
counts_sorted = summary.get("counts_sorted")
ordered = []
if isinstance(counts_sorted, list) and counts_sorted:
    for item in counts_sorted:
        if not isinstance(item, dict):
            continue
        reason = item.get("reason")
        value = item.get("count")
        if isinstance(reason, str) and reason:
            try:
                ordered.append((reason, int(value)))
            except Exception:
                continue
elif isinstance(counts, dict) and counts:
    def _key(item):
        reason, raw_value = item
        try:
            count_value = int(raw_value)
        except Exception:
            count_value = 0
        return (-count_value, str(reason))
    for reason, raw_value in counts.items():
        if not isinstance(reason, str) or not reason:
            continue
        try:
            count_value = int(raw_value)
        except Exception:
            continue
        ordered.append((reason, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))

if ordered:
    print(", ".join(f"{reason}={value}" for reason, value in ordered))
else:
    print("none")
PY
)
  GATING_REASONS_TABLE=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary", {})
counts = summary.get("counts")
counts_sorted = summary.get("counts_sorted")
ordered = []
if isinstance(counts_sorted, list) and counts_sorted:
    for item in counts_sorted:
        if not isinstance(item, dict):
            continue
        reason = item.get("reason")
        value = item.get("count")
        if isinstance(reason, str) and reason:
            try:
                ordered.append((reason, int(value)))
            except Exception:
                continue
elif isinstance(counts, dict) and counts:
    for reason, raw_value in counts.items():
        if not isinstance(reason, str) or not reason:
            continue
        try:
            count_value = int(raw_value)
        except Exception:
            continue
        ordered.append((reason, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))

if ordered:
    print("| Reason | Count |")
    print("| --- | --- |")
    for reason, value in ordered:
        print(f"| {reason} | {value} |")
PY
)
  echo "History summary gating reasons: ${GATING_REASONS}"
  if [[ -n "${GATING_REASONS_TABLE}" ]]; then
    printf '%s\n' "Streaming gating reasons:"
    printf '%s\n' "${GATING_REASONS_TABLE}"
  fi

  if [[ -n "${GITHUB_REPOSITORY:-}" ]] && [[ -n "${GITHUB_RUN_ID:-}" ]]; then

    ARTIFACT_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}#artifacts"
    echo "History summary artifact: ${ARTIFACT_URL}"
  else
    ARTIFACT_URL=""
  fi

  STREAMING_ARGS=(--summarize-json "${SUMMARY_FILE}" --summary-format streaming)
  STREAMING_LINE=$(python3 scripts/tools/history-axis-validate.py "${STREAMING_ARGS[@]}")
  echo "${STREAMING_LINE}"

  STREAMING_JSON_ARGS=(--summarize-json "${SUMMARY_FILE}" --summary-format json)
  if [[ -n "${ARTIFACT_URL}" ]]; then
    STREAMING_JSON_ARGS+=(--artifact-url "${ARTIFACT_URL}")
  fi
  STREAMING_JSON=$(python3 scripts/tools/history-axis-validate.py "${STREAMING_JSON_ARGS[@]}")
  echo "Streaming gating summary (json): ${STREAMING_JSON}"
  STREAMING_JSON_PATH="${SUMMARY_DIR}/history-validation-summary.streaming.json"
  printf '%s\n' "${STREAMING_JSON}" > "${STREAMING_JSON_PATH}"
  echo "Streaming JSON summary recorded at ${STREAMING_JSON_PATH}; job summary will reference this file when running in GitHub Actions."

  TELEMETRY_PATH="${SUMMARY_DIR}/history-validation-summary.telemetry.json"
  TELEMETRY_ARGS=("${SUMMARY_FILE}" --output "${TELEMETRY_PATH}" --top 5 --pretty)
  if [[ -n "${ARTIFACT_URL}" ]]; then
    TELEMETRY_ARGS+=(--artifact-url "${ARTIFACT_URL}")
  fi
  python3 scripts/tools/history-axis-export-telemetry.py "${TELEMETRY_ARGS[@]}"
  TELEMETRY_JSON=$(cat "${TELEMETRY_PATH}")
  echo "Telemetry summary (json): ${TELEMETRY_JSON}"

  SUMMARY_ARGS=(--summarize-json "${SUMMARY_FILE}")

  if [[ -n "${ARTIFACT_URL}" ]]; then
    SUMMARY_ARGS+=(--artifact-url "${ARTIFACT_URL}")
  fi
  SUMMARY_DETAILS=$(python3 scripts/tools/history-axis-validate.py "${SUMMARY_ARGS[@]}")
  echo "${SUMMARY_DETAILS}"
  echo "History summary artifact retained for 30 days via GitHub Actions upload-artifact."

  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
      printf '%s\n' "${SUMMARY_DETAILS}"
      printf '\n'
      if [[ -n "${ARTIFACT_URL}" ]]; then
        printf '%s\n' "- Download summary artifact: [History axis summary](${ARTIFACT_URL})"
      else
        printf '%s\n' "- Download summary artifact: [History axis summary](${STREAMING_JSON_PATH})"
      fi
      printf '%s\n' "- Streaming JSON summary recorded at ${STREAMING_JSON_PATH}"
      printf '%s\n' "- Streaming gating summary (text): ${STREAMING_LINE}"
      printf '%s\n' "- total entries: ${TOTAL_ENTRIES:-unknown}"
      printf '%s\n' "- gating drops: ${GATING_DROPS:-unknown}"
      if [[ -n "${GATING_REASONS_TABLE}" ]]; then
        printf '%s\n' "Streaming gating reasons:"
        printf '%s\n' "${GATING_REASONS_TABLE}"
      else
        printf '%s\n' "- Streaming gating reasons: ${GATING_REASONS:-none}"
      fi
      printf '%s\n' "- Telemetry summary recorded at ${TELEMETRY_PATH}"
      printf '\n'
      printf '%s\n' "Streaming summary (json):"
      printf '```json\n%s\n```\n' "${STREAMING_JSON}"
      printf '%s\n' "Telemetry payload (json):"
      printf '```json\n%s\n```\n' "${TELEMETRY_JSON}"
    } >> "${GITHUB_STEP_SUMMARY}"
  fi
elif [[ "${REQUIRE_SUMMARY}" == "true" ]]; then
  echo "History validation summary required for target ${TARGET} but not found at ${SUMMARY_FILE}" >&2
  exit 1
else
  echo "History validation summary not found at ${SUMMARY_FILE}; target ${TARGET} does not require it."
  echo "History summary not required for target ${TARGET}; no job summary entry created."
fi


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
  echo "History summary artifact retained for 30 days via GitHub Actions upload-artifact."
  if [[ -n "${GITHUB_REPOSITORY:-}" ]] && [[ -n "${GITHUB_RUN_ID:-}" ]]; then
    ARTIFACT_URL="${GITHUB_SERVER_URL:-https://github.com}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}#artifacts"
    echo "History summary artifact: ${ARTIFACT_URL}"
  fi
elif [[ "${REQUIRE_SUMMARY}" == "true" ]]; then
  echo "History validation summary required for target ${TARGET} but not found at ${SUMMARY_FILE}" >&2
  exit 1
else
  echo "History validation summary not found at ${SUMMARY_FILE}; target ${TARGET} does not require it."
  echo "History summary not required for target ${TARGET}; no job summary entry created."
fi


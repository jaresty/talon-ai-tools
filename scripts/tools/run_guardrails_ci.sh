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
elif [[ "${REQUIRE_SUMMARY}" == "true" ]]; then
  echo "History validation summary required for target ${TARGET} but not found at ${SUMMARY_FILE}" >&2
  exit 1
else
  echo "History validation summary not found at ${SUMMARY_FILE}; target ${TARGET} does not require it."
fi

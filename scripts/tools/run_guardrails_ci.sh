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

cd "${ROOT}"

# Run the guardrails target (defaults to CI guardrails + parity tests).
echo "Running guardrails target: ${TARGET}"
make "${TARGET}"

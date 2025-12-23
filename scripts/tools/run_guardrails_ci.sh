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

run_telemetry_export() {
  if PYTHONPATH=. python3 -m lib.telemetryExport --output-dir "artifacts/telemetry" --reset-gating; then
    return 0
  fi
  if python3 -m talon_user.lib.telemetryExport --output-dir "artifacts/telemetry" --reset-gating; then
    return 0
  fi
  python3 scripts/tools/history-axis-validate.py --summary-path "artifacts/telemetry/history-validation-summary.json"
  if [[ ! -f "artifacts/telemetry/suggestion-skip-summary.json" ]]; then
    python3 scripts/tools/suggestion-skip-export.py --output "artifacts/telemetry/suggestion-skip-summary.json" --pretty
  fi
  python3 scripts/tools/history-axis-export-telemetry.py "artifacts/telemetry/history-validation-summary.json" --output "artifacts/telemetry/history-validation-summary.telemetry.json" --top 5 --pretty --skip-summary "artifacts/telemetry/suggestion-skip-summary.json"
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

TELEMETRY_DIR="artifacts/telemetry"
mkdir -p "${TELEMETRY_DIR}"

SUMMARY_DIR="${TELEMETRY_DIR}"
SUMMARY_FILE="${SUMMARY_DIR}/history-validation-summary.json"

if [[ ! -f "${SUMMARY_FILE}" ]]; then
  if [[ "${REQUIRE_SUMMARY}" == "true" ]]; then
    if ! run_telemetry_export; then
      echo "Talon telemetry exporter unavailable; history summary remains unset." >&2
    fi
  else
    echo "History validation summary not found at ${SUMMARY_FILE}; target ${TARGET} does not require it."
    echo "History summary not required for target ${TARGET}; no job summary entry created."
    exit 0
  fi
fi

if [[ -f "${SUMMARY_FILE}" ]]; then
  echo "History validation summary (JSON): ${SUMMARY_FILE}"
  cat "${SUMMARY_FILE}"
  echo "History summary recorded at ${SUMMARY_FILE}; job summary will reference this file when running in GitHub Actions."
  echo "History guardrail target: ${TARGET}"
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
  GATING_STATUS=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary")
status = ""
if isinstance(summary, dict):
    status = str(summary.get("status") or "").strip()
print(status or "unknown")
PY
 )

  IFS=$'\n' read -r GATING_LAST_MESSAGE GATING_LAST_CODE <<EOF
$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
message = str(data.get("gating_drop_last_message") or "").strip().replace("\n", " ")
code = str(data.get("gating_drop_last_code") or "").strip().replace("\n", " ")
if not message:
    message = "none"
print(message)
print(code)
PY
)
EOF
  GATING_LAST_MESSAGE=${GATING_LAST_MESSAGE:-none}
  GATING_LAST_CODE=${GATING_LAST_CODE:-}
  if [[ -n "${GATING_LAST_CODE}" ]]; then
    GATING_LAST_SUMMARY="${GATING_LAST_MESSAGE} (code=${GATING_LAST_CODE})"
  else
    GATING_LAST_SUMMARY="${GATING_LAST_MESSAGE}"
  fi

  echo "History summary gating status: ${GATING_STATUS}"
  echo "History summary last drop: ${GATING_LAST_SUMMARY}"

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

  GATING_SOURCES=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary", {})
sources = summary.get("sources")
sources_sorted = summary.get("sources_sorted")
ordered = []
if isinstance(sources_sorted, list) and sources_sorted:
    for item in sources_sorted:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        value = item.get("count")
        if isinstance(source, str) and source:
            try:
                ordered.append((source, int(value)))
            except Exception:
                continue
elif isinstance(sources, dict) and sources:
    for source, raw_value in sources.items():
        if not isinstance(source, str) or not source:
            continue
        try:
            count_value = int(raw_value)
        except Exception:
            continue
        ordered.append((source, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))

if ordered:
    print(", ".join(f"{source}={value}" for source, value in ordered))
else:
    print("none")
PY
)
  GATING_SOURCES_TABLE=$(python3 - "$SUMMARY_FILE" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary", {})
sources = summary.get("sources")
sources_sorted = summary.get("sources_sorted")
ordered = []
if isinstance(sources_sorted, list) and sources_sorted:
    for item in sources_sorted:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        value = item.get("count")
        if isinstance(source, str) and source:
            try:
                ordered.append((source, int(value)))
            except Exception:
                continue
elif isinstance(sources, dict) and sources:
    for source, raw_value in sources.items():
        if not isinstance(source, str) or not source:
            continue
        try:
            count_value = int(raw_value)
        except Exception:
            continue
        ordered.append((source, count_value))
    ordered.sort(key=lambda item: (-item[1], item[0]))

if ordered:
    print("| Source | Count |")
    print("| --- | --- |")
    for source, value in ordered:
        print(f"| {source} | {value} |")
PY
)
  echo "History summary gating sources: ${GATING_SOURCES}"
  if [[ -n "${GATING_SOURCES_TABLE}" ]]; then
    printf '%s\n' "Streaming gating sources:"
    printf '%s\n' "${GATING_SOURCES_TABLE}"
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
  MARKER_PATH="${SUMMARY_DIR}/talon-export-marker.json"
  SCHEDULER_INFO=$(python3 scripts/tools/scheduler_source.py --summary "${SUMMARY_FILE}" --telemetry "${TELEMETRY_PATH}" --marker "${MARKER_PATH}")
  SCHEDULER_JSON=$(SCHEDULER_INFO_DATA="${SCHEDULER_INFO}" python3 - <<'PY'
import json, os

try:
    info = json.loads(os.environ.get("SCHEDULER_INFO_DATA") or "{}")
except json.JSONDecodeError:
    info = {}
stats = info.get("stats") or {}
print(json.dumps(stats, separators=(", ", ": ")))
PY
)
  SCHEDULER_LINES=$(SCHEDULER_INFO_DATA="${SCHEDULER_INFO}" python3 - <<'PY'
import datetime
import json
import os

try:
    info = json.loads(os.environ.get("SCHEDULER_INFO_DATA") or "{}")
except json.JSONDecodeError:
    info = {}
stats = info.get("stats") or {}
source = str(info.get("source") or "defaults")

threshold_env = os.environ.get("SCHEDULER_STALE_THRESHOLD_MINUTES")
try:
    stale_threshold = max(0, int(threshold_env))
except (TypeError, ValueError):
    stale_threshold = 360

now_override = os.environ.get("SCHEDULER_STALE_NOW")
if now_override:
    try:
        now = datetime.datetime.fromisoformat(now_override.replace("Z", "+00:00"))
        if now.tzinfo is None:
            now = now.replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
else:
    now = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

reschedule_raw = stats.get("reschedule_count")
if isinstance(reschedule_raw, bool):
    reschedules = 0
else:
    try:
        reschedules = int(reschedule_raw)
    except Exception:
        reschedules = 0

interval_raw = stats.get("last_interval_minutes")
if isinstance(interval_raw, bool):
    interval_text = "none"
elif isinstance(interval_raw, (int, float)):
    interval_text = str(int(interval_raw))
elif isinstance(interval_raw, str):
    interval_text = interval_raw.strip() or "none"
else:
    interval_text = "none"

reason_raw = stats.get("last_reason")
if isinstance(reason_raw, str):
    reason_text = reason_raw.strip() or "none"
else:
    reason_text = "none"

timestamp_raw = stats.get("last_timestamp")
timestamp_text = "none"
parsed_timestamp = None
if isinstance(timestamp_raw, str):
    stripped = timestamp_raw.strip()
    if stripped:
        timestamp_text = stripped
        try:
            parsed_timestamp = datetime.datetime.fromisoformat(stripped.replace("Z", "+00:00"))
            if parsed_timestamp.tzinfo is None:
                parsed_timestamp = parsed_timestamp.replace(tzinfo=datetime.timezone.utc)
        except ValueError:
            parsed_timestamp = None

if parsed_timestamp is not None:
    age_minutes = (now - parsed_timestamp).total_seconds() / 60.0
    is_stale = age_minutes > stale_threshold
else:
    is_stale = False

qualifiers = ["missing"] if source == "defaults" else []
if source != "defaults":
    qualifiers.append("non-default")
if is_stale:
    qualifiers.append("stale")
missing_scheduler = source == "defaults"
invalid_timestamp = timestamp_text != "none" and parsed_timestamp is None

if invalid_timestamp:
    qualifiers.append("invalid-timestamp")
suffix = f" ({', '.join(qualifiers)})" if qualifiers else ""
warnings = []
if source != "defaults" and qualifiers:
    warnings.append(
        f"WARNING: Scheduler telemetry uses {source}{suffix}; refresh Talon exports."
    )
elif source != "defaults":
    warnings.append(
        f"WARNING: Scheduler telemetry uses {source}; refresh Talon exports."
    )
if invalid_timestamp:
    warnings.append(
        f"WARNING: Scheduler telemetry timestamp '{timestamp_text}' could not be parsed; refresh Talon exports."
    )
if missing_scheduler:
    warnings.append(
        "WARNING: Scheduler telemetry missing; run `model export telemetry` inside Talon to populate stats."
    )

lines = [
    f"- Scheduler reschedules: {reschedules}",
    f"- Scheduler last interval (minutes): {interval_text}",
    f"- Scheduler last reason: {reason_text}",
    f"- Scheduler last timestamp: {timestamp_text}",
    f"- Scheduler data source: {source}{suffix}",
]
lines.extend(warnings)
print("\n".join(lines))
PY
)

  if [[ -n "${SCHEDULER_JSON}" ]]; then
    echo "Telemetry scheduler stats: ${SCHEDULER_JSON}"
    printf '%s\n' "${SCHEDULER_LINES}"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
      {
        echo
        echo "### Scheduler Telemetry"
        echo
        echo '```json'
        echo "${SCHEDULER_JSON}"
        echo '```'
        echo
        printf '%s\n' "${SCHEDULER_LINES}"
      } >> "${GITHUB_STEP_SUMMARY}"
    fi
  fi

  STREAK_LOG="${SUMMARY_DIR}/cli-warning-streak.json"
  STREAK_REPORT=$(python3 - "${STREAK_LOG}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    raw = json.loads(path.read_text(encoding="utf-8"))
except FileNotFoundError:
    raw = {}
except json.JSONDecodeError:
    raw = {}
if not isinstance(raw, dict):
    raw = {}
streak_value = raw.get("streak")
if isinstance(streak_value, bool):
    streak_value = int(streak_value)
try:
    streak = int(streak_value)
except Exception:
    streak = 0
reason_raw = raw.get("last_reason")
if isinstance(reason_raw, str):
    reason_text = reason_raw.strip() or "none"
else:
    reason_text = "none"
command_raw = raw.get("last_command")
if isinstance(command_raw, str):
    command_text = command_raw.strip() or "unknown"
else:
    command_text = "unknown"
updated_raw = raw.get("updated_at")
if isinstance(updated_raw, str):
    updated_text = updated_raw.strip() or "unknown"
else:
    updated_text = "unknown"
json_state = {
    "streak": streak,
    "last_reason": reason_raw if isinstance(reason_raw, str) else None,
    "last_command": command_raw if isinstance(command_raw, str) else None,
    "updated_at": updated_raw if isinstance(updated_raw, str) else None,
}
print(f"Telemetry export streak state: {json.dumps(json_state, separators=(', ', ': '))}")
print(f"- Telemetry export warning streak: {streak}")
print(f"- Telemetry export last reason: {reason_text}")
print(f"- Telemetry export last updated: {updated_text}")
print(f"- Telemetry export last command: {command_text}")
PY
)
  STREAK_ALERT=$(python3 - "${STREAK_LOG}" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
try:
    raw = json.loads(path.read_text(encoding="utf-8"))
except (FileNotFoundError, json.JSONDecodeError):
    raw = {}
if not isinstance(raw, dict):
    raw = {}
streak_value = raw.get("streak")
if isinstance(streak_value, bool):
    streak_value = int(streak_value)
try:
    streak = int(streak_value)
except Exception:
    streak = 0
reason_raw = raw.get("last_reason")
if isinstance(reason_raw, str):
    reason_text = reason_raw.strip() or "unknown"
else:
    reason_text = "unknown"
if streak > 0:
    print(f"{streak} consecutive warnings (reason: {reason_text})")
PY
)
  if [[ -n "${STREAK_ALERT}" ]]; then
    printf '%s\n' "- Streak alert: ${STREAK_ALERT}"
  fi
  printf '%s\n' "${STREAK_REPORT}"
  if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    {
      echo
      echo "### Telemetry Export Streak"
      echo
      if [[ -n "${STREAK_ALERT}" ]]; then
        echo "| Alert | Detail |"
        echo "| --- | --- |"
        echo "| Telemetry export streak | ${STREAK_ALERT} |"
        printf '%s\n' "- Streak alert: ${STREAK_ALERT}"
      fi
      printf '%s\n' "${STREAK_REPORT}"
    } >> "${GITHUB_STEP_SUMMARY}"
  fi

  STREAMING_LAST_OUTPUT=$(python3 - "${SUMMARY_FILE}" <<'PY'

import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
summary = data.get("streaming_gating_summary") or {}
message = str(summary.get("last_message") or "").strip().replace("\n", " ")
code = str(summary.get("last_code") or "").strip().replace("\n", " ")
if not message:
    message = "none"
sys.stdout.write(f"{message}\t{code}")
PY
)
  IFS=$'\t' read -r STREAMING_LAST_MESSAGE STREAMING_LAST_CODE <<<"${STREAMING_LAST_OUTPUT}"
  STREAMING_LAST_MESSAGE=${STREAMING_LAST_MESSAGE:-none}
  STREAMING_LAST_CODE=${STREAMING_LAST_CODE:-}
  if [[ -n "${STREAMING_LAST_CODE}" ]]; then
    STREAMING_LAST_SUMMARY="${STREAMING_LAST_MESSAGE} (code=${STREAMING_LAST_CODE})"
  else
    STREAMING_LAST_SUMMARY="${STREAMING_LAST_MESSAGE}"
  fi
  echo "Streaming gating last drop: ${STREAMING_LAST_SUMMARY}"

  SKIP_SUMMARY_PATH="${SUMMARY_DIR}/suggestion-skip-summary.json"
  if [[ ! -f "${SKIP_SUMMARY_PATH}" ]]; then
    python3 scripts/tools/suggestion-skip-export.py --output "${SKIP_SUMMARY_PATH}" --pretty
  fi
  SKIP_JSON=$(cat "${SKIP_SUMMARY_PATH}")
  echo "Suggestion skip summary (json): ${SKIP_JSON}"
  SKIP_TOTAL=$(python3 - "${SKIP_SUMMARY_PATH}" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
print(data.get("total_skipped", 0))
PY
)
  SKIP_REASONS=$(python3 - "${SKIP_SUMMARY_PATH}" <<'PY'
import json, sys
from pathlib import Path
path = Path(sys.argv[1])
try:
    data = json.loads(path.read_text())
except Exception:
    data = {}
reasons = data.get("reason_counts", [])
if not isinstance(reasons, list):
    reasons = []
formatted = []
for item in reasons:
    if not isinstance(item, dict):
        continue
    reason = item.get("reason")
    count = item.get("count")
    if isinstance(reason, str) and reason:
        try:
            formatted.append((reason, int(count)))
        except Exception:
            continue
if formatted:
    formatted.sort(key=lambda item: (-item[1], item[0]))
    print(", ".join(f"{reason}={count}" for reason, count in formatted))
else:
    print("none")
PY
 )
  echo "Suggestion skip total: ${SKIP_TOTAL}"
  echo "Suggestion skip reasons: ${SKIP_REASONS}"
 
  TELEMETRY_PATH="${SUMMARY_DIR}/history-validation-summary.telemetry.json"
  python3 scripts/tools/history-axis-export-telemetry.py "${SUMMARY_FILE}" --output "${TELEMETRY_PATH}" --top 5 --pretty --skip-summary "${SKIP_SUMMARY_PATH}"
  if [[ -f "${TELEMETRY_PATH}" ]]; then
    TELEMETRY_JSON=$(cat "${TELEMETRY_PATH}")
    echo "Telemetry summary saved at ${TELEMETRY_PATH}"
    echo "Telemetry summary (json): ${TELEMETRY_JSON}"
  else
    echo "Telemetry summary missing at ${TELEMETRY_PATH}; run the Talon telemetry exporter to populate it." >&2
  fi
 
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
        printf '%s\n' "- Download telemetry summary: [Telemetry payload](${ARTIFACT_URL})"
      else
        printf '%s\n' "- Download summary artifact: [History axis summary](${STREAMING_JSON_PATH})"
      fi
      printf '%s\n' "- guardrail target: ${TARGET}"
      printf '%s\n' "- Streaming JSON summary recorded at ${STREAMING_JSON_PATH}"
      printf '%s\n' "- Streaming gating summary (text): ${STREAMING_LINE}"
      printf '%s\n' "- streaming status: ${GATING_STATUS}"
      printf '%s\n' "- streaming last drop: ${STREAMING_LAST_SUMMARY}"
      printf '%s\n' "- last drop: ${GATING_LAST_SUMMARY}"
      printf '%s\n' "- total entries: ${TOTAL_ENTRIES:-unknown}"
      printf '%s\n' "- gating drops: ${GATING_DROPS:-unknown}"
      if [[ -n "${GATING_REASONS_TABLE}" ]]; then
        printf '%s\n' "Streaming gating reasons:"
        printf '%s\n' "${GATING_REASONS_TABLE}"
      else
        printf '%s\n' "- Streaming gating reasons: ${GATING_REASONS:-none}"
      fi
      if [[ -n "${GATING_SOURCES_TABLE}" ]]; then
        printf '%s\n' "Streaming gating sources:"
        printf '%s\n' "${GATING_SOURCES_TABLE}"
      fi
      printf '%s\n' "- suggestion skips total: ${SKIP_TOTAL}"
      if [[ "${SKIP_REASONS}" != "none" ]]; then
        printf '%s\n' "- suggestion skip reasons: ${SKIP_REASONS}"
      else
        printf '%s\n' "- suggestion skip reasons: none"
      fi
      printf '%s\n' "- Suggestion skip summary saved at ${SKIP_SUMMARY_PATH}"
      printf '%s\n' "- Telemetry summary saved at ${TELEMETRY_PATH}"
      printf '\n'
      printf '%s\n' "Streaming summary (json):"
      printf '```json\n%s\n```\n' "${STREAMING_JSON}"
      printf '%s\n' "Telemetry payload (json):"
      printf '```json\n%s\n```\n' "${TELEMETRY_JSON}"
      printf '%s\n' "Suggestion skip summary (json):"
      printf '```json\n%s\n```\n' "${SKIP_JSON}"
    } >> "${GITHUB_STEP_SUMMARY}"
  fi

elif [[ "${REQUIRE_SUMMARY}" == "true" ]]; then
  echo "History validation summary required for target ${TARGET} but not found at ${SUMMARY_FILE}" >&2
  exit 1
else
  echo "History validation summary not found at ${SUMMARY_FILE}; target ${TARGET} does not require it."
  echo "History summary not required for target ${TARGET}; no job summary entry created."
fi


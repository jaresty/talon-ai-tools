"""CLI health probe helpers."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from . import cliDelegation

_CLI_BINARY = Path("bin/bar")


def _run_health_command() -> subprocess.CompletedProcess[str]:
    """Execute the CLI health command."""

    return subprocess.run(
        [str(_CLI_BINARY), "--health"],
        capture_output=True,
        text=True,
        check=False,
    )


def probe_cli_health(*, source: str = "health_probe") -> bool:
    """Return True when the CLI health probe succeeds."""

    result = _run_health_command()
    if result.returncode != 0:
        reason = result.stderr.strip() or (
            f"CLI health probe failed with exit {result.returncode}"
        )
        cliDelegation.record_health_failure(reason, source=source)
        return False

    try:
        payload = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        cliDelegation.record_health_failure(
            f"CLI health returned invalid JSON ({exc})",
            source=source,
        )
        return False

    status = payload.get("status")
    if status != "ok":
        message = payload.get("message") or "unknown"
        cliDelegation.record_health_failure(
            f"CLI health status={status} message={message}",
            source=source,
        )
        return False

    cliDelegation.record_health_success(source=source)
    return True

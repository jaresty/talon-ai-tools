"""
When imported under `python -m unittest`, this delegates to `_tests/bootstrap.py`,
which configures sys.path and namespace packages so imports like
`from talon import actions` and `from talon_user.lib...` resolve against the
local stubs.

When Talon itself imports this module from the user directory, the `_tests`
package is not available, so we fall back to a no-op `bootstrap()` to avoid
import errors in the Talon runtime.
"""

from __future__ import annotations

import sys

_BOOTSTRAP_WARNINGS: list[str] = []


def get_bootstrap_warnings(*, clear: bool = False) -> list[str]:
    warnings = list(_BOOTSTRAP_WARNINGS)
    if clear:
        _BOOTSTRAP_WARNINGS.clear()
        try:
            from lib.bootstrapTelemetry import clear_bootstrap_warning_events
        except Exception:
            pass
        else:
            try:
                clear_bootstrap_warning_events()
            except Exception:
                pass
    return warnings


def _warn(message: str) -> None:
    _BOOTSTRAP_WARNINGS.append(message)
    try:
        from lib.bootstrapTelemetry import record_bootstrap_warning
    except Exception:
        record_bootstrap_warning = None
    if record_bootstrap_warning is not None:
        try:
            record_bootstrap_warning(message)
        except Exception:
            pass
    sys.stderr.write(f"bootstrap: {message}\n")
    try:
        from talon import actions
    except Exception:
        actions = None
    if actions is not None:
        try:
            actions.user.notify(message)
            return
        except Exception:
            pass
    try:
        from talon import app
    except Exception:
        app = None
    if app is not None:
        try:
            app.notify(message)
        except Exception:
            pass


def _maybe_install_cli() -> None:
    """Attempt to install the packaged CLI binary before delegation."""

    try:
        from scripts.tools.install_bar_cli import install_cli  # type: ignore
    except Exception as exc:  # pragma: no cover - import errors depend on env
        _warn(f"unable to import installer; falling back to go build ({exc})")
        return

    try:
        install_cli(quiet=True)
    except Exception as exc:  # pragma: no cover - depends on filesystem state
        _warn(
            "install failed; run `python3 scripts/tools/package_bar_cli.py --print-paths` "
            f"to rebuild packaged CLI (falling back to go build: {exc})"
        )
        return


def bootstrap() -> None:  # type: ignore[override]
    """Initialize test bootstrap (if available) and install the CLI binary."""

    try:
        from _tests.bootstrap import bootstrap as _bootstrap
    except ModuleNotFoundError:  # Talon runtime (no tests package)
        pass
    else:
        _bootstrap()

    _maybe_install_cli()

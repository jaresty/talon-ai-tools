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


def _maybe_install_cli() -> None:
    """Attempt to install the packaged CLI binary before delegation."""

    try:
        from scripts.tools.install_bar_cli import install_cli  # type: ignore
    except Exception:
        return

    try:
        install_cli(quiet=True)
    except Exception:
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

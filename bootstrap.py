"""Top-level test bootstrap for running unit tests outside the Talon runtime.

When imported under `python -m unittest`, this delegates to `_tests/bootstrap.py`,
which configures sys.path and namespace packages so imports like
`from talon import actions` and `from talon_user.lib...` resolve against the
local stubs.

When Talon itself imports this module from the user directory, the `_tests`
package is not available, so we fall back to a no-op `bootstrap()` to avoid
import errors in the Talon runtime.
"""

try:
    from _tests.bootstrap import bootstrap as _bootstrap
except ModuleNotFoundError:  # Talon runtime (no tests package)

    def bootstrap() -> None:  # type: ignore[override]
        return None

else:

    def bootstrap() -> None:
        _bootstrap()

"""Top-level test bootstrap for running unit tests outside the Talon runtime.

This delegates to `tests/bootstrap.py`, which configures sys.path and
namespace packages so imports like `from talon import actions` and
`from talon_user.lib...` resolve against the local stubs.
"""

from tests.bootstrap import bootstrap as _bootstrap


def bootstrap() -> None:
    _bootstrap()


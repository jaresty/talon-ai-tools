import unittest
from pathlib import Path
from typing import TYPE_CHECKING

try:
    from bootstrap import bootstrap
except ModuleNotFoundError:  # pragma: no cover - Talon runtime fallback
    bootstrap = None
else:  # pragma: no cover - executed in test harness
    bootstrap()

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "readme.md"
GO_MOD_PATH = REPO_ROOT / "go.mod"
INSTALL_SCRIPT_PATH = REPO_ROOT / "scripts" / "install-bar.sh"
APP_PATH = REPO_ROOT / "internal" / "barcli" / "app.go"


def declared_module_path() -> str:
    """Return the module path declared in go.mod, which is Go's canonical repo identity."""
    for line in GO_MOD_PATH.read_text(encoding="utf-8").splitlines():
        if line.startswith("module "):
            return line.split(maxsplit=1)[1].strip()
    raise AssertionError("go.mod does not declare a module path")


def github_slug(module: str) -> str:
    """Turn a module path into the "owner/repo" slug GitHub uses in clone and raw URLs."""
    return module.removeprefix("github.com/")

if bootstrap is not None:

    class PortablePromptGrammarCLIDocs(unittest.TestCase):
        def test_readme_covers_portable_cli_quickstart(self) -> None:
            content = README_PATH.read_text(encoding="utf-8")
            self.assertIn("Portable prompt grammar CLI", content)

            expectations = (
                "python3 -m prompts.export --output build/prompt-grammar.json",
                "bar help tokens",
                "bar build todo focus steps fog --json",
                'echo "Fix onboarding" | bar build todo focus steps fog persona=facilitator intent=coach',
            )

            for snippet in expectations:
                with self.subTest(snippet=snippet):
                    self.assertIn(snippet, content)

        def test_install_commands_match_declared_go_module(self) -> None:
            """Guardrail: `go install` only works when the README path equals go.mod's module path.

            Go rejects a module whose declared path differs from the URL path it fetched, so a
            README that advertises a different owner/repo than go.mod is not a typo — it is a
            broken install instruction.
            """
            module = declared_module_path()
            owner, repo = github_slug(module).split("/")[:2]
            content = README_PATH.read_text(encoding="utf-8")
            installer = INSTALL_SCRIPT_PATH.read_text(encoding="utf-8")
            app = APP_PATH.read_text(encoding="utf-8")

            self.assertIn(f"go install {module}/cmd/bar@latest", content)
            self.assertIn(f"raw.githubusercontent.com/{owner}/{repo}/main/scripts/install-bar.sh", content)
            self.assertIn(f'REPO="{owner}/{repo}"', installer)
            self.assertIn(f'return "{owner}"', app)
            self.assertIn(f'return "{repo}"', app)

            for source, text in (("readme.md", content), ("go.mod", GO_MOD_PATH.read_text(encoding="utf-8"))):
                self.assertNotIn("talonvoice", text, f"{source} still references the retired talonvoice repo path")
else:
    if not TYPE_CHECKING:

        class PortablePromptGrammarCLIDocs(unittest.TestCase):
            @unittest.skip("Test harness unavailable outside unittest runs")
            def test_placeholder(self) -> None:
                pass

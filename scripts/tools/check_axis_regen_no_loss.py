"""Guard: fail if the live axisConfig.py defines symbols the generated file omits.

Usage:
    python scripts/tools/check_axis_regen_no_loss.py <live> <generated>

Compares top-level public names (assignments, functions, classes) between the
live file and the freshly-generated file. If the live file defines anything the
generated file doesn't, the generator template is out of sync — exit non-zero
before the generated file overwrites the live one.

Imports and private names (starting with _) are excluded from the check.
"""

import ast
import sys


def toplevel_public_names(path: str) -> set[str]:
    source = open(path, encoding="utf-8").read()
    tree = ast.parse(source, filename=path)
    names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.add(node.name)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
                names.add(node.target.id)
    return names


def main() -> None:
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <live> <generated>", file=sys.stderr)
        sys.exit(2)

    live_path, gen_path = sys.argv[1], sys.argv[2]
    live_names = toplevel_public_names(live_path)
    gen_names = toplevel_public_names(gen_path)

    lost = sorted(live_names - gen_names)
    if lost:
        sys.exit(
            f"axis-regenerate-apply: regeneration would lose symbols present in {live_path}.\n"
            f"Update generate_axis_config.py to emit these, then retry:\n"
            + "".join(f"  - {name}\n" for name in lost)
        )


if __name__ == "__main__":
    main()

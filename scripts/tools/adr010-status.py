#!/usr/bin/env python3
"""
Summarise ADR-010-related churn × complexity hotspots from the latest scan.

Reads tmp/churn-scan/line-hotspots.json (produced by the churn-scan tools)
and prints the top nodes for the key ADR-010 files.
"""

from __future__ import annotations

import json
from pathlib import Path


ADR010_FILES = {
    "lib/staticPromptConfig.py",
    "lib/talonSettings.py",
    "lib/modelHelpGUI.py",
    "lib/modelPromptPatternGUI.py",
    "lib/modelPatternGUI.py",
    "GPT/gpt.py",
    "GPT/lists/staticPrompt.talon-list",
}


def main() -> None:
    path = Path("tmp/churn-scan/line-hotspots.json")
    if not path.is_file():
        raise SystemExit(
            "No churn scan found at tmp/churn-scan/line-hotspots.json; "
            "run `make churn-scan` first."
        )

    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])

    focus_nodes = [
        n for n in nodes if n.get("file") in ADR010_FILES
    ]
    focus_nodes.sort(key=lambda n: n.get("score", 0.0), reverse=True)

    since = data.get("since", "?")
    scope = ", ".join(data.get("scope", []))
    print(f"ADR-010 hotspots since {since} (scope: {scope}):\n")

    if not focus_nodes:
        print("No ADR-010-related nodes found in the current scan.")
        return

    for n in focus_nodes:
        file = n.get("file")
        symbol = n.get("symbolName")
        kind = n.get("nodeKind")
        start = n.get("nodeStartLine")
        score = n.get("score", 0.0)
        churn = n.get("totalChurn", 0)
        coord = n.get("totalCoordination", 0.0)
        avg_cx = n.get("avgComplexity", 0.0)
        print(
            f"- {file}:{start} {symbol} ({kind}) "
            f"score={score:.1f} churn={churn} coord={coord:.1f} avgCx={avg_cx:.1f}"
        )


if __name__ == "__main__":
    main()


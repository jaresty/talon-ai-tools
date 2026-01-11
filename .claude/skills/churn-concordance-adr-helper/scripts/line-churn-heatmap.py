#!/usr/bin/env python3
"""
Line‑level churn × complexity heatmap for this repo.

This is a lightweight Python replacement for the original Node-based
`line-churn-heatmap.mjs` used in other projects. It focuses on:

- Per-line churn from `git log -p`.
- A simple per-line complexity heuristic tailored to Python and Go sources.
- A coordination weight based on how many files change together in a commit.
- Language-aware node grouping for Python (`def`/`class`) and Go (`func`).

It writes a JSON report at `LINE_CHURN_OUTPUT` (default:
`tmp/churn-scan/line-hotspots.json`) that matches the schema expected by
`docs/adr/churn-concordance-adr-helper.md` closely enough for ADR work.

Environment variables:
    LINE_CHURN_SINCE   - git --since window (default: "90 days ago")
    LINE_CHURN_SCOPE   - comma-separated path prefixes
                          (default: "lib/,GPT/,copilot/,tests/")
    LINE_CHURN_LIMIT   - max nodes/lines to report (default: 200)
    LINE_CHURN_OUTPUT  - JSON output path
                          (default: "tmp/churn-scan/line-hotspots.json")
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass
class LineStat:
    churn: int = 0
    coordination_sum: float = 0.0


@dataclass
class NodeStat:
    file: str
    symbol_name: str
    node_kind: str
    node_start_line: int
    total_churn: int = 0
    total_coordination: float = 0.0
    complexity_sum: float = 0.0
    sample_lines: List[int] = field(default_factory=list)


def _env_default(name: str, default: str) -> str:
    value = os.environ.get(name)
    return value if value else default


def _parse_scope(scope_raw: str) -> List[str]:
    return [s.strip() for s in scope_raw.split(",") if s.strip()]


def _run_git_log_patch(since: str, scopes: Iterable[str]) -> Iterable[str]:
    args = [
        "git",
        "log",
        "--patch",
        "--unified=0",
        f"--since={since}",
        "--date=iso",
        "--no-color",
        "--reverse",
        "--format=commit %H",
    ]
    scopes = list(scopes)
    if scopes:
        args.append("--")
        args.extend(scopes)

    proc = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        yield line.rstrip("\n")

    _, stderr = proc.communicate()
    if proc.returncode != 0:
        raise SystemExit(f"git log -p failed with code {proc.returncode}:\n{stderr}")


def _complexity_for_line(line: str, suffix: str) -> float:
    """Very small heuristic: count control-flow-ish keywords."""
    stripped = line.strip()
    if not stripped:
        return 0.5

    lowered = stripped.lower()
    if stripped.startswith(("'''", '"""')):
        return 0.5
    if lowered.startswith("#") or lowered.startswith("//") or lowered.startswith("/*"):
        return 0.5

    keywords = [
        "if ",
        "elif ",
        "else:",
        "for ",
        "while ",
        "try:",
        "except ",
        "with ",
        "match ",
        "case ",
        " and ",
        " or ",
    ]
    if suffix == ".go":
        keywords.extend(
            [
                "switch ",
                "select ",
                "defer ",
                "go ",
                "range ",
                " default:",
                " && ",
                " || ",
            ]
        )

    score = 1.0
    for kw in keywords:
        if kw in lowered:
            score += 1.0
    if suffix == ".go" and lowered.endswith("{"):
        score += 0.5
    return score


def _build_line_stats(
    since: str, scopes: Iterable[str]
) -> Tuple[Dict[Tuple[str, int], LineStat], Dict[str, Dict[int, float]]]:
    """
    Parse `git log -p` output and accumulate line-level churn and coordination.

    Returns:
        line_stats: (file, line) -> LineStat
        file_line_complexity: file -> { line -> complexity }
    """
    line_stats: Dict[Tuple[str, int], LineStat] = defaultdict(LineStat)

    current_commit = None
    files_in_commit: set[str] = set()
    additions_in_commit: List[Tuple[str, int]] = []

    current_file: str | None = None
    new_line_no = 0

    commit_header_re = re.compile(r"^commit ([0-9a-f]{7,40})$")
    diff_header_re = re.compile(r"^diff --git a/(.+?) b/(.+)$")
    hunk_header_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

    def flush_commit() -> None:
        nonlocal additions_in_commit, files_in_commit
        if not additions_in_commit:
            files_in_commit.clear()
            return
        coordination = float(len(files_in_commit)) or 1.0
        for file_path, line_no in additions_in_commit:
            stat = line_stats[(file_path, line_no)]
            stat.churn += 1
            stat.coordination_sum += coordination
        additions_in_commit = []
        files_in_commit = set()

    for raw_line in _run_git_log_patch(since, scopes):
        if not raw_line:
            continue

        m_commit = commit_header_re.match(raw_line)
        if m_commit:
            # New commit boundary.
            flush_commit()
            current_commit = m_commit.group(1)
            current_file = None
            new_line_no = 0
            continue

        m_diff = diff_header_re.match(raw_line)
        if m_diff:
            matched_file = m_diff.group(2)
            if matched_file is None:
                current_file = None
                continue
            current_file = matched_file
            files_in_commit.add(matched_file)
            new_line_no = 0
            continue

        m_hunk = hunk_header_re.match(raw_line)
        if m_hunk:
            new_line_no = int(m_hunk.group(1))
            continue

        if current_file is None or new_line_no == 0:
            continue

        # Patch body lines
        prefix = raw_line[0]
        if prefix == "+" and not raw_line.startswith("+++"):
            additions_in_commit.append((current_file, new_line_no))
            new_line_no += 1
        elif prefix == "-" and not raw_line.startswith("---"):
            # deletion: only advance old line number (not tracked)
            continue
        else:
            # context
            new_line_no += 1

    # Flush last commit
    flush_commit()

    # Pre-compute complexity per file/line for files that appear in stats.
    files = {file for (file, _line) in line_stats.keys()}
    file_line_complexity: Dict[str, Dict[int, float]] = {}
    for file in files:
        path = Path(file)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        per_line: Dict[int, float] = {}
        suffix = path.suffix.lower()
        for idx, line in enumerate(text.splitlines(), start=1):
            per_line[idx] = _complexity_for_line(line, suffix)
        file_line_complexity[file] = per_line

    return line_stats, file_line_complexity


def _build_nodes(
    line_stats: Dict[Tuple[str, int], LineStat],
    file_line_complexity: Dict[str, Dict[int, float]],
) -> List[NodeStat]:
    # Map each (file, line) to a simple "node" representing the nearest
    # language construct (Python def/class or Go func), or a file-level fallback.
    nodes: Dict[Tuple[str, int], NodeStat] = {}

    go_func_re = re.compile(
        r"^func\s*(?:\((?P<receiver>[^)]+)\)\s*)?(?P<name>[A-Za-z0-9_]+)"
    )

    file_nodes_boundaries: Dict[str, List[Tuple[int, str, str]]] = {}
    for file in {f for (f, _l) in line_stats.keys()}:
        path = Path(file)
        boundaries: List[Tuple[int, str, str]] = [(1, "File", path.name)]
        suffix = path.suffix.lower()
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            file_nodes_boundaries[file] = boundaries
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("def ") or stripped.startswith("class "):
                # Approximate symbol name.
                name = stripped.split()[1].split("(")[0].split(":")[0]
                node_kind = "Function" if stripped.startswith("def ") else "Class"
                boundaries.append((idx, node_kind, name))
            elif suffix == ".go" and stripped.startswith("func"):
                match = go_func_re.match(stripped)
                if not match:
                    continue
                name = match.group("name")
                if not name:
                    continue
                receiver = match.group("receiver")
                node_kind = "Method" if receiver else "Function"
                boundaries.append((idx, node_kind, name))
        file_nodes_boundaries[file] = sorted(boundaries, key=lambda t: t[0])

    for (file, line_no), stat in line_stats.items():
        per_line_complexity = file_line_complexity.get(file, {})
        complexity = per_line_complexity.get(line_no, 1.0)

        existing_boundaries = file_nodes_boundaries.get(file)
        if existing_boundaries:
            boundaries: List[Tuple[int, str, str]] = existing_boundaries
        else:
            boundaries = [(1, "File", Path(file).name)]
        # Nearest boundary whose start <= line_no.
        node_start, node_kind, symbol_name = boundaries[0]
        for start, boundary_kind, name in boundaries:
            if start <= line_no:
                node_start, node_kind, symbol_name = start, boundary_kind, name
            else:
                break

        key = (file, node_start)
        node = nodes.get(key)
        if node is None:
            node = NodeStat(
                file=file,
                symbol_name=symbol_name,
                node_kind=node_kind,
                node_start_line=node_start,
            )
            nodes[key] = node

        node.total_churn += stat.churn
        node.total_coordination += stat.coordination_sum
        node.complexity_sum += complexity * stat.churn
        if len(node.sample_lines) < 5:
            node.sample_lines.append(line_no)

    return list(nodes.values())


def _to_json(
    since: str,
    scopes: List[str],
    limit: int,
    line_stats: Dict[Tuple[str, int], LineStat],
    file_line_complexity: Dict[str, Dict[int, float]],
    nodes: List[NodeStat],
) -> dict:
    # Per-line entries
    lines_payload: List[dict] = []
    for (file, line_no), stat in line_stats.items():
        avg_coord = stat.coordination_sum / stat.churn if stat.churn else 0.0
        complexity = file_line_complexity.get(file, {}).get(line_no, 1.0)
        score = stat.churn * complexity * (avg_coord or 1.0)
        lines_payload.append(
            {
                "file": file,
                "line": line_no,
                "churn": stat.churn,
                "complexity": complexity,
                "coordination": avg_coord,
                "score": score,
            }
        )

    lines_payload.sort(key=lambda x: x["score"], reverse=True)
    lines_payload = lines_payload[:limit]

    # Node entries
    nodes_payload: List[dict] = []
    for node in nodes:
        if node.total_churn == 0:
            continue
        avg_coord = node.total_coordination / node.total_churn
        avg_complexity = node.complexity_sum / node.total_churn
        score = node.total_churn * avg_complexity * (avg_coord or 1.0)
        nodes_payload.append(
            {
                "file": node.file,
                "symbolName": node.symbol_name,
                "role": "",
                "nodeKind": node.node_kind,
                "nodeStartLine": node.node_start_line,
                "totalChurn": node.total_churn,
                "totalCoordination": node.total_coordination,
                "avgComplexity": avg_complexity,
                "score": score,
                "sampleLines": sorted(node.sample_lines),
                "episodes": [],
            }
        )

    nodes_payload.sort(key=lambda x: x["score"], reverse=True)
    nodes_payload = nodes_payload[:limit]

    return {
        "since": since,
        "scope": scopes,
        "limit": limit,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "lines": lines_payload,
        "nodes": nodes_payload,
    }


def main() -> None:
    since = _env_default("LINE_CHURN_SINCE", "90 days ago")
    scope_raw = _env_default(
        "LINE_CHURN_SCOPE",
        "lib/,GPT/,copilot/,tests/",
    )
    scopes = _parse_scope(scope_raw)
    limit_str = _env_default("LINE_CHURN_LIMIT", "200")
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 200

    line_stats, file_line_complexity = _build_line_stats(since, scopes)
    nodes = _build_nodes(line_stats, file_line_complexity)
    payload = _to_json(since, scopes, limit, line_stats, file_line_complexity, nodes)

    output_path = Path(
        _env_default("LINE_CHURN_OUTPUT", "tmp/churn-scan/line-hotspots.json")
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote line churn heatmap to {output_path}")


if __name__ == "__main__":
    main()

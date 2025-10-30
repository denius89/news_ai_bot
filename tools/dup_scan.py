#!/usr/bin/env python3
"""
Duplication Scanner (AST-based, lightweight)

Purpose:
- Scan Python files for similar function implementations
- Compute token-level Jaccard similarity for function bodies
- Emit JSON report to reports/duplications.json

Notes:
- Read-only; no code changes performed
- Threshold is conservative (default 0.8)
- Skips vendor/venv/logs/tests by default

Usage:
    python3 tools/dup_scan.py [--threshold 0.8]
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

# Exclude directories
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "logs",
    "node_modules",
}

# File name patterns to skip
SKIP_FILE_REGEX = re.compile(r"(test_|_test\.py$)")

TOKEN_REGEX = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|\+|\-|\*|/|%|\(|\)|\[|\]|\{|\}|\.|")


@dataclass
class FunctionInfo:
    file: str
    name: str
    qualname: str
    lineno: int
    tokens: Set[str]
    token_count: int
    hash: str


def tokenize_source(source: str) -> List[str]:
    return TOKEN_REGEX.findall(source)


class FuncVisitor(ast.NodeVisitor):
    def __init__(self, file_path: Path, source_lines: List[str]) -> None:
        self.file_path = file_path
        self.source_lines = source_lines
        self.funcs: List[FunctionInfo] = []
        self.scope: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore
        self._handle_func(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore
        self._handle_func(node)
        self.generic_visit(node)

    def _handle_func(self, node: ast.AST) -> None:
        # Best-effort to extract function source
        try:
            start = getattr(node, "lineno", None)
            end = getattr(node, "end_lineno", None)
            if start is None or end is None:
                return
            snippet = "\n".join(self.source_lines[start - 1 : end])
        except Exception:
            return

        tokens = tokenize_source(snippet)
        token_set = set(tokens)
        token_hash = hashlib.sha1(" ".join(tokens).encode("utf-8")).hexdigest()

        qual = ".".join(self.scope + [getattr(node, "name", "<anon>")])
        self.funcs.append(
            FunctionInfo(
                file=str(self.file_path),
                name=getattr(node, "name", "<anon>"),
                qualname=qual,
                lineno=getattr(node, "lineno", 0),
                tokens=token_set,
                token_count=len(tokens),
                hash=token_hash,
            )
        )


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def collect_functions(project_root: Path) -> List[FunctionInfo]:
    results: List[FunctionInfo] = []

    for py in project_root.rglob("*.py"):
        rel = py.relative_to(project_root)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if SKIP_FILE_REGEX.search(str(rel)):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        visitor = FuncVisitor(py, src.splitlines())
        visitor.visit(tree)
        results.extend(visitor.funcs)
    return results


def find_duplicates(funcs: List[FunctionInfo], threshold: float) -> List[Dict[str, object]]:
    # Quick bucket by token_count window to reduce comparisons
    buckets: Dict[int, List[FunctionInfo]] = {}
    for f in funcs:
        buckets.setdefault(f.token_count // 20, []).append(f)

    duplicates: List[Dict[str, object]] = []
    seen_pairs: Set[Tuple[str, str, int, int]] = set()

    def add_pair(a: FunctionInfo, b: FunctionInfo, score: float) -> None:
        key = tuple(sorted([(a.file, a.qualname, a.lineno), (b.file, b.qualname, b.lineno)]))
        if key in seen_pairs:
            return
        seen_pairs.add(key)
        duplicates.append(
            {
                "score": round(score, 3),
                "a": {"file": a.file, "func": a.qualname, "line": a.lineno, "tokens": a.token_count},
                "b": {"file": b.file, "func": b.qualname, "line": b.lineno, "tokens": b.token_count},
            }
        )

    for _, group in buckets.items():
        n = len(group)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = group[i], group[j]
                # Fast prefilter: identical hashes
                if a.hash == b.hash:
                    add_pair(a, b, 1.0)
                    continue
                # Token-count sanity check (within ~25%)
                if not (0.75 <= (min(a.token_count, b.token_count) / max(a.token_count, b.token_count)) <= 1.25):
                    continue
                score = jaccard(a.tokens, b.tokens)
                if score >= threshold:
                    add_pair(a, b, score)

    duplicates.sort(key=lambda x: (-x["score"], x["a"]["file"]))
    return duplicates


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=0.8, help="Similarity threshold (0..1)")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    funcs = collect_functions(project_root)
    dups = find_duplicates(funcs, threshold=args.threshold)

    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "duplications.json"

    out = {
        "summary": {
            "threshold": args.threshold,
            "functions_scanned": len(funcs),
            "pairs_detected": len(dups),
        },
        "duplicates": dups,
    }

    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Duplications report: {out_file}")


if __name__ == "__main__":
    main()

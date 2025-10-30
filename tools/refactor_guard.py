#!/usr/bin/env python3
"""
Refactor Guard

Purpose:
- Snapshot and check stability of public APIs annotated with @public_api

Commands:
    --snapshot            Create/overwrite snapshot of public_api signatures
    --check public_api    Validate current signatures against snapshot

Snapshot file:
    reports/public_api_snapshot.json

Exit codes:
    0 = ok
    1 = violations found / error
"""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional


SNAPSHOT_PATH = Path(__file__).resolve().parents[1] / "reports" / "public_api_snapshot.json"
PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ApiSymbol:
    module: str
    qualname: str
    kind: str  # function|method|class
    args: List[str]
    defaults: int


class ApiVisitor(ast.NodeVisitor):
    def __init__(self, module_path: str) -> None:
        self.module_path = module_path
        self.stack: List[str] = []
        self.symbols: List[ApiSymbol] = []

    def _is_public_api(self, node: ast.AST) -> bool:
        decorators = getattr(node, "decorator_list", [])
        for d in decorators:
            name = None
            if isinstance(d, ast.Name):
                name = d.id
            elif isinstance(d, ast.Attribute):
                name = d.attr
            elif isinstance(d, ast.Call):
                if isinstance(d.func, ast.Name):
                    name = d.func.id
                elif isinstance(d.func, ast.Attribute):
                    name = d.func.attr
            if name == "public_api":
                return True
        return False

    def _collect_args(self, node: ast.AST) -> tuple[list[str], int]:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return [], 0
        a = node.args
        names: List[str] = []
        defaults_count = len(a.defaults) + len(a.kw_defaults) if a.kw_defaults else len(a.defaults)
        for arg in list(a.posonlyargs) + list(a.args):
            names.append(arg.arg)
        if a.vararg:
            names.append("*" + a.vararg.arg)
        for kw in a.kwonlyargs:
            names.append(kw.arg)
        if a.kwarg:
            names.append("**" + a.kwarg.arg)
        return names, defaults_count

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # type: ignore
        self.stack.append(node.name)
        if self._is_public_api(node):
            qual = ".".join(self.stack)
            self.symbols.append(ApiSymbol(module=self.module_path, qualname=qual, kind="class", args=[], defaults=0))
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Methods
                if self._is_public_api(stmt):
                    qual = ".".join(self.stack + [stmt.name])
                    args, defaults = self._collect_args(stmt)
                    self.symbols.append(
                        ApiSymbol(module=self.module_path, qualname=qual, kind="method", args=args, defaults=defaults)
                    )
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # type: ignore
        if self._is_public_api(node):
            qual = ".".join(self.stack + [node.name])
            args, defaults = self._collect_args(node)
            self.symbols.append(
                ApiSymbol(module=self.module_path, qualname=qual, kind="function", args=args, defaults=defaults)
            )
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # type: ignore
        return self.visit_FunctionDef(node)  # type: ignore


def discover_public_api(project_root: Path) -> List[ApiSymbol]:
    symbols: List[ApiSymbol] = []
    for py in project_root.rglob("*.py"):
        rel = py.relative_to(project_root)
        parts = rel.parts
        if any(p in {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "logs"} for p in parts):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
        except Exception:
            continue
        module = str(rel).replace("/", ".")
        visitor = ApiVisitor(module)
        visitor.visit(tree)
        symbols.extend(visitor.symbols)
    return symbols


def load_snapshot(path: Path) -> Dict[str, Dict[str, object]]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {k: v for k, v in data.items()}
    except Exception:
        return {}


def save_snapshot(path: Path, symbols: List[ApiSymbol]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {f"{s.module}:{s.qualname}": asdict(s) for s in symbols}
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def check_public_api(path: Path, symbols: List[ApiSymbol]) -> List[dict]:
    snap = load_snapshot(path)
    problems: List[dict] = []
    current = {f"{s.module}:{s.qualname}": s for s in symbols}

    # Removed or changed
    for key, snap_entry in snap.items():
        cur = current.get(key)
        if cur is None:
            problems.append({"type": "removed", "symbol": key})
            continue
        # Compare signature
        if snap_entry.get("args") != cur.args or snap_entry.get("kind") != cur.kind:
            problems.append(
                {
                    "type": "changed_signature",
                    "symbol": key,
                    "was": {"args": snap_entry.get("args"), "kind": snap_entry.get("kind")},
                    "now": {"args": cur.args, "kind": cur.kind},
                }
            )

    # Added new public APIs (informational)
    for key in current.keys() - snap.keys():
        problems.append({"type": "added", "symbol": key})

    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", action="store_true", help="Create/overwrite snapshot")
    parser.add_argument("--check", choices=["public_api"], help="Run guard checks")
    args = parser.parse_args()

    symbols = discover_public_api(PROJECT_ROOT)

    if args.snapshot:
        save_snapshot(SNAPSHOT_PATH, symbols)
        print(f"✅ Snapshot saved: {SNAPSHOT_PATH}")
        return 0

    if args.check == "public_api":
        problems = check_public_api(SNAPSHOT_PATH, symbols)
        if problems:
            report_path = SNAPSHOT_PATH.parent / "public_api_violations.json"
            report_path.write_text(json.dumps(problems, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"❌ Public API violations: {len(problems)} (see {report_path})")
            # Treat added as warning; removals/changes as error
            has_error = any(p["type"] in {"removed", "changed_signature"} for p in problems)
            return 1 if has_error else 0
        print("✅ Public API check passed")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Docstring Sync

Reports Python modules without a module-level docstring.
Optionally can add a minimal docstring header for specific files.

Usage:
  - Report only (default):
        python3 tools/docstring_sync.py
  - Apply to selected files:
        python3 tools/docstring_sync.py --apply path1.py path2.py
"""

from __future__ import annotations

import argparse
import ast
from pathlib import Path
from typing import List


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def find_modules_without_docstring(root: Path) -> List[Path]:
    missing: List[Path] = []
    for py in root.rglob("*.py"):
        rel = py.relative_to(root)
        if any(p in {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "logs"} for p in rel.parts):
            continue
        try:
            src = py.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
        except Exception:
            continue
        if not ast.get_docstring(tree):
            missing.append(py)
    return missing


def apply_docstring_header(targets: List[Path]) -> None:
    header_tpl = '"""\nModule: {name}\n"""\n\n'
    for t in targets:
        try:
            src = t.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(src)
            if ast.get_docstring(tree):
                continue
            new_src = header_tpl.format(name=t.name) + src
            t.write_text(new_src, encoding="utf-8")
            print(f"✅ Docstring added: {t}")
        except Exception as e:
            print(f"⚠️  Skip {t}: {e}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", nargs="*", help="Add docstring header to given files")
    args = parser.parse_args()

    if args.apply is not None and len(args.apply) > 0:
        targets = [Path(p).resolve() if Path(p).is_absolute() else PROJECT_ROOT / p for p in args.apply]
        apply_docstring_header(targets)
        return 0

    missing = find_modules_without_docstring(PROJECT_ROOT)
    if not missing:
        print("✅ All modules have docstrings (module-level)")
        return 0
    print("❗ Modules without module-level docstring:")
    for m in missing[:200]:
        print(f" - {m.relative_to(PROJECT_ROOT)}")
    if len(missing) > 200:
        print(f" ... and {len(missing) - 200} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

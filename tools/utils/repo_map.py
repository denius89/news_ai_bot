#!/usr/bin/env python3

"""
Генератор CODEMAP.md — структуры проекта.
"""

from datetime import datetime
from pathlib import Path

# Исключённые директории
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "prompts",
    "utils",
}

# Исключённые файлы
EXCLUDE_FILES = {".DS_Store", ".env"}

# Директории, куда заходим, но не рекурсируем
STOP_RECURSE_DIRS = {"logs"}


def build_tree(root: Path, prefix: str = "") -> list[str]:
    """Строит список строк с древовидной структурой проекта."""
    dirs = []
    files = []
    for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if p.is_dir():
            if p.name in EXCLUDED_DIRS:
                continue
            dirs.append(p)
        else:
            if p.name in EXCLUDE_FILES:
                continue
            files.append(p)

    entries = dirs + files
    lines: list[str] = []

    for idx, p in enumerate(entries):
        last = idx == len(entries) - 1
        connector = "└── " if last else "├── "

        if p.is_dir():
            lines.append(f"{prefix}{connector}{p.name}/")
            if p.name in STOP_RECURSE_DIRS:
                continue
            extension = "    " if last else "│   "
            lines.extend(build_tree(p, prefix + extension))
        else:
            lines.append(f"{prefix}{connector}{p.name}")

    return lines


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    lines = build_tree(project_root)
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    out = project_root / "CODEMAP.md"

    with out.open("w", encoding="utf-8") as f:
        f.write("# 📂 Project Structure\n\n")
        f.write(f"_Generated on {ts}_\n\n")
        f.write("```\n")
        f.write("\n".join(lines))
        f.write("\n```\n")

    print("✅ CODEMAP.md updated")


if __name__ == "__main__":
    main()

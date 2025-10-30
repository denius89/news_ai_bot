#!/usr/bin/env python3

"""
Генератор репортов по репозиторию:

- CODEMAP.md (корень и docs/)
- ARCHITECTURE.md (docs/)
- ROADMAP.md (docs/)
- architecture.json (корень)

Цель — только чтение файлов, без изменения зависимостей.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import re
from typing import Dict, List, Set, Tuple

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


# Слои проекта (верхнеуровневые директории)
LAYER_DIRS: List[str] = [
    "ai_modules",
    "digests",
    "parsers",
    "database",
    "routes",
    "webapp",
    "tools",
]


def detect_layer(module_or_path: str) -> str:
    """Возвращает имя слоя по имени модуля или относительному пути."""
    for layer in LAYER_DIRS:
        if module_or_path.startswith(layer):
            return layer
    return "other"


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


IMPORT_RE = re.compile(r"^\s*(from\s+([\w\.]+)\s+import|import\s+([\w\.]+))")


def scan_imports(project_root: Path) -> Dict[str, Set[str]]:
    """Грубый анализ импортов между верхнеуровневыми пакетами.

    Возвращает граф зависимостей между слоями: {src_layer: {dst_layer, ...}}
    """
    deps: Dict[str, Set[str]] = {layer: set() for layer in LAYER_DIRS + ["other"]}

    for py_file in project_root.rglob("*.py"):
        # Пропускаем скрытые/исключённые пути
        parts = py_file.relative_to(project_root).parts
        if any(part in EXCLUDED_DIRS for part in parts):
            continue
        if any(part in STOP_RECURSE_DIRS for part in parts):
            continue

        src_layer = detect_layer(parts[0]) if parts else "other"

        try:
            content = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for line in content.splitlines():
            m = IMPORT_RE.match(line)
            if not m:
                continue
            target = (m.group(2) or m.group(3) or "").split(".")[0]
            if not target:
                continue
            dst_layer = detect_layer(target)
            if dst_layer and dst_layer != src_layer:
                deps.setdefault(src_layer, set()).add(dst_layer)

    return deps


def write_architecture_json(project_root: Path, deps: Dict[str, Set[str]]) -> None:
    data = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "layers": LAYER_DIRS + ["other"],
        "dependencies": {k: sorted(list(v)) for k, v in deps.items()},
    }
    (project_root / "architecture.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_docs(project_root: Path, tree_lines: List[str], deps: Dict[str, Set[str]]) -> None:
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1) CODEMAP.md в корне (сохранить существующее поведение)
    out_root = project_root / "CODEMAP.md"
    out_root.write_text(
        "# 📂 Project Structure\n\n" f"_Generated on {ts}_\n\n" "```\n" + "\n".join(tree_lines) + "\n```\n",
        encoding="utf-8",
    )

    # 2) CODEMAP.md в docs/
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    (docs_dir / "CODEMAP.md").write_text(
        "# 📂 Project Structure\n\n" f"_Generated on {ts}_\n\n" "```\n" + "\n".join(tree_lines) + "\n```\n",
        encoding="utf-8",
    )

    # 3) ARCHITECTURE.md в docs/
    arch_md = [
        "# 🧱 Architecture Overview",
        "",
        f"_Generated on {ts}_",
        "",
        "## Layers",
        "",
        "- ai_modules",
        "- digests",
        "- parsers",
        "- database",
        "- routes",
        "- webapp",
        "- tools",
        "",
        "## Dependency Graph (by imports)",
        "",
    ]
    for src in LAYER_DIRS + ["other"]:
        targets = sorted(deps.get(src, set()))
        arch_md.append(f"- {src} → {', '.join(targets) if targets else '—'}")
    arch_md.append("")
    arch_md.append("> Rule: no cross-layer violations beyond documented flows.")
    (docs_dir / "ARCHITECTURE.md").write_text("\n".join(arch_md) + "\n", encoding="utf-8")

    # 4) ROADMAP.md в docs/
    roadmap = [
        "# 🗺️ Technical Roadmap (Auto‑generated seed)",
        "",
        f"_Generated on {ts}_",
        "",
        "## Suggested Next Steps",
        "- Add duplication scan and refactor guardrails (see plan)",
        "- Ensure test coverage for changed modules",
        "- Monitor /metrics and enforce thresholds",
        "",
        "## Known Risks",
        "- Cross-layer imports may exist in legacy modules",
        "- Tight coupling between digests and ai_modules",
    ]
    (docs_dir / "ROADMAP.md").write_text("\n".join(roadmap) + "\n", encoding="utf-8")


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    tree_lines = build_tree(project_root)
    deps = scan_imports(project_root)
    write_architecture_json(project_root, deps)
    write_docs(project_root, tree_lines, deps)
    print("✅ CODEMAP.md, docs/* and architecture.json updated")


if __name__ == "__main__":
    main()

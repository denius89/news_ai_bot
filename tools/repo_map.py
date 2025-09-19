#!/usr/bin/env python3
import os

OUTPUT_FILE = "CODEMAP.md"
EXCLUDE = {".git", "venv", "__pycache__", "logs", ".pytest_cache"}

def build_tree(root_dir, prefix=""):
    entries = []
    try:
        entries = sorted(os.listdir(root_dir))
    except PermissionError:
        return []

    tree = []
    for i, entry in enumerate(entries):
        if entry in EXCLUDE:
            continue
        path = os.path.join(root_dir, entry)
        connector = "└── " if i == len(entries) - 1 else "├── "
        if os.path.isdir(path):
            tree.append(prefix + connector + entry + "/")
            extension = "    " if i == len(entries) - 1 else "│   "
            tree.extend(build_tree(path, prefix + extension))
        else:
            tree.append(prefix + connector + entry)
    return tree

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tree = build_tree(project_root)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# 📂 Project Structure\n\n")
        f.write("```\n")
        f.write("\n".join(tree))
        f.write("\n```\n")
    print(f"✅ {OUTPUT_FILE} updated")

import os

# Папки и файлы, которые нужно исключать
EXCLUDE_DIRS = {'.git', '.venv', 'logs', '__pycache__', 'prompts', 'utils'}
EXCLUDE_FILES = {'.DS_Store', '.env', '.gitignore'}

def generate_tree(start_path='.', indent=''):
    entries = sorted(os.listdir(start_path))
    tree_lines = []

    for entry in entries:
        path = os.path.join(start_path, entry)

        # Пропускаем лишние файлы и папки
        if entry in EXCLUDE_FILES:
            continue
        if os.path.isdir(path) and entry in EXCLUDE_DIRS:
            continue

        if os.path.isdir(path):
            tree_lines.append(f"{indent}├── {entry}/")
            tree_lines.extend(generate_tree(path, indent + "│   "))
        else:
            tree_lines.append(f"{indent}├── {entry}")

    return tree_lines

def save_codemap(output_file="CODEMAP.md"):
    tree = generate_tree('.')
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Project Structure\n\n")
        f.write("```\n")
        f.write("\n".join(tree))
        f.write("\n```\n")

if __name__ == "__main__":
    save_codemap()
    print("✅ CODEMAP.md updated")
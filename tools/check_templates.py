#!/usr/bin/env python3
"""
PulseAI Template Consistency Checker
Проверяет, что все шаблоны правильно используют includes и base.html
"""

import os
import re
from pathlib import Path


def check_templates():
    """Проверяет консистентность шаблонов."""
    templates_dir = Path("templates")
    issues = []

    # Найти все HTML шаблоны
    html_files = list(templates_dir.rglob("*.html"))

    for html_file in html_files:
        print(f"Проверяю {html_file}...")

        try:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            issues.append(f"❌ {html_file}: Ошибка чтения - {e}")
            continue

        # Проверки
        checks = [check_doctype, check_includes, check_base_extend, check_inline_styles, check_meta_tags]

        for check_func in checks:
            result = check_func(html_file, content)
            if result:
                issues.append(result)

    # Отчёт
    print("\n" + "=" * 60)
    print("📊 ОТЧЁТ ПРОВЕРКИ ШАБЛОНОВ")
    print("=" * 60)

    if issues:
        print(f"❌ Найдено {len(issues)} проблем:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("✅ Все шаблоны соответствуют стандартам!")

    return len(issues) == 0


def check_doctype(file_path, content):
    """Проверяет наличие DOCTYPE."""
    # Includes и component файлы не должны иметь DOCTYPE
    parts = file_path.parts
    if len(parts) >= 2 and parts[-2] == "includes":
        return None
    if len(parts) >= 3 and parts[-3] == "components":
        return None

    if not content.strip().startswith("<!DOCTYPE html>"):
        return f"❌ {file_path}: Отсутствует <!DOCTYPE html>"
    return None


def check_includes(file_path, content):
    """Проверяет использование includes."""
    # Includes файлы не проверяем
    parts = file_path.parts
    if len(parts) >= 2 and parts[-2] == "includes":
        return None
    if len(parts) >= 3 and parts[-3] == "components":
        return None

    if file_path.name == "base.html":
        return None  # base.html не должен включать сам себя

    if file_path.name == "webapp.html":
        # WebApp использует свой includes
        if "{% include 'includes/webapp_head.html' %}" not in content:
            return f"❌ {file_path}: Должен использовать includes/webapp_head.html"
        return None

    # Обычные шаблоны должны использовать base.html
    if '{% extends "base.html" %}' in content:
        # Если наследуется от base.html, includes подключается автоматически
        return None
    elif "{% extends" in content:
        if "{% include 'includes/head.html' %}" not in content:
            return f"❌ {file_path}: Должен включать includes/head.html через base.html"

    return None


def check_base_extend(file_path, content):
    """Проверяет наследование от base.html."""
    # Includes и component файлы не должны наследоваться
    parts = file_path.parts
    if len(parts) >= 2 and parts[-2] == "includes":
        return None
    if len(parts) >= 3 and parts[-3] == "components":
        return None

    if file_path.name in ["base.html", "webapp.html"]:
        return None  # Эти файлы не наследуются

    if "{% extends" not in content:
        return f"❌ {file_path}: Должен наследоваться от base.html"

    if '{% extends "base.html" %}' not in content:
        return f"❌ {file_path}: Должен наследоваться от base.html"

    return None


def check_inline_styles(file_path, content):
    """Проверяет наличие inline стилей."""
    inline_style_patterns = [
        r'style\s*=\s*["\'][^"\']*["\']',
        r"<style[^>]*>.*?</style>",
    ]

    for pattern in inline_style_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        if matches:
            return f"⚠️  {file_path}: Найдены inline стили ({len(matches)} шт.)"

    return None


def check_meta_tags(file_path, content):
    """Проверяет наличие основных meta тегов."""
    # Includes и component файлы не проверяем
    parts = file_path.parts
    if len(parts) >= 2 and parts[-2] == "includes":
        return None
    if len(parts) >= 3 and parts[-3] == "components":
        return None

    if file_path.name == "webapp.html":
        return None  # WebApp имеет свои meta теги

    required_meta = ['charset="utf-8"', 'name="viewport"', 'name="description"']

    missing_meta = []
    for meta in required_meta:
        if meta not in content:
            missing_meta.append(meta)

    if missing_meta and '{% extends "base.html" %}' in content:
        # Если наследуется от base.html, meta теги должны быть в base
        return None

    if missing_meta:
        return f"❌ {file_path}: Отсутствуют meta теги: {', '.join(missing_meta)}"

    return None


def main():
    """Главная функция."""
    print("🔍 Проверка консистентности шаблонов PulseAI...")

    # Переходим в корень проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    success = check_templates()

    if success:
        print("\n🎉 Все проверки пройдены успешно!")
        return 0
    else:
        print("\n💥 Обнаружены проблемы в шаблонах!")
        return 1


if __name__ == "__main__":
    exit(main())

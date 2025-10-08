#!/usr/bin/env python3
"""
Объединенный инструмент для оптимизации CSS.
Объединяет функциональность cleanup_css.py, optimize_css.py
"""


# === ИЗ cleanup_css.py ===

#!/usr/bin/env python3
"""
PulseAI CSS Cleanup Tool
Удаляет неиспользуемые CSS классы и оптимизирует файлы
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def get_used_classes():
    """Получает список используемых CSS классов."""
    print("🔍 Поиск используемых CSS классов...")

    template_files = list(Path("templates").rglob("*.html"))
    js_files = list(Path("static/js").rglob("*.js"))

    used_classes = set()

    for template_file in template_files:
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Найти class атрибуты
                class_pattern = r'class\s*=\s*["\']([^"\']+)["\']'
                matches = re.findall(class_pattern, content)

                for match in matches:
                    classes = match.split()
                    used_classes.update(classes)

        except Exception as e:
            print(f"    ❌ Ошибка чтения {template_file}: {e}")

    for js_file in js_files:
        try:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Найти обращения к классам в JS
                class_pattern = r'["\']([a-zA-Z][a-zA-Z0-9_-]*(?:\s+[a-zA-Z][a-zA-Z0-9_-]*)*)["\']'
                matches = re.findall(class_pattern, content)

                for match in matches:
                    classes = match.split()
                    used_classes.update(classes)

        except Exception as e:
            print(f"    ❌ Ошибка чтения {js_file}: {e}")

    print(f"  Найдено {len(used_classes)} используемых классов")
    return used_classes


def cleanup_css_file(file_path, used_classes, dry_run=True):
    """Очищает CSS файл от неиспользуемых классов."""
    print(f"  Очистка {file_path}...")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        removed_classes = []

        # Найти все CSS правила
        css_rules = re.findall(r"([^{}]+)\s*\{([^{}]*)\}", content, re.MULTILINE | re.DOTALL)

        for selector, properties in css_rules:
            selector = selector.strip()

            # Пропускаем специальные селекторы
            if any(
                skip in selector for skip in [
                    "@",
                    ":",
                    "html",
                    "body",
                    "root",
                    "svg",
                    "path",
                    "line"]):
                continue

            # Извлекаем классы из селектора
            class_pattern = r"\.([a-zA-Z][a-zA-Z0-9_-]*)"
            classes_in_selector = re.findall(class_pattern, selector)

            # Проверяем, используются ли все классы
            unused_in_selector = [cls for cls in classes_in_selector if cls not in used_classes]

            if unused_in_selector and len(classes_in_selector) == len(unused_in_selector):
                # Весь селектор не используется
                removed_classes.extend(unused_in_selector)

                if not dry_run:
                    # Удаляем правило
                    rule_pattern = re.escape(selector) + r"\s*\{" + re.escape(properties) + r"\}"
                    content = re.sub(rule_pattern, "", content, flags=re.MULTILINE | re.DOTALL)

        if removed_classes and not dry_run:
            # Очищаем пустые строки
            content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

            # Сохраняем файл
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"    ✅ Удалено {len(removed_classes)} неиспользуемых классов")
            print(f"    📉 Размер уменьшен на {len(original_content) - len(content)} байт")

        return removed_classes, len(original_content) - len(content) if not dry_run else 0

    except Exception as e:
        print(f"    ❌ Ошибка обработки {file_path}: {e}")
        return [], 0


def merge_duplicate_selectors():
    """Объединяет дублирующиеся селекторы."""
    print("\n🔄 Объединение дублирующихся селекторов...")

    css_files = list(Path("static/css").rglob("*.css"))

    for css_file in css_files:
        print(f"  Обработка {css_file}...")

        try:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Найти дублирующиеся селекторы
            selector_pattern = r"([^{}]+)\s*\{([^{}]*)\}"
            rules = re.findall(selector_pattern, content, re.MULTILINE | re.DOTALL)

            selector_properties = defaultdict(list)

            for selector, properties in rules:
                selector = selector.strip()
                properties = properties.strip()

                if properties:
                    selector_properties[selector].append(properties)

            # Объединить свойства для дублирующихся селекторов
            merged_content = content

            for selector, properties_list in selector_properties.items():
                if len(properties_list) > 1:
                    # Объединить все свойства
                    all_properties = []
                    for props in properties_list:
                        all_properties.extend([p.strip() for p in props.split(";") if p.strip()])

                    # Удалить дубликаты свойств
                    unique_properties = []
                    seen = set()
                    for prop in all_properties:
                        if prop not in seen:
                            unique_properties.append(prop)
                            seen.add(prop)

                    # Создать новое правило
                    new_rule = f"{selector} {{\n  {'; '.join(unique_properties)};\n}}"

                    # Заменить все вхождения
                    old_pattern = re.escape(selector) + r"\s*\{[^{}]*\}"
                    matches = re.findall(old_pattern, content, re.MULTILINE | re.DOTALL)

                    for match in matches:
                        merged_content = merged_content.replace(match, "", 1)

                    # Добавить новое правило
                    merged_content += f"\n{new_rule}\n"

                    print(f"    ✅ Объединён селектор {selector} ({len(properties_list)} раз)")

            # Сохранить результат
            if merged_content != content:
                with open(css_file, "w", encoding="utf-8") as f:
                    f.write(merged_content)
                print(f"    📉 Размер уменьшен на {len(content) - len(merged_content)} байт")

        except Exception as e:
            print(f"    ❌ Ошибка обработки {css_file}: {e}")


def minify_css_file(file_path):
    """Минифицирует CSS файл."""
    print(f"  Минификация {file_path}...")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_size = len(content)

        # Удалить комментарии
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        # Удалить лишние пробелы
        content = re.sub(r"\s+", " ", content)
        content = re.sub(r"\s*{\s*", "{", content)
        content = re.sub(r"\s*}\s*", "}", content)
        content = re.sub(r"\s*;\s*", ";", content)
        content = re.sub(r"\s*:\s*", ":", content)
        content = re.sub(r"\s*,\s*", ",", content)

        # Удалить пробелы вокруг селекторов
        content = re.sub(r"\s*>\s*", ">", content)
        content = re.sub(r"\s*\+\s*", "+", content)
        content = re.sub(r"\s*~\s*", "~", content)

        # Удалить последние точки с запятой
        content = re.sub(r";}", "}", content)

        # Сохранить минифицированную версию
        minified_path = file_path.with_suffix(".min.css")
        with open(minified_path, "w", encoding="utf-8") as f:
            f.write(content.strip())

        reduction = original_size - len(content)
        print(f"    ✅ Минифицирован: {reduction} байт ({reduction/original_size*100:.1f}%)")
        print(f"    💾 Сохранён как {minified_path}")

        return reduction

    except Exception as e:
        print(f"    ❌ Ошибка минификации {file_path}: {e}")
        return 0


def main():
    """Главная функция."""
    print("🧹 PulseAI CSS Cleanup Tool")
    print("=" * 50)

    # Переходим в корень проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    # Получаем используемые классы
    used_classes = get_used_classes()

    # Очищаем CSS файлы
    print("\n🗑️  Очистка неиспользуемых классов...")
    css_files = list(Path("static/css").rglob("*.css"))

    total_removed = 0
    total_saved = 0

    for css_file in css_files:
        if css_file.name.endswith(".min.css"):
            continue  # Пропускаем уже минифицированные файлы

        removed, saved = cleanup_css_file(css_file, used_classes, dry_run=False)
        total_removed += len(removed)
        total_saved += saved

    print(f"\n📊 РЕЗУЛЬТАТЫ ОЧИСТКИ:")
    print(f"  Удалено неиспользуемых классов: {total_removed}")
    print(f"  Сэкономлено байт: {total_saved:,}")

    # Объединяем дублирующиеся селекторы
    merge_duplicate_selectors()

    # Создаём минифицированные версии
    print("\n⚡ Создание минифицированных версий...")
    total_minified = 0

    for css_file in css_files:
        if css_file.name.endswith(".min.css"):
            continue

        saved = minify_css_file(css_file)
        total_minified += saved

    print(f"\n📊 ИТОГОВАЯ ОПТИМИЗАЦИЯ:")
    print(f"  Сэкономлено при очистке: {total_saved:,} байт")
    print(f"  Сэкономлено при минификации: {total_minified:,} байт")
    print(f"  Общая экономия: {total_saved + total_minified:,} байт")

    print("\n🎉 Очистка завершена!")
    return 0


if __name__ == "__main__":
    exit(main())


# === ИЗ optimize_css.py ===

#!/usr/bin/env python3
"""
PulseAI CSS Optimizer
Анализирует и оптимизирует CSS файлы, находит неиспользуемые стили
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def analyze_css_usage():
    """Анализирует использование CSS классов в проекте."""
    print("🔍 Анализ использования CSS классов...")

    # Найти все CSS файлы
    css_files = list(Path("static/css").rglob("*.css"))
    template_files = list(Path("templates").rglob("*.html"))
    js_files = list(Path("static/js").rglob("*.js"))

    # Собрать все CSS классы
    css_classes = set()
    css_selectors = defaultdict(int)

    for css_file in css_files:
        print(f"  Анализирую {css_file}...")
        try:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Найти CSS классы
                class_pattern = r"\.([a-zA-Z][a-zA-Z0-9_-]*)(?:\s*[,{])"
                classes = re.findall(class_pattern, content)
                css_classes.update(classes)

                # Подсчитать селекторы
                selector_pattern = r"([^{}]+)\s*\{"
                selectors = re.findall(selector_pattern, content)
                for selector in selectors:
                    selector = selector.strip()
                    if selector:
                        css_selectors[selector] += 1

        except Exception as e:
            print(f"    ❌ Ошибка чтения {css_file}: {e}")

    # Найти использование классов в HTML/JS
    used_classes = set()

    for template_file in template_files:
        print(f"  Проверяю использование в {template_file}...")
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Найти class атрибуты
                class_pattern = r'class\s*=\s*["\']([^"\']+)["\']'
                matches = re.findall(class_pattern, content)

                for match in matches:
                    classes = match.split()
                    used_classes.update(classes)

        except Exception as e:
            print(f"    ❌ Ошибка чтения {template_file}: {e}")

    for js_file in js_files:
        print(f"  Проверяю использование в {js_file}...")
        try:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()

                # Найти обращения к классам в JS
                class_pattern = r'["\']([a-zA-Z][a-zA-Z0-9_-]*(?:\s+[a-zA-Z][a-zA-Z0-9_-]*)*)["\']'
                matches = re.findall(class_pattern, content)

                for match in matches:
                    classes = match.split()
                    used_classes.update(classes)

        except Exception as e:
            print(f"    ❌ Ошибка чтения {js_file}: {e}")

    # Анализ результатов
    unused_classes = css_classes - used_classes

    print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
    print(f"  Всего CSS классов: {len(css_classes)}")
    print(f"  Используемых классов: {len(used_classes)}")
    print(f"  Неиспользуемых классов: {len(unused_classes)}")

    if unused_classes:
        print(f"\n🗑️  НЕИСПОЛЬЗУЕМЫЕ КЛАССЫ:")
        for cls in sorted(unused_classes):
            print(f"    .{cls}")

    # Найти дублирующиеся селекторы
    duplicates = {k: v for k, v in css_selectors.items() if v > 1}
    if duplicates:
        print(f"\n🔄 ДУБЛИРУЮЩИЕСЯ СЕЛЕКТОРЫ:")
        for selector, count in sorted(duplicates.items()):
            print(f"    {selector} ({count} раз)")

    return {
        "total_classes": len(css_classes),
        "used_classes": len(used_classes),
        "unused_classes": len(unused_classes),
        "unused_list": unused_classes,
        "duplicates": duplicates,
    }


def check_css_size():
    """Проверяет размер CSS файлов."""
    print("\n📏 АНАЛИЗ РАЗМЕРОВ CSS:")

    css_files = list(Path("static/css").rglob("*.css"))
    total_size = 0

    for css_file in css_files:
        try:
            size = css_file.stat().st_size
            total_size += size
            print(f"  {css_file}: {size:,} байт ({size/1024:.1f} KB)")
        except Exception as e:
            print(f"    ❌ Ошибка чтения {css_file}: {e}")

    print(f"\n  Общий размер CSS: {total_size:,} байт ({total_size/1024:.1f} KB)")


def generate_optimization_report():
    """Генерирует отчёт по оптимизации."""
    print("\n📋 ГЕНЕРАЦИЯ ОТЧЁТА ОПТИМИЗАЦИИ...")

    results = analyze_css_usage()
    check_css_size()

    report = f"""# CSS Optimization Report

**Дата:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Статистика

- **Всего CSS классов:** {results['total_classes']}
- **Используемых классов:** {results['used_classes']}
- **Неиспользуемых классов:** {results['unused_classes']}
- **Эффективность использования:** {(results['used_classes']/results['total_classes']*100):.1f}%

## 🗑️ Неиспользуемые классы

"""

    if results["unused_list"]:
        for cls in sorted(results["unused_list"]):
            report += f"- `.{cls}`\n"
    else:
        report += "✅ Неиспользуемых классов не найдено!\n"

    report += f"""

## 🔄 Дублирующиеся селекторы

"""

    if results["duplicates"]:
        for selector, count in sorted(results["duplicates"].items()):
            report += f"- `{selector}` ({count} раз)\n"
    else:
        report += "✅ Дублирующихся селекторов не найдено!\n"

    report += """

## 💡 Рекомендации по оптимизации

1. **Удалить неиспользуемые классы** - уменьшит размер CSS
2. **Объединить дублирующиеся стили** - улучшит читаемость
3. **Использовать CSS минификацию** в продакшене
4. **Регулярно проверять использование** классов при рефакторинге

## 🎯 Цели оптимизации

- Уменьшить размер CSS на 10-20%
- Устранить дублирование стилей
- Улучшить производительность загрузки
- Упростить поддержку кода

---
*Отчёт сгенерирован автоматически CSS Optimizer*
"""

    with open("CSS_OPTIMIZATION_REPORT.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ Отчёт сохранён в CSS_OPTIMIZATION_REPORT.md")


def main():
    """Главная функция."""
    print("🎨 PulseAI CSS Optimizer")
    print("=" * 50)

    # Переходим в корень проекта
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    generate_optimization_report()

    print("\n🎉 Анализ завершён!")
    return 0


if __name__ == "__main__":
    exit(main())

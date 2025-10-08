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

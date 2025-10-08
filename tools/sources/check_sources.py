#!/usr/bin/env python3
"""
Объединенный инструмент для проверки источников.
Объединяет функциональность check_all_sources.py, check_templates.py
"""


# === ИЗ check_all_sources.py ===

#!/usr/bin/env python3
"""
Проверка корректности и работоспособности всех источников в config/sources.yaml
"""

import asyncio
import aiohttp
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SourceChecker:
    def __init__(self):
        self.results = []
        self.session = None
        self.total_sources = 0
        self.valid_sources = 0
        self.invalid_sources = 0

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10), headers={"User-Agent": "Mozilla/5.0 (compatible; PulseAI Bot)"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_url(self, url: str) -> tuple[bool, str]:
        """Проверяет доступность URL"""
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    content_type = response.headers.get("content-type", "").lower()
                    if "xml" in content_type or "rss" in content_type or "atom" in content_type:
                        return True, "✅ OK (RSS/XML)"
                    else:
                        return False, f"❌ HTML вместо RSS (Content-Type: {content_type})"
                elif response.status == 404:
                    return False, "❌ 404 Not Found"
                elif response.status == 403:
                    return False, "❌ 403 Forbidden"
                elif response.status == 301 or response.status == 302:
                    return False, f"❌ Redirect ({response.status})"
                else:
                    return False, f"❌ HTTP {response.status}"
        except asyncio.TimeoutError:
            return False, "❌ Timeout"
        except aiohttp.ClientError as e:
            return False, f"❌ Connection Error: {str(e)}"
        except Exception as e:
            return False, f"❌ Error: {str(e)}"

    async def check_rss_structure(self, url: str) -> tuple[bool, str]:
        """Проверяет структуру RSS"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return False, f"❌ HTTP {response.status}"

                content = await response.text()

                try:
                    root = ET.fromstring(content)

                    # Проверяем наличие элементов RSS
                    items = root.findall(".//item") or root.findall(".//entry")
                    if not items:
                        return False, "❌ No <item> or <entry> elements found"

                    # Проверяем наличие обязательных полей
                    for item in items[:3]:  # Проверяем первые 3 элемента
                        title = item.find("title") or item.find("{http://purl.org/rss/1.0/}title")
                        link = item.find("link") or item.find("{http://purl.org/rss/1.0/}link")

                        if title is None or link is None:
                            return False, "❌ Missing title or link in RSS items"

                    return True, f"✅ OK (RSS with {len(items)} items)"

                except ET.ParseError:
                    return False, "❌ Invalid XML structure"

        except Exception as e:
            return False, f"❌ RSS Check Error: {str(e)}"

    async def try_rss_alternatives(self, base_url: str) -> str:
        """Пробует найти RSS альтернативы"""
        alternatives = [
            f"{base_url}/feed",
            f"{base_url}/rss",
            f"{base_url}/rss.xml",
            f"{base_url}/feed.xml",
            f"{base_url}/feeds/all.rss",
        ]

        for alt_url in alternatives:
            try:
                async with self.session.get(alt_url) as response:
                    if response.status == 200:
                        content_type = response.headers.get("content-type", "").lower()
                        if "xml" in content_type or "rss" in content_type:
                            return f"🔄 Try: {alt_url}"
            except BaseException:
                continue

        return "❌ No RSS alternatives found"

    async def check_source(self, category: str, subcategory: str, source: dict) -> None:
        """Проверяет один источник"""
        name = source.get("name", "Unknown")
        url = source.get("url", "")

        if not url:
            result = "❌ Empty URL"
            self.results.append((category, subcategory, name, url, result))
            self.invalid_sources += 1
            return

        # Проверяем доступность URL
        is_accessible, access_result = await self.check_url(url)

        if is_accessible:
            # Проверяем структуру RSS
            is_valid_rss, rss_result = await self.check_rss_structure(url)
            if is_valid_rss:
                result = rss_result
                self.valid_sources += 1
            else:
                # Пробуем найти альтернативы
                alternatives = await self.try_rss_alternatives(url.rstrip("/"))
                result = f"{access_result} | {rss_result} | {alternatives}"
                self.invalid_sources += 1
        else:
            # Пробуем найти альтернативы
            alternatives = await self.try_rss_alternatives(url.rstrip("/"))
            result = f"{access_result} | {alternatives}"
            self.invalid_sources += 1

        self.results.append((category, subcategory, name, url, result))
        logger.info(f"Checked: {category}/{subcategory} - {name}")

    async def check_all_sources(self, sources_config: dict) -> None:
        """Проверяет все источники"""
        for category, cat_data in sources_config.items():
            if category == "version" or not isinstance(cat_data, dict):
                continue

            for subcategory, sub_data in cat_data.items():
                if not isinstance(sub_data, dict) or "sources" not in sub_data:
                    continue

                sources = sub_data["sources"]
                if not isinstance(sources, list):
                    continue

                for source in sources:
                    self.total_sources += 1
                    await self.check_source(category, subcategory, source)

    def save_results(self, log_file: str = "logs/bad_sources.log") -> None:
        """Сохраняет результаты в файл"""
        Path("logs").mkdir(exist_ok=True)

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"# Source Check Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for category, subcategory, name, url, result in self.results:
                f.write(f"[{category}/{subcategory}] {name}: {url} — {result}\n")

        logger.info(f"Results saved to {log_file}")

    def print_statistics(self) -> None:
        """Выводит статистику"""
        print("\n" + "=" * 60)
        print("📊 СТАТИСТИКА ПРОВЕРКИ ИСТОЧНИКОВ")
        print("=" * 60)
        print(f"📈 Общее количество источников: {self.total_sources}")
        print(f"✅ Валидных источников: {self.valid_sources}")
        print(f"❌ Невалидных источников: {self.invalid_sources}")
        print(
            f"📊 Процент валидности: {(self.valid_sources/self.total_sources*100):.1f}%"
            if self.total_sources > 0
            else "0%"
        )

        # Топ 5 невалидных источников
        invalid_results = [
            (cat, sub, name, url, result) for cat, sub, name, url, result in self.results if "❌" in result
        ]

        if invalid_results:
            print(f"\n🔴 ТОП-5 НЕВАЛИДНЫХ ИСТОЧНИКОВ:")
            for i, (category, subcategory, name, url, result) in enumerate(invalid_results[:5], 1):
                print(f"{i}. [{category}/{subcategory}] {name}")
                print(f"   URL: {url}")
                print(f"   Проблема: {result}")
                print()

        print("=" * 60)


async def main():
    """Основная функция"""
    print("🔍 Начинаем проверку источников...")

    # Загружаем конфигурацию
    try:
        with open("config/data/sources.yaml", "r", encoding="utf-8") as f:
            sources_config = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Ошибка загрузки config/sources.yaml: {e}")
        return

    # Проверяем источники
    async with SourceChecker() as checker:
        await checker.check_all_sources(sources_config)

    # Сохраняем результаты
    checker.save_results()

    # Выводим статистику
    checker.print_statistics()

    print("\n✅ Проверка завершена!")


if __name__ == "__main__":
    asyncio.run(main())


# === ИЗ check_templates.py ===

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

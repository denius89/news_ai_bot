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
            except:
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
        with open("config/sources.yaml", "r", encoding="utf-8") as f:
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

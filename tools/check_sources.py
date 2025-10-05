#!/usr/bin/env python3
"""
Инструмент проверки RSS источников из config/sources.yaml.
Выполняет параллельные запросы с таймаутами и ретраями.
Генерирует отчеты в CSV, Markdown и JSON форматах.
"""

import os
import sys
import yaml
import time
import json
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SourceChecker:
    """Класс для проверки RSS источников."""

    def __init__(self, sources_file="config/sources.yaml", max_workers=20):
        self.sources_file = sources_file
        self.max_workers = max_workers
        self.results = []

        # Настройка сессии с ретраями
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # User-Agent для избежания блокировок
        self.session.headers.update(
            {
                'User-Agent': (
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/91.0.4472.124 Safari/537.36'
                )
            }
        )

    def load_sources(self):
        """Загружает источники из YAML файла."""
        try:
            with open(self.sources_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data
        except Exception as e:
            print(f"❌ Ошибка загрузки {self.sources_file}: {e}")
            return {}

    def check_single_source(self, category, subcategory, name, url):
        """Проверяет один источник RSS."""
        start_time = time.time()
        result = {
            'category': category,
            'subcategory': subcategory,
            'name': name,
            'url': url,
            'status': 'Unknown',
            'rss_ok': False,
            'http_status': None,
            'final_url': url,
            'elapsed_ms': 0,
            'error': None,
        }

        try:
            # Выполняем запрос с таймаутом
            response = self.session.get(url, timeout=10, allow_redirects=True)
            elapsed_ms = int((time.time() - start_time) * 1000)

            result['elapsed_ms'] = elapsed_ms
            result['http_status'] = response.status_code
            result['final_url'] = response.url

            # Определяем статус по HTTP коду
            if response.status_code == 200:
                result['status'] = 'OK'

                # Проверяем, является ли это RSS/Atom
                content_type = response.headers.get('content-type', '').lower()
                if any(xml_type in content_type for xml_type in ['xml', 'rss', 'atom']):
                    # Парсим как XML и проверяем наличие элементов RSS/Atom
                    try:
                        # Простая проверка на наличие RSS/Atom элементов
                        content = response.text.lower()
                        if '<item>' in content or '<entry>' in content:
                            result['rss_ok'] = True
                        else:
                            result['status'] = 'OK (No RSS items)'
                    except Exception:
                        result['status'] = 'OK (Parse error)'
                else:
                    result['status'] = 'OK (Not XML)'

            elif 300 <= response.status_code < 400:
                result['status'] = 'Redirect'
            elif response.status_code == 403:
                result['status'] = 'Forbidden'
            elif response.status_code == 404:
                result['status'] = 'Not Found'
            else:
                result['status'] = f'HTTP {response.status_code}'

        except requests.exceptions.Timeout:
            result['status'] = 'Error: Timeout'
            result['error'] = 'Request timeout after 10 seconds'
        except requests.exceptions.ConnectionError as e:
            result['status'] = 'Error: Connection'
            result['error'] = str(e)
        except requests.exceptions.RequestException as e:
            result['status'] = 'Error: Request'
            result['error'] = str(e)
        except Exception as e:
            result['status'] = 'Error: Unknown'
            result['error'] = str(e)

        return result

    def check_all_sources(self):
        """Проверяет все источники параллельно."""
        sources_data = self.load_sources()
        if not sources_data:
            print("❌ Не удалось загрузить источники")
            return

        # Подготавливаем список задач
        tasks = []
        total_sources = 0

        for category, subcategories in sources_data.items():
            for subcategory, subcategory_data in subcategories.items():
                if isinstance(subcategory_data, dict) and 'sources' in subcategory_data:
                    sources = subcategory_data['sources']
                else:
                    sources = subcategory_data

                for source in sources:
                    if isinstance(source, dict) and 'name' in source and 'url' in source:
                        tasks.append((category, subcategory, source['name'], source['url']))
                        total_sources += 1

        print(f"🔍 Начинаем проверку {total_sources} источников с {self.max_workers} потоками...")

        # Выполняем проверки параллельно
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Отправляем все задачи
            future_to_task = {
                executor.submit(self.check_single_source, *task): task for task in tasks
            }

            # Собираем результаты
            completed = 0
            for future in as_completed(future_to_task):
                try:
                    result = future.result()
                    self.results.append(result)
                    completed += 1

                    # Показываем прогресс каждые 10 источников
                    if completed % 10 == 0 or completed == total_sources:
                        print(
                            f"   📊 Проверено: {completed}/{total_sources} ({completed/total_sources*100:.1f}%)"
                        )

                except Exception as e:
                    task = future_to_task[future]
                    print(f"   ❌ Ошибка при проверке {task[2]}: {e}")

        print(f"✅ Проверка завершена! Обработано {len(self.results)} источников")

    def generate_csv_report(self, output_file="logs/sources_check.csv"):
        """Генерирует CSV отчет."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'category',
                'subcategory',
                'name',
                'url',
                'status',
                'rss_ok',
                'http_status',
                'final_url',
                'elapsed_ms',
                'error',
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for result in self.results:
                writer.writerow(result)

        print(f"📄 CSV отчет сохранен: {output_file}")

    def generate_json_report(self, output_file="logs/sources_check.json"):
        """Генерирует JSON отчет."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        report_data = {
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(self.results),
            'summary': self.get_summary(),
            'results': self.results,
        }

        with open(output_file, 'w', encoding='utf-8') as jsonfile:
            json.dump(report_data, jsonfile, indent=2, ensure_ascii=False)

        print(f"📄 JSON отчет сохранен: {output_file}")

    def get_summary(self):
        """Возвращает сводную статистику."""
        summary = {
            'total': len(self.results),
            'ok': 0,
            'redirect': 0,
            'forbidden': 0,
            'not_found': 0,
            'error': 0,
            'rss_ok': 0,
        }

        for result in self.results:
            status = result['status']
            if status == 'OK' or status.startswith('OK'):
                summary['ok'] += 1
            elif status == 'Redirect':
                summary['redirect'] += 1
            elif status == 'Forbidden':
                summary['forbidden'] += 1
            elif status == 'Not Found':
                summary['not_found'] += 1
            else:
                summary['error'] += 1

            if result['rss_ok']:
                summary['rss_ok'] += 1

        return summary

    def generate_markdown_report(self, output_file="logs/sources_check.md"):
        """Генерирует Markdown отчет."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        summary = self.get_summary()

        # Находим топ проблемных источников
        error_sources = [r for r in self.results if r['status'] not in ['OK', 'Redirect']]
        error_sources.sort(key=lambda x: x['status'])

        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write("# Отчет проверки RSS источников\n\n")
            md_file.write(f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Сводка
            md_file.write("## 📊 Сводка\n\n")
            md_file.write(f"- **Всего источников:** {summary['total']}\n")
            md_file.write(f"- **✅ OK:** {summary['ok']}\n")
            md_file.write(f"- **🔄 Redirect:** {summary['redirect']}\n")
            md_file.write(f"- **🚫 Forbidden:** {summary['forbidden']}\n")
            md_file.write(f"- **❌ Not Found:** {summary['not_found']}\n")
            md_file.write(f"- **⚠️ Error:** {summary['error']}\n")
            md_file.write(f"- **📰 RSS OK:** {summary['rss_ok']}\n\n")

            # Процент успешности
            success_rate = (summary['ok'] + summary['redirect']) / summary['total'] * 100
            md_file.write(f"**Процент успешности:** {success_rate:.1f}%\n\n")

            # Топ проблемных источников
            if error_sources:
                md_file.write("## 🚨 Топ проблемных источников\n\n")
                md_file.write("| Категория | Подкатегория | Название | Статус | URL |\n")
                md_file.write("|-----------|--------------|----------|--------|-----|\n")

                for source in error_sources[:20]:  # Показываем топ 20
                    md_file.write(
                        f"| {source['category']} | {source['subcategory']} | "
                        f"{source['name']} | {source['status']} | {source['url']} |\n"
                    )

                if len(error_sources) > 20:
                    md_file.write(f"\n... и еще {len(error_sources) - 20} проблемных источников\n")

            # Статистика по категориям
            md_file.write("\n## 📈 Статистика по категориям\n\n")
            category_stats = {}
            for result in self.results:
                cat = result['category']
                if cat not in category_stats:
                    category_stats[cat] = {'total': 0, 'ok': 0, 'error': 0}

                category_stats[cat]['total'] += 1
                if result['status'] in ['OK', 'Redirect']:
                    category_stats[cat]['ok'] += 1
                else:
                    category_stats[cat]['error'] += 1

            md_file.write("| Категория | Всего | OK | Ошибки | % Успеха |\n")
            md_file.write("|-----------|-------|----|---------|----------|\n")

            for cat, stats in category_stats.items():
                success_rate = stats['ok'] / stats['total'] * 100 if stats['total'] > 0 else 0
                md_file.write(
                    f"| {cat} | {stats['total']} | {stats['ok']} | {stats['error']} | {success_rate:.1f}% |\n"
                )

        print(f"📄 Markdown отчет сохранен: {output_file}")

    def run_check(self):
        """Запускает полную проверку и генерирует отчеты."""
        print("🚀 Запуск проверки RSS источников...")
        print(f"📁 Файл источников: {self.sources_file}")
        print(f"⚙️ Потоков: {self.max_workers}")
        print("-" * 50)

        # Проверяем источники
        self.check_all_sources()

        if not self.results:
            print("❌ Нет результатов для генерации отчетов")
            return

        # Генерируем отчеты
        print("\n📊 Генерация отчетов...")
        self.generate_csv_report()
        self.generate_json_report()
        self.generate_markdown_report()

        # Показываем краткую сводку
        summary = self.get_summary()
        print("\n📈 Итоговая сводка:")
        print(f"   Всего источников: {summary['total']}")
        print(f"   ✅ OK: {summary['ok']}")
        print(f"   🔄 Redirect: {summary['redirect']}")
        print(f"   🚫 Forbidden: {summary['forbidden']}")
        print(f"   ❌ Not Found: {summary['not_found']}")
        print(f"   ⚠️ Error: {summary['error']}")
        print(f"   📰 RSS OK: {summary['rss_ok']}")

        success_rate = (summary['ok'] + summary['redirect']) / summary['total'] * 100
        print(f"   📊 Успешность: {success_rate:.1f}%")


def main():
    """Основная функция."""
    checker = SourceChecker()
    checker.run_check()


if __name__ == "__main__":
    main()

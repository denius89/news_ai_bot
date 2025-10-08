#!/usr/bin/env python3
"""
🔧 Скрипт обновления импортов после оптимизации tools
Автор: AI Assistant
Версия: 1.0

Обновляет импорты tools в других файлах проекта
"""

import os
import re
from pathlib import Path


class ToolsImportUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

        # Маппинг старых импортов на новые
        self.import_mappings = {
            # Management импорты
            "from tools.run_all": "from tools.management.run_all",
            "from tools.port_manager": "from tools.management.port_manager",
            "import tools.run_all": "import tools.management.run_all",
            "import tools.port_manager": "import tools.management.port_manager",
            # News импорты
            "from tools.fetch_and_store_news": "from tools.news.fetch_news",
            "from tools.fetch_loop": "from tools.news.fetch_news",
            "from tools.fetch_optimized": "from tools.news.fetch_news",
            "from tools.load_fresh_news": "from tools.news.load_fresh_news",
            "from tools.refresh_news": "from tools.news.refresh_news",
            "from tools.clean_old_news": "from tools.news.clean_old_news",
            "from tools.update_news_with_universal_parser": "from tools.news.update_news",
            "import tools.fetch_and_store_news": "import tools.news.fetch_news",
            "import tools.fetch_loop": "import tools.news.fetch_news",
            "import tools.fetch_optimized": "import tools.news.fetch_news",
            "import tools.load_fresh_news": "import tools.news.load_fresh_news",
            "import tools.refresh_news": "import tools.news.refresh_news",
            "import tools.clean_old_news": "import tools.news.clean_old_news",
            "import tools.update_news_with_universal_parser": "import tools.news.update_news",
            # Events импорты
            "from tools.fetch_and_store_events": "from tools.events.fetch_events",
            "import tools.fetch_and_store_events": "import tools.events.fetch_events",
            # Sources импорты
            "from tools.check_all_sources": "from tools.sources.check_sources",
            "from tools.check_templates": "from tools.sources.check_sources",
            "from tools.distribute_sources": "from tools.sources.distribute_sources",
            "from tools.smart_distribute_sources": "from tools.sources.distribute_sources",
            "from tools.merge_sources": "from tools.sources.merge_sources",
            "from tools.update_rss_sources": "from tools.sources.validate_sources",
            "from tools.validate_rss_sources": "from tools.sources.validate_sources",
            "import tools.check_all_sources": "import tools.sources.check_sources",
            "import tools.check_templates": "import tools.sources.check_sources",
            "import tools.distribute_sources": "import tools.sources.distribute_sources",
            "import tools.smart_distribute_sources": "import tools.sources.distribute_sources",
            "import tools.merge_sources": "import tools.sources.merge_sources",
            "import tools.update_rss_sources": "import tools.sources.validate_sources",
            "import tools.validate_rss_sources": "import tools.sources.validate_sources",
            # AI импорты
            "from tools.build_baseline_dataset": "from tools.ai.build_dataset",
            "from tools.fill_ai_analysis_all": "from tools.ai.train_models",
            "from tools.train_self_tuning": "from tools.ai.train_models",
            "from tools.analyze_rejections": "from tools.ai.analyze_data",
            "import tools.build_baseline_dataset": "import tools.ai.build_dataset",
            "import tools.fill_ai_analysis_all": "import tools.ai.train_models",
            "import tools.train_self_tuning": "import tools.ai.train_models",
            "import tools.analyze_rejections": "import tools.ai.analyze_data",
            # Frontend импорты
            "from tools.cleanup_css": "from tools.frontend.optimize_css",
            "from tools.optimize_css": "from tools.frontend.optimize_css",
            "import tools.cleanup_css": "import tools.frontend.optimize_css",
            "import tools.optimize_css": "import tools.frontend.optimize_css",
            # Notifications импорты
            "from tools.send_daily_digests": "from tools.notifications.send_digests",
            "import tools.send_daily_digests": "import tools.notifications.send_digests",
            # Testing импорты
            "from tools.test_advanced_parser": "from tools.testing.test_parser",
            "import tools.test_advanced_parser": "import tools.testing.test_parser",
            # Utils импорты
            "from tools.repo_map": "from tools.utils.repo_map",
            "import tools.repo_map": "import tools.utils.repo_map",
        }

    def update_file_imports(self, file_path):
        """Обновляет импорты в одном файле"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            updated_count = 0

            # Применяем все маппинги
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    updated_count += 1

            # Записываем обновленный контент если были изменения
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                return updated_count

            return 0

        except Exception as e:
            print(f"  ❌ Ошибка при обновлении {file_path}: {e}")
            return 0

    def update_all_imports(self):
        """Обновляет все импорты в проекте"""
        print("🔧 Начинаю обновление импортов tools...")
        print("=" * 50)

        total_files = 0
        total_updates = 0

        # Ищем файлы, которые могут импортировать tools
        search_paths = [
            "ai_modules",
            "database",
            "digests",
            "events",
            "parsers",
            "repositories",
            "routes",
            "services",
            "telegram_bot",
            "tests",
            "utils",
        ]

        for search_path in search_paths:
            path = self.project_root / search_path
            if path.exists():
                for py_file in path.glob("**/*.py"):
                    total_files += 1
                    updates = self.update_file_imports(py_file)
                    if updates > 0:
                        print(f"  ✅ {py_file.relative_to(self.project_root)} - {updates} импортов обновлено")
                        total_updates += updates

        # Также проверяем файлы в корне
        for py_file in self.project_root.glob("*.py"):
            total_files += 1
            updates = self.update_file_imports(py_file)
            if updates > 0:
                print(f"  ✅ {py_file.name} - {updates} импортов обновлено")
                total_updates += updates

        print(f"\n🎉 ОБНОВЛЕНИЕ ИМПОРТОВ ЗАВЕРШЕНО!")
        print(f"📊 Всего обновлено: {total_updates} импортов в {total_files} файлах")

        return total_updates

    def verify_imports(self):
        """Проверяет, что все импорты корректны"""
        print("🔍 Проверяю корректность импортов...")

        # Проверяем основные импорты
        test_files = ["scripts/start_services.sh", "scripts/stop_services.sh", "Makefile"]

        for test_file in test_files:
            file_path = self.project_root / test_file
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Проверяем, что старые импорты заменены
                old_imports = [imp for imp in self.import_mappings.keys() if imp in content]
                if old_imports:
                    print(f"  ⚠️ {test_file} все еще содержит старые импорты: {old_imports}")
                else:
                    print(f"  ✅ {test_file} - импорты корректны")

        print("✅ Проверка импортов завершена")


if __name__ == "__main__":
    updater = ToolsImportUpdater()
    updater.update_all_imports()
    updater.verify_imports()

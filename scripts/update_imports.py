#!/usr/bin/env python3
"""
🔧 Скрипт обновления импортов после оптимизации
Автор: AI Assistant
Версия: 1.0

Обновляет импорты в перемещенных файлах tests и utils
"""

import os
import re
from pathlib import Path


class ImportUpdater:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)

        # Маппинг старых импортов на новые
        self.import_mappings = {
            # Utils импорты
            "from utils.clean_text": "from utils.text.clean_text",
            "from utils.formatters": "from utils.text.formatters",
            "from utils.cache": "from utils.system.cache",
            "from utils.dates": "from utils.system.dates",
            "from utils.progress_animation": "from utils.system.progress_animation",
            "from utils.ai_client": "from utils.ai.ai_client",
            "from utils.news_distribution": "from utils.ai.news_distribution",
            "from utils.http_client": "from utils.network.http_client",
            "from utils.telegram_sender": "from utils.network.telegram_sender",
            "from utils.logging_setup": "from utils.logging.logging_setup",
            "from utils.standard_logging": "from utils.logging.standard_logging",
            # Import statements
            "import utils.clean_text": "import utils.text.clean_text",
            "import utils.formatters": "import utils.text.formatters",
            "import utils.cache": "import utils.system.cache",
            "import utils.dates": "import utils.system.dates",
            "import utils.progress_animation": "import utils.system.progress_animation",
            "import utils.ai_client": "import utils.ai.ai_client",
            "import utils.news_distribution": "import utils.ai.news_distribution",
            "import utils.http_client": "import utils.network.http_client",
            "import utils.telegram_sender": "import utils.network.telegram_sender",
            "import utils.logging_setup": "import utils.logging.logging_setup",
            "import utils.standard_logging": "import utils.logging.standard_logging",
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

    def update_tests_imports(self):
        """Обновляет импорты в папке tests"""
        print("🔧 Обновляю импорты в tests...")

        total_files = 0
        total_updates = 0

        # Находим все Python файлы в tests
        for py_file in self.project_root.glob("tests/**/*.py"):
            if py_file.name != "__init__.py":
                total_files += 1
                updates = self.update_file_imports(py_file)
                if updates > 0:
                    print(f"  ✅ {py_file.relative_to(self.project_root)} - {updates} импортов обновлено")
                    total_updates += updates

        print(f"✅ Обновлено {total_updates} импортов в {total_files} файлах tests")
        return total_updates

    def update_utils_imports(self):
        """Обновляет импорты в папке utils"""
        print("🔧 Обновляю импорты в utils...")

        total_files = 0
        total_updates = 0

        # Находим все Python файлы в utils
        for py_file in self.project_root.glob("utils/**/*.py"):
            if py_file.name != "__init__.py":
                total_files += 1
                updates = self.update_file_imports(py_file)
                if updates > 0:
                    print(f"  ✅ {py_file.relative_to(self.project_root)} - {updates} импортов обновлено")
                    total_updates += updates

        print(f"✅ Обновлено {total_updates} импортов в {total_files} файлах utils")
        return total_updates

    def update_other_files_imports(self):
        """Обновляет импорты в других файлах проекта"""
        print("🔧 Обновляю импорты в других файлах...")

        total_files = 0
        total_updates = 0

        # Ищем файлы, которые могут импортировать utils
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
            "tools",
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

        print(f"✅ Обновлено {total_updates} импортов в {total_files} других файлах")
        return total_updates

    def verify_imports(self):
        """Проверяет, что все импорты корректны"""
        print("🔍 Проверяю корректность импортов...")

        # Проверяем основные импорты
        test_files = [
            "tests/unit/parsers/test_clean_text.py",
            "tests/unit/utils/test_cache.py",
            "tests/integration/telegram/test_telegram_sender.py",
        ]

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

    def update_all_imports(self):
        """Обновляет все импорты в проекте"""
        print("🔧 Начинаю обновление импортов...")
        print("=" * 50)

        total_updates = 0

        # Обновляем импорты в tests
        total_updates += self.update_tests_imports()
        print()

        # Обновляем импорты в utils
        total_updates += self.update_utils_imports()
        print()

        # Обновляем импорты в других файлах
        total_updates += self.update_other_files_imports()
        print()

        # Проверяем корректность
        self.verify_imports()

        print(f"\n🎉 ОБНОВЛЕНИЕ ИМПОРТОВ ЗАВЕРШЕНО!")
        print(f"📊 Всего обновлено: {total_updates} импортов")

        return total_updates


if __name__ == "__main__":
    updater = ImportUpdater()
    updater.update_all_imports()

#!/usr/bin/env python3
"""
🧹 Скрипт аккуратной оптимизации папок tests и utils
Автор: AI Assistant
Версия: 1.0

Максимально аккуратно реорганизует структуру папок tests и utils
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class TestsUtilsOptimizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "optimization_backup"
        
        # Определяем новые директории
        self.tests_new = self.project_root / "tests_new"
        self.utils_new = self.project_root / "utils_new"
        
        # Маппинг файлов tests
        self.tests_mapping = {
            # Unit тесты - AI
            "test_ai_modules.py": "unit/ai/",
            "test_ai_optimization.py": "unit/ai/",
            "test_ai_service.py": "unit/ai/",
            "test_ai_summary.py": "unit/ai/",
            
            # Unit тесты - Database
            "test_database_service.py": "unit/database/",
            "test_db_content.py": "unit/database/",
            "test_db_insert.py": "unit/database/",
            "test_db_models.py": "unit/database/",
            "test_supabase.py": "unit/database/",
            
            # Unit тесты - Parsers
            "test_advanced_parser.py": "unit/parsers/",
            "test_parsers.py": "unit/parsers/",
            "test_clean_text.py": "unit/parsers/",
            "test_sources.py": "unit/parsers/",
            
            # Unit тесты - Utils
            "test_cache.py": "unit/utils/",
            "test_formatters.py": "unit/utils/",
            "test_progress_animation.py": "unit/utils/",
            
            # Integration тесты - API
            "test_api_notifications.py": "integration/api/",
            "test_api_subscriptions.py": "integration/api/",
            "test_routes.py": "integration/api/",
            
            # Integration тесты - Telegram
            "test_telegram_sender.py": "integration/telegram/",
            "test_telegram_keyboards.py": "integration/telegram/",
            "test_keyboards_subscriptions.py": "integration/telegram/",
            "test_bot_routers.py": "integration/telegram/",
            
            # Integration тесты - WebApp
            "test_webapp.py": "integration/webapp/",
            "test_dashboard_webapp.py": "integration/webapp/",
            
            # Quick тесты - Smoke
            "test_main_import.py": "quick/smoke/",
            "test_main.py": "quick/smoke/",
            
            # Quick тесты - Performance
            "test_optimization_integration.py": "quick/performance/",
            
            # External Services
            "test_openai.py": "external/",
            "test_deepl.py": "external/",
            "test_http_client.py": "external/",
            
            # Fixtures (оставляем в корне)
            "conftest.py": "",
            "__init__.py": "",
        }
        
        # Маппинг файлов utils
        self.utils_mapping = {
            # AI утилиты
            "ai_client.py": "ai/",
            "news_distribution.py": "ai/",
            
            # Network утилиты
            "http_client.py": "network/",
            "telegram_sender.py": "network/",
            
            # Text утилиты
            "clean_text.py": "text/",
            "formatters.py": "text/",
            
            # System утилиты
            "cache.py": "system/",
            "dates.py": "system/",
            "progress_animation.py": "system/",
            
            # Logging утилиты
            "logging_setup.py": "logging/",
            "standard_logging.py": "logging/",
        }
        
    def create_backup(self):
        """Создает резервную копию всех файлов"""
        print("🔄 Создаю резервную копию...")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Копируем папки tests и utils
        if (self.project_root / "tests").exists():
            shutil.copytree(self.project_root / "tests", self.backup_dir / "tests")
            print("  ✅ Скопирована папка tests")
            
        if (self.project_root / "utils").exists():
            shutil.copytree(self.project_root / "utils", self.backup_dir / "utils")
            print("  ✅ Скопирована папка utils")
        
        print(f"✅ Резервная копия создана в {self.backup_dir}")
        
    def analyze_files(self):
        """Анализирует файлы перед перемещением"""
        print("🔍 Анализирую файлы...")
        
        tests_files = list((self.project_root / "tests").glob("*.py"))
        utils_files = list((self.project_root / "utils").glob("*.py"))
        
        print(f"  📁 Найдено {len(tests_files)} файлов в tests")
        print(f"  📁 Найдено {len(utils_files)} файлов в utils")
        
        # Проверяем маппинг
        unmapped_tests = []
        for file_path in tests_files:
            if file_path.name not in self.tests_mapping:
                unmapped_tests.append(file_path.name)
        
        unmapped_utils = []
        for file_path in utils_files:
            if file_path.name not in self.utils_mapping:
                unmapped_utils.append(file_path.name)
        
        if unmapped_tests:
            print(f"  ⚠️ Не маппированы тесты: {unmapped_tests}")
        
        if unmapped_utils:
            print(f"  ⚠️ Не маппированы утилиты: {unmapped_utils}")
        
        return unmapped_tests, unmapped_utils
        
    def move_tests_files(self):
        """Перемещает файлы tests по новой структуре"""
        print("📁 Перемещаю файлы tests...")
        
        moved_count = 0
        for filename, target_dir in self.tests_mapping.items():
            src = self.project_root / "tests" / filename
            if src.exists():
                dst_dir = self.tests_new / target_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / filename
                
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещен {filename} → {target_dir}")
                moved_count += 1
            else:
                print(f"  ⚠️ Файл {filename} не найден")
        
        print(f"✅ Перемещено {moved_count} файлов tests")
        
    def move_utils_files(self):
        """Перемещает файлы utils по новой структуре"""
        print("📁 Перемещаю файлы utils...")
        
        moved_count = 0
        for filename, target_dir in self.utils_mapping.items():
            src = self.project_root / "utils" / filename
            if src.exists():
                dst_dir = self.utils_new / target_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / filename
                
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещен {filename} → {target_dir}")
                moved_count += 1
            else:
                print(f"  ⚠️ Файл {filename} не найден")
        
        print(f"✅ Перемещено {moved_count} файлов utils")
        
    def create_init_files(self):
        """Создает __init__.py файлы в новых директориях"""
        print("📄 Создаю __init__.py файлы...")
        
        # Для tests
        test_dirs = [
            "unit", "unit/ai", "unit/database", "unit/parsers", "unit/utils",
            "integration", "integration/api", "integration/telegram", "integration/webapp",
            "quick", "quick/smoke", "quick/performance",
            "external", "fixtures"
        ]
        
        for dir_name in test_dirs:
            init_file = self.tests_new / dir_name / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text('"""Модули для тестирования."""\n')
            print(f"  ✅ Создан {dir_name}/__init__.py")
        
        # Для utils
        utils_dirs = ["ai", "network", "text", "system", "logging"]
        
        for dir_name in utils_dirs:
            init_file = self.utils_new / dir_name / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text('"""Утилиты для работы с системой."""\n')
            print(f"  ✅ Создан {dir_name}/__init__.py")
        
        print("✅ Все __init__.py файлы созданы")
        
    def replace_old_with_new(self):
        """Заменяет старые папки новыми"""
        print("🔄 Заменяю старые папки новыми...")
        
        # Удаляем старые папки
        if (self.project_root / "tests").exists():
            shutil.rmtree(self.project_root / "tests")
            print("  ✅ Удалена старая папка tests")
        
        if (self.project_root / "utils").exists():
            shutil.rmtree(self.project_root / "utils")
            print("  ✅ Удалена старая папка utils")
        
        # Переименовываем новые папки
        self.tests_new.rename(self.project_root / "tests")
        self.utils_new.rename(self.project_root / "utils")
        
        print("✅ Папки заменены успешно")
        
    def verify_structure(self):
        """Проверяет новую структуру"""
        print("🔍 Проверяю новую структуру...")
        
        # Проверяем tests
        tests_structure = {
            "unit/ai": 4,
            "unit/database": 5,
            "unit/parsers": 4,
            "unit/utils": 3,
            "integration/api": 3,
            "integration/telegram": 4,
            "integration/webapp": 2,
            "quick/smoke": 2,
            "quick/performance": 1,
            "external": 3,
        }
        
        for dir_name, expected_count in tests_structure.items():
            dir_path = self.project_root / "tests" / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*.py")))
                print(f"  ✅ {dir_name}/ - {file_count} файлов (ожидалось {expected_count})")
            else:
                print(f"  ❌ {dir_name}/ - директория не найдена")
        
        # Проверяем utils
        utils_structure = {
            "ai": 2,
            "network": 2,
            "text": 2,
            "system": 3,
            "logging": 2,
        }
        
        for dir_name, expected_count in utils_structure.items():
            dir_path = self.project_root / "utils" / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*.py")))
                print(f"  ✅ {dir_name}/ - {file_count} файлов (ожидалось {expected_count})")
            else:
                print(f"  ❌ {dir_name}/ - директория не найдена")
        
        print("✅ Проверка структуры завершена")
        
    def optimize_structure(self):
        """Основная функция оптимизации"""
        print("🧹 Начинаю аккуратную оптимизацию папок tests и utils...")
        print("=" * 60)
        
        try:
            # Создаем резервную копию
            self.create_backup()
            print()
            
            # Анализируем файлы
            unmapped_tests, unmapped_utils = self.analyze_files()
            print()
            
            # Перемещаем файлы
            self.move_tests_files()
            print()
            
            self.move_utils_files()
            print()
            
            # Создаем __init__.py файлы
            self.create_init_files()
            print()
            
            # Заменяем старые папки новыми
            self.replace_old_with_new()
            print()
            
            # Проверяем структуру
            self.verify_structure()
            
            print("\n🎉 ОПТИМИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("💡 Следующие шаги:")
            print("  1. Обновить импорты в перемещенных файлах")
            print("  2. Протестировать все изменения")
            print("  3. Обновить документацию")
            print("  4. Зафиксировать изменения в git")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            print("🔄 Восстанавливаю из резервной копии...")
            
            # Восстанавливаем из резервной копии
            if self.backup_dir.exists():
                if (self.backup_dir / "tests").exists():
                    shutil.copytree(self.backup_dir / "tests", self.project_root / "tests")
                    print("  ✅ Восстановлена папка tests")
                
                if (self.backup_dir / "utils").exists():
                    shutil.copytree(self.backup_dir / "utils", self.project_root / "utils")
                    print("  ✅ Восстановлена папка utils")
                    
            print("✅ Восстановление завершено")

if __name__ == "__main__":
    optimizer = TestsUtilsOptimizer()
    optimizer.optimize_structure()

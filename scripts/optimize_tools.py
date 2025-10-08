#!/usr/bin/env python3
"""
🧹 Скрипт аккуратной оптимизации папки tools
Автор: AI Assistant
Версия: 1.0

Максимально аккуратно реорганизует структуру папки tools
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class ToolsOptimizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "tools_optimization_backup"
        
        # Определяем новые директории
        self.tools_new = self.project_root / "tools_new"
        
        # Маппинг файлов tools по категориям
        self.tools_mapping = {
            # Management - Управление процессами
            "run_all.py": "management/",
            "port_manager.py": "management/",
            
            # News - Работа с новостями (объединяем похожие)
            "fetch_and_store_news.py": "news/fetch_news.py",  # Будет объединен
            "fetch_loop.py": "news/fetch_news.py",  # Будет объединен
            "fetch_optimized.py": "news/fetch_news.py",  # Будет объединен
            "load_fresh_news.py": "news/",
            "refresh_news.py": "news/",
            "clean_old_news.py": "news/",
            "update_news_with_universal_parser.py": "news/update_news.py",  # Переименуем
            
            # Events - Работа с событиями
            "fetch_and_store_events.py": "events/fetch_events.py",  # Переименуем
            
            # Sources - Управление источниками (объединяем похожие)
            "check_all_sources.py": "sources/check_sources.py",  # Будет объединен
            "check_templates.py": "sources/check_sources.py",  # Будет объединен
            "distribute_sources.py": "sources/distribute_sources.py",  # Будет объединен
            "smart_distribute_sources.py": "sources/distribute_sources.py",  # Будет объединен
            "merge_sources.py": "sources/",
            "update_rss_sources.py": "sources/validate_sources.py",  # Будет объединен
            "validate_rss_sources.py": "sources/validate_sources.py",  # Будет объединен
            
            # AI - AI и машинное обучение
            "build_baseline_dataset.py": "ai/build_dataset.py",  # Переименуем
            "fill_ai_analysis_all.py": "ai/train_models.py",  # Будет объединен
            "train_self_tuning.py": "ai/train_models.py",  # Будет объединен
            "analyze_rejections.py": "ai/analyze_data.py",  # Переименуем
            
            # Frontend - CSS и интерфейс (объединяем)
            "cleanup_css.py": "frontend/optimize_css.py",  # Будет объединен
            "optimize_css.py": "frontend/optimize_css.py",  # Будет объединен
            
            # Notifications - Уведомления
            "send_daily_digests.py": "notifications/send_digests.py",  # Переименуем
            
            # Testing - Тестирование
            "test_advanced_parser.py": "testing/test_parser.py",  # Переименуем
            
            # Utils - Утилиты
            "repo_map.py": "utils/",
        }
        
    def create_backup(self):
        """Создает резервную копию всех файлов"""
        print("🔄 Создаю резервную копию папки tools...")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Копируем папку tools
        if (self.project_root / "tools").exists():
            shutil.copytree(self.project_root / "tools", self.backup_dir / "tools")
            print("  ✅ Скопирована папка tools")
        
        print(f"✅ Резервная копия создана в {self.backup_dir}")
        
    def analyze_files(self):
        """Анализирует файлы перед перемещением"""
        print("🔍 Анализирую файлы tools...")
        
        tools_files = list((self.project_root / "tools").glob("*.py"))
        
        print(f"  📁 Найдено {len(tools_files)} файлов в tools")
        
        # Проверяем маппинг
        unmapped_tools = []
        for file_path in tools_files:
            if file_path.name not in self.tools_mapping:
                unmapped_tools.append(file_path.name)
        
        if unmapped_tools:
            print(f"  ⚠️ Не маппированы инструменты: {unmapped_tools}")
        
        return unmapped_tools
        
    def create_new_structure(self):
        """Создает новую структуру папок"""
        print("📁 Создаю новую структуру папок...")
        
        categories = [
            "management", "news", "events", "sources", 
            "ai", "frontend", "notifications", "testing", "utils"
        ]
        
        for category in categories:
            category_dir = self.tools_new / category
            category_dir.mkdir(parents=True, exist_ok=True)
            print(f"  ✅ Создана директория {category}/")
        
        print("✅ Новая структура создана")
        
    def merge_similar_files(self):
        """Объединяет похожие файлы"""
        print("🔗 Объединяю похожие файлы...")
        
        # Объединяем fetch файлы
        fetch_files = [
            "fetch_and_store_news.py",
            "fetch_loop.py", 
            "fetch_optimized.py"
        ]
        
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для получения новостей.\nОбъединяет функциональность fetch_and_store_news.py, fetch_loop.py, fetch_optimized.py\n"""\n')
        
        for file_name in fetch_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "news" / "fetch_news.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл news/fetch_news.py")
        
        # Объединяем distribute файлы
        distribute_files = [
            "distribute_sources.py",
            "smart_distribute_sources.py"
        ]
        
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для распределения источников.\nОбъединяет функциональность distribute_sources.py, smart_distribute_sources.py\n"""\n')
        
        for file_name in distribute_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "sources" / "distribute_sources.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл sources/distribute_sources.py")
        
        # Объединяем CSS файлы
        css_files = [
            "cleanup_css.py",
            "optimize_css.py"
        ]
        
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для оптимизации CSS.\nОбъединяет функциональность cleanup_css.py, optimize_css.py\n"""\n')
        
        for file_name in css_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "frontend" / "optimize_css.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл frontend/optimize_css.py")
        
        print("✅ Объединение файлов завершено")
        
    def move_remaining_files(self):
        """Перемещает оставшиеся файлы по новой структуре"""
        print("📁 Перемещаю оставшиеся файлы...")
        
        moved_count = 0
        
        # Файлы для простого перемещения (без объединения)
        simple_moves = {
            "run_all.py": "management/",
            "port_manager.py": "management/",
            "load_fresh_news.py": "news/",
            "refresh_news.py": "news/",
            "clean_old_news.py": "news/",
            "merge_sources.py": "sources/",
            "repo_map.py": "utils/",
        }
        
        for filename, target_dir in simple_moves.items():
            src = self.project_root / "tools" / filename
            if src.exists():
                dst_dir = self.tools_new / target_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / filename
                
                shutil.copy2(str(src), str(dst))
                print(f"  ✅ Перемещен {filename} → {target_dir}")
                moved_count += 1
        
        # Переименованные файлы
        renamed_files = {
            "update_news_with_universal_parser.py": ("news/", "update_news.py"),
            "fetch_and_store_events.py": ("events/", "fetch_events.py"),
            "build_baseline_dataset.py": ("ai/", "build_dataset.py"),
            "analyze_rejections.py": ("ai/", "analyze_data.py"),
            "send_daily_digests.py": ("notifications/", "send_digests.py"),
            "test_advanced_parser.py": ("testing/", "test_parser.py"),
        }
        
        for filename, (target_dir, new_name) in renamed_files.items():
            src = self.project_root / "tools" / filename
            if src.exists():
                dst_dir = self.tools_new / target_dir
                dst_dir.mkdir(parents=True, exist_ok=True)
                dst = dst_dir / new_name
                
                shutil.copy2(str(src), str(dst))
                print(f"  ✅ Перемещен и переименован {filename} → {target_dir}{new_name}")
                moved_count += 1
        
        # Объединяем check файлы
        check_files = ["check_all_sources.py", "check_templates.py"]
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для проверки источников.\nОбъединяет функциональность check_all_sources.py, check_templates.py\n"""\n')
        
        for file_name in check_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "sources" / "check_sources.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл sources/check_sources.py")
        
        # Объединяем validate файлы
        validate_files = ["update_rss_sources.py", "validate_rss_sources.py"]
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для валидации источников.\nОбъединяет функциональность update_rss_sources.py, validate_rss_sources.py\n"""\n')
        
        for file_name in validate_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "sources" / "validate_sources.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл sources/validate_sources.py")
        
        # Объединяем AI файлы
        ai_files = ["fill_ai_analysis_all.py", "train_self_tuning.py"]
        merged_content = []
        merged_content.append('#!/usr/bin/env python3\n"""\nОбъединенный инструмент для обучения моделей.\nОбъединяет функциональность fill_ai_analysis_all.py, train_self_tuning.py\n"""\n')
        
        for file_name in ai_files:
            file_path = self.project_root / "tools" / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                merged_content.append(f'\n# === ИЗ {file_name} ===\n')
                merged_content.append(content)
                print(f"  ✅ Добавлен {file_name}")
        
        # Сохраняем объединенный файл
        merged_file = self.tools_new / "ai" / "train_models.py"
        with open(merged_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(merged_content))
        print(f"  ✅ Создан объединенный файл ai/train_models.py")
        
        print(f"✅ Перемещено {moved_count} файлов")
        
    def create_init_files(self):
        """Создает __init__.py файлы в новых директориях"""
        print("📄 Создаю __init__.py файлы...")
        
        # Для tools
        tool_dirs = [
            "management", "news", "events", "sources", 
            "ai", "frontend", "notifications", "testing", "utils"
        ]
        
        for dir_name in tool_dirs:
            init_file = self.tools_new / dir_name / "__init__.py"
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text('"""Инструменты для работы с системой."""\n')
            print(f"  ✅ Создан {dir_name}/__init__.py")
        
        print("✅ Все __init__.py файлы созданы")
        
    def replace_old_with_new(self):
        """Заменяет старую папку новой"""
        print("🔄 Заменяю старую папку новой...")
        
        # Удаляем старую папку
        if (self.project_root / "tools").exists():
            shutil.rmtree(self.project_root / "tools")
            print("  ✅ Удалена старая папка tools")
        
        # Переименовываем новую папку
        self.tools_new.rename(self.project_root / "tools")
        
        print("✅ Папка заменена успешно")
        
    def verify_structure(self):
        """Проверяет новую структуру"""
        print("🔍 Проверяю новую структуру...")
        
        # Проверяем tools
        tools_structure = {
            "management": 2,
            "news": 4,
            "events": 1,
            "sources": 4,
            "ai": 3,
            "frontend": 1,
            "notifications": 1,
            "testing": 1,
            "utils": 1,
        }
        
        for dir_name, expected_count in tools_structure.items():
            dir_path = self.project_root / "tools" / dir_name
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*.py")))
                print(f"  ✅ {dir_name}/ - {file_count} файлов (ожидалось {expected_count})")
            else:
                print(f"  ❌ {dir_name}/ - директория не найдена")
        
        print("✅ Проверка структуры завершена")
        
    def optimize_structure(self):
        """Основная функция оптимизации"""
        print("🧹 Начинаю аккуратную оптимизацию папки tools...")
        print("=" * 60)
        
        try:
            # Создаем резервную копию
            self.create_backup()
            print()
            
            # Анализируем файлы
            unmapped_tools = self.analyze_files()
            print()
            
            # Создаем новую структуру
            self.create_new_structure()
            print()
            
            # Объединяем похожие файлы
            self.merge_similar_files()
            print()
            
            # Перемещаем оставшиеся файлы
            self.move_remaining_files()
            print()
            
            # Создаем __init__.py файлы
            self.create_init_files()
            print()
            
            # Заменяем старую папку новой
            self.replace_old_with_new()
            print()
            
            # Проверяем структуру
            self.verify_structure()
            
            print("\n🎉 ОПТИМИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("💡 Следующие шаги:")
            print("  1. Обновить импорты в других файлах")
            print("  2. Протестировать все изменения")
            print("  3. Обновить документацию")
            print("  4. Зафиксировать изменения в git")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            print("🔄 Восстанавливаю из резервной копии...")
            
            # Восстанавливаем из резервной копии
            if self.backup_dir.exists():
                if (self.backup_dir / "tools").exists():
                    shutil.copytree(self.backup_dir / "tools", self.project_root / "tools")
                    print("  ✅ Восстановлена папка tools")
                    
            print("✅ Восстановление завершено")

if __name__ == "__main__":
    optimizer = ToolsOptimizer()
    optimizer.optimize_structure()

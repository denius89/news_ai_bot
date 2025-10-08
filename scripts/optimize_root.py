#!/usr/bin/env python3
"""
🧹 Скрипт аккуратной оптимизации корня проекта PulseAI
Автор: AI Assistant
Версия: 1.0

Максимально аккуратно реорганизует структуру корня проекта
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class RootOptimizer:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "optimization_backup"
        
        # Определяем новые директории
        self.config_dir = self.project_root / "config_files"
        self.scripts_dir = self.project_root / "scripts"
        self.tests_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        self.archive_dir = self.project_root / "archive"
        
    def create_backup(self):
        """Создает резервную копию всех файлов"""
        print("🔄 Создаю резервную копию...")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Копируем все файлы из корня
        root_files = list(self.project_root.glob("*"))
        for item in root_files:
            if item.is_file() and not item.name.startswith('.'):
                dst = self.backup_dir / item.name
                shutil.copy2(item, dst)
                print(f"  ✅ Скопирован {item.name}")
        
        print(f"✅ Резервная копия создана в {self.backup_dir}")
        
    def create_directories(self):
        """Создает новые директории"""
        print("📁 Создаю новые директории...")
        
        directories = [
            self.config_dir,
            self.src_dir,
            self.archive_dir
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"  ✅ Создана директория {directory.name}")
            
        print("✅ Все директории созданы")
        
    def move_config_files(self):
        """Перемещает конфигурационные файлы"""
        print("⚙️ Перемещаю конфигурационные файлы...")
        
        config_files = [
            ".env", ".env.example",
            "mypy.ini", "pytest.ini", "setup.cfg",
            ".flake8", ".eslintrc.json", ".htmlhintrc",
            ".pre-commit-config.yaml", ".safety-ignore",
            ".editorconfig", ".cursorignore"
        ]
        
        moved_count = 0
        for file_name in config_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.config_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещен {file_name}")
                moved_count += 1
            else:
                print(f"  ⚠️ Файл {file_name} не найден")
                
        print(f"✅ Перемещено {moved_count} конфигурационных файлов")
        
    def move_test_files(self):
        """Перемещает тестовые файлы"""
        print("🧪 Перемещаю тестовые файлы...")
        
        test_files = list(self.project_root.glob("test_*.py"))
        moved_count = 0
        
        for test_file in test_files:
            dst = self.tests_dir / test_file.name
            shutil.move(str(test_file), str(dst))
            print(f"  ✅ Перемещен {test_file.name}")
            moved_count += 1
            
        print(f"✅ Перемещено {moved_count} тестовых файлов")
        
    def move_source_files(self):
        """Перемещает исходные файлы"""
        print("📄 Перемещаю исходные файлы...")
        
        source_files = [
            "main.py", "webapp.py"
        ]
        
        moved_count = 0
        for file_name in source_files:
            src = self.project_root / file_name
            if src.exists():
                dst = self.src_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещен {file_name}")
                moved_count += 1
            else:
                print(f"  ⚠️ Файл {file_name} не найден")
                
        print(f"✅ Перемещено {moved_count} исходных файлов")
        
    def move_archive_files(self):
        """Перемещает архивные файлы"""
        print("📦 Перемещаю архивные файлы...")
        
        moved_count = 0
        
        # Обрабатываем директорию archive_old (если она есть)
        archive_old = self.project_root / "archive_old"
        if archive_old.exists():
            print(f"  📁 Обрабатываю archive_old...")
            for item in archive_old.iterdir():
                if item.is_file():
                    dst = self.archive_dir / item.name
                    shutil.move(str(item), str(dst))
                    print(f"  ✅ Перемещен файл {item.name}")
                elif item.is_dir():
                    dst = self.archive_dir / item.name
                    shutil.move(str(item), str(dst))
                    print(f"  ✅ Перемещена директория {item.name}")
                moved_count += 1
            # Удаляем пустую директорию
            archive_old.rmdir()
            print(f"  ✅ Обработана директория archive_old")
        
        # Обрабатываем другие архивные директории в корне
        archive_items = [
            "backup_md_files", "backup_root_md_files"
        ]
        
        for item_name in archive_items:
            src = self.project_root / item_name
            if src.exists():
                dst = self.archive_dir / item_name
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещена {item_name}")
                moved_count += 1
            else:
                print(f"  ⚠️ Директория {item_name} не найдена")
                
        print(f"✅ Перемещено {moved_count} архивных элементов")
        
    def move_report_files(self):
        """Перемещает отчеты в docs"""
        print("📊 Перемещаю отчеты в docs...")
        
        report_files = [
            "STRUCTURE_REORGANIZATION_REPORT.md"
        ]
        
        docs_dir = self.project_root / "docs"
        moved_count = 0
        
        for file_name in report_files:
            src = self.project_root / file_name
            if src.exists():
                dst = docs_dir / file_name
                shutil.move(str(src), str(dst))
                print(f"  ✅ Перемещен {file_name}")
                moved_count += 1
            else:
                print(f"  ⚠️ Файл {file_name} не найден")
                
        print(f"✅ Перемещено {moved_count} отчетов")
        
    def remove_unused_files(self):
        """Удаляет неиспользуемые файлы"""
        print("🗑️ Удаляю неиспользуемые файлы...")
        
        unused_files = [
            "unused_main.py"
        ]
        
        removed_count = 0
        for file_name in unused_files:
            src = self.project_root / file_name
            if src.exists():
                src.unlink()
                print(f"  ✅ Удален {file_name}")
                removed_count += 1
            else:
                print(f"  ⚠️ Файл {file_name} не найден")
                
        print(f"✅ Удалено {removed_count} неиспользуемых файлов")
        
    def update_makefile(self):
        """Обновляет Makefile с новыми путями"""
        print("🔧 Обновляю Makefile...")
        
        makefile_path = self.project_root / "Makefile"
        if not makefile_path.exists():
            print("  ⚠️ Makefile не найден")
            return
            
        # Читаем текущий Makefile
        with open(makefile_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Обновляем пути к скриптам
        updates = [
            ("start_services.sh", "scripts/start_services.sh"),
            ("stop_services.sh", "scripts/stop_services.sh"),
            ("run_bot.sh", "scripts/run_bot.sh"),
            ("check_dependencies.sh", "scripts/check_dependencies.sh"),
            ("check_processes.sh", "scripts/check_processes.sh"),
        ]
        
        updated_content = content
        for old_path, new_path in updates:
            updated_content = updated_content.replace(old_path, new_path)
            
        # Записываем обновленный Makefile
        with open(makefile_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
            
        print("✅ Makefile обновлен")
        
    def verify_structure(self):
        """Проверяет новую структуру"""
        print("🔍 Проверяю новую структуру...")
        
        # Проверяем основные файлы в корне
        essential_files = [
            "README.md", "pyproject.toml", "requirements.txt", 
            "Makefile", "LICENSE", ".gitignore"
        ]
        
        missing_files = []
        for file_name in essential_files:
            if not (self.project_root / file_name).exists():
                missing_files.append(file_name)
                
        if missing_files:
            print(f"  ⚠️ Отсутствуют файлы: {missing_files}")
        else:
            print("  ✅ Все основные файлы на месте")
            
        # Проверяем новые директории
        new_dirs = [self.config_dir, self.src_dir, self.archive_dir]
        for directory in new_dirs:
            if directory.exists():
                file_count = len(list(directory.iterdir()))
                print(f"  ✅ {directory.name}/ - {file_count} элементов")
            else:
                print(f"  ⚠️ Директория {directory.name} не создана")
                
        print("✅ Проверка структуры завершена")
        
    def show_final_structure(self):
        """Показывает финальную структуру"""
        print("\n📁 ФИНАЛЬНАЯ СТРУКТУРА КОРНЯ:")
        print("=" * 50)
        
        # Показываем файлы в корне
        root_files = [f for f in self.project_root.iterdir() 
                     if f.is_file() and not f.name.startswith('.')]
        
        print(f"📄 Файлы в корне ({len(root_files)}):")
        for file_path in sorted(root_files):
            print(f"  📋 {file_path.name}")
            
        # Показываем директории
        root_dirs = [d for d in self.project_root.iterdir() 
                    if d.is_dir() and not d.name.startswith('.')]
        
        print(f"\n📁 Директории ({len(root_dirs)}):")
        for dir_path in sorted(root_dirs):
            file_count = len(list(dir_path.iterdir()))
            print(f"  📁 {dir_path.name}/ ({file_count} элементов)")
            
        print("\n🎯 РЕЗУЛЬТАТ:")
        print(f"  - Файлов в корне: {len(root_files)}")
        print(f"  - Директорий: {len(root_dirs)}")
        print("  - Структура оптимизирована!")
        
    def optimize_root(self):
        """Основная функция оптимизации"""
        print("🧹 Начинаю аккуратную оптимизацию корня PulseAI...")
        print("=" * 60)
        
        try:
            # Создаем резервную копию
            self.create_backup()
            print()
            
            # Создаем новые директории
            self.create_directories()
            print()
            
            # Перемещаем файлы по категориям
            self.move_config_files()
            print()
            
            self.move_test_files()
            print()
            
            self.move_source_files()
            print()
            
            self.move_archive_files()
            print()
            
            self.move_report_files()
            print()
            
            # Удаляем неиспользуемые файлы
            self.remove_unused_files()
            print()
            
            # Обновляем Makefile
            self.update_makefile()
            print()
            
            # Проверяем структуру
            self.verify_structure()
            print()
            
            # Показываем результат
            self.show_final_structure()
            
            print("\n🎉 ОПТИМИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("💡 Следующие шаги:")
            print("  1. Проверьте работоспособность скриптов")
            print("  2. Обновите документацию")
            print("  3. Протестируйте все команды")
            print("  4. Зафиксируйте изменения в git")
            
        except Exception as e:
            print(f"\n❌ ОШИБКА: {e}")
            print("🔄 Восстанавливаю из резервной копии...")
            
            # Восстанавливаем из резервной копии
            if self.backup_dir.exists():
                for backup_file in self.backup_dir.iterdir():
                    dst = self.project_root / backup_file.name
                    shutil.copy2(backup_file, dst)
                    print(f"  ✅ Восстановлен {backup_file.name}")
                    
            print("✅ Восстановление завершено")

if __name__ == "__main__":
    optimizer = RootOptimizer()
    optimizer.optimize_root()

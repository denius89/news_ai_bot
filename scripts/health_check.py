#!/usr/bin/env python3
"""
Система проверки зависимостей и здоровья проекта.

Этот скрипт проверяет все критические компоненты проекта
перед запуском сервисов.
"""

import sys
import os
from pathlib import Path
from typing import List

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config.paths import PATHS, ensure_path_exists
except ImportError:
    # Fallback если config.paths недоступен
    PATHS = {}

    def ensure_path_exists(key):
        return Path(key)


class HealthChecker:
    """Проверяет здоровье проекта."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def check_paths(self) -> bool:
        """Проверяет существование критических путей."""
        print("🔍 Проверка путей...")

        critical_paths = ["webapp_dist", "webapp_index", "logs", "config", "ai_modules", "utils", "telegram_bot"]

        for path_key in critical_paths:
            try:
                ensure_path_exists(path_key)
                print(f"  ✅ {path_key}: {PATHS[path_key]}")
            except FileNotFoundError as e:
                self.errors.append(str(e))
                print(f"  ❌ {path_key}: НЕ НАЙДЕН")

        return len(self.errors) == 0

    def check_imports(self) -> bool:
        """Проверяет критические импорты."""
        print("\n🔍 Проверка импортов...")

        critical_imports = [
            ("config.core.settings", "Настройки проекта"),
            ("utils.ai.ai_client", "AI клиент"),
            ("telegram_bot.handlers", "Обработчики бота"),
            ("database.service", "Сервис базы данных"),
            ("ai_modules.credibility", "Модуль достоверности"),
        ]

        for module, description in critical_imports:
            try:
                __import__(module)
                print(f"  ✅ {module}: {description}")
            except ImportError as e:
                self.errors.append(f"Ошибка импорта {module}: {e}")
                print(f"  ❌ {module}: {description} - ОШИБКА")

        return len(self.errors) == 0

    def check_environment(self) -> bool:
        """Проверяет переменные окружения."""
        print("\n🔍 Проверка переменных окружения...")

        required_env = [
            "TELEGRAM_BOT_TOKEN",
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_KEY",
        ]

        for env_var in required_env:
            if os.getenv(env_var):
                print(f"  ✅ {env_var}: установлена")
            else:
                self.warnings.append(f"Переменная {env_var} не установлена")
                print(f"  ⚠️ {env_var}: НЕ УСТАНОВЛЕНА")

        return True  # Переменные не критичны для проверки

    def check_processes(self) -> bool:
        """Проверяет запущенные процессы."""
        print("\n🔍 Проверка процессов...")

        import subprocess

        try:
            # Проверяем процессы Python
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True)
            python_processes = [
                line for line in result.stdout.split("\n") if "python" in line and "webapp" in line or "bot" in line
            ]

            if python_processes:
                print(f"  ⚠️ Найдено {len(python_processes)} процессов Python:")
                for proc in python_processes[:3]:  # Показываем только первые 3
                    print(f"    {proc.split()[1]}: {proc.split()[10:12]}")
                self.warnings.append("Обнаружены запущенные процессы Python")
            else:
                print("  ✅ Процессы Python не найдены")

        except Exception as e:
            self.warnings.append(f"Не удалось проверить процессы: {e}")

        return True

    def run_all_checks(self) -> bool:
        """Запускает все проверки."""
        print("🛡️ ПРОВЕРКА ЗДОРОВЬЯ ПРОЕКТА")
        print("=" * 40)

        checks = [
            self.check_paths,
            self.check_imports,
            self.check_environment,
            self.check_processes,
        ]

        all_passed = True
        for check in checks:
            if not check():
                all_passed = False

        # Выводим результаты
        print("\n" + "=" * 40)
        if self.errors:
            print("❌ ОШИБКИ:")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.warnings:
                print(f"  • {warning}")

        if all_passed and not self.errors:
            print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
            return True
        else:
            print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
            return False


def main():
    """Основная функция."""
    checker = HealthChecker()
    success = checker.run_all_checks()

    if not success:
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("  1. Проверьте структуру проекта")
        print("  2. Установите зависимости: pip install -r requirements.txt")
        print("  3. Соберите React: cd webapp && npm run build")
        print("  4. Настройте переменные окружения")
        sys.exit(1)

    print("\n🚀 Проект готов к запуску!")


if __name__ == "__main__":
    main()

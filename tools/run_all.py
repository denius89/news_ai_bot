#!/usr/bin/env python3
"""
Скрипт-оркестратор для запуска Telegram-бота и WebApp одной командой.
Поддерживает команды: start, stop, restart, status, logs
"""

import os
import sys
import time
import argparse
import subprocess
from pathlib import Path
from typing import List

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

    ensure_dirs,
    write_pid,
    read_pid,
    is_running,
    kill_gracefully,
    find_entrypoints,
    check_port_available,
    find_webapp_port,
    cleanup_pid_file,
    find_processes_by_command,
    load_env_file,
)


class ProcessManager:
    """Менеджер процессов для бота и WebApp."""

    def __init__(self):
        self.entrypoints = find_entrypoints()
        self.processes = {}

    def start(self):
        """Запустить все процессы."""
        print("🚀 Запуск Telegram-бота и WebApp...")

        # Загружаем .env если доступен
        load_env_file()

        # Создаем необходимые директории
        ensure_dirs()

        # Проверяем, не запущены ли уже процессы
        self._stop_existing_processes()

        # Проверяем порт WebApp
        self._check_webapp_port()

        # Запускаем процессы
        success = True

        for name, command in self.entrypoints.items():
            if not self._start_process(name, command):
                success = False

        if success:
            print("✅ Все процессы запущены успешно!")
            print(f"📋 Логи бота: logs/bot.log")
            print(f"📋 Логи WebApp: logs/webapp.log")
            print("\nДля просмотра логов: make logs")
            print("Для остановки: make stop-all")
        else:
            print("❌ Некоторые процессы не удалось запустить")
            sys.exit(1)

    def stop(self):
        """Остановить все процессы."""
        print("🛑 Остановка процессов...")

        stopped_count = 0

        # Останавливаем процессы по PID файлам
        for name in ["bot", "webapp"]:
            pid = read_pid(name)
            if pid and is_running(pid):
                print(f"Останавливаем {name} (PID: {pid})...")
                if kill_gracefully(pid):
                    cleanup_pid_file(name)
                    stopped_count += 1
                    print(f"✅ {name} остановлен")
                else:
                    print(f"❌ Не удалось остановить {name}")

        # Если PID файлов нет, ищем процессы по командной строке
        if stopped_count == 0:
            command_patterns = []
            for name, command in self.entrypoints.items():
                if len(command) > 1:
                    command_patterns.append(command[1])  # Имя скрипта

            if command_patterns:
                pids = find_processes_by_command(command_patterns)
                for pid in pids:
                    if is_running(pid):
                        print(f"Останавливаем процесс (PID: {pid})...")
                        if kill_gracefully(pid):
                            stopped_count += 1
                            print(f"✅ Процесс {pid} остановлен")

        if stopped_count > 0:
            print(f"✅ Остановлено {stopped_count} процессов")
        else:
            print("ℹ️  Активные процессы не найдены")

    def restart(self):
        """Перезапустить все процессы."""
        print("🔄 Перезапуск процессов...")
        self.stop()
        time.sleep(2)  # Даем время на завершение
        self.start()

    def status(self):
        """Показать статус процессов."""
        print("📊 Статус процессов:")
        print("-" * 50)

        for name in ["bot", "webapp"]:
            pid = read_pid(name)
            if pid and is_running(pid):
                print(f"✅ {name.upper()}: запущен (PID: {pid})")

                # Показываем время последней модификации лога
                log_file = Path(f"logs/{name}.log")
                if log_file.exists():
                    mtime = log_file.stat().st_mtime
                    mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
                    print(f"   📝 Лог обновлен: {mtime_str}")
            else:
                print(f"❌ {name.upper()}: не запущен")

        # Проверяем порт WebApp
        port = find_webapp_port()
        if port:
            if check_port_available(port):
                print(f"🔌 Порт {port}: свободен")
            else:
                print(f"⚠️  Порт {port}: занят")

    def logs(self):
        """Показать логи процессов."""
        print("📋 Просмотр логов (последние 100 строк каждого):")
        print("-" * 60)

        for name in ["bot", "webapp"]:
            log_file = Path(f"logs/{name}.log")
            if log_file.exists():
                print(f"\n🔹 {name.upper()} LOGS:")
                print("-" * 30)
                try:
                    # Читаем последние 100 строк
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        last_lines = lines[-100:] if len(lines) > 100 else lines
                        for line in last_lines:
                            print(line.rstrip())
                except Exception as e:
                    print(f"Ошибка чтения лога: {e}")
            else:
                print(f"\n⚠️  Лог {name} не найден")

        print("\n💡 Для отслеживания логов в реальном времени используйте:")
        print("   tail -f logs/bot.log logs/webapp.log")

    def _stop_existing_processes(self):
        """Остановить существующие процессы перед запуском."""
        for name in ["bot", "webapp"]:
            pid = read_pid(name)
            if pid and is_running(pid):
                print(f"🔄 Останавливаем существующий процесс {name}...")
                kill_gracefully(pid)
                cleanup_pid_file(name)

    def _check_webapp_port(self):
        """Проверить доступность порта WebApp и освободить при необходимости."""
        port = find_webapp_port()
        if port and not check_port_available(port):
            print(f"⚠️  Порт {port} занят!")
            print("🛑 Пытаемся освободить порт...")

            # Пытаемся освободить порт
            if cleanup_pid_file('webapp'):
                print(f"✅ Процесс WebApp остановлен")
                time.sleep(2)  # Даем время порту освободиться

                # Проверяем еще раз
                if check_port_available(port):
                    print(f"✅ Порт {port} освобожден")
                else:
                    print(f"❌ Порт {port} все еще занят")
                    print("💡 Попробуйте: make free-ports")
            else:
                print("❌ Не удалось остановить процесс")
                print("💡 Попробуйте: make free-ports")

    def _start_process(self, name: str, command: List[str]) -> bool:
        """Запустить один процесс."""
        try:
            print(f"🚀 Запуск {name}...")

            # Открываем лог файл
            log_file = open(f"logs/{name}.log", "w", encoding="utf-8")

            # Запускаем процесс
            process = subprocess.Popen(
                command,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=project_root,
                env=os.environ.copy(),
            )

            # Сохраняем PID
            write_pid(name, process.pid)
            self.processes[name] = process

            # Даем время на запуск
            time.sleep(2)

            # Проверяем, что процесс еще жив
            if is_running(process.pid):
                print(f"✅ {name} запущен (PID: {process.pid})")
                return True
            else:
                print(f"❌ {name} не запустился")
                cleanup_pid_file(name)
                return False

        except Exception as e:
            print(f"❌ Ошибка запуска {name}: {e}")
            return False


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description="Управление Telegram-ботом и WebApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python tools/run_all.py start     # Запустить все
  python tools/run_all.py stop      # Остановить все  
  python tools/run_all.py restart   # Перезапустить все
  python tools/run_all.py status    # Показать статус
  python tools/run_all.py logs      # Показать логи

Или через Makefile:
  make run-all      # Запустить все
  make stop-all     # Остановить все
  make restart-all  # Перезапустить все
  make status       # Показать статус
  make logs         # Показать логи
        """,
    )

    parser.add_argument(
        "command",
        choices=["start", "stop", "restart", "status", "logs"],
        help="Команда для выполнения",
    )

    args = parser.parse_args()

    # Проверяем, что мы в корневой директории проекта
    if not Path("Makefile").exists() and not Path("webapp.py").exists():
        print("❌ Запустите скрипт из корневой директории проекта")
        sys.exit(1)

    manager = ProcessManager()

    # Проверяем, что найдены entrypoints
    if not manager.entrypoints:
        print("❌ Не найдены entrypoints для бота или WebApp")
        print("💡 Убедитесь, что файлы webapp.py и telegram_bot/bot.py существуют")
        sys.exit(1)

    print(f"🔍 Найдены entrypoints:")
    for name, command in manager.entrypoints.items():
        print(f"   {name}: {' '.join(command)}")
    print()

    # Выполняем команду
    if args.command == "start":
        manager.start()
    elif args.command == "stop":
        manager.stop()
    elif args.command == "restart":
        manager.restart()
    elif args.command == "status":
        manager.status()
    elif args.command == "logs":
        manager.logs()


if __name__ == "__main__":
    main()

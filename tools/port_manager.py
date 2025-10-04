#!/usr/bin/env python3
"""
Менеджер портов и процессов для PulseAI.
Автоматически проверяет и освобождает порты перед запуском тестов.
"""

import os
import sys
import time
import socket
import subprocess
import psutil
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class PortManager:
    """Менеджер для автоматического управления портами и процессами."""

    def __init__(self):
        # Исключаем системные порты (5000 - ControlCenter на macOS)
        self.default_ports = [8001, 8080, 3000, 8002, 8003, 9000, 9001]
        self.system_ports = [5000, 22, 80, 443, 53, 25, 110, 143, 993, 995]  # Системные порты
        self.process_names = ['webapp.py', 'telegram_bot/bot.py', 'main.py']

    def find_free_port(self, start_port: int = 8001, max_attempts: int = 20) -> Optional[int]:
        """Находит свободный порт, начиная с start_port, избегая системных портов."""
        for port in range(start_port, start_port + max_attempts):
            # Пропускаем системные порты
            if port in self.system_ports:
                continue
            if self.is_port_free(port):
                return port
        return None

    def is_port_free(self, port: int) -> bool:
        """Проверяет, свободен ли порт."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return True
            except OSError:
                return False

    def get_processes_on_port(self, port: int) -> List[Dict]:
        """Возвращает информацию о процессах, использующих порт."""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        processes.append(
                            {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': ' '.join(proc.info['cmdline'] or []),
                            }
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def kill_process_on_port(self, port: int, force: bool = False) -> bool:
        """Убивает процесс, использующий порт."""
        # Не трогаем системные порты
        if port in self.system_ports:
            print(f"⚠️ Порт {port} - системный, не трогаем")
            return False

        processes = self.get_processes_on_port(port)
        killed = False

        for proc_info in processes:
            pid = proc_info['pid']
            try:
                process = psutil.Process(pid)

                # Проверяем, что это наш процесс
                if self.is_our_process(proc_info['cmdline']):
                    print(f"🛑 Убиваем наш процесс {pid} ({proc_info['name']}) на порту {port}")
                    if force:
                        process.kill()
                    else:
                        process.terminate()

                    # Ждем завершения
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        if force:
                            process.kill()
                        else:
                            print(f"⚠️ Процесс {pid} не завершился, принудительно убиваем")
                            process.kill()
                    killed = True
                else:
                    print(f"⚠️ Порт {port} занят внешним процессом {pid} ({proc_info['name']})")
                    print(f"   Команда: {proc_info['cmdline']}")

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return killed

    def is_our_process(self, cmdline: str) -> bool:
        """Проверяет, является ли процесс нашим (PulseAI)."""
        our_indicators = ['webapp.py', 'telegram_bot', 'news_ai_bot', 'pulseai']
        return any(indicator.lower() in cmdline.lower() for indicator in our_indicators)

    def find_duplicate_processes(self) -> List[Dict]:
        """Находит дублирующие процессы PulseAI."""
        duplicates = []

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])

                # Проверяем, является ли процесс нашим
                if self.is_our_process(cmdline):
                    # Проверяем, не является ли это текущим процессом
                    if proc.info['pid'] != os.getpid():
                        duplicates.append(
                            {
                                'pid': proc.info['pid'],
                                'name': proc.info['name'],
                                'cmdline': cmdline,
                                'create_time': proc.info['create_time'],
                                'age': time.time() - proc.info['create_time'],
                            }
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return duplicates

    def cleanup_duplicate_processes(self, force: bool = False) -> int:
        """Очищает дублирующие процессы."""
        duplicates = self.find_duplicate_processes()
        killed_count = 0

        if duplicates:
            print(f"🔄 Найдено {len(duplicates)} дублирующих процессов PulseAI:")

            for proc_info in duplicates:
                age_minutes = proc_info['age'] / 60
                print(
                    f"   PID {proc_info['pid']}: {proc_info['cmdline'][:80]}... (возраст: {age_minutes:.1f} мин)"
                )

                try:
                    process = psutil.Process(proc_info['pid'])

                    if force or age_minutes > 1:  # Убиваем процессы старше 1 минуты
                        print(f"   🛑 Убиваем процесс {proc_info['pid']}")
                        if force:
                            process.kill()
                        else:
                            process.terminate()

                        try:
                            process.wait(timeout=3)
                        except psutil.TimeoutExpired:
                            process.kill()
                        killed_count += 1
                    else:
                        print(f"   ⏳ Оставляем молодой процесс {proc_info['pid']}")

                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        else:
            print("✅ Дублирующих процессов не найдено")

        return killed_count

    def prepare_environment(self, force: bool = False) -> Dict:
        """Подготавливает окружение: очищает процессы и находит свободные порты."""
        print("🔧 Подготовка окружения для тестов...")

        result = {'ports_freed': 0, 'processes_killed': 0, 'free_ports': {}, 'warnings': []}

        # 1. Очищаем дублирующие процессы
        print("\n1️⃣ Проверка дублирующих процессов...")
        result['processes_killed'] = self.cleanup_duplicate_processes(force)

        # 2. Проверяем и освобождаем порты (исключаем системные)
        print("\n2️⃣ Проверка портов...")
        for port in self.default_ports:
            if port in self.system_ports:
                print(f"⏭️ Порт {port} - системный, пропускаем")
                continue

            if not self.is_port_free(port):
                print(f"⚠️ Порт {port} занят")

                if self.kill_process_on_port(port, force):
                    result['ports_freed'] += 1
                    time.sleep(1)  # Даем время порту освободиться

                    if self.is_port_free(port):
                        print(f"✅ Порт {port} освобожден")
                    else:
                        result['warnings'].append(
                            f"Порт {port} все еще занят после попытки освобождения"
                        )
                else:
                    result['warnings'].append(f"Не удалось освободить порт {port}")
            else:
                print(f"✅ Порт {port} свободен")

        # 3. Находим свободные порты для использования
        print("\n3️⃣ Поиск свободных портов для использования...")
        for service, start_port in [('webapp', 8001), ('api', 5001), ('test', 8080)]:
            free_port = self.find_free_port(start_port)
            if free_port:
                result['free_ports'][service] = free_port
                print(f"✅ {service}: порт {free_port}")
            else:
                result['warnings'].append(f"Не удалось найти свободный порт для {service}")

        # 4. Итоговый отчет
        print(f"\n📊 Итоговый отчет:")
        print(f"   Убито дублирующих процессов: {result['processes_killed']}")
        print(f"   Освобождено портов: {result['ports_freed']}")
        print(f"   Найдено свободных портов: {len(result['free_ports'])}")

        if result['warnings']:
            print(f"\n⚠️ Предупреждения:")
            for warning in result['warnings']:
                print(f"   - {warning}")

        return result


def main():
    """CLI для управления портами и процессами."""
    import argparse

    parser = argparse.ArgumentParser(description='Менеджер портов и процессов PulseAI')
    parser.add_argument(
        '--check', action='store_true', help='Проверить состояние портов и процессов'
    )
    parser.add_argument(
        '--cleanup', action='store_true', help='Очистить дублирующие процессы и порты'
    )
    parser.add_argument('--force', action='store_true', help='Принудительная очистка')
    parser.add_argument('--prepare', action='store_true', help='Подготовить окружение для тестов')

    args = parser.parse_args()

    manager = PortManager()

    if args.check:
        print("🔍 Проверка состояния...")

        # Проверяем порты
        print("\n📡 Проверка портов:")
        for port in manager.default_ports:
            if manager.is_port_free(port):
                print(f"   ✅ Порт {port}: свободен")
            else:
                processes = manager.get_processes_on_port(port)
                print(f"   ❌ Порт {port}: занят")
                for proc in processes:
                    print(f"      PID {proc['pid']}: {proc['name']} - {proc['cmdline'][:60]}...")

        # Проверяем дублирующие процессы
        print("\n🔄 Проверка дублирующих процессов:")
        duplicates = manager.find_duplicate_processes()
        if duplicates:
            print(f"   Найдено {len(duplicates)} дублирующих процессов:")
            for proc in duplicates:
                age_min = proc['age'] / 60
                print(
                    f"   PID {proc['pid']}: {proc['cmdline'][:60]}... (возраст: {age_min:.1f} мин)"
                )
        else:
            print("   ✅ Дублирующих процессов не найдено")

    elif args.cleanup:
        print("🧹 Очистка процессов и портов...")

        # Очищаем дублирующие процессы
        killed = manager.cleanup_duplicate_processes(args.force)
        print(f"Убито процессов: {killed}")

        # Освобождаем порты
        freed = 0
        for port in manager.default_ports:
            if not manager.is_port_free(port):
                if manager.kill_process_on_port(port, args.force):
                    freed += 1
                    time.sleep(1)
        print(f"Освобождено портов: {freed}")

    elif args.prepare:
        result = manager.prepare_environment(args.force)

        # Возвращаем код выхода на основе результата
        # Критическими считаем только предупреждения о невозможности найти свободные порты
        critical_warnings = [
            w for w in result['warnings'] if 'не удалось найти свободный порт' in w
        ]

        # Если у нас есть свободные порты для всех сервисов, то все хорошо
        if len(result['free_ports']) >= 3:  # webapp, api, test
            print(f"\n✅ Достаточно свободных портов найдено ({len(result['free_ports'])}/3)")
            if critical_warnings:
                print(f"⚠️ Есть предупреждения, но они не критичны:")
                for warning in critical_warnings:
                    print(f"   - {warning}")
            sys.exit(0)  # Все хорошо
        elif critical_warnings:
            print(f"\n❌ Критические предупреждения:")
            for warning in critical_warnings:
                print(f"   - {warning}")
            sys.exit(1)  # Есть критические предупреждения
        else:
            sys.exit(0)  # Все хорошо

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

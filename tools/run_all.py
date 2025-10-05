#!/usr/bin/env python3
"""
Управление всеми процессами PulseAI (бот + WebApp).
"""

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))

def kill_processes():
    """Убивает все процессы бота и веб-приложения."""
    try:
        # Убиваем процессы по имени
        subprocess.run(["pkill", "-f", "telegram_bot.bot"], check=False)
        subprocess.run(["pkill", "-f", "webapp.py"], check=False)
        print("🛑 Остановлены все процессы")
    except Exception as e:
        print(f"⚠️ Ошибка при остановке процессов: {e}")

def start_processes():
    """Запускает бота и веб-приложение в фоне."""
    try:
        # Создаем директорию для логов если не существует
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Запускаем бота
        print("🤖 Запуск Telegram бота...")
        bot_process = subprocess.Popen([
            sys.executable, "-m", "telegram_bot.bot"
        ], stdout=open("logs/bot.log", "w"), stderr=subprocess.STDOUT)
        
        time.sleep(2)  # Даем боту время запуститься
        
        # Запускаем веб-приложение
        print("🌐 Запуск WebApp...")
        webapp_process = subprocess.Popen([
            sys.executable, "webapp.py"
        ], stdout=open("logs/webapp.log", "w"), stderr=subprocess.STDOUT)
        
        # Сохраняем PID процессов
        with open("logs/bot.pid", "w") as f:
            f.write(str(bot_process.pid))
        with open("logs/webapp.pid", "w") as f:
            f.write(str(webapp_process.pid))
        
        print("✅ Все процессы запущены!")
        print(f"🤖 Бот PID: {bot_process.pid}")
        print(f"🌐 WebApp PID: {webapp_process.pid}")
        print("📝 Логи: logs/bot.log, logs/webapp.log")
        
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        return False
    
    return True

def show_status():
    """Показывает статус процессов."""
    print("📊 Статус процессов PulseAI:")
    
    # Проверяем бота
    try:
        result = subprocess.run(["pgrep", "-f", "telegram_bot.bot"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Telegram бот: Запущен")
        else:
            print("❌ Telegram бот: Остановлен")
    except:
        print("❌ Telegram бот: Статус неизвестен")
    
    # Проверяем веб-приложение
    try:
        result = subprocess.run(["pgrep", "-f", "webapp.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ WebApp: Запущен")
        else:
            print("❌ WebApp: Остановлен")
    except:
        print("❌ WebApp: Статус неизвестен")
    
    # Проверяем порты
    try:
        result = subprocess.run(["lsof", "-i", ":8001"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ WebApp доступен на порту 8001")
        else:
            print("❌ WebApp недоступен на порту 8001")
    except:
        print("❓ Статус порта 8001 неизвестен")

def show_logs():
    """Показывает логи процессов."""
    print("📝 Логи процессов:")
    
    bot_log = Path("logs/bot.log")
    webapp_log = Path("logs/webapp.log")
    
    if bot_log.exists():
        print(f"\n🤖 Последние 10 строк лога бота ({bot_log}):")
        try:
            with open(bot_log, "r") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"❌ Ошибка чтения лога бота: {e}")
    else:
        print("❌ Лог бота не найден")
    
    if webapp_log.exists():
        print(f"\n🌐 Последние 10 строк лога WebApp ({webapp_log}):")
        try:
            with open(webapp_log, "r") as f:
                lines = f.readlines()
                for line in lines[-10:]:
                    print(f"  {line.strip()}")
        except Exception as e:
            print(f"❌ Ошибка чтения лога WebApp: {e}")
    else:
        print("❌ Лог WebApp не найден")

def main():
    parser = argparse.ArgumentParser(description="Управление процессами PulseAI")
    parser.add_argument("action", choices=["start", "stop", "restart", "status", "logs"],
                       help="Действие для выполнения")
    
    args = parser.parse_args()
    
    if args.action == "start":
        kill_processes()
        time.sleep(1)
        start_processes()
    elif args.action == "stop":
        kill_processes()
    elif args.action == "restart":
        kill_processes()
        time.sleep(2)
        start_processes()
    elif args.action == "status":
        show_status()
    elif args.action == "logs":
        show_logs()

if __name__ == "__main__":
    main()
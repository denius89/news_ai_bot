"""
Утилиты для управления процессами Telegram-бота и WebApp.
Поддерживает обнаружение entrypoints, управление PID-файлами и graceful shutdown.
"""

import os
import sys
import signal
import time
import subprocess
import glob
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import re


def ensure_dirs():
    """Создать необходимые директории при отсутствии."""
    dirs = ["logs", ".runtime"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)


def write_pid(name: str, pid: int):
    """Записать PID в файл."""
    pid_file = Path(".runtime") / f"{name}.pid"
    pid_file.write_text(str(pid))


def read_pid(name: str) -> Optional[int]:
    """Прочитать PID из файла."""
    pid_file = Path(".runtime") / f"{name}.pid"
    if not pid_file.exists():
        return None
    try:
        return int(pid_file.read_text().strip())
    except (ValueError, OSError):
        return None


def is_running(pid: int) -> bool:
    """Проверить, жив ли процесс."""
    if pid is None:
        return False
    try:
        if sys.platform == "win32":
            # На Windows используем tasklist
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False
            )
            return str(pid) in result.stdout
        else:
            # На Unix-системах используем kill(0) для проверки
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.CalledProcessError):
        return False


def kill_gracefully(pid: int, timeout: int = 5):
    """Graceful завершение процесса с таймаутом."""
    if not is_running(pid):
        return True
    
    try:
        if sys.platform == "win32":
            # На Windows используем CTRL_BREAK_EVENT
            os.kill(pid, signal.CTRL_BREAK_EVENT)
        else:
            # На Unix отправляем SIGTERM
            os.kill(pid, signal.SIGTERM)
        
        # Ждем завершения
        for _ in range(timeout * 10):  # Проверяем каждые 0.1 секунды
            if not is_running(pid):
                return True
            time.sleep(0.1)
        
        # Если не завершился - принудительно
        if is_running(pid):
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
            else:
                os.kill(pid, signal.SIGKILL)
            time.sleep(0.5)  # Даем время на завершение
            
        return not is_running(pid)
        
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Ошибка при завершении процесса {pid}: {e}")
        return False


def detect_python() -> str:
    """Определить команду Python."""
    return sys.executable


def find_entrypoints() -> Dict[str, List[str]]:
    """
    Найти entrypoints для бота и WebApp.
    Сначала проверяет Makefile, затем сканирует код.
    """
    # Проверяем Makefile
    makefile_path = Path("Makefile")
    if makefile_path.exists():
        makefile_content = makefile_path.read_text()
        
        # Ищем существующие цели
        if "run-bot:" in makefile_content and "run-web:" in makefile_content:
            return {
                "bot": ["make", "run-bot"],
                "webapp": ["make", "run-web"]
            }
    
    # Если Makefile целей нет - сканируем код
    entrypoints = {}
    
    # Поиск bot entrypoint
    bot_candidates = [
        "telegram_bot/bot.py",
        "main.py", 
        "bot.py"
    ]
    
    for candidate in bot_candidates:
        if Path(candidate).exists():
            if _is_bot_entrypoint(candidate):
                entrypoints["bot"] = [detect_python(), candidate]
                break
    
    # Поиск webapp entrypoint  
    webapp_candidates = [
        "webapp.py",
        "app.py",
        "main.py"
    ]
    
    for candidate in webapp_candidates:
        if Path(candidate).exists():
            if _is_webapp_entrypoint(candidate):
                entrypoints["webapp"] = [detect_python(), candidate]
                break
    
    return entrypoints


def _is_bot_entrypoint(file_path: str) -> bool:
    """Проверить, является ли файл entrypoint для бота."""
    try:
        content = Path(file_path).read_text()
        
        # Ищем признаки Telegram-бота
        bot_indicators = [
            "aiogram",
            "telebot", 
            "telegram",
            "from aiogram",
            "import aiogram",
            "from telebot",
            "import telebot"
        ]
        
        has_bot_imports = any(indicator in content for indicator in bot_indicators)
        has_main_block = 'if __name__ == "__main__":' in content
        
        return has_bot_imports and has_main_block
        
    except (OSError, UnicodeDecodeError):
        return False


def _is_webapp_entrypoint(file_path: str) -> bool:
    """Проверить, является ли файл entrypoint для WebApp."""
    try:
        content = Path(file_path).read_text()
        
        # Ищем признаки Web-приложения
        webapp_indicators = [
            "Flask",
            "FastAPI",
            "uvicorn",
            "from flask",
            "import flask",
            "from fastapi",
            "import fastapi",
            "app.run(",
            "uvicorn.run("
        ]
        
        has_webapp_imports = any(indicator in content for indicator in webapp_indicators)
        has_main_block = 'if __name__ == "__main__":' in content
        
        return has_webapp_imports and has_main_block
        
    except (OSError, UnicodeDecodeError):
        return False


def check_port_available(port: int) -> bool:
    """Проверить, свободен ли порт."""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0
    except Exception:
        return True


def find_webapp_port() -> Optional[int]:
    """Попытаться определить порт WebApp из кода или переменных окружения."""
    # Проверяем переменные окружения
    port_env = os.getenv("WEBAPP_PORT") or os.getenv("PORT") or os.getenv("FLASK_PORT")
    if port_env:
        try:
            return int(port_env)
        except ValueError:
            pass
    
    # Проверяем webapp.py
    webapp_path = Path("webapp.py")
    if webapp_path.exists():
        try:
            content = webapp_path.read_text()
            # Ищем app.run(port=...)
            port_match = re.search(r'app\.run\([^)]*port\s*=\s*(\d+)', content)
            if port_match:
                return int(port_match.group(1))
            
            # Ищем переменную WEBAPP_PORT
            port_var_match = re.search(r'WEBAPP_PORT\s*=\s*(\d+)', content)
            if port_var_match:
                return int(port_var_match.group(1))
                
        except (OSError, UnicodeDecodeError):
            pass
    
    # Проверяем config/settings.py
    settings_path = Path("config/settings.py")
    if settings_path.exists():
        try:
            content = settings_path.read_text()
            port_match = re.search(r'WEBAPP_PORT\s*=\s*(\d+)', content)
            if port_match:
                return int(port_match.group(1))
        except (OSError, UnicodeDecodeError):
            pass
    
    # По умолчанию Flask порт
    return 5000


def cleanup_pid_file(name: str):
    """Удалить PID файл."""
    pid_file = Path(".runtime") / f"{name}.pid"
    if pid_file.exists():
        try:
            pid_file.unlink()
        except OSError:
            pass


def find_processes_by_command(command_patterns: List[str]) -> List[int]:
    """Найти процессы по паттернам командной строки."""
    if sys.platform == "win32":
        return _find_processes_windows(command_patterns)
    else:
        return _find_processes_unix(command_patterns)


def _find_processes_windows(command_patterns: List[str]) -> List[int]:
    """Найти процессы на Windows."""
    try:
        result = subprocess.run(
            ["wmic", "process", "get", "processid,commandline", "/format:csv"],
            capture_output=True,
            text=True,
            check=False
        )
        
        pids = []
        for line in result.stdout.split('\n'):
            if any(pattern in line for pattern in command_patterns):
                parts = line.split(',')
                if len(parts) >= 2:
                    try:
                        pids.append(int(parts[-1].strip()))
                    except ValueError:
                        pass
        return pids
        
    except Exception:
        return []


def _find_processes_unix(command_patterns: List[str]) -> List[int]:
    """Найти процессы на Unix-системах."""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            check=False
        )
        
        pids = []
        for line in result.stdout.split('\n'):
            if any(pattern in line for pattern in command_patterns):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        pids.append(int(parts[1]))
                    except ValueError:
                        pass
        return pids
        
    except Exception:
        return []


def load_env_file():
    """Загрузить .env файл если доступен python-dotenv."""
    try:
        from dotenv import load_dotenv
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)
            return True
    except ImportError:
        # python-dotenv не установлен - это нормально
        pass
    return False

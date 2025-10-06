# tests/conftest.py
import pytest
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from tools.port_manager import PortManager

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Автоматически загружает переменные из .env
    перед запуском всех тестов.
    """
    load_dotenv()


@pytest.fixture(scope="session", autouse=True)
def prepare_test_environment():
    """
    Автоматически подготавливает окружение перед запуском тестов:
    - Очищает дублирующие процессы
    - Освобождает занятые порты
    - Проверяет доступность ресурсов
    """
    print("\n🔧 Подготовка окружения для тестов...")

    manager = PortManager()

    # Подготавливаем окружение
    result = manager.prepare_environment(force=False)

    # Если есть критические предупреждения, прерываем тесты
    # Исключаем предупреждения о порте 5000 (системный процесс ControlCenter)
    critical_warnings = [w for w in result["warnings"] if "не удалось найти свободный порт" in w and "5000" not in w]

    if critical_warnings:
        print("\n❌ Критические ошибки при подготовке окружения:")
        for warning in critical_warnings:
            print(f"   - {warning}")
        print("\n💡 Попробуйте:")
        print("   make free-ports")
        print("   python tools/port_manager.py --cleanup")
        pytest.exit("Окружение не готово для тестов", returncode=1)

    # Сохраняем информацию о свободных портах для использования в тестах
    os.environ["TEST_WEBAPP_PORT"] = str(result["free_ports"].get("webapp", 8001))
    os.environ["TEST_API_PORT"] = str(result["free_ports"].get("api", 5000))

    print("✅ Окружение готово для тестов")
    print(f"   WebApp порт: {os.environ['TEST_WEBAPP_PORT']}")
    print(f"   API порт: {os.environ['TEST_API_PORT']}")

    yield result

    print("\n🧹 Очистка после тестов...")
    # Можно добавить очистку ресурсов после тестов


@pytest.fixture
def test_ports():
    """
    Предоставляет свободные порты для использования в тестах.
    """
    return {
        "webapp": int(os.environ.get("TEST_WEBAPP_PORT", 8001)),
        "api": int(os.environ.get("TEST_API_PORT", 5000)),
        "test": 8080,
    }


@pytest.fixture
def port_manager():
    """
    Предоставляет экземпляр PortManager для использования в тестах.
    """
    return PortManager()

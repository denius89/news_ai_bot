# tests/conftest.py
import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def load_env():
    """
    Автоматически загружает переменные из .env
    перед запуском всех тестов.
    """
    load_dotenv()

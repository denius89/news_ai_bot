import os
import pytest
from supabase import create_client
from dotenv import load_dotenv

@pytest.mark.integration
def test_supabase():
    """Интеграционный тест: проверка подключения к Supabase"""

    load_dotenv(dotenv_path=".env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        pytest.skip("❌ Нет ключей Supabase в .env")

    supabase = create_client(url, key)
    data = supabase.table("news").select("*").execute()

    # Проверяем, что запрос вернул структуру с данными
    assert isinstance(data.data, list)
    print("✅ Подключение к Supabase работает, записей в news:", len(data.data))


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_supabase()
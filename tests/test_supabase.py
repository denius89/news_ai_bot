import os
import pytest
from supabase import create_client
from dotenv import load_dotenv

@pytest.mark.integration
def test_supabase():
    load_dotenv(dotenv_path=".env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    assert url and key, "❌ Нет ключей Supabase"

    supabase = create_client(url, key)
    data = supabase.table("news").select("*").execute()
    assert isinstance(data.data, list)
    print("✅ Подключение к Supabase работает, записей в news:", len(data.data))


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_supabase()
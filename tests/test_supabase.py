"""
Интеграционный тест для проверки подключения к Supabase.
"""

import os
import pytest
from dotenv import load_dotenv
from supabase import create_client


@pytest.mark.integration
def test_supabase():
    """Проверка, что клиент Supabase инициализируется и возвращает данные."""

    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        pytest.skip("❌ Пропущен: нет SUPABASE_URL и SUPABASE_KEY в .env")

    client = create_client(url, key)
    response = client.table("news").select("*").limit(1).execute()

    assert isinstance(response.data, list)
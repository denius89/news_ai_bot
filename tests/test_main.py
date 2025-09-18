import subprocess
import os
from supabase import create_client
from dotenv import load_dotenv

def test_main_etl():
    """
    E2E тест: запускает main.py и проверяет,
    что в Supabase есть новости с полями credibility и importance.
    """
    load_dotenv()

    # Запуск main.py с ограничением 2 новости
    result = subprocess.run(
        ["python", "main.py", "--source", "crypto", "--limit", "2"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"main.py завершился с ошибкой: {result.stderr}"

    # Подключение к Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    client = create_client(url, key)

    # Проверяем наличие новостей
    response = client.table("news").select("*").order("id", desc=True).limit(5).execute()
    assert len(response.data) > 0, "Новости не найдены в базе"

    # Проверяем, что хотя бы у одной записи есть credibility и importance
    has_ai_fields = any(
        (item.get("credibility") is not None and item.get("importance") is not None)
        for item in response.data
    )
    assert has_ai_fields, "Нет записей с полями credibility и importance"
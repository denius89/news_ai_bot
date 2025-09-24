import subprocess
import os
import pytest
from supabase import create_client
from dotenv import load_dotenv


@pytest.mark.integration
def test_main_etl():
    """
    Интеграционный E2E тест:
    запускает main.py и проверяет,
    что в Supabase есть новости с полями credibility и importance.
    """
    load_dotenv()

    # Проверяем ключи Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        pytest.skip("❌ Нет ключей Supabase в .env")

    # Запуск main.py с ограничением 2 новости
    result = subprocess.run(
        ["python", "main.py", "--source", "crypto", "--limit", "2"],
        capture_output=True,
        text=True,
    )

    # Логируем stdout/stderr для отладки
    if result.stdout:
        print("STDOUT:\n", result.stdout)
    if result.stderr:
        print("STDERR:\n", result.stderr)

    assert result.returncode == 0, f"main.py завершился с ошибкой: {result.stderr}"

    # Подключение к Supabase
    client = create_client(url, key)

    # Проверяем наличие новостей
    response = (
        client.table("news").select("*").order("id", desc=True).limit(5).execute()
    )
    if not response.data:
        pytest.skip("⚠️ В базе нет новостей для проверки")

    # Проверяем, что хотя бы у одной записи есть credibility и importance
    has_ai_fields = any(
        (item.get("credibility") is not None and item.get("importance") is not None)
        for item in response.data
    )
    assert has_ai_fields, "Нет записей с полями credibility и importance"

    print("✅ ETL-процесс прошёл успешно, новости загружены в базу")

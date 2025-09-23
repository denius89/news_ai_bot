# tests/test_deepl.py

import os
import pytest
import deepl
from dotenv import load_dotenv

@pytest.mark.integration
def test_deepl():
    """Интеграционный тест: проверка подключения к DeepL API"""

    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("DEEPL_API_KEY")

    if not api_key:
        pytest.skip("❌ Нет ключа DEEPL_API_KEY в .env")

    translator = deepl.Translator(api_key)
    result = translator.translate_text("Hello, world!", target_lang="RU")

    # Проверка, что перевод не пустой
    assert result.text and isinstance(result.text, str)

    print("✅ DeepL работает, перевод:", result.text)


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_deepl()
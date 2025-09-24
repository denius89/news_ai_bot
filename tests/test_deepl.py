import os
import pytest
import deepl
from dotenv import load_dotenv


@pytest.mark.integration
def test_deepl():
    """Проверка подключения к DeepL API"""
    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("DEEPL_API_KEY")

    assert api_key, "❌ Ключ DeepL не найден"

    translator = deepl.Translator(api_key)
    result = translator.translate_text("Hello, world!", target_lang="RU")
    assert "Привет" in result.text or len(result.text) > 0
    print("✅ DeepL работает, перевод:", result.text)


if __name__ == "__main__":
    # Локальный запуск (в обход pytest)
    test_deepl()

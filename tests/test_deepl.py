import os
import pytest
import deepl
from dotenv import load_dotenv


@pytest.mark.integration
def test_deepl_translation():
    """Интеграционный тест: перевод через DeepL API"""
    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("DEEPL_API_KEY")

    if not api_key:
        pytest.skip("❌ Ключ DeepL не найден в .env")

    translator = deepl.Translator(api_key)

    # EN → RU
    result_ru = translator.translate_text("Hello, world!", target_lang="RU")
    assert isinstance(result_ru.text, str)
    assert len(result_ru.text) > 0
    print("✅ DeepL EN→RU:", result_ru.text)

    # RU → EN
    result_en = translator.translate_text("Привет, мир!", target_lang="EN-US")
    assert isinstance(result_en.text, str)
    assert len(result_en.text) > 0
    print("✅ DeepL RU→EN:", result_en.text)


if __name__ == "__main__":
    test_deepl_translation()

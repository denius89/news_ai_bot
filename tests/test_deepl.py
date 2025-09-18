# tests/test_deepl.py

import os
import deepl
from dotenv import load_dotenv

def test_deepl():
    """Проверка подключения к DeepL API"""
    load_dotenv(dotenv_path=".env")
    api_key = os.getenv("DEEPL_API_KEY")

    if not api_key:
        print("❌ Ключ DeepL не найден")
        return

    translator = deepl.Translator(api_key)
    result = translator.translate_text("Hello, world!", target_lang="RU")
    print("✅ DeepL работает, перевод:", result.text)

if __name__ == "__main__":
    test_deepl()

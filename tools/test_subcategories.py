#!/usr/bin/env python3
"""
Тест интеграции субкатегорий в UI и API.
"""

import sys
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_api_subcategories():
    """Тест API endpoint для получения субкатегорий."""

    print("🧪 Тестируем API для субкатегорий...")

    try:
        # Тест получения категорий и субкатегорий
        response = requests.get("http://localhost:5000/api/digests/categories")

        if response.status_code == 200:
            data = response.json()
            print("✅ API ответ получен")

            if "subcategories" in data.get("data", {}):
                subcategories = data["data"]["subcategories"]
                print(f"✅ Субкатегории найдены: {list(subcategories.keys())}")

                # Проверяем конкретные субкатегории
                if "crypto" in subcategories:
                    crypto_subs = subcategories["crypto"]
                    print(f"📊 Crypto субкатегории: {list(crypto_subs.keys())}")

                    expected_subs = ["bitcoin", "ethereum", "defi", "nft"]
                    for sub in expected_subs:
                        if sub in crypto_subs:
                            print(f"  ✅ {sub}: {crypto_subs[sub]}")
                        else:
                            print(f"  ❌ {sub}: не найден")
                else:
                    print("❌ Crypto субкатегории не найдены")
            else:
                print("❌ Субкатегории не найдены в ответе")

        else:
            print(f"❌ API ошибка: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Ошибка тестирования API: {e}")


def test_generate_with_subcategory():
    """Тест генерации дайджеста с субкатегорией."""

    print("\n🧪 Тестируем генерацию с субкатегорией...")

    test_data = {
        "category": "crypto",
        "subcategory": "bitcoin",  # Новый параметр!
        "style": "analytical",
        "period": "today",
        "length": "medium",
        "limit": 5,
        "user_id": "test_user",
        "save": False,
        "use_rag": True,
        "use_personalization": True,
        "audience": "general",
    }

    try:
        response = requests.post(
            "http://localhost:5000/api/digests/generate", headers={"Content-Type": "application/json"}, json=test_data
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print("✅ Генерация с субкатегорией успешна")
                digest = data.get("data", {}).get("digest", "")
                if digest:
                    print(f"📝 Длина дайджеста: {len(digest)} символов")
                    print(f"📄 Превью: {digest[:200]}...")
                else:
                    print("⚠️ Дайджест пустой")
            else:
                print(f"❌ Ошибка генерации: {data}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Ошибка тестирования генерации: {e}")


def test_prompts_v2_subcategories():
    """Тест работы с субкатегориями в prompts_v2.py."""

    print("\n🧪 Тестируем prompts_v2.py субкатегории...")

    try:
        from digests.prompts_v2 import CATEGORY_CARDS, get_subcategory_config, get_available_subcategories

        # Тест получения субкатегорий для crypto
        crypto_subs = get_available_subcategories("crypto")
        print(f"✅ Crypto субкатегории: {crypto_subs}")

        # Тест получения конфигурации субкатегории
        btc_config = get_subcategory_config("crypto", "bitcoin")
        print(f"✅ Bitcoin конфигурация: {btc_config}")

        expected_subs = ["bitcoin", "ethereum", "defi", "nft"]
        for sub in expected_subs:
            if sub in crypto_subs:
                config = get_subcategory_config("crypto", sub)
                print(f"  ✅ {sub}: {config.get('focus', 'Нет focus')}")
            else:
                print(f"  ❌ {sub}: не найден")

    except Exception as e:
        print(f"❌ Ошибка тестирования prompts_v2: {e}")


if __name__ == "__main__":
    print("🚀 Запуск тестов субкатегорий...")

    # Проверяем доступность сервера
    try:
        response = requests.get("http://localhost:5000/api/digests/categories", timeout=5)
        is_server_running = response.status_code in [200, 404, 401]
    except (requests.RequestException, ConnectionError, requests.Timeout):
        is_server_running = False

    if is_server_running:
        test_api_subcategories()
        test_generate_with_subcategory()
    else:
        print("⚠️ Сервер не запущен, тестируем только prompts_v2.py")

    test_prompts_v2_subcategories()

    print("\n✅ Тесты субкатегорий завершены!")

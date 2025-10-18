#!/usr/bin/env python3
"""
Тест интеграции UI с новыми AI возможностями.
"""

import sys
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_ui_api_integration():
    """Тест API endpoint для UI с новыми возможностями."""

    print("🧪 Тестируем интеграцию UI с новыми AI возможностями...")

    # Тестовые данные с новыми параметрами
    test_requests = [
        {
            "name": "Базовый запрос",
            "data": {"category": "crypto", "style": "analytical", "length": "medium", "limit": 5},
        },
        {
            "name": "С RAG и персонализацией",
            "data": {
                "category": "crypto",
                "style": "analytical",
                "length": "medium",
                "limit": 5,
                "use_rag": True,
                "use_personalization": True,
                "audience": "general",
            },
        },
        {
            "name": "С multi-stage генерацией",
            "data": {
                "category": "crypto",
                "style": "analytical",
                "length": "long",
                "limit": 5,
                "use_multistage": True,
                "use_rag": True,
                "use_personalization": True,
                "audience": "pro",
            },
        },
    ]

    base_url = "http://localhost:8001"
    endpoint = f"{base_url}/api/digests/generate"

    for test_case in test_requests:
        print(f"\n📋 Тест: {test_case['name']}")
        print(f"Данные: {json.dumps(test_case['data'], indent=2, ensure_ascii=False)}")

        try:
            # Отправляем запрос
            response = requests.post(
                endpoint, json=test_case["data"], headers={"Content-Type": "application/json"}, timeout=30
            )

            print(f"Статус: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    digest = result.get("data", {}).get("content", "")
                    metadata = result.get("data", {}).get("metadata", {})

                    print(f"✅ Успешно сгенерирован дайджест: {len(digest)} символов")
                    print(f"Метаданные новых возможностей:")

                    # Проверяем новые возможности в метаданных
                    new_features = ["use_multistage", "use_rag", "use_personalization", "audience"]
                    for feature in new_features:
                        value = metadata.get(feature, "не указано")
                        print(f"  - {feature}: {value}")

                    # Показываем начало дайджеста
                    if digest:
                        preview = digest[:200] + "..." if len(digest) > 200 else digest
                        print(f"Начало: {preview}")
                else:
                    print(f"❌ Ошибка в ответе: {result.get('message', 'Неизвестная ошибка')}")
            else:
                print(f"❌ HTTP ошибка: {response.status_code}")
                print(f"Ответ: {response.text}")

        except requests.exceptions.ConnectionError:
            print("❌ Не удается подключиться к серверу. Убедитесь, что он запущен на localhost:8001")
        except requests.exceptions.Timeout:
            print("❌ Таймаут запроса")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    print(f"\n💡 Чтобы протестировать через UI:")
    print(f"1. Откройте веб-приложение")
    print(f"2. Используйте генерацию дайджестов")
    print(f"3. Проверьте параметры в Network tab браузера")
    print(f"4. Новые параметры: use_multistage, use_rag, use_personalization, audience")


if __name__ == "__main__":
    test_ui_api_integration()
